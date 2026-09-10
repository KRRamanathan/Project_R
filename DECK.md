# Deck speaker notes (not the submit file)

**Submit `deck/Project_R_deck.pdf`** (6 landscape slides). HTML source: `deck/slides.html`. Chart: `figures/funnel_waterfall.png`.

Rebuild:

```bash
python make_waterfall.py
google-chrome --headless --disable-gpu --no-pdf-header-footer \
  --print-to-pdf=deck/Project_R_deck.pdf deck/slides.html
```

Open `deck/slides.html` from a local file if the chart path breaks in Chrome; generate the PDF from the repo root.

## 10-minute talk track

1. **180, medium confidence.** ~134 RC grace + ~50 Insurance UX. Waterfall: we are not claiming the whole RC bar. 98.7% of approved already take a first trip.
2. **Photos, not eligibility.** Retry rates go up. 1,637 / 411 capture-only.
3. **C1a vs C1b.** Legal on RC only. ~1 FTE for visits. If remaining docs still bind, C1a → ~36/month — that’s the Legal ask.
4. **Airport.** Two independent penalties. ₹35.4 derived. No hire.
5. **Trap slide.** Naive 29 vs 11 vs honest 0pp. Don’t add fos 128–256.
6. **Ask.** Ship C1b now; Legal on C1a; 4-week ARA; kill 5× this week.

If interrupted twice, keep slides 1, 5, and 6.
