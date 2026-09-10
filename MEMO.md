# Memo to the Head of Supply
**Onboarding leak and overnight airport** · 10 Sep 2026 · extract 30 Jun 2026, 23:59 IST

![Split of ~180 extra approved / month](figures/pie_c1.png)
![Airport unfulfilled volume by clock](figures/pie_airport_night.png)

## Page 1 — What to do this week

**About 180 more approved captains a month, medium confidence — roughly 134 from an RC grace window and 50 from Insurance upload UX.** The two groups do not overlap. The 179.5–185.6 range is a sensitivity table, not a three-decimal forecast. Show-up for in-person RC is unobserved. If Legal will not let captains proceed with RC deferred, the RC piece is an upper bound.

These approvals are not hollow. Among mature approved captains, **98.7% take a first trip** (3,895 / 3,946). Documents are the bottleneck, not first-order.

**Stop scaling CAMP_WA_002.** Clickers complete at 0pp vs non-clickers (about −1.5pp; interval −3.6 to +0.6). Most recipients had already cleared RC. The 29% vs 11% “got the campaign” gap is targeting, not lift. Do not fund 5×. That same null is why we do **not** harvest the large “never uploaded the next doc” pile with another WhatsApp.

**Ranked by monthly impact.** Item 3 is the smallest number and the **fastest yes** (no sign-off). Airport is rec 2 on purpose: the answer is **do not hire**, not a second onboarding slide.

| # | Do this | Impact | Cost / risk | Watch |
|---|---|---|---|---|
| **1** | **C1b** Insurance camera UX (411; must clear before a ride) **this week**, then **C1a** 10-day in-person RC (1,637) once Legal signs | ~180 approved/month (~50 + ~134). Same camera on DL/Aadhaar/Permit/Fitness is a **free rider after C1b — not added to 180** | C1a: Legal/T&S + **~1 FTE (~₹40–60k/month, ~180 visits)**, assumed. C1b: engineering only | Approved split by cohort |
| **2** | **Airport Return Assurance** at **₹35.4 per unpaid night-suburban leg** (~₹69–103k/month sample) | Restores rest-of-day suburban economics. **No catchment hiring** | Sampled trips ≠ city P&L. Target rest-suburban, not city-core | Night suburban return-in-20m, cancels, **falling payout run-rate** over 4 weeks |
| **3** | Kill the 5× WhatsApp; send vs no-send RCT among RC-cleared app/paid captains, no other campaign | Cost avoided + answer in 4–6 weeks | Near zero | Aadhaar pass and approved |

**Airport, said plainly:** unfilled demand is ~40% at terminals vs ~3% elsewhere; 84% of that pain is 21:00–03:59. After the trip, suburban backhaul and overnight return-collapse **compound**, and mix does **not** shift after dark. New hires inherit both penalties. ARA first; headcount only if a 4-week run-rate is **not** falling and nights stay unfilled.

---

## Page 2 — Why these two stages, what we left, what would change my mind

![RC capture-only slice](figures/pie_rc_capture.png)
![Insurance C1b slice](figures/pie_c1b.png)

![Where volume is lost](figures/bar_volume_lost.png)

**Why RC and Insurance, not “fix the whole funnel.”** RC loses 5,405 people — the largest stage. **1,637** failed *only* on blur / OCR / illegible; retry pass rates go **up** (65% → 74%). RC is vehicle identity, not passenger liability, so a 10-day in-person grace is scoped. Insurance loses 3,289, but **~2,530 never uploaded** after Fitness. C1b is only the **411** capture-only fails (same photo mechanism; **cannot** defer — liability). DL (1,166) is 100% uploaded-fail and **cannot** be deferred. Aadhaar / Permit / Fitness losses are real (1,540 / 2,616 / 2,653) but mostly **never-uploaded** or mixed with eligibility (expired, duplicate, name mismatch). A camera does not fix those. Rejected 409 already cleared docs — a gate.

**Leftover queue — possible, not banked.** (1) Reuse C1b’s capture UX on every upload screen including DL — cheap once C1b ships; capture-only n not sized except RC/Insurance; do not add it to 180. (2) Never-upload RC (~2,388) and Insurance (~2,530): looks like a nudge; CAMP_WA_002 was 0pp and only 13 post-Fitness nudges exist in 7,644 people. Fos abandonment after Fitness is 26% vs paid 43% — in-person help, not WhatsApp. That is the **assisted-onboarding RCT** (unproven ceiling 128–256/month; overlaps 726 C1a captains; do not add). (3) Paid never-starts docs at 11.5% vs fos ~1% — channel quality; no CAC so not sized.

**How ~134 and ~50 are built.** RC flow ~300/month × 60% show-up × 74% pass = **~134**. Insurance 67→76% × 91% approved-if-cleared = **~46–52**. If remaining docs still bind after RC, historical P(approved | passed RC) is 27% and C1a shrinks toward **~36/month** — that is the Legal ask (deferral-as-activation).

**ARA:** ₹31.6 gap (₹24.9 vs ₹56.5) is a mean across *all* completed worst-suburban trips. ARA pays only the 89.31% with no return in 20 min → **31.6 / 0.8931 ≈ ₹35.4**/leg. 80/100/120% → ~₹69–103k/month sample. 30% of fare (₹105) overpays. City-core ₹104.7 is geography.

### What I assumed, and what would change my answer

- **~15.6-day cutoff.** Later capture-fails → 180 is a floor; they finish alone → slight overstatement.
- **Document events**, not the approvals file, for which docs passed (disagree only while unfinished).
- **Field vs app not banked** until a randomised assist test on ordinary app/paid signups.
- **ARA = rest-suburban, not city-core.** Night suburban trips would have to get as short as city-core. They don’t.
- **₹31.6 / 0.8931.** If night returns rise, re-derive; do not freeze ₹35.4.
- **C1a ops ₹40–60k** assumes one FTE at 12–15 checks/day.

### Unresolved (not omitted)

No CAC — cannot price field vs paid. `airport_trips.csv` is sampled — rates hold; ₹/month is not a city budget. `signup_zone_id` does not join airport zones. Capture-only was not counted on Aadhaar/Permit/Fitness — reuse UX, then measure.
