# Project_R — working

Captain onboarding (A2O) and overnight airport supply.  
Extract clock: **2026-06-30 23:59 IST** (naive timestamps; we do not invent a timezone offset).

**Submit:** `MEMO.docx` (or `MEMO.md`), `DECK.pptx`, and this repo.

## Setup

- **Python:** 3.10 or newer (developed on 3.12).
- **Install:**

```bash
python3 -m pip install -r requirements.txt
```

`requirements.txt`: pandas, numpy, scipy, statsmodels, matplotlib, python-docx, python-pptx, streamlit.

Raw inputs (must be in the repo root): `captains.csv`, `doc_events.csv`, `approvals.csv`, `activation.csv`, `nudges.csv`, `airport_hourly.csv`, `airport_trips.csv`.

## Run order

From a clean clone, one command:

```bash
./run_all.sh
```

That runs `01_data_audit.py` → `09_deliverables.py` in order, tees every print to `0N_*_output.txt`, writes `MEMO.docx`, `DECK.pptx`, `figures/funnel_waterfall.png`, then **fails the build** if headline numbers moved.

Individual scripts (each re-derives from CSVs; none reads another script’s console):

| Script | What it produces |
|---|---|
| `01_data_audit.py` | Schema, joins, mature-relevant flags |
| `02_funnel.py` | Empirical 15.6-day cut; stage funnel |
| `03_dropoff.py` | Where volume is lost; attempt-level pass rates |
| `04_channel_leaks.py` | fos vs self-serve; C1 capture-only 1,637 / 411 |
| `05_campaign.py` | CAMP_WA_002 0pp lift; RCT sketch |
| `06_airport_hourly.py` | When/how much airport unfulfilled |
| `07_airport_trips.py` | Post-trip economics; two independent penalties |
| `08_intervention_sizing.py` | C1a/C1b/ARA sizing (derived ₹35.4) |
| `09_deliverables.py` | Waterfall, `MEMO.docx`, `DECK.pptx`, R2A |
| `check_regression.py` | Headline lock (called by `run_all.sh`) |

Shared maths live in `metrics.py` so Step 8, the regression check, and the Streamlit app cannot drift.

Optional: run `streamlit run sensitivity_explorer.py` to explore the two assumption-dependent numbers live.

## Data-quality decisions (carried through every step)

**~15.6-day censoring cutoff.** `in_progress` is unfinished, not failed. Cut = **max signup age among `in_progress` = 15.602778 days**. Mature = signup age **greater than** that. Funnel rates use mature ∩ has `doc_events` (**n = 21,024**). The 1,416 mature captains with zero document events are **never-attempted**, reported separately, never mixed into stage capture-failure stats.

**`doc_events` over `approvals.csv` for which documents passed.** Stage flags are `verification_pass` in `doc_events`. `docs_cleared` disagrees with n-unique passes for 451 captains, **all immature**. Mature mismatch = 0.

**Rejected is a distinct outcome.** 409 rejected captains all sit **after** required docs cleared — an eligibility gate, not a document-UX leak. Not folded into “dropped in docs.”

**Nudges.** 457 rows are `clicked=1` and `delivered=0` (impossible). Dropped from campaign lift. CAMP_WA_002 is sent after RC; recipient vs non-recipient is targeting, not an experiment.

**Activation.** One row per approved captain. Answers R2A (first trip), not the A2O funnel. 98.7% of mature approved have a first order.

**Airport files do not mix.** `airport_hourly.csv` = when terminals fail (marketplace state). `airport_trips.csv` = sampled post-pickup economics. `signup_zone_id` does not join airport `zone_id`.

**Rigor bar.** Point estimate, n, test, CI. n<100 directional. Multi-cut Bonferroni. Confound check before a univariate cut becomes a cause.

## Where each brief question is answered

| Brief | Question | Go here |
|---|---|---|
| **A1** | Build the signup→approved funnel | `02_funnel.py` / `02_funnel_output.txt` — empirical mature cut, stage rates vs signup, volume lost. Waterfall: `figures/funnel_waterfall.png`. |
| **A2** | Biggest fixable leak, sized /month | `03_dropoff.py` (failure mix, retry pattern) then `04_channel_leaks.py` (C1 = 1,637 RC + 411 Insurance capture-only) then `08_intervention_sizing.py` §1–2 (C1a ~134/month central, C1b ~46–52/month). |
| **A3** | CAMP_WA_002 5× claim | `05_campaign.py` / `05_campaign_output.txt` §4 — clicked vs not **0 pp**; naive recipient gap is targeting. Deck slide 5. |
| **A4** | Three ranked recommendations | `MEMO.docx` page 1 table; `DECK.pptx` slide 6; working in `08` + `09`. |
| **B1** | Airport demand–supply mismatch when/how much | `06_airport_hourly.py` — 40% unfulfilled, 84% in 21:00–03:59, ~13 vs ~37 captains. |
| **B2** | What happens after an airport trip | `07_airport_trips.py` — suburban + overnight penalties, mix does **not** shift (χ² p=0.12). |
| **B3** | Is targeted acquisition the right intervention? | **No.** `08` §6 + memo page 1: ARA at **₹35.4/eligible leg**, not hiring. Headcount only if a 4-week payout run-rate does not fall. |

## What I chose not to do, and why

- **No ML churn model.** Time budget, and the decision is a product fix plus a campaign stop, not a scoring layer.
- **No CAC-based channel ROI.** Spend/bid/CAC is not in the extract. Paid never-attempt is named, not priced.
- **No city-core-parity target for ARA.** City-core net is a different geography. The matching comparison is rest-of-day suburban (₹56.5 vs ₹24.9).
- **No blind 30/50/70%-of-fare ARA grid.** Population gap ₹31.6 ÷ eligible share 0.8931 ≈ **₹35.4** per unpaid leg. Sensitivity is 80/100/120% of that derived point.

## Known limitations

- **C1a show-up is unobserved** and assumed (central 60%; band 40–80%). If Legal will not treat RC as deferred activation, remaining-funnel conversion (~27% after RC) shrinks C1a toward ~36/month.
- **Field vs self-serve 128–256/month is an unproven ceiling**, not banked. fos recruits in person. It overlaps 726 C1a captains — do not add it to ~180.
- **`airport_trips.csv` is sampled**, not a census. Rates and the ₹35.4 derivation hold; ₹69k–103k/month is sample-implied, not a city P&L line.
- **C1a ops ₹40–60k/month** is a stated FTE assumption (12–15 checks/day), not a field in the file.
- **No join** from `signup_zone_id` to airport zones — cannot size existing catchment headcount.
