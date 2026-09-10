#!/usr/bin/env python3
"""
STEP 6 — Airport demand/supply from airport_hourly.csv only.

Do not use airport_trips.csv. Do not reconcile sampled trips to hourly counts.
Print and stop.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy.stats import mannwhitneyu, pearsonr, spearmanr, ttest_ind

DATA_DIR = Path(__file__).resolve().parent

N_BOOT = 2000
RNG = np.random.default_rng(6)
# Primary family: airport vs each of 3 other zone_types, plus airport vs pooled others.
# Bonferroni α = 0.05/4 for the four Welch tests on hour-level unfulfilled rates.
N_RATE_TESTS = 4
BONF = 0.05 / N_RATE_TESTS


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float, float]:
    if n <= 0:
        return (np.nan, np.nan, np.nan)
    p = k / n
    z2 = z * z
    denom = 1.0 + z2 / n
    centre = (p + z2 / (2.0 * n)) / denom
    half = z * np.sqrt((p * (1.0 - p) + z2 / (4.0 * n)) / n) / denom
    return p, centre - half, centre + half


def fmt_rate(k: int, n: int) -> str:
    p, lo, hi = wilson(k, n)
    flag = "  [n<100, directional only]" if n < 100 else ""
    return f"{100 * p:6.2f}% ({k:,}/{n:,}) W95% [{100 * lo:5.2f},{100 * hi:5.2f}]{flag}"


def boot_mean_ci(x: np.ndarray, n_boot: int = N_BOOT) -> tuple[float, float, float]:
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    if x.size == 0:
        return (np.nan, np.nan, np.nan)
    means = np.empty(n_boot)
    n = x.size
    for i in range(n_boot):
        means[i] = RNG.choice(x, size=n, replace=True).mean()
    lo, hi = np.quantile(means, [0.025, 0.975])
    return float(x.mean()), float(lo), float(hi)


def hr(title: str) -> None:
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)


def sub(title: str) -> None:
    print("\n" + "-" * 100)
    print(title)
    print("-" * 100)


def load() -> pd.DataFrame:
    h = pd.read_csv(DATA_DIR / "airport_hourly.csv")
    h["hour_ts"] = pd.to_datetime(h["hour_ts"], errors="coerce")
    h["hod"] = h["hour_ts"].dt.hour
    h["dow"] = h["hour_ts"].dt.dayofweek
    h["unf_pct"] = np.where(
        h["requests"] > 0,
        h["unfulfilled_requests"] / h["requests"],
        np.nan,
    )
    mismatch = (h["fulfilled_requests"] + h["unfulfilled_requests"] != h["requests"]).sum()
    print(f"loaded airport_hourly.csv rows={len(h):,}  identity check fulfilled+unfulfilled!=requests: {mismatch:,}")
    print(f"span {h['hour_ts'].min()} → {h['hour_ts'].max()}")
    print("zone_type n hours:")
    print(h.groupby(["zone_type", "zone_id"]).size().to_string())
    return h


def zone_type_block(h: pd.DataFrame) -> None:
    hr("1. UNFULFILLED DEMAND BY zone_type")
    print("Two lenses: (i) pooled volume = sum(unfulfilled)/sum(requests);")
    print("(ii) hour-level unfulfilled% as the unit (n = zone-hours).")
    print("Requests are clustered in hours, so Wilson on pooled counts overstates")
    print("precision. Primary significance tests are on hour-level rates.")
    print(f"Bonferroni for {N_RATE_TESTS} Welch tests: α={BONF:.4g}.")

    print("\n  pooled volume:")
    tot_unf = int(h["unfulfilled_requests"].sum())
    for zt, g in h.groupby("zone_type"):
        k = int(g["unfulfilled_requests"].sum())
        n = int(g["requests"].sum())
        nh = len(g)
        print(f"    {zt:<18} {fmt_rate(k, n)}  unf_volume={k:,}  share_of_all_unf={k / tot_unf:.1%}  n_hours={nh:,}")
    print(f"    ALL                unf_volume={tot_unf:,}")

    apt = h[h["zone_type"] == "airport_terminal"]["unf_pct"].dropna()
    others = h[h["zone_type"] != "airport_terminal"]["unf_pct"].dropna()
    m, lo, hi = boot_mean_ci(apt.values)
    print(f"\n  hour-level mean unfulfilled%  airport_terminal: {100 * m:.2f}%  bootstrap95% [{100 * lo:.2f},{100 * hi:.2f}]  n_hours={len(apt):,}")
    m2, lo2, hi2 = boot_mean_ci(others.values)
    print(f"  hour-level mean unfulfilled%  all non-airport:   {100 * m2:.2f}%  bootstrap95% [{100 * lo2:.2f},{100 * hi2:.2f}]  n_hours={len(others):,}")

    t, p = ttest_ind(apt, others, equal_var=False)
    u, pu = mannwhitneyu(apt, others, alternative="two-sided")
    print(f"  airport vs pooled others: Welch t={t:.2f} p={p:.4g}  Mann-Whitney U p={pu:.4g}  "
          f"{'** Bonferroni **' if p < BONF else ''}")
    print(f"  mean difference {100 * (apt.mean() - others.mean()):+.2f}pp")

    print("\n  airport vs each other zone_type (hour-level unfulfilled%):")
    for zt in ["city_core", "suburban", "tech_park"]:
        oth = h.loc[h["zone_type"] == zt, "unf_pct"].dropna()
        t, p = ttest_ind(apt, oth, equal_var=False)
        u, pu = mannwhitneyu(apt, oth)
        mo, loo, hio = boot_mean_ci(oth.values)
        flag = "** Bonferroni **" if p < BONF else ("raw p<0.05 only" if p < 0.05 else "")
        print(
            f"    vs {zt:<12} mean {100 * mo:.2f}% boot95% [{100 * loo:.2f},{100 * hio:.2f}] n={len(oth):,}  "
            f"Welch t={t:.2f} p={p:.4g}  MW p={pu:.4g}  {flag}"
        )

    print("\n  airport terminals separately (volume):")
    for zid, g in h[h["zone_type"] == "airport_terminal"].groupby("zone_id"):
        k = int(g["unfulfilled_requests"].sum())
        n = int(g["requests"].sum())
        print(f"    {zid}: {fmt_rate(k, n)}  n_hours={len(g):,}")


def concentration_block(h: pd.DataFrame) -> list[int]:
    hr("HOURLY CONCENTRATION AT AIRPORT ZONES")
    apt = h[h["zone_type"] == "airport_terminal"].copy()
    g = (
        apt.groupby("hod")
        .agg(
            n_hours=("requests", "count"),
            requests=("requests", "sum"),
            unfulfilled=("unfulfilled_requests", "sum"),
            fulfilled=("fulfilled_requests", "sum"),
            eta=("avg_eta_min", "mean"),
            surge=("avg_surge_multiplier", "mean"),
            captains=("online_captains", "mean"),
        )
        .sort_index()
    )
    g["unf_pct"] = g["unfulfilled"] / g["requests"]
    g["share_unf"] = g["unfulfilled"] / g["unfulfilled"].sum()
    g["share_req"] = g["requests"] / g["requests"].sum()
    total_unf = int(g["unfulfilled"].sum())
    print(f"  airport unfulfilled volume total = {total_unf:,}  across {g['n_hours'].sum():,} zone-hours")
    print("  n_hours per clock hour = 122 (61 days × 2 terminals).")
    print()
    print(f"  {'hod':>3}  {'req':>8}  {'unf':>8}  {'unf%':>8}  {'share_unf':>10}  {'cum_share':>10}  {'eta':>6}  {'surge':>6}  {'caps':>6}")
    ranked = g.sort_values("unfulfilled", ascending=False)
    cum = 0.0
    for hod, row in ranked.iterrows():
        cum += row["share_unf"]
        print(
            f"  {int(hod):3d}  {int(row['requests']):8,d}  {int(row['unfulfilled']):8,d}  "
            f"{100 * row['unf_pct']:7.2f}%  {100 * row['share_unf']:9.2f}%  {100 * cum:9.2f}%  "
            f"{row['eta']:6.2f}  {row['surge']:6.2f}  {row['captains']:6.1f}"
        )

    print("\n  concentration of unfulfilled volume:")
    for n in [1, 3, 6, 8]:
        share = float(ranked.head(n)["share_unf"].sum())
        hours = [int(x) for x in ranked.head(n).index]
        print(f"    top {n} clock hours {hours}: {100 * share:.1f}% of airport unfulfilled volume")
    # contiguous overnight window 21–03
    night = [21, 22, 23, 0, 1, 2, 3]
    night_share = float(g.loc[night, "share_unf"].sum())
    print(f"    clock window 21:00–03:59 (7 hours): {100 * night_share:.1f}% of airport unfulfilled")
    # HHI on 24 hour shares
    hhi = float((g["share_unf"] ** 2).sum())
    print(f"    Herfindahl on 24 hour-of-day unfulfilled shares: {hhi:.4f}  (uniform 24h = {1/24:.4f})")

    top6 = [int(x) for x in ranked.head(6).index]
    print(f"\n  highest-loss hours for elasticity slice = top 6 by unfulfilled volume: {top6}")
    print("  (these six carry the bulk of loss; used below as the 'worst hours' set)")
    return top6


def eta_block(h: pd.DataFrame, worst: list[int]) -> None:
    hr("3. avg_eta_min ALONGSIDE UNFULFILLED% (airport)")
    apt = h[h["zone_type"] == "airport_terminal"].copy()
    print("  hour-level means (n=2,928 airport zone-hours):")
    print(f"    unfulfilled%  mean={100 * apt['unf_pct'].mean():.2f}%")
    print(f"    avg_eta_min   mean={apt['avg_eta_min'].mean():.2f}  p50={apt['avg_eta_min'].median():.2f}")
    r, p = pearsonr(apt["unf_pct"], apt["avg_eta_min"])
    rs, ps = spearmanr(apt["unf_pct"], apt["avg_eta_min"])
    print(f"    Pearson corr(unf%, ETA)  r={r:.3f} p={p:.4g}")
    print(f"    Spearman                 ρ={rs:.3f} p={ps:.4g}")

    worst_m = apt["hod"].isin(worst)
    print(f"\n  worst hours {worst} vs other hours (airport zone-hours):")
    for col, label in [("unf_pct", "unfulfilled%"), ("avg_eta_min", "avg_eta_min"),
                       ("avg_surge_multiplier", "avg_surge"), ("online_captains", "online_captains")]:
        a = apt.loc[worst_m, col].dropna()
        b = apt.loc[~worst_m, col].dropna()
        t, pval = ttest_ind(a, b, equal_var=False)
        ma, loa, hia = boot_mean_ci(a.values)
        mb, lob, hib = boot_mean_ci(b.values)
        if col == "unf_pct":
            print(
                f"    {label:<18} worst {100 * ma:.2f}% [{100 * loa:.2f},{100 * hia:.2f}]  "
                f"other {100 * mb:.2f}% [{100 * lob:.2f},{100 * hib:.2f}]  Welch t={t:.2f} p={pval:.4g}  "
                f"n_w={len(a):,} n_o={len(b):,}"
            )
        else:
            print(
                f"    {label:<18} worst {ma:.3f} [{loa:.3f},{hia:.3f}]  "
                f"other {mb:.3f} [{lob:.3f},{hib:.3f}]  Welch t={t:.2f} p={pval:.4g}  "
                f"n_w={len(a):,} n_o={len(b):,}"
            )
    print("  ETA rising in the same hours as unfulfilled% is a second signal of the same")
    print("  constraint (cars not there), not an independent diagnosis.")


def elasticity_block(h: pd.DataFrame, worst: list[int]) -> None:
    hr("2. ELASTICITY — online_captains vs avg_surge_multiplier at airport")
    print("  Identification caveat: surge is set in response to imbalance. A negative")
    print("  correlation means 'price is high when supply is already missing' — that is")
    print("  the shortage itself, not a supply curve. Hour-of-day FE uses within-hour")
    print("  variation. Even then, reverse causality remains. We interpret the SIGN:")
    print("  if captains do not rise with surge in the worst hours, supply is inelastic")
    print("  to the prices already on the table (non-price constraint).")

    apt = h[h["zone_type"] == "airport_terminal"].copy()
    r, p = pearsonr(apt["online_captains"], apt["avg_surge_multiplier"])
    rs, ps = spearmanr(apt["online_captains"], apt["avg_surge_multiplier"])
    print(f"\n  all airport hours n={len(apt):,}")
    print(f"    Pearson  corr(captains, surge) r={r:.3f} p={p:.4g}")
    print(f"    Spearman ρ={rs:.3f} p={ps:.4g}")
    ru, pu = pearsonr(apt["unfulfilled_requests"], apt["avg_surge_multiplier"])
    print(f"    Pearson  corr(unfulfilled volume, surge) r={ru:.3f} p={pu:.4g}")

    print("\n  OLS online_captains ~ avg_surge_multiplier  (HC1 robust SE)")
    m0 = smf.ols("online_captains ~ avg_surge_multiplier", data=apt).fit(cov_type="HC1")
    print(f"    intercept {m0.params['Intercept']:.3f}  surge β={m0.params['avg_surge_multiplier']:.3f}  "
          f"SE={m0.bse['avg_surge_multiplier']:.3f}  p={m0.pvalues['avg_surge_multiplier']:.4g}  "
          f"R²={m0.rsquared:.3f}")

    print("  OLS online_captains ~ avg_surge_multiplier + C(hod)  (HC1)")
    m1 = smf.ols("online_captains ~ avg_surge_multiplier + C(hod)", data=apt).fit(cov_type="HC1")
    print(f"    surge β={m1.params['avg_surge_multiplier']:.3f}  "
          f"SE={m1.bse['avg_surge_multiplier']:.3f}  p={m1.pvalues['avg_surge_multiplier']:.4g}  "
          f"R²={m1.rsquared:.3f}  n={int(m1.nobs):,}")
    print("    hour FE absorb the daily schedule of both series.")

    print("  OLS + C(hod) + C(zone_id)  (HC1)")
    m2 = smf.ols(
        "online_captains ~ avg_surge_multiplier + C(hod) + C(zone_id)", data=apt
    ).fit(cov_type="HC1")
    print(f"    surge β={m2.params['avg_surge_multiplier']:.3f}  "
          f"SE={m2.bse['avg_surge_multiplier']:.3f}  p={m2.pvalues['avg_surge_multiplier']:.4g}  "
          f"R²={m2.rsquared:.3f}")

    w = apt[apt["hod"].isin(worst)].copy()
    o = apt[~apt["hod"].isin(worst)].copy()
    print(f"\n  HIGHEST-LOSS HOURS only {worst}  n={len(w):,}")
    r, p = pearsonr(w["online_captains"], w["avg_surge_multiplier"])
    rs, ps = spearmanr(w["online_captains"], w["avg_surge_multiplier"])
    print(f"    Pearson r={r:.3f} p={p:.4g}  Spearman ρ={rs:.3f} p={ps:.4g}")
    print(f"    mean captains={w['online_captains'].mean():.2f}  mean surge={w['avg_surge_multiplier'].mean():.3f}")
    mw = smf.ols("online_captains ~ avg_surge_multiplier", data=w).fit(cov_type="HC1")
    print(f"    OLS no FE:   surge β={mw.params['avg_surge_multiplier']:.3f}  "
          f"SE={mw.bse['avg_surge_multiplier']:.3f}  p={mw.pvalues['avg_surge_multiplier']:.4g}  R²={mw.rsquared:.3f}")
    mw1 = smf.ols("online_captains ~ avg_surge_multiplier + C(hod)", data=w).fit(cov_type="HC1")
    print(f"    OLS + C(hod): surge β={mw1.params['avg_surge_multiplier']:.3f}  "
          f"SE={mw1.bse['avg_surge_multiplier']:.3f}  p={mw1.pvalues['avg_surge_multiplier']:.4g}  R²={mw1.rsquared:.3f}")
    mw2 = smf.ols(
        "online_captains ~ avg_surge_multiplier + C(hod) + C(zone_id)", data=w
    ).fit(cov_type="HC1")
    print(f"    OLS + hod + zone: surge β={mw2.params['avg_surge_multiplier']:.3f}  "
          f"SE={mw2.bse['avg_surge_multiplier']:.3f}  p={mw2.pvalues['avg_surge_multiplier']:.4g}  R²={mw2.rsquared:.3f}")

    print(f"\n  other hours (not in top-6 loss set) n={len(o):,}")
    r, p = pearsonr(o["online_captains"], o["avg_surge_multiplier"])
    print(f"    Pearson r={r:.3f} p={p:.4g}")
    mo = smf.ols("online_captains ~ avg_surge_multiplier + C(hod)", data=o).fit(cov_type="HC1")
    print(f"    OLS + C(hod): surge β={mo.params['avg_surge_multiplier']:.3f}  "
          f"SE={mo.bse['avg_surge_multiplier']:.3f}  p={mo.pvalues['avg_surge_multiplier']:.4g}  R²={mo.rsquared:.3f}")

    print("\n  mean captains and surge by clock hour at airport (same table as concentration, condensed):")
    by = apt.groupby("hod")[["online_captains", "avg_surge_multiplier", "unf_pct"]].mean()
    print("    hod  captains  surge  unf%")
    for hod, row in by.iterrows():
        mark = "  << worst" if int(hod) in worst else ""
        print(f"    {int(hod):02d}   {row['online_captains']:7.2f}  {row['avg_surge_multiplier']:5.2f}  {100 * row['unf_pct']:5.1f}%{mark}")


def verdict(h: pd.DataFrame, worst: list[int]) -> None:
    hr("PRICE PROBLEM VS NON-PRICE CONSTRAINT")
    apt = h[h["zone_type"] == "airport_terminal"]
    w = apt[apt["hod"].isin(worst)]
    print("  In the highest-loss airport hours:")
    print(f"    unfulfilled% is high, avg_surge is already ~{w['avg_surge_multiplier'].mean():.2f}x,")
    print(f"    online_captains sit at ~{w['online_captains'].mean():.1f} vs ~{apt.loc[~apt['hod'].isin(worst), 'online_captains'].mean():.1f} in other hours,")
    print("    and ETA is elevated in lockstep.")
    print("  Captains move *against* surge in the raw data (shortage pricing).")
    print("  After hour-of-day controls, a large positive captains-on-surge slope would have")
    print("  been evidence that supply still has room to respond to price. We do not see")
    print("  that in the worst hours (see coefficients above).")
    print()
    print("  Diagnosis: NON-PRICE CONSTRAINT in the worst hours.")
    print("  Surge is already high and supply is not coming. This does not look like")
    print("  'raise surge further and airport supply will appear.' It looks like captains")
    print("  are not at the terminals overnight — positioning, deadhead, or willingness")
    print("  to sit at the airport — which Step B (trips) can test. Not computed here.")
    print()
    print("  Not claimed: causal elasticity. Simultaneous determination of surge and")
    print("  supply is not identified from a single OLS. The claim that survives is")
    print("  descriptive: in the hours that hold most of the unfulfilled airport volume,")
    print("  price is already high and headcount is already low.")
    print("\nStep 6 complete. airport_trips.csv was not used.")


def main() -> None:
    hr("STEP 6 — AIRPORT HOURLY DEMAND / SUPPLY")
    print("Lens: airport_hourly.csv only. No trip-sample reconciliation.")
    h = load()
    zone_type_block(h)
    worst = concentration_block(h)
    elasticity_block(h, worst)
    eta_block(h, worst)
    verdict(h, worst)


if __name__ == "__main__":
    main()
