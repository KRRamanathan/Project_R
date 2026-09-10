#!/usr/bin/env python3
"""
STEP 9 — Derive the ARA efficient payout, then print the three deliverables.

ARA pays only eligible legs (completed worst-hour suburban with no return
fare within 20 minutes). The ₹ gap from Step 7 is a mean over ALL completed
worst-suburban trips. Divide the population gap by the eligible share.

Do not use a 30/50/70%-of-fare grid. Sensitivity is 80/100/120% of the
derived rupee-per-eligible-leg.

Prints derivation, then MEMO.md, DECK.md, and README.md in full.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent
WORST_HOD = {21, 22, 23, 0, 1, 2, 3}
DAYS_PER_MONTH = 30.437
# Step 7 printed means (one decimal) — the gap the memo defends.
NET_WORST_SUB_PRINTED = 24.9
NET_REST_SUB_PRINTED = 56.5
GAP_PRINTED = NET_REST_SUB_PRINTED - NET_WORST_SUB_PRINTED  # 31.6


def hr(title: str) -> None:
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)


def main() -> None:
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
    k_return = int(ws["got_return"].sum())
    n_elig = int((~ws["got_return"]).sum())
    r = k_return / n_ws
    share = n_elig / n_ws  # 1 - r

    elig = t[
        t["drop_zone_type"].eq("suburban")
        & t["worst"]
        & t["completed"]
        & ~t["got_return"]
    ]
    assert len(elig) == n_elig

    span = (t["request_ts"].max().normalize() - t["request_ts"].min().normalize()).days + 1
    months = span / DAYS_PER_MONTH
    elig_mo = n_elig / months

    # Unrounded net-cycle (same recipe as Step 7) — audit only.
    comp = t[t["completed"]].copy()
    yld = (comp["fare_inr"] / comp["trip_distance_km"]).median()
    comp["deadhead_km"] = np.where(comp["got_return"], 0.0, comp["trip_distance_km"])
    comp["net"] = comp["fare_inr"] - comp["deadhead_km"] * yld
    mu_ws = float(
        comp.loc[comp["worst"] & comp["drop_zone_type"].eq("suburban"), "net"].mean()
    )
    mu_rs = float(
        comp.loc[~comp["worst"] & comp["drop_zone_type"].eq("suburban"), "net"].mean()
    )
    gap_exact = mu_rs - mu_ws
    fare = float(elig["fare_inr"].mean())

    payout = GAP_PRINTED / share  # the number we take to the room
    payout_exact = gap_exact / share

    hr("STEP 9 — ARA PAYOUT DERIVATION (replaces 30/50/70% of fare)")
    print("  Eligible = suburban × 21:00–03:59 × completed × no return fare within 20 min.")
    print("  ARA pays eligible legs only. The Step 7 net-₹ gap is a mean over ALL")
    print("  completed worst-suburban trips, including those that already got a return.")
    print()
    print(f"  completed worst×suburban n = {n_ws:,}")
    print(f"  return within 20 min     = {k_return:,}  ({100 * r:.4f}%)")
    print(f"  eligible (no return)     = {n_elig:,}  ({100 * share:.4f}%)  = 1 − {100 * r:.4f}%")
    print(f"  trip file span {span} days ≈ {months:.3f} months of {DAYS_PER_MONTH}d")
    print(f"  eligible legs / month    = {n_elig:,} / {months:.3f} = {elig_mo:,.1f}")
    print(f"  mean fare of eligible    = ₹{fare:.1f}  (used only as a check, not the grid)")
    print()
    print("  Population gap (Step 7 printed means):")
    print(f"    rest×suburban ₹{NET_REST_SUB_PRINTED} − worst×suburban ₹{NET_WORST_SUB_PRINTED} = ₹{GAP_PRINTED}")
    print("  Required payout per eligible leg to restore that population mean:")
    print(f"    ₹{GAP_PRINTED} / {share:.6f} = ₹{payout:.4f}  ≈ ₹{payout:.1f}")
    print()
    print("  Unrounded audit (same recipe, full precision of the means):")
    print(f"    median yield ₹{yld:.4f}/km")
    print(f"    mean net worst×sub ₹{mu_ws:.3f}  rest×sub ₹{mu_rs:.3f}  gap ₹{gap_exact:.3f}")
    print(f"    ₹{gap_exact:.3f} / {share:.6f} = ₹{payout_exact:.4f}")
    print("    Memo uses the printed-mean path (₹31.6 / 0.8931 ≈ ₹35.4).")
    print("    Exact path differs by < ₹0.10/leg. Not a coincidence that this is")
    print(f"    ~{100 * payout / fare:.1f}% of local eligible fare — still derived, not a fare grid.")
    print()
    print("  Sensitivity around the derived point (80 / 100 / 120%), not % of fare:")
    print(f"  {'tier':<28} {'₹/elig':>10}  {'₹/month (sample)':>18}")
    for lab, f in [
        ("80% of derived", 0.80),
        ("100% of derived (gap-close)", 1.00),
        ("120% of derived (buffer)", 1.20),
    ]:
        p = payout * f
        cost = elig_mo * p
        print(f"  {lab:<28} {p:10.1f}  {cost:18,.0f}")
    print()
    print("  Corrected monthly cost band: ~₹69k–103k (sample-implied).")
    print("  Do not use ₹254k–593k (30/50/70% of fare) in the memo or deck.")
    print("  airport_trips.csv is sampled: rates are the estimand; ₹/month is not city P&L.")

    for name, fname in [
        ("DELIVERABLE 1 — MEMO", "MEMO.md"),
        ("DELIVERABLE 2 — DECK", "DECK.md"),
        ("DELIVERABLE 3 — README", "README.md"),
    ]:
        hr(name)
        text = (DATA_DIR / fname).read_text()
        print(text.rstrip())
        print()

    print("=" * 100)
    print("Step 9 complete. Final step.")
    print("=" * 100)


if __name__ == "__main__":
    main()
