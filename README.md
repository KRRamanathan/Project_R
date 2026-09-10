# Project_R

Rapido take-home: captain onboarding (A2O) and overnight airport supply.  
Extract clock: **2026-06-30 23:59 IST**.

**Submit:** `MEMO.md` · `DECK.pptx` · this repo.

## Run

```bash
python3 -m pip install -r requirements.txt
./run_all.sh
```

Rebuild the deck (optional): `node generate_deck.js`  
Chart PNGs for the memo: `python3 make_exec_charts.py`

| File | Role |
|---|---|
| `01`–`08_*.py` | Working, from the seven CSVs |
| `metrics.py` | Shared maths (also used by `check_regression.py`) |
| `MEMO.md` | 2-page memo |
| `DECK.pptx` | 6-slide deck (+ title) |
| `CANDIDATE_BRIEF.md` | The assignment |

## Answers (short)

| Brief | Answer |
|---|---|
| A1 | Mature ∩ `doc_events`, n=21,024. Cut = max `in_progress` age (15.6 days). |
| A2 | C1a RC grace ~134/mo + C1b Insurance UX ~50/mo. Bank **~180**. Do not add field 128–256. |
| A3 | CAMP_WA_002 click lift **0 pp**. Do not scale 5×. |
| A4 | (1) C1b then C1a (2) ARA ₹35.4/eligible night-suburban leg — do not hire (3) stop CAMP 5× |
| B1–B3 | ~40% unfulfilled at terminals, 84% in 21:00–03:59. Mix does not shift overnight. **No catchment hiring.** |

Funnel uses `verification_pass` in `doc_events`. Show-up for C1a is assumed (60%). `airport_trips.csv` is sampled.
