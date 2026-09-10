#!/usr/bin/env python3
"""Two-page Word memo: yellow / orange / red, pies, ranked ask, memo-only depth."""

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
NAVY = (0x1E, 0x27, 0x61)
INK = (0x3A, 0x22, 0x08)
WHITE = (0xFF, 0xFF, 0xFF)
YELLOW = "FFC400"
ORANGE = "FF8A3D"
RED = "E85D4C"
PEACH = "FFE8C2"
CREAM = "FFF6E8"


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


def _set_doc_bg(doc, hex_color: str = "FFE8C2") -> None:
    background = OxmlElement("w:background")
    background.set(qn("w:color"), hex_color)
    doc.element.insert(0, background)
    display = OxmlElement("w:displayBackgroundShape")
    doc.settings.element.append(display)


def _bar(doc, text: str, fill: str, color=NAVY, size=11) -> None:
    t = doc.add_table(rows=1, cols=1)
    t.autofit = True
    cell = t.cell(0, 0)
    _shade(cell, fill)
    p = cell.paragraphs[0]
    _tight(p, 2, 2)
    r = p.add_run(text)
    _run(r, size, True, color)
    sp = doc.add_paragraph()
    _tight(sp, 4, 0)


def _para(doc, text, size=10.5, bold=False, color=INK, after=6):
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
    _set_doc_bg(doc, "FFE8C2")
    section = doc.sections[0]
    section.page_width = Inches(8.5)
    section.page_height = Inches(11)
    section.top_margin = Inches(0.5)
    section.bottom_margin = Inches(0.5)
    section.left_margin = Inches(0.65)
    section.right_margin = Inches(0.65)

    # ── Page 1 ────────────────────────────────────────────────────────────
    _bar(doc, "RAPIDO  ·  MEMO TO THE HEAD OF SUPPLY  ·  Ramanathan K R  ·  10 Sep 2026  ·  extract 30 Jun 2026, 23:59 IST",
         YELLOW, NAVY, 10)

    h = doc.add_paragraph()
    _tight(h, 6)
    r = h.add_run("~180 more approved captains a month — two photo fixes, not five programmes")
    _run(r, 16, True, NAVY, "Cambria")

    _para(
        doc,
        "Bank only two disjoint capture fixes: ~134/month from a 10-day in-person RC grace (C1a) and "
        "~50 from Insurance upload UX (C1b). 98.7% of mature approved captains already take a first trip "
        "(3,895 / 3,946) — documents are the bottleneck, not first-order. Show-up for RC is unobserved; "
        "if Legal will not treat deferred RC as activation, C1a shrinks toward ~36/month. That is the "
        "only number I would put in a deck with my name on the campaign: 0 pp, not 5×.",
        10.5, False, INK, 6,
    )

    pics = doc.add_paragraph()
    pics.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _tight(pics, 2)
    for fname in ("pie_c1.png", "pie_airport_night.png"):
        pth = ROOT / "figures" / fname
        if pth.exists():
            pics.add_run().add_picture(str(pth), width=Inches(3.35))
            pics.add_run("  ")
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _tight(cap, 8)
    r = cap.add_run("Left: bank C1a + C1b only. Right: 84% of airport unfulfilled volume is 21:00–03:59.")
    _run(r, 8.5, False, (0x6B, 0x4A, 0x2A))

    _bar(doc, "PAGE 1  ·  WHAT TO DO THIS WEEK", ORANGE, WHITE, 11)

    tbl = doc.add_table(rows=4, cols=5)
    tbl.style = "Table Grid"
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["#", "Do this", "Impact", "Cost / risk", "Watch"]
    data = [
        ["1", "C1b Insurance camera this week (411). Then C1a 10-day RC grace after Legal (1,637). Same camera on other docs: free rider, not in 180.",
         "~180/mo (~50 + ~134)", "C1b: engineering. C1a: Legal/T&S + ~1 FTE ₹40–60k (assumed).", "Approved by cohort"],
        ["2", "Airport Return Assurance at ₹35.4 / unpaid night-suburban leg. Do not hire the catchment.",
         "Sample ~₹69–103k/mo. Restores rest-suburban net.", "Sampled trips ≠ city P&L. Not city-core.", "Return-in-20m, cancels, falling 4-wk run-rate"],
        ["3", "Kill CAMP_WA_002 5×. Send/no-send RCT on RC-cleared app/paid captains, no other campaign.",
         "0 pp lift. Cost avoided + 4–6 week answer.", "Near zero", "Aadhaar pass and approved"],
    ]
    for i, htxt in enumerate(headers):
        cell = tbl.rows[0].cells[i]
        _shade(cell, RED)
        r = cell.paragraphs[0].add_run(htxt)
        _run(r, 8.5, True, WHITE)
        _tight(cell.paragraphs[0], 2, 2)
    for ri, row in enumerate(data):
        for ci, val in enumerate(row):
            cell = tbl.rows[ri + 1].cells[ci]
            _shade(cell, PEACH if ri % 2 == 0 else CREAM)
            p = cell.paragraphs[0]
            _tight(p, 3, 2)
            r = p.add_run(val)
            _run(r, 8, ci == 0, NAVY if ci == 0 else INK)
    _set_widths(tbl, [0.4, 2.55, 1.55, 1.7, 1.5])

    sp = doc.add_paragraph()
    _tight(sp, 6)

    why = doc.add_table(rows=1, cols=2)
    _set_widths(why, [3.55, 3.55])
    left, right = why.cell(0, 0), why.cell(0, 1)
    _shade(left, ORANGE)
    _shade(right, RED)
    p = left.paragraphs[0]
    r = p.add_run("Why rec 2 is “do not hire”\n")
    _run(r, 10, True, WHITE)
    r = p.add_run(
        "Terminals ~40% unfulfilled vs ~3% elsewhere. After the trip, suburban backhaul and overnight "
        "return-collapse compound. Mix does not shift after dark (χ² p=0.12). New hires inherit both "
        "penalties. Price the deadhead for 4 weeks; hire only if the payout run-rate is not falling."
    )
    _run(r, 9, False, WHITE)
    p = right.paragraphs[0]
    r = p.add_run("Why rec 3 is a hard no on 5×\n")
    _run(r, 10, True, WHITE)
    r = p.add_run(
        "Clicked vs not (delivered): −1.5pp, CI −3.6 to +0.6 → 0 pp. The 29% vs 11% “got CAMP” gap "
        "is targeting after RC, not lift. That same null is why never-upload is not another WhatsApp. "
        "Redirect the paper into a send/no-send RCT this week."
    )
    _run(r, 9, False, WHITE)

    # ── Page 2 ────────────────────────────────────────────────────────────
    _bar(doc, "PAGE 2  ·  WHY THESE TWO STAGES, WHAT WE LEFT, WHAT WOULD CHANGE MY MIND", ORANGE, WHITE, 11)

    _para(
        doc,
        "The deck shows the leaks. This page is the bound: what is C1a vs leftover, how ₹35.4 is derived, "
        "and which piles I refuse to add to 180. RC loses 5,405 people — largest stage — but only 1,637 "
        "failed solely on blur / OCR / illegible. Insurance loses 3,289; ~2,530 never uploaded after Fitness. "
        "C1b is the 411 photo fails and cannot defer (liability). DL (1,166) is 100% uploaded-fail and "
        "cannot be deferred. Aadhaar / Permit / Fitness (1,540 / 2,616 / 2,653) are mostly never-upload or "
        "eligibility. Rejected 409 already cleared docs — a gate, not a UX leak.",
        10.5, False, INK, 6,
    )

    pics2 = doc.add_paragraph()
    pics2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _tight(pics2, 2)
    for fname in ("pie_rc_capture.png", "pie_c1b.png"):
        pth = ROOT / "figures" / fname
        if pth.exists():
            pics2.add_run().add_picture(str(pth), width=Inches(3.25))
            pics2.add_run("  ")
    cap2 = doc.add_paragraph()
    cap2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _tight(cap2, 6)
    r = cap2.add_run("Left: 1,637 of 5,405 RC losses are C1a. Right: 411 of 3,289 Insurance leftovers are C1b.")
    _run(r, 8.5, False, (0x6B, 0x4A, 0x2A))

    bar = ROOT / "figures" / "bar_volume_lost.png"
    if bar.exists():
        bp = doc.add_paragraph()
        bp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        _tight(bp, 4)
        bp.add_run().add_picture(str(bar), width=Inches(6.5))

    maths = doc.add_table(rows=3, cols=4)
    maths.style = "Table Grid"
    maths.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, htxt in enumerate(["Fix", "Flow", "Maths", "Bank"]):
        cell = maths.rows[0].cells[i]
        _shade(cell, YELLOW)
        r = cell.paragraphs[0].add_run(htxt)
        _run(r, 9, True, NAVY)
    rows_m = [
        ["C1a RC grace", "~300/mo capture-only", "× 60% show-up × 74% pass", "~134/mo"],
        ["C1b Insurance UX", "411 capture-only", "67→76% × 91% approved-if-cleared", "~46–52/mo"],
    ]
    for ri, row in enumerate(rows_m):
        for ci, val in enumerate(row):
            cell = maths.rows[ri + 1].cells[ci]
            _shade(cell, CREAM)
            r = cell.paragraphs[0].add_run(val)
            _run(r, 9, ci == 3, NAVY)
    _set_widths(maths, [1.8, 1.9, 2.3, 1.1])

    _para(
        doc,
        "40–80% show-up → ~89–188. If remaining docs still bind after RC, historical P(approved | passed RC) "
        "is 27% and C1a → ~36/month — that is the Legal question (deferral-as-activation).",
        10, False, INK, 6,
    )

    _bar(doc, "NOT BANKED  ·  leftover queue (possible, not in the 180)", RED, WHITE, 11)
    _para(
        doc,
        "(1) Reuse C1b’s camera on DL / Aadhaar / Permit / Fitness after C1b ships — cheap, capture-only n not "
        "sized except RC/Insurance. (2) Never-upload RC ~2,388 and Insurance ~2,530 looks like a nudge; CAMP was "
        "0 pp and only 13 post-Fitness nudges exist in 7,644 people. Fos abandon after Fitness 26% vs paid 43% — "
        "assisted-onboarding RCT, unproven ceiling 128–256/month, overlaps 726 C1a captains. (3) Paid never-starts "
        "docs at 11.5% vs fos ~1% — channel quality; no CAC, not sized.",
        10.5, False, INK, 6,
    )

    _bar(doc, "ARA  ·  derived payout, not 30% of fare", ORANGE, WHITE, 11)
    _para(
        doc,
        "Night-suburban net ₹24.9 vs rest-suburban ₹56.5 → gap ₹31.6 across all completed worst-suburban trips. "
        "ARA pays only the 89.31% with no return in 20 min → 31.6 / 0.8931 ≈ ₹35.4 per eligible leg. "
        "80 / 100 / 120% → sample ~₹69k / ₹86k / ₹103k a month. 30% of a ₹350 fare (₹105) overpays. "
        "City-core ₹104.7 is geography, not the matching comparison.",
        10.5, False, INK, 6,
    )

    _bar(doc, "WHAT I ASSUMED, AND WHAT WOULD CHANGE MY ANSWER", YELLOW, NAVY, 11)
    _para(
        doc,
        "• ~15.6-day cutoff (max in_progress age). Later capture-fails still in flight → 180 is a floor; they finish alone → slight overstatement.  "
        "• doc_events.verification_pass, not approvals.docs_cleared (they disagree only while unfinished).  "
        "• Field vs app not banked until a randomised assist test on ordinary app/paid signups.  "
        "• ARA matches rest-suburban, not city-core. If night returns rise, re-derive ₹35.4; do not freeze it.  "
        "• C1a ops ₹40–60k assumes one FTE at 12–15 checks/day.  "
        "Unresolved, not omitted: no CAC so field vs paid cannot be priced. airport_trips.csv is sampled — rates hold; ₹/month is not a city budget. signup_zone_id does not join airport zones. Capture-only was counted only on RC and Insurance.",
        10, False, INK, 2,
    )

    out = ROOT / "MEMO.docx"
    doc.save(out)
    print(f"wrote {out}")
    return out


if __name__ == "__main__":
    build_memo()
