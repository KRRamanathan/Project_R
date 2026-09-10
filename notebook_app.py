"""Rapido-yellow dashboard HTML for Project_R.ipynb (local + Colab)."""

from __future__ import annotations

import base64
from pathlib import Path

from IPython.display import HTML, display

YELLOW = "#FFD400"
INK = "#111111"
CREAM = "#FFF8E7"
CARD = "#FFFFFF"
MUTED = "#5C5C5C"
LEAK = "#E85D04"
OK = "#1B7A4E"
NAVY = "#1A1A1A"

ROOT = Path(__file__).resolve().parent


def _b64_img(path: Path) -> str:
    raw = path.read_bytes()
    return "data:image/png;base64," + base64.b64encode(raw).decode("ascii")


def cartoon_src(stem: str) -> str:
    p = ROOT / "figures" / "cartoons" / f"{stem}.png"
    if p.exists():
        return _b64_img(p)
    return ""


def inject_css() -> None:
    display(
        HTML(
            f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
.pr-wrap {{
  font-family: 'Plus Jakarta Sans', ui-sans-serif, system-ui, sans-serif;
  color: {INK};
  background: {CREAM};
  padding: 8px 4px 28px;
  border-radius: 20px;
}}
.pr-hero {{
  background: linear-gradient(135deg, {YELLOW} 0%, #FFE566 55%, #FFC400 100%);
  border: 3px solid {INK};
  border-radius: 22px;
  padding: 28px 32px 24px;
  box-shadow: 8px 8px 0 {INK};
  margin-bottom: 22px;
  position: relative;
  overflow: hidden;
}}
.pr-hero h1 {{
  margin: 0 0 6px;
  font-size: 2.05rem;
  font-weight: 800;
  letter-spacing: -0.03em;
}}
.pr-hero p {{ margin: 0; color: {INK}; opacity: 0.82; font-size: 0.98rem; }}
.pr-kicker {{
  display: inline-block;
  background: {INK};
  color: {YELLOW};
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  padding: 4px 10px;
  border-radius: 999px;
  margin-bottom: 10px;
}}
.pr-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 14px;
  margin: 14px 0 22px;
}}
.pr-card {{
  background: {CARD};
  border: 2px solid {INK};
  border-radius: 16px;
  padding: 16px 16px 14px;
  box-shadow: 4px 4px 0 {INK};
}}
.pr-card .lbl {{ font-size: 0.75rem; color: {MUTED}; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; }}
.pr-card .val {{ font-size: 1.65rem; font-weight: 800; margin-top: 4px; letter-spacing: -0.03em; }}
.pr-card .sub {{ font-size: 0.78rem; color: {MUTED}; margin-top: 4px; }}
.pr-sec {{
  font-size: 1.15rem;
  font-weight: 800;
  margin: 22px 0 10px;
  display: flex;
  align-items: center;
  gap: 8px;
}}
.pr-chip {{
  background: {YELLOW};
  border: 2px solid {INK};
  border-radius: 999px;
  padding: 2px 10px;
  font-size: 0.72rem;
  font-weight: 700;
}}
.pr-veh {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 14px;
  margin: 8px 0 20px;
}}
.pr-veh .pr-card {{ text-align: center; }}
.pr-veh img {{
  width: 118px; height: 118px; object-fit: contain;
  margin: 4px auto 8px;
  display: block;
}}
.pr-warn {{
  background: #FFF3CD;
  border: 2px solid {INK};
  border-radius: 14px;
  padding: 12px 16px;
  font-size: 0.9rem;
  margin: 12px 0;
}}
.pr-ok {{
  background: #E7F6EE;
  border: 2px solid {INK};
  border-radius: 14px;
  padding: 12px 16px;
  font-size: 0.9rem;
}}
.pr-progress {{
  display: flex; flex-wrap: wrap; gap: 8px; margin: 10px 0 18px;
}}
.pr-step {{
  border: 2px solid {INK};
  border-radius: 999px;
  padding: 6px 12px;
  font-size: 0.78rem;
  font-weight: 700;
  background: #eee;
}}
.pr-step.done {{ background: {YELLOW}; }}
.pr-step.run {{ background: #fff; box-shadow: 3px 3px 0 {INK}; }}
.pr-ask {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px;
}}
.pr-ask .pr-card h3 {{ margin: 0 0 6px; font-size: 1rem; }}
.pr-ask .n {{ font-size: 0.8rem; font-weight: 800; color: {OK}; }}
details.pr-log {{
  border: 2px solid {INK};
  border-radius: 14px;
  padding: 8px 12px;
  background: #fff;
  margin: 8px 0;
}}
details.pr-log summary {{ cursor: pointer; font-weight: 700; }}
details.pr-log pre {{
  max-height: 280px; overflow: auto; font-size: 0.72rem;
  background: #111; color: #F3F3F3; padding: 10px; border-radius: 8px;
}}
</style>
"""
        )
    )


def hero() -> None:
    display(
        HTML(
            """
<div class="pr-wrap">
  <div class="pr-hero">
    <div class="pr-kicker">RAPIDO · PROJECT_R</div>
    <h1>Captain onboarding leak, sized. Airport nights, priced.</h1>
    <p>Extract 30 Jun 2026, 23:59 IST · synthetic CSVs · Kernel → Run All (works on Google Colab)</p>
  </div>
</div>
"""
        )
    )


def progress_html(done: list[str], current: str | None = None) -> str:
    chips = []
    for name in done:
        chips.append(f'<span class="pr-step done">✓ {name}</span>')
    if current:
        chips.append(f'<span class="pr-step run">… {current}</span>')
    return f'<div class="pr-progress">{"".join(chips)}</div>'


def metric_cards(rows: list[tuple[str, str, str]]) -> None:
    inner = "".join(
        f'<div class="pr-card"><div class="lbl">{a}</div><div class="val">{b}</div><div class="sub">{c}</div></div>'
        for a, b, c in rows
    )
    display(HTML(f'<div class="pr-wrap"><div class="pr-grid">{inner}</div></div>'))


def vehicle_strip(counts: dict[str, int], note: str) -> None:
    items = [
        ("auto", "Auto", "In extract"),
        ("cab", "Cab", "In extract"),
        ("scooty", "E-rickshaw / scooty", "ERickshaw in file"),
        ("bike", "Bike", "Not in this extract"),
    ]
    cards = []
    for stem, label, sub in items:
        src = cartoon_src(stem)
        img = f'<img src="{src}" alt="{label}"/>' if src else ""
        n = ""
        if stem == "auto":
            n = f"{counts.get('Auto', 0):,} signups"
        elif stem == "cab":
            n = f"{counts.get('Cab', 0):,} signups"
        elif stem == "scooty":
            n = f"{counts.get('ERickshaw', 0):,} signups"
        else:
            n = "Decorative — no Bike rows"
        cards.append(
            f'<div class="pr-card">{img}<div class="lbl">{label}</div>'
            f'<div class="val" style="font-size:1.05rem">{n}</div>'
            f'<div class="sub">{sub}</div></div>'
        )
    display(
        HTML(
            f'<div class="pr-wrap"><div class="pr-sec">Fleet mix <span class="pr-chip">{note}</span></div>'
            f'<div class="pr-veh">{"".join(cards)}</div></div>'
        )
    )


def rec_cards() -> None:
    display(
        HTML(
            """
<div class="pr-wrap">
  <div class="pr-sec">Ask — in this order</div>
  <div class="pr-ask">
    <div class="pr-card">
      <div class="n">1 · PRODUCT</div>
      <h3>C1b Insurance capture UX</h3>
      <p>Blur/OCR at upload. ~46–52 extra approved / month. No legal deferral.</p>
    </div>
    <div class="pr-card">
      <div class="n">2 · LEGAL + OPS</div>
      <h3>C1a provisional RC, 10-day grace</h3>
      <p>Central 60% show-up × att-3 → ~133.5 / month. Show-up unobserved.</p>
    </div>
    <div class="pr-card">
      <div class="n">3 · AIRPORT</div>
      <h3>ARA ₹35.4 / unpaid night-suburban leg</h3>
      <p>4-week run. Do not hire the catchment. Sample ~₹69–103k / month.</p>
    </div>
    <div class="pr-card">
      <div class="n">STOP</div>
      <h3>Kill CAMP_WA_002 5×</h3>
      <p>Clicked vs not ≈ 0 pp. Naive recipient gap is targeting after RC.</p>
    </div>
  </div>
  <div class="pr-warn">Do not bank fos 128–256 / month. Do not add leftover stages into ~180. Do not pay 30% of fare as ARA (₹105 overpays vs ₹35.4).</div>
</div>
"""
        )
    )


def log_block(title: str, text: str) -> None:
    safe = (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
    display(
        HTML(
            f'<details class="pr-log"><summary>{title} — click to expand print log</summary>'
            f"<pre>{safe[-20000:]}</pre></details>"
        )
    )
