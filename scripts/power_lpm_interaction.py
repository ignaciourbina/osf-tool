#!/usr/bin/env python3
"""Power simulation for the H3 interaction term in the mixed-effects LPM.

Generates synthetic datasets under the 2×2 design (opponent_type × communication)
with game_type as a within-subjects factor, fits the mixed-effects linear
probability model via statsmodels, and reports power for the interaction term
across a range of effect sizes.

This mirrors the registered analysis: mixed-effects LPM with random intercept
for pair, matching the approach used in Study 2 (OSF: zux2b).

Usage:
    python scripts/power_lpm_interaction.py                    # default sweep
    python scripts/power_lpm_interaction.py --n-sims 500       # more precise
    python scripts/power_lpm_interaction.py --beta-inter -0.10 # single point
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

warnings.filterwarnings("ignore", category=UserWarning, module="statsmodels")
warnings.filterwarnings("ignore", category=RuntimeWarning, module="statsmodels")

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"

# ── DGP parameters calibrated from Study 2 ─────────────────────────
# Study 2 cooperation rates (from manuscript Table 2):
#   PD:  HH-NoCom=43.9%, HH-Com=73.2%, AI-NoCom=38.0%, AI-Com=70.3%
#   SH:  HH-NoCom=66.7%, HH-Com=83.5%, AI-NoCom=59.8%, AI-Com=90.6%
#
# LPM coefficients (probability scale):
#   intercept ≈ 0.44  (HH, NoCom, PD baseline)
#   beta_opp  ≈ -0.06 (AI main effect, small)
#   beta_comm ≈  0.29  (communication main effect, large)
#   beta_game ≈  0.22  (SH vs PD, large)
#   beta_inter: swept — H3 predicts negative (comm helps AI less)
#   pair-level ICC ≈ 0.10 (plausible for dyadic data)

DEFAULTS = {
    "intercept": 0.44,
    "beta_opp": -0.06,
    "beta_comm": 0.29,
    "beta_game": 0.22,
    "tau_pair": 0.15,     # pair-level SD (gives ICC ≈ 0.10 for binary outcome)
}

N_PER_CONDITION = 100
ALPHA = 0.05  # one-tailed for directional H3


def generate_data(
    beta_inter: float,
    params: dict[str, float],
    n_per_cond: int = N_PER_CONDITION,
    rng: np.random.Generator | None = None,
) -> pd.DataFrame:
    """Generate one synthetic dataset under the LPM DGP."""
    if rng is None:
        rng = np.random.default_rng()

    rows = []
    pair_id = 0

    conditions = {
        1: (0, 0),  # HH, no comm
        2: (0, 1),  # HH, comm
        3: (1, 0),  # AI, no comm
        4: (1, 1),  # AI, comm
    }

    for cond, (opp, comm) in conditions.items():
        # HH: n/2 pairs × 2 humans; AI: n pairs × 1 human
        n_pairs = n_per_cond // 2 if opp == 0 else n_per_cond
        humans_per_pair = 2 if opp == 0 else 1

        for _ in range(n_pairs):
            pair_id += 1
            u_pair = rng.normal(0, params["tau_pair"])

            for _ in range(humans_per_pair):
                for game in [0, 1]:  # 0=PD, 1=SH
                    prob = (
                        params["intercept"]
                        + params["beta_opp"] * opp
                        + params["beta_comm"] * comm
                        + beta_inter * opp * comm
                        + params["beta_game"] * game
                        + u_pair
                    )
                    # Clip to [0.01, 0.99] for valid probabilities
                    prob = np.clip(prob, 0.01, 0.99)
                    y = int(rng.random() < prob)

                    rows.append({
                        "pair_id": pair_id,
                        "opponent_type": opp,
                        "communication": comm,
                        "game_type": game,
                        "cooperation": y,
                    })

    return pd.DataFrame(rows)


def fit_lpm(df: pd.DataFrame) -> dict:
    """Fit the mixed-effects LPM and return interaction test results."""
    model = smf.mixedlm(
        "cooperation ~ opponent_type + communication + opponent_type:communication + game_type",
        data=df,
        groups=df["pair_id"],
    )
    # Use default (Powell) optimizer — more robust for LPMs with small clusters
    result = model.fit(reml=True)

    inter_key = "opponent_type:communication"
    coef = result.fe_params[inter_key]
    pval = result.pvalues[inter_key]
    ci = result.conf_int().loc[inter_key]

    return {
        "coef": float(coef),
        "pval_twotail": float(pval),
        "ci_lo": float(ci[0]),
        "ci_hi": float(ci[1]),
        "converged": result.converged,
    }


def _single_sim(args: tuple) -> dict | None:
    """Run one simulation (for use with ProcessPoolExecutor)."""
    beta_inter, params, n_per_cond, seed = args
    rng = np.random.default_rng(seed=seed)
    df = generate_data(beta_inter, params, n_per_cond, rng)
    try:
        return fit_lpm(df)
    except Exception:
        return None


def run_power_simulation(
    beta_inter: float,
    params: dict[str, float],
    n_sims: int = 200,
    n_per_cond: int = N_PER_CONDITION,
    alpha: float = ALPHA,
    n_workers: int = 1,
) -> dict:
    """Run n_sims simulations and compute power for the interaction term."""
    from concurrent.futures import ProcessPoolExecutor

    sim_args = [
        (beta_inter, params, n_per_cond, 12345 + i)
        for i in range(n_sims)
    ]

    significant = 0
    converged = 0
    coefficients = []

    if n_workers > 1:
        with ProcessPoolExecutor(max_workers=n_workers) as pool:
            for result in pool.map(_single_sim, sim_args, chunksize=10):
                if result is None:
                    continue
                if result["converged"]:
                    converged += 1
                    coefficients.append(result["coef"])
                    if result["coef"] < 0 and result["pval_twotail"] / 2 < alpha:
                        significant += 1
    else:
        for i, sa in enumerate(sim_args):
            result = _single_sim(sa)
            if result is None:
                continue
            if result["converged"]:
                converged += 1
                coefficients.append(result["coef"])
                if result["coef"] < 0 and result["pval_twotail"] / 2 < alpha:
                    significant += 1

    power = significant / converged if converged > 0 else 0.0

    return {
        "beta_inter": beta_inter,
        "n_sims": n_sims,
        "n_converged": converged,
        "n_significant": significant,
        "power": power,
        "mean_coef": float(np.mean(coefficients)) if coefficients else None,
        "sd_coef": float(np.std(coefficients)) if coefficients else None,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Power simulation for H3 interaction in mixed-effects LPM"
    )
    parser.add_argument("--n-sims", type=int, default=500,
                        help="Simulations per effect size (default: 500)")
    parser.add_argument("--n-per-condition", type=int, default=N_PER_CONDITION,
                        help="Humans per condition (default: 100)")
    parser.add_argument("--beta-inter", type=float, default=None,
                        help="Single interaction effect size to test (default: sweep)")
    parser.add_argument("--n-workers", type=int, default=8,
                        help="Parallel workers (default: 8)")
    parser.add_argument("--output-json", type=str, default="",
                        help="Save results to JSON file")
    args = parser.parse_args()

    params = DEFAULTS.copy()

    print("=" * 70)
    print("H3 INTERACTION POWER ANALYSIS — Mixed-Effects LPM")
    print("Communication and Cooperation with Human and Artificial Agents")
    print("=" * 70)
    print(f"\nDesign: 2×2 between-subjects, game_type within-subjects")
    print(f"N = {args.n_per_condition * 4} human participants ({args.n_per_condition}/condition)")
    print(f"Observations per simulation: {args.n_per_condition * 4 * 2} (2 games each)")
    print(f"Alpha = {ALPHA} (one-tailed, H3 predicts beta_inter < 0)")
    print(f"Simulations per point: {args.n_sims}")
    print(f"Workers: {args.n_workers}")
    print(f"\nDGP parameters (from Study 2):")
    for k, v in params.items():
        print(f"  {k}: {v}")

    if args.beta_inter is not None:
        # Single point
        print(f"\nTesting beta_inter = {args.beta_inter} ({args.n_workers} workers)...")
        t0 = time.time()
        result = run_power_simulation(
            args.beta_inter, params, args.n_sims, args.n_per_condition,
            n_workers=args.n_workers,
        )
        elapsed = time.time() - t0
        print(f"  Power: {result['power']:.1%} ({result['n_significant']}/{result['n_converged']})")
        print(f"  Mean estimated coef: {result['mean_coef']:.4f} (SD: {result['sd_coef']:.4f})")
        print(f"  Time: {elapsed:.1f}s")
        results = [result]
    else:
        # Sweep across effect sizes
        sweep_values = [0.0, -0.05, -0.08, -0.10, -0.13, -0.15, -0.18, -0.20, -0.25]
        results = []

        print(f"\n{'beta_inter':>12s}  {'Power':>8s}  {'Sig/Conv':>10s}  {'Mean coef':>10s}  {'SD coef':>10s}")
        print("-" * 58)

        t0 = time.time()
        for beta_val in sweep_values:
            result = run_power_simulation(
                beta_val, params, args.n_sims, args.n_per_condition,
                n_workers=args.n_workers,
            )
            results.append(result)
            print(f"{beta_val:12.3f}  {result['power']:8.1%}  "
                  f"{result['n_significant']:>4d}/{result['n_converged']:<4d}  "
                  f"{result['mean_coef']:10.4f}  {result['sd_coef']:10.4f}")

        elapsed = time.time() - t0

        # Find MDES at 80% power via interpolation
        powers = np.array([r["power"] for r in results])
        betas = np.array([r["beta_inter"] for r in results])
        # Find where power crosses 0.80
        mdes_80 = None
        for i in range(1, len(powers)):
            if powers[i - 1] < 0.80 <= powers[i]:
                # Linear interpolation
                frac = (0.80 - powers[i - 1]) / (powers[i] - powers[i - 1])
                mdes_80 = betas[i - 1] + frac * (betas[i] - betas[i - 1])
                break

        print(f"\n{'─' * 70}")
        print("SUMMARY")
        print(f"{'─' * 70}")
        if mdes_80 is not None:
            print(f"  Minimum detectable interaction at 80% power: beta_inter ≈ {mdes_80:.3f}")
            print(f"  This means communication must boost cooperation by at least "
                  f"{abs(mdes_80):.1%} LESS")
            print(f"  for AI opponents than for human opponents to be detectable.")
        else:
            # Check if power is already above 80% at the smallest nonzero effect
            above = [r for r in results if r["power"] >= 0.80 and r["beta_inter"] != 0]
            if above:
                print(f"  Power exceeds 80% at beta_inter = {above[0]['beta_inter']:.3f}")
            else:
                print(f"  Power does not reach 80% in the tested range.")
                print(f"  Largest effect tested: beta_inter = {betas[-1]:.3f}, "
                      f"power = {powers[-1]:.1%}")

        print(f"\n  Context from Study 2:")
        print(f"    Communication boost (HH):  ~29pp (PD), ~17pp (SH)")
        print(f"    Communication boost (AI):  ~32pp (PD), ~31pp (SH)")
        print(f"    Observed interaction: b=0.110 (OPPOSITE to H3 prediction)")
        print(f"    Study 2 was online (MTurk) with structured message menus.")
        print(f"    Study 3 moves to in-person lab with free-form text + live ChatGPT.")
        print(f"\n  Total time: {elapsed:.0f}s")
        print("=" * 70)

    # Save results
    if args.output_json:
        out_path = Path(args.output_json)
    else:
        out_path = OUTPUT_DIR / "69bce30f-coop-ai-study3" / "power_lpm_interaction.json"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    output = {
        "analysis": "H3 interaction power — mixed-effects LPM",
        "design": {
            "n_per_condition": args.n_per_condition,
            "total_human_participants": args.n_per_condition * 4,
            "total_observations": args.n_per_condition * 4 * 2,
            "alpha": ALPHA,
            "test": "one-tailed (H3: beta_inter < 0)",
            "model": "cooperation ~ opp + comm + opp:comm + game + (1|pair)",
        },
        "dgp_parameters": params,
        "n_sims_per_point": args.n_sims,
        "results": results,
    }
    with out_path.open("w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to: {out_path}")


if __name__ == "__main__":
    main()
