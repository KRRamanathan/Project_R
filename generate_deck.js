const pptxgen = require("pptxgenjs");
const fs = require("fs");
const path = require("path");

// Claude-like lights only. Dark ink on cream — no navy/red fills, no white-on-colour.
const PAPER  = "FAF7F2";
const PEACH  = "F6E4D4";
const CREAM  = "F8F1E3";
const YELLOW = "F3E6C0";
const ORANGE = "F0C9A0";
const WHITE  = "FFFFFF";
const INK    = "1C1917";
const MUTED  = "57534E";
const GOLD   = "C45C26";
const LINE   = "E8D5C0";

function png(rel) {
  return "image/png;base64," + fs.readFileSync(path.join(__dirname, rel)).toString("base64");
}

const AUTO   = png("figures/vehicles/auto.png");
const CAB    = png("figures/vehicles/cab.png");
const SCOOTY = png("figures/vehicles/scooty.png");
const BIKE   = png("figures/vehicles/bike.png");
const PIE180 = png("figures/pie_c1.png");
const PIEAIR = png("figures/pie_airport_night.png");
const PIERC  = png("figures/pie_rc_capture.png");
const PIEC1B = png("figures/pie_c1b.png");

const FOOTER_L = "Rapido Supply  ·  Captain onboarding & airport supply";
const FOOTER_R = "Ramanathan K R  ·  Rapido Data Science Assessment";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
const SW = 13.333, SH = 7.5;

function footer(slide, pageNum) {
  slide.addShape("rect", {
    x: 0, y: SH - 0.48, w: SW, h: 0.48,
    fill: { color: PEACH }, line: { type: "none" },
  });
  slide.addText(FOOTER_L, {
    x: 0.55, y: SH - 0.42, w: 7.2, h: 0.32,
    fontFace: "Calibri", fontSize: 11, color: MUTED, align: "left",
    isTextBox: true, margin: 0,
  });
  slide.addText(FOOTER_R + "     " + pageNum + " / 6", {
    x: SW - 6.4, y: SH - 0.42, w: 5.85, h: 0.32,
    fontFace: "Calibri", fontSize: 11, color: MUTED, align: "right",
    isTextBox: true, margin: 0,
  });
}

function kicker(slide, text) {
  slide.addText(text.toUpperCase(), {
    x: 0.6, y: 0.32, w: 10.5, h: 0.32,
    fontFace: "Calibri", fontSize: 13, bold: true,
    color: GOLD, charSpacing: 1.8, align: "left", isTextBox: true, margin: 0,
  });
}

function card(slide, x, y, w, h, fill) {
  slide.addShape("roundRect", {
    x, y, w, h, rectRadius: 0.1,
    fill: { color: fill || WHITE },
    line: { color: LINE, width: 1.25 },
  });
}

function statCard(slide, x, y, w, h, num, label) {
  card(slide, x, y, w, h, WHITE);
  slide.addText(num, {
    x: x + 0.2, y: y + 0.14, w: w - 0.4, h: 0.58,
    fontFace: "Cambria", fontSize: 28, bold: true, color: INK,
    valign: "middle", isTextBox: true, margin: 0,
  });
  slide.addText(label, {
    x: x + 0.2, y: y + 0.72, w: w - 0.4, h: h - 0.86,
    fontFace: "Calibri", fontSize: 13, color: MUTED,
    lineSpacingMultiple: 1.15, isTextBox: true, margin: 0,
  });
}

function addARAChart(slide, x, y, w, h) {
  slide.addChart(pres.ChartType.bar, [{
    name: "₹k / month",
    labels: ["Low (80%)", "Central (100%)", "High (120%)"],
    values: [69, 86, 103],
  }], {
    x, y, w, h,
    barDir: "col",
    barGrouping: "clustered",
    chartColors: [ORANGE, GOLD, YELLOW],
    showLegend: false,
    showValue: true, dataLabelFontSize: 13, dataLabelColor: INK,
    catAxisLabelColor: INK, catAxisLabelFontSize: 12,
    valAxisLabelColor: MUTED, valAxisLabelFontSize: 11,
    valAxisMinVal: 0, valAxisMaxVal: 130,
    valGridLine: { color: LINE, size: 0.5 },
    catGridLine: { style: "none" },
    chartArea: { fill: { color: WHITE } },
    plotAreaBorderColor: WHITE,
  });
}

function addCampaignChart(slide, x, y, w, h) {
  slide.addChart(pres.ChartType.bar, [{
    name: "Completion rate (%)",
    labels: ["Naive: got\ncampaign", "Naive: never\ngot it", "Honest: clicked", "Honest:\nnot clicked"],
    values: [29, 11, 28.3, 29.8],
  }], {
    x, y, w, h,
    barDir: "col",
    barGrouping: "clustered",
    chartColors: [GOLD, PEACH, ORANGE, PEACH],
    showLegend: false,
    showValue: true, dataLabelFontSize: 12, dataLabelColor: INK,
    catAxisLabelColor: INK, catAxisLabelFontSize: 11,
    valAxisLabelColor: MUTED, valAxisLabelFontSize: 11,
    valAxisMinVal: 0, valAxisMaxVal: 40,
    valGridLine: { color: LINE, size: 0.5 },
    catGridLine: { style: "none" },
    chartArea: { fill: { color: WHITE } },
    plotAreaBorderColor: WHITE,
  });
}

// ── Title ────────────────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: PAPER };
  s.addShape("ellipse", { x: 9.6, y: -2.4, w: 6.4, h: 6.4, fill: { color: PEACH }, line: { type: "none" } });
  s.addShape("ellipse", { x: -2.6, y: 4.6, w: 5.2, h: 5.2, fill: { color: CREAM }, line: { type: "none" } });
  s.addShape("ellipse", { x: 10.4, y: 4.9, w: 3.4, h: 3.4, fill: { color: YELLOW }, line: { type: "none" } });

  s.addText("RAPIDO DATA SCIENCE ASSESSMENT", {
    x: 0.75, y: 1.15, w: 9.5, h: 0.36,
    fontFace: "Calibri", fontSize: 14, bold: true,
    color: GOLD, charSpacing: 2.2, isTextBox: true, margin: 0,
  });
  s.addText("Captain onboarding leak\n& overnight airport supply", {
    x: 0.7, y: 1.58, w: 8.8, h: 1.7,
    fontFace: "Cambria", fontSize: 34, bold: true, color: INK,
    align: "left", lineSpacingMultiple: 1.12, isTextBox: true, margin: 0,
  });
  s.addText("Where the extra ~180 approved captains a month come from, and why overnight airport supply is an economics problem, not a headcount one.", {
    x: 0.75, y: 3.42, w: 8.4, h: 0.9,
    fontFace: "Calibri", fontSize: 16, color: MUTED,
    align: "left", lineSpacingMultiple: 1.28, isTextBox: true, margin: 0,
  });
  s.addShape("line", { x: 0.75, y: 4.48, w: 2.6, h: 0, line: { color: ORANGE, width: 2.5 } });
  s.addText("Ramanathan K R", {
    x: 0.75, y: 4.66, w: 7, h: 0.42,
    fontFace: "Cambria", fontSize: 22, bold: true, color: INK, isTextBox: true, margin: 0,
  });
  s.addText("10 September 2026  ·  Data extract as of 30 Jun 2026, 23:59 IST", {
    x: 0.75, y: 5.12, w: 8.5, h: 0.32,
    fontFace: "Calibri", fontSize: 14, color: MUTED, isTextBox: true, margin: 0,
  });

  s.addShape("roundRect", {
    x: 9.35, y: 3.42, w: 3.5, h: 3.4, rectRadius: 0.16,
    fill: { color: PEACH }, line: { type: "none" },
  });
  s.addImage({ data: AUTO,   x: 9.5, y: 3.52, w: 1.55, h: 1.55 });
  s.addImage({ data: CAB,    x: 11.1, y: 3.52, w: 1.55, h: 1.55 });
  s.addImage({ data: SCOOTY, x: 9.5, y: 5.15, w: 1.55, h: 1.55 });
  s.addImage({ data: BIKE,   x: 11.1, y: 5.15, w: 1.55, h: 1.55 });
}

// ── 1 Headline ──────────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: PAPER };
  kicker(s, "Captain onboarding — the headline");
  s.addImage({ data: AUTO, x: 12.05, y: 0.18, w: 0.95, h: 0.95 });

  s.addText("One broken capture step costs ~180 captains/month.", {
    x: 0.6, y: 0.68, w: 11.2, h: 0.7,
    fontFace: "Cambria", fontSize: 26, bold: true, color: INK, isTextBox: true, margin: 0,
  });
  s.addText("Two capture-quality fixes on RC and Insurance — not a mix of five things — recover ~180 additional approved captains/month at medium confidence.", {
    x: 0.6, y: 1.4, w: 12.1, h: 0.55,
    fontFace: "Calibri", fontSize: 15, color: MUTED, isTextBox: true, margin: 0,
  });

  card(s, 0.55, 2.1, 7.55, 4.4, WHITE);
  s.addText("Split of the ~180  (disjoint C1a + C1b)", {
    x: 0.75, y: 2.2, w: 7.15, h: 0.34,
    fontFace: "Calibri", fontSize: 14, bold: true, color: INK, isTextBox: true, margin: 0,
  });
  s.addImage({ data: PIE180, x: 0.75, y: 2.52, w: 7.15, h: 3.8 });

  statCard(s, 8.3, 2.1, 4.45, 1.38, "98.7%", "of mature approved captains take a first trip (3,895 / 3,946). Documents are the bottleneck.");
  statCard(s, 8.3, 3.6, 4.45, 1.38, "~134 / mo", "Recovered from an RC in-person grace window (C1a).");
  statCard(s, 8.3, 5.1, 4.45, 1.38, "~50 / mo", "Recovered from Insurance guided capture UX (C1b).");

  footer(s, 1);
  s.addNotes("Talk track: ~180, medium confidence (~134 RC + ~50 Insurance). 98.7% take a first trip.");
}

// ── 2 Root cause ─────────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: PAPER };
  kicker(s, "Root cause");
  s.addImage({ data: CAB, x: 12.05, y: 0.18, w: 0.95, h: 0.95 });

  s.addText("RC and Insurance are failing as photographs, not documents", {
    x: 0.6, y: 0.68, w: 11.3, h: 0.62,
    fontFace: "Cambria", fontSize: 24, bold: true, color: INK, isTextBox: true, margin: 0,
  });
  s.addText("Capture-class failures (blur, weak OCR, illegibility) dominate RC and Insurance, and later attempts pass more often. That is a capture / UX problem, not an eligibility one.", {
    x: 0.6, y: 1.32, w: 12.1, h: 0.55,
    fontFace: "Calibri", fontSize: 15, color: MUTED, isTextBox: true, margin: 0,
  });

  card(s, 0.55, 2.02, 6.0, 4.05, WHITE);
  s.addText("RC loss: only the photo slice is C1a", {
    x: 0.75, y: 2.12, w: 5.6, h: 0.32,
    fontFace: "Calibri", fontSize: 14, bold: true, color: INK, isTextBox: true, margin: 0,
  });
  s.addImage({ data: PIERC, x: 0.7, y: 2.42, w: 5.7, h: 3.5 });

  card(s, 6.75, 2.02, 6.05, 4.05, WHITE);
  s.addText("Insurance leftovers — only 411 are C1b", {
    x: 6.95, y: 2.12, w: 5.65, h: 0.32,
    fontFace: "Calibri", fontSize: 14, bold: true, color: INK, isTextBox: true, margin: 0,
  });
  s.addImage({ data: PIEC1B, x: 6.9, y: 2.42, w: 5.75, h: 3.5 });

  card(s, 0.55, 6.18, 12.25, 0.78, YELLOW);
  s.addText("1,637 RC and 411 Insurance captains are capture-only fails — isolated from eligibility (expired, duplicate, wrong type). DL (1,166) is 100% uploaded-fail and cannot be deferred.", {
    x: 0.75, y: 6.18, w: 11.85, h: 0.78,
    fontFace: "Calibri", fontSize: 14, color: INK, valign: "middle", isTextBox: true, margin: 0,
  });

  footer(s, 2);
}

// ── 3 The fix ──────────────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: PAPER };
  kicker(s, "The fix");
  s.addImage({ data: SCOOTY, x: 12.05, y: 0.18, w: 0.95, h: 0.95 });

  s.addText("One recommendation, two sub-actions — RC defers, Insurance doesn’t", {
    x: 0.6, y: 0.68, w: 11.3, h: 0.58,
    fontFace: "Cambria", fontSize: 24, bold: true, color: INK, isTextBox: true, margin: 0,
  });

  function fixCard(x, tag, title, rows, note) {
    card(s, x, 1.4, 6.05, 5.15, WHITE);
    s.addShape("roundRect", {
      x: x + 0.28, y: 1.58, w: 2.15, h: 0.4,
      rectRadius: 0.2, fill: { color: YELLOW }, line: { type: "none" },
    });
    s.addText(tag, {
      x: x + 0.28, y: 1.58, w: 2.15, h: 0.4,
      fontFace: "Calibri", fontSize: 13, bold: true, color: INK,
      align: "center", valign: "middle", isTextBox: true, margin: 0,
    });
    s.addText(title, {
      x: x + 0.28, y: 2.08, w: 5.5, h: 0.7,
      fontFace: "Cambria", fontSize: 16, bold: true, color: INK, isTextBox: true, margin: 0,
    });
    let ry = 2.85;
    rows.forEach(([label, val]) => {
      s.addText([
        { text: label + "  ", options: { bold: true, color: GOLD } },
        { text: val, options: { color: INK } },
      ], {
        x: x + 0.28, y: ry, w: 5.5, h: 0.52,
        fontFace: "Calibri", fontSize: 14, isTextBox: true, margin: 0,
      });
      ry += 0.54;
    });
    s.addShape("roundRect", {
      x: x + 0.18, y: 5.95, w: 5.7, h: 0.48,
      rectRadius: 0.06, fill: { color: CREAM }, line: { type: "none" },
    });
    s.addText(note, {
      x: x + 0.28, y: 5.95, w: 5.5, h: 0.48,
      fontFace: "Calibri", fontSize: 12, italic: true, color: MUTED,
      valign: "middle", isTextBox: true, margin: 0,
    });
  }

  fixCard(0.5, "C1a — RC", "Provisional activation · 10-day in-person grace", [
    ["Who", "1,637 RC capture-only fails (~300/mo)"],
    ["Why", "Vehicle identity — no passenger-liability exposure"],
    ["Show-up", "40 / 60 / 80% × 74–78% pass rate"],
    ["Central", "~134/month additional approved"],
    ["Needs", "Legal + Trust & Safety sign-off on deferral"],
  ], "If remaining docs still bind: ~36/month (Legal ask).");

  fixCard(6.78, "C1b — Insurance", "Guided capture UX — no deferral possible", [
    ["Who", "411 Insurance capture-only fails (~75/mo)"],
    ["Why not", "Liability document — must clear before first ride"],
    ["Retry", "67.4% → 73.8% → 76.4% pass on own retry"],
    ["Central", "~46–52/month additional approved"],
    ["Needs", "Engineering UX only — no sign-off required"],
  ], "Ship C1b this week. Start Legal on C1a in parallel.");

  footer(s, 3);
}

// ── 4 Airport ─────────────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: PAPER };
  kicker(s, "Airport supply");
  s.addImage({ data: BIKE, x: 12.05, y: 0.18, w: 0.95, h: 0.95 });

  s.addText("Overnight airport is compounding economics, not a headcount problem", {
    x: 0.6, y: 0.68, w: 11.3, h: 0.62,
    fontFace: "Cambria", fontSize: 22, bold: true, color: INK, isTextBox: true, margin: 0,
  });

  card(s, 0.55, 1.42, 6.0, 3.55, WHITE);
  s.addText("When the pain sits (unfulfilled volume)", {
    x: 0.75, y: 1.5, w: 5.6, h: 0.32,
    fontFace: "Calibri", fontSize: 14, bold: true, color: INK, isTextBox: true, margin: 0,
  });
  s.addImage({ data: PIEAIR, x: 0.7, y: 1.82, w: 5.7, h: 3.05 });

  card(s, 6.75, 1.42, 6.05, 3.55, WHITE);
  s.addText("ARA monthly payout (₹k/month) at ₹35.4/leg", {
    x: 6.95, y: 1.5, w: 5.7, h: 0.32,
    fontFace: "Calibri", fontSize: 14, bold: true, color: INK, isTextBox: true, margin: 0,
  });
  addARAChart(s, 6.85, 1.82, 5.8, 3.05);

  [
    ["40%", "Airport demand unfulfilled vs ~3% elsewhere"],
    ["84%", "Of the night gap sits in 21:00–03:59 — ~13 captains vs ~37 by day"],
    ["₹35.4", "Per eligible leg — derived ARA. Not 30% of fare (₹105)."],
  ].forEach(([n, d], i) => {
    const sx = 0.55 + i * 4.1;
    card(s, sx, 5.1, 3.95, 1.4, i === 1 ? YELLOW : PEACH);
    s.addText(n, {
      x: sx + 0.18, y: 5.18, w: 3.6, h: 0.5,
      fontFace: "Cambria", fontSize: 26, bold: true, color: INK, isTextBox: true, margin: 0,
    });
    s.addText(d, {
      x: sx + 0.18, y: 5.68, w: 3.6, h: 0.72,
      fontFace: "Calibri", fontSize: 13, color: MUTED, isTextBox: true, margin: 0,
    });
  });

  footer(s, 4);
}

// ── 5 What doesn’t work ───────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: PAPER };
  kicker(s, "What does not work — and how easy it is to be fooled");
  s.addImage({ data: AUTO, x: 12.05, y: 0.18, w: 0.95, h: 0.95 });

  s.addText("A campaign with 0 pp lift, and a gap we must not bank", {
    x: 0.6, y: 0.68, w: 11.3, h: 0.52,
    fontFace: "Cambria", fontSize: 24, bold: true, color: INK, isTextBox: true, margin: 0,
  });

  card(s, 0.55, 1.32, 6.05, 4.72, WHITE);
  s.addText("CAMP_WA_002 — WhatsApp campaign", {
    x: 0.75, y: 1.42, w: 5.65, h: 0.36,
    fontFace: "Cambria", fontSize: 16, bold: true, color: INK, isTextBox: true, margin: 0,
  });
  s.addText("The 29% vs 11% headline is targeting, not effect.", {
    x: 0.75, y: 1.8, w: 5.65, h: 0.32,
    fontFace: "Calibri", fontSize: 14, bold: true, color: GOLD, isTextBox: true, margin: 0,
  });
  addCampaignChart(s, 0.65, 2.12, 5.8, 2.55);
  s.addText("Honest comparison: clicked vs not-clicked (delivered only) = −1.5 pp; 95% CI [−3.6, +0.6]. That is 0 pp lift. Do not fund 5×.", {
    x: 0.75, y: 4.72, w: 5.65, h: 0.7,
    fontFace: "Calibri", fontSize: 13, color: INK, isTextBox: true, margin: 0,
  });
  s.addText("~30% of recipients also got another campaign — confounding further inflated.", {
    x: 0.75, y: 5.42, w: 5.65, h: 0.42,
    fontFace: "Calibri", fontSize: 13, italic: true, color: MUTED, isTextBox: true, margin: 0,
  });

  card(s, 6.78, 1.32, 6.05, 4.72, WHITE);
  s.addText("Field vs self-serve — do not double-count", {
    x: 6.98, y: 1.42, w: 5.65, h: 0.4,
    fontFace: "Cambria", fontSize: 16, bold: true, color: INK, isTextBox: true, margin: 0,
  });
  const bullets = [
    "Mechanical ceiling if app/paid converted like field: 128–256 additional/month.",
    "Field teams recruit in person — extract cannot separate who they recruit from how they onboard.",
    "726 of the C1a RC group are the same self-serve captains this gap already counts. Do not add 180 + 128–256.",
    "Fos abandonment after Fitness: 26% vs paid 43% — in-person assist, not WhatsApp.",
    "Correct move: randomised assisted-onboarding pilot on app/paid (~900 per arm to detect a 5 pp lift).",
  ];
  let by = 1.92;
  bullets.forEach((t) => {
    s.addShape("ellipse", {
      x: 7.0, y: by + 0.1, w: 0.14, h: 0.14,
      fill: { color: ORANGE }, line: { type: "none" },
    });
    s.addText(t, {
      x: 7.28, y: by, w: 5.35, h: 0.72,
      fontFace: "Calibri", fontSize: 13, color: INK, isTextBox: true, margin: 0,
    });
    by += 0.78;
  });

  footer(s, 5);
}

// ── 6 Recommendations ────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: PAPER };
  kicker(s, "Recommendations & decision points");
  s.addImage({ data: CAB, x: 12.05, y: 0.18, w: 0.95, h: 0.95 });

  s.addText("Ranked by monthly impact. The campaign call is the fastest yes.", {
    x: 0.6, y: 0.68, w: 11.3, h: 0.5,
    fontFace: "Cambria", fontSize: 24, bold: true, color: INK, isTextBox: true, margin: 0,
  });

  [["Action", 2.15, 4.3], ["Monthly impact", 6.55, 2.45], ["Cost / risk", 9.1, 3.4]].forEach(([t, x, w]) => {
    s.addText(t.toUpperCase(), {
      x, y: 1.28, w, h: 0.26,
      fontFace: "Calibri", fontSize: 12, bold: true, color: GOLD,
      charSpacing: 1.2, isTextBox: true, margin: 0,
    });
  });

  const rows = [
    {
      num: "1",
      what: "C1a: 10-day RC in-person grace\nC1b: Insurance upload UX (ship this week)",
      impact: "~180/mo approved",
      risk: "C1a: Legal + T&S. C1b: engineering only.",
    },
    {
      num: "2",
      what: "Airport Return Assurance at ₹35.4/leg\n(derived payout — not 30% of fare)",
      impact: "₹69k–103k/mo sample",
      risk: "Sampled trips ≠ city P&L. Rest-suburban only.",
    },
    {
      num: "3",
      what: "Stop CAMP_WA_002 5× scaling. Send/no-send RCT on RC-cleared self-serve captains.",
      impact: "Cost avoided + 4–6 week answer",
      risk: "Near zero — a redirection, not new spend.",
    },
  ];
  let ry = 1.58;
  rows.forEach(({ num, what, impact, risk }, i) => {
    card(s, 0.55, ry, 12.25, 1.18, i % 2 === 0 ? WHITE : CREAM);
    s.addShape("ellipse", {
      x: 0.78, y: ry + 0.34, w: 0.5, h: 0.5,
      fill: { color: ORANGE }, line: { type: "none" },
    });
    s.addText(num, {
      x: 0.78, y: ry + 0.34, w: 0.5, h: 0.5,
      fontFace: "Cambria", fontSize: 16, bold: true, color: INK,
      align: "center", valign: "middle", isTextBox: true, margin: 0,
    });
    s.addText(what, {
      x: 1.5, y: ry + 0.1, w: 4.85, h: 0.98,
      fontFace: "Calibri", fontSize: 14, bold: true, color: INK,
      valign: "middle", isTextBox: true, margin: 0,
    });
    s.addText(impact, {
      x: 6.5, y: ry + 0.1, w: 2.5, h: 0.98,
      fontFace: "Calibri", fontSize: 14, bold: true, color: GOLD,
      valign: "middle", isTextBox: true, margin: 0,
    });
    s.addText(risk, {
      x: 9.1, y: ry + 0.1, w: 3.45, h: 0.98,
      fontFace: "Calibri", fontSize: 13, color: MUTED,
      valign: "middle", isTextBox: true, margin: 0,
    });
    ry += 1.26;
  });

  card(s, 0.55, 5.42, 12.25, 1.12, YELLOW);
  s.addText("Ask of the room   (1) Ship Insurance capture UX — no need to wait.   (2) Legal scoping on RC deferral, this week.   (3) Kill the 5× WhatsApp paper; stand up the RCT.   (4) Four-week ARA pilot at the derived ₹35.4, not 30% of fare.", {
    x: 0.75, y: 5.42, w: 11.85, h: 1.12,
    fontFace: "Calibri", fontSize: 14, color: INK, valign: "middle", isTextBox: true, margin: 0,
  });

  footer(s, 6);
}

const outPptx = path.join(__dirname, "DECK.pptx");
pres.writeFile({ fileName: outPptx })
  .then(() => console.log("wrote", outPptx))
  .catch((e) => { console.error(e); process.exit(1); });
