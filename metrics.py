"""Shared headline metrics — used by Step 8, regression, office builds, Streamlit.

All functions read raw CSVs only. No step depends on another step's stdout.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent
EXTRACTION_TS = pd.Timestamp("2026-06-30 23:59:00")
EXTRACTION_LABEL = "2026-06-30 23:59 IST"
SELF_SERVE = ["organic_app", "paid_digital"]
STAGE_DOCS = ["DL", "RC", "AADHAAR", "PERMIT", "FITNESS", "INSURANCE"]
CAPTURE_REASONS = {"image_blurred", "ocr_low_confidence", "details_not_legible"}
WORST_HOD = {21, 22, 23, 0, 1, 2, 3}
DAYS_PER_MONTH = 30.437
NET_WORST_SUBURBAN = 24.9
NET_REST_SUBURBAN = 56.5
NET_GAP_VS_REST_SUB = NET_REST_SUBURBAN - NET_WORST_SUBURBAN  # 31.6
C1A_CENTRAL_SHOWUP = 0.60


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


@lru_cache(maxsize=1)
def load_onboarding() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    captains = pd.read_csv(DATA_DIR / "captains.csv")
    approvals = pd.read_csv(DATA_DIR / "approvals.csv")
    docs = pd.read_csv(DATA_DIR / "doc_events.csv")
    captains["signup_ts"] = pd.to_datetime(captains["signup_ts"], errors="coerce")
    captains["signup_age_days"] = (
        EXTRACTION_TS - captains["signup_ts"]
    ).dt.total_seconds() / 86400.0
    docs["event_ts"] = pd.to_datetime(docs["event_ts"], errors="coerce")
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
    return df.copy(), docs.copy(), captains.copy()


def event_funnel() -> pd.DataFrame:
    df, _, _ = load_onboarding()
    return df[df["mature"] & df["has_doc_events"]].copy()


def mature_months() -> tuple[float, int, pd.Timestamp, pd.Timestamp]:
    df, _, _ = load_onboarding()
    mature = df[df["mature"]]
    tmin, tmax = mature["signup_ts"].min(), mature["signup_ts"].max()
    span_days = int((tmax.normalize() - tmin.normalize()).days + 1)
    return span_days / DAYS_PER_MONTH, span_days, tmin, tmax


def capture_only_never_pass(funnel: pd.DataFrame, docs: pd.DataFrame, doc: str) -> pd.Index:
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
        .agg(
            lambda s: "verification_pass"
            if (s == "verification_pass").any()
            else "verification_fail"
        )
        .reset_index()
    )
    g["passed"] = g["event_type"].eq("verification_pass")
    out = {}
    for a in (1, 2, 3):
        sl = g[g["attempt_no"] == a]
        out[a] = (int(sl["passed"].sum()), int(len(sl)))
    return out


def rc_attempt3_pass_rate() -> float:
    funnel = event_funnel()
    _, docs, _ = load_onboarding()
    k, n = attempt_pass_table(funnel, docs, "RC")[3]
    return k / n


def c1a_flow() -> tuple[int, float]:
    """Capture-only RC never-pass count and monthly flow."""
    funnel = event_funnel()
    _, docs, _ = load_onboarding()
    n = len(capture_only_never_pass(funnel, docs, "RC"))
    months, *_ = mature_months()
    return n, n / months


def c1a_monthly(show_up: float, pass_rate: float | None = None) -> float:
    """Additional captains/month under provisional RC path.

    additional = monthly_flow × P(show up in 10-day grace) × P(in-person pass).
    Default pass_rate is RC attempt-3 (floor).
    """
    _, flow = c1a_flow()
    if pass_rate is None:
        pass_rate = rc_attempt3_pass_rate()
    return flow * float(show_up) * float(pass_rate)


def c1b_n() -> int:
    funnel = event_funnel()
    _, docs, _ = load_onboarding()
    return len(capture_only_never_pass(funnel, docs, "INSURANCE"))


def c1b_monthly(attempt: int = 2) -> float:
    """Insurance capture-UX additional approved/month at attempt-k pass rate."""
    funnel = event_funnel()
    _, docs, _ = load_onboarding()
    n = len(capture_only_never_pass(funnel, docs, "INSURANCE"))
    months, *_ = mature_months()
    k, n_att = attempt_pass_table(funnel, docs, "INSURANCE")[attempt]
    pass_rate = k / n_att
    cleared = funnel[funnel["cleared_INSURANCE"]]
    p_appr = float(cleared["final_status"].eq("approved").mean())
    return (n / months) * pass_rate * p_appr


def ara_economics() -> dict:
    t = pd.read_csv(DATA_DIR / "airport_trips.csv")
    t["cancelled"] = pd.to_numeric(t["captain_cancelled"], errors="coerce").eq(1)
    t["got_return"] = pd.to_numeric(
        t["got_return_fare_within_20min"], errors="coerce"
    ).eq(1)
    t["completed"] = ~t["cancelled"]
    t["request_ts"] = pd.to_datetime(t["request_ts"], errors="coerce")
    t["hod"] = t["request_ts"].dt.hour
    t["worst"] = t["hod"].isin(WORST_HOD)
    ws = t[t["completed"] & t["worst"] & t["drop_zone_type"].eq("suburban")]
    n_ws = len(ws)
    n_elig = int((~ws["got_return"]).sum())
    share = n_elig / n_ws
    span = (t["request_ts"].max().normalize() - t["request_ts"].min().normalize()).days + 1
    months = span / DAYS_PER_MONTH
    elig_mo = n_elig / months
    payout = NET_GAP_VS_REST_SUB / share
    return {
        "n_completed_worst_sub": n_ws,
        "n_eligible": n_elig,
        "eligible_share": share,
        "elig_per_month": elig_mo,
        "payout_per_eligible_leg": payout,
        "months": months,
    }


def ara_monthly_cost(payout_frac_of_derived: float = 1.0) -> float:
    eco = ara_economics()
    return eco["elig_per_month"] * eco["payout_per_eligible_leg"] * float(
        payout_frac_of_derived
    )


def headlines() -> dict:
    funnel = event_funnel()
    n_c1a, _ = c1a_flow()
    eco = ara_economics()
    return {
        "mature_has_events_n": int(len(funnel)),
        "rc_capture_only_n": int(n_c1a),
        "insurance_capture_only_n": int(c1b_n()),
        "c1a_central_per_month": float(c1a_monthly(C1A_CENTRAL_SHOWUP)),
        "ara_payout_per_eligible_leg": float(eco["payout_per_eligible_leg"]),
        "ip_max_days": float(funnel["_ip_max"].iloc[0]),
    }
