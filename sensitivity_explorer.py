"""Live sensitivity on the two assumed numbers. Same functions as the pipeline."""

from __future__ import annotations

import streamlit as st

from metrics import (
    C1A_CENTRAL_SHOWUP,
    ara_economics,
    ara_monthly_cost,
    c1a_monthly,
    c1b_monthly,
    headlines,
)

st.set_page_config(page_title="Project_R sensitivity", layout="centered")
st.title("Project_R — assumption explorer")
st.caption("Uses metrics.py (same functions as run_all.sh / check_regression.py). Not a forecast.")


@st.cache_data(show_spinner="Loading CSVs…")
def _base():
    h = headlines()
    eco = ara_economics()
    return h, eco


h, eco = _base()
derived = eco["payout_per_eligible_leg"]
elig_mo = eco["elig_per_month"]

show = st.slider("C1a 10-day show-up rate", 0, 100, int(C1A_CENTRAL_SHOWUP * 100), 1, format="%d%%")
payout_pct = st.slider("ARA payout as % of derived ₹35.4 / eligible leg", 50, 150, 100, 5, format="%d%%")

c1a = c1a_monthly(show / 100.0)
c1b = c1b_monthly(2)
ara = ara_monthly_cost(payout_pct / 100.0)

st.metric("C1a additional approved / month", f"{c1a:,.1f}")
st.metric("ARA sample cost / month", f"₹{ara:,.0f}")
st.metric("Onboarding (C1a + C1b att-2, disjoint)", f"{c1a + c1b:,.1f} / month")

st.write(
    f"Locked (not on sliders): mature∩events **{h['mature_has_events_n']:,}**, "
    f"RC capture-only **{h['rc_capture_only_n']:,}**, "
    f"Insurance capture-only **{h['insurance_capture_only_n']:,}**, "
    f"C1b @ att-2 **{c1b:,.1f}**/month, "
    f"derived payout **₹{derived:.2f}**/leg, "
    f"**{elig_mo:,.1f}** eligible sample legs/month."
)
st.warning(
    "Show-up is unobserved. ARA ₹/month is sample-implied, not a city P&L. "
    "Field-vs-app 128–256/month is not in this explorer and is not banked."
)
