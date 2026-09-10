#!/usr/bin/env python3
"""
STEP 3 — Where volume is lost in the mature ∩ has-doc_events funnel.

Does not merge the zero-doc_events never-attempted cohort into stage
capture-failure stats. No campaign evaluation. No recommendations.
"""

from __future__ import annotations

from math import comb
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy.stats import chi2_contingency, norm

DATA_DIR = Path(__file__).resolve().parent
EXTRACTION_TS = pd.Timestamp("2026-06-30 23:59:00")
EXTRACTION_LABEL = "2026-06-30 23:59 IST"

SEQ = {
    "Auto": ["DL", "RC", "AADHAAR", "PERMIT", "FITNESS", "INSURANCE"],
    "Cab": ["DL", "RC", "AADHAAR", "PERMIT", "FITNESS", "INSURANCE"],
    "ERickshaw": ["DL", "RC", "AADHAAR", "FITNESS", "INSURANCE"],
}
STAGE_DOCS = ["DL", "RC", "AADHAAR", "PERMIT", "FITNESS", "INSURANCE"]
SEGMENT_COLS = ["city", "vehicle_type", "device_tier", "acquisition_channel", "app_language"]

# Family of primary tests: 6 stages × 5 factors = 30 chi-square tests.
N_PRIMARY_TESTS = 6 * 5
BONFERRONI_ALPHA = 0.05 / N_PRIMARY_TESTS


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float, float]:
    if n <= 0:
        return (np.nan, np.nan, np.nan)
    k, n = int(k), int(n)
    p = k / n
    z2 = z * z
    denom = 1.0 + z2 / n
    centre = (p + z2 / (2.0 * n)) / denom
    half = z * np.sqrt((p * (1.0 - p) + z2 / (4.0 * n)) / n) / denom
    return p, centre - half, centre + half


def fmt_rate(k: int, n: int) -> str:
    p, lo, hi = wilson(k, n)
    if n <= 0 or np.isnan(p):
        return "n/a"
    flag = "  [n<100, directional only]" if n < 100 else ""
    return f"{100 * p:6.2f}% ({k:,}/{n:,}) W95% [{100 * lo:5.2f},{100 * hi:5.2f}]{flag}"


def two_prop_z(k1: int, n1: int, k2: int, n2: int) -> tuple[float, float]:
    """Unpooled two-proportion z-test (H0: p1=p2). Returns (z, p_value)."""
    if min(n1, n2) <= 0:
        return (np.nan, np.nan)
    p1, p2 = k1 / n1, k2 / n2
    p = (k1 + k2) / (n1 + n2)
    se = np.sqrt(p * (1 - p) * (1 / n1 + 1 / n2))
    if se == 0:
        return (0.0, 1.0)
    z = (p1 - p2) / se
    pval = 2 * norm.sf(abs(z))
    return float(z), float(pval)


def hr(title: str) -> None:
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)


def sub(title: str) -> None:
    print("\n" + "-" * 100)
    print(title)
    print("-" * 100)


def load_base() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    captains = pd.read_csv(DATA_DIR / "captains.csv")
    approvals = pd.read_csv(DATA_DIR / "approvals.csv")
    docs = pd.read_csv(DATA_DIR / "doc_events.csv")
    captains["signup_ts"] = pd.to_datetime(captains["signup_ts"], errors="coerce")
    captains["signup_age_days"] = (
        EXTRACTION_TS - captains["signup_ts"]
    ).dt.total_seconds() / 86400.0
    passed = (
        docs.loc[docs["event_type"] == "verification_pass", ["captain_id", "doc_type"]]
        .drop_duplicates()
        .assign(v=1)
        .pivot_table(index="captain_id", columns="doc_type", values="v", aggfunc="max")
        .fillna(0)
        .astype(int)
    )
    for col in STAGE_DOCS:
        if col not in passed.columns:
            passed[col] = 0
    n_events = docs.groupby("captain_id").size().rename("n_doc_events")
    df = captains.merge(approvals, on="captain_id", how="left")
    df = df.merge(passed, on="captain_id", how="left")
    df = df.merge(n_events, on="captain_id", how="left")
    for col in STAGE_DOCS:
        df[col] = df[col].fillna(0).astype(int)
    df["n_doc_events"] = df["n_doc_events"].fillna(0).astype(int)
    df["has_doc_events"] = df["n_doc_events"] > 0
    ip_max = float(df.loc[df["final_status"] == "in_progress", "signup_age_days"].max())
    df["mature"] = df["signup_age_days"] > ip_max
    df["_ip_max"] = ip_max
    return df, docs, captains


def attach_cleared(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    ac = out["vehicle_type"].isin(["Auto", "Cab"])
    er = out["vehicle_type"].eq("ERickshaw")
    out["cleared_DL"] = out["DL"].eq(1)
    out["cleared_RC"] = out["cleared_DL"] & out["RC"].eq(1)
    out["cleared_AADHAAR"] = out["cleared_RC"] & out["AADHAAR"].eq(1)
    out["cleared_PERMIT"] = ac & out["cleared_AADHAAR"] & out["PERMIT"].eq(1)
    out["cleared_FITNESS"] = (
        (ac & out["cleared_PERMIT"] & out["FITNESS"].eq(1))
        | (er & out["cleared_AADHAAR"] & out["FITNESS"].eq(1))
    )
    out["cleared_INSURANCE"] = out["cleared_FITNESS"] & out["INSURANCE"].eq(1)
    out["atrisk_DL"] = True
    out["atrisk_RC"] = out["cleared_DL"]
    out["atrisk_AADHAAR"] = out["cleared_RC"]
    out["atrisk_PERMIT"] = ac & out["cleared_AADHAAR"]
    out["atrisk_FITNESS"] = (ac & out["cleared_PERMIT"]) | (er & out["cleared_AADHAAR"])
    out["atrisk_INSURANCE"] = out["cleared_FITNESS"]
    return out


def attach_uploads(df: pd.DataFrame, docs: pd.DataFrame) -> pd.DataFrame:
    ids = set(df["captain_id"])
    sub_docs = docs[docs["captain_id"].isin(ids)]
    uploaded = (
        sub_docs.groupby(["captain_id", "doc_type"])
        .size()
        .reset_index(name="n")
        .assign(uploaded=1)
        .pivot_table(index="captain_id", columns="doc_type", values="uploaded", aggfunc="max")
        .fillna(0)
        .astype(int)
    )
    uploaded = uploaded.add_prefix("upl_")
    out = df.merge(uploaded, on="captain_id", how="left")
    for doc in STAGE_DOCS:
        col = f"upl_{doc}"
        if col not in out.columns:
            out[col] = 0
        out[col] = out[col].fillna(0).astype(int)
    return out


def chi2_factor(y: pd.Series, x: pd.Series) -> dict:
    ct = pd.crosstab(x, y)
    if ct.shape[0] < 2 or ct.shape[1] < 2:
        return {"chi2": np.nan, "p": np.nan, "dof": np.nan, "min_exp": np.nan, "n": int(len(y))}
    chi2, p, dof, exp = chi2_contingency(ct)
    return {
        "chi2": float(chi2),
        "p": float(p),
        "dof": int(dof),
        "min_exp": float(exp.min()),
        "n": int(ct.values.sum()),
    }


def print_segment_table(at: pd.DataFrame, doc: str, factor: str) -> None:
    y = at[f"cleared_{doc}"].astype(int)
    x = at[factor]
    stats = chi2_factor(y, x)
    pflag = ""
    if np.isfinite(stats["p"]):
        if stats["p"] < BONFERRONI_ALPHA:
            pflag = f"  ** significant vs Bonferroni α={BONFERRONI_ALPHA:.5f} **"
        elif stats["p"] < 0.05:
            pflag = "  (raw p<0.05 but NOT below Bonferroni; treat as exploratory)"
    print(
        f"    chi-square {factor} × passed {doc}: "
        f"χ²={stats['chi2']:.2f} dof={stats['dof']} p={stats['p']:.4g} "
        f"n={stats['n']:,} min_exp={stats['min_exp']:.2f}{pflag}"
    )
    levels = list(x.dropna().unique())
    # pairwise vs the largest at-risk level (reference)
    sizes = x.value_counts()
    ref = sizes.index[0]
    ref_mask = x.eq(ref)
    k_ref = int(y[ref_mask].sum())
    n_ref = int(ref_mask.sum())
    n_pairs = comb(len(sizes), 2) if len(sizes) >= 2 else 1
    pair_alpha = 0.05 / max(n_pairs, 1)
    print(f"    pairwise z-tests vs largest at-risk group '{ref}' (n={n_ref:,}); "
          f"within-factor Bonferroni α=0.05/{n_pairs}={pair_alpha:.4g}")
    rows = []
    for lvl, n in sizes.items():
        k = int(y[x.eq(lvl)].sum())
        p, lo, hi = wilson(k, n)
        z, pz = two_prop_z(k, n, k_ref, n_ref) if lvl != ref else (0.0, 1.0)
        lost = n - k
        flag = "n<100 directional" if n < 100 else ""
        sig = ""
        if lvl != ref and np.isfinite(pz):
            if pz < pair_alpha:
                sig = "sig vs ref (Bonferroni)"
            elif pz < 0.05:
                sig = "raw p<0.05 only"
        rows.append(
            {
                "level": lvl,
                "n_atrisk": n,
                "n_passed": k,
                "n_lost": lost,
                "rate": None if n == 0 else k / n,
                "lo": lo,
                "hi": hi,
                "z_vs_ref": z,
                "p_vs_ref": pz,
                "note": " ".join([flag, sig]).strip(),
            }
        )
        print(
            f"      {str(lvl):<18} passed {fmt_rate(k, n)}  lost={lost:,}  "
            f"z_vs_{ref}={z:6.2f} p={pz:.4g}  {flag} {sig}".rstrip()
        )
    return


def stage_block(funnel: pd.DataFrame, docs: pd.DataFrame, doc: str) -> None:
    at = funnel[funnel[f"atrisk_{doc}"]].copy()
    n_at = len(at)
    n_pass = int(at[f"cleared_{doc}"].sum())
    n_lost = n_at - n_pass
    upl = at[f"upl_{doc}"].eq(1)
    never = (~at[f"cleared_{doc}"]) & (~upl)
    attempted_fail = (~at[f"cleared_{doc}"]) & upl
    sub(f"STAGE {doc}: at-risk n={n_at:,}  passed={n_pass:,}  lost={n_lost:,}")
    print(f"  step conversion {fmt_rate(n_pass, n_at)}")
    print("  among the lost, two failure modes (not mixed with the zero-doc signup cohort):")
    print(f"    never uploaded this doc:     {fmt_rate(int(never.sum()), n_lost) if n_lost else 'n/a'}   "
          f"share of at-risk {fmt_rate(int(never.sum()), n_at)}")
    print(f"    uploaded but never passed:   {fmt_rate(int(attempted_fail.sum()), n_lost) if n_lost else 'n/a'}   "
          f"share of at-risk {fmt_rate(int(attempted_fail.sum()), n_at)}")

    # failure reasons among verification_fail on this doc for at-risk who didn't pass
    ids_fail = set(at.loc[~at[f"cleared_{doc}"], "captain_id"])
    fails = docs[
        (docs["captain_id"].isin(ids_fail))
        & (docs["doc_type"] == doc)
        & (docs["event_type"] == "verification_fail")
    ]
    print(f"  verification_fail events on {doc} among at-risk drop-offs: {len(fails):,}")
    if len(fails):
        print("  failure_reason counts:")
        print("    " + fails["failure_reason"].value_counts(dropna=False).to_string().replace("\n", "\n    "))

    print("  segmentation (one factor at a time; not a full cross-cut):")
    for factor in SEGMENT_COLS:
        if doc == "PERMIT" and factor == "vehicle_type":
            # at-risk is already Auto/Cab only
            print("    vehicle_type at PERMIT: ERickshaw not in denominator (not required). Auto vs Cab:")
        print_segment_table(at, doc, factor)


def attempt_pass_rates(funnel: pd.DataFrame, docs: pd.DataFrame, doc: str) -> None:
    """
    One verification outcome per (captain, doc, attempt_no) in the mature event cohort.
    Pass rate by attempt_no. Later-attempt denoms are selected on prior failure.
    """
    ids = set(funnel["captain_id"])
    ev = docs[
        (docs["captain_id"].isin(ids))
        & (docs["doc_type"] == doc)
        & (docs["event_type"].isin(["verification_pass", "verification_fail"]))
    ].copy()
    if ev.empty:
        print(f"  no verification events for {doc}")
        return
    # collapse to one row per attempt
    g = (
        ev.groupby(["captain_id", "attempt_no"])["event_type"]
        .agg(lambda s: "verification_pass" if (s == "verification_pass").any() else "verification_fail")
        .reset_index()
    )
    g["passed"] = g["event_type"].eq("verification_pass").astype(int)
    sub(f"ATTEMPT-LEVEL PASS RATES — {doc} (mature ∩ has-doc_events captains)")
    print("  unit = (captain, attempt_no) with a verification outcome.")
    print("  attempt 2/3 are conditional on still not having passed; this is not a randomized retry.")
    counts = []
    for a in [1, 2, 3]:
        sl = g[g["attempt_no"] == a]
        k, n = int(sl["passed"].sum()), len(sl)
        counts.append((a, k, n))
        print(f"    attempt {a}: {fmt_rate(k, n)}")
    # overall chi-square attempt × pass
    ct = pd.crosstab(g["attempt_no"], g["passed"])
    if ct.shape[0] >= 2 and ct.shape[1] >= 2:
        chi2, p, dof, exp = chi2_contingency(ct)
        print(f"  chi-square attempt_no × passed: χ²={chi2:.2f} dof={dof} p={p:.4g} min_exp={exp.min():.2f}")
    print("  pairwise two-proportion z-tests (Bonferroni α=0.05/3=0.01667):")
    pairs = [(1, 2), (2, 3), (1, 3)]
    for a, b in pairs:
        _, k1, n1 = counts[a - 1]
        _, k2, n2 = counts[b - 1]
        z, pz = two_prop_z(k1, n1, k2, n2)
        p1 = k1 / n1 if n1 else np.nan
        p2 = k2 / n2 if n2 else np.nan
        direction = ""
        if n1 and n2:
            if p2 > p1 and a < b:
                direction = "later attempt HIGHER — consistent with capture/UX (retry can work)"
            elif p2 < p1 and a < b:
                direction = "later attempt LOWER — mix of selection (harder remainder) and/or eligibility"
        sig = "sig Bonferroni" if (np.isfinite(pz) and pz < 0.05 / 3) else (
            "raw p<0.05 only" if (np.isfinite(pz) and pz < 0.05) else "not sig"
        )
        print(f"    attempt {a} vs {b}: Δ={100 * (p2 - p1):+.2f}pp  z={z:.2f} p={pz:.4g}  {sig}")
        print(f"      {direction}")
    # retry among attempt-1 failures
    a1_fail = set(g.loc[(g["attempt_no"] == 1) & (g["passed"] == 0), "captain_id"])
    a2 = g[g["attempt_no"] == 2]
    retried = a2[a2["captain_id"].isin(a1_fail)]
    print(
        f"  among attempt-1 failures n={len(a1_fail):,}: "
        f"took attempt 2: {fmt_rate(len(retried), len(a1_fail))}; "
        f"passed attempt 2 | retried: {fmt_rate(int(retried['passed'].sum()), len(retried))}"
    )


def zero_doc_block(df: pd.DataFrame, docs: pd.DataFrame) -> None:
    hr("3. MATURE ZERO-DOC_EVENTS (n expected 1,416) — never-attempted, not capture-failure")
    print("This cohort signed up, reached a terminal dropped_in_docs status, and has zero rows")
    print("in doc_events. That is a different failure mode from RC/Insurance verification fail.")
    print("They are NOT merged into the stage segmentation above.")
    mature = df[df["mature"]]
    zero = mature[~mature["has_doc_events"]].copy()
    ev = mature[mature["has_doc_events"]].copy()
    print(f"  mature zero-doc n={len(zero):,}  mature with events n={len(ev):,}  mature total={len(mature):,}")
    print(f"  final_status: {zero['final_status'].value_counts().to_dict()}")
    print(f"  docs_cleared value counts: {zero['docs_cleared'].value_counts().to_dict()}")
    print(f"  last_stage_reached: {zero['last_stage_reached'].value_counts(dropna=False).to_dict()}")

    print("\n  share of mature signups who never produce a doc_event, by segment:")
    print("  (k = zero-doc captains, n = all mature signups in that level — includes both modes)")
    for factor in SEGMENT_COLS:
        print(f"\n  {factor}:")
        y = (~mature["has_doc_events"]).astype(int)
        stats = chi2_factor(y, mature[factor])
        pflag = ""
        # 5 chi-squares here; Bonferroni among this family of 5
        a = 0.05 / 5
        if np.isfinite(stats["p"]) and stats["p"] < a:
            pflag = f"  ** sig vs Bonferroni α={a:.3g} **"
        elif np.isfinite(stats["p"]) and stats["p"] < 0.05:
            pflag = "  (raw p<0.05, not Bonferroni)"
        print(f"    χ²={stats['chi2']:.2f} p={stats['p']:.4g} n={stats['n']:,}{pflag}")
        ref = mature[factor].value_counts().index[0]
        for lvl, n in mature[factor].value_counts().items():
            k = int((~mature.loc[mature[factor].eq(lvl), "has_doc_events"]).sum())
            z, pz = two_prop_z(
                k, n,
                int((~mature.loc[mature[factor].eq(ref), "has_doc_events"]).sum()),
                int(mature[factor].eq(ref).sum()),
            )
            extra = "  [n<100, directional only]" if n < 100 else ""
            print(f"      {str(lvl):<18} never-attempted {fmt_rate(k, n)}  vs {ref}: z={z:.2f} p={pz:.4g}{extra}")

    print("\n  composition of the 1,416 vs the 21,024 (column %):")
    for factor in SEGMENT_COLS:
        a = zero[factor].value_counts(normalize=True)
        b = ev[factor].value_counts(normalize=True)
        vals = pd.concat(
            [zero[factor].reset_index(drop=True), ev[factor].reset_index(drop=True)],
            ignore_index=True,
        )
        lab = pd.Series(["zero"] * len(zero) + ["events"] * len(ev))
        ct = pd.crosstab(vals, lab)
        chi2, p, dof, exp = chi2_contingency(ct)
        print(f"\n    {factor}  χ²={chi2:.2f} p={p:.4g}")
        tab = pd.concat(
            [zero[factor].value_counts().rename("n_zero"), ev[factor].value_counts().rename("n_events")],
            axis=1,
        ).fillna(0).astype(int)
        tab["pct_zero"] = 100 * tab["n_zero"] / tab["n_zero"].sum()
        tab["pct_events"] = 100 * tab["n_events"] / tab["n_events"].sum()
        print(tab.to_string())

    print("\n  time from signup to abandonment: NOT inferable.")
    print("    dropped_in_docs has null decision_ts; zero-doc captains have no event_ts.")
    print("    signup_age is time from signup to EXTRACT, not time-to-abandon.")
    print("    signup_age_days among zero-doc mature:")
    print(zero["signup_age_days"].describe(percentiles=[0.1, 0.25, 0.5, 0.75, 0.9]).to_string())
    print("    signup calendar month:")
    print(zero["signup_ts"].dt.to_period("M").value_counts().sort_index().to_string())

    nudges = pd.read_csv(DATA_DIR / "nudges.csv")
    nudges["sent_ts"] = pd.to_datetime(nudges["sent_ts"], errors="coerce")
    zids = set(zero["captain_id"])
    eids = set(ev["captain_id"])
    n_z = nudges[nudges["captain_id"].isin(zids)]
    n_e = nudges[nudges["captain_id"].isin(eids)]
    print(
        f"\n  nudge coverage: zero-doc captains with ≥1 nudge "
        f"{fmt_rate(n_z['captain_id'].nunique(), len(zero))}; "
        f"event captains {fmt_rate(n_e['captain_id'].nunique(), len(ev))}"
    )
    z_nudge, pz = two_prop_z(n_z["captain_id"].nunique(), len(zero), n_e["captain_id"].nunique(), len(ev))
    print(f"    two-proportion z (nudge coverage zero vs events): z={z_nudge:.2f} p={pz:.4g}")
    if len(n_z):
        first = n_z.groupby("captain_id")["sent_ts"].min()
        merged = zero.merge(first.rename("first_nudge_ts"), on="captain_id", how="left")
        has = merged["first_nudge_ts"].notna()
        delay = (merged.loc[has, "first_nudge_ts"] - merged.loc[has, "signup_ts"]).dt.total_seconds() / 86400
        print("    days signup → first nudge among zero-doc who were nudged:")
        print(delay.describe().to_string())
        print("    this is time-to-first-touch, not time-to-abandon.")


def confound_vehicle_city(funnel: pd.DataFrame) -> None:
    hr("2. CONFOUND CHECK — ERickshaw vs Auto/Cab approval, controlling for city")
    y = (funnel["final_status"] == "approved").astype(int)
    print(f"  sample: mature ∩ has-doc_events n={len(funnel):,}; approved={int(y.sum()):,}")
    print("\n  univariate approved | vehicle_type:")
    for lvl, n in funnel["vehicle_type"].value_counts().items():
        k = int(((funnel["vehicle_type"] == lvl) & (funnel["final_status"] == "approved")).sum())
        print(f"    {lvl:<12} {fmt_rate(k, n)}")
    # Auto/Cab pooled vs ERickshaw
    er = funnel["vehicle_type"].eq("ERickshaw")
    k_er, n_er = int(y[er].sum()), int(er.sum())
    k_ac, n_ac = int(y[~er].sum()), int((~er).sum())
    z, p = two_prop_z(k_er, n_er, k_ac, n_ac)
    print(f"\n  ERickshaw vs Auto+Cab pooled: {fmt_rate(k_er, n_er)} vs {fmt_rate(k_ac, n_ac)}")
    print(f"    two-proportion z={z:.2f} p={p:.4g}  Δ={100 * (k_er / n_er - k_ac / n_ac):+.2f}pp")

    print("\n  univariate approved | city:")
    for lvl, n in funnel["city"].value_counts().items():
        k = int(((funnel["city"] == lvl) & (funnel["final_status"] == "approved")).sum())
        print(f"    {lvl:<12} {fmt_rate(k, n)}")

    print("\n  city × vehicle_type (counts) — ERickshaw concentration:")
    ct_n = pd.crosstab(funnel["city"], funnel["vehicle_type"], margins=True)
    print(ct_n.to_string())
    print("\n  city × vehicle_type approval rate (k/n):")
    for city in funnel["city"].unique():
        for vt in ["Auto", "Cab", "ERickshaw"]:
            sl = funnel[(funnel["city"] == city) & (funnel["vehicle_type"] == vt)]
            k = int((sl["final_status"] == "approved").sum())
            n = len(sl)
            flag = "  [n<100, directional only]" if n < 100 else ""
            print(f"    {city:<12} {vt:<12} {fmt_rate(k, n)}{flag}")

    chi_vt = chi2_factor(funnel["vehicle_type"], funnel["city"])
    print(
        f"\n  association city × vehicle_type: χ²={chi_vt['chi2']:.1f} "
        f"p={chi_vt['p']:.4g} (confounding is plausible if this is large)"
    )

    print("\n  logistic regression: approved ~ C(vehicle_type) + C(city)")
    print("  reference levels = first categorical in pandas (shown in model).")
    model_df = funnel[["final_status", "vehicle_type", "city"]].copy()
    model_df["approved"] = (model_df["final_status"] == "approved").astype(int)
    # lock references: Auto, and Hyderabad (largest city) for interpretability
    model_df["vehicle_type"] = pd.Categorical(
        model_df["vehicle_type"], categories=["Auto", "Cab", "ERickshaw"]
    )
    model_df["city"] = pd.Categorical(
        model_df["city"], categories=["Hyderabad", "Delhi", "Bangalore", "Pune"]
    )
    fit = smf.logit("approved ~ C(vehicle_type) + C(city)", data=model_df).fit(disp=False)
    print(fit.summary().as_text())
    print("\n  odds ratios and 95% CI:")
    params = fit.params
    conf = fit.conf_int()
    pvals = fit.pvalues
    for name in params.index:
        or_ = np.exp(params[name])
        lo, hi = np.exp(conf.loc[name])
        print(
            f"    {name:<40} OR={or_:6.3f}  95%CI [{lo:5.3f}, {hi:5.3f}]  "
            f"p={pvals[name]:.4g}  logit={params[name]:.4f}"
        )

    print("\n  sensitivity: approved ~ C(vehicle_type) + C(city) + C(device_tier) + C(acquisition_channel)")
    model_df2 = funnel[
        ["final_status", "vehicle_type", "city", "device_tier", "acquisition_channel"]
    ].copy()
    model_df2["approved"] = (model_df2["final_status"] == "approved").astype(int)
    model_df2["vehicle_type"] = pd.Categorical(
        model_df2["vehicle_type"], categories=["Auto", "Cab", "ERickshaw"]
    )
    fit2 = smf.logit(
        "approved ~ C(vehicle_type) + C(city) + C(device_tier) + C(acquisition_channel)",
        data=model_df2,
    ).fit(disp=False)
    for name in [ix for ix in fit2.params.index if "vehicle_type" in ix]:
        or_ = np.exp(fit2.params[name])
        lo, hi = np.exp(fit2.conf_int().loc[name])
        print(
            f"    {name}: OR={or_:.3f}  95%CI [{lo:.3f}, {hi:.3f}]  p={fit2.pvalues[name]:.4g}"
        )

    er_or = np.exp(fit.params["C(vehicle_type)[T.ERickshaw]"])
    er_p = fit.pvalues["C(vehicle_type)[T.ERickshaw]"]
    print("\n  READ-OUT (not a recommendation):")
    print("  If ERickshaw OR vs Auto stays >1 with p below 0.05 after city is in the model,")
    print("  the vehicle_type association is not fully explained by Delhi concentration.")
    print(f"  Observed: ERickshaw vs Auto OR={er_or:.3f}, p={er_p:.4g} (city-adjusted).")

    # Device and channel both move RC/Insurance; they may be collinear.
    print("\n  additional confound check (rigor bar): device_tier vs channel on RC and Insurance pass")
    ct_dc = pd.crosstab(funnel["device_tier"], funnel["acquisition_channel"])
    chi2, p, dof, exp = chi2_contingency(ct_dc)
    print(f"  device_tier × acquisition_channel in funnel: χ²={chi2:.1f} p={p:.4g}")
    print(ct_dc.to_string())

    rc = funnel[funnel["atrisk_RC"]].copy()
    rc["passed"] = rc["cleared_RC"].astype(int)
    rc["device_tier"] = pd.Categorical(rc["device_tier"], categories=["low", "mid", "high"])
    fit_rc = smf.logit(
        "passed ~ C(device_tier) + C(acquisition_channel) + C(city) + C(vehicle_type)",
        data=rc,
    ).fit(disp=False)
    print("\n  logit P(pass RC | at-risk) ~ device + channel + city + vehicle")
    for name in fit_rc.params.index:
        if name == "Intercept":
            continue
        or_ = np.exp(fit_rc.params[name])
        lo, hi = np.exp(fit_rc.conf_int().loc[name])
        print(
            f"    {name:<45} OR={or_:5.3f}  95%CI [{lo:5.3f}, {hi:5.3f}]  p={fit_rc.pvalues[name]:.4g}"
        )

    ins = funnel[funnel["atrisk_INSURANCE"]].copy()
    ins["passed"] = ins["cleared_INSURANCE"].astype(int)
    ins["device_tier"] = pd.Categorical(ins["device_tier"], categories=["low", "mid", "high"])
    fit_ins = smf.logit(
        "passed ~ C(device_tier) + C(acquisition_channel) + C(city) + C(vehicle_type)",
        data=ins,
    ).fit(disp=False)
    print("\n  logit P(pass INSURANCE | at-risk) ~ device + channel + city + vehicle")
    for name in fit_ins.params.index:
        if name == "Intercept":
            continue
        or_ = np.exp(fit_ins.params[name])
        lo, hi = np.exp(fit_ins.conf_int().loc[name])
        print(
            f"    {name:<45} OR={or_:5.3f}  95%CI [{lo:5.3f}, {hi:5.3f}]  p={fit_ins.pvalues[name]:.4g}"
        )


def main() -> None:
    hr("STEP 3 — WHERE VOLUME IS LOST")
    print(f"extract: {EXTRACTION_LABEL}")
    print("Primary cohort: mature ∩ has-doc_events from Step 2.")
    print(
        f"Multiple-comparison note: {N_PRIMARY_TESTS} primary chi-square tests "
        f"(6 stages × 5 factors). Bonferroni α = 0.05/{N_PRIMARY_TESTS} = {BONFERRONI_ALPHA:.5f}."
    )
    print("Pairwise z-tests inside a factor use a separate within-factor Bonferroni.")
    print("Single 'leaks' that only appear in one pairwise cut still need independent confirmation.")
    print("n<100: directional only. No 5-way city×vehicle×device×channel×language cross-cut.")

    df, docs, _ = load_base()
    ip_max = float(df["_ip_max"].iloc[0])
    print(f"\nmature cutoff: signup_age > {ip_max:.6f} days (max in_progress age)")

    funnel = df[df["mature"] & df["has_doc_events"]].copy()
    funnel = attach_cleared(funnel)
    funnel = attach_uploads(funnel, docs)
    print(f"funnel n={len(funnel):,} (expect 21,024)")
    assert len(funnel) == 21024, f"unexpected funnel n={len(funnel)}"

    hr("1. STAGE-BY-STAGE DROP-OFF, SEGMENTED")
    print("At-risk = reached the previous required stage (vehicle-aware for PERMIT/FITNESS).")
    print("passed  = verification_pass on this required doc (sequential prefix).")
    for doc in STAGE_DOCS:
        stage_block(funnel, docs, doc)

    # Attempt-level for large volume-loss stages: RC (largest), Insurance (2nd),
    # plus FITNESS and PERMIT which are also >2.5k lost. DL/Aadhaar smaller.
    hr("ATTEMPT-LEVEL PASS RATES FOR LARGE STAGE LOSSES")
    print("Step 2 volume lost: RC 5,405; Insurance 3,289; Fitness 2,653; Permit 2,616;")
    print("Aadhaar 1,540; DL 1,166. Attempt rates run for RC, INSURANCE, FITNESS, PERMIT.")
    print("Question: do later attempts pass higher (capture/UX) or lower (eligibility/selection)?")
    for doc in ["RC", "INSURANCE", "FITNESS", "PERMIT"]:
        attempt_pass_rates(funnel, docs, doc)

    confound_vehicle_city(funnel)
    zero_doc_block(df, docs)

    print("\nStep 3 complete. No recommendations, no campaign evaluation.")


if __name__ == "__main__":
    main()
