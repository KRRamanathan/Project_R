#!/usr/bin/env python3
"""
STEP 1 — Data audit only.
Describe schema, nulls, dtypes, duplicates, timestamp ranges, categorical
cross-tabs vs outcomes, and referential / internal consistency checks.
No funnel construction. No causal conclusions.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent
EXTRACTION_TS = pd.Timestamp("2026-06-30 23:59:00")  # IST, as stated in brief
EXTRACTION_LABEL = "2026-06-30 23:59 IST"

EXPECTED = {
    "captains.csv": [
        "captain_id",
        "signup_ts",
        "city",
        "vehicle_type",
        "acquisition_channel",
        "signup_zone_id",
        "device_tier",
        "app_language",
        "age_band",
    ],
    "doc_events.csv": [
        "event_id",
        "captain_id",
        "doc_type",
        "attempt_no",
        "event_type",
        "event_ts",
        "failure_reason",
    ],
    "approvals.csv": [
        "captain_id",
        "decision_ts",
        "final_status",
        "last_stage_reached",
        "docs_cleared",
    ],
    "activation.csv": [
        "captain_id",
        "first_order_ts",
        "orders_d7",
        "orders_d30",
        "online_hours_d30",
    ],
    "nudges.csv": [
        "captain_id",
        "campaign_id",
        "channel",
        "sent_ts",
        "delivered",
        "clicked",
    ],
    "airport_hourly.csv": [
        "zone_id",
        "zone_type",
        "hour_ts",
        "requests",
        "fulfilled_requests",
        "unfulfilled_requests",
        "online_captains",
        "avg_eta_min",
        "avg_surge_multiplier",
    ],
    "airport_trips.csv": [
        "trip_id",
        "pickup_zone_id",
        "drop_zone_id",
        "drop_zone_type",
        "request_ts",
        "trip_distance_km",
        "captain_cancelled",
        "got_return_fare_within_20min",
        "fare_inr",
    ],
}

TS_COLS = {
    "captains.csv": ["signup_ts"],
    "doc_events.csv": ["event_ts"],
    "approvals.csv": ["decision_ts"],
    "activation.csv": ["first_order_ts"],
    "nudges.csv": ["sent_ts"],
    "airport_hourly.csv": ["hour_ts"],
    "airport_trips.csv": ["request_ts"],
}

KEY_COLS = {
    "captains.csv": ["captain_id"],
    "doc_events.csv": ["event_id"],
    "approvals.csv": ["captain_id"],
    "activation.csv": ["captain_id"],
    "nudges.csv": None,  # not unique by captain
    "airport_hourly.csv": ["zone_id", "hour_ts"],
    "airport_trips.csv": ["trip_id"],
}

OUTCOME_FIELDS = {
    "approvals.csv": ["final_status"],
    "activation.csv": [],  # first_order presence treated separately
    "nudges.csv": ["delivered", "clicked"],
    "airport_trips.csv": ["captain_cancelled", "got_return_fare_within_20min"],
}


def hr(title: str, char: str = "=") -> None:
    print("\n" + char * 88)
    print(title)
    print(char * 88)


def sub(title: str) -> None:
    print("\n" + "-" * 88)
    print(title)
    print("-" * 88)


def load_all() -> dict[str, pd.DataFrame]:
    frames = {}
    for name in EXPECTED:
        path = DATA_DIR / name
        if not path.exists():
            print(f"MISSING FILE: {path}")
            frames[name] = pd.DataFrame()
            continue
        frames[name] = pd.read_csv(path)
    return frames


def schema_check(name: str, df: pd.DataFrame) -> None:
    expected = EXPECTED[name]
    actual = list(df.columns)
    print(f"rows={len(df):,}  cols={len(actual)}")
    print(f"expected columns: {expected}")
    print(f"actual columns:   {actual}")
    missing = [c for c in expected if c not in actual]
    extra = [c for c in actual if c not in expected]
    print(f"missing vs brief: {missing or 'none'}")
    print(f"extra vs brief:   {extra or 'none'}")
    print("\ndtypes:")
    print(df.dtypes.to_string())
    print("\nmemory (approx):", f"{df.memory_usage(deep=True).sum() / 1e6:.2f} MB")


def null_check(df: pd.DataFrame) -> None:
    n = len(df)
    rows = []
    for col in df.columns:
        n_null = int(df[col].isna().sum())
        empty_str = 0
        if df[col].dtype == object or pd.api.types.is_string_dtype(df[col]):
            empty_str = int((df[col].astype(str).str.strip() == "").sum())
            # empty string after fillna would count NaN as 'nan' — handle separately
            empty_str = int(((df[col].notna()) & (df[col].astype(str).str.strip() == "")).sum())
        rows.append(
            {
                "column": col,
                "nulls": n_null,
                "null_pct": round(100 * n_null / n, 3) if n else None,
                "empty_string": empty_str,
                "nunique": int(df[col].nunique(dropna=True)),
            }
        )
    print(pd.DataFrame(rows).to_string(index=False))


def duplicate_check(name: str, df: pd.DataFrame) -> None:
    full_dups = int(df.duplicated().sum())
    print(f"full-row duplicates: {full_dups:,}")
    keys = KEY_COLS[name]
    if keys is None:
        print("declared primary key: none (event-level / multi-row per captain expected)")
        if "captain_id" in df.columns:
            vc = df["captain_id"].value_counts()
            print(f"unique captain_id: {df['captain_id'].nunique():,}")
            print(f"rows per captain: min={vc.min()} p50={vc.median():.1f} max={vc.max()}")
        return
    missing_keys = [k for k in keys if k not in df.columns]
    if missing_keys:
        print(f"cannot check key uniqueness; missing {missing_keys}")
        return
    key_dups = int(df.duplicated(subset=keys).sum())
    print(f"declared key {keys}: duplicate extra rows = {key_dups:,}")
    print(f"unique key combinations: {df[keys].drop_duplicates().shape[0]:,} / {len(df):,} rows")


def timestamp_check(name: str, df: pd.DataFrame) -> None:
    cols = TS_COLS.get(name, [])
    for col in cols:
        if col not in df.columns:
            print(f"{col}: column missing")
            continue
        raw_null = int(df[col].isna().sum())
        parsed = pd.to_datetime(df[col], errors="coerce")
        parse_fail = int(parsed.isna().sum() - raw_null)
        print(f"\n{col}:")
        print(f"  nulls={raw_null:,}  unparseable_non_null={parse_fail:,}")
        valid = parsed.dropna()
        if valid.empty:
            print("  no valid timestamps")
            continue
        print(f"  min={valid.min()}  max={valid.max()}")
        before_2026 = int((valid < pd.Timestamp("2026-01-01")).sum())
        after_extract = int((valid > EXTRACTION_TS).sum())
        print(f"  < 2026-01-01: {before_2026:,}")
        print(f"  > extraction ({EXTRACTION_LABEL}): {after_extract:,}")
        print("  by calendar month (valid timestamps):")
        monthly = valid.dt.to_period("M").value_counts().sort_index()
        print(monthly.to_string())
        # naive vs timezone: raw strings with offset?
        sample = df.loc[df[col].notna(), col].astype(str).head(3).tolist()
        has_tz = df.loc[df[col].notna(), col].astype(str).str.contains(r"Z|[+-]\d{2}:\d{2}", regex=True)
        print(f"  sample values: {sample}")
        print(f"  values that look timezone-aware: {int(has_tz.sum()):,} / {int(df[col].notna().sum()):,}")


def value_counts_block(df: pd.DataFrame, cols: list[str], top: int = 30) -> None:
    for col in cols:
        if col not in df.columns:
            continue
        vc = df[col].value_counts(dropna=False)
        print(f"\n{col}  (nunique={df[col].nunique(dropna=True)}, shown up to {top}):")
        print(vc.head(top).to_string())
        if len(vc) > top:
            print(f"  ... {len(vc) - top} more levels")


def crosstab_print(df: pd.DataFrame, row: str, col: str, margins: bool = True) -> None:
    if row not in df.columns or col not in df.columns:
        print(f"skip crosstab {row} x {col}: missing column")
        return
    ct = pd.crosstab(df[row].fillna("<NA>"), df[col].fillna("<NA>"), margins=margins)
    print(f"\ncrosstab: {row} x {col}  (counts; n={len(df):,})")
    print(ct.to_string())


def numeric_summary(df: pd.DataFrame, cols: list[str]) -> None:
    present = [c for c in cols if c in df.columns]
    if not present:
        return
    print("\nnumeric describe:")
    print(df[present].describe(percentiles=[0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99]).T.to_string())
    for c in present:
        n_neg = int((pd.to_numeric(df[c], errors="coerce") < 0).sum())
        print(f"  {c}: negatives={n_neg:,}")


def audit_captains(df: pd.DataFrame) -> None:
    hr("FILE: captains.csv")
    schema_check("captains.csv", df)
    sub("nulls / emptiness / cardinality")
    null_check(df)
    sub("duplicates")
    duplicate_check("captains.csv", df)
    sub("timestamps")
    timestamp_check("captains.csv", df)
    sub("categorical value counts")
    value_counts_block(
        df,
        ["city", "vehicle_type", "acquisition_channel", "device_tier", "app_language", "age_band"],
    )
    print("\nsignup_zone_id: nunique=", df["signup_zone_id"].nunique(dropna=True))
    print("zone prefix x city (first token before '-'):")
    prefix = df["signup_zone_id"].astype(str).str.split("-").str[0]
    print(pd.crosstab(df["city"].fillna("<NA>"), prefix.fillna("<NA>"), margins=True).to_string())
    sub("city x vehicle_type")
    crosstab_print(df, "city", "vehicle_type")
    sub("city x acquisition_channel")
    crosstab_print(df, "city", "acquisition_channel")
    sub("city x device_tier")
    crosstab_print(df, "city", "device_tier")
    sub("vehicle_type x device_tier")
    crosstab_print(df, "vehicle_type", "device_tier")
    sub("acquisition_channel x device_tier")
    crosstab_print(df, "acquisition_channel", "device_tier")
    sub("age_band x vehicle_type")
    crosstab_print(df, "age_band", "vehicle_type")


def audit_doc_events(df: pd.DataFrame) -> None:
    hr("FILE: doc_events.csv")
    schema_check("doc_events.csv", df)
    sub("nulls / emptiness / cardinality")
    null_check(df)
    sub("duplicates")
    duplicate_check("doc_events.csv", df)
    sub("timestamps")
    timestamp_check("doc_events.csv", df)
    sub("categorical value counts")
    value_counts_block(df, ["doc_type", "event_type", "failure_reason", "attempt_no"])
    sub("event_type x doc_type")
    crosstab_print(df, "doc_type", "event_type")
    sub("failure_reason x event_type")
    crosstab_print(df, "failure_reason", "event_type")
    sub("failure_reason x doc_type (verification_fail only)")
    fails = df[df["event_type"] == "verification_fail"]
    print(f"verification_fail rows n={len(fails):,}")
    if not fails.empty:
        crosstab_print(fails, "doc_type", "failure_reason")
        n_fail_no_reason = int(fails["failure_reason"].isna().sum())
        print(f"verification_fail with null failure_reason: {n_fail_no_reason:,}")
    non_fail = df[df["event_type"] != "verification_fail"]
    n_reason_on_nonfail = int(non_fail["failure_reason"].notna().sum())
    print(f"non-fail events with non-null failure_reason: {n_reason_on_nonfail:,}")

    sub("attempt_no distribution by event_type")
    crosstab_print(df, "attempt_no", "event_type")
    print("\nattempt_no describe:", df["attempt_no"].describe().to_string())
    gt3 = int((df["attempt_no"] > 3).sum())
    lt1 = int((df["attempt_no"] < 1).sum())
    print(f"attempt_no > 3 (brief says up to 3 attempts): {gt3:,}")
    print(f"attempt_no < 1: {lt1:,}")

    sub("per (captain, doc, attempt) event mix")
    g = df.groupby(["captain_id", "doc_type", "attempt_no"])["event_type"].agg(list)
    n_groups = len(g)
    has_upload = g.apply(lambda x: "upload_success" in x)
    n_pass_and_fail = int(
        g.apply(lambda x: "verification_pass" in x and "verification_fail" in x).sum()
    )
    n_multi_same = int(g.apply(lambda x: len(x) != len(set(x))).sum())
    n_no_upload = int((~has_upload).sum())
    n_verify_no_upload = int(
        g.apply(
            lambda x: ("verification_pass" in x or "verification_fail" in x)
            and "upload_success" not in x
        ).sum()
    )
    print(f"(captain_id, doc_type, attempt_no) groups: {n_groups:,}")
    print(f"groups with both pass and fail: {n_pass_and_fail:,}")
    print(f"groups with duplicate event_type in list: {n_multi_same:,}")
    print(f"groups with no upload_success: {n_no_upload:,}")
    print(f"groups with verify event but no upload_success: {n_verify_no_upload:,}")

    sub("events per captain")
    ev_per = df.groupby("captain_id").size()
    print(ev_per.describe(percentiles=[0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99]).to_string())
    print(f"captains with 0 events in this file: n/a here; see cross-file section")


def audit_approvals(df: pd.DataFrame) -> None:
    hr("FILE: approvals.csv")
    schema_check("approvals.csv", df)
    sub("nulls / emptiness / cardinality")
    null_check(df)
    sub("duplicates")
    duplicate_check("approvals.csv", df)
    sub("timestamps")
    timestamp_check("approvals.csv", df)
    sub("categorical / outcome value counts")
    value_counts_block(df, ["final_status", "last_stage_reached", "docs_cleared"])
    sub("final_status x last_stage_reached")
    crosstab_print(df, "final_status", "last_stage_reached")
    sub("final_status x docs_cleared")
    crosstab_print(df, "final_status", "docs_cleared")
    sub("decision_ts nulls by final_status")
    tmp = df.copy()
    tmp["decision_ts_null"] = tmp["decision_ts"].isna()
    crosstab_print(tmp, "final_status", "decision_ts_null")
    sub("last_stage_reached nulls by final_status")
    tmp["last_stage_null"] = tmp["last_stage_reached"].isna()
    crosstab_print(tmp, "final_status", "last_stage_null")

    numeric_summary(df, ["docs_cleared"])
    print("\ndocs_cleared value counts:")
    print(df["docs_cleared"].value_counts(dropna=False).sort_index().to_string())


def audit_activation(df: pd.DataFrame) -> None:
    hr("FILE: activation.csv")
    schema_check("activation.csv", df)
    sub("nulls / emptiness / cardinality")
    null_check(df)
    sub("duplicates")
    duplicate_check("activation.csv", df)
    sub("timestamps")
    timestamp_check("activation.csv", df)
    numeric_summary(df, ["orders_d7", "orders_d30", "online_hours_d30"])
    sub("first_order_ts presence")
    n_no_first = int(df["first_order_ts"].isna().sum())
    print(f"rows with null first_order_ts: {n_no_first:,} / {len(df):,}")
    sub("orders / hours vs first_order presence")
    tmp = df.copy()
    tmp["has_first_order"] = tmp["first_order_ts"].notna()
    print(
        tmp.groupby("has_first_order")[["orders_d7", "orders_d30", "online_hours_d30"]]
        .agg(["count", "mean", "median", "min", "max"])
        .to_string()
    )
    # rows with orders but no first_order
    num_d7 = pd.to_numeric(df["orders_d7"], errors="coerce")
    num_d30 = pd.to_numeric(df["orders_d30"], errors="coerce")
    print(
        f"null first_order AND orders_d7>0: {int((df['first_order_ts'].isna() & (num_d7 > 0)).sum()):,}"
    )
    print(
        f"null first_order AND orders_d30>0: {int((df['first_order_ts'].isna() & (num_d30 > 0)).sum()):,}"
    )
    print(f"orders_d7 > orders_d30: {int((num_d7 > num_d30).sum()):,}")
    print(f"has first_order AND orders_d30==0: {int((df['first_order_ts'].notna() & (num_d30 == 0)).sum()):,}")


def audit_nudges(df: pd.DataFrame) -> None:
    hr("FILE: nudges.csv")
    schema_check("nudges.csv", df)
    sub("nulls / emptiness / cardinality")
    null_check(df)
    sub("duplicates")
    duplicate_check("nudges.csv", df)
    sub("timestamps")
    timestamp_check("nudges.csv", df)
    sub("categorical / outcome value counts")
    value_counts_block(df, ["campaign_id", "channel", "delivered", "clicked"])
    sub("campaign_id x channel")
    crosstab_print(df, "campaign_id", "channel")
    sub("campaign_id x delivered")
    crosstab_print(df, "campaign_id", "delivered")
    sub("campaign_id x clicked")
    crosstab_print(df, "campaign_id", "clicked")
    sub("delivered x clicked")
    crosstab_print(df, "delivered", "clicked")
    sub("channel x delivered")
    crosstab_print(df, "channel", "delivered")
    sub("channel x clicked")
    crosstab_print(df, "channel", "clicked")
    clicked_not_delivered = int(((df["clicked"] == 1) & (df["delivered"] == 0)).sum())
    print(f"clicked=1 and delivered=0: {clicked_not_delivered:,}")


def audit_airport_hourly(df: pd.DataFrame) -> None:
    hr("FILE: airport_hourly.csv")
    schema_check("airport_hourly.csv", df)
    sub("nulls / emptiness / cardinality")
    null_check(df)
    sub("duplicates")
    duplicate_check("airport_hourly.csv", df)
    sub("timestamps")
    timestamp_check("airport_hourly.csv", df)
    sub("categorical value counts")
    value_counts_block(df, ["zone_id", "zone_type"])
    sub("zone_id x zone_type")
    crosstab_print(df, "zone_id", "zone_type")
    numeric_summary(
        df,
        [
            "requests",
            "fulfilled_requests",
            "unfulfilled_requests",
            "online_captains",
            "avg_eta_min",
            "avg_surge_multiplier",
        ],
    )
    req = pd.to_numeric(df["requests"], errors="coerce")
    ful = pd.to_numeric(df["fulfilled_requests"], errors="coerce")
    unf = pd.to_numeric(df["unfulfilled_requests"], errors="coerce")
    mismatch = int((ful + unf != req).sum())
    print(f"\nfulfilled + unfulfilled != requests: {mismatch:,} / {len(df):,}")
    if mismatch:
        diff = (ful + unf - req).describe()
        print("difference (fulfilled+unfulfilled-requests) describe:")
        print(diff.to_string())
    print(f"fulfilled > requests: {int((ful > req).sum()):,}")
    print(f"hour_ts unique values: {df['hour_ts'].nunique():,}")
    hours_per_zone = df.groupby("zone_id").size()
    print("rows per zone_id:")
    print(hours_per_zone.to_string())


def audit_airport_trips(df: pd.DataFrame) -> None:
    hr("FILE: airport_trips.csv")
    schema_check("airport_trips.csv", df)
    sub("nulls / emptiness / cardinality")
    null_check(df)
    sub("duplicates")
    duplicate_check("airport_trips.csv", df)
    sub("timestamps")
    timestamp_check("airport_trips.csv", df)
    sub("categorical / outcome value counts")
    value_counts_block(
        df,
        [
            "pickup_zone_id",
            "drop_zone_id",
            "drop_zone_type",
            "captain_cancelled",
            "got_return_fare_within_20min",
        ],
    )
    sub("pickup_zone_id x drop_zone_type")
    crosstab_print(df, "pickup_zone_id", "drop_zone_type")
    sub("captain_cancelled x got_return_fare_within_20min")
    crosstab_print(df, "captain_cancelled", "got_return_fare_within_20min")
    sub("drop_zone_type x captain_cancelled")
    crosstab_print(df, "drop_zone_type", "captain_cancelled")
    sub("drop_zone_type x got_return_fare_within_20min")
    crosstab_print(df, "drop_zone_type", "got_return_fare_within_20min")
    numeric_summary(df, ["trip_distance_km", "fare_inr"])
    print(f"\npickup == drop zone: {int((df['pickup_zone_id'] == df['drop_zone_id']).sum()):,}")


def cross_file(frames: dict[str, pd.DataFrame]) -> None:
    hr("CROSS-FILE CONSISTENCY")
    captains = frames["captains.csv"]
    docs = frames["doc_events.csv"]
    appr = frames["approvals.csv"]
    act = frames["activation.csv"]
    nudges = frames["nudges.csv"]
    hourly = frames["airport_hourly.csv"]
    trips = frames["airport_trips.csv"]

    cap_ids = set(captains["captain_id"].dropna())
    doc_ids = set(docs["captain_id"].dropna())
    appr_ids = set(appr["captain_id"].dropna())
    act_ids = set(act["captain_id"].dropna())
    nudge_ids = set(nudges["captain_id"].dropna())

    print(f"captains unique ids: {len(cap_ids):,}")
    print(f"doc_events unique captain_id: {len(doc_ids):,}")
    print(f"approvals unique ids: {len(appr_ids):,}")
    print(f"activation unique ids: {len(act_ids):,}")
    print(f"nudges unique captain_id: {len(nudge_ids):,}")

    def set_diff(a: set, b: set, a_name: str, b_name: str) -> None:
        only_a = len(a - b)
        only_b = len(b - a)
        both = len(a & b)
        print(f"  {a_name} ∩ {b_name} = {both:,}; only {a_name}={only_a:,}; only {b_name}={only_b:,}")

    print("\nset overlaps (captain_id):")
    set_diff(cap_ids, appr_ids, "captains", "approvals")
    set_diff(cap_ids, doc_ids, "captains", "doc_events")
    set_diff(appr_ids, doc_ids, "approvals", "doc_events")
    set_diff(cap_ids, act_ids, "captains", "activation")
    set_diff(appr_ids, act_ids, "approvals", "activation")
    set_diff(cap_ids, nudge_ids, "captains", "nudges")
    set_diff(appr_ids, nudge_ids, "approvals", "nudges")

    sub("activation vs approvals.final_status")
    merged_act = act.merge(appr[["captain_id", "final_status"]], on="captain_id", how="left")
    print("activation rows by approvals.final_status (NA = not in approvals):")
    print(merged_act["final_status"].value_counts(dropna=False).to_string())
    approved = set(appr.loc[appr["final_status"] == "approved", "captain_id"])
    print(f"approved in approvals: {len(approved):,}")
    print(f"approved missing from activation: {len(approved - act_ids):,}")
    print(f"activation not approved: {len(act_ids - approved):,}")

    sub("doc coverage vs captains / approvals")
    no_docs = cap_ids - doc_ids
    print(f"captains with zero doc_events: {len(no_docs):,}")
    if no_docs:
        nodoc_appr = appr[appr["captain_id"].isin(no_docs)]
        print("final_status for captains with zero doc_events:")
        print(nodoc_appr["final_status"].value_counts(dropna=False).to_string())
        print("last_stage_reached for captains with zero doc_events:")
        print(nodoc_appr["last_stage_reached"].value_counts(dropna=False).to_string())
        print("docs_cleared for captains with zero doc_events:")
        print(nodoc_appr["docs_cleared"].value_counts(dropna=False).to_string())

    sub("approvals.docs_cleared vs doc_events verification_pass uniqueness")
    passed = (
        docs[docs["event_type"] == "verification_pass"]
        .groupby("captain_id")["doc_type"]
        .nunique()
        .rename("n_unique_docs_passed")
    )
    cmp = appr.merge(passed, on="captain_id", how="left")
    cmp["n_unique_docs_passed"] = cmp["n_unique_docs_passed"].fillna(0).astype(int)
    print("docs_cleared vs nunique verification_pass doc_types:")
    ct = pd.crosstab(cmp["docs_cleared"].fillna("<NA>"), cmp["n_unique_docs_passed"], margins=True)
    print(ct.to_string())
    mismatch = cmp[cmp["docs_cleared"].fillna(-1) != cmp["n_unique_docs_passed"]]
    print(f"rows where docs_cleared != nunique passed docs: {len(mismatch):,}")
    if len(mismatch):
        print("mismatch by final_status:")
        print(mismatch["final_status"].value_counts(dropna=False).to_string())
        print("sample of mismatches (up to 10):")
        print(
            mismatch[
                ["captain_id", "final_status", "docs_cleared", "n_unique_docs_passed", "last_stage_reached"]
            ]
            .head(10)
            .to_string(index=False)
        )

    sub("signup_ts vs first event / decision / first_order / nudge")
    cap_ts = captains[["captain_id", "signup_ts"]].copy()
    cap_ts["signup_ts"] = pd.to_datetime(cap_ts["signup_ts"], errors="coerce")

    first_ev = docs.copy()
    first_ev["event_ts"] = pd.to_datetime(first_ev["event_ts"], errors="coerce")
    first_ev = first_ev.groupby("captain_id")["event_ts"].min().rename("first_event_ts")
    m = cap_ts.merge(first_ev, on="captain_id", how="left")
    both = m.dropna(subset=["signup_ts", "first_event_ts"])
    print(f"captains with signup and at least one event: {len(both):,}")
    print(f"first_event_ts < signup_ts: {int((both['first_event_ts'] < both['signup_ts']).sum()):,}")

    appr_ts = appr.copy()
    appr_ts["decision_ts"] = pd.to_datetime(appr_ts["decision_ts"], errors="coerce")
    m2 = cap_ts.merge(appr_ts[["captain_id", "decision_ts", "final_status"]], on="captain_id", how="left")
    both2 = m2.dropna(subset=["signup_ts", "decision_ts"])
    print(f"captains with signup and decision_ts: {len(both2):,}")
    print(f"decision_ts < signup_ts: {int((both2['decision_ts'] < both2['signup_ts']).sum()):,}")

    last_ev = docs.copy()
    last_ev["event_ts"] = pd.to_datetime(last_ev["event_ts"], errors="coerce")
    last_ev = last_ev.groupby("captain_id")["event_ts"].max().rename("last_event_ts")
    m3 = appr_ts.merge(last_ev, on="captain_id", how="left")
    both3 = m3.dropna(subset=["decision_ts", "last_event_ts"])
    print(f"captains with decision_ts and last_event_ts: {len(both3):,}")
    print(f"decision_ts < last_event_ts: {int((both3['decision_ts'] < both3['last_event_ts']).sum()):,}")

    act_ts = act.copy()
    act_ts["first_order_ts"] = pd.to_datetime(act_ts["first_order_ts"], errors="coerce")
    m4 = cap_ts.merge(act_ts, on="captain_id", how="left").merge(
        appr[["captain_id", "decision_ts", "final_status"]], on="captain_id", how="left"
    )
    m4["decision_ts"] = pd.to_datetime(m4["decision_ts"], errors="coerce")
    both4 = m4.dropna(subset=["signup_ts", "first_order_ts"])
    print(f"captains with signup and first_order_ts: {len(both4):,}")
    print(f"first_order_ts < signup_ts: {int((both4['first_order_ts'] < both4['signup_ts']).sum()):,}")
    both5 = m4.dropna(subset=["decision_ts", "first_order_ts"])
    print(f"captains with decision_ts and first_order_ts: {len(both5):,}")
    print(f"first_order_ts < decision_ts: {int((both5['first_order_ts'] < both5['decision_ts']).sum()):,}")

    nudge_ts = nudges.copy()
    nudge_ts["sent_ts"] = pd.to_datetime(nudge_ts["sent_ts"], errors="coerce")
    first_nudge = nudge_ts.groupby("captain_id")["sent_ts"].min().rename("first_nudge_ts")
    m5 = cap_ts.merge(first_nudge, on="captain_id", how="left")
    both6 = m5.dropna(subset=["signup_ts", "first_nudge_ts"])
    print(f"captains with signup and at least one nudge: {len(both6):,}")
    print(f"first_nudge_ts < signup_ts: {int((both6['first_nudge_ts'] < both6['signup_ts']).sum()):,}")

    sub("captains attributes vs final_status (counts only)")
    cap_ap = captains.merge(appr, on="captain_id", how="outer", indicator=True)
    print("merge indicator captains vs approvals:")
    print(cap_ap["_merge"].value_counts().to_string())
    inner = captains.merge(appr, on="captain_id", how="inner")
    for col in ["city", "vehicle_type", "acquisition_channel", "device_tier", "app_language", "age_band"]:
        crosstab_print(inner, col, "final_status")

    sub("Permit applicability vs vehicle_type (from brief: Permit applies to Auto, Cab)")
    permit_events = docs[docs["doc_type"].astype(str).str.upper().isin(["PERMIT", "PERMIT "])]
    permit_caps = set(permit_events["captain_id"])
    cap_vt = captains.set_index("captain_id")["vehicle_type"]
    with_permit = captains[captains["captain_id"].isin(permit_caps)]
    print("vehicle_type among captains who have any PERMIT event:")
    print(with_permit["vehicle_type"].value_counts(dropna=False).to_string())
    bike_with_permit = int((with_permit["vehicle_type"].astype(str).str.lower() == "bike").sum())
    print(f"Bike captains with any PERMIT event: {bike_with_permit:,}")
    # Auto/Cab without permit events
    auto_cab = captains[captains["vehicle_type"].isin(["Auto", "Cab"])]
    auto_cab_no_permit = auto_cab[~auto_cab["captain_id"].isin(permit_caps)]
    print(f"Auto/Cab captains with zero PERMIT events: {len(auto_cab_no_permit):,} / {len(auto_cab):,}")
    if len(auto_cab_no_permit):
        print("final_status for Auto/Cab with zero PERMIT events:")
        print(
            appr[appr["captain_id"].isin(auto_cab_no_permit["captain_id"])]["final_status"]
            .value_counts(dropna=False)
            .to_string()
        )

    sub("doc_type inventory vs brief sequence")
    print("doc_type levels in data:")
    print(docs["doc_type"].value_counts(dropna=False).to_string())
    print("last_stage_reached levels in approvals:")
    print(appr["last_stage_reached"].value_counts(dropna=False).to_string())

    sub("airport_hourly vs airport_trips zone ids / time window")
    h_zones = set(hourly["zone_id"].dropna())
    t_pick = set(trips["pickup_zone_id"].dropna())
    t_drop = set(trips["drop_zone_id"].dropna())
    print(f"hourly zone_id: {sorted(h_zones)}")
    print(f"trip pickup_zone_id: {sorted(t_pick)}")
    print(f"trip drop_zone_id nunique={len(t_drop)} sample={sorted(list(t_drop))[:20]}")
    print(f"pickup zones not in hourly: {sorted(t_pick - h_zones)}")
    print(f"hourly zones never used as pickup: {sorted(h_zones - t_pick)}")
    print(f"drop zones that appear in hourly: {sorted(t_drop & h_zones)}")

    h_ts = pd.to_datetime(hourly["hour_ts"], errors="coerce")
    t_ts = pd.to_datetime(trips["request_ts"], errors="coerce")
    print(f"hourly hour_ts range: {h_ts.min()} -> {h_ts.max()}  n={h_ts.notna().sum():,}")
    print(f"trips request_ts range: {t_ts.min()} -> {t_ts.max()}  n={t_ts.notna().sum():,}")

    # fulfilled_requests vs trip counts (descriptive only; trips are sampled)
    print("\nNote from brief: airport_trips is sampled. Compare volume only as a sanity check.")
    trip_by_pickup_hour = trips.copy()
    trip_by_pickup_hour["hour_floor"] = pd.to_datetime(
        trip_by_pickup_hour["request_ts"], errors="coerce"
    ).dt.floor("h")
    trip_counts = (
        trip_by_pickup_hour.groupby(["pickup_zone_id", "hour_floor"]).size().rename("sampled_trips")
    )
    hourly2 = hourly.copy()
    hourly2["hour_ts"] = pd.to_datetime(hourly2["hour_ts"], errors="coerce")
    joined = hourly2.merge(
        trip_counts,
        left_on=["zone_id", "hour_ts"],
        right_on=["pickup_zone_id", "hour_floor"],
        how="left",
    )
    joined["sampled_trips"] = joined["sampled_trips"].fillna(0)
    print(
        "sampled_trips vs fulfilled_requests (hourly grain) describe of sampled/fulfilled where fulfilled>0:"
    )
    ratio = joined.loc[joined["fulfilled_requests"] > 0, "sampled_trips"] / joined.loc[
        joined["fulfilled_requests"] > 0, "fulfilled_requests"
    ]
    print(ratio.describe().to_string())
    print(f"hours with sampled_trips > fulfilled_requests: {int((joined['sampled_trips'] > joined['fulfilled_requests']).sum()):,}")
    print(f"hours with sampled_trips > requests: {int((joined['sampled_trips'] > joined['requests']).sum()):,}")

    sub("signup_zone_id vs airport zone ids")
    sz = set(captains["signup_zone_id"].dropna())
    print(f"captain signup_zone_id overlapping hourly zones: {sorted(sz & h_zones)}")
    print(f"n captains whose signup_zone_id is an hourly airport zone: {int(captains['signup_zone_id'].isin(h_zones).sum()):,}")

    sub("nudge targeting vs final_status")
    n_join = nudges.merge(appr[["captain_id", "final_status"]], on="captain_id", how="left")
    print("nudge rows by final_status:")
    print(n_join["final_status"].value_counts(dropna=False).to_string())
    print("unique captains nudged by final_status:")
    print(n_join.drop_duplicates("captain_id")["final_status"].value_counts(dropna=False).to_string())
    crosstab_print(n_join, "campaign_id", "final_status")

    sub("in_progress / right-censoring vs extraction timestamp")
    print(f"extraction timestamp (brief): {EXTRACTION_LABEL}")
    print("final_status counts:")
    print(appr["final_status"].value_counts(dropna=False).to_string())
    cap_ts2 = captains.copy()
    cap_ts2["signup_ts"] = pd.to_datetime(cap_ts2["signup_ts"], errors="coerce")
    cap_ts2["days_before_extract"] = (EXTRACTION_TS - cap_ts2["signup_ts"]).dt.total_seconds() / 86400
    merged_c = cap_ts2.merge(appr[["captain_id", "final_status"]], on="captain_id", how="left")
    print("\nsignup recency (days before extraction) by final_status:")
    print(
        merged_c.groupby("final_status")["days_before_extract"]
        .describe(percentiles=[0.1, 0.25, 0.5, 0.75, 0.9])
        .to_string()
    )
    print("\nsignups in last 14 days before extraction by final_status:")
    recent = merged_c[merged_c["days_before_extract"] <= 14]
    print(f"n signups with days_before_extract <= 14: {len(recent):,}")
    print(recent["final_status"].value_counts(dropna=False).to_string())


def items_worth_a_closer_look(frames: dict[str, pd.DataFrame]) -> None:
    """
    Observations only — flags, not conclusions.
    Recompute the most important inconsistency counts so this section is self-contained.
    """
    hr("ITEMS THAT LOOK INCONSISTENT OR WORTH A CLOSER LOOK (no conclusions)")
    captains = frames["captains.csv"]
    docs = frames["doc_events.csv"]
    appr = frames["approvals.csv"]
    act = frames["activation.csv"]
    nudges = frames["nudges.csv"]
    hourly = frames["airport_hourly.csv"]
    trips = frames["airport_trips.csv"]

    flags = []

    # 1. timestamp > extraction
    for fname, col in [
        ("captains.csv", "signup_ts"),
        ("doc_events.csv", "event_ts"),
        ("approvals.csv", "decision_ts"),
        ("activation.csv", "first_order_ts"),
        ("nudges.csv", "sent_ts"),
        ("airport_hourly.csv", "hour_ts"),
        ("airport_trips.csv", "request_ts"),
    ]:
        s = pd.to_datetime(frames[fname][col], errors="coerce")
        n = int((s > EXTRACTION_TS).sum())
        if n:
            flags.append(f"{fname}.{col}: {n:,} values after extraction {EXTRACTION_LABEL} (max={s.max()})")

    # 2. activation coverage
    approved = set(appr.loc[appr["final_status"] == "approved", "captain_id"])
    act_ids = set(act["captain_id"])
    flags.append(
        f"activation.csv has {len(act):,} rows; approved captains={len(approved):,}; "
        f"approved missing from activation={len(approved - act_ids):,}; "
        f"activation not in approved={len(act_ids - approved):,}"
    )

    # 3. captains vs approvals 1:1
    flags.append(
        f"captains n={len(captains):,} unique={captains['captain_id'].nunique():,}; "
        f"approvals n={len(appr):,} unique={appr['captain_id'].nunique():,}; "
        f"id overlap={len(set(captains['captain_id']) & set(appr['captain_id'])):,}"
    )

    # 4. decision_ts missing
    flags.append(
        "decision_ts null by final_status: "
        + str(appr.groupby("final_status")["decision_ts"].apply(lambda s: int(s.isna().sum())).to_dict())
    )

    # 5. last_stage null
    flags.append(
        "last_stage_reached null by final_status: "
        + str(appr.groupby("final_status")["last_stage_reached"].apply(lambda s: int(s.isna().sum())).to_dict())
    )

    # 6. docs with no events
    no_docs = set(captains["captain_id"]) - set(docs["captain_id"])
    flags.append(f"captains with zero rows in doc_events: {len(no_docs):,}")

    # 7. clicked not delivered
    n_bad_click = int(((nudges["clicked"] == 1) & (nudges["delivered"] == 0)).sum())
    flags.append(f"nudges with clicked=1 and delivered=0: {n_bad_click:,}")

    # 8. hourly identity
    req = pd.to_numeric(hourly["requests"], errors="coerce")
    ful = pd.to_numeric(hourly["fulfilled_requests"], errors="coerce")
    unf = pd.to_numeric(hourly["unfulfilled_requests"], errors="coerce")
    flags.append(
        f"airport_hourly rows where fulfilled+unfulfilled != requests: {int((ful + unf != req).sum()):,}"
    )

    # 9. attempt_no > 3
    flags.append(f"doc_events attempt_no > 3: {int((docs['attempt_no'] > 3).sum()):,}")

    # 10. failure_reason on non-fail
    flags.append(
        "failure_reason non-null on non-verification_fail: "
        f"{int(docs.loc[docs['event_type'] != 'verification_fail', 'failure_reason'].notna().sum()):,}; "
        "failure_reason null on verification_fail: "
        f"{int(docs.loc[docs['event_type'] == 'verification_fail', 'failure_reason'].isna().sum()):,}"
    )

    # 11. timezone-naive
    flags.append(
        "All inspected timestamp columns are timezone-naive strings (no Z / offset). "
        "Brief extraction clock is labelled IST; files do not declare timezone."
    )

    # 12. activation first order nulls
    flags.append(
        f"activation first_order_ts null: {int(act['first_order_ts'].isna().sum()):,} / {len(act):,}"
    )

    # 13. Permit vs bike
    permit_ids = set(docs.loc[docs["doc_type"].astype(str).str.upper() == "PERMIT", "captain_id"])
    bike_permit = int(
        captains.loc[captains["captain_id"].isin(permit_ids), "vehicle_type"]
        .astype(str)
        .str.lower()
        .eq("bike")
        .sum()
    )
    flags.append(f"Bike captains with PERMIT events (brief: Permit applies to Auto, Cab): {bike_permit:,}")

    passed = (
        docs[docs["event_type"] == "verification_pass"]
        .groupby("captain_id")["doc_type"]
        .nunique()
        .rename("n_pass")
    )
    cmp = appr.merge(passed, on="captain_id", how="left")
    cmp["n_pass"] = cmp["n_pass"].fillna(0)
    n_mismatch = int((cmp["docs_cleared"].fillna(-1) != cmp["n_pass"]).sum())
    flags.append(
        f"approvals.docs_cleared != nunique verification_pass doc_types: {n_mismatch:,} "
        f"(by final_status: {cmp.loc[cmp['docs_cleared'].fillna(-1) != cmp['n_pass'], 'final_status'].value_counts().to_dict()})"
    )

    d7 = pd.to_numeric(act["orders_d7"], errors="coerce")
    d30 = pd.to_numeric(act["orders_d30"], errors="coerce")
    flags.append(
        f"activation orders_d7 > orders_d30 (both non-null): {int(((d7 > d30) & d7.notna() & d30.notna()).sum()):,}; "
        f"orders_d7 null={int(act['orders_d7'].isna().sum()):,}; "
        f"orders_d30 null={int(act['orders_d30'].isna().sum()):,} "
        f"(same count as online_hours_d30 null={int(act['online_hours_d30'].isna().sum()):,})"
    )

    rej_stages = appr.loc[appr["final_status"] == "rejected", "last_stage_reached"].value_counts().to_dict()
    flags.append(f"rejected last_stage_reached values (not in the 6-doc sequence): {rej_stages}")

    approved_docs5 = int(((appr["final_status"] == "approved") & (appr["docs_cleared"] == 5)).sum())
    approved_docs6 = int(((appr["final_status"] == "approved") & (appr["docs_cleared"] == 6)).sum())
    flags.append(
        f"approved with docs_cleared=5: {approved_docs5:,}; approved with docs_cleared=6: {approved_docs6:,} "
        f"(Bike vs Auto/Cab may explain 5 vs 6; not tested here)"
    )

    flags.append(
        f"captain signup_zone_id overlap with airport_hourly zone_id: "
        f"{int(captains['signup_zone_id'].isin(set(hourly['zone_id'])).sum()):,} / {len(captains):,}"
    )

    print("Each bullet is a description of a pattern in the files, not an explanation.\n")
    for i, f in enumerate(flags, 1):
        print(f"{i:02d}. {f}")

    print("\nAudit complete. Funnel construction was not run.")


def main() -> None:
    hr("DATA AUDIT — STEP 1")
    print(f"data dir: {DATA_DIR}")
    print(f"extraction timestamp (brief): {EXTRACTION_LABEL}")
    print("This script only describes contents. No funnel. No recommendations.")
    frames = load_all()
    for name, df in frames.items():
        print(f"  loaded {name}: shape={df.shape}")

    audit_captains(frames["captains.csv"])
    audit_doc_events(frames["doc_events.csv"])
    audit_approvals(frames["approvals.csv"])
    audit_activation(frames["activation.csv"])
    audit_nudges(frames["nudges.csv"])
    audit_airport_hourly(frames["airport_hourly.csv"])
    audit_airport_trips(frames["airport_trips.csv"])
    cross_file(frames)
    items_worth_a_closer_look(frames)


if __name__ == "__main__":
    main()
