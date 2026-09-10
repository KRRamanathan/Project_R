#!/usr/bin/env python3
"""
STEP 2 — Signup → approved funnel only.

Resolved rules (also restated next to the numbers they affect):
  1. Cohorting uses signup-age vs extract, not decision_ts.
  2. Stage progress comes from doc_events verification_pass; approvals
     fields are a fallback only when a captain has zero doc_events.
  3. approved / rejected / dropped_in_docs stay distinct terminal states.
  4. PERMIT is required for Auto and Cab only; ERickshaw has a 5-doc path.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent
EXTRACTION_TS = pd.Timestamp("2026-06-30 23:59:00")  # labelled IST in the brief
EXTRACTION_LABEL = "2026-06-30 23:59 IST"

# Vehicle-specific required sequence. PERMIT is Auto/Cab only (brief + audit).
SEQ = {
    "Auto": ["DL", "RC", "AADHAAR", "PERMIT", "FITNESS", "INSURANCE"],
    "Cab": ["DL", "RC", "AADHAAR", "PERMIT", "FITNESS", "INSURANCE"],
    "ERickshaw": ["DL", "RC", "AADHAAR", "FITNESS", "INSURANCE"],
}


def wilson_interval(k: int, n: int, z: float = 1.96) -> tuple[float, float, float]:
    """Wilson score 95% CI for a binomial proportion. Returns (p, lo, hi)."""
    if n <= 0:
        return (np.nan, np.nan, np.nan)
    k = int(k)
    n = int(n)
    p = k / n
    z2 = z * z
    denom = 1.0 + z2 / n
    centre = (p + z2 / (2.0 * n)) / denom
    half = z * np.sqrt((p * (1.0 - p) + z2 / (4.0 * n)) / n) / denom
    return (p, centre - half, centre + half)


def fmt_rate(k: int, n: int) -> str:
    p, lo, hi = wilson_interval(k, n)
    if n <= 0 or np.isnan(p):
        return "n/a"
    flag = "  [n<100, directional only]" if n < 100 else ""
    return f"{100 * p:6.2f}%  ({k:,}/{n:,})  Wilson95% [{100 * lo:5.2f}%, {100 * hi:5.2f}%]{flag}"


def hr(title: str) -> None:
    print("\n" + "=" * 96)
    print(title)
    print("=" * 96)


def sub(title: str) -> None:
    print("\n" + "-" * 96)
    print(title)
    print("-" * 96)


def load() -> pd.DataFrame:
    captains = pd.read_csv(DATA_DIR / "captains.csv")
    approvals = pd.read_csv(DATA_DIR / "approvals.csv")
    docs = pd.read_csv(DATA_DIR / "doc_events.csv")

    captains["signup_ts"] = pd.to_datetime(captains["signup_ts"], errors="coerce")
    # Signup-age = time from signup to extract. Used for the mature-cohort cut.
    captains["signup_age_days"] = (
        EXTRACTION_TS - captains["signup_ts"]
    ).dt.total_seconds() / 86400.0

    passed = (
        docs.loc[docs["event_type"] == "verification_pass", ["captain_id", "doc_type"]]
        .drop_duplicates()
        .assign(passed=1)
        .pivot_table(index="captain_id", columns="doc_type", values="passed", aggfunc="max")
        .fillna(0)
        .astype(int)
    )
    for col in ["DL", "RC", "AADHAAR", "PERMIT", "FITNESS", "INSURANCE"]:
        if col not in passed.columns:
            passed[col] = 0

    n_pass = (
        docs.loc[docs["event_type"] == "verification_pass"]
        .groupby("captain_id")["doc_type"]
        .nunique()
        .rename("n_unique_docs_passed_events")
    )
    n_events = docs.groupby("captain_id").size().rename("n_doc_events")

    df = captains.merge(approvals, on="captain_id", how="left")
    df = df.merge(passed, on="captain_id", how="left")
    df = df.merge(n_pass, on="captain_id", how="left")
    df = df.merge(n_events, on="captain_id", how="left")
    for col in ["DL", "RC", "AADHAAR", "PERMIT", "FITNESS", "INSURANCE"]:
        df[col] = df[col].fillna(0).astype(int)
    df["n_unique_docs_passed_events"] = df["n_unique_docs_passed_events"].fillna(0).astype(int)
    df["n_doc_events"] = df["n_doc_events"].fillna(0).astype(int)
    df["has_doc_events"] = df["n_doc_events"] > 0
    df["docs_cleared_mismatch"] = df["docs_cleared"].fillna(-1) != df["n_unique_docs_passed_events"]
    return df


def empirical_cutoff(df: pd.DataFrame) -> float:
    """
    Censoring cutoff — derived from signup-age of in_progress, NOT decision_ts.

    Why not decision_ts
        dropped_in_docs (19,062) and in_progress (1,297) have null decision_ts.
        A follow-up window keyed on decision_ts would silently drop the largest
        terminal state. Signup-age vs the known extract clock is observable for
        every captain.

    Why this cutoff
        in_progress is right-censored at extract: those captains have not yet
        reached a terminal status. Their signup-age distribution is the empirical
        observation window of unresolved onboarding:
            n=1,297; mean≈5.13 days; p99≈12.22 days; max≈15.60 days.
        No captain older than that max is still in_progress in this extract.
        So any captain with signup_age > max(in_progress signup_age) has had
        enough calendar time that the extract always records a terminal status
        (approved / rejected / dropped_in_docs). That is the mature cohort.

    in_progress is excluded as censored, not coded as failed.
    Captains younger than the cutoff who already terminated are also excluded
    so the denominator is one mature window, not a mix of 'had time' and
    'finished early'.
    """
    ip = df.loc[df["final_status"] == "in_progress", "signup_age_days"]
    print("in_progress signup-age (days before extract):")
    print(ip.describe(percentiles=[0.5, 0.9, 0.95, 0.99]).to_string())
    cutoff = float(ip.max())
    print(f"\nempirical cutoff = max(in_progress signup_age) = {cutoff:.6f} days")
    print("mature cohort definition: signup_age_days > cutoff")
    print("in_progress treatment: censored (excluded from funnel rates), not failed")
    return cutoff


def event_cleared(row: pd.Series) -> dict[str, int]:
    """Prefix of vehicle-required docs with verification_pass (no skips in this extract)."""
    seq = SEQ[row["vehicle_type"]]
    flags = {d: 0 for d in ["DL", "RC", "AADHAAR", "PERMIT", "FITNESS", "INSURANCE"]}
    still = True
    for doc in seq:
        ok = still and int(row[doc]) == 1
        flags[doc] = int(ok)
        if not ok:
            still = False
    flags["all_required"] = int(all(flags[d] == 1 for d in seq))
    return flags


def fallback_cleared(row: pd.Series) -> dict[str, int]:
    """
    Used ONLY when n_doc_events == 0.
    docs_cleared is the count of vehicle-required docs passed
    (approved ERickshaw = 5, Auto/Cab = 6 in the audit). last_stage_reached
    is not used to invent passes: for ERickshaw it still contains the label
    PERMIT even though PERMIT is not required.
    """
    seq = SEQ[row["vehicle_type"]]
    flags = {d: 0 for d in ["DL", "RC", "AADHAAR", "PERMIT", "FITNESS", "INSURANCE"]}
    k = int(row["docs_cleared"]) if pd.notna(row["docs_cleared"]) else 0
    k = max(0, min(k, len(seq)))
    for i, doc in enumerate(seq):
        flags[doc] = int(i < k)
    flags["all_required"] = int(k >= len(seq))
    return flags


def apply_stage_flags(df: pd.DataFrame) -> pd.DataFrame:
    flags_event = []
    flags_fallback = []
    for _, row in df.iterrows():
        flags_event.append(event_cleared(row))
        flags_fallback.append(fallback_cleared(row))
    ev = pd.DataFrame(flags_event, index=df.index).add_prefix("ev_")
    fb = pd.DataFrame(flags_fallback, index=df.index).add_prefix("fb_")
    out = pd.concat([df, ev, fb], axis=1)
    docs = ["DL", "RC", "AADHAAR", "PERMIT", "FITNESS", "INSURANCE", "all_required"]
    for doc in docs:
        ev_col, fb_col = f"ev_{doc}", f"fb_{doc}"
        if ev_col not in out.columns:
            out[ev_col] = 0
        if fb_col not in out.columns:
            out[fb_col] = 0
        # events win when present; approvals.docs_cleared only if zero events
        out[f"use_{doc}"] = np.where(out["has_doc_events"], out[ev_col], out[fb_col])
    return out


def print_funnel_block(label: str, d: pd.DataFrame, source: str) -> None:
    """
    Vehicle-aware stage table.
    Permit denominator is Auto/Cab who cleared Aadhaar (ERickshaw skipped).
    Fitness previous-stage denom is Permit (Auto/Cab) or Aadhaar (ERickshaw).
    """
    n_signups = len(d)
    print(f"\n[{label}] source={source}  n_signups={n_signups:,}")
    if n_signups == 0:
        print("  empty group")
        return

    vt = d["vehicle_type"]
    auto_cab = vt.isin(["Auto", "Cab"])
    erick = vt.eq("ERickshaw")

    passed_dl = d["use_DL"] == 1
    passed_rc = d["use_RC"] == 1
    passed_aa = d["use_AADHAAR"] == 1
    passed_pe = d["use_PERMIT"] == 1
    passed_fi = d["use_FITNESS"] == 1
    passed_in = d["use_INSURANCE"] == 1
    passed_all = d["use_all_required"] == 1

    n_dl = int(passed_dl.sum())
    n_rc = int(passed_rc.sum())
    n_aa = int(passed_aa.sum())
    n_pe = int((passed_pe & auto_cab).sum())
    n_fi = int(passed_fi.sum())
    n_in = int(passed_in.sum())
    n_all = int(passed_all.sum())

    n_ac = int(auto_cab.sum())
    n_er = int(erick.sum())
    n_aa_ac = int((passed_aa & auto_cab).sum())
    n_aa_er = int((passed_aa & erick).sum())
    n_pe_ac = int((passed_pe & auto_cab).sum())
    n_fi_ac = int((passed_fi & auto_cab).sum())
    n_fi_er = int((passed_fi & erick).sum())

    n_approved = int((d["final_status"] == "approved").sum())
    n_rejected = int((d["final_status"] == "rejected").sum())
    n_dropped = int((d["final_status"] == "dropped_in_docs").sum())
    n_inprog = int((d["final_status"] == "in_progress").sum())

    n_approved_all = int(((d["final_status"] == "approved") & passed_all).sum())
    n_rejected_all = int(((d["final_status"] == "rejected") & passed_all).sum())

    print(f"  vehicle mix: Auto/Cab={n_ac:,}  ERickshaw={n_er:,}  in_progress_remaining={n_inprog:,}")
    print()
    print(f"  {'stage':<76} {'n':>8}  rate")
    print("  " + "-" * 92)

    def line(stage: str, k: int, denom: int | None, note: str) -> None:
        if denom is None:
            print(f"  {stage:<76} {k:8,}  —  {note}")
        else:
            print(f"  {stage:<76} {k:8,}  {fmt_rate(k, denom)}")
            print(f"  {'':76} {'':8}  {note}")

    line("signup (mature, this block)", n_signups, None, "denominator for vs-signup rates")
    if source == "doc_events":
        n_started = int(d["has_doc_events"].sum())
        line("any doc_event (started verification trail)", n_started, n_signups, "vs signup")
    else:
        line("zero doc_events (fallback block — not merged into event funnel)", n_signups, None, "separate line, as specified")

    line("passed DL", n_dl, n_signups, "vs signup")
    if n_signups:
        # also vs previous when previous ≠ signup
        pass
    line("passed RC | passed DL", n_rc, n_dl, "step conversion")
    line("passed AADHAAR | passed RC", n_aa, n_rc, "step conversion")
    line("passed PERMIT | Auto/Cab passed AADHAAR", n_pe, n_aa_ac, "ERickshaw excluded from this denom (PERMIT not required)")
    print(
        f"  {'  ERickshaw at AADHAAR (skip PERMIT, enter FITNESS denom)':<76} {n_aa_er:8,}  "
        f"{fmt_rate(n_aa_er, n_er) if n_er else 'n/a'}"
    )
    fitness_denom = n_pe_ac + n_aa_er
    line(
        "passed FITNESS | (Auto/Cab passed PERMIT + ERickshaw passed AADHAAR)",
        n_fi,
        fitness_denom,
        f"split: Auto/Cab FITNESS {n_fi_ac:,}/{n_pe_ac:,}; ERickshaw FITNESS {n_fi_er:,}/{n_aa_er:,}",
    )
    line("passed INSURANCE | passed FITNESS  (= all required docs cleared)", n_in, n_fi, "step conversion")
    line("cleared all required docs | signup", n_all, n_signups, "vs signup")
    line("approved | signup", n_approved, n_signups, "A2O-style conversion in this block")
    line("approved | cleared all required docs", n_approved_all, n_all, "post-clearance eligibility pass")
    line("rejected | signup", n_rejected, n_signups, "do not treat as a document-stage leak")
    line("rejected | cleared all required docs", n_rejected_all, n_all, "post-clearance eligibility fail")
    line("dropped_in_docs | signup", n_dropped, n_signups, "document-path non-completion")

    # Volume lost between sequential stages (absolute captains)
    print("\n  absolute volume between sequential doc stages (this block):")
    print(f"    signup → passed DL:                 lost {n_signups - n_dl:,}")
    print(f"    DL → RC:                            lost {n_dl - n_rc:,}")
    print(f"    RC → AADHAAR:                       lost {n_rc - n_aa:,}")
    print(f"    AADHAAR → PERMIT (Auto/Cab only):   lost {n_aa_ac - n_pe:,}  (denom Auto/Cab at AADHAAR={n_aa_ac:,})")
    print(f"    previous → FITNESS:                 lost {fitness_denom - n_fi:,}")
    print(f"    FITNESS → INSURANCE:                lost {n_fi - n_in:,}")
    print(f"    all-required-cleared → approved:    {n_all:,} cleared → {n_approved_all:,} approved, {n_rejected_all:,} rejected")
    if n_inprog:
        print(f"    WARNING: {n_inprog:,} in_progress remain in this block (should be 0 in mature cohort)")


def main() -> None:
    hr("STEP 2 — SIGNUP → APPROVED FUNNEL")
    print(f"extract clock: {EXTRACTION_LABEL} (timestamps in files are timezone-naive)")
    print("in_progress is censored, not failed. rejected is an eligibility gate, not a doc fail.")
    df = load()

    sub("A. Empirical mature-cohort cutoff (signup-age)")
    cutoff = empirical_cutoff(df)
    df["mature"] = df["signup_age_days"] > cutoff

    print("\nfull extract by final_status:")
    print(df["final_status"].value_counts().to_string())
    print("\nmature (signup_age > cutoff) by final_status:")
    print(df.loc[df["mature"], "final_status"].value_counts().to_string())
    print("\nexcluded as immature (signup_age ≤ cutoff) by final_status:")
    print(df.loc[~df["mature"], "final_status"].value_counts().to_string())
    print(
        f"\ncohort sizes: all={len(df):,}  mature={int(df['mature'].sum()):,}  "
        f"immature={int((~df['mature']).sum()):,}"
    )
    print(
        "immature includes ALL in_progress (censored) plus already-terminal captains "
        "who signed up inside the unresolved window."
    )

    sub("B. Fallback / exclusion rule counts (print, do not silently merge)")
    n_zero = int((~df["has_doc_events"]).sum())
    n_zero_m = int((~df["has_doc_events"] & df["mature"]).sum())
    n_mis = int(df["docs_cleared_mismatch"].sum())
    n_mis_m = int((df["docs_cleared_mismatch"] & df["mature"]).sum())
    n_mis_ev = int((df["docs_cleared_mismatch"] & df["has_doc_events"]).sum())
    n_mis_ev_m = int((df["docs_cleared_mismatch"] & df["has_doc_events"] & df["mature"]).sum())
    n_mis_z = int((df["docs_cleared_mismatch"] & ~df["has_doc_events"]).sum())
    n_mis_z_m = int((df["docs_cleared_mismatch"] & ~df["has_doc_events"] & df["mature"]).sum())

    print("Rule 1 — zero doc_events (FALLBACK to approvals.docs_cleared; separate line):")
    print(f"  full extract: {n_zero:,}")
    print(f"  mature cohort: {n_zero_m:,}")
    print("  these captains are NOT folded into the event-derived stage counts.")
    print("\nRule 2 — approvals.docs_cleared != nunique(verification_pass doc_types)")
    print("  (EXCLUSION of approvals fields as a stage source; captains with events STAY")
    print("   in the event-derived funnel. Stage = doc_events, not docs_cleared.)")
    print(f"  full extract: {n_mis:,}  (with events {n_mis_ev:,}; zero-events {n_mis_z:,})")
    print(f"  mature cohort: {n_mis_m:,}  (with events {n_mis_ev_m:,}; zero-events {n_mis_z_m:,})")

    print("\nzero-doc-event mature, by final_status:")
    print(df.loc[~df["has_doc_events"] & df["mature"], "final_status"].value_counts().to_string())
    print("\nmismatch ∩ has events, mature, by final_status:")
    print(
        df.loc[df["docs_cleared_mismatch"] & df["has_doc_events"] & df["mature"], "final_status"]
        .value_counts()
        .to_string()
    )

    df = apply_stage_flags(df)
    mature = df[df["mature"]].copy()
    event_m = mature[mature["has_doc_events"]].copy()
    zero_m = mature[~mature["has_doc_events"]].copy()

    # For the event-derived block, "use_*" is already ev_* because has_doc_events is True.
    sub("C. Event-derived funnel — mature captains WITH doc_events (primary)")
    print("furthest cleared stage = prefix of vehicle-required docs with verification_pass.")
    print("audit check: this extract has 0 later-doc passes without earlier required passes.")
    print_funnel_block("MATURE + HAS doc_events", event_m, source="doc_events")

    sub("D. Fallback funnel — mature captains with ZERO doc_events (separate line)")
    print("stages from approvals.docs_cleared mapped onto the vehicle-required sequence.")
    print("not merged into section C.")
    print_funnel_block("MATURE + ZERO doc_events (fallback)", zero_m, source="approvals_fallback")

    sub("E. Same event-derived funnel, split by vehicle_type (vehicle-aware denoms)")
    for vt in ["Auto", "Cab", "ERickshaw"]:
        print_funnel_block(
            f"MATURE + HAS doc_events + vehicle_type={vt}",
            event_m[event_m["vehicle_type"] == vt],
            source="doc_events",
        )

    sub("F. Terminal-state mix among mature event-derived captains who cleared all required docs")
    cleared = event_m[event_m["use_all_required"] == 1]
    print(f"n cleared all required (event-derived, mature) = {len(cleared):,}")
    print(cleared["final_status"].value_counts().to_string())
    print("\nrejected last_stage_reached among event-derived mature rejected:")
    rej = event_m[event_m["final_status"] == "rejected"]
    print(f"n rejected in this block = {len(rej):,}")
    print(rej["last_stage_reached"].value_counts(dropna=False).to_string())
    print("\nrejected × vehicle_type:")
    print(pd.crosstab(rej["vehicle_type"], rej["last_stage_reached"]).to_string())
    n_rej_all = int((rej["use_all_required"] == 1).sum())
    print(
        f"\nrejected with all required docs passed in events: {n_rej_all:,} / {len(rej):,}  "
        f"{fmt_rate(n_rej_all, len(rej)) if len(rej) else ''}"
    )

    sub("G. Headline mature rates (event-derived block only — fallback not merged)")
    n = len(event_m)
    n_appr = int((event_m["final_status"] == "approved").sum())
    n_rej = int((event_m["final_status"] == "rejected").sum())
    n_drop = int((event_m["final_status"] == "dropped_in_docs").sum())
    n_all = int((event_m["use_all_required"] == 1).sum())
    print(f"mature ∩ has doc_events n={n:,}")
    print(f"  approved            {fmt_rate(n_appr, n)}")
    print(f"  rejected            {fmt_rate(n_rej, n)}")
    print(f"  dropped_in_docs     {fmt_rate(n_drop, n)}")
    print(f"  cleared all req docs {fmt_rate(n_all, n)}")
    print(f"  approved | cleared  {fmt_rate(n_appr, n_all)}")
    print(
        f"\nfallback mature n={len(zero_m):,} is reported in section D and is NOT in the rates above."
    )

    print("\nFunnel construction complete. No leak segmentation, no campaign eval.")


if __name__ == "__main__":
    main()
