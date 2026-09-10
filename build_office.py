#!/usr/bin/env python3
"""Build MEMO.docx and DECK.pptx from MEMO.md + waterfall figure."""

from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.shared import Inches, Pt, RGBColor
from pptx import Presentation
from pptx.dml.color import RGBColor as PptRGB
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches as PptInches, Pt as PptPt

ROOT = Path(__file__).resolve().parent
NAVY = PptRGB(0x1F, 0x3A, 0x5F)
ORANGE = PptRGB(0xC4, 0x5C, 0x26)
CREAM = PptRGB(0xF7, 0xF4, 0xEE)


from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
import subprocess
import sys

import make_exec_charts


def _shade(cell, hex_color: str) -> None:
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), hex_color)
    shd.set(qn("w:val"), "clear")
    tcPr.append(shd)


def _set_run(run, size=11, bold=False, color=None, name="Calibri"):
    run.font.size = Pt(float(size))
    run.font.bold = bold
    run.font.name = name
    if color:
        run.font.color.rgb = RGBColor(*color)


def build_memo() -> Path:
    make_exec_charts.main()
    doc = Document()
    section = doc.sections[0]
    section.page_width = Inches(8.5)
    section.page_height = Inches(11)
    section.top_margin = Inches(0.55)
    section.bottom_margin = Inches(0.55)
    section.left_margin = Inches(0.7)
    section.right_margin = Inches(0.7)

    banner = doc.add_table(rows=1, cols=1)
    banner.autofit = True
    cell = banner.cell(0, 0)
    _shade(cell, "CADCFC")
    p = cell.paragraphs[0]
    r = p.add_run("RAPIDO  ·  MEMO TO THE HEAD OF SUPPLY")
    _set_run(r, 10, True, (0x1E, 0x27, 0x61))
    p2 = cell.add_paragraph()
    r2 = p2.add_run("Onboarding leak and overnight airport  ·  10 Sep 2026  ·  extract 30 Jun 2026, 23:59 IST")
    _set_run(r2, 9, False, (0x1C, 0x72, 0x93))

    h = doc.add_paragraph()
    r = h.add_run("~180 more approved captains a month — two photo fixes, not five programmes")
    _set_run(r, 16, True, (0x1E, 0x27, 0x61), "Cambria")

    lead = doc.add_paragraph()
    r = lead.add_run(
        "Central case is about 134 from a 10-day RC in-person grace (C1a) and ~50 from Insurance "
        "upload UX (C1b). The groups do not overlap. 98.7% of mature approved captains already take a "
        "first trip (3,895 / 3,946) — documents are the bottleneck. Show-up for RC is unobserved; if Legal "
        "will not treat deferred RC as activation, C1a shrinks toward ~36/month."
    )
    _set_run(r, 10.5, False, (0x33, 0x33, 0x33))

    pics = doc.add_paragraph()
    pics.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for fname in ("pie_c1.png", "pie_airport_night.png"):
        pth = ROOT / "figures" / fname
        if pth.exists():
            pics.add_run().add_picture(str(pth), width=Inches(3.15))
            pics.add_run("  ")

    cap = doc.add_paragraph()
    r = cap.add_run(
        "Left: bank only C1a + C1b (~180). Right: 84% of airport unfulfilled volume sits in 21:00–03:59."
    )
    _set_run(r, 8.5, False, (0x8A, 0x8F, 0xA3))
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER

    sub = doc.add_paragraph()
    r = sub.add_run("What to do this week")
    _set_run(r, 13, True, (0x1C, 0x72, 0x93), "Cambria")

    tbl = doc.add_table(rows=4, cols=4)
    tbl.style = "Table Grid"
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["#", "Do this", "Impact", "Watch"]
    data = [
        [
            "1",
            "C1b Insurance camera this week, then C1a 10-day RC grace after Legal (1,637 + 411 capture-only). Same camera on other docs is a free rider — not added to 180.",
            "~180/mo (~50 + ~134). C1a ops ~1 FTE ₹40–60k assumed.",
            "Approved by cohort",
        ],
        [
            "2",
            "Airport Return Assurance at ₹35.4 per unpaid night-suburban leg. Do not hire the catchment.",
            "Sample ~₹69–103k/mo. Restores rest-of-day suburban net, not city-core.",
            "Return-in-20m, cancels, falling 4-week payout run-rate",
        ],
        [
            "3",
            "Stop CAMP_WA_002 5×. Send/no-send RCT on RC-cleared app/paid captains, no other campaign.",
            "0 pp click lift. Cost avoided + answer in 4–6 weeks.",
            "Aadhaar pass and approved",
        ],
    ]
    for i, htxt in enumerate(headers):
        cell = tbl.rows[0].cells[i]
        _shade(cell, "1E2761")
        p = cell.paragraphs[0]
        r = p.add_run(htxt)
        _set_run(r, 9, True, (0xFF, 0xFF, 0xFF))
    for ri, row in enumerate(data):
        for ci, val in enumerate(row):
            cell = tbl.rows[ri + 1].cells[ci]
            _shade(cell, "F7F8FC" if ri % 2 == 0 else "FFFFFF")
            p = cell.paragraphs[0]
            r = p.add_run(val)
            _set_run(r, 8.5, ci == 0, (0x1E, 0x27, 0x61) if ci == 0 else (0x33, 0x33, 0x33))

    p = doc.add_paragraph()
    r = p.add_run(
        "Stop scaling CAMP_WA_002. Clicked vs not is −1.5pp (CI −3.6 to +0.6) → 0 pp. The 29% vs 11% "
        "recipient gap is targeting after RC. That same null is why never-upload is not another WhatsApp."
    )
    _set_run(r, 10.5)

    p = doc.add_paragraph()
    r = p.add_run("Why these two stages — leftover queue — ARA maths")
    _set_run(r, 13, True, (0x1C, 0x72, 0x93), "Cambria")

    pics2 = doc.add_paragraph()
    pics2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for fname in ("pie_rc_capture.png", "pie_c1b.png"):
        pth = ROOT / "figures" / fname
        if pth.exists():
            pics2.add_run().add_picture(str(pth), width=Inches(3.15))
            pics2.add_run("  ")
    cap2 = doc.add_paragraph()
    r = cap2.add_run(
        "Left: only 1,637 of 5,405 RC losses are C1a. Right: only 411 of 3,289 Insurance leftovers are C1b."
    )
    _set_run(r, 8.5, False, (0x8A, 0x8F, 0xA3))
    cap2.alignment = WD_ALIGN_PARAGRAPH.CENTER

    if (ROOT / "figures" / "bar_volume_lost.png").exists():
        bp = doc.add_paragraph()
        bp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        bp.add_run().add_picture(str(ROOT / "figures" / "bar_volume_lost.png"), width=Inches(6.1))

    p = doc.add_paragraph()
    r = p.add_run(
        "RC loses 5,405; only 1,637 are capture-only (C1a). Insurance loses 3,289 but ~2,530 never uploaded "
        "after Fitness — C1b is the 411 photo fails. DL cannot be deferred. Mix does not shift overnight "
        "(χ² p=0.12). ARA: gap ₹31.6 ÷ 0.8931 eligible share ≈ ₹35.4/leg. 30% of fare (₹105) overpays."
    )
    _set_run(r, 10.5)

    p = doc.add_paragraph()
    r = p.add_run("What I assumed, and what would change my answer. ")
    _set_run(r, 11, True, (0x1E, 0x27, 0x61))
    r = p.add_run(
        "~15.6-day cutoff; doc_events not approvals.docs_cleared; field gap not banked; ARA vs rest-suburban "
        "not city-core; C1a FTE ₹40–60k assumed; trips file is sampled so ₹/month is not a city P&L."
    )
    _set_run(r, 10)

    out = ROOT / "MEMO.docx"
    doc.save(out)
    print(f"wrote {out}")
    return out


def _bg(slide, rgb):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = rgb


def _textbox(slide, l, t, w, h, text, size=18, bold=False, color=NAVY, align=PP_ALIGN.LEFT):
    box = slide.shapes.add_textbox(PptInches(l), PptInches(t), PptInches(w), PptInches(h))
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = PptPt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = "Calibri"
    return tf


def build_deck() -> Path:
    prs = Presentation()
    prs.slide_width = PptInches(13.333)
    prs.slide_height = PptInches(7.5)
    blank = prs.slide_layouts[6]
    chart = ROOT / "figures" / "funnel_waterfall.png"

    # 1
    s = prs.slides.add_slide(blank)
    _bg(s, CREAM)
    _textbox(s, 0.45, 0.22, 12, 0.3, "1 / 6  ·  HEADLINE", 11, True, ORANGE)
    _textbox(
        s,
        0.45,
        0.5,
        12.4,
        1.15,
        "About 180 more approved captains a month\nmedium confidence — ~134 RC grace + ~50 Insurance UX",
        26,
        True,
        NAVY,
    )
    if chart.exists():
        s.shapes.add_picture(str(chart), PptInches(0.35), PptInches(1.75), width=PptInches(12.6))
    _textbox(
        s,
        0.45,
        7.05,
        12.4,
        0.3,
        "Do not add 128–256 field conversion — 726 of C1a are the same people.  98.7% of approved take a first trip.",
        11,
        False,
        PptRGB(0x44, 0x44, 0x44),
    )

    # 2
    s = prs.slides.add_slide(blank)
    _bg(s, CREAM)
    _textbox(s, 0.45, 0.22, 12, 0.3, "2 / 6  ·  ROOT CAUSE", 11, True, ORANGE)
    _textbox(s, 0.45, 0.5, 12.4, 0.8, "RC and Insurance are failing as photos, not eligibility", 26, True, NAVY)
    _textbox(
        s,
        0.45,
        1.5,
        6.2,
        5.2,
        "RC: 1,637 uploaded, never passed, only blur / weak OCR / not legible.\n\n"
        "Insurance: 411, same definition. ~2,530 never uploaded after Fitness — C1b does not claim that pile.\n\n"
        "Other stages: real loss, wrong tool. DL cannot defer. Aadhaar/Permit/Fitness mostly never-upload or eligibility.\n\n"
        "Later attempts pass HIGHER. Capture/UX — not harder remainder.",
        16,
        False,
        NAVY,
    )
    _textbox(
        s,
        6.9,
        1.5,
        5.8,
        5.2,
        "Pass by attempt\n\nRC          65.3% → 68.4% → 74.1%\nInsurance   67.4% → 73.8% → 76.4%\n\n"
        "Reuse the same camera on other docs after C1b — free rider, not in the 180.\n\n"
        "Never-upload is not another WhatsApp (CAMP = 0pp). Next: assist RCT.",
        16,
        False,
        NAVY,
    )

    # 3
    s = prs.slides.add_slide(blank)
    _bg(s, CREAM)
    _textbox(s, 0.45, 0.22, 12, 0.3, "3 / 6  ·  THE FIX", 11, True, ORANGE)
    _textbox(s, 0.45, 0.5, 12.4, 0.7, "C1a defers RC. DL and Insurance still gate.", 26, True, NAVY)
    _textbox(
        s,
        0.45,
        1.4,
        6.2,
        5.5,
        "C1a — 10-day in-person RC\n1,637 people (~300/month).\n60% show-up × 74% pass → ~134/month.\nShow-up unobserved (40–80% → ~89–188).\nLegal/T&S required.\nIf remaining docs still bind, P(approved|RC)=27% → ~36/month.\nOps: ~180 visits/month ≈ 1 FTE, ₹40–60k (assumed).",
        15,
        False,
        NAVY,
    )
    _textbox(
        s,
        6.9,
        1.4,
        5.8,
        5.5,
        "C1b — Insurance camera UX\n411 people. Must clear before first ride.\n67→74→76% × 91% approved-if-cleared\n→ ~46–52/month.\nNo deferral sign-off. Ship this week.\n\nThen: same UX on DL/Aadhaar/Permit/Fitness — measure, do not add to 180.\nR2A: 98.7% of approved take a first order.",
        15,
        False,
        NAVY,
    )

    # 4
    s = prs.slides.add_slide(blank)
    _bg(s, CREAM)
    _textbox(s, 0.45, 0.22, 12, 0.3, "4 / 6  ·  AIRPORT", 11, True, ORANGE)
    _textbox(s, 0.45, 0.5, 12.4, 0.8, "Nights + compounding economics. Not hire-near-the-airport.", 24, True, NAVY)
    _textbox(
        s,
        0.45,
        1.5,
        6.2,
        5.4,
        "Airport unfulfilled 40% vs ~3% elsewhere. 84% of pain is 21:00–03:59. ~13 captains online vs ~37 by day.\n\n"
        "Suburban cancel 24% vs city-core 12%. Overnight return-in-20m: 10.7% vs 47%.\n"
        "Mix does NOT shift overnight — two independent penalties.\n\n"
        "Net ₹/cycle: worst×sub ₹24.9 vs rest×sub ₹56.5 vs worst×core ₹104.7.",
        15,
        False,
        NAVY,
    )
    _textbox(
        s,
        6.9,
        1.5,
        5.8,
        5.4,
        "ARA payout — derived, not % of fare\n\n"
        "₹31.6 population gap ÷ 0.8931 eligible share\n= ₹35.4 / unpaid night-suburban leg.\n\n"
        "80/100/120% → ₹28.3 / 35.4 / 42.5\nsample ~₹69k / ₹86k / ₹103k a month.\n\n"
        "30% of ₹350 fare (₹105) overpays.\nTarget rest-suburban, not city-core.\nNo blanket hiring.",
        15,
        False,
        NAVY,
    )

    # 5
    s = prs.slides.add_slide(blank)
    _bg(s, CREAM)
    _textbox(s, 0.45, 0.22, 12, 0.3, "5 / 6  ·  WHAT DOES NOT WORK", 11, True, ORANGE)
    _textbox(s, 0.45, 0.5, 12.4, 0.7, "A 0pp WhatsApp, and a field gap we must not bank", 26, True, NAVY)
    _textbox(
        s,
        0.45,
        1.4,
        12.4,
        5.5,
        "Got CAMP_WA_002 vs never got it: ~29% vs ~11%  →  TARGETING (sent after RC).\n"
        "Clicked vs not, delivered: −1.5pp  →  0 pp lift. Do not scale 5×. Do not use WhatsApp to harvest never-uploads.\n\n"
        "Never-upload is the leftover (RC ~2,388; Insurance ~2,530). Fos Insurance abandon 26% vs paid 43%.\n"
        "Field vs app 128–256/month IF zero selection. 726 of C1a already inside. Do not add to ~180.\n"
        "Test: randomised assist on app/paid (~900/arm for 5pp approval lift).",
        16,
        False,
        NAVY,
    )

    # 6
    s = prs.slides.add_slide(blank)
    _bg(s, CREAM)
    _textbox(s, 0.45, 0.22, 12, 0.3, "6 / 6  ·  ASK OF THE ROOM", 11, True, ORANGE)
    _textbox(s, 0.45, 0.5, 12.4, 0.7, "Ranked by monthly impact. Campaign is the fastest yes.", 24, True, NAVY)
    _textbox(
        s,
        0.45,
        1.4,
        12.4,
        5.5,
        "1  C1b camera UX this week + C1a RC grace after Legal     ~180/mo (~50+~134). Reuse camera on other docs: not in the 180.\n\n"
        "2  ARA ₹35.4/eligible leg — DO NOT HIRE THE AIRPORT     sample ~₹69–103k/mo. Two independent penalties; mix does not shift overnight.\n"
        "    4-week pilot: returns up, cancels down, run-rate FALLING. Hire only if nights stay unfilled after that.\n\n"
        "3  Stop 5× CAMP_WA_002; send/no-send RCT     cost avoided + 4–6 week answer. This week.\n\n"
        "Do not: WhatsApp for never-uploads · blanket airport hiring · bank 128–256 · ARA at 30% of fare.\n"
        "Queue: other-doc camera → assist RCT.",
        16,
        False,
        NAVY,
    )

    out = ROOT / "DECK.pptx"
    prs.save(out)
    print(f"wrote {out}")
    return out


def main() -> None:
    build_memo()
    subprocess.check_call(["node", str(ROOT / "generate_deck.js")], cwd=str(ROOT))
    print("wrote DECK.pptx via generate_deck.js")


if __name__ == "__main__":
    main()
