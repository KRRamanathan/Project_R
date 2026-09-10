#!/usr/bin/env python3
"""
STEP 9 — Final packet: derived ARA payout, R2A one-liner, waterfall, print memo.

Deck lives at deck/slides.html → deck/Project_R_deck.pdf (6 landscape slides).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent
WORST_HOD = {21, 22, 23, 0, 1, 2, 3}
DAYS_PER_MONTH = 30.437
GAP_PRINTED = 31.6
EXTRACTION_TS = pd.Timestamp("2026-06-30 23:59:00")


def hr(title: str) -> None:
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)


def wilson(k, n, z=1.96):
    k, n = int(k), int(n)
    p = k / n
    z2 = z * z
    denom = 1 + z2 / n
    centre = (p + z2 / (2 * n)) / denom
    half = z * np.sqrt((p * (1 - p) + z2 / (4 * n)) / n) / denom
    return p, centre - half, centre + half


def r2a_block() -> None:
    hr("R2A — do these approvals take a trip?")
    cap = pd.read_csv(DATA_DIR / "captains.csv")
    appr = pd.read_csv(DATA_DIR / "approvals.csv")
    act = pd.read_csv(DATA_DIR / "activation.csv")
    cap["signup_ts"] = pd.to_datetime(cap["signup_ts"])
    cap["age"] = (EXTRACTION_TS - cap["signup_ts"]).dt.total_seconds() / 86400
    df = cap.merge(appr, on="captain_id", how="left")
    ip_max = float(df.loc[df["final_status"] == "in_progress", "age"].max())
    df["mature"] = df["age"] > ip_max
    act["first_order_ts"] = pd.to_datetime(act["first_order_ts"], errors="coerce")
    m = df[(df["mature"]) & (df["final_status"] == "approved")].merge(
        act, on="captain_id", how="left"
    )
    k = int(m["first_order_ts"].notna().sum())
    n = len(m)
    p, lo, hi = wilson(k, n)
    print(f"  mature approved n={n:,}  (activation is 1:1 with approved overall)")
    print(
        f"  first trip: {100 * p:.2f}% ({k:,}/{n:,})  W95% [{100 * lo:.2f},{100 * hi:.2f}]"
    )
    print("  A2O is the bottleneck. If C1a/C1b produce extra approved captains,")
    print("  historically almost all of them take a first order. We did not re-estimate")
    print("  R2A for the *stuck* capture-only cohorts (they are not yet approved).")


def ara_block() -> None:
    hr("ARA PAYOUT (derived; same as corrected Step 8)")
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
    n_ws, n_elig = len(ws), int((~ws["got_return"]).sum())
    share = n_elig / n_ws
    span = (t["request_ts"].max().normalize() - t["request_ts"].min().normalize()).days + 1
    months = span / DAYS_PER_MONTH
    elig_mo = n_elig / months
    payout = GAP_PRINTED / share
    print(f"  eligible share {100 * share:.2f}%  payout ₹{payout:.2f}/leg")
    for f in (0.8, 1.0, 1.2):
        print(f"    {100 * f:.0f}% → ₹{payout * f:.1f}/leg  ₹{elig_mo * payout * f:,.0f}/mo sample")


def main() -> None:
    import make_waterfall

    make_waterfall.main()
    r2a_block()
    ara_block()
    print("\n  C1a ops ballpark (not in extract): ~180 visits/month at 60% show-up.")
    print("  Assume 12–15 checks/day × 22 days ⇒ one FTE covers it.")
    print("  Fully loaded centre agent ₹40–60k/month (stated assumption).")
    print("  Per extra approved at 74% pass: ~₹300–450. Replace with Ops roster if they have one.")

    for name, fname in [
        ("DELIVERABLE 1 — MEMO", "MEMO.md"),
        ("DELIVERABLE 3 — README", "README.md"),
    ]:
        hr(name)
        print((DATA_DIR / fname).read_text().rstrip())
        print()
    hr("DELIVERABLE 2 — DECK")
    print("  Rendered slides: deck/slides.html")
    print("  PDF:             deck/Project_R_deck.pdf")
    print("  Speaker notes:   DECK.md (do not submit DECK.md as the deck)")
    print("=" * 100)
    print("Step 9 complete.")
    print("=" * 100)


if __name__ == "__main__":
    main()
