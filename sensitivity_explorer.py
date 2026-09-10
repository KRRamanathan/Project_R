"""Live sensitivity. Same functions as the pipeline. Two tabs: onboarding + airport."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from metrics import (
    C1A_CENTRAL_SHOWUP,
    NET_GAP_VS_REST_SUB,
    NET_GAP_VS_WORST_CORE,
    NET_REST_SUBURBAN,
    NET_WORST_CITY_CORE,
    NET_WORST_SUBURBAN,
    airport_hourly_snapshot,
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
    return headlines(), ara_economics(), airport_hourly_snapshot()


h, eco, hourly = _base()
derived = eco["payout_per_eligible_leg"]
elig_mo = eco["elig_per_month"]
fare_30 = eco["fare_30pct"]

onb, apt = st.tabs(["Onboarding (C1a / C1b)", "Airport (hourly + ARA)"])

with onb:
    show = st.slider(
        "C1a 10-day show-up rate",
        0,
        100,
        int(C1A_CENTRAL_SHOWUP * 100),
        1,
        format="%d%%",
        key="c1a_show",
    )
    c1a = c1a_monthly(show / 100.0)
    c1b = c1b_monthly(2)
    st.metric("C1a additional approved / month", f"{c1a:,.1f}")
    st.metric("Onboarding (C1a + C1b att-2, disjoint)", f"{c1a + c1b:,.1f} / month")
    st.write(
        f"Locked (not on sliders): mature∩events **{h['mature_has_events_n']:,}**, "
        f"RC capture-only **{h['rc_capture_only_n']:,}**, "
        f"Insurance capture-only **{h['insurance_capture_only_n']:,}**, "
        f"C1b @ att-2 **{c1b:,.1f}**/month."
    )
    st.warning(
        "Show-up is unobserved. Field-vs-app 128–256/month is not in this explorer "
        "and is not banked."
    )

with apt:
    st.subheader("Marketplace — airport_hourly.csv (not sampled)")
    c1, c2, c3 = st.columns(3)
    c1.metric("Airport unfulfilled", f"{100 * hourly['airport_unf_share']:.0f}%")
    c2.metric("Elsewhere unfulfilled", f"{100 * hourly['other_unf_share']:.0f}%")
    c3.metric("Of airport unfulfilled in 21:00–03:59", f"{100 * hourly['night_share_of_airport_unf']:.0f}%")
    d1, d2, d3 = st.columns(3)
    d1.metric("Mean captains online, nights", f"{hourly['mean_captains_worst']:.0f}")
    d2.metric("Mean captains online, rest of day", f"{hourly['mean_captains_rest']:.0f}")
    d3.metric("Night unfulfilled / month", f"{hourly['unf_worst_per_month']:,.0f}")
    st.caption(
        f"{hourly['n_airport_hours']:,} airport zone-hours. "
        "Do not multiply these counts by sampled ARA legs — no join key."
    )

    st.subheader("After the trip — sampled airport_trips.csv")
    st.write(
        f"Net ₹/completed cycle: worst×suburban **₹{NET_WORST_SUBURBAN}** vs "
        f"rest×suburban **₹{NET_REST_SUBURBAN}** (gap ₹{NET_GAP_VS_REST_SUB:.1f}) vs "
        f"worst×city-core **₹{NET_WORST_CITY_CORE}** (geography, not ARA). "
        f"Eligible share of completed worst-suburban: **{100 * eco['eligible_share']:.2f}%** "
        f"→ derived payout ₹{NET_GAP_VS_REST_SUB:.1f} / {eco['eligible_share']:.4f} = "
        f"**₹{derived:.2f}**/leg."
    )

    payout_pct = st.slider(
        "ARA payout as % of derived ₹35.4 / eligible leg",
        50,
        150,
        100,
        5,
        format="%d%%",
        key="ara_pct",
    )
    ara = ara_monthly_cost(payout_pct / 100.0)
    pay = derived * (payout_pct / 100.0)
    e1, e2, e3 = st.columns(3)
    e1.metric("₹ / eligible leg", f"₹{pay:.1f}")
    e2.metric("ARA sample cost / month", f"₹{ara:,.0f}")
    e3.metric("Eligible sample legs / month", f"{elig_mo:,.1f}")

    rows = []
    for lab, frac in [("80% of derived", 0.80), ("100% gap-close", 1.00), ("120% buffer", 1.20)]:
        rows.append(
            {
                "tier": lab,
                "₹/eligible leg": round(derived * frac, 1),
                "sample ₹/month": round(elig_mo * derived * frac),
            }
        )
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
    st.write(
        f"30% of local eligible fare would be **₹{fare_30:.1f}/leg** — overpays vs "
        f"₹{derived:.1f}. City-core gap ₹{NET_GAP_VS_WORST_CORE:.1f} is geography, not ARA's job."
    )
    st.warning(
        "Mix does not shift overnight (χ² p=0.12). New hires inherit both penalties. "
        "Do not hire the airport catchment instead of ARA. Sample ₹/month is not a city P&L. "
        "Headcount only if a 4-week payout run-rate is not falling and nights stay unfilled."
    )
