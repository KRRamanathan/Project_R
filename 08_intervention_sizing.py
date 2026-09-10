#!/usr/bin/env python3
"""
STEP 8 — Intervention sizing (final step before memo/deck).

Size only what the evidence supports. Do not add overlapping or unproven
mechanisms. Channel-replication and CAMP_WA_002 are test designs, not
bankable monthly volumes. Airport Return Assurance is a costed trip-leg
product, not an onboarding-captain add.

Re-derives C1a/C1b cohorts, attempt-level pass rates, fos RC conversion,
Step 4(a) self-serve funnel membership, and ARA-eligible trip-legs from
source CSVs. Print and stop.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm

DATA_DIR = Path(__file__).resolve().parent
EXTRACTION_TS = pd.Timestamp("2026-06-30 23:59:00")
EXTRACTION_LABEL = "2026-06-30 23:59 IST"

SELF_SERVE = ["organic_app", "paid_digital"]
FOS = "fos_field"
STAGE_DOCS = ["DL", "RC", "AADHAAR", "PERMIT", "FITNESS", "INSURANCE"]
CAPTURE_REASONS = {"image_blurred", "ocr_low_confidence", "details_not_legible"}
WORST_HOD = {21, 22, 23, 0, 1, 2, 3}  # 21:00–03:59 inclusive
DAYS_PER_MONTH = 30.437
# Step 4 combined (a)+(b) approved/month at 50/75/100% gap close — restated, not re-banked.
CHANNEL_GAP_PER_MONTH = {0.50: 127.9, 0.75: 191.8, 1.00: 255.8}
CHANNEL_GAP_A_PER_MONTH_100 = 216.5
CHANNEL_GAP_A_APPROVED_100 = 1181.0

# Step 7 net-cycle means (₹, completed trips) — used as the comparison, not re-estimated.
NET_WORST_SUBURBAN = 24.9
NET_REST_SUBURBAN = 56.5
NET_WORST_CITY_CORE = 104.7
NET_GAP_VS_REST_SUB = NET_REST_SUBURBAN - NET_WORST_SUBURBAN  # 31.6
NET_GAP_VS_WORST_CORE = NET_WORST_CITY_CORE - NET_WORST_SUBURBAN  # 79.8


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


def hr(title: str) -> None:
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)


def sub(title: str) -> None:
    print("\n" + "-" * 100)
    print(title)
    print("-" * 100)


def n_per_arm_two_prop(
    p_ctrl: float, delta: float, alpha: float = 0.05, power: float = 0.80
) -> float:
    """Two-sample equal-n, two-sided proportion test, unpooled variance at design p's."""
    p_trt = p_ctrl + delta
    if min(p_ctrl, p_trt) <= 0 or max(p_ctrl, p_trt) >= 1 or delta == 0:
        return np.nan
    za = float(norm.ppf(1 - alpha / 2))
    zb = float(norm.ppf(power))
    return (za + zb) ** 2 * (p_ctrl * (1 - p_ctrl) + p_trt * (1 - p_trt)) / (delta ** 2)


def load_onboarding() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    captains = pd.read_csv(DATA_DIR / "captains.csv")
    approvals = pd.read_csv(DATA_DIR / "approvals.csv")
    docs = pd.read_csv(DATA_DIR / "doc_events.csv")
    nudges = pd.read_csv(DATA_DIR / "nudges.csv")
    captains["signup_ts"] = pd.to_datetime(captains["signup_ts"], errors="coerce")
    captains["signup_age_days"] = (
        EXTRACTION_TS - captains["signup_ts"]
    ).dt.total_seconds() / 86400.0
    docs["event_ts"] = pd.to_datetime(docs["event_ts"], errors="coerce")
    nudges["sent_ts"] = pd.to_datetime(nudges["sent_ts"], errors="coerce")
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
    uploaded = (
        docs.groupby(["captain_id", "doc_type"])
        .size()
        .reset_index(name="n")
        .assign(u=1)
        .pivot_table(index="captain_id", columns="doc_type", values="u", aggfunc="max")
        .fillna(0)
        .astype(int)
        .add_prefix("upl_")
    )
    df = df.merge(uploaded, on="captain_id", how="left")
    for col in STAGE_DOCS:
        c = f"upl_{col}"
        if c not in df.columns:
            df[c] = 0
        df[c] = df[c].fillna(0).astype(int)
    ac = df["vehicle_type"].isin(["Auto", "Cab"])
    er = df["vehicle_type"].eq("ERickshaw")
    df["cleared_DL"] = df["DL"].eq(1)
    df["cleared_RC"] = df["cleared_DL"] & df["RC"].eq(1)
    df["cleared_AADHAAR"] = df["cleared_RC"] & df["AADHAAR"].eq(1)
    df["cleared_PERMIT"] = ac & df["cleared_AADHAAR"] & df["PERMIT"].eq(1)
    df["cleared_FITNESS"] = (ac & df["cleared_PERMIT"] & df["FITNESS"].eq(1)) | (
        er & df["cleared_AADHAAR"] & df["FITNESS"].eq(1)
    )
    df["cleared_INSURANCE"] = df["cleared_FITNESS"] & df["INSURANCE"].eq(1)
    df["atrisk_RC"] = df["cleared_DL"]
    df["atrisk_INSURANCE"] = df["cleared_FITNESS"]
    df["self_serve"] = df["acquisition_channel"].isin(SELF_SERVE)
    return df, docs, nudges, captains


def capture_only_never_pass(
    funnel: pd.DataFrame, docs: pd.DataFrame, doc: str
) -> pd.Index:
    """Mature event-funnel, uploaded stage, never passed, all fail reasons capture-class."""
    at = funnel[funnel[f"atrisk_{doc}"]].copy()
    lost_upl = at[(~at[f"cleared_{doc}"]) & (at[f"upl_{doc}"] == 1)]
    fails = docs[
        docs["captain_id"].isin(set(lost_upl["captain_id"]))
        & docs["doc_type"].eq(doc)
        & docs["event_type"].eq("verification_fail")
    ]
    per = (
        fails.groupby("captain_id")["failure_reason"]
        .agg(lambda s: set(s.dropna()))
        .reset_index()
    )
    per["only_capture"] = per["failure_reason"].apply(
        lambda s: len(s) > 0 and s <= CAPTURE_REASONS
    )
    return pd.Index(per.loc[per["only_capture"], "captain_id"])


def attempt_pass_table(
    funnel: pd.DataFrame, docs: pd.DataFrame, doc: str, mask: pd.Series | None = None
) -> dict[int, tuple[int, int]]:
    ids = set(funnel.loc[mask, "captain_id"] if mask is not None else funnel["captain_id"])
    ev = docs[
        docs["captain_id"].isin(ids)
        & docs["doc_type"].eq(doc)
        & docs["event_type"].isin(["verification_pass", "verification_fail"])
    ]
    g = (
        ev.groupby(["captain_id", "attempt_no"])["event_type"]
        .agg(lambda s: "verification_pass" if (s == "verification_pass").any() else "verification_fail")
        .reset_index()
    )
    g["passed"] = g["event_type"].eq("verification_pass")
    out = {}
    for a in (1, 2, 3):
        sl = g[g["attempt_no"] == a]
        out[a] = (int(sl["passed"].sum()), int(len(sl)))
    return out


def main() -> None:
    df, docs, nudges, _captains = load_onboarding()
    mature = df[df["mature"]].copy()
    funnel = mature[mature["has_doc_events"]].copy()
    ip_max = float(df["_ip_max"].iloc[0])

    tmin, tmax = mature["signup_ts"].min(), mature["signup_ts"].max()
    span_days = (tmax.normalize() - tmin.normalize()).days + 1
    months = span_days / DAYS_PER_MONTH

    hr("STEP 8 — INTERVENTION SIZING")
    print(f"Extract clock: {EXTRACTION_LABEL}  (naive timestamps, same convention as prior steps)")
    print(f"in_progress max age = {ip_max:.6f} d  → mature = signup_age > that cut")
    print(
        f"mature signup window: {tmin} → {tmax}  "
        f"({span_days} inclusive days ≈ {months:.3f} months of {DAYS_PER_MONTH}d)"
    )
    print(f"mature n={len(mature):,}  event-funnel n={len(funnel):,}")
    print("per-month = cohort count / that month-count (June truncated by the mature cut).")
    print("Insurance is excluded from C1a. C1b is a separate, non-deferral intervention.")
    print("vehicle_type is not a sizing cut (Step 3: structural, pseudo-R² 0.0065).")

    # ------------------------------------------------------------------
    # Re-derive C1a / C1b and grounding rates
    # ------------------------------------------------------------------
    rc_ids = capture_only_never_pass(funnel, docs, "RC")
    ins_ids = capture_only_never_pass(funnel, docs, "INSURANCE")
    c1a = funnel[funnel["captain_id"].isin(rc_ids)].copy()
    c1b = funnel[funnel["captain_id"].isin(ins_ids)].copy()
    overlap_ab = set(rc_ids) & set(ins_ids)

    rc_att = attempt_pass_table(funnel, docs, "RC")
    ins_att = attempt_pass_table(funnel, docs, "INSURANCE")
    rc_att_ss = attempt_pass_table(funnel, docs, "RC", funnel["self_serve"])

    fos_rc_at = funnel[funnel["atrisk_RC"] & funnel["acquisition_channel"].eq(FOS)]
    fos_rc_k = int(fos_rc_at["cleared_RC"].sum())
    fos_rc_n = int(len(fos_rc_at))
    fos_rc_p = fos_rc_k / fos_rc_n

    rc_a3_k, rc_a3_n = rc_att[3]
    rc_a3_p = rc_a3_k / rc_a3_n
    ins_p = {a: ins_att[a][0] / ins_att[a][1] for a in (1, 2, 3)}

    approved_given_cleared = funnel[funnel["cleared_INSURANCE"]]
    p_appr_cleared = (
        approved_given_cleared["final_status"].eq("approved").mean()
        if len(approved_given_cleared)
        else np.nan
    )
    n_cleared = len(approved_given_cleared)
    k_appr_cleared = int(approved_given_cleared["final_status"].eq("approved").sum())

    hr("1. C1a — RC-ONLY PROVISIONAL ACTIVATION (deferrable stage; Insurance excluded)")
    print("  Sizing base: RC capture-only-fail, same definition as Step 4 C1:")
    print("    mature ∩ has-doc_events, at-risk for RC (passed DL), uploaded RC,")
    print("    never passed RC, ALL verification_fail reasons ∈")
    print("    {image_blurred, ocr_low_confidence, details_not_legible}.")
    print(f"  C1a n = {len(c1a):,}  (expected 1,637)")
    print(f"  C1b n = {len(c1b):,}  (expected 411)  — NOT in this intervention")
    print(f"  C1a ∩ C1b = {len(overlap_ab):,}  (must be 0 to keep them separate)")
    print("  Why RC is deferrable and Insurance is not: RC is a vehicle-identity")
    print("  capture/UX problem with no pre-ride passenger-liability exposure.")
    print("  Insurance is the liability document and must still clear before the")
    print("  captain rides — that is C1b, a different product, sized in §2.")
    print("  Mechanism sized here: provisional activation with a 10-day grace")
    print("  window for in-person RC verification (show-up × in-person pass).")
    print("  This table is RC-resolution of this cohort. It does NOT multiply")
    print("  through remaining Aadhaar→Insurance conversion. If remaining stages")
    print("  still bind after RC is deferred, these figures are an upper bound")
    print("  on additional fully-approved captains from C1a alone.")

    print("\n  C1a channel mix:")
    for ch, nch in c1a["acquisition_channel"].value_counts().items():
        print(f"    {ch:<16} {fmt_rate(int(nch), len(c1a))}")
    n_c1a_ss = int(c1a["self_serve"].sum())
    n_c1a_fos = int(c1a["acquisition_channel"].eq(FOS).sum())
    n_c1a_other = len(c1a) - n_c1a_ss - n_c1a_fos
    print(f"    self-serve share {fmt_rate(n_c1a_ss, len(c1a))}")
    print(f"    fos_field share  {fmt_rate(n_c1a_fos, len(c1a))}")
    print(f"    other channels   {fmt_rate(n_c1a_other, len(c1a))}")

    sub("Grounded in-person pass-rate range (not an assumed 85–90%)")
    print("  Floor = RC attempt-3 pass rate, mature event-funnel, all channels")
    print(f"    (Step 3 headline): {fmt_rate(rc_a3_k, rc_a3_n)}")
    print("    Unit = (captain, attempt_no=3) with a verification outcome;")
    print("    conditional on still not having passed after 1 and 2 — not an RCT.")
    ss_a3_k, ss_a3_n = rc_att_ss[3]
    print("  Same attempt-3 rate, self-serve only (check, not the floor used):")
    print(f"    {fmt_rate(ss_a3_k, ss_a3_n)}")
    print("  Ceiling = fos_field assisted RC step conversion (cleared_RC | at-risk),")
    print(f"    event-funnel (Step 4): {fmt_rate(fos_rc_k, fos_rc_n)}")
    print("  Using overall att-3 74.12% as the floor per the Step 3 number named")
    print("  in the brief, even though that figure is all-channel not self-serve.")
    print("  In-person assist is not guaranteed to beat fos's 78.41% (fos recruits")
    print("  a different pool); 78.41% is a plausible assisted ceiling, not a target.")

    flow = len(c1a) / months
    print(f"\n  monthly flow of this stock: {len(c1a):,} / {months:.3f} = {flow:,.1f} captains/month")
    print("  additional approved/month = flow × P(show up in 10-day grace) × P(in-person pass)")
    print("  Show-up is unobserved in this extract — sensitivity only (40/60/80/100%).")

    show_rates = [0.40, 0.60, 0.80, 1.00]
    pass_rates = [("floor att-3", rc_a3_p), ("ceiling fos RC", fos_rc_p)]
    sub("C1a sensitivity — additional captains/month (RC resolved under provisional path)")
    hdr = f"{'show-up':>10}  " + "  ".join(f"{lab:>22}" for lab, _ in pass_rates)
    print("  " + hdr)
    c1a_grid = {}
    for s in show_rates:
        cells = []
        for lab, p in pass_rates:
            val = flow * s * p
            c1a_grid[(s, lab)] = val
            cells.append(f"{val:22.1f}")
        print(f"  {100 * s:9.0f}%  " + "  ".join(cells))
    print("\n  same grid as additional captains over the mature window (not /month):")
    for s in show_rates:
        cells = []
        for lab, p in pass_rates:
            cells.append(f"{len(c1a) * s * p:22.1f}")
        print(f"  {100 * s:9.0f}%  " + "  ".join(cells))

    # Reference cells for the rollup
    c1a_lo = c1a_grid[(0.40, "floor att-3")]
    c1a_mid = c1a_grid[(0.60, "floor att-3")]
    c1a_hi = c1a_grid[(0.80, "ceiling fos RC")]
    c1a_cap = c1a_grid[(1.00, "ceiling fos RC")]
    print("\n  Headline range for the rollup (not a CI):")
    print(f"    conservative 40% show × att-3 floor:     {c1a_lo:.1f} / month")
    print(f"    central     60% show × att-3 floor:     {c1a_mid:.1f} / month")
    print(f"    optimistic  80% show × fos ceiling:     {c1a_hi:.1f} / month")
    print(f"    mechanical cap 100% × fos ceiling:      {c1a_cap:.1f} / month  (not a forecast)")
    print("  Confidence: MEDIUM on the cohort identity (capture-only is observed);")
    print("  LOW–MEDIUM on monthly additional approved (show-up is unobserved;")
    print("  remaining stages not applied; att-3 / fos rates are ceilings from")
    print("  different selected populations, not experimental in-person pass rates).")

    # ------------------------------------------------------------------
    # C1b
    # ------------------------------------------------------------------
    hr("2. C1b — INSURANCE CAPTURE-QUALITY UX (no deferral; must clear before ride)")
    print("  Sizing base: Insurance capture-only-fail, same definition as Step 4.")
    print(f"  C1b n = {len(c1b):,}")
    print(f"  monthly flow: {len(c1b):,} / {months:.3f} = {len(c1b) / months:,.1f} / month")
    print("  Product: guided capture at upload (blur/OCR feedback) — same UX")
    print("  pattern as C1a capture-quality, but Insurance is NOT deferrable.")
    print("  Pass-rate grounding is Insurance attempt 1→2→3 (Step 3), NOT RC:")
    for a in (1, 2, 3):
        k, n = ins_att[a]
        print(f"    attempt {a}: {fmt_rate(k, n)}")
    print("  These 411 currently pass at 0%. Counterfactual: under capture UX as")
    print("  good as the observed attempt-k pass rate, that fraction would pass.")
    print("  This is a grounding range, not an experiment. Attempt 2/3 are")
    print("  selected on prior failure.")
    print(
        f"  P(approved | cleared all required docs) in event-funnel: "
        f"{fmt_rate(k_appr_cleared, n_cleared)}"
    )
    print("  Insurance pass = cleared-all for this cohort (they are already at-risk")
    print("  for Insurance). Approved = that pass × P(approved | cleared-all).")

    flow_b = len(c1b) / months
    sub("C1b sensitivity — additional approved/month (kept separate from C1a)")
    print(f"  {'Insurance pass anchor':<28} {'P(pass)':>8}  {'cleared/mo':>12}  {'approved/mo':>12}")
    c1b_appr = {}
    for a, lab in [(1, "att-1 floor 67.36%"), (2, "att-2 73.82%"), (3, "att-3 76.36%")]:
        p = ins_p[a]
        cleared_mo = flow_b * p
        appr_mo = cleared_mo * p_appr_cleared
        c1b_appr[a] = appr_mo
        print(f"  {lab:<28} {100 * p:7.2f}%  {cleared_mo:12.1f}  {appr_mo:12.1f}")
    print("\n  Headline range: "
          f"{c1b_appr[1]:.1f} – {c1b_appr[2]:.1f} – {c1b_appr[3]:.1f} approved/month")
    print("  Confidence: MEDIUM on the 411 identity; LOW–MEDIUM on the pass")
    print("  counterfactual (retry pass rates are not a randomized UX treatment).")
    print("  Do not add C1b into C1a. Overlap of the two cohorts is 0, but the")
    print("  mechanisms are different (deferral+in-person vs upload-time UX with")
    print("  a hard Insurance gate). They may be funded together because they")
    print("  target disjoint captains.")

    # ------------------------------------------------------------------
    # Overlap C1a vs Step 4(a)
    # ------------------------------------------------------------------
    hr("3. OVERLAP — C1a vs Step 4(a) self-serve RC stage-conversion gap")
    ss_funnel = funnel[funnel["self_serve"]].copy()
    ss_rc_gap_pop = ss_funnel[ss_funnel["atrisk_RC"] & ~ss_funnel["cleared_RC"]].copy()
    # Step 4(a) sizing base = self-serve event-funnel starters (all of them enter the sequential CF)
    ss_starters = ss_funnel
    c1a_ids = set(c1a["captain_id"])
    ss_funnel_ids = set(ss_funnel["captain_id"])
    ss_rc_gap_ids = set(ss_rc_gap_pop["captain_id"])
    ov_funnel = c1a_ids & ss_funnel_ids
    ov_rc_gap = c1a_ids & ss_rc_gap_ids

    print("  Step 4(a) is the sequential counterfactual: self-serve (organic_app +")
    print("  paid_digital) mature ∩ has-doc_events starters converting at fos_field")
    print("  device-specific stage rates. The RC slice of that gap lives inside")
    print("  self-serve captains who reached RC (passed DL) and did not pass RC.")
    print(f"  self-serve event-funnel starters (a base):     {len(ss_starters):,}")
    print(f"  self-serve at-risk RC, not passed (RC-gap pop): {len(ss_rc_gap_pop):,}")
    print(f"  C1a total:                                      {len(c1a):,}")
    print(f"  C1a ∩ (a) starters:                             {len(ov_funnel):,}")
    print(f"  C1a ∩ self-serve RC-not-passed:                 {len(ov_rc_gap):,}")
    print("  These two overlap counts match: every self-serve C1a captain is in")
    print("  the RC-not-passed at-risk set (they uploaded and failed capture-only).")
    print(f"  C1a outside (a) — fos + referral + gc_telecalling: {len(c1a) - len(ov_rc_gap):,}")
    print(f"    of which fos_field: {n_c1a_fos:,}")
    print(f"    of which other:     {n_c1a_other:,}")

    print("\n  OVERLAP COUNT TO PUT IN THE DECK: "
          f"{len(ov_rc_gap):,} captains sit in both C1a and the Step 4(a)")
    print("  self-serve RC stage-conversion gap population.")
    print("  They are the same people, counted under two mechanisms:")
    print("    C1a: 10-day provisional RC + in-person verification")
    print("    (a): make self-serve convert like fos at RC (and every later stage)")
    print("  Do not add C1a monthly additional approved to the 128–256/month")
    print("  channel-replication range. Those are alternative estimates of an")
    print("  overlapping opportunity (plus C1a also covers 911 non-self-serve")
    print("  capture-fail captains that (a) does not).")

    # Overlap-adjusted combined figure (illustrative; not bankable as a sum)
    # Non-overlapping C1a piece can sit next to channel (a) without double-counting
    # the 726, IF channel (a) is treated as the vehicle for self-serve. Channel
    # (a) is still unproven — report the arithmetic, then exclude from the total.
    c1a_non_ss = c1a[~c1a["self_serve"]]
    flow_non_ss = len(c1a_non_ss) / months
    flow_ss = len(ov_rc_gap) / months
    print("\n  Overlap-adjusted arithmetic (illustrative union of *captains*, not")
    print("  a recommendation to add unproven channel lift to C1a):")
    print(f"    C1a self-serve (the overlap) monthly flow:     {flow_ss:,.1f}")
    print(f"    C1a non-self-serve monthly flow:               {flow_non_ss:,.1f}")
    print("    If C1a is the RC-capture vehicle: size C1a (all 1,637) and do")
    print("    not add channel-replication. Residual (a) opportunity is later")
    print("    stages + RC never-upload + non-capture RC fails — unproven, not sized.")
    print("    If channel-replication were proven AND C1a were still run for")
    print("    non-self-serve only, additional C1a at the central cell")
    print("    (60% show × att-3 floor) on the 911 = "
          f"{flow_non_ss * 0.60 * rc_a3_p:.1f}/month")
    print("    sitting beside Step 4(a) 216.5/month at 100% close")
    print(f"    → illustrative combined {flow_non_ss * 0.60 * rc_a3_p + CHANNEL_GAP_A_PER_MONTH_100:.1f}/month.")
    print("    That combined figure still treats 216.5 as bankable, which it is")
    print("    not (selection bias). Report it as an overlap-adjusted *ceiling")
    print("    arithmetic*, then exclude it from the summed total in §7.")
    combined_ceiling_central = flow_non_ss * 0.60 * rc_a3_p + CHANNEL_GAP_A_PER_MONTH_100
    combined_ceiling_lo = flow_non_ss * 0.40 * rc_a3_p + 127.9  # 50% a+b close + C1a non-ss
    print("    Alternative (stricter): C1a (central, all 1,637) OR channel")
    print(f"    128–256/month — take one frame, not both. C1a central = {c1a_mid:.1f}/month.")

    # ------------------------------------------------------------------
    # Channel-replication test design
    # ------------------------------------------------------------------
    hr("4. CHANNEL-REPLICATION GAP — NOT A BANKABLE NUMBER; TEST DESIGN ONLY")
    print("  Restated from Step 4, not re-derived as a forecast:")
    print("    (a) stage-conversion among event-funnel self-serve, 100% close:")
    print(f"        +{CHANNEL_GAP_A_APPROVED_100:,.0f} approved  ({CHANNEL_GAP_A_PER_MONTH_100:.1f}/month)")
    print("    (a)+(b) including never-attempt, 50/75/100% of the fos vs")
    print("    self-serve gap: 128 / 192 / 256 approved per month.")
    print("  This is an unproven ceiling IF zero selection difference between")
    print("  fos_field and self-serve. fos is in-person recruitment; the extract")
    print("  cannot separate who they recruit from how they onboard. Do not put")
    print("  128–256 in a board pack as 'we will get this'. Do not add it to C1a.")

    ss_appr_k = int(ss_funnel["final_status"].eq("approved").sum())
    ss_appr_n = len(ss_funnel)
    ss_rc_at = ss_funnel[ss_funnel["atrisk_RC"]]
    ss_rc_k = int(ss_rc_at["cleared_RC"].sum())
    ss_rc_n = len(ss_rc_at)
    print(f"\n  Current self-serve event-funnel approved: {fmt_rate(ss_appr_k, ss_appr_n)}")
    print(f"  Current self-serve RC step conversion:    {fmt_rate(ss_rc_k, ss_rc_n)}")
    print(f"  fos_field RC step conversion (ceiling):   {fmt_rate(fos_rc_k, fos_rc_n)}")

    sub("Controlled pilot design")
    print("  Population: new organic_app and paid_digital signups (the self-serve")
    print("  channels behind the gap). Exclude fos_field, referral, gc_telecalling.")
    print("  Assignment: individual-level randomization at signup (or at first")
    print("  doc-upload intent) to assisted onboarding support vs current self-serve.")
    print("  Treatment: time-bounded human assist (video/centre/call) aimed at the")
    print("  fos operational experience — document capture and stage progression —")
    print("  NOT a change in who is recruited. That is the point of the test:")
    print("  hold the signup pool fixed, vary assist.")
    print("  Control: status-quo self-serve funnel, same eligibility and docs.")
    print("  Do not send CAMP_WA_002 differentially across arms (see §5).")
    print("  Primary endpoint (confirmatory): P(approved) within a pre-registered")
    print("  mature window (signup age > ~16 days, matching the empirical cut).")
    print("  Secondary: P(RC pass | reached RC); P(cleared all required docs);")
    print("  time-to-RC-pass; never-attempt rate.")
    print("  Guardrails: no peeking at 128–256 as a success bar; success is a")
    print("  pre-registered MDE on the randomized contrast. Stratify by channel")
    print("  (organic vs paid) and device_tier.")

    p_appr = ss_appr_k / ss_appr_n
    p_rc = ss_rc_k / ss_rc_n
    sub("Approximate sample size (two-arm, 1:1, two-sided α=0.05, 80% power)")
    print("  Formula: n_per_arm = (z_{α/2}+z_β)^2 [p_c(1-p_c)+p_t(1-p_t)] / δ^2")
    print("  Control rates locked to observed self-serve event-funnel.")
    print("  fos's +6.4pp approved / +35.9pp RC gaps are NOT the design MDE —")
    print("  those mix selection and operations. Design for a smaller, operationally")
    print("  plausible lift.")
    print(f"\n  {'endpoint':<40} {'p_ctrl':>8}  {'MDE':>8}  {'n/arm':>8}  {'n total':>8}")
    rows = [
        ("approved (primary)", p_appr, 0.03),
        ("approved (primary)", p_appr, 0.05),
        ("RC pass | reached RC", p_rc, 0.05),
        ("RC pass | reached RC", p_rc, 0.08),
    ]
    n_primary_5pp = None
    for name, p0, mde in rows:
        n1 = n_per_arm_two_prop(p0, mde)
        ntot = 2 * n1
        if name.startswith("approved") and abs(mde - 0.05) < 1e-9:
            n_primary_5pp = n1
        print(
            f"  {name:<40} {100 * p0:7.2f}%  {100 * mde:6.1f}pp  "
            f"{n1:8,.0f}  {ntot:8,.0f}"
        )
    print("  Attrition/immature: inflate n by the immature share (~signup last")
    print("  16 days of the experiment calendar). For a ~2-month enrollment,")
    print("  budget ~15–20% extra. No clustering inflation if assignment is")
    print("  individual; inflate if assist is centre-batched.")
    print("  Practical read: ~900/arm detects a 5pp approved lift; ~2,400/arm")
    print("  for a 3pp lift. That is a real experiment, not a 50-person ops trial.")
    print("  A null at 5pp would reject 'fos rates are portable to organic/paid")
    print("  signups' as an operating assumption, which is the decision this")
    print("  test is for.")

    # ------------------------------------------------------------------
    # Campaign RCT only
    # ------------------------------------------------------------------
    hr("5. CAMP_WA_002 — NO SCALE-UP SIZING; RCT DESIGN ONLY")
    print("  Observational result (Step 5) stands: among mature delivered")
    print("  recipients, clicked vs not Δ = −1.51pp approved, Wald95% [−3.61, +0.58],")
    print("  z=−1.41 p=0.16. Deck number: 0 pp completion lift. Do not scale 5×.")
    print("  30.5% overlap with other campaigns; send is ~2.2d post-signup;")
    print("  ~89% already through RC — so the null is informative, not a dead-end send.")

    # Eligible pool for the proposed RCT (sizing the *experiment*, not the campaign)
    other_campaigns = nudges[nudges["campaign_id"] != "CAMP_WA_002"]
    wa = nudges[nudges["campaign_id"] == "CAMP_WA_002"].copy()
    # data-quality exclusion used in Step 5
    bad_click = nudges["clicked"].eq(1) & nudges["delivered"].eq(0)
    print(f"  data-quality rows clicked=1 & delivered=0 (all nudges): {int(bad_click.sum()):,}")

    has_other = set(other_campaigns["captain_id"].unique())
    rc_cleared_ss = funnel[funnel["self_serve"] & funnel["cleared_RC"]].copy()
    exclusive = rc_cleared_ss[~rc_cleared_ss["captain_id"].isin(has_other)]
    print(f"  mature event-funnel, self-serve, RC-cleared: {len(rc_cleared_ss):,}")
    print(f"  of whom have no other-campaign row in nudges.csv: {len(exclusive):,}")
    print("  (historical pool over the mature window — RCT enrollment is prospective.)")

    sub("RCT to fund (already proposed in Step 5 — not modified)")
    print("  Population: RC-cleared self-serve captains (organic_app + paid_digital).")
    print("  Exclusion: any captain already assigned to another campaign (overlap).")
    print("  Also exclude the clicked=1 & delivered=0 logging failure from analysis.")
    print("  Assignment: randomized send vs no-send of CAMP_WA_002, 1:1, at the")
    print("  current send trigger (post-RC, ~2.2 days after signup — keep the")
    print("  window; do not expand to pre-RC).")
    print("  Primary endpoints (pre-register both, split α or gate):")
    print("    (i)  Aadhaar verification_pass after assignment")
    print("    (ii) final approved within the mature window")
    print("  Secondary: click-among-delivered (send arm), Permit/Fitness/Insurance")
    print("  progression, time-to-Aadhaar.")
    print("  Analysis: ITT on assignment, not on click. Do not scale on a")
    print("  significant click-rate; the decision metric is completion.")
    print("  No monthly 'if we scale 5×' volume is reported. This item is a")
    print("  test design and is excluded from the §7 summed total.")

    # ------------------------------------------------------------------
    # Airport Return Assurance
    # ------------------------------------------------------------------
    hr("6. AIRPORT RETURN ASSURANCE — eligible trip-legs and payout sensitivity")
    print("  airport_trips.csv is SAMPLED. Counts are not a city census.")
    print("  Sampling fraction is unknown. ₹/month below is sample-implied,")
    print("  scaled only by the file's own date span — not market ₹.")

    t = pd.read_csv(DATA_DIR / "airport_trips.csv")
    t["captain_cancelled"] = pd.to_numeric(t["captain_cancelled"], errors="coerce")
    t["got_return_fare_within_20min"] = pd.to_numeric(
        t["got_return_fare_within_20min"], errors="coerce"
    )
    t["cancelled"] = t["captain_cancelled"].eq(1)
    t["got_return"] = t["got_return_fare_within_20min"].eq(1)
    t["completed"] = ~t["cancelled"]
    t["request_ts"] = pd.to_datetime(t["request_ts"], errors="coerce")
    t["hod"] = t["request_ts"].dt.hour
    t["worst_hours"] = t["hod"].isin(WORST_HOD)
    tmin_t, tmax_t = t["request_ts"].min(), t["request_ts"].max()
    span_t = (tmax_t.normalize() - tmin_t.normalize()).days + 1
    months_t = span_t / DAYS_PER_MONTH
    print(f"  trip file span: {tmin_t} → {tmax_t}  ({span_t} inclusive days ≈ {months_t:.3f} months)")

    elig = t[
        t["drop_zone_type"].eq("suburban")
        & t["worst_hours"]
        & t["completed"]
        & ~t["got_return"]
    ].copy()
    print(
        "  Eligible = suburban drop × worst hours 21:00–03:59 × completed "
        "× no return fare within 20 min"
    )
    print(f"  eligible trip-legs in file: {len(elig):,}")
    elig_mo = len(elig) / months_t
    print(f"  sample-implied eligible legs/month: {elig_mo:,.1f}")

    fare = elig["fare_inr"].dropna()
    local_avg = float(fare.mean())
    local_med = float(fare.median())
    print(f"  local avg fare (mean of eligible legs): ₹{local_avg:.1f}  "
          f"median ₹{local_med:.1f}  n={len(fare):,}")
    print("  Payout = 30/50/70% of that local mean (not of city-wide fare).")

    # hourly context for new-headcount — airport unfulfilled / captains, not a census of trips
    h = pd.read_csv(DATA_DIR / "airport_hourly.csv")
    h["hour_ts"] = pd.to_datetime(h["hour_ts"], errors="coerce")
    h["hod"] = h["hour_ts"].dt.hour
    h["worst"] = h["hod"].isin(WORST_HOD)
    apt = h[h["zone_type"].eq("airport_terminal")].copy()
    print("\n  airport_hourly (census-like marketplace file — for headcount context only):")
    for name, m in [
        ("worst 21–03 airport", apt["worst"]),
        ("rest of day airport", ~apt["worst"]),
    ]:
        sl = apt[m]
        print(
            f"    {name}: hours={len(sl):,}  "
            f"mean online_captains={sl['online_captains'].mean():.1f}  "
            f"mean unfulfilled={sl['unfulfilled_requests'].mean():.1f}  "
            f"unfulfilled share="
            f"{sl['unfulfilled_requests'].sum() / sl['requests'].sum():.1%}"
        )
    cap_worst = float(apt.loc[apt["worst"], "online_captains"].mean())
    cap_rest = float(apt.loc[~apt["worst"], "online_captains"].mean())
    unf_worst_mo = (
        apt.loc[apt["worst"], "unfulfilled_requests"].sum()
        / ((apt["hour_ts"].max().normalize() - apt["hour_ts"].min().normalize()).days + 1)
        * DAYS_PER_MONTH
    )
    print(f"    mean captain deficit worst vs rest: {cap_rest - cap_worst:.1f} online captains")
    print(f"    sample-free unfulfilled requests/month in worst airport hours: {unf_worst_mo:,.0f}")
    print("    (hourly is not sampled the way trips are; do not multiply ARA")
    print("    sample legs by this to 'inflate to market' — no join key supports that.)")

    sub("Payout sensitivity vs the net-₹-per-cycle gap this is trying to close")
    print("  Step 7 net_cycle means on completed trips (independent penalties,")
    print("  not a mix-shift: overnight mix of suburban is unchanged, χ² p=0.12):")
    print(f"    worst × suburban:     ₹{NET_WORST_SUBURBAN}")
    print(f"    rest  × suburban:     ₹{NET_REST_SUBURBAN}   gap vs worst-sub ₹{NET_GAP_VS_REST_SUB:.1f}")
    print(f"    worst × city_core:    ₹{NET_WORST_CITY_CORE}  gap vs worst-sub ₹{NET_GAP_VS_WORST_CORE:.1f}")
    print("  ARA pays on the eligible deadhead leg. It can close a captain's")
    print("  overnight-suburban penalty; it cannot turn a suburban drop into")
    print("  city_core geography.")
    print(f"\n  {'payout':>8}  {'₹/leg':>10}  {'sample ₹/mo':>14}  {'vs rest-sub gap':>16}  {'vs worst-core gap':>18}")
    ara_costs = {}
    for pct in (0.30, 0.50, 0.70):
        pay = pct * local_avg
        cost_mo = elig_mo * pay
        ara_costs[pct] = (pay, cost_mo)
        vs_rest = pay - NET_GAP_VS_REST_SUB
        vs_core = pay - NET_GAP_VS_WORST_CORE
        print(
            f"  {100 * pct:7.0f}%  {pay:10.1f}  {cost_mo:14,.0f}  "
            f"{vs_rest:+16.1f}  {vs_core:+18.1f}"
        )
    print("  'vs gap' = payout per eligible leg minus the net-cycle gap (₹).")
    print("  Positive ⇒ payout more than fills that comparison gap on a per-trip")
    print("  basis (overpay relative to that benchmark); negative ⇒ underfills.")
    gap_pct_rest = 100 * NET_GAP_VS_REST_SUB / local_avg
    gap_pct_core = 100 * NET_GAP_VS_WORST_CORE / local_avg
    print(
        f"  Gap-equivalent share of local fare: "
        f"₹{NET_GAP_VS_REST_SUB:.1f} = {gap_pct_rest:.1f}% of fare "
        f"(restore rest-suburban net); "
        f"₹{NET_GAP_VS_WORST_CORE:.1f} = {gap_pct_core:.1f}% of fare "
        f"(match worst×city_core — geography, not ARA's job)."
    )
    print("  All three requested cells (30/50/70%) overshoot BOTH gaps:")
    print(f"    30% of fare = ₹{0.30 * local_avg:.1f} vs ₹{NET_GAP_VS_REST_SUB:.1f} rest-sub")
    print(f"    and vs ₹{NET_GAP_VS_WORST_CORE:.1f} worst-core. ARA at 30%+ of fare")
    print("    overpays relative to closing the overnight-suburban penalty.")
    print("    The evidence-grounded payout to close rest-suburban net is ~9% of")
    print("    fare, not 30–70%. Report 30/50/70 as requested; do not bank them")
    print("    as the efficient price.")

    sub("Naive new-headcount alternative")
    print("  A 'hire more captains to sit the airport overnight' plan faces the")
    print("  same two independent penalties Step 7 documented for incumbents:")
    print("    (1) suburban backhaul (distance ~23 km vs ~13 km city_core, all hours)")
    print("    (2) overnight return-fare collapse (−8 to −9pp in every drop type)")
    print("  Mix does not shift overnight, so new captains are not a mix-shift")
    print("  lever. They inherit worst×suburban net ₹24.9. Staffing the mean")
    print(f"  deficit of ~{cap_rest - cap_worst:.0f} online captains vs daytime does not")
    print("  change trip geography or return probability. ARA prices the deadhead;")
    print("  hiring does not. No CAC field exists — cannot convert headcount to ₹.")
    print("  Qualitative: do not substitute 'recruit N airport captains' for ARA")
    print("  without a product that changes overnight-suburban expected net.")
    print("\n  ARA rollup number (sample-implied monthly cost, not market):")
    print(f"    30% fare: ₹{ara_costs[0.30][1]:,.0f}/month  (₹{ara_costs[0.30][0]:.1f}/elig. leg)")
    print(f"    50% fare: ₹{ara_costs[0.50][1]:,.0f}/month  (₹{ara_costs[0.50][0]:.1f}/elig. leg)")
    print(f"    70% fare: ₹{ara_costs[0.70][1]:,.0f}/month  (₹{ara_costs[0.70][0]:.1f}/elig. leg)")
    print(f"    eligible volume: {elig_mo:,.1f} sample legs/month")
    print("  Confidence: HIGH on the eligibility definition and the Step 7 gap")
    print("  comparison; LOW on rupee totals as a budget (sampled trips, unknown")
    print("  sampling fraction). Take the per-leg payout-vs-gap comparison to the")
    print("  memo; do not take sample ₹/month as a city P&L line.")

    # ------------------------------------------------------------------
    # Rollup
    # ------------------------------------------------------------------
    hr("7. FINAL ROLLUP — sized interventions only")
    print("  Units differ: C1a/C1b are additional approved captains/month;")
    print("  ARA is ₹/month (sample) and ₹/eligible leg. They are not added")
    print("  to one number. Channel-replication and CAMP_WA_002 are tests,")
    print("  excluded from any summed total.")
    print()
    print(f"  {'item':<44} {'number':<42} {'confidence':<14} mechanism")
    print("  " + "-" * 140)
    print(
        f"  {'C1a RC provisional (central 60%×att-3)':<44} "
        f"{c1a_mid:>6.1f} appr/mo  (range {c1a_lo:.1f}–{c1a_hi:.1f}; cap {c1a_cap:.1f})"
        f"{'':>1} {'MED (cohort) / LOW-MED (show-up)':<14} "
        "10-day grace in-person RC; Insurance excluded"
    )
    print(
        f"  {'C1b Insurance capture UX (att-1→3)':<44} "
        f"{c1b_appr[1]:.1f}–{c1b_appr[3]:.1f} appr/mo  (mid att-2 {c1b_appr[2]:.1f})"
        f"{'':>4} {'MED / LOW-MED':<14} "
        "upload-time blur/OCR; still must clear before ride"
    )
    print(
        f"  {'ARA 30/50/70% of local fare':<44} "
        f"₹{ara_costs[0.30][0]:.0f}/₹{ara_costs[0.50][0]:.0f}/₹{ara_costs[0.70][0]:.0f}/leg  "
        f"sample ₹{ara_costs[0.30][1]/1000:.0f}k/"
        f"{ara_costs[0.50][1]/1000:.0f}k/"
        f"{ara_costs[0.70][1]/1000:.0f}k/mo"
        f"{'':>2} {'HIGH def / LOW ₹':<14} "
        "all three overshoot ₹31.6 rest-sub gap; efficient fill ≈9% of fare"
    )
    print(
        f"  {'Overlap-adjusted C1a+(a) ceiling (NOT banked)':<44} "
        f"{combined_ceiling_central:.1f}/mo at 60%×att-3 on 911 + (a) 216.5"
        f"{'':>2} {'LOW':<14} "
        "arithmetic union; (a) selection-biased; do not sum into total"
    )
    print(
        f"  {'C1a ∩ Step 4(a) RC-gap captains':<44} "
        f"{len(ov_rc_gap):,} captains (not additive with channel 128–256/mo)"
        f"{'':>2} {'HIGH':<14} "
        "same people; C1a vs channel-replication are alternatives"
    )
    print()
    print("  SUMMED TOTAL (sized, disjoint onboarding only):")
    print(f"    C1a central + C1b att-1 floor: {c1a_mid + c1b_appr[1]:.1f} additional approved/month")
    print(f"    C1a central + C1b att-3:       {c1a_mid + c1b_appr[3]:.1f} additional approved/month")
    print("    C1a ∩ C1b = 0 captains, so adding C1a+C1b does not double-count")
    print("    people. It still adds two different product bets.")
    print("    EXCLUDED from this sum: channel-replication 128–256/mo, CAMP_WA_002,")
    print("    the overlap-adjusted C1a+(a) ceiling, ARA ₹ (different unit).")
    print()
    print("  Not sized as bankable:")
    print("    Channel-replication: 128–256/mo unproven ceiling → §4 pilot")
    print("      (~900/arm for 5pp approved MDE at 80% power).")
    print("    CAMP_WA_002: 0 pp observational lift → §5 send/no-send RCT.")
    print()
    print("Step 8 complete. No memo. No deck.")


if __name__ == "__main__":
    main()
