# Project_R

Rapido take-home: captain onboarding (A2O) and overnight airport supply.  
Extract clock: **2026-06-30 23:59 IST**.

**Submit:** `MEMO.docx` · `DECK.pptx` · this repo (working = `Project_R.ipynb`).

## Run (easiest)

```bash
python3 -m pip install -r requirements.txt
python3 -m jupyter notebook Project_R.ipynb
```

Then **Run all**. You get **one Rapido-yellow page** (KPI cards + two sliders), not eight stacked log cells. Same maths as `./run_all.sh`. Yellow cards move with the sliders; C1b, approval %, and airport stay locked.

Same working from the shell:

```bash
./run_all.sh
```

Rebuild the deck: `node generate_deck.js`  
Rebuild the Word memo: `python3 build_memo.py`

| File | Role |
|---|---|
| `Project_R.ipynb` | Run-all → yellow dashboard |
| `01`–`08_*.py` | Same working as scripts |
| `metrics.py` | Shared maths |
| `MEMO.docx` | 2-page memo |
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
