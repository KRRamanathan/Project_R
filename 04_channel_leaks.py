#!/usr/bin/env python3
"""
STEP 4 — Characterize the leading leaks through the channel lens.

fos_field vs self-serve (organic_app, paid_digital) is the headline.
RC/Insurance failure-mode detail is supporting depth.
vehicle_type / ERickshaw is not reported (Step 3: structural, pseudo-R² 0.0065).
No campaign eval. No CAC estimate.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency, norm

DATA_DIR = Path(__file__).resolve().parent
EXTRACTION_TS = pd.Timestamp("2026-06-30 23:59:00")
EXTRACTION_LABEL = "2026-06-30 23:59 IST"

SELF_SERVE = ["organic_app", "paid_digital"]
FOS = "fos_field"
FOCUS = [FOS, "organic_app", "paid_digital"]
DEVICES = ["low", "mid", "high"]
STAGE_DOCS = ["DL", "RC", "AADHAAR", "PERMIT", "FITNESS", "INSURANCE"]

CAPTURE_REASONS = {"image_blurred", "ocr_low_confidence", "details_not_legible"}
ELIGIBILITY_REASONS = {
    "document_expired",
    "duplicate_document",
    "name_mismatch",
    "wrong_document_type",
}

# C1 (not previously checked in as a named object; definition used here):
# "pure capture-only failure" = mature ∩ has-doc_events captains who uploaded
# the stage, never passed it, and whose verification_fail reasons on that stage
# are exclusively capture-class (blur / OCR / not-legible) — no eligibility
# codes on that stage. Provisional-activation / guided-capture targeting is
# this set, not a device-tier slice.


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
    if min(n1, n2) <= 0:
        return (np.nan, np.nan)
    p = (k1 + k2) / (n1 + n2)
    se = np.sqrt(p * (1 - p) * (1 / n1 + 1 / n2))
    if se == 0:
        return (0.0, 1.0)
    z = (k1 / n1 - k2 / n2) / se
    return float(z), float(2 * norm.sf(abs(z)))


def hr(title: str) -> None:
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)


def sub(title: str) -> None:
    print("\n" + "-" * 100)
    print(title)
    print("-" * 100)


def load() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
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
    df["atrisk_DL"] = True
    df["atrisk_RC"] = df["cleared_DL"]
    df["atrisk_AADHAAR"] = df["cleared_RC"]
    df["atrisk_PERMIT"] = ac & df["cleared_AADHAAR"]
    df["atrisk_FITNESS"] = (ac & df["cleared_PERMIT"]) | (er & df["cleared_AADHAAR"])
    df["atrisk_INSURANCE"] = df["cleared_FITNESS"]
    df["needs_permit"] = ac
    return df, docs, nudges


def fos_rate_by_device(at: pd.DataFrame, doc: str) -> dict[str, tuple[int, int, float]]:
    """Return device -> (k, n, p) for fos_field at this stage."""
    fos = at[at["acquisition_channel"] == FOS]
    out = {}
    for d in DEVICES:
        sl = fos[fos["device_tier"] == d]
        n = len(sl)
        k = int(sl[f"cleared_{doc}"].sum())
        out[d] = (k, n, (k / n) if n else np.nan)
    return out


def print_stage_channel_rates(funnel: pd.DataFrame, doc: str) -> None:
    at = funnel[funnel[f"atrisk_{doc}"]].copy()
    sub(f"Observed step conversion at {doc} (event-funnel at-risk), by channel")
    print(f"  at-risk n={len(at):,}")
    for ch in FOCUS + ["referral", "gc_telecalling"]:
        sl = at[at["acquisition_channel"] == ch]
        k = int(sl[f"cleared_{doc}"].sum())
        n = len(sl)
        print(f"    {ch:<16} {fmt_rate(k, n)}")
    print("  fos_field rate by device_tier (the rates applied in the counterfactual):")
    rates = fos_rate_by_device(at, doc)
    for d, (k, n, p) in rates.items():
        flag = "  [n<100, directional only]" if n < 100 else ""
        print(f"    fos × {d:<4} {fmt_rate(k, n)}{flag}")
    # never-uploaded vs fail among lost, by focus channel
    print("  among at-risk who did NOT pass, never-uploaded vs uploaded-fail (focus channels):")
    for ch in FOCUS:
        sl = at[at["acquisition_channel"] == ch]
        lost = sl[~sl[f"cleared_{doc}"]]
        never = lost[lost[f"upl_{doc}"] == 0]
        failu = lost[lost[f"upl_{doc}"] == 1]
        n_lost = len(lost)
        print(
            f"    {ch:<16} lost={n_lost:,}  never-uploaded {fmt_rate(len(never), n_lost) if n_lost else 'n/a'}  "
            f"uploaded-fail {fmt_rate(len(failu), n_lost) if n_lost else 'n/a'}"
        )


def sequential_expected(
    funnel: pd.DataFrame,
    starters: pd.DataFrame,
    fos_rates: dict[str, dict[str, float]],
    fos_permit_rates: dict[str, float],
    fos_fit_ac: dict[str, float],
    fos_fit_er: dict[str, float],
    fos_approve_given_clear: float,
) -> dict[str, float]:
    """
    Expected cleared-all and approved if each starter faces fos device-specific
    stage rates along their own required path (Permit skipped when not required).
    Device mix is the starters' mix, not fos's mix.
    """
    exp_clear = 0.0
    for _, row in starters.iterrows():
        d = row["device_tier"]
        p = 1.0
        p *= fos_rates["DL"].get(d, np.nan)
        p *= fos_rates["RC"].get(d, np.nan)
        p *= fos_rates["AADHAAR"].get(d, np.nan)
        if row["needs_permit"]:
            p *= fos_permit_rates.get(d, np.nan)
            p *= fos_fit_ac.get(d, np.nan)
        else:
            p *= fos_fit_er.get(d, np.nan)
        p *= fos_rates["INSURANCE"].get(d, np.nan)
        if np.isnan(p):
            continue
        exp_clear += p
    return {
        "n_starters": float(len(starters)),
        "exp_cleared": float(exp_clear),
        "exp_approved": float(exp_clear * fos_approve_given_clear),
        "obs_cleared": float(starters["cleared_INSURANCE"].sum()),
        "obs_approved": float((starters["final_status"] == "approved").sum()),
    }


def collect_fos_stage_rates(funnel: pd.DataFrame) -> tuple[dict, dict, dict, dict, float, dict]:
    fos_rates = {}
    cell_ns = {}
    for doc in ["DL", "RC", "AADHAAR", "INSURANCE"]:
        at = funnel[funnel[f"atrisk_{doc}"] & funnel["acquisition_channel"].eq(FOS)]
        fos_rates[doc] = {}
        cell_ns[doc] = {}
        for d in DEVICES:
            sl = at[at["device_tier"] == d]
            n, k = len(sl), int(sl[f"cleared_{doc}"].sum())
            fos_rates[doc][d] = (k / n) if n else np.nan
            cell_ns[doc][d] = (k, n)

    at_p = funnel[funnel["atrisk_PERMIT"] & funnel["acquisition_channel"].eq(FOS)]
    fos_permit = {}
    cell_ns["PERMIT"] = {}
    for d in DEVICES:
        sl = at_p[at_p["device_tier"] == d]
        n, k = len(sl), int(sl["cleared_PERMIT"].sum())
        fos_permit[d] = (k / n) if n else np.nan
        cell_ns["PERMIT"][d] = (k, n)

    at_f = funnel[funnel["atrisk_FITNESS"] & funnel["acquisition_channel"].eq(FOS)]
    fos_fit_ac, fos_fit_er = {}, {}
    cell_ns["FITNESS_ac"] = {}
    cell_ns["FITNESS_er"] = {}
    ac = at_f["needs_permit"]
    for d in DEVICES:
        sl = at_f[ac & at_f["device_tier"].eq(d)]
        n, k = len(sl), int(sl["cleared_FITNESS"].sum())
        fos_fit_ac[d] = (k / n) if n else np.nan
        cell_ns["FITNESS_ac"][d] = (k, n)
        sl2 = at_f[~ac & at_f["device_tier"].eq(d)]
        n2, k2 = len(sl2), int(sl2["cleared_FITNESS"].sum())
        fos_fit_er[d] = (k2 / n2) if n2 else np.nan
        cell_ns["FITNESS_er"][d] = (k2, n2)

    fos_clear = funnel[
        funnel["acquisition_channel"].eq(FOS) & funnel["cleared_INSURANCE"]
    ]
    n_clear = len(fos_clear)
    n_appr = int((fos_clear["final_status"] == "approved").sum())
    p_appr = n_appr / n_clear if n_clear else np.nan
    return fos_rates, fos_permit, fos_fit_ac, fos_fit_er, p_appr, cell_ns


def never_attempt_device_std(mature: pd.DataFrame) -> None:
    sub("Never-attempted (zero doc_events) among ALL mature signups — channel, device-stratified")
    print("  This is component (b)'s raw material. Not mixed into RC/Insurance verify fails.")
    for ch in FOCUS:
        sl = mature[mature["acquisition_channel"] == ch]
        k = int((~sl["has_doc_events"]).sum())
        print(f"    {ch:<16} {fmt_rate(k, len(sl))}")
    print("  fos_field never-attempt by device (applied to self-serve device mix):")
    fos = mature[mature["acquisition_channel"] == FOS]
    p_fos_d = {}
    for d in DEVICES:
        sl = fos[fos["device_tier"] == d]
        k = int((~sl["has_doc_events"]).sum())
        p_fos_d[d] = k / len(sl) if len(sl) else np.nan
        print(f"    fos × {d:<4} {fmt_rate(k, len(sl))}")
    print("  device-standardized never-attempt: sum_d w_channel,d * p_never_fos,d")
    for ch in SELF_SERVE:
        sl = mature[mature["acquisition_channel"] == ch]
        w = sl["device_tier"].value_counts(normalize=True)
        p_std = sum(float(w.get(d, 0.0)) * p_fos_d[d] for d in DEVICES)
        p_obs = (~sl["has_doc_events"]).mean()
        print(
            f"    {ch:<16} observed never-attempt {100 * p_obs:.2f}%  "
            f"fos-rate at this channel's device mix {100 * p_std:.2f}%  "
            f"gap {100 * (p_obs - p_std):+.2f}pp  n={len(sl):,}"
        )


def failure_reason_block(funnel: pd.DataFrame, docs: pd.DataFrame, doc: str) -> None:
    at = funnel[funnel[f"atrisk_{doc}"]].copy()
    lost_upl = at[(~at[f"cleared_{doc}"]) & (at[f"upl_{doc}"] == 1)]
    sub(f"Failure-reason mix — {doc} uploaded-but-never-passed captains n={len(lost_upl):,}")
    print("  unit below: verification_fail EVENTS (a captain may have more than one).")
    fails = docs[
        docs["captain_id"].isin(set(lost_upl["captain_id"]))
        & docs["doc_type"].eq(doc)
        & docs["event_type"].eq("verification_fail")
    ]
    print(f"  verification_fail events: {len(fails):,}")
    vc = fails["failure_reason"].value_counts(dropna=False)
    n_ev = len(fails)
    for reason, c in vc.items():
        klass = "capture" if reason in CAPTURE_REASONS else (
            "eligibility" if reason in ELIGIBILITY_REASONS else "unclassified"
        )
        print(f"    {str(reason):<22} {fmt_rate(int(c), n_ev)}  [{klass}]")
    cap_n = int(fails["failure_reason"].isin(CAPTURE_REASONS).sum())
    elig_n = int(fails["failure_reason"].isin(ELIGIBILITY_REASONS).sum())
    print(f"  capture-class events (blur/OCR/illegible): {fmt_rate(cap_n, n_ev)}")
    print(f"  eligibility-class events:                  {fmt_rate(elig_n, n_ev)}")

    # captain-level exclusive classes
    per = (
        fails.groupby("captain_id")["failure_reason"]
        .agg(lambda s: set(s.dropna()))
        .reset_index()
    )
    per["only_capture"] = per["failure_reason"].apply(
        lambda s: len(s) > 0 and s <= CAPTURE_REASONS
    )
    per["any_elig"] = per["failure_reason"].apply(lambda s: len(s & ELIGIBILITY_REASONS) > 0)
    per["only_elig"] = per["failure_reason"].apply(
        lambda s: len(s) > 0 and s <= ELIGIBILITY_REASONS
    )
    n_capts = len(lost_upl)
    n_with_fail_ev = len(per)
    print(f"  captains uploaded-never-passed: {n_capts:,}; with ≥1 fail event: {n_with_fail_ev:,}")
    print(f"    only capture reasons:      {fmt_rate(int(per['only_capture'].sum()), n_with_fail_ev)}")
    print(f"    any eligibility reason:    {fmt_rate(int(per['any_elig'].sum()), n_with_fail_ev)}")
    print(f"    only eligibility reasons:  {fmt_rate(int(per['only_elig'].sum()), n_with_fail_ev)}")

    print("  event-level mix by focus channel:")
    meta = lost_upl[["captain_id", "acquisition_channel"]]
    f2 = fails.merge(meta, on="captain_id", how="left")
    for ch in FOCUS:
        sl = f2[f2["acquisition_channel"] == ch]
        if sl.empty:
            print(f"    {ch}: no fail events")
            continue
        print(f"    {ch} events n={len(sl):,}")
        for reason, c in sl["failure_reason"].value_counts().items():
            print(f"      {reason:<22} {fmt_rate(int(c), len(sl))}")
    return per.loc[per["only_capture"], "captain_id"]


def insurance_abandon(funnel: pd.DataFrame, docs: pd.DataFrame, nudges: pd.DataFrame) -> None:
    hr("3. INSURANCE ABANDONMENT — cleared Fitness, never uploaded Insurance")
    at = funnel[funnel["atrisk_INSURANCE"]].copy()
    abandon = at[at["upl_INSURANCE"] == 0]
    uploaded = at[at["upl_INSURANCE"] == 1]
    print(f"  at-risk (cleared Fitness) n={len(at):,}")
    print(f"  never uploaded Insurance n={len(abandon):,}  (Step 3 figure 2,530)")
    print(f"  uploaded Insurance n={len(uploaded):,}")
    print("  abandonment rate | cleared Fitness, by channel:")
    y = (at["upl_INSURANCE"] == 0).astype(int)
    ct = pd.crosstab(at["acquisition_channel"], y)
    chi2, p, dof, exp = chi2_contingency(ct)
    print(f"    χ² channel × never-upload Insurance: χ²={chi2:.2f} p={p:.4g} n={ct.values.sum():,}")
    print("    (Bonferroni for 5 channel levels vs fos: α=0.05/4=0.0125 for pairwise)")
    fos_sl = at[at["acquisition_channel"] == FOS]
    k_fos, n_fos = int((fos_sl["upl_INSURANCE"] == 0).sum()), len(fos_sl)
    for ch, n in at["acquisition_channel"].value_counts().items():
        sl = at[at["acquisition_channel"] == ch]
        k = int((sl["upl_INSURANCE"] == 0).sum())
        z, pz = two_prop_z(k, n, k_fos, n_fos)
        flag = "sig vs fos (Bonferroni 0.0125)" if (ch != FOS and pz < 0.0125) else (
            "raw p<0.05 only" if (ch != FOS and pz < 0.05) else ""
        )
        print(f"    {ch:<16} abandon {fmt_rate(k, n)}  vs fos z={z:.2f} p={pz:.4g}  {flag}")

    print("\n  same abandonment by device_tier (supporting; not the headline):")
    for d, n in at["device_tier"].value_counts().items():
        sl = at[at["device_tier"] == d]
        k = int((sl["upl_INSURANCE"] == 0).sum())
        print(f"    {d:<16} {fmt_rate(k, n)}")

    # Fitness pass timestamp
    fit_pass = (
        docs[
            (docs["event_type"] == "verification_pass") & (docs["doc_type"] == "FITNESS")
        ]
        .groupby("captain_id")["event_ts"]
        .min()
        .rename("fitness_pass_ts")
    )
    ins_first = (
        docs[docs["doc_type"] == "INSURANCE"]
        .groupby("captain_id")["event_ts"]
        .min()
        .rename("ins_first_ts")
    )
    at2 = at.merge(fit_pass, on="captain_id", how="left").merge(ins_first, on="captain_id", how="left")
    n_fit_ts = int(at2["fitness_pass_ts"].notna().sum())
    print(f"\n  captains at-risk with a FITNESS verification_pass timestamp: {n_fit_ts:,}/{len(at2):,}")

    ng = nudges.merge(at2[["captain_id", "fitness_pass_ts", "upl_INSURANCE", "acquisition_channel"]], on="captain_id", how="inner")
    ng["after_fitness"] = ng["sent_ts"] >= ng["fitness_pass_ts"]
    after = ng[ng["after_fitness"] & ng["fitness_pass_ts"].notna()]
    nudged_after = set(after["captain_id"])
    at2["nudged_after_fitness"] = at2["captain_id"].isin(nudged_after)
    print(f"  any nudge with sent_ts ≥ fitness_pass_ts: {fmt_rate(int(at2['nudged_after_fitness'].sum()), len(at2))}")

    # correlate nudge-after-fitness with eventually uploading insurance
    k_nudge_up = int((at2["nudged_after_fitness"] & at2["upl_INSURANCE"].eq(1)).sum())
    n_nudge = int(at2["nudged_after_fitness"].sum())
    k_none_up = int((~at2["nudged_after_fitness"] & at2["upl_INSURANCE"].eq(1)).sum())
    n_none = int((~at2["nudged_after_fitness"]).sum())
    print("  Insurance upload | nudged after Fitness vs not:")
    print(f"    nudged after Fitness: {fmt_rate(k_nudge_up, n_nudge)}")
    print(f"    not nudged after:     {fmt_rate(k_none_up, n_none)}")
    z, pz = two_prop_z(k_nudge_up, n_nudge, k_none_up, n_none)
    print(f"    two-proportion z={z:.2f} p={pz:.4g}")
    print("    this is an association, not an experiment (who gets a nudge is not random).")

    print("  nudge-after-Fitness coverage by channel (at-risk Insurance):")
    for ch in FOCUS:
        sl = at2[at2["acquisition_channel"] == ch]
        print(f"    {ch:<16} nudged-after {fmt_rate(int(sl['nudged_after_fitness'].sum()), len(sl))}  "
              f"upload {fmt_rate(int(sl['upl_INSURANCE'].sum()), len(sl))}")
        s_n = sl[sl["nudged_after_fitness"]]
        s_x = sl[~sl["nudged_after_fitness"]]
        print(
            f"      upload | nudged-after {fmt_rate(int(s_n['upl_INSURANCE'].sum()), len(s_n))}  "
            f"| not {fmt_rate(int(s_x['upl_INSURANCE'].sum()), len(s_x))}"
        )

    if len(after):
        delay = (
            after.groupby("captain_id")["sent_ts"].min()
            - at2.set_index("captain_id")["fitness_pass_ts"]
        ).dt.total_seconds() / 86400
        delay = delay.dropna()
        print("  days Fitness-pass → first subsequent nudge (among those with one):")
        print(delay.describe(percentiles=[0.25, 0.5, 0.75]).to_string())

    # abandonment vs upload: time from fitness to extract for abandoners
    print("\n  days Fitness-pass → extract among abandoners vs uploaders (censoring clock, not time-to-upload):")
    at2["days_fit_to_extract"] = (
        EXTRACTION_TS - at2["fitness_pass_ts"]
    ).dt.total_seconds() / 86400
    print("    abandoners:")
    print(at2.loc[at2["upl_INSURANCE"] == 0, "days_fit_to_extract"].describe().to_string())
    print("    uploaders:")
    print(at2.loc[at2["upl_INSURANCE"] == 1, "days_fit_to_extract"].describe().to_string())


def c1_channel_mix(funnel: pd.DataFrame, rc_only_capture_ids: pd.Series, ins_only_capture_ids: pd.Series) -> None:
    hr("5. C1 PURE CAPTURE-ONLY COHORT — reframed on channel, not device_tier")
    print("  Definition used (C1 was not a named object in the repo; this is the operationalisation):")
    print("    mature ∩ has-doc_events, uploaded the stage, never passed it, and ALL")
    print("    verification_fail reasons on that stage ∈ {image_blurred, ocr_low_confidence,")
    print("    details_not_legible}. No eligibility codes on that stage.")
    print("  RC is the main capture leak; Insurance's 759 uploaded-fails are the second slice.")
    print("  Combined unique captains = union of the two stage-level sets.")
    print("  Not sized as an activation impact here — channel mix only.")

    rc_ids = set(rc_only_capture_ids)
    ins_ids = set(ins_only_capture_ids)
    union_ids = rc_ids | ins_ids
    print(f"  RC capture-only never-pass:         {len(rc_ids):,}")
    print(f"  Insurance capture-only never-pass:  {len(ins_ids):,}")
    print(f"  union (unique captains):            {len(union_ids):,}")
    print(f"  overlap RC ∩ Insurance:             {len(rc_ids & ins_ids):,}")

    c1 = funnel[funnel["captain_id"].isin(union_ids)].copy()
    n = len(c1)
    print(f"\n  channel mix of the union n={n:,}:")
    for ch, cnt in c1["acquisition_channel"].value_counts().items():
        print(f"    {ch:<16} {fmt_rate(cnt, n)}")
    n_ss = int(c1["acquisition_channel"].isin(SELF_SERVE).sum())
    n_fos = int(c1["acquisition_channel"].eq(FOS).sum())
    n_other = n - n_ss - n_fos
    print(f"  self-serve (organic_app + paid_digital): {fmt_rate(n_ss, n)}")
    print(f"  fos_field:                               {fmt_rate(n_fos, n)}")
    print(f"  other (referral + gc_telecalling):       {fmt_rate(n_other, n)}")

    print("\n  device_tier mix (supporting contrast only — not the target slice):")
    for d, cnt in c1["device_tier"].value_counts().items():
        print(f"    {d:<16} {fmt_rate(cnt, n)}")

    print("\n  RC-only capture-fail channel mix:")
    rc = funnel[funnel["captain_id"].isin(rc_ids)]
    for ch, cnt in rc["acquisition_channel"].value_counts().items():
        print(f"    {ch:<16} {fmt_rate(cnt, len(rc))}")
    print(
        f"    self-serve share {fmt_rate(int(rc['acquisition_channel'].isin(SELF_SERVE).sum()), len(rc))}  "
        f"fos share {fmt_rate(int(rc['acquisition_channel'].eq(FOS).sum()), len(rc))}"
    )


def main() -> None:
    hr("STEP 4 — LEADING LEAKS THROUGH THE CHANNEL LENS")
    print(f"extract: {EXTRACTION_LABEL}")
    print("Headline: fos_field vs self-serve (organic_app, paid_digital).")
    print("vehicle_type/ERickshaw is omitted from this printout on purpose.")
    print("Multiple-comparison: channel pairwise tests vs fos use Bonferroni α=0.05/4=0.0125")
    print("when 4 non-fos channels are compared; 50/75/100% is a sensitivity range, not a CI.")

    df, docs, nudges = load()
    ip_max = float(df["_ip_max"].iloc[0])
    mature = df[df["mature"]].copy()
    funnel = mature[mature["has_doc_events"]].copy()
    assert len(funnel) == 21024, len(funnel)
    assert int((~mature["has_doc_events"]).sum()) == 1416

    tmin, tmax = mature["signup_ts"].min(), mature["signup_ts"].max()
    span_days = (tmax - tmin).days + 1  # inclusive
    months = span_days / 30.437
    print(f"\nmature signup window: {tmin} → {tmax}  ({span_days} inclusive days ≈ {months:.3f} months of 30.437d)")
    print("per-month figures = cohort total / that month-count (June is truncated by the mature cut).")
    print(f"mature n={len(mature):,}  event-funnel n={len(funnel):,}")

    hr("1. CHANNEL EFFECT ACROSS THE FULL FUNNEL")
    print("Self-serve = organic_app + paid_digital. Counterfactual = those captains face")
    print("fos_field's device-tier-specific conversion rates (device mix held at self-serve's).")
    print("Stage rates come from fos_field at-risk cells; n<100 cells are flagged.")

    for doc in STAGE_DOCS:
        print_stage_channel_rates(funnel, doc)

    never_attempt_device_std(mature)

    fos_rates, fos_permit, fos_fit_ac, fos_fit_er, p_appr_fos, cell_ns = collect_fos_stage_rates(funnel)
    sub("fos_field P(approved | cleared all required docs) — applied after Insurance")
    fos_cleared = funnel[funnel["acquisition_channel"].eq(FOS) & funnel["cleared_INSURANCE"]]
    print(
        f"  {fmt_rate(int((fos_cleared['final_status']=='approved').sum()), len(fos_cleared))}  "
        f"(eligibility gates, not a doc stage)"
    )
    print("  fos cell sizes used for sequential rates (k passed / n at-risk):")
    for doc, mp in cell_ns.items():
        for d, (k, n) in mp.items():
            flag = "  [n<100]" if n < 100 else ""
            print(f"    {doc:<12} {d:<4} {k:,}/{n:,}{flag}")

    sub("Component (a) — stage-conversion gap among captains who already have doc_events")
    print("  Sequential: product of fos device-specific step rates along each captain's path.")
    print("  Compared to their observed cleared-all / approved counts.")
    print("  Does NOT add the 1,416 never-attempters.")

    results_a = {}
    for ch in SELF_SERVE:
        starters = funnel[funnel["acquisition_channel"] == ch].copy()
        r = sequential_expected(
            funnel, starters, fos_rates, fos_permit, fos_fit_ac, fos_fit_er, p_appr_fos
        )
        results_a[ch] = r
        gap_clear = r["exp_cleared"] - r["obs_cleared"]
        gap_appr = r["exp_approved"] - r["obs_approved"]
        print(f"\n  {ch} event-funnel starters n={r['n_starters']:,.0f}")
        print(f"    observed cleared-all {r['obs_cleared']:,.0f}  approved {r['obs_approved']:,.0f}")
        print(f"    expected under fos device-specific rates: cleared-all {r['exp_cleared']:,.1f}  "
              f"approved {r['exp_approved']:,.1f}")
        print(f"    gap (100% close): cleared-all {gap_clear:+,.1f}  approved {gap_appr:+,.1f}")

    sub("Component (b) — never-attempted gap (mature signups with zero doc_events)")
    print("  Extra starters if never-attempt rate matched fos_field's device-specific rates")
    print("  at the channel's own device mix, then those extra starters flow through the")
    print("  same fos sequential rates as (a).")
    fos_m = mature[mature["acquisition_channel"] == FOS]
    p_never_fos_d = {
        d: (~fos_m.loc[fos_m["device_tier"] == d, "has_doc_events"]).mean()
        for d in DEVICES
    }
    results_b = {}
    for ch in SELF_SERVE:
        sl = mature[mature["acquisition_channel"] == ch]
        extra_by_d = {}
        extra_total = 0.0
        for d in DEVICES:
            sl_d = sl[sl["device_tier"] == d]
            n_d = len(sl_d)
            obs_never = (~sl_d["has_doc_events"]).sum()
            exp_never = n_d * p_never_fos_d[d]
            extra = max(0.0, obs_never - exp_never)
            extra_by_d[d] = extra
            extra_total += extra
        # flow extra starters: simulate extra_d captains of device d through fos path.
        # Use channel's vehicle mix among never-attempters (or among all mature) for Permit skip.
        never = sl[~sl["has_doc_events"]]
        # expected clear per extra starter of device d = mean fos-path p over never-attempters'
        # vehicle mix in that channel (fallback: channel overall vehicle mix).
        mix_src = never if len(never) else sl
        exp_clear_b = 0.0
        for d in DEVICES:
            extra_d = extra_by_d[d]
            if extra_d <= 0:
                continue
            src_d = mix_src[mix_src["device_tier"] == d]
            if src_d.empty:
                src_d = sl[sl["device_tier"] == d]
            share_permit = src_d["needs_permit"].mean() if len(src_d) else 1.0
            p_ac = (
                fos_rates["DL"][d]
                * fos_rates["RC"][d]
                * fos_rates["AADHAAR"][d]
                * fos_permit[d]
                * fos_fit_ac[d]
                * fos_rates["INSURANCE"][d]
            )
            p_er = (
                fos_rates["DL"][d]
                * fos_rates["RC"][d]
                * fos_rates["AADHAAR"][d]
                * fos_fit_er[d]
                * fos_rates["INSURANCE"][d]
            )
            p = share_permit * p_ac + (1 - share_permit) * p_er
            exp_clear_b += extra_d * p
        results_b[ch] = {
            "extra_starters": extra_total,
            "exp_cleared": exp_clear_b,
            "exp_approved": exp_clear_b * p_appr_fos,
            "extra_by_d": extra_by_d,
        }
        print(f"\n  {ch}: extra starters vs fos never-attempt (device-std) = {extra_total:,.1f}")
        for d in DEVICES:
            print(f"      {d}: {extra_by_d[d]:,.1f}")
        print(
            f"    if those extra starters convert at fos path rates: "
            f"cleared-all {exp_clear_b:,.1f}  approved {exp_clear_b * p_appr_fos:,.1f}"
        )

    sub("Combined (a)+(b) and per-month, sensitivity 50/75/100% of the fos vs self-serve gap")
    print("  Endpoint = additional APPROVED captains (fos P(approved|cleared-all) after Insurance).")
    print("  Also showing additional all-required-cleared. Range is mechanical % of gap, not a CI.")
    gap_appr_a = sum(results_a[ch]["exp_approved"] - results_a[ch]["obs_approved"] for ch in SELF_SERVE)
    gap_appr_b = sum(results_b[ch]["exp_approved"] for ch in SELF_SERVE)
    gap_clr_a = sum(results_a[ch]["exp_cleared"] - results_a[ch]["obs_cleared"] for ch in SELF_SERVE)
    gap_clr_b = sum(results_b[ch]["exp_cleared"] for ch in SELF_SERVE)
    print(f"  months in mature window: {months:.3f}")
    print(f"  (a) approved gap 100%: {gap_appr_a:,.1f}  ({gap_appr_a / months:,.1f} / month)")
    print(f"  (b) approved gap 100%: {gap_appr_b:,.1f}  ({gap_appr_b / months:,.1f} / month)")
    print(f"  (a) cleared-all gap 100%: {gap_clr_a:,.1f}")
    print(f"  (b) cleared-all gap 100%: {gap_clr_b:,.1f}")
    print()
    print(f"  {'close':>6}  {'(a) appr':>12}  {'(b) appr':>12}  {'a+b appr':>12}  "
          f"{'(a)/mo':>10}  {'(b)/mo':>10}  {'a+b/mo':>10}")
    for frac in (0.50, 0.75, 1.00):
        a, b = gap_appr_a * frac, gap_appr_b * frac
        print(
            f"  {100 * frac:5.0f}%  {a:12,.1f}  {b:12,.1f}  {a + b:12,.1f}  "
            f"{a / months:10,.1f}  {b / months:10,.1f}  {(a + b) / months:10,.1f}"
        )
    print("\n  by self-serve channel, 100% close, approved:")
    for ch in SELF_SERVE:
        a = results_a[ch]["exp_approved"] - results_a[ch]["obs_approved"]
        b = results_b[ch]["exp_approved"]
        print(f"    {ch:<16} (a) {a:,.1f}  (b) {b:,.1f}  sum {a+b:,.1f}  /month {(a+b)/months:,.1f}")

    print("\n  LIMITATION — not computed, named as a follow-up:")
    print("  paid_digital's 11.45% never-attempt rate is a channel-quality red flag, but this")
    print("  extract has no cost-per-acquisition, spend, or bid field. A CAC-efficiency")
    print("  comparison across fos_field / organic_app / paid_digital cannot be computed from")
    print("  what's given. Follow-up ask: finance/growth to supply CAC (or spend + attributed")
    print("  signups) by acquisition_channel for the same Jan–mid-June window.")

    hr("2. RC AND INSURANCE FAILURE-REASON MIX (supporting depth)")
    rc_ids = failure_reason_block(funnel, docs, "RC")
    ins_ids = failure_reason_block(funnel, docs, "INSURANCE")

    insurance_abandon(funnel, docs, nudges)
    c1_channel_mix(funnel, rc_ids, ins_ids)

    print("\nStep 4 complete. No campaign evaluation. No vehicle_type section.")


if __name__ == "__main__":
    main()
