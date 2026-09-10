#!/usr/bin/env bash
# Run the full Project_R pipeline from raw CSVs. No manual steps in between.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
export PYTHONUNBUFFERED=1
PYTHON="${PYTHON:-python3}"

echo "==> Python: $($PYTHON --version)"
echo "==> Installing dependencies"
"$PYTHON" -m pip install -q -r requirements.txt

run_step() {
  local script="$1"
  local out="$2"
  echo ""
  echo "======== $script → $out ========"
  "$PYTHON" "$script" | tee "$out"
}

run_step 01_data_audit.py           01_data_audit_output.txt
run_step 02_funnel.py               02_funnel_output.txt
run_step 03_dropoff.py              03_dropoff_output.txt
run_step 04_channel_leaks.py        04_channel_leaks_output.txt
run_step 05_campaign.py             05_campaign_output.txt
run_step 06_airport_hourly.py       06_airport_hourly_output.txt
run_step 07_airport_trips.py        07_airport_trips_output.txt
run_step 08_intervention_sizing.py  08_intervention_sizing_output.txt
run_step 09_deliverables.py         09_deliverables_output.txt

echo ""
echo "==> Optional Chrome PDF of HTML slides (15s timeout; DECK.pptx is the submit deck)"
if command -v google-chrome >/dev/null 2>&1 && command -v timeout >/dev/null 2>&1; then
  timeout 15 google-chrome --headless --disable-gpu --no-sandbox --disable-dev-shm-usage \
    --no-pdf-header-footer --allow-file-access-from-files \
    --virtual-time-budget=5000 \
    --print-to-pdf="$ROOT/deck/Project_R_deck.pdf" \
    "file://$ROOT/deck/slides.html" \
    >/dev/null 2>&1 && echo "    wrote deck/Project_R_deck.pdf" \
    || echo "    Chrome PDF skipped (timeout or error). DECK.pptx is the submit deck."
else
  echo "    skipped (no google-chrome/timeout); using DECK.pptx"
fi

echo ""
echo "==> Regression lock on headline numbers"
"$PYTHON" check_regression.py

echo ""
echo "DONE. Artifacts:"
echo "  printed logs:  01_…09_*_output.txt"
echo "  memo:          MEMO.md  MEMO.docx"
echo "  deck:          DECK.pptx  deck/slides.html  deck/Project_R_deck.pdf"
echo "  figures:       figures/funnel_waterfall.png"
echo "Optional: streamlit run sensitivity_explorer.py"
