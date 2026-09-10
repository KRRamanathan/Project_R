# Memo to the Head of Supply
**Onboarding leak and overnight airport** · 10 Sep 2026 · extract 30 Jun 2026, 23:59 IST

## Page 1 — What to do this week

**About 180 more approved captains a month, medium confidence — roughly 134 from an RC grace window and 50 from Insurance upload UX.** The two groups do not overlap. The exact 179.5–185.6 range is a sensitivity table, not a forecast to three digits. Show-up for in-person RC is not in the data, and if Legal will not let captains proceed with RC deferred, the RC piece is an upper bound.

These approvals are not hollow. Among mature approved captains, **98.7% take a first trip** (3,895 / 3,946). Getting them through documents is the bottleneck that matters.

**Stop scaling CAMP_WA_002.** Clickers complete at 0pp vs non-clickers (about −1.5pp; interval −3.6 to +0.6). Most recipients had already cleared RC. The 29% vs 11% “got the campaign” gap is targeting, not lift. Do not fund 5×. Run send vs no-send instead — zero cost, this week.

**Ranked by monthly impact.** Item 3 is the smallest number and the **fastest yes** (no sign-off).

| # | Do this | Impact | Cost / risk | Watch |
|---|---|---|---|---|
| **1** | **C1a** 10-day in-person RC for 1,637 capture-only fails, plus **C1b** Insurance camera UX for 411 (must still clear before a ride) | ~180 approved/month (~134 + ~50) | C1a: Legal/T&S on deferral, plus **~1 centre FTE (~₹40–60k/month, ~180 visits)** — assumed agent load, not a field in the file. C1b: no deferral, engineering only | Approved captains split by the two cohorts |
| **2** | **Airport Return Assurance** at **₹35.4 per unpaid night-suburban leg** (~₹69–103k/month on the sample) | Restores rest-of-day suburban economics; does not hire | Sampled trips ≠ city P&L. Target rest-suburban, not city-core | Night suburban return-in-20m, cancels, **falling payout run-rate** over 4 weeks |
| **3** | Kill the 5× WhatsApp paper; RCT send vs no-send among RC-cleared app/paid captains, no other campaign | Cost avoided + answer in 4–6 weeks | Near zero | Aadhaar pass and approved |

**Airport in one line:** do not hire the catchment. Nights fail because suburban backhaul and overnight return-collapse **compound**, and mix does not shift after dark. New captains inherit both penalties. ARA first; headcount only if a 4-week pilot’s payout run-rate is **not** falling and unfilled demand remains.

---

## Page 2 — Why, and what would change my mind

**RC vs Insurance.** 1,637 captains failed RC only on blur / weak OCR / illegible text. RC is vehicle identity — no passenger liability — so a 10-day in-person check is a scoped deferral. 411 failed Insurance the same way; Insurance is the liability document and **cannot** defer. Most Insurance *volume* never uploaded after Fitness; C1b does not claim that pile.

**How ~134 and ~50 are built.** RC stock is ~300/month. Additional = flow × 10-day show-up × pass. Pass is grounded: 74% on a third RC attempt, 78% when field assists RC. Central cell: 60% show-up × 74% = **~134/month**. Insurance uses its own 67% → 74% → 76% retry pattern × 91% approved-if-cleared = **~46–52/month**. **Do not add 128–256/month** from “make app signups convert like field”: 726 of the RC group are already in that gap, and field teams recruit a different pool.

**If remaining documents still bind.** Historical P(approved \| passed RC) is 27% (3,946 / 14,453). If Legal only defers RC *inside* the rest of the funnel, C1a shrinks toward ~36 fully-approved/month until Aadhaar→Insurance is also fixed. That is why the Legal ask is deferral-as-activation, not a photo waiver. C1b is already at Insurance; that haircut does not apply.

**ARA payout is derived, not a % of fare.** Eligible = suburban × 21:00–03:59 × completed × no return in 20 min (89.31% of those trips; 2,422.5 sample legs/month). The ₹31.6 gap (₹24.9 vs ₹56.5) averages *all* completed worst-suburban trips, including the 10.69% that already got a return. Required ₹/eligible leg = **31.6 / 0.8931 ≈ 35.4**. Band 80/100/120% of that: ₹28.3 / ₹35.4 / ₹42.5 → **~₹69k–103k/month** sample. 30% of the ₹350 fare (₹105) would overpay. City-core (₹104.7 net) is geography, not this product.

### What I assumed, and what would change my answer

- **~15.6-day cutoff.** Newer signups are unfinished, not failed. Later capture-fails → 180 is a floor; they finish alone → slight overstatement.
- **Document events decide which docs passed**, not the approvals file (they disagree only while unfinished).
- **Field vs app is not banked** until a randomised assist test on ordinary app/paid signups.
- **ARA target is rest-suburban, not city-core.** Night suburban trips would have to get as short as city-core to change that. They don’t.
- **₹31.6 / 0.8931.** If night returns rise, re-derive; do not freeze ₹35.4.
- **C1a ops ₹40–60k/month** assumes one FTE at a typical centre-agent load (~12–15 checks/day). A wage or roster from Ops would replace this.

### Unresolved (not omitted)

No CAC/spend field — cannot price field vs paid as media ROI. `airport_trips.csv` is sampled — rates hold; ₹/month is not a city budget. `signup_zone_id` does not join airport zones — cannot size captains who already live in the catchment.
