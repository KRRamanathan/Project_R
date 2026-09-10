#!/usr/bin/env python3
"""Two-page Word memo: Claude cream / peach / light yellow / light orange, dark type."""

from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

import make_exec_charts

ROOT = Path(__file__).resolve().parent
INK = (0x1C, 0x19, 0x17)
MUTED = (0x57, 0x53, 0x4E)
PAPER = "FAF7F2"
PEACH = "F6E4D4"
CREAM = "F8F1E3"
YELLOW = "F3E6C0"
ORANGE = "F0C9A0"
WHITE = "FFFFFF"


def _shade(cell, hex_color: str) -> None:
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), hex_color)
    shd.set(qn("w:val"), "clear")
    tcPr.append(shd)


def _run(run, size=11, bold=False, color=None, name="Calibri"):
    run.font.size = Pt(float(size))
    run.font.bold = bold
    run.font.name = name
    if color:
        run.font.color.rgb = RGBColor(*color)


def _tight(p, after=4, before=0):
    pf = p.paragraph_format
    pf.space_after = Pt(after)
    pf.space_before = Pt(before)
    pf.line_spacing_rule = WD_LINE_SPACING.SINGLE


def _set_doc_bg(doc, hex_color: str = PAPER) -> None:
    background = OxmlElement("w:background")
    background.set(qn("w:color"), hex_color)
    doc.element.insert(0, background)
    display = OxmlElement("w:displayBackgroundShape")
    doc.settings.element.append(display)


def _bar(doc, text: str, fill: str, color=INK, size=12) -> None:
    t = doc.add_table(rows=1, cols=1)
    t.autofit = True
    cell = t.cell(0, 0)
    _shade(cell, fill)
    p = cell.paragraphs[0]
    _tight(p, 4, 4)
    r = p.add_run(text)
    _run(r, size, True, color)
    sp = doc.add_paragraph()
    _tight(sp, 4, 0)


def _para(doc, text, size=11, bold=False, color=INK, after=6):
    p = doc.add_paragraph()
    _tight(p, after)
    r = p.add_run(text)
    _run(r, size, bold, color)
    return p


def _set_widths(table, inches):
    for row in table.rows:
        for i, w in enumerate(inches):
            row.cells[i].width = Inches(w)


def build_memo() -> Path:
    make_exec_charts.main()
    doc = Document()
    _set_doc_bg(doc, PAPER)
    section = doc.sections[0]
    section.page_width = Inches(8.5)
    section.page_height = Inches(11)
    section.top_margin = Inches(0.55)
    section.bottom_margin = Inches(0.55)
    section.left_margin = Inches(0.7)
    section.right_margin = Inches(0.7)

    _bar(
        doc,
        "RAPIDO  ·  MEMO TO THE HEAD OF SUPPLY  ·  Ramanathan K R  ·  10 Sep 2026  ·  extract 30 Jun 2026, 23:59 IST",
        YELLOW,
        INK,
        11,
    )

    h = doc.add_paragraph()
    _tight(h, 8)
    r = h.add_run("Ship ~50 extra approved captains this week. Do not bank ~180.")
    _run(r, 17, True, INK, "Cambria")

    _para(
        doc,
        "The number I will put my name on this week is ~46–52 extra approved / month from Insurance "
        "capture UX (C1b). It needs engineering, not Legal. A 10-day RC grace (C1a) is ~134/month only "
        "if Legal treats deferred RC as activation and captains show up — show-up is unobserved. If remaining "
        "docs still bind after RC, that path is ~36/month. 98.7% of mature approved already take a first trip "
        "(3,895 / 3,946) — documents are the bottleneck, not first-order. CAMP_WA_002 is 0 pp, not 5×. "
        "Airport: do not hire; price the night at ₹35.4 / unpaid suburban leg.",
        11.5,
        False,
        INK,
        8,
    )

    pics = doc.add_paragraph()
    pics.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _tight(pics, 4)
    for fname in ("pie_c1.png", "pie_airport_night.png"):
        pth = ROOT / "figures" / fname
        if pth.exists():
            pics.add_run().add_picture(str(pth), width=Inches(3.25))
            pics.add_run("  ")
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _tight(cap, 8)
    r = cap.add_run("Left: C1a vs C1b if Legal says yes — not this week’s bank. Right: 84% of airport unfulfilled is 21:00–03:59.")
    _run(r, 10.5, False, MUTED)

    _bar(doc, "PAGE 1  ·  WHAT TO DO THIS WEEK", ORANGE, INK, 12)

    tbl = doc.add_table(rows=4, cols=5)
    tbl.style = "Table Grid"
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["#", "Do this", "Impact", "Cost / risk", "Watch"]
    data = [
        [
            "1",
            "C1b Insurance camera this week (411). Same camera on other docs: measure, not in the bank. Legal scoping on C1a RC grace (1,637) in parallel — do not add ~134 until they say yes.",
            "~50/mo now. +~134 only if Legal; else ~36.",
            "C1b: engineering. C1a: Legal/T&S. Show-up unobserved. FTE ₹40–60k assumed.",
            "Approved by cohort",
        ],
        [
            "2",
            "Airport Return Assurance at ₹35.4 / unpaid night-suburban leg. Do not hire the catchment.",
            "Sample ~₹69–103k/mo. Restores rest-suburban net.",
            "Sampled trips ≠ city P&L. Not city-core.",
            "Return-in-20m, cancels, falling 4-wk run-rate",
        ],
        [
            "3",
            "Kill CAMP_WA_002 5×. Send/no-send RCT on RC-cleared app/paid captains, no other campaign.",
            "0 pp lift. Cost avoided + 4–6 week answer.",
            "Near zero",
            "Aadhaar pass and approved",
        ],
    ]
    for i, htxt in enumerate(headers):
        cell = tbl.rows[0].cells[i]
        _shade(cell, ORANGE)
        r = cell.paragraphs[0].add_run(htxt)
        _run(r, 10.5, True, INK)
        _tight(cell.paragraphs[0], 3, 3)
    for ri, row in enumerate(data):
        for ci, val in enumerate(row):
            cell = tbl.rows[ri + 1].cells[ci]
            _shade(cell, PEACH if ri % 2 == 0 else CREAM)
            p = cell.paragraphs[0]
            _tight(p, 4, 3)
            r = p.add_run(val)
            _run(r, 10, ci == 0, INK)
    _set_widths(tbl, [0.4, 2.5, 1.55, 1.7, 1.5])

    sp = doc.add_paragraph()
    _tight(sp, 8)

    why = doc.add_table(rows=1, cols=2)
    _set_widths(why, [3.5, 3.55])
    left, right = why.cell(0, 0), why.cell(0, 1)
    _shade(left, PEACH)
    _shade(right, CREAM)
    p = left.paragraphs[0]
    r = p.add_run("Why rec 2 is “do not hire”\n")
    _run(r, 12, True, INK)
    r = p.add_run(
        "Terminals ~40% unfulfilled vs ~3% elsewhere. After the trip, suburban backhaul and overnight "
        "return-collapse compound. Mix does not shift after dark (χ² p=0.12). New hires inherit both "
        "penalties. Price the deadhead for 4 weeks; hire only if the payout run-rate is not falling."
    )
    _run(r, 10.5, False, INK)
    p = right.paragraphs[0]
    r = p.add_run("Why rec 3 is a hard no on 5×\n")
    _run(r, 12, True, INK)
    r = p.add_run(
        "Clicked vs not (delivered): −1.5pp, CI −3.6 to +0.6 → 0 pp. The 29% vs 11% “got CAMP” gap "
        "is targeting after RC, not lift. That same null is why never-upload is not another WhatsApp. "
        "Redirect the paper into a send/no-send RCT this week."
    )
    _run(r, 10.5, False, INK)

    _bar(
        doc,
        "PAGE 2  ·  WHY THESE TWO STAGES, WHAT WE LEFT, WHAT WOULD CHANGE MY MIND",
        YELLOW,
        INK,
        12,
    )

    _para(
        doc,
        "The deck shows the leaks. This page is the bound: C1b is unconditional; C1a is a Legal scenario; "
        "₹35.4 is derived; these piles are not added to ~50. RC loses 5,405 — only 1,637 failed solely on "
        "blur / OCR / illegible. Insurance loses 3,289; ~2,530 never uploaded after Fitness. C1b is the 411 "
        "photo fails and cannot defer (liability). DL (1,166) is 100% uploaded-fail and cannot be deferred. "
        "Aadhaar / Permit / Fitness (1,540 / 2,616 / 2,653) are mostly never-upload or eligibility. Rejected 409 "
        "already cleared docs — a gate.",
        11,
        False,
        INK,
        6,
    )

    pics2 = doc.add_paragraph()
    pics2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _tight(pics2, 4)
    for fname in ("pie_rc_capture.png", "pie_c1b.png"):
        pth = ROOT / "figures" / fname
        if pth.exists():
            pics2.add_run().add_picture(str(pth), width=Inches(2.9))
            pics2.add_run("  ")
    cap2 = doc.add_paragraph()
    cap2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _tight(cap2, 4)
    r = cap2.add_run("Left: 1,637 of 5,405 RC losses are C1a. Right: 411 of 3,289 Insurance leftovers are C1b.")
    _run(r, 10.5, False, MUTED)

    bar = ROOT / "figures" / "bar_volume_lost.png"
    if bar.exists():
        bp = doc.add_paragraph()
        bp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        _tight(bp, 4)
        bp.add_run().add_picture(str(bar), width=Inches(5.8))

    maths = doc.add_table(rows=3, cols=4)
    maths.style = "Table Grid"
    maths.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, htxt in enumerate(["Fix", "Flow", "Maths", "What I bank"]):
        cell = maths.rows[0].cells[i]
        _shade(cell, YELLOW)
        r = cell.paragraphs[0].add_run(htxt)
        _run(r, 11, True, INK)
        _tight(cell.paragraphs[0], 3, 3)
    rows_m = [
        ["C1b Insurance UX", "411 capture-only", "67→76% × 91% approved-if-cleared", "~50/mo — yes"],
        ["C1a RC grace", "~300/mo capture-only", "× 60% show-up × 74% pass", "~134 if Legal; ~36 if not"],
    ]
    for ri, row in enumerate(rows_m):
        for ci, val in enumerate(row):
            cell = maths.rows[ri + 1].cells[ci]
            _shade(cell, CREAM)
            p = cell.paragraphs[0]
            _tight(p, 3, 2)
            r = p.add_run(val)
            _run(r, 10.5, ci == 3, INK)
    _set_widths(maths, [1.8, 1.9, 2.3, 1.1])

    _para(
        doc,
        "40–80% show-up → C1a ~89–188. I would not put 180 in a deck with my name on it until Legal answers.",
        11,
        False,
        INK,
        6,
    )

    close = doc.add_table(rows=2, cols=3)
    close.style = "Table Grid"
    close.alignment = WD_TABLE_ALIGNMENT.CENTER
    heads = [
        ("NOT BANKED", ORANGE),
        ("ARA (not 30% of fare)", YELLOW),
        ("ASSUMPTIONS / WHAT WOULD CHANGE IT", PEACH),
    ]
    bodies = [
        "Other-doc camera after C1b: measure, not +50. Never-upload RC ~2,388 / Insurance ~2,530: assist RCT, not WhatsApp (CAMP 0 pp). Overlaps 726 C1a. Paid never-starts 11.5% vs fos ~1% — no CAC, not sized.",
        "Gap ₹31.6 (₹24.9 vs ₹56.5) ÷ 0.8931 eligible ≈ ₹35.4/leg. 80/100/120% → ~₹69–103k sample. ₹105 (30% of fare) overpays. City-core ₹104.7 is geography.",
        "~15.6-day cutoff (eligible pool is a floor, not a bank). doc_events, not docs_cleared. Field gap not banked. C1a 60% show-up unobserved — if Legal says no, bank C1b only. Re-derive ₹35.4 if night returns rise. C1a FTE ₹40–60k assumed. No CAC. Trips sampled. signup_zone_id ≠ airport zones.",
    ]
    for i, (htxt, fill) in enumerate(heads):
        cell = close.rows[0].cells[i]
        _shade(cell, fill)
        p = cell.paragraphs[0]
        _tight(p, 3, 3)
        r = p.add_run(htxt)
        _run(r, 10.5, True, INK)
    for i, txt in enumerate(bodies):
        cell = close.rows[1].cells[i]
        _shade(cell, WHITE)
        p = cell.paragraphs[0]
        _tight(p, 3, 3)
        r = p.add_run(txt)
        _run(r, 10, False, INK)
    _set_widths(close, [2.4, 2.4, 2.4])

    out = ROOT / "MEMO.docx"
    doc.save(out)
    print(f"wrote {out}")
    return out


if __name__ == "__main__":
    build_memo()
