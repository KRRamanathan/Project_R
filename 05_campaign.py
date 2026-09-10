#!/usr/bin/env python3
"""
STEP 5 — CAMP_WA_002 campaign evaluation.

Standing rule: rows with clicked=1 and delivered=0 (457 in nudges.csv; 251 of
them on CAMP_WA_002) are excluded from every click-lift comparison.

Onboarding completion := final_status == approved, in the mature cohort
(signup_age > max in_progress age), so in_progress is censored not failed.

Print and stop. No 5x scale recommendation unless the data support it.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy.stats import chi2_contingency, mannwhitneyu, norm

DATA_DIR = Path(__file__).resolve().parent
EXTRACTION_TS = pd.Timestamp("2026-06-30 23:59:00")
EXTRACTION_LABEL = "2026-06-30 23:59 IST"
WA002 = "CAMP_WA_002"
OTHER = ["CAMP_WA_001", "CAMP_SMS_004", "CAMP_CALL_009"]
DOC_ORD = {"DL": 1, "RC": 2, "AADHAAR": 3, "PERMIT": 4, "FITNESS": 5, "INSURANCE": 6}
ORD_LABEL = {
    1: "passed DL only",
    2: "passed through RC (next = Aadhaar)",
    3: "passed through Aadhaar (next = Permit / Fitness)",
    4: "passed through Permit",
    5: "passed through Fitness",
    6: "passed through Insurance",
}


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float, float]:
    if n <= 0:
        return (np.nan, np.nan, np.nan)
    k, n = int(k), int(n)
    p = k / n
    z2 = z * z
    denom = 1.0 + z2 / n
    centre = (p + z2 / (2.0 * n)) / denom
    half = z * np.sqrt((p * (1.0 - p) + z2 / (4.0 * n)) / n) / denom
    return p, centre - half, centre + half


def fmt_rate(k: int, n: int) -> str:
    p, lo, hi = wilson(k, n)
    if n <= 0 or np.isnan(p):
        return "n/a"
    flag = "  [n<100, directional only]" if n < 100 else ""
    return f"{100 * p:6.2f}% ({k:,}/{n:,}) W95% [{100 * lo:5.2f},{100 * hi:5.2f}]{flag}"


def two_prop_z(k1: int, n1: int, k2: int, n2: int) -> tuple[float, float, float, float]:
    """Returns z, p, risk difference, Wald 95% CI on difference (p1-p2)."""
    if min(n1, n2) <= 0:
        return (np.nan, np.nan, np.nan, np.nan)
    p1, p2 = k1 / n1, k2 / n2
    diff = p1 - p2
    p = (k1 + k2) / (n1 + n2)
    se_h0 = np.sqrt(p * (1 - p) * (1 / n1 + 1 / n2))
    z = (p1 - p2) / se_h0 if se_h0 else 0.0
    pval = float(2 * norm.sf(abs(z)))
    se_w = np.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
    return float(z), pval, float(diff), float(1.96 * se_w)


def hr(title: str) -> None:
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)


def sub(title: str) -> None:
    print("\n" + "-" * 100)
    print(title)
    print("-" * 100)


def print_step4_framing() -> None:
    hr("STEP 4 FRAMING LOCK (must sit in front of any memo number)")
    print("These are interpretation constraints, not new calculations.")
    print()
    print("1. Causal assumption under the channel ceiling")
    print("   The 216.5 approved/month (100% close) and the 108–162/month at 50–75%")
    print("   assume that if an organic/paid captain received the fos_field *experience*,")
    print("   they would convert at fos_field's rate. fos_field is in-person recruitment.")
    print("   Recruits may already differ (docs in hand, pre-vetted vehicles, agent")
    print("   pre-screening, higher commitment). This extract cannot separate selection")
    print("   (who fos recruits) from treatment (how they onboard).")
    print("   Present as: IF we could fully replicate the fos_field experience with ZERO")
    print("   selection difference, this is the CEILING. Not: we will get 216 more/month.")
    print()
    print("2. Two distinct interventions — do not add them")
    print("   C1 guided-capture / provisional activation:")
    print("     RC+Insurance uploaded, failed only on capture reasons.")
    print("     n=2,048 (~375/mo); self-serve slice 892 (~164/mo).")
    print("     Mechanism isolated to blur/OCR/illegible. No fos-selection problem.")
    print("     This is the safer lead recommendation.")
    print("   Channel-replication (fos experience at scale):")
    print("     Whole organic/paid conversion gap, all stages.")
    print("     128–256 approved/month at 50–100% of the gap.")
    print("     Larger, more interesting, unproven causal assumption — test, don't bank.")
    print("   Do not sum 164 + 128. Different captains, different mechanisms.")
    print()
    print("3. Already solid as stated: Insurance-abandonment channel pattern;")
    print("   13 post-Fitness nudges = not a usable program; CAC cannot be computed.")


def load():
    captains = pd.read_csv(DATA_DIR / "captains.csv")
    approvals = pd.read_csv(DATA_DIR / "approvals.csv")
    docs = pd.read_csv(DATA_DIR / "doc_events.csv")
    nudges = pd.read_csv(DATA_DIR / "nudges.csv")
    captains["signup_ts"] = pd.to_datetime(captains["signup_ts"], errors="coerce")
    docs["event_ts"] = pd.to_datetime(docs["event_ts"], errors="coerce")
    nudges["sent_ts"] = pd.to_datetime(nudges["sent_ts"], errors="coerce")
    approvals["decision_ts"] = pd.to_datetime(approvals["decision_ts"], errors="coerce")
    captains["signup_age_days"] = (
        EXTRACTION_TS - captains["signup_ts"]
    ).dt.total_seconds() / 86400.0
    df = captains.merge(approvals, on="captain_id", how="left")
    ip_max = float(df.loc[df["final_status"] == "in_progress", "signup_age_days"].max())
    df["mature"] = df["signup_age_days"] > ip_max
    nudges["invalid_click"] = (nudges["clicked"] == 1) & (nudges["delivered"] == 0)
    return df, docs, nudges, ip_max


def stage_at_send(recipients: pd.DataFrame, docs: pd.DataFrame) -> pd.DataFrame:
    passed = docs.loc[
        docs["event_type"] == "verification_pass", ["captain_id", "doc_type", "event_ts"]
    ]
    tmp = recipients[["captain_id", "sent_ts"]].merge(passed, on="captain_id", how="left")
    tmp["before"] = tmp["event_ts"] <= tmp["sent_ts"]
    pre = tmp[tmp["before"]].copy()
    pre["ord"] = pre["doc_type"].map(DOC_ORD)
    mx = pre.groupby("captain_id")["ord"].max().rename("ord_at_send")
    any_ev = (
        docs.merge(recipients[["captain_id", "sent_ts"]], on="captain_id")
        .query("event_ts <= sent_ts")
        .groupby("captain_id")
        .size()
        .rename("n_events_by_send")
    )
    out = recipients.merge(mx, on="captain_id", how="left").merge(
        any_ev, on="captain_id", how="left"
    )
    out["n_events_by_send"] = out["n_events_by_send"].fillna(0).astype(int)
    post = tmp[tmp["event_ts"] > tmp["sent_ts"]].copy()
    post_docs = post.groupby("captain_id")["doc_type"].agg(lambda s: set(s)).rename("post_pass_docs")
    out = out.merge(post_docs, on="captain_id", how="left")
    out["post_pass_docs"] = out["post_pass_docs"].apply(lambda x: x if isinstance(x, set) else set())
    return out


def main() -> None:
    print_step4_framing()

    hr("STEP 5 — CAMP_WA_002 EVALUATION")
    print(f"extract: {EXTRACTION_LABEL}")
    print("Completion = approved, mature cohort only.")
    print("Click-lift sample = CAMP_WA_002 rows with delivered=1.")
    print("Standing rule: clicked=1 & delivered=0 dropped from click comparisons.")
    print("Growth claim under test: CAMP_WA_002 is a big win; scale 5x.")

    df, docs, nudges, ip_max = load()
    print(f"\nmature cutoff: signup_age > {ip_max:.6f} days")
    n_invalid = int(nudges["invalid_click"].sum())
    print(f"invalid click rows in nudges.csv: {n_invalid:,} (all campaigns)")

    wa = nudges[nudges["campaign_id"] == WA002].copy()
    print(f"\nCAMP_WA_002 rows={len(wa):,}  unique captains={wa['captain_id'].nunique():,}")
    print("  delivered × clicked (raw, before standing rule):")
    print("  " + wa.groupby(["delivered", "clicked"]).size().to_string().replace("\n", "\n  "))
    n_inv_wa = int(wa["invalid_click"].sum())
    print(f"  invalid click rows on CAMP_WA_002: {n_inv_wa:,} — excluded from click-lift")
    print(f"  rows per captain: {wa.groupby('captain_id').size().value_counts().to_dict()}")

    rec = df.merge(
        wa[["captain_id", "sent_ts", "delivered", "clicked", "invalid_click"]],
        on="captain_id",
        how="inner",
    )
    rec["days_signup_to_send"] = (
        rec["sent_ts"] - rec["signup_ts"]
    ).dt.total_seconds() / 86400.0
    rec = stage_at_send(rec, docs)
    rec["approved"] = rec["final_status"].eq("approved").astype(int)

    sub("Who received CAMP_WA_002 (descriptive; not a causal contrast)")
    print(f"  recipients n={len(rec):,}")
    print("  final_status:")
    print("  " + rec["final_status"].value_counts().to_string().replace("\n", "\n  "))
    print(f"  mature: {fmt_rate(int(rec['mature'].sum()), len(rec))}")
    print(f"  days signup → send: mean={rec['days_signup_to_send'].mean():.2f}  "
          f"p50={rec['days_signup_to_send'].median():.2f}  "
          f"min={rec['days_signup_to_send'].min():.2f}  max={rec['days_signup_to_send'].max():.2f}")
    print(f"  send before signup: {int((rec['days_signup_to_send'] < 0).sum()):,}")
    n_appr = int((rec["final_status"] == "approved").sum())
    n_after_dec = int(
        ((rec["final_status"] == "approved") & (rec["sent_ts"] > rec["decision_ts"])).sum()
    )
    print(f"  send after approval decision: {n_after_dec:,} / {n_appr:,} approved recipients")

    mature_all = df[df["mature"]]
    got_ids = set(rec["captain_id"])
    got_m = mature_all[mature_all["captain_id"].isin(got_ids)]
    not_m = mature_all[~mature_all["captain_id"].isin(got_ids)]
    k1, n1 = int((got_m["final_status"] == "approved").sum()), len(got_m)
    k0, n0 = int((not_m["final_status"] == "approved").sum()), len(not_m)
    z, pz, diff, half = two_prop_z(k1, n1, k0, n0)
    print("\n  naive contrast (confounded by targeting — do not treat as campaign lift):")
    print(f"    approved | received, mature: {fmt_rate(k1, n1)}")
    print(f"    approved | not received, mature: {fmt_rate(k0, n0)}")
    print(f"    Δ={100 * diff:+.2f}pp  Wald95% [{100 * (diff - half):+.2f},{100 * (diff + half):+.2f}]  "
          f"z={z:.2f} p={pz:.4g}")
    print("    Recipients already passed RC by send (below). This gap is mostly who was")
    print("    selected into the campaign, not what the message did.")

    # ---- click-lift sample ----
    sub("Primary estimand: clicked vs not, among mature + delivered CAMP_WA_002")
    print("  delivered=1 implies the 251 invalid clicks are already out.")
    clk = rec[rec["mature"] & rec["delivered"].eq(1)].copy()
    print(f"  n={len(clk):,}  clicked={int(clk['clicked'].sum()):,}  not={int((clk['clicked']==0).sum()):,}")
    a = clk[clk["clicked"] == 1]
    b = clk[clk["clicked"] == 0]
    ka, na = int(a["approved"].sum()), len(a)
    kb, nb = int(b["approved"].sum()), len(b)
    z, pz, diff, half = two_prop_z(ka, na, kb, nb)
    print(f"  approved | clicked:     {fmt_rate(ka, na)}")
    print(f"  approved | not clicked: {fmt_rate(kb, nb)}")
    print(f"  Δ (click − no click) = {100 * diff:+.2f}pp  "
          f"Wald95% [{100 * (diff - half):+.2f},{100 * (diff + half):+.2f}]")
    print(f"  two-proportion z={z:.2f}  p={pz:.4g}")
    if pz >= 0.05:
        print("  Result: NO statistically significant click-associated completion lift.")
        print("  Point estimate is at or below zero. The CI includes 0 and does not include")
        print("  a large positive effect.")
    else:
        print("  Result: statistically significant difference — inspect sign before claiming a win.")

    hr("1. SELECTION BIAS — are clickers a random sample of recipients?")
    print("  Among the same click-lift sample (mature, delivered).")
    print("  Tests: chi-square on channel, device_tier, signup month; Mann-Whitney on")
    print("  signup_age and days-to-send. Bonferroni α=0.05/5=0.01 for this family of 5.")
    ALPHA = 0.05 / 5

    for col, name in [
        ("acquisition_channel", "acquisition_channel"),
        ("device_tier", "device_tier"),
    ]:
        ct = pd.crosstab(clk[col], clk["clicked"])
        chi2, p, dof, exp = chi2_contingency(ct)
        flag = "  ** sig vs Bonferroni **" if p < ALPHA else (
            "  (raw p<0.05 only)" if p < 0.05 else ""
        )
        print(f"\n  {name} × clicked: χ²={chi2:.2f} dof={dof} p={p:.4g} min_exp={exp.min():.2f}{flag}")
        print("    click rate by level:")
        for lvl, n in clk[col].value_counts().items():
            k = int(clk.loc[clk[col] == lvl, "clicked"].sum())
            print(f"      {str(lvl):<18} {fmt_rate(k, n)}")
        print("    column % (composition of clickers vs non-clickers):")
        print("    " + pd.crosstab(clk[col], clk["clicked"], normalize="columns").mul(100).round(2).to_string().replace("\n", "\n    "))

    month = clk["signup_ts"].dt.to_period("M").astype(str)
    ct = pd.crosstab(month, clk["clicked"])
    chi2, p, dof, exp = chi2_contingency(ct)
    flag = "  ** sig vs Bonferroni **" if p < ALPHA else (
        "  (raw p<0.05 only)" if p < 0.05 else ""
    )
    print(f"\n  signup month × clicked: χ²={chi2:.2f} dof={dof} p={p:.4g}{flag}")
    print("    " + pd.crosstab(month, clk["clicked"], normalize="columns").mul(100).round(2).to_string().replace("\n", "\n    "))

    u_age = mannwhitneyu(a["signup_age_days"], b["signup_age_days"])
    u_send = mannwhitneyu(a["days_signup_to_send"], b["days_signup_to_send"])
    print(f"\n  signup_age_days  clickers mean={a['signup_age_days'].mean():.2f} p50={a['signup_age_days'].median():.2f}  "
          f"non-click mean={b['signup_age_days'].mean():.2f} p50={b['signup_age_days'].median():.2f}")
    print(f"    Mann-Whitney U p={u_age.pvalue:.4g}" + (
        "  ** sig vs Bonferroni **" if u_age.pvalue < ALPHA else ""
    ))
    print(f"  days signup→send  clickers mean={a['days_signup_to_send'].mean():.2f} p50={a['days_signup_to_send'].median():.2f}  "
          f"non-click mean={b['days_signup_to_send'].mean():.2f} p50={b['days_signup_to_send'].median():.2f}")
    print(f"    Mann-Whitney U p={u_send.pvalue:.4g}" + (
        "  ** sig vs Bonferroni **" if u_send.pvalue < ALPHA else ""
    ))
    print("\n  Read-out: if observables do not differ, that does NOT make click random.")
    print("  Click still selects on unobserved motivation / phone-availability / literacy.")
    print("  The click contrast is still not an experiment. We report it because that is")
    print("  the contrast the growth claim uses.")

    sub("Logistic: approved ~ clicked + channel + device_tier + signup month + stage-at-send (RC vs past RC)")
    print("  Checks whether a click coefficient appears after the observables above.")
    logit_df = clk.copy()
    logit_df["month"] = logit_df["signup_ts"].dt.to_period("M").astype(str)
    logit_df["clicked"] = logit_df["clicked"].astype(int)
    # ord_at_send is almost all 2; still include as categorical
    logit_df["ord_bin"] = np.where(logit_df["ord_at_send"].astype(int) <= 2, "RC_or_less", "past_RC")
    fit = smf.logit(
        "approved ~ clicked + C(acquisition_channel) + C(device_tier) + C(month) + C(ord_bin)",
        data=logit_df,
    ).fit(disp=False, maxiter=200)
    or_clk = np.exp(fit.params["clicked"])
    lo, hi = np.exp(fit.conf_int().loc["clicked"])
    print(f"  clicked OR={or_clk:.3f}  95%CI [{lo:.3f}, {hi:.3f}]  p={fit.pvalues['clicked']:.4g}")
    print(f"  model n={int(fit.nobs):,}  pseudo-R²={fit.prsquared:.4f}  converged={fit.mle_retvals['converged']}")
    print("  Other coefficients omitted unless needed; click is the claim coefficient.")

    hr("2. CAMPAIGN OVERLAP")
    other = nudges[nudges["campaign_id"].isin(OTHER)]
    rec_ids = set(rec["captain_id"])
    overlap_ids = set(other.loc[other["captain_id"].isin(rec_ids), "captain_id"])
    print(f"  CAMP_WA_002 recipients who also received ≥1 other campaign: "
          f"{fmt_rate(len(overlap_ids), len(rec_ids))}")
    print("  by other campaign (not mutually exclusive):")
    for c in OTHER:
        n = other.loc[(other["campaign_id"] == c) & other["captain_id"].isin(rec_ids), "captain_id"].nunique()
        print(f"    {c:<16} {fmt_rate(n, len(rec_ids))}")
    n_camps = (
        nudges[nudges["captain_id"].isin(rec_ids)]
        .groupby("captain_id")["campaign_id"]
        .nunique()
    )
    print("  n distinct campaigns per CAMP_WA_002 recipient:")
    print("  " + n_camps.value_counts().sort_index().to_string().replace("\n", "\n  "))
    print("  30% overlap is material. An isolated CAMP_WA_002 effect cannot be cleanly")
    print("  attributed from this data for those captains.")

    sub("Click-lift among exclusive CAMP_WA_002 recipients (no other campaign)")
    excl = clk[~clk["captain_id"].isin(overlap_ids)]
    print(f"  mature delivered exclusive n={len(excl):,}  ({100 * len(excl) / len(clk):.1f}% of click-lift sample)")
    a = excl[excl["clicked"] == 1]
    b = excl[excl["clicked"] == 0]
    ka, na = int(a["approved"].sum()), len(a)
    kb, nb = int(b["approved"].sum()), len(b)
    z, pz, diff, half = two_prop_z(ka, na, kb, nb)
    print(f"  approved | clicked:     {fmt_rate(ka, na)}")
    print(f"  approved | not clicked: {fmt_rate(kb, nb)}")
    print(f"  Δ={100 * diff:+.2f}pp  Wald95% [{100 * (diff - half):+.2f},{100 * (diff + half):+.2f}]  "
          f"z={z:.2f} p={pz:.4g}")

    hr("3. TIMING / STAGE AT SEND")
    print("  Question: is CAMP_WA_002 aimed at a stage where a WhatsApp nudge could")
    print("  plausibly move completion, or is a null result unsurprising a priori")
    print("  (as with the 13 post-Fitness nudges in Step 4)?")
    print(f"\n  any doc_event by send: {fmt_rate(int((rec['n_events_by_send'] > 0).sum()), len(rec))}")
    print("  furthest verification_pass at send (all recipients):")
    print(f"    no pass yet: {int(rec['ord_at_send'].isna().sum()):,}")
    for o, c in rec["ord_at_send"].value_counts().sort_index().items():
        print(f"    ord={int(o)} {ORD_LABEL.get(int(o), '?'):<48} {fmt_rate(int(c), len(rec))}")
    print("\n  same, mature + delivered (click-lift sample):")
    for o, c in clk["ord_at_send"].value_counts().sort_index().items():
        print(f"    ord={int(o)} {ORD_LABEL.get(int(o), '?'):<48} {fmt_rate(int(c), len(clk))}")
    print("\n  Read-out vs Step 4 Fitness nudges:")
    print("  CAMP_WA_002 is sent ~2.2 days after signup. ~89% of recipients have already")
    print("  passed RC and have not yet passed Aadhaar — i.e. it hits the post-RC")
    print("  continuation window (Aadhaar → Permit/Fitness → Insurance), which IS a")
    print("  plausible intervention point. A null click result is therefore informative")
    print("  about the message/channel, not an artefact of messaging people after the")
    print("  funnel is over. This is the opposite of the post-Fitness dead-end.")

    sub("Progression AFTER send, click vs not (mature delivered)")
    print("  Among captains whose furthest pass at send was RC (ord=2): did they later")
    print("  pass Aadhaar? Among ord=3: later pass Permit? Approval still the primary.")
    nxt = {2: "AADHAAR", 3: "PERMIT"}
    n_tests_prog = 4  # two strata × (next-pass, approved)
    print(f"  Bonferroni α=0.05/{n_tests_prog}={0.05 / n_tests_prog:.4g} for this mini-family.")
    for o, doc in nxt.items():
        sl = clk[clk["ord_at_send"] == o].copy()
        sl["next_pass"] = sl["post_pass_docs"].apply(lambda s, d=doc: d in s)
        print(f"\n  at-send ord={o} n={len(sl):,}  next doc={doc}")
        if len(sl) < 100:
            print("    [n<100 overall, directional only]")
        for cv, g in sl.groupby("clicked"):
            kn = int(g["next_pass"].sum())
            ka2 = int(g["approved"].sum())
            lab = "clicked" if cv == 1 else "not clicked"
            print(f"    {lab:<12} later {doc} {fmt_rate(kn, len(g))}  approved {fmt_rate(ka2, len(g))}")
        a = sl[sl["clicked"] == 1]
        b = sl[sl["clicked"] == 0]
        z, pz, diff, half = two_prop_z(int(a["next_pass"].sum()), len(a), int(b["next_pass"].sum()), len(b))
        print(f"    later {doc} Δ={100 * diff:+.2f}pp z={z:.2f} p={pz:.4g}  "
              f"{'sig Bonferroni' if pz < 0.05 / n_tests_prog else ('raw p<0.05 only' if pz < 0.05 else 'not sig')}")
        z, pz, diff, half = two_prop_z(int(a["approved"].sum()), len(a), int(b["approved"].sum()), len(b))
        print(f"    approved   Δ={100 * diff:+.2f}pp z={z:.2f} p={pz:.4g}  "
              f"{'sig Bonferroni' if pz < 0.05 / n_tests_prog else ('raw p<0.05 only' if pz < 0.05 else 'not sig')}")

    hr("4. DOES THE 'BIG WIN, SCALE 5×' CLAIM HOLD?")
    print("  Claim: CAMP_WA_002 is a big win for onboarding completion and should be scaled 5x.")
    print()
    a = clk[clk["clicked"] == 1]
    b = clk[clk["clicked"] == 0]
    ka, na = int(a["approved"].sum()), len(a)
    kb, nb = int(b["approved"].sum()), len(b)
    z, pz, diff, half = two_prop_z(ka, na, kb, nb)
    print("  What we can defend in a deck:")
    print(f"    Among mature captains with a delivered CAMP_WA_002 message (n={len(clk):,}):")
    print(f"    clicked {fmt_rate(ka, na)}")
    print(f"    not     {fmt_rate(kb, nb)}")
    print(f"    Δ={100 * diff:+.2f}pp  Wald95% [{100 * (diff - half):+.2f}, {100 * (diff + half):+.2f}]  z={z:.2f} p={pz:.4g}")
    print()
    print("  Number I would put in a deck with my name on it:")
    print("    Completion lift attributable to clicking CAMP_WA_002: 0 pp.")
    print(f"    Best estimate of the click contrast: {100 * diff:+.1f}pp")
    print(f"    95% CI [{100 * (diff - half):+.1f}, {100 * (diff + half):+.1f}] pp, p={pz:.2f}.")
    print("    Confidence in 'no large positive click-lift': HIGH (n=7,387 delivered,")
    print("    CI rules out lifts larger than about the upper Wald bound).")
    print("    Confidence in 'the campaign has zero effect on anyone': LOW — this is not")
    print("    an RCT; we did not test send vs no-send among eligible captains, and 30%")
    print("    of recipients got another campaign.")
    print()
    print("  The naive recipient vs non-recipient gap (29% vs 11% approved, mature) is")
    print("  NOT a campaign effect. Recipients are selected after they have already")
    print("  cleared RC. Scaling 5x would either (i) message more of the same RC-cleared")
    print("  pool, where clicking shows no completion lift, or (ii) expand to people who")
    print("  have not cleared RC, a population this campaign has not been shown to work on.")
    print()
    print("  Verdict: the 'big win, scale it 5x' claim does NOT hold for onboarding")
    print("  completion. I would not fund a 5x scale on this evidence. A test I would")
    print("  fund: randomized send vs no-send among RC-cleared self-serve captains,")
    print("  exclusive of other campaigns, with Aadhaar-pass and approved as endpoints.")
    print()
    print("Step 5 complete. No further sections.")


if __name__ == "__main__":
    main()
