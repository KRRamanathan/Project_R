# Memo to the Head of Supply

**Onboarding leak and overnight airport** · Ramanathan K R · 10 Sep 2026 · extract 30 Jun 2026, 23:59 IST

**~180 more approved captains a month — two photo fixes, not five programmes.** Bank only two disjoint capture fixes: ~134/month from a 10-day in-person RC grace (C1a) and ~50 from Insurance upload UX (C1b). 98.7% of mature approved captains already take a first trip (3,895 / 3,946). Show-up for RC is unobserved; if Legal will not treat deferred RC as activation, C1a shrinks toward ~36/month. Campaign number: **0 pp**, not 5×.

![Split of ~180](figures/pie_c1.png)
![Airport unfulfilled by clock](figures/pie_airport_night.png)

## Page 1 — What to do this week

| # | Do this | Impact | Cost / risk | Watch |
|---|---|---|---|---|
| **1** | C1b Insurance camera this week (411). Then C1a 10-day RC grace after Legal (1,637). Other-doc camera is a free rider — not in 180. | ~180/mo (~50 + ~134) | C1b: engineering. C1a: Legal/T&S + ~1 FTE ₹40–60k assumed. | Approved by cohort |
| **2** | Airport Return Assurance at **₹35.4** / unpaid night-suburban leg. **Do not hire** the catchment. | Sample ~₹69–103k/mo | Sampled trips ≠ city P&L. Not city-core. | Return-in-20m, cancels, falling 4-wk run-rate |
| **3** | Kill CAMP_WA_002 5×. Send/no-send RCT on RC-cleared app/paid captains. | 0 pp lift + 4–6 week answer | Near zero | Aadhaar pass and approved |

**Why rec 2 is “do not hire.”** ~40% unfulfilled vs ~3% elsewhere. Suburban backhaul and overnight return-collapse compound. Mix does not shift after dark (χ² p=0.12). New hires inherit both penalties.

**Why rec 3 is a hard no on 5×.** Clicked vs not (delivered): −1.5pp (CI −3.6 to +0.6). The 29% vs 11% gap is targeting after RC. Never-upload is not another WhatsApp.

## Page 2 — Bound, leftover, ARA, assumptions

The deck shows the leaks. This page is the bound: what is C1a vs leftover, how ₹35.4 is derived, which piles I refuse to add to 180.

![RC capture slice](figures/pie_rc_capture.png)
![Insurance C1b slice](figures/pie_c1b.png)

![Volume lost by stage](figures/bar_volume_lost.png)

| Fix | Flow | Maths | Bank |
|---|---|---|---|
| C1a RC grace | ~300/mo capture-only | × 60% show-up × 74% pass | **~134/mo** |
| C1b Insurance UX | 411 capture-only | 67→76% × 91% approved-if-cleared | **~46–52/mo** |

40–80% show-up → ~89–188. If remaining docs bind, P(approved \| passed RC)=27% → **~36/month** (Legal ask).

**Not banked.** Other-doc camera after C1b — measure. Never-upload RC ~2,388 / Insurance ~2,530: assist RCT, not WhatsApp; overlaps 726 C1a. Paid never-starts 11.5% vs fos ~1% — no CAC, not sized. DL cannot defer. Aadhaar/Permit/Fitness mostly never-upload or eligibility. Rejected 409 is a gate.

**ARA.** Gap ₹31.6 (₹24.9 vs ₹56.5) ÷ 0.8931 eligible share ≈ **₹35.4**/leg. 80/100/120% → ~₹69–103k sample. 30% of fare (₹105) overpays.

**Assumptions that would change my answer.** 15.6-day cutoff; `doc_events` not `docs_cleared`; field gap not banked; ARA vs rest-suburban not city-core; re-derive ₹35.4 if night returns rise; C1a FTE assumed. No CAC. Trips file sampled. `signup_zone_id` does not join airport zones.
