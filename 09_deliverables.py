#!/usr/bin/env python3
"""STEP 9 — packet: waterfall, MEMO.docx, DECK.pptx, R2A/ARA print."""

from __future__ import annotations

import build_office
import make_waterfall
from metrics import ara_economics, c1a_monthly, headlines, wilson
import pandas as pd

from metrics import DATA_DIR, EXTRACTION_TS


def r2a() -> None:
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
    print("R2A  mature approved first trip: "
          f"{100 * p:.2f}% ({k:,}/{n:,}) W95% [{100 * lo:.2f},{100 * hi:.2f}]")


def main() -> None:
    print("=" * 80)
    print("STEP 9 — deliverables")
    print("=" * 80)
    make_waterfall.main()
    build_office.main()
    h = headlines()
    eco = ara_economics()
    print("\nHeadlines (from metrics.py — same functions as regression/Streamlit):")
    for k, v in h.items():
        print(f"  {k}: {v}")
    print(f"  C1a @ 60% show-up: {c1a_monthly(0.60):.2f}/month")
    print(f"  ARA ₹/eligible: {eco['payout_per_eligible_leg']:.2f}")
    r2a()
    print("\nWrote: figures/funnel_waterfall.png  figures/pie_*.png  MEMO.docx  DECK.pptx")
    print("Also: MEMO.md  deck/slides.html  deck/Project_R_deck.pdf (if Chrome printed it)")
    print("Step 9 complete.")


if __name__ == "__main__":
    main()
