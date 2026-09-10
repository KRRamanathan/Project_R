# Project_R — what to submit

Captain onboarding (A2O) and airport supply. Extract **2026-06-30 23:59 IST**.

## Submit these three

1. **`MEMO.md`** (or a PDF export of it) — Head of Supply, 2 pages.
2. **`deck/Project_R_deck.pdf`** — 6 slides. Not `DECK.md` (those are speaker notes).
3. **This repo** — scripts 01–09, CSVs, `requirements.txt`.

Headline to say without notes: *about 180 more approved captains a month, medium confidence (~134 RC grace + ~50 Insurance UX); don’t scale the WhatsApp; don’t hire the airport — ARA at ₹35.4/leg first.*

## How to run

```bash
pip install -r requirements.txt
python 01_data_audit.py
python 02_funnel.py
python 03_dropoff.py
python 04_channel_leaks.py
python 05_campaign.py
python 06_airport_hourly.py
python 07_airport_trips.py
python 08_intervention_sizing.py   # ARA uses derived ₹35.4, not % of fare
python 09_final_deliverables.py    # R2A, ARA check, waterfall, reprints memo
python make_waterfall.py
google-chrome --headless --disable-gpu --no-pdf-header-footer \
  --print-to-pdf=deck/Project_R_deck.pdf file://$PWD/deck/slides.html
```

Each `0N_*.py` prints to stdout; copies live in `0N_*_output.txt`. Later steps re-derive from CSVs.

`activation.csv` is required (1:1 with approved). It was missing from the original GitHub upload.

## Data-quality summary

**Censoring.** `in_progress` is not failure. Mature = signup age **> 15.602778 days** (max in-progress age). Funnel: mature ∩ has `doc_events` (n = 21,024). Zero-event mature (1,416) = never-attempted, separate.

**`doc_events` over `approvals.csv` for which docs passed.** Mature mismatch = 0. Rejected (409) is after clearance — a gate, not UX.

**Nudges.** Drop `clicked=1 & delivered=0` (457). CAMP_WA_002 is sent after RC; recipient vs non-recipient is targeting.

**Activation / R2A.** One row per approved captain. 98.7% of mature approved have a first trip (3,895/3,946).

**Airport files don’t mix.** Hourly = when terminals fail. Trips = sampled post-pickup economics. `signup_zone_id` does not join airport `zone_id`.

**Rigor.** Point estimate, n, test, CI. n<100 directional. Multi-cut Bonferroni. Confound check before a univariate cut becomes a cause.

## What I chose not to do

- No ML churn model — the decision is a product fix and a campaign stop.
- No CAC channel ROI — spend is not in the file. C1a ops cost is an **explicit FTE assumption** (₹40–60k), not fake media math.
- No city-core target for ARA — that pays for geography.
- No 30/50/70%-of-fare ARA grid — derived ₹31.6 / 0.8931 ≈ ₹35.4; 80/100/120% of that.
- No banking field vs app (128–256/month). Overlaps 726 C1a captains. Pilot, not a target.
- No vehicle-type headline (pseudo-R² 0.0065).
