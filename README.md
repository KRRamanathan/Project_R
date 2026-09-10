# Project_R — working README

Captain onboarding (A2O) and airport supply take-home.  
**Extract clock:** 2026-06-30 23:59 IST (timestamps are naive; we do not invent a timezone offset).

## How to run

```bash
pip install -r requirements.txt

python 01_data_audit.py          # inventory, joins, mature-relevant flags
python 02_funnel.py              # mature cohort, stage funnel from doc_events
python 03_dropoff.py             # where volume is lost; attempt-level pass rates
python 04_channel_leaks.py       # fos vs self-serve; C1 capture-only cohorts
python 05_campaign.py            # CAMP_WA_002 — 0pp lift; RCT sketch
python 06_airport_hourly.py      # when/how much airport unfulfilled
python 07_airport_trips.py       # post-trip economics; two independent penalties
python 08_intervention_sizing.py # C1a/C1b/overlap; tests not banked
python 09_final_deliverables.py  # derived ARA payout + prints memo/deck/README
```

Each step prints to stdout and is saved as `0N_*_output.txt`. Steps are designed to **print and stop**; later steps re-derive cohorts from the CSVs rather than reading a previous output as source of truth.

**Deliverables:** `MEMO.md` (Head of Supply, ≤2 pages), `DECK.md` (6 slides), this README.

`activation.csv` is required for Step 1 (post-approval activity). It was missing from the original GitHub upload and is in this repo.

## Data-quality summary (standing rules)

**Censoring cutoff.** `in_progress` is not failure. Empirical mature cut = max signup age among `in_progress` (**15.602778 days**). Mature = signup age **greater than** that cut. Funnel rates are mature ∩ has `doc_events` (n = 21,024). The 1,416 mature captains with zero document events are a **never-attempted** group, reported separately, never mixed into stage capture-failure stats.

**`doc_events` over `approvals.csv` as source of truth for which documents passed.** Stage flags are `verification_pass` in `doc_events`. `docs_cleared` on the approvals file disagrees with n-unique passes for 451 captains, **all immature**. Mature mismatch count = 0. Rejected captains (409) all sit **after** required docs cleared — an eligibility gate, not a document-UX leak. **Rejected is a distinct outcome**, not “dropped in docs.”

**Nudges.** 457 rows are `clicked=1` and `delivered=0` (impossible). They are excluded from campaign lift. Do not treat “received a campaign” vs “did not” as an experiment; CAMP_WA_002 is sent after RC for almost everyone.

**Activation.** One row per approved captain. It answers post-approval activity, not the A2O funnel.

**Airport file separation.** `airport_hourly.csv` characterises **when** terminals fail (marketplace state). `airport_trips.csv` characterises **what happens after pickup** (sampled legs). Do not use trip counts as a city census. Do not join `signup_zone_id` to airport `zone_id` — they are not a key.

**Rigor bar used throughout.** Point estimate, n per group, a proper test, a confidence interval. n < 100 is directional. Multi-cut families are Bonferroni-flagged. A univariate cut is not a cause until a confound check says so.

## What I chose not to do, and why

**No ML churn / “who will finish onboarding” model.** The time budget and the n do not justify it, and the decision on the table is a product fix (camera UX / RC grace) plus a campaign stop, not a scoring layer. A model would also train through the same censoring cutoff we already handled with a cohort rule.

**No CAC-based channel ROI.** There is no spend, bid, or cost-per-acquisition field. Paid digital’s high never-attempt rate is a red flag I named and did not pretend to price.

**No city-core-parity target for Airport Return Assurance.** Worst-hour city-core net ₹/cycle is a different geography (shorter trips, higher return rates). Paying captains until suburban night looks like city-core would overpay for distance we cannot remove. The comparison that matches the product is **rest-of-day suburban** (₹56.5 vs ₹24.9).

**No blind 30/50/70%-of-fare grid for ARA.** That grid was arbitrary and, at 30% of the ₹350 local fare, already overshot the economic gap. The ₹31.6 gap is a **population average** across all completed worst-suburban trips; ARA only pays the **89.31%** that got no return within 20 minutes. Gap-closing payout = **₹31.6 / 0.8931 ≈ ₹35.4 per eligible leg**. Sensitivity is 80/100/120% of that derived point (~₹69k–103k/month on sample volume), not a percent-of-fare ladder.

**No banking the field-vs-app conversion gap.** fos_field looks better; fos_field also recruits in person. 128–256 additional approved/month is an unproven ceiling. It overlaps 726 captains with C1a. It is a randomised assist pilot, not a supply target.

**No vehicle-type / ERickshaw headline.** City-adjusted, ERickshaw vs Auto still differs, but pseudo-R² is 0.0065 — structural and not an ops lever.

## Scripts vs memo

If Step 8’s 30/50/70%-of-fare ARA table disagrees with the memo, **the memo is correct.** Step 9 re-derives the efficient payout and is the number to defend in the room.
