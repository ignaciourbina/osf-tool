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
    "beta_opp": -0.5,      # AI opponent reduces cooperation (~12pp)
    "beta_comm": 0.5,      # communication increases cooperation (~12pp)
    "beta_inter": -0.2,    # interaction: comm effect smaller with AI
    "beta_game": 0.3,      # SH slightly higher cooperation than PD
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
        summaries[param] = {
            "mean": float(np.mean(samples)),
            "median": float(np.median(samples)),
            "sd": float(np.std(samples)),
            "hdi_lo": lo,
            "hdi_hi": hi,
            "excludes_zero": (lo > 0) or (hi < 0),
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


def run_assurance(
    model_code: str,
    theorized: dict[str, float],
    n_sims: int = 50,
    n_per_condition: int = N_PER_CONDITION,
    num_chains: int = 4,
    num_samples: int = 1000,
) -> dict:
    """Run the assurance analysis across n_sims simulated datasets."""
    params_of_interest = ["beta_opp", "beta_comm", "beta_inter", "beta_game"]
    detections = {p: 0 for p in params_of_interest}
    all_summaries = []

    print(f"\nRunning {n_sims} simulations...")
    print(f"  N per condition: {n_per_condition}")
    print(f"  Theorized coefficients (log-odds):")
    for k, v in theorized.items():
        print(f"    {k}: {v}")
    print()

    for sim in range(n_sims):
        t0 = time.time()
        seed = 42000 + sim

        # Generate data
        df = generate_synthetic_data(theorized, n_per_condition, seed=seed)
        stan_data = df_to_stan_data(df)

        # Fit model
        try:
            summary = fit_and_summarize(
                model_code, stan_data,
                num_chains=num_chains,
                num_samples=num_samples,
                seed=seed,
            )
        except Exception as e:
            print(f"  Sim {sim + 1}/{n_sims}: FAILED ({e})")
            continue

        elapsed = time.time() - t0

        # Track detections
        for p in params_of_interest:
            if summary[p]["excludes_zero"]:
                detections[p] += 1

        status = " | ".join(
            f"{p}={'Y' if summary[p]['excludes_zero'] else 'n'}"
            for p in params_of_interest
        )
        print(f"  Sim {sim + 1}/{n_sims} ({elapsed:.1f}s): {status}")

        all_summaries.append(summary)

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
        print("=" * 65)
        print("SINGLE FIT CHECK")
        print("=" * 65)

        df = generate_synthetic_data(theorized, args.n_per_condition, seed=42)
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
        print(f"\nFitting Stan model ({args.num_chains} chains, "
              f"{args.num_samples} samples each)...")

        t0 = time.time()
        summary = fit_and_summarize(
            model_code, stan_data,
            num_chains=args.num_chains,
            num_samples=args.num_samples,
            seed=42,
        )
        elapsed = time.time() - t0
        print(f"  Done in {elapsed:.1f}s\n")

        print(f"{'Parameter':<18s} {'Mean':>8s} {'Median':>8s} {'SD':>8s} "
              f"{'HDI_lo':>8s} {'HDI_hi':>8s} {'Excl 0':>8s} {'True':>8s}")
        print("-" * 82)
        for param in ["alpha", "beta_opp", "beta_comm", "beta_inter", "beta_game"]:
            s = summary[param]
            true_val = theorized.get(param, "")
            excl = "YES" if s["excludes_zero"] else "no"
            print(f"{param:<18s} {s['mean']:8.3f} {s['median']:8.3f} {s['sd']:8.3f} "
                  f"{s['hdi_lo']:8.3f} {s['hdi_hi']:8.3f} {excl:>8s} {true_val:8.3f}")

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
    )

    # Print results
    print("\n" + "=" * 65)
    print("ASSURANCE RESULTS")
    print("=" * 65)
    print(f"\nSimulations completed: {results['n_sims_completed']}/{results['n_sims_requested']}")
    print(f"\nAssurance (prob. 95% HDI excludes zero):")
    print(f"  {'Parameter':<18s} {'Assurance':>10s} {'Detections':>12s} {'Theorized':>12s}")
    print(f"  {'-'*52}")
    for param, assur in results["assurance"].items():
        det = results["detections"][param]
        true_val = theorized.get(param, 0)
        print(f"  {param:<18s} {assur:10.1%} {det:>8d}/{results['n_sims_completed']:<3d} "
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
