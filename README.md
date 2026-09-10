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
Rebuild the clickable page: `python3 notebook_app.py` → `dashboard.html`

Open without Jupyter:

https://raw.githack.com/KRRamanathan/Project_R/main/dashboard.html

| File | Role |
|---|---|
| `Project_R.ipynb` | Run-all → yellow dashboard |
| `dashboard.html` | Same page, static (raw.githack) |
| `01`–`08_*.py` | Same working as scripts |
| `metrics.py` | Shared maths |
| `MEMO.docx` | 2-page memo |
| `DECK.pptx` | 6-slide deck |
| `CANDIDATE_BRIEF.md` | The assignment |

## Answers (short)

| Brief | Answer |
|---|---|
| A1 | Mature ∩ `doc_events`, n=21,024. Cut = max `in_progress` age (15.6 days). |
| A2 | C1b Insurance UX **~50/mo (ship now)**. C1a RC grace ~134/mo **only if Legal**; else ~36. Do not add field 128–256. |
| A3 | CAMP_WA_002 click lift **0 pp**. Do not scale 5×. |
| A4 | (1) C1b this week (2) Legal on C1a (3) ARA ₹35.4/leg — do not hire (4) stop CAMP 5× |
| B1–B3 | ~40% unfulfilled, 84% in 21:00–03:59. After the trip mix does not shift (p=0.12). **No catchment hiring.** |

Funnel uses `verification_pass` in `doc_events`. Show-up for C1a is assumed (60%). `airport_trips.csv` is sampled.
