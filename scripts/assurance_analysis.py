#!/usr/bin/env python3
"""Bayesian assurance (design) analysis for the cooperation experiment.

Simulates datasets under theorized effect sizes, fits the Bayesian
mixed-effects logit via PyStan, and reports the proportion of simulations
in which each coefficient's 95% HDI excludes zero.

Usage:
    python scripts/assurance_analysis.py                  # default 50 sims
    python scripts/assurance_analysis.py --n-sims 200     # more sims
    python scripts/assurance_analysis.py --fit-one         # single fit check
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import stan

# ── Paths ────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
STAN_MODEL = SCRIPT_DIR / "stan_models" / "cooperation_mlm.stan"
OUTPUT_DIR = SCRIPT_DIR.parent / "output"

# ── Theorized coefficients (log-odds scale) ──────────────────────────
# These are the assumed true effects for the assurance analysis.
# Adjust to match your theoretical expectations.
THEORIZED = {
    "alpha": 0.0,          # intercept: ~50% baseline cooperation
    "beta_opp": -0.8,      # AI opponent reduces cooperation (moderate)
    "beta_comm": 0.8,      # communication increases cooperation (moderate)
    "beta_inter": -0.4,    # interaction: comm effect smaller with AI
    "beta_game": 0.8,      # SH higher cooperation than PD (moderate)
    "tau_intercept": 0.5,   # pair-level SD for random intercept
    "tau_slope": 0.3,       # pair-level SD for random slope (game)
    "rho": 0.2,             # correlation between intercept and slope
}

# ── Design parameters ────────────────────────────────────────────────
N_PER_CONDITION = 100
CONDITIONS = {
    # condition: (opponent_type, communication)
    1: (0, 0),  # HH, no comm
    2: (0, 1),  # HH, comm
    3: (1, 0),  # AIH, no comm
    4: (1, 1),  # AIH, comm
}

# Predicted direction for each coefficient (directional hypotheses).
# "negative" = H predicts coeff < 0; "positive" = H predicts coeff > 0.
PREDICTED_DIRECTION = {
    "beta_opp": "negative",    # H1: AI reduces cooperation
    "beta_comm": "positive",   # H2: communication increases cooperation
    "beta_inter": "negative",  # H3: comm effect smaller with AI
    "beta_game": "positive",   # SH has higher cooperation than PD
}


def generate_synthetic_data(
    theorized: dict[str, float],
    n_per_condition: int = N_PER_CONDITION,
    seed: int | None = None,
) -> pd.DataFrame:
    """Generate one synthetic dataset under the theorized DGP.

    In HH conditions (c1, c2): pairs of 2 humans → n_per_condition/2 pairs,
    each contributing 2 observations (both humans decide).
    In AIH conditions (c3, c4): 1 human per pair → n_per_condition pairs,
    each contributing 1 observation.

    Each participant contributes 2 rows (one per game: PD and SH).
    """
    rng = np.random.default_rng(seed)

    alpha = theorized["alpha"]
    beta_opp = theorized["beta_opp"]
    beta_comm = theorized["beta_comm"]
    beta_inter = theorized["beta_inter"]
    beta_game = theorized["beta_game"]
    tau_int = theorized["tau_intercept"]
    tau_sl = theorized["tau_slope"]
    rho = theorized["rho"]

    # Covariance matrix for random effects
    cov_re = np.array([
        [tau_int ** 2, rho * tau_int * tau_sl],
        [rho * tau_int * tau_sl, tau_sl ** 2],
    ])

    rows = []
    pair_id = 0

    for cond, (opp, comm) in CONDITIONS.items():
        if opp == 0:
            # HH: n_per_condition humans in n_per_condition/2 pairs
            n_pairs = n_per_condition // 2
            humans_per_pair = 2
        else:
            # AIH: n_per_condition humans, each in their own pair
            n_pairs = n_per_condition
            humans_per_pair = 1

        for _ in range(n_pairs):
            pair_id += 1
            # Draw pair-level random effects
            re = rng.multivariate_normal([0, 0], cov_re)
            u_int, u_sl = re[0], re[1]

            for _p in range(humans_per_pair):
                for game in [0, 1]:  # 0 = PD, 1 = SH
                    eta = (
                        alpha + u_int
                        + beta_opp * opp
                        + beta_comm * comm
                        + beta_inter * opp * comm
                        + (beta_game + u_sl) * game
                    )
                    prob = 1 / (1 + np.exp(-eta))
                    y = int(rng.random() < prob)

                    rows.append({
                        "pair_id": pair_id,
                        "condition": cond,
                        "opponent_type": opp,
                        "communication": comm,
                        "game_type": game,
                        "cooperation": y,
                    })

    return pd.DataFrame(rows)


def df_to_stan_data(df: pd.DataFrame) -> dict:
    """Convert a dataframe to the dict expected by the Stan model."""
    # Re-index pair_id to 1..J
    pair_labels = df["pair_id"].unique()
    pair_map = {pid: idx + 1 for idx, pid in enumerate(sorted(pair_labels))}
    mapped_pairs = df["pair_id"].map(pair_map).values

    return {
        "N": len(df),
        "J": len(pair_labels),
        "y": df["cooperation"].values.astype(int).tolist(),
        "opponent_type": df["opponent_type"].values.astype(float).tolist(),
        "communication": df["communication"].values.astype(float).tolist(),
        "game_type": df["game_type"].values.astype(float).tolist(),
        "pair_id": mapped_pairs.astype(int).tolist(),
    }


def hdi(samples: np.ndarray, prob: float = 0.95) -> tuple[float, float]:
    """Compute the highest density interval."""
    sorted_samples = np.sort(samples)
    n = len(sorted_samples)
    interval_size = int(np.ceil(prob * n))
    widths = sorted_samples[interval_size:] - sorted_samples[:n - interval_size]
    best = int(np.argmin(widths))
    return float(sorted_samples[best]), float(sorted_samples[best + interval_size])


def fit_and_summarize(
    model_code: str,
    stan_data: dict,
    num_chains: int = 4,
    num_samples: int = 1000,
    seed: int | None = None,
) -> dict[str, dict]:
    """Fit the Stan model and return posterior summaries for fixed effects."""
    posterior = stan.build(model_code, data=stan_data, random_seed=seed)
    fit = posterior.sample(
        num_chains=num_chains,
        num_samples=num_samples,
    )

    params = ["alpha", "beta_opp", "beta_comm", "beta_inter", "beta_game"]
    summaries = {}
    for param in params:
        samples = fit[param].flatten()
        lo, hi = hdi(samples)
        # Directional detection: check if 95% HDI falls entirely
        # in the predicted direction
        direction = PREDICTED_DIRECTION.get(param)
        if direction == "negative":
            detected = hi < 0
            prob_correct = float(np.mean(samples < 0))
        elif direction == "positive":
            detected = lo > 0
            prob_correct = float(np.mean(samples > 0))
        else:
            detected = (lo > 0) or (hi < 0)
            prob_correct = None
        summaries[param] = {
            "mean": float(np.mean(samples)),
            "median": float(np.median(samples)),
            "sd": float(np.std(samples)),
            "hdi_lo": lo,
            "hdi_hi": hi,
            "detected": detected,
            "prob_correct_direction": prob_correct,
        }

    # Also report random effects SDs
    for i, name in enumerate(["tau_intercept", "tau_slope"]):
        samples = fit["tau"][i, :].flatten()
        lo, hi = hdi(samples)
        summaries[name] = {
            "mean": float(np.mean(samples)),
            "median": float(np.median(samples)),
            "sd": float(np.std(samples)),
            "hdi_lo": lo,
            "hdi_hi": hi,
        }

    return summaries


def _run_single_sim_inprocess(sim_idx, model_code, theorized, n_per_condition, num_chains, num_samples):
    """Run a single simulation in the current process."""
    seed = 42000 + sim_idx
    df = generate_synthetic_data(theorized, n_per_condition, seed=seed)
    stan_data = df_to_stan_data(df)
    try:
        summary = fit_and_summarize(
            model_code, stan_data,
            num_chains=num_chains,
            num_samples=num_samples,
            seed=seed,
        )
        return {"sim": sim_idx, "summary": summary}
    except Exception as e:
        return {"sim": sim_idx, "error": str(e)}


def run_assurance(
    model_code: str,
    theorized: dict[str, float],
    n_sims: int = 50,
    n_per_condition: int = N_PER_CONDITION,
    num_chains: int = 4,
    num_samples: int = 1000,
    n_workers: int = 1,
) -> dict:
    """Run the assurance analysis across n_sims simulated datasets."""
    params_of_interest = ["beta_opp", "beta_comm", "beta_inter", "beta_game"]
    detections = {p: 0 for p in params_of_interest}
    all_summaries = []

    print(f"\nRunning {n_sims} simulations ({n_workers} workers, {num_chains} chains each)...")
    print(f"  N per condition: {n_per_condition}")
    print(f"  Theorized coefficients (log-odds):")
    for k, v in theorized.items():
        print(f"    {k}: {v}")
    print()

    t_start = time.time()

    if n_workers <= 1:
        # Sequential mode
        for sim in range(n_sims):
            t0 = time.time()
            result = _run_single_sim_inprocess(
                sim, model_code, theorized, n_per_condition, num_chains, num_samples
            )
            elapsed = time.time() - t0

            if "error" in result:
                print(f"  Sim {sim + 1}/{n_sims}: FAILED ({result['error']})")
                continue

            summary = result["summary"]
            for p in params_of_interest:
                if summary[p]["detected"]:
                    detections[p] += 1

            status = " | ".join(
                f"{p}={'Y' if summary[p]['detected'] else 'n'}"
                for p in params_of_interest
            )
            print(f"  Sim {sim + 1}/{n_sims} ({elapsed:.1f}s): {status}")
            all_summaries.append(summary)
    else:
        # Parallel mode via subprocesses (avoids PyStan/httpstan fork issues)
        import tempfile
        tmpdir = tempfile.mkdtemp(prefix="assurance_")
        python = sys.executable
        script = str(SCRIPT_DIR / "assurance_analysis.py")

        # Build per-sim CLI args
        coeff_args = []
        for key, val in theorized.items():
            coeff_args.extend([f"--{key.replace('_', '-')}", str(val)])

        # Launch all sims as subprocesses
        processes: dict[int, tuple[subprocess.Popen, str]] = {}
        running: set[int] = set()
        next_sim = 0
        completed = 0

        while completed < n_sims:
            # Launch up to n_workers concurrent sims
            while len(running) < n_workers and next_sim < n_sims:
                out_file = os.path.join(tmpdir, f"sim_{next_sim}.json")
                cmd = [
                    python, script, "--fit-one",
                    "--n-per-condition", str(n_per_condition),
                    "--num-chains", str(num_chains),
                    "--num-samples", str(num_samples),
                    *coeff_args,
                    "--sim-seed", str(42000 + next_sim),
                    "--output-json", out_file,
                ]
                proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                processes[next_sim] = (proc, out_file)
                running.add(next_sim)
                next_sim += 1

            # Poll for completions
            newly_done = set()
            for sim_idx in running:
                proc, out_file = processes[sim_idx]
                ret = proc.poll()
                if ret is not None:
                    newly_done.add(sim_idx)
                    completed += 1
                    if ret == 0 and os.path.exists(out_file):
                        with open(out_file) as f:
                            summary = json.load(f)
                        for p in params_of_interest:
                            if summary[p]["detected"]:
                                detections[p] += 1
                        status = " | ".join(
                            f"{p}={'Y' if summary[p]['detected'] else 'n'}"
                            for p in params_of_interest
                        )
                        print(f"  Sim {sim_idx + 1}/{n_sims} [{completed}/{n_sims} done]: {status}")
                        all_summaries.append(summary)
                    else:
                        print(f"  Sim {sim_idx + 1}/{n_sims}: FAILED (exit {ret})")
            running -= newly_done

            if not newly_done and running:
                time.sleep(1)

    total_elapsed = time.time() - t_start
    print(f"\n  Total time: {total_elapsed:.0f}s ({total_elapsed/60:.1f}min)")

    # Compute assurance
    n_completed = len(all_summaries)
    assurance = {p: detections[p] / n_completed if n_completed > 0 else 0
                 for p in params_of_interest}

    return {
        "n_sims_requested": n_sims,
        "n_sims_completed": n_completed,
        "theorized_coefficients": theorized,
        "design": {
            "n_per_condition": n_per_condition,
            "total_human_participants": n_per_condition * 4,
            "conditions": {str(k): v for k, v in CONDITIONS.items()},
        },
        "assurance": assurance,
        "detections": detections,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Bayesian assurance analysis")
    parser.add_argument("--n-sims", type=int, default=50,
                        help="Number of simulated datasets (default: 50)")
    parser.add_argument("--n-per-condition", type=int, default=N_PER_CONDITION,
                        help="Human participants per condition (default: 100)")
    parser.add_argument("--num-chains", type=int, default=4,
                        help="MCMC chains per fit (default: 4)")
    parser.add_argument("--num-samples", type=int, default=1000,
                        help="Samples per chain (default: 1000)")
    parser.add_argument("--fit-one", action="store_true",
                        help="Fit a single dataset and print summary (quick check)")
    parser.add_argument("--n-workers", type=int, default=1,
                        help="Parallel workers for simulations (default: 1, try ncores/chains)")
    parser.add_argument("--sim-seed", type=int, default=42,
                        help=argparse.SUPPRESS)  # internal: seed for subprocess mode
    parser.add_argument("--output-json", type=str, default="",
                        help=argparse.SUPPRESS)  # internal: write summary JSON for subprocess mode

    # Allow overriding theorized coefficients
    for key, default in THEORIZED.items():
        parser.add_argument(f"--{key.replace('_', '-')}",
                            type=float, default=default,
                            help=f"Theorized {key} (default: {default})")
    args = parser.parse_args()

    # Build theorized dict from args
    theorized = {}
    for key in THEORIZED:
        theorized[key] = getattr(args, key.replace("-", "_"))

    # Load Stan model
    model_code = STAN_MODEL.read_text(encoding="utf-8")

    if args.fit_one:
        seed = args.sim_seed
        quiet = bool(args.output_json)  # quiet mode when called as subprocess

        if not quiet:
            print("=" * 65)
            print("SINGLE FIT CHECK")
            print("=" * 65)

        df = generate_synthetic_data(theorized, args.n_per_condition, seed=seed)
        if not quiet:
            print(f"\nSynthetic data: {len(df)} observations, "
                  f"{df['pair_id'].nunique()} pairs")
            print(f"  Conditions: {df.groupby('condition').size().to_dict()}")
            print(f"  Cooperation rate: {df['cooperation'].mean():.3f}")
            print(f"  By condition: {df.groupby('condition')['cooperation'].mean().to_dict()}")

            # Save synthetic data
            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            data_path = OUTPUT_DIR / "synthetic_cooperation_data.csv"
            df.to_csv(data_path, index=False)
            print(f"\n  Saved synthetic data to: {data_path}")

        stan_data = df_to_stan_data(df)
        if not quiet:
            print(f"\nFitting Stan model ({args.num_chains} chains, "
                  f"{args.num_samples} samples each)...")

        t0 = time.time()
        summary = fit_and_summarize(
            model_code, stan_data,
            num_chains=args.num_chains,
            num_samples=args.num_samples,
            seed=seed,
        )
        elapsed = time.time() - t0

        # If called as subprocess, write JSON and exit
        if args.output_json:
            with open(args.output_json, "w") as f:
                json.dump(summary, f)
            return

        print(f"  Done in {elapsed:.1f}s\n")

        print(f"{'Parameter':<18s} {'Mean':>8s} {'Median':>8s} {'SD':>8s} "
              f"{'HDI_lo':>8s} {'HDI_hi':>8s} {'Detect':>8s} {'P(dir)':>8s} {'True':>8s}")
        print("-" * 92)
        for param in ["alpha", "beta_opp", "beta_comm", "beta_inter", "beta_game"]:
            s = summary[param]
            true_val = theorized.get(param, "")
            det = "YES" if s["detected"] else "no"
            pdir = f"{s['prob_correct_direction']:.3f}" if s["prob_correct_direction"] is not None else "n/a"
            dirn = PREDICTED_DIRECTION.get(param, "none")
            print(f"{param:<18s} {s['mean']:8.3f} {s['median']:8.3f} {s['sd']:8.3f} "
                  f"{s['hdi_lo']:8.3f} {s['hdi_hi']:8.3f} {det:>8s} {pdir:>8s} {true_val:8.3f}")

        print()
        for name in ["tau_intercept", "tau_slope"]:
            s = summary[name]
            true_val = theorized.get(name, "")
            print(f"{name:<18s} {s['mean']:8.3f} {s['median']:8.3f} {s['sd']:8.3f} "
                  f"{s['hdi_lo']:8.3f} {s['hdi_hi']:8.3f} {'':>8s} {true_val:8.3f}")

        return

    # Full assurance analysis
    print("=" * 65)
    print("BAYESIAN ASSURANCE ANALYSIS")
    print("Communication and Cooperation with Human and Artificial Agents")
    print("=" * 65)

    results = run_assurance(
        model_code=model_code,
        theorized=theorized,
        n_sims=args.n_sims,
        n_per_condition=args.n_per_condition,
        num_chains=args.num_chains,
        num_samples=args.num_samples,
        n_workers=args.n_workers,
    )

    # Print results
    print("\n" + "=" * 65)
    print("ASSURANCE RESULTS")
    print("=" * 65)
    print(f"\nSimulations completed: {results['n_sims_completed']}/{results['n_sims_requested']}")
    print(f"\nAssurance (prob. 95% HDI falls in predicted direction):")
    print(f"  {'Parameter':<18s} {'Direction':>10s} {'Assurance':>10s} {'Detections':>12s} {'Theorized':>12s}")
    print(f"  {'-'*64}")
    for param, assur in results["assurance"].items():
        det = results["detections"][param]
        true_val = theorized.get(param, 0)
        dirn = PREDICTED_DIRECTION.get(param, "—")
        print(f"  {param:<18s} {dirn:>10s} {assur:10.1%} {det:>8d}/{results['n_sims_completed']:<3d} "
              f"{true_val:12.3f}")

    print(f"\nInterpretation:")
    print(f"  Assurance >= 80%: well-powered to detect the theorized effect")
    print(f"  Assurance 50-80%: adequate but uncertain")
    print(f"  Assurance < 50%:  insufficient power for that effect size")

    # Save results
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    results_path = OUTPUT_DIR / "assurance_results.json"
    with results_path.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\n  Results saved to: {results_path}")
    print("=" * 65)


if __name__ == "__main__":
    main()
