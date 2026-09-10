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


def build_memo() -> Path:
    md = (ROOT / "MEMO.md").read_text()
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Inches(0.7)
    section.bottom_margin = Inches(0.7)
    section.left_margin = Inches(0.85)
    section.right_margin = Inches(0.85)

    for raw in md.splitlines():
        line = raw.rstrip()
        if not line:
            continue
        if line.startswith("# "):
            p = doc.add_paragraph()
            r = p.add_run(line[2:])
            r.bold = True
            r.font.size = Pt(16)
            r.font.color.rgb = RGBColor(0x1F, 0x3A, 0x5F)
        elif line.startswith("## "):
            p = doc.add_paragraph()
            r = p.add_run(line[3:])
            r.bold = True
            r.font.size = Pt(13)
            r.font.color.rgb = RGBColor(0xC4, 0x5C, 0x26)
        elif line.startswith("### "):
            p = doc.add_paragraph()
            r = p.add_run(line[4:])
            r.bold = True
            r.font.size = Pt(12)
        elif line.startswith("|") and "---" not in line:
            # skip markdown tables as tables — collect later; simple paragraph
            p = doc.add_paragraph(line.strip("|").replace("|", " · "))
            p.runs[0].font.size = Pt(9) if p.runs else None
        elif line.startswith("|---"):
            continue
        elif line.startswith("- "):
            p = doc.add_paragraph(line[2:], style="List Bullet")
        elif line.startswith("---"):
            continue
        else:
            p = doc.add_paragraph()
            # very light **bold** handling
            text = line
            while "**" in text:
                pre, rest = text.split("**", 1)
                if pre:
                    p.add_run(pre)
                if "**" not in rest:
                    p.add_run(rest)
                    text = ""
                    break
                bold, text = rest.split("**", 1)
                r = p.add_run(bold)
                r.bold = True
            if text:
                p.add_run(text)
            for r in p.runs:
                r.font.size = Pt(10.5)
                r.font.name = "Calibri"
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
    build_deck()


if __name__ == "__main__":
    main()
