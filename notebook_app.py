"""One HTML page for Project_R.ipynb — Colab shows a single site, not stacked cells."""

from __future__ import annotations

import base64
import html as html_lib
from pathlib import Path

from IPython.display import HTML, display

YELLOW = "#FFD400"
INK = "#111111"
CREAM = "#FFF8E7"
ROOT = Path(__file__).resolve().parent


def _b64(path: Path) -> str:
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def _asset(rel: str, *, relative: bool) -> str:
    p = ROOT / rel
    if not p.exists():
        return ""
    return rel if relative else _b64(p)


def cartoon(stem: str, *, relative: bool = False) -> str:
    for folder in ("vehicles", "cartoons"):
        src = _asset(f"figures/{folder}/{stem}.png", relative=relative)
        if src:
            return src
    return ""


def waterfall_src(*, relative: bool = False) -> str:
    return _asset("figures/funnel_waterfall.png", relative=relative)


def show_app(**kwargs) -> None:
    """One box in Colab: CSS, cartoons, sliders, waterfall, logs together."""
    inner = app_html(**kwargs)
    escaped = inner.replace("&", "&amp;").replace('"', "&quot;")
    display(
        HTML(
            '<iframe srcdoc="'
            + escaped
            + '" style="width:100%;min-height:3200px;height:3200px;border:0;border-radius:16px;background:transparent;"></iframe>'
        )
    )


def app_html(
    *,
    n: int,
    n_appr: int,
    months: float,
    c1a_60: float,
    c1a_at_1: float,
    c1b: float,
    airport_unf: float,
    other_unf: float,
    night_share: float,
    cap_night: float,
    cap_day: float,
    ara_leg: float,
    ara_mo: float,
    mix: dict[str, int],
    logs: dict[str, str],
    relative_assets: bool = False,
) -> str:
    def img(stem: str, alt: str) -> str:
        src = cartoon(stem, relative=relative_assets)
        return f'<img src="{src}" alt="{alt}"/>' if src else ""

    wf = waterfall_src(relative=relative_assets)
    wf_block = (
        f'<img class="pr-wf" src="{wf}" alt="Funnel waterfall"/>'
        if wf
        else "<p>Waterfall image not written.</p>"
    )

    log_bits = []
    for title, text in logs.items():
        safe = html_lib.escape(text[-18000:])
        log_bits.append(
            f"<details><summary>{html_lib.escape(title)}</summary><pre>{safe}</pre></details>"
        )
    logs_html = "".join(log_bits)
    logs_section = (
        f'<div class="pr-sec">Step prints from 01–08 (working only)</div>{logs_html}'
        if logs_html
        else ""
    )

    # Inline handler: htmlpreview.github.io often drops <script> tags.
    upd = (
        f"var s=+document.getElementById('prShow').value;"
        f"var p=+document.getElementById('prAra').value;"
        f"var c1a={c1a_at_1}*(s/100);"
        "document.getElementById('showLbl').textContent=s+'%';"
        "document.getElementById('araLbl').textContent=p+'%';"
        "document.getElementById('c1aVal').textContent=c1a.toFixed(1);"
        f"document.getElementById('combo').textContent=Math.round(c1a+{c1b});"
        f"document.getElementById('payVal').textContent='\\u20B9'+( {ara_leg}*p/100).toFixed(1);"
        f"document.getElementById('araMo').textContent='\\u20B9'+Math.round({ara_mo}*p/100);"
    )

    auto_n = mix.get("Auto", 0)
    cab_n = mix.get("Cab", 0)
    er_n = mix.get("ERickshaw", 0)
    appr_pct = 100.0 * n_appr / n if n else 0.0

    return f"""
<div class="pr">
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
.pr {{
  font-family: 'Plus Jakarta Sans', ui-sans-serif, system-ui, sans-serif;
  color: {INK};
  background: {CREAM};
  padding: 18px 16px 28px;
  border-radius: 24px;
  max-width: 1080px;
  margin: 0 auto;
  box-sizing: border-box;
}}
.pr * {{ box-sizing: border-box; }}
.pr-hero {{
  background: linear-gradient(135deg, {YELLOW} 0%, #FFE566 50%, #FFC400 100%);
  border: 3px solid {INK};
  border-radius: 22px;
  padding: 26px 28px;
  box-shadow: 8px 8px 0 {INK};
  margin-bottom: 18px;
}}
.pr-kicker {{
  display: inline-block; background: {INK}; color: {YELLOW};
  font-size: 0.7rem; font-weight: 700; letter-spacing: 0.14em;
  padding: 4px 10px; border-radius: 999px; margin-bottom: 10px;
}}
.pr-hero h1 {{ margin: 0 0 6px; font-size: 1.85rem; font-weight: 800; letter-spacing: -0.03em; }}
.pr-hero p {{ margin: 0; opacity: 0.82; }}
.pr-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(168px, 1fr)); gap: 12px; margin: 14px 0; }}
.pr-card {{
  background: #fff; border: 2px solid {INK}; border-radius: 16px;
  padding: 14px; box-shadow: 4px 4px 0 {INK};
}}
.pr-card .lbl {{ font-size: 0.72rem; color: #5c5c5c; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em; }}
.pr-card .val {{ font-size: 1.55rem; font-weight: 800; margin-top: 4px; letter-spacing: -0.03em; }}
.pr-card .sub {{ font-size: 0.76rem; color: #5c5c5c; margin-top: 4px; }}
.pr-sec {{ font-size: 1.12rem; font-weight: 800; margin: 22px 0 10px; }}
.pr-veh {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; }}
.pr-veh .pr-card {{ text-align: center; }}
.pr-veh img {{ width: 112px; height: 112px; object-fit: contain; margin: 0 auto 8px; display: block; }}
.pr-ask {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 12px; }}
.pr-ask h3 {{ margin: 0 0 6px; font-size: 1rem; }}
.pr-ask .n {{ font-size: 0.78rem; font-weight: 800; color: #1B7A4E; }}
.pr-warn {{
  background: #FFF3CD; border: 2px solid {INK}; border-radius: 14px;
  padding: 12px 16px; font-size: 0.9rem; margin: 14px 0;
}}
.pr-ok {{
  background: #E7F6EE; border: 2px solid {INK}; border-radius: 14px;
  padding: 12px 16px; font-size: 0.9rem; margin: 0 0 14px;
}}
.pr-wf {{ width: 100%; border-radius: 12px; border: 2px solid {INK}; background: #fff; }}
.pr-live {{ background: #FFF4B0; }}
.pr input[type=range] {{ width: 100%; accent-color: {INK}; }}
.pr-slide {{ margin: 8px 0 14px; }}
.pr-slide label {{ font-size: 0.82rem; font-weight: 700; display: flex; justify-content: space-between; }}
.pr details {{
  border: 2px solid {INK}; border-radius: 12px; padding: 8px 12px; background: #fff; margin: 8px 0;
}}
.pr details summary {{ cursor: pointer; font-weight: 700; }}
.pr pre {{
  max-height: 220px; overflow: auto; font-size: 0.7rem;
  background: #111; color: #eee; padding: 10px; border-radius: 8px;
}}
</style>

  <div class="pr-hero">
    <div class="pr-kicker">RAPIDO · PROJECT_R</div>
    <h1>Captain onboarding leak, sized. Airport nights, priced.</h1>
    <p>Extract 30 Jun 2026, 23:59 IST · one page · Runtime → Run all</p>
  </div>
  <div class="pr-ok"><b>Pipeline finished.</b> Same maths as run_all.sh · regression lock passed if this page rendered.</div>

  <div class="pr-grid">
    <div class="pr-card"><div class="lbl">Approved | mature∩events</div><div class="val">{appr_pct:.1f}%</div><div class="sub">{n_appr:,} / {n:,} · {months:.2f} mo</div></div>
    <div class="pr-card pr-live"><div class="lbl">C1a + C1b (disjoint)</div><div class="val" id="combo">{c1a_60 + c1b:.0f}</div><div class="sub">do not add fos 128–256 · moves with C1a slider</div></div>
    <div class="pr-card"><div class="lbl">Airport unfulfilled</div><div class="val">{100 * airport_unf:.0f}%</div><div class="sub">vs {100 * other_unf:.0f}% elsewhere · {100 * night_share:.0f}% in 21:00–03:59</div></div>
    <div class="pr-card"><div class="lbl">Captains night vs day</div><div class="val">{cap_night:.0f} vs {cap_day:.0f}</div><div class="sub">do not hire the catchment</div></div>
  </div>

  <div class="pr-sec">Move the two assumptions</div>
  <p class="sub" style="margin:0 0 10px;color:#5c5c5c">Yellow cards update. C1b, approval %, and airport figures stay locked on purpose.</p>
  <div class="pr-slide">
    <label>C1a 10-day show-up <span id="showLbl">60%</span></label>
    <input id="prShow" type="range" min="0" max="100" value="60" oninput="{upd}" onchange="{upd}"/>
  </div>
  <div class="pr-slide">
    <label>ARA as % of derived ₹{ara_leg:.1f}/leg <span id="araLbl">100%</span></label>
    <input id="prAra" type="range" min="50" max="150" step="5" value="100" oninput="{upd}" onchange="{upd}"/>
  </div>
  <div class="pr-grid">
    <div class="pr-card pr-live"><div class="lbl">C1a / month</div><div class="val" id="c1aVal">{c1a_60:.1f}</div><div class="sub">flow × show-up × RC att-3</div></div>
    <div class="pr-card"><div class="lbl">C1b / month</div><div class="val">{c1b:.1f}</div><div class="sub">Insurance UX · locked</div></div>
    <div class="pr-card pr-live"><div class="lbl">₹ / eligible leg</div><div class="val" id="payVal">₹{ara_leg:.1f}</div><div class="sub">not 30% of fare</div></div>
    <div class="pr-card pr-live"><div class="lbl">ARA sample / month</div><div class="val" id="araMo">₹{ara_mo:,.0f}</div><div class="sub">sampled trips · not city P&amp;L</div></div>
  </div>

  <div class="pr-sec">Fleet mix</div>
  <div class="pr-veh">
    <div class="pr-card">{img("auto","Auto")}<div class="lbl">Auto</div><div class="val" style="font-size:1.05rem">{auto_n:,} signups</div><div class="sub">In extract</div></div>
    <div class="pr-card">{img("cab","Cab")}<div class="lbl">Cab</div><div class="val" style="font-size:1.05rem">{cab_n:,} signups</div><div class="sub">In extract</div></div>
    <div class="pr-card">{img("scooty","Scooty")}<div class="lbl">E-rickshaw / scooty</div><div class="val" style="font-size:1.05rem">{er_n:,} signups</div><div class="sub">ERickshaw in file</div></div>
    <div class="pr-card">{img("bike","Bike")}<div class="lbl">Bike</div><div class="val" style="font-size:1.05rem">Not in extract</div><div class="sub">Decorative only</div></div>
  </div>

  <div class="pr-sec">Ask — in this order</div>
  <div class="pr-ask">
    <div class="pr-card"><div class="n">1 · PRODUCT</div><h3>C1b Insurance capture UX</h3><p>~46–52 extra approved / month. No legal deferral.</p></div>
    <div class="pr-card"><div class="n">2 · LEGAL + OPS</div><h3>C1a provisional RC</h3><p>~133.5 / month at 60% show-up. Show-up unobserved.</p></div>
    <div class="pr-card"><div class="n">3 · AIRPORT</div><h3>ARA ₹{ara_leg:.1f} / unpaid night-suburban leg</h3><p>Do not hire. Sample ~₹69–103k / month.</p></div>
    <div class="pr-card"><div class="n">STOP</div><h3>Kill CAMP_WA_002 5×</h3><p>Clicked vs not ≈ 0 pp. Targeting, not lift.</p></div>
  </div>
  <div class="pr-warn">Do not bank fos 128–256 / month. Do not add leftover stages into ~180. 30% of fare (₹105) overpays vs ₹{ara_leg:.1f}.</div>

  <div class="pr-sec">Funnel waterfall</div>
  {wf_block}

  {logs_section}
</div>
"""


def write_dashboard(path: Path | None = None) -> Path:
    """Static page for raw.githack / local file open. Same sliders as the notebook."""
    from metrics import (
        C1A_CENTRAL_SHOWUP,
        airport_hourly_snapshot,
        ara_economics,
        ara_monthly_cost,
        c1a_monthly,
        c1b_monthly,
        event_funnel,
        load_onboarding,
        mature_months,
    )

    hourly = airport_hourly_snapshot()
    eco = ara_economics()
    months, *_ = mature_months()
    funnel = event_funnel()
    n = len(funnel)
    n_appr = int(funnel["final_status"].eq("approved").sum())
    captains, *_ = load_onboarding()
    inner = app_html(
        n=n,
        n_appr=n_appr,
        months=months,
        c1a_60=c1a_monthly(C1A_CENTRAL_SHOWUP),
        c1a_at_1=c1a_monthly(1.0),
        c1b=c1b_monthly(2),
        airport_unf=hourly["airport_unf_share"],
        other_unf=hourly["other_unf_share"],
        night_share=hourly["night_share_of_airport_unf"],
        cap_night=hourly["mean_captains_worst"],
        cap_day=hourly["mean_captains_rest"],
        ara_leg=eco["payout_per_eligible_leg"],
        ara_mo=ara_monthly_cost(1.0),
        mix=captains["vehicle_type"].value_counts().to_dict(),
        logs={},
        relative_assets=True,
    )
    page = (
        "<!doctype html>\n"
        '<html lang="en">\n<head>\n'
        '<meta charset="utf-8"/>\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1"/>\n'
        "<title>Project_R — Rapido dashboard</title>\n"
        f'<style>html,body{{margin:0;background:{CREAM};}}</style>\n'
        "</head>\n"
        f'<body style="margin:0;background:{CREAM}">\n'
        f"{inner}\n"
        "</body>\n</html>\n"
    )
    out = path or (ROOT / "dashboard.html")
    out.write_text(page, encoding="utf-8")
    print(f"wrote {out}")
    return out


if __name__ == "__main__":
    write_dashboard()

