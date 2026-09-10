# Memo to the Head of Supply
**Captain onboarding leak and overnight airport supply**
10 September 2026 · Extract 30 June 2026, 23:59 IST

## The number

The single biggest verified finding is a volume, not a percentage: **two capture fixes on RC and Insurance would add about 180 approved captains a month (179.5–185.6), at medium confidence.** The two groups do not overlap, so that range adds two products, not the same people twice.

**1,637** captains uploaded a Registration Certificate, never passed, and failed only because the photo was blurred, OCR was weak, or details were not legible — not because the document was expired, duplicated, or the wrong type. **411** others are in the same situation at Insurance. RC is a vehicle-identity check with no passenger-liability exposure; we can provisionally let those captains proceed and require an in-person RC check within **10 days**. Insurance is the liability document. It must still clear before a ride. That fix is better guided capture at upload, not a deferral.

How 180 is built. The RC group is about 300 captains a month. Additional approvals = flow × show-up in the 10-day window × in-person pass. Show-up is not in the extract (sensitivity 40–80%). Pass is grounded on what we already see: **74.12%** on a third RC attempt and **78.41%** when field teams assist RC — not an assumed 85–90%. Central cell (60% show-up × 74%): **133.5 a month**. Insurance uses its own retry pattern (67.36% → 73.82% → 76.36%) and the 90.6% chance a fully cleared captain is approved: **46.0–52.1 a month**. Combined: **179.5–185.6**. Confidence is medium because the stuck cohorts are observed; show-up and “better camera UX matches retry rates” are not experiments. Do not add the field-vs-app gap (128–256/month) on top: **726** of the RC group are the same self-serve captains that gap already counts, and field teams also recruit a different pool.

**CAMP_WA_002 is cost avoidance, not a win.** The growth ask is to scale it 5× as an onboarding completion lever. Among captains who received the message, clickers completed at **0 percentage points** above non-clickers (best estimate −1.5pp; interval about −3.6 to +0.6). About 89% of recipients had already cleared RC, so we did hit a live part of the funnel and still saw no lift. The large gap between “got the campaign” and “never got it” is targeting — we message people who already cleared RC — not an effect of the WhatsApp. Do not fund 5×. Redirect to a send vs no-send test; it costs almost nothing and can start this week.

## Airport: not a hiring problem

Overnight airport failure is not “hire captains who live nearby.” About **40%** of airport requests go unfilled vs low-single-digits elsewhere, and **84%** of that pain is 21:00–03:59, when roughly **13** captains are online vs **37** by day. After the trip, two penalties compound and they are independent: suburban drops are a longer backhaul at every hour, **and** return fares within 20 minutes collapse overnight in every drop type. The suburban vs city-core mix does **not** change overnight. New hires would face the same two penalties as incumbents. **No blanket hiring. Airport Return Assurance first. Headcount only if a 4-week ARA pilot shows the payout run-rate is not falling.**

ARA pays only when a completed suburban night trip does **not** get a return within 20 minutes (**89.31%** of those trips; **2,422.5** eligible legs/month in the sample). The **₹31.6** gap (worst-suburban net **₹24.9** vs rest-suburban **₹56.5**) averages *all* completed worst-suburban trips, including the **10.69%** that already got a return and need no payout. Required payout per eligible leg is **₹31.6 ÷ 0.8931 ≈ ₹35.4**. At 80 / 100 / 120% of that derived value: **₹28.3 / ₹35.4 / ₹42.5** per leg, about **₹69k–103k a month** on sample volume — not 30/50/70% of fare (₹254k–593k), which overpays relative to rest-of-day suburban economics. Target rest-suburban parity, **not** city-core (that gap is geography). Trip rupees are sampled; **₹69k–103k** is a design price and a sample-implied run-rate, not a city P&L line.

**Ranking basis:** items 1–2 are ordered by monthly impact (onboarding, then airport). Item 3 is the smallest number and is flagged as the **fastest to action** — zero cost, no sign-off, actionable immediately — if sequencing by speed is the more useful lens this week.

**1. Onboarding — two sub-actions of one recommendation.** **C1a:** 10-day in-person RC window for the 1,637. **C1b:** Insurance capture UX for the 411, no deferral. **Impact:** 179.5–185.6 additional approved captains/month. **Risk:** C1a needs legal / trust-and-safety sign-off on deferral; C1b has none. **Metric:** monthly approved captains, split by those two cohorts.

**2. Airport Return Assurance at the derived payout (~₹35.4 / eligible leg, ~₹69k–103k/month sample).** Pair with rematching. **Risk:** sampled trips, not a city budget. We are buying rest-suburban parity, not city-core economics. **Metric:** night suburban return-within-20-minutes, cancel rate, and the payout run-rate. A **falling** run-rate over four weeks is the proof it is working. If it does not fall, do not hire; redesign matching. If it falls and night unfilled stays high, *then* consider catchment hiring.

**3. Stop the CAMP_WA_002 5× ask; run the send/no-send test already designed.** RC-cleared app/paid captains, excluding other campaigns. Endpoints: Aadhaar pass and approved. **Impact:** spend not wasted on a 0pp lever, plus an answer in 4–6 weeks. **Cost:** near zero — a redirection. **Metric:** those endpoints at test close. **Fastest of the three to action.**

### What I assumed, and what would change my answer

- **~15.6-day cutoff.** Newer signups are unfinished, not failed. If they later fail in the same capture pattern, 180 is a floor. If they mostly finish on their own, it is a slight overstatement.
- **Document events, not the approvals file, decide which docs passed.** They disagree only for unfinished captains. If production reporting must follow the approvals file, rebuild the funnel before changing a target.
- **Field vs app is not banked.** Field looks better; field also recruits in person. What would change this: a randomised assist test on ordinary app/paid signups. Until then, 128–256/month is a ceiling, not a forecast.
- **ARA target is rest-suburban parity, not city-core.** Paying for city-core economics would pay for distance we cannot remove. What would change this: night suburban trips becoming as short as city-core. We do not see that.
- **Eligible-share adjustment (₹31.6 ÷ 0.8931 ≈ ₹35.4).** The ₹31.6 gap includes trips that already got a return. If night suburban returns rise, re-derive; do not freeze ₹35.4.

### Unresolved (not omitted)

**No cost-per-acquisition or spend field** — I cannot cost field vs paid as media ROI. **`airport_trips.csv` is sampled** — rates are reliable; raw counts and ₹/month are illustrative. **`signup_zone_id` does not join to airport zones** — I cannot size how many existing captains already live in the airport catchment.
