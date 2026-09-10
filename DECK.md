# Deck — 6 slides (10 minutes, expect two interruptions)

Audience: Head of Supply. One number per slide. No appendix maths on the slides; derivation lives in the working.

---

## Slide 1 — Headline: ~180 more approved captains a month

**Title:** Two capture fixes recover **179.5–185.6 additional approved captains per month** (medium confidence).

**Waterfall (mature captains who started documents, n = 21,024 → 3,946 approved, 18.8%):**

| Stage | Lost here | Recoverable now |
|---|---:|---|
| Driving licence | 1,166 | Not this rec (eligibility + never-start mix) |
| **RC** | **5,405** | **1,637** capture-only fails → C1a (central **133.5**/month) |
| Aadhaar | 1,540 | Not sized (not a capture-only product) |
| Permit / Fitness | 2,616 / 2,653 | Not sized |
| **Insurance** | **3,289** | **411** capture-only fails → C1b (**46–52**/month); most of the 3,289 never uploaded — different problem |
| Rejected after clearing | 409 | Eligibility gate, not UX |

**Spoken line:** “The 180 is not ‘if we fixed all of RC.’ It is the capture-only slice, converted to a monthly flow, with a 10-day show-up sensitivity. Insurance is a smaller, separate product. They do not overlap.”

**Footer:** C1a ∩ C1b = 0 captains. Do not add the 128–256 field-replication range on this slide.

---

## Slide 2 — Root cause: photos, not eligibility

**Title:** RC and Insurance are failing as **pictures**, then later attempts pass more often.

**RC uploaded but never passed:** among captains with a fail reason, **54%** are *only* blur / weak OCR / not legible (1,637 people). Eligibility codes (expired, duplicate, name mismatch, wrong type) are a different pile — do not mix them into a “defer RC” product.

**Insurance uploaded but never passed:** **411** people, same capture-only definition. Most Insurance *volume* is never-uploaded after Fitness (a continuation problem). C1b does not claim that pile.

**Retry pattern (pass rate by attempt, among people who still have a verification outcome):**

| | Attempt 1 | Attempt 2 | Attempt 3 |
|---|---:|---:|---:|
| RC | 65.3% | 68.4% | **74.1%** |
| Insurance | **67.4%** | **73.8%** | **76.4%** |

Later attempts go **up**, not down. That is what a capture/UX problem looks like. If the remainder were “harder documents,” later attempts would go down.

**Spoken line:** “We are not asking Trust & Safety to waive expired documents. We are asking Product for a guided camera, and Legal for a 10-day RC grace — only for the 1,637.”

---

## Slide 3 — The fix: C1a + C1b, and why RC is special

**Title:** One recommendation, two sub-actions. DL and Insurance still gate. RC does not have to.

**C1a — RC provisional activation**
- Who: 1,637 capture-only RC fails (~300/month).
- What: let them continue / provisionally activate; **in-person RC within 10 days**.
- Why RC can defer: vehicle identity, **no pre-ride passenger liability**.
- Sizing: 40/60/80% show-up × pass **74.1–78.4%** (third-attempt floor, field-assisted RC ceiling). Central: **133.5/month**.
- **Needs legal / T&S sign-off.**

**C1b — Insurance capture UX**
- Who: 411 capture-only Insurance fails (~75/month).
- What: blur/OCR feedback at upload. **Document must still clear before the first ride.**
- Why Insurance cannot defer: it *is* the liability document.
- Sizing: Insurance’s own 67.4 → 73.8 → 76.4% pattern × 90.6% approved-if-cleared: **46.0–52.1/month**.
- **No deferral sign-off.**

**Still gated before a ride:** driving licence (always), Insurance (always), remaining docs under current policy. RC is the scoped exception.

**Metric:** monthly approved captains, split by these two cohorts.

---

## Slide 4 — Airport: nights + compounding economics, not “hire near the airport”

**Title:** Overnight airport is a **suburban backhaul + night return-collapse** problem. Derived ARA cost **~₹69k–103k/month** (sample).

**When (marketplace file):** airport unfulfilled **40%** vs ~3% elsewhere; **84%** of airport unfulfilled is 21:00–03:59; ~13 captains online vs ~37 by day. Surge is already high. This is a **non-price constraint** (captains are not sitting the airport), not “raise surge.”

**After the trip (sampled trips — rates, not a census):**
- Suburban cancel **24%** vs city-core **12%**.
- Completed return-in-20-min, overnight: suburban **10.7%** vs city-core **47%**.
- Mix of suburban vs city-core **does not change overnight**. Two **independent** penalties, not a mix-shift.
- Net ₹ per cycle: worst×suburban **₹24.9** vs rest×suburban **₹56.5** vs worst×city-core **₹104.7**.

**ARA payout, derived (not 30/50/70% of fare):**
- Eligible = suburban × 21:00–03:59 × completed × no return in 20 min (**89.31%** of completed worst-suburban trips).
- Population gap ₹31.6 is averaged across *all* those trips, including the 10.69% that already got a return.
- **₹31.6 ÷ 0.8931 ≈ ₹35.4 per eligible leg.**
- 80 / 100 / 120% of derived: **₹28.3 / ₹35.4 / ₹42.5** → **~₹69k / ₹86k / ₹103k a month** on 2,422.5 sample-eligible legs.
- Target: **rest-suburban parity**, not city-core (that would pay for geography).

**Hiring answer on this slide:** new captains inherit both penalties. **No blanket hiring.**

---

## Slide 5 — What does not work (and how easy it is to be fooled)

**Title:** A WhatsApp campaign with a 0pp lift, and a field-vs-app gap we must not bank.

**CAMP_WA_002 — naive vs real**

| Contrast | Approved | What it is |
|---|---|---|
| Got the campaign vs never got it | ~29% vs ~11% | **Targeting.** Recipients are chosen after they already cleared RC. |
| Clicked vs did not click, among delivered | 28.3% vs 29.8% (**−1.5pp**) | **The honest contrast.** Interval −3.6 to +0.6pp. |

**Deck number with a name on it: 0 pp completion lift. Do not scale 5×.** About 30% of recipients also got another campaign; the test we *would* fund is send vs no-send among RC-cleared self-serve captains, exclusive of other campaigns.

**Field onboarding vs app/paid — unproven ceiling, not a win**
- Mechanical gap if app/paid converted like field: **128–256 approved/month**.
- Field teams **recruit in person**. We cannot see selection vs process.
- **726** of the C1a RC-capture captains are the same self-serve people inside that gap. **Do not add 180 to 128–256.**
- Correct move: randomised assisted onboarding on ordinary app/paid signups (~900 per arm to detect a 5pp approval lift).

---

## Slide 6 — Recommendations, costs, decision points

**Title:** Ranked by monthly impact. Campaign is the fastest yes.

*Ranking basis (say it): “I ranked 1–2 by monthly impact. Item 3 is the smallest number and the fastest to execute — zero cost, no sign-off, this week.”*

| # | What | Impact | Cost / risk | Decision point |
|---|---|---|---|---|
| **1** | **C1a** 10-day RC grace + **C1b** Insurance upload UX | **180/month** approved (179.5–185.6) | C1a: legal/T&S. C1b: none | Split metric by cohort. Do not wait on the field-replication pilot to ship C1b. |
| **2** | **ARA at ~₹35.4/eligible leg** | Night suburban economics → rest-suburban; sample run-rate **₹69k–103k/month** | Sampled trips ≠ city P&L. Do not target city-core parity | **4-week pilot.** Success = return-in-20m up, cancels down, **payout run-rate falling**. Hire catchment **only if** unfulfilled stays high after the run-rate falls. |
| **3** | **Stop 5× CAMP_WA_002**; send/no-send RCT | Cost avoided + answer in 4–6 weeks | Near zero | Primary: Aadhaar pass, approved. ITT, not clicks. **Actionable immediately.** |

**Do not spend next:** 5× WhatsApp; blanket airport hiring; treating 128–256 as a committed supply target.

**Ask of the room:** (1) legal scoping on RC deferral this week; (2) ship Insurance capture UX without waiting; (3) kill the 5× paper and stand up the RCT; (4) four-week ARA at the derived ₹35.4, not at 30% of fare.
