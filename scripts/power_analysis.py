#!/usr/bin/env python3
"""Power analysis for the 2x2 between-subjects cooperation experiment.

Allocation: 1/6, 1/6, 2/6, 2/6 for conditions 1–4.  Total N = 400.

Reports:
  1. One-way ANOVA (4 groups, unequal n): detectable effect size (f) at 80% power
  2. Two-sample t-test (HH vs AIH, unequal n): detectable effect size (d) at 80% power
  3. Power curves across a range of effect sizes
"""

from __future__ import annotations

import numpy as np
from scipy import stats

# ── Design parameters ────────────────────────────────────────────────
N_TOTAL = 400
ALPHA = 0.05
TARGET_POWER = 0.80

# Human observations per condition (balanced at ~100 each).
# Sessions are allocated 1/6, 1/6, 2/6, 2/6 across c1-c4, but
# HH sessions (c1,c2) yield 2 human data points each while
# AIH sessions (c3,c4) yield 1, so human n is equal across conditions.
n = np.array([100, 100, 100, 100])
K = len(n)  # number of groups

# For t-tests: HH (c1+c2) vs AIH (c3+c4)
n_hh = n[0] + n[1]
n_aih = n[2] + n[3]


# ── ANOVA power (non-central F) ─────────────────────────────────────
def anova_power(f_effect: float, group_ns: np.ndarray, alpha: float = ALPHA) -> float:
    """Power for one-way ANOVA with unequal group sizes.

    f_effect: Cohen's f  (f = sqrt(eta^2 / (1 - eta^2)))
    Uses the non-central F distribution with lambda = sum(n_i) * f^2
    adjusted for unequal n via the harmonic-mean approach isn't needed
    here — we use the exact non-centrality parameter:
        lambda = f^2 * N   (for equal variance, balanced-equivalent)
    For unequal n the exact NCP is:
        lambda = sum_i [ n_i * (mu_i - mu_bar)^2 ] / sigma^2
    With Cohen's f defined as sqrt( (1/k) * sum(tau_i^2) / sigma^2 ),
    and a balanced-equivalent NCP = N * f^2, the standard approximation
    is adequate for moderate imbalance (our ratio is 1:1:2:2).
    """
    N = group_ns.sum()
    df1 = len(group_ns) - 1
    df2 = N - len(group_ns)
    lam = f_effect ** 2 * N  # non-centrality parameter
    crit = stats.f.ppf(1 - alpha, df1, df2)
    return 1 - stats.ncf.cdf(crit, df1, df2, lam)


# ── t-test power (non-central t) ────────────────────────────────────
def ttest_power(d: float, n1: int, n2: int, alpha: float = ALPHA) -> float:
    """Power for independent two-sample t-test (two-tailed), unequal n."""
    df = n1 + n2 - 2
    se = np.sqrt(1 / n1 + 1 / n2)
    ncp = d / se  # non-centrality parameter
    crit = stats.t.ppf(1 - alpha / 2, df)
    return 1 - stats.nct.cdf(crit, df, ncp) + stats.nct.cdf(-crit, df, ncp)


# ── Find minimum detectable effect size at target power ──────────────
def find_mdes(power_func, target: float = TARGET_POWER,
              lo: float = 0.001, hi: float = 1.5, tol: float = 1e-5) -> float:
    """Binary search for the smallest effect size achieving target power."""
    while hi - lo > tol:
        mid = (lo + hi) / 2
        if power_func(mid) < target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def main() -> None:
    print("=" * 65)
    print("POWER ANALYSIS")
    print("Communication and Cooperation with Human and Artificial Agents")
    print("=" * 65)

    print(f"\nDesign: 2x2 between-subjects, 4 conditions")
    print(f"Total N = {N_TOTAL}")
    print(f"Allocation (1/6, 1/6, 2/6, 2/6): n = {n.tolist()}")
    print(f"  HH group  (c1+c2): n = {n_hh}")
    print(f"  AIH group (c3+c4): n = {n_aih}")
    print(f"Alpha = {ALPHA}, two-tailed")

    # ── ANOVA: minimum detectable f ──────────────────────────────────
    mdes_f = find_mdes(lambda f: anova_power(f, n))
    mdes_eta2 = mdes_f ** 2 / (1 + mdes_f ** 2)

    print(f"\n{'─' * 65}")
    print("1. ONE-WAY ANOVA (prisoner_decision / stag_decision ~ treatment)")
    print(f"   Groups: k = {K}, df1 = {K-1}, df2 = {N_TOTAL - K}")
    print(f"   Minimum detectable effect at {TARGET_POWER:.0%} power:")
    print(f"     Cohen's f  = {mdes_f:.4f}")
    print(f"     eta-squared = {mdes_eta2:.4f}")

    print(f"\n   Power curve (ANOVA):")
    print(f"   {'f':>8s}  {'eta²':>8s}  {'power':>8s}  {'label':>12s}")
    for f_val in [0.10, 0.15, 0.20, 0.25, 0.30, 0.40]:
        pwr = anova_power(f_val, n)
        eta2 = f_val ** 2 / (1 + f_val ** 2)
        label = {0.10: "small", 0.25: "medium", 0.40: "large"}.get(f_val, "")
        print(f"   {f_val:8.2f}  {eta2:8.4f}  {pwr:8.3f}  {label:>12s}")

    # ── t-test: minimum detectable d ─────────────────────────────────
    mdes_d = find_mdes(lambda d: ttest_power(d, n_hh, n_aih))

    print(f"\n{'─' * 65}")
    print("2. INDEPENDENT t-TEST (HH vs AIH)")
    print(f"   n_HH = {n_hh}, n_AIH = {n_aih}, df = {n_hh + n_aih - 2}")
    print(f"   Minimum detectable effect at {TARGET_POWER:.0%} power:")
    print(f"     Cohen's d = {mdes_d:.4f}")

    print(f"\n   Power curve (t-test):")
    print(f"   {'d':>8s}  {'power':>8s}  {'label':>12s}")
    for d_val in [0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.80]:
        pwr = ttest_power(d_val, n_hh, n_aih)
        label = {0.20: "small", 0.50: "medium", 0.80: "large"}.get(d_val, "")
        print(f"   {d_val:8.2f}  {pwr:8.3f}  {label:>12s}")

    # ── Summary ──────────────────────────────────────────────────────
    print(f"\n{'─' * 65}")
    print("SUMMARY")
    print(f"  With N = {N_TOTAL} (allocation 1/6, 1/6, 2/6, 2/6), alpha = {ALPHA}:")
    print(f"  • ANOVA (4 groups): 80% power to detect Cohen's f >= {mdes_f:.3f} (eta² >= {mdes_eta2:.4f})")
    print(f"  • t-test (HH vs AIH): 80% power to detect Cohen's d >= {mdes_d:.3f}")
    print(f"\n  Conventional benchmarks (Cohen, 1988):")
    print(f"    ANOVA f:  small=0.10, medium=0.25, large=0.40")
    print(f"    t-test d: small=0.20, medium=0.50, large=0.80")
    print(f"\n  The design is well-powered to detect small-to-medium effects.")
    print("=" * 65)


if __name__ == "__main__":
    main()
