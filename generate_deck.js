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

// ── 1 Ask (title lives here so the deck is 6 slides) ────────────────────
{
  const s = pres.addSlide();
  s.background = { color: PAPER };
  kicker(s, "Rapido  ·  Ramanathan K R  ·  extract 30 Jun 2026, 23:59 IST");
  s.addImage({ data: AUTO, x: 12.05, y: 0.18, w: 0.95, h: 0.95 });

  s.addText("Ship Insurance capture this week (~50/mo). Do not 5× WhatsApp. Do not hire the airport.", {
    x: 0.6, y: 0.64, w: 11.3, h: 0.78,
    fontFace: "Cambria", fontSize: 22, bold: true, color: INK, isTextBox: true, margin: 0,
  });
  s.addText("The number I will put my name on this week is ~50 extra approved / month (C1b, no Legal). RC grace is ~134/mo only if Legal treats deferred RC as activation — otherwise ~36. 98.7% of mature approved already take a first trip (3,895 / 3,946): documents, not first-order.", {
    x: 0.6, y: 1.42, w: 12.1, h: 0.7,
    fontFace: "Calibri", fontSize: 14, color: MUTED, isTextBox: true, margin: 0,
  });

  card(s, 0.55, 2.18, 7.55, 4.32, WHITE);
  s.addText("If Legal says yes, C1a + C1b (disjoint) — not an unconditional bank", {
    x: 0.75, y: 2.26, w: 7.15, h: 0.36,
    fontFace: "Calibri", fontSize: 13, bold: true, color: INK, isTextBox: true, margin: 0,
  });
  s.addImage({ data: PIE180, x: 0.75, y: 2.58, w: 7.15, h: 3.75 });

  statCard(s, 8.3, 2.18, 4.45, 1.38, "~50 / mo", "C1b Insurance UX. Ship this week. Engineering only. This is the unconditional number.");
  statCard(s, 8.3, 3.68, 4.45, 1.38, "~134 / ~36", "C1a RC grace at 60% show-up if Legal yes. If remaining docs still bind: ~36.");
  statCard(s, 8.3, 5.18, 4.45, 1.32, "0 pp", "CAMP_WA_002 honest contrast (clicked vs not). Do not fund 5×.");

  footer(s, 1);
  s.addNotes("Lead with C1b ~50. C1a is a Legal scenario. Campaign 0 pp. 98.7% R2A.");
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

  s.addText("C1b ships this week. C1a is a Legal decision, not a bank.", {
    x: 0.6, y: 0.68, w: 11.3, h: 0.58,
    fontFace: "Cambria", fontSize: 22, bold: true, color: INK, isTextBox: true, margin: 0,
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

  fixCard(0.5, "C1b — ship now", "Guided Insurance capture UX — no deferral", [
    ["Who", "411 Insurance capture-only fails (~75/mo)"],
    ["Why not defer", "Liability document — must clear before first ride"],
    ["Retry", "67.4% → 73.8% → 76.4% pass on own retry"],
    ["Bank", "~46–52/month additional approved"],
    ["Needs", "Engineering UX only — no Legal sign-off"],
  ], "This is the number I would put in a deck with my name on it this week.");

  fixCard(6.78, "C1a — if Legal", "Provisional RC · 10-day in-person grace", [
    ["Who", "1,637 RC capture-only fails (~300/mo)"],
    ["Why defer", "Vehicle identity — no passenger-liability exposure"],
    ["Show-up", "Unobserved. 40 / 60 / 80% × 74–78% pass"],
    ["If Legal yes", "~134/month at 60% show-up"],
    ["If docs still bind", "~36/month (27% approved | passed RC)"],
  ], "Do not add C1a to ~50 until Legal/T&S treat deferred RC as activation.");

  footer(s, 3);
}

// ── 4 Airport ─────────────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: PAPER };
  kicker(s, "Airport supply");
  s.addImage({ data: SCOOTY, x: 12.05, y: 0.18, w: 0.95, h: 0.95 });

  s.addText("Do not hire the catchment. After the trip, the night still loses money.", {
    x: 0.6, y: 0.66, w: 11.3, h: 0.5,
    fontFace: "Cambria", fontSize: 22, bold: true, color: INK, isTextBox: true, margin: 0,
  });

  card(s, 0.55, 1.22, 6.0, 3.22, WHITE);
  s.addText("B1 — when the pain sits", {
    x: 0.75, y: 1.28, w: 5.6, h: 0.28,
    fontFace: "Calibri", fontSize: 14, bold: true, color: INK, isTextBox: true, margin: 0,
  });
  s.addImage({ data: PIEAIR, x: 0.7, y: 1.54, w: 5.7, h: 2.8 });

  card(s, 6.75, 1.22, 6.05, 3.22, WHITE);
  s.addText("B3 — price the deadhead (₹k/mo at ₹35.4/leg)", {
    x: 6.95, y: 1.28, w: 5.7, h: 0.28,
    fontFace: "Calibri", fontSize: 14, bold: true, color: INK, isTextBox: true, margin: 0,
  });
  addARAChart(s, 6.85, 1.54, 5.8, 2.8);

  card(s, 0.55, 4.52, 12.25, 0.7, YELLOW);
  s.addText("B2 — after the trip: suburban backhaul and overnight return-in-20min collapse compound. Mix does not shift after dark (χ² p=0.12). New hires inherit both penalties. Not 30% of fare (₹105).", {
    x: 0.72, y: 4.52, w: 11.9, h: 0.7,
    fontFace: "Calibri", fontSize: 14, color: INK, valign: "middle", isTextBox: true, margin: 0,
  });

  [
    ["40%", "Unfulfilled at terminals vs ~3% elsewhere"],
    ["84%", "Of that gap is 21:00–03:59 — ~13 captains vs ~37 by day"],
    ["₹35.4", "Per eligible night-suburban leg. 4-week pilot; hire only if run-rate falls."],
  ].forEach(([n, d], i) => {
    const sx = 0.55 + i * 4.1;
    card(s, sx, 5.3, 3.95, 1.18, i === 1 ? YELLOW : PEACH);
    s.addText(n, {
      x: sx + 0.18, y: 5.34, w: 3.6, h: 0.42,
      fontFace: "Cambria", fontSize: 24, bold: true, color: INK, isTextBox: true, margin: 0,
    });
    s.addText(d, {
      x: sx + 0.18, y: 5.76, w: 3.6, h: 0.64,
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

  s.addText("Ranked by what can start Monday. C1a is not in the unconditional bank.", {
    x: 0.6, y: 0.68, w: 11.3, h: 0.5,
    fontFace: "Cambria", fontSize: 22, bold: true, color: INK, isTextBox: true, margin: 0,
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
      what: "C1b Insurance capture UX — ship this week\nThen Legal scoping on C1a RC grace (do not bank 134 yet)",
      impact: "~50/mo now\n(+134 only if Legal)",
      risk: "C1b: engineering. C1a: Legal/T&S. Show-up unobserved.",
    },
    {
      num: "2",
      what: "Airport Return Assurance at ₹35.4/leg\nDo not hire. After-trip mix does not shift (p=0.12).",
      impact: "₹69k–103k/mo sample",
      risk: "Sampled trips ≠ city P&L. Rest-suburban only.",
    },
    {
      num: "3",
      what: "Stop CAMP_WA_002 5×. Send/no-send RCT on RC-cleared self-serve captains.",
      impact: "0 pp  ·  cost avoided",
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
  s.addText("Ask of the room   (1) Ship Insurance capture UX this week — the ~50.   (2) Legal: is deferred RC activation? If no, C1a is ~36 not ~134.   (3) Kill 5× WhatsApp; stand up the RCT.   (4) Four-week ARA at ₹35.4, not 30% of fare.", {
    x: 0.75, y: 5.42, w: 11.85, h: 1.12,
    fontFace: "Calibri", fontSize: 14, color: INK, valign: "middle", isTextBox: true, margin: 0,
  });

  footer(s, 6);
}

const outPptx = path.join(__dirname, "DECK.pptx");
pres.writeFile({ fileName: outPptx })
  .then(() => console.log("wrote", outPptx))
  .catch((e) => { console.error(e); process.exit(1); });
