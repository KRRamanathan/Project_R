#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
PYTHON="${PYTHON:-python3}"
"$PYTHON" -m pip install -q -r requirements.txt
for s in 01_data_audit.py 02_funnel.py 03_dropoff.py 04_channel_leaks.py \
         05_campaign.py 06_airport_hourly.py 07_airport_trips.py \
         08_intervention_sizing.py; do
  echo "======== $s ========"
  "$PYTHON" "$s"
done
"$PYTHON" build_memo.py
"$PYTHON" notebook_app.py
if command -v node >/dev/null 2>&1; then node generate_deck.js; fi
"$PYTHON" check_regression.py
echo "DONE. Memo: MEMO.docx  Deck: DECK.pptx  Dashboard: dashboard.html"
