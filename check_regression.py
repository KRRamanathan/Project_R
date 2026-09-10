#!/usr/bin/env python3
"""Assert headline numbers against locked values. Fail the pipeline if they move."""

from __future__ import annotations

import sys

from metrics import headlines

# Locked from the mature ∩ has-doc_events extract (2026-06-30 23:59 IST).
EXPECTED = {
    "mature_has_events_n": (21024, 0),       # exact
    "rc_capture_only_n": (1637, 0),
    "insurance_capture_only_n": (411, 0),
    "c1a_central_per_month": (133.5, 0.15),  # 60% show-up × RC att-3
    "ara_payout_per_eligible_leg": (35.4, 0.15),  # 31.6 / eligible share
}


def main() -> int:
    got = headlines()
    failed = []
    print("REGRESSION — headline lock")
    for key, (want, tol) in EXPECTED.items():
        val = got[key]
        ok = abs(val - want) <= tol
        mark = "OK" if ok else "FAIL"
        print(f"  [{mark}] {key}: got {val}  expected {want} ± {tol}")
        if not ok:
            failed.append(key)
    if failed:
        print(f"\nFAILED: {', '.join(failed)}", file=sys.stderr)
        return 1
    print("All headline assertions passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
