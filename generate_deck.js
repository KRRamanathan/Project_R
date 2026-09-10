const pptxgen = require("pptxgenjs");
const fs = require("fs");
const path = require("path");

const NAVY    = "1E2761";
const CORAL   = "F96167";
const TEAL    = "1C7293";
const ICE     = "CADCFC";
const GREY    = "8A8FA3";
const LIGHTBG = "F7F8FC";
const BORDER  = "E3E6F0";
const WHITE   = "FFFFFF";
const YELLOW  = "FFC400";
const GREEN   = "2A9D8F";

const FOOTER_L = "Rapido Supply  ·  Captain Onboarding & Airport Supply";
const FOOTER_R = "Ramanathan K R   ·   Rapido Data Science Assessment";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
const SW = 13.333, SH = 7.5;

function png(rel) {
  const buf = fs.readFileSync(path.join(__dirname, rel));
  return "image/png;base64," + buf.toString("base64");
}

const SCOOTY  = png("assets/scooty.png");
const CAB     = png("assets/cab.png");
const BIKE    = png("assets/bike.png");
const AUTO    = png("assets/auto.png");

function footer(slide, pageNum) {
  slide.addText(FOOTER_L, {
    x: 0.45, y: SH - 0.38, w: 7.0, h: 0.26,
    fontFace: "Calibri", fontSize: 8.5, color: GREY, margin: 0,
  });
  slide.addText(FOOTER_R + "     " + pageNum + " / 6", {
    x: SW - 6.6, y: SH - 0.38, w: 6.1, h: 0.26,
    fontFace: "Calibri", fontSize: 8.5, color: GREY, align: "right", margin: 0,
  });
}

function kicker(slide, text, color) {
  slide.addText(text.toUpperCase(), {
    x: 0.55, y: 0.28, w: 12, h: 0.26,
    fontFace: "Calibri", fontSize: 11, bold: true,
    color: color, charSpacing: 2.4, margin: 0,
  });
}

function card(slide, x, y, w, h) {
  slide.addShape("roundRect", {
    x, y, w, h, rectRadius: 0.1,
    fill: { color: WHITE },
    line: { color: BORDER, width: 1 },
  });
}

function addLostChart(slide, x, y, w, h) {
  slide.addChart(pres.ChartType.bar, [
    {
      name: "Captains lost",
      labels: ["DL", "RC", "Aadhaar", "Permit", "Fitness", "Insurance"],
      values: [1166, 5405, 1540, 2616, 2653, 3289],
    },
  ], {
    x, y, w, h,
    barDir: "bar",
    chartColors: [CORAL],
    showLegend: false,
    showValue: true,
    dataLabelFontSize: 8,
    dataLabelColor: NAVY,
    catAxisLabelColor: NAVY,
    catAxisLabelFontSize: 9,
    valAxisLabelColor: GREY,
    valAxisLabelFontSize: 8,
    valGridLine: { color: ICE, size: 0.5 },
    plotAreaBorderColor: WHITE,
    chartArea: { fill: { color: WHITE } },
  });
}

function addRetryChart(slide, x, y, w, h) {
  slide.addChart(pres.ChartType.line, [
    { name: "RC pass %", labels: ["1st try", "2nd try", "3rd try"], values: [65.3, 68.4, 74.1] },
    { name: "Insurance pass %", labels: ["1st try", "2nd try", "3rd try"], values: [67.4, 73.8, 76.4] },
  ], {
    x, y, w, h,
    chartColors: [CORAL, TEAL],
    showLegend: true, legendPos: "b", legendFontSize: 9, legendColor: NAVY,
    showValue: true, dataLabelFontSize: 8, dataLabelColor: NAVY,
    lineSize: 2.5,
    catAxisLabelColor: NAVY, catAxisLabelFontSize: 9,
    valAxisLabelColor: GREY, valAxisLabelFontSize: 8,
    valAxisMinVal: 55, valAxisMaxVal: 85,
    valGridLine: { color: ICE, size: 0.5 },
    plotAreaBorderColor: WHITE,
    chartArea: { fill: { color: WHITE } },
  });
}

function addCampaignChart(slide, x, y, w, h) {
  slide.addChart(pres.ChartType.bar, [
    {
      name: "Completion %",
      labels: ["Naive: got CAMP", "Naive: never", "Clicked", "Not clicked"],
      values: [29, 11, 28.3, 29.8],
    },
  ], {
    x, y, w, h,
    barDir: "col",
    chartColors: [CORAL],
    showLegend: false,
    showValue: true, dataLabelFontSize: 9, dataLabelColor: NAVY,
    catAxisLabelColor: NAVY, catAxisLabelFontSize: 8,
    valAxisMinVal: 0, valAxisMaxVal: 40,
    valGridLine: { color: ICE, size: 0.5 },
    plotAreaBorderColor: WHITE,
    chartArea: { fill: { color: WHITE } },
  });
}

function addARAChart(slide, x, y, w, h) {
  slide.addChart(pres.ChartType.bar, [
    {
      name: "Sample ₹k / month",
      labels: ["80%", "100%", "120%"],
      values: [69, 86, 103],
    },
  ], {
    x, y, w, h,
    barDir: "col",
    chartColors: [TEAL],
    showLegend: false,
    showValue: true, dataLabelFontSize: 10, dataLabelColor: NAVY,
    catAxisLabelColor: NAVY, catAxisLabelFontSize: 9,
    valAxisMinVal: 0, valAxisMaxVal: 130,
    valGridLine: { color: ICE, size: 0.5 },
    plotAreaBorderColor: WHITE,
    chartArea: { fill: { color: WHITE } },
  });
}

function addPie180(slide, x, y, w, h) {
  slide.addChart(pres.ChartType.doughnut, [
    { name: "of ~180/mo", labels: ["C1a RC ~134", "C1b Insurance ~50"], values: [134, 50] },
  ], {
    x, y, w, h,
    chartColors: [TEAL, CORAL],
    showLegend: true, legendPos: "b", legendFontSize: 9, legendColor: NAVY,
    showPercent: true,
    chartArea: { fill: { color: WHITE } },
  });
}

function addPieNight(slide, x, y, w, h) {
  slide.addChart(pres.ChartType.pie, [
    { name: "Airport unfulfilled", labels: ["21:00–03:59", "Rest of day"], values: [84, 16] },
  ], {
    x, y, w, h,
    chartColors: [CORAL, ICE],
    showLegend: true, legendPos: "b", legendFontSize: 9, legendColor: NAVY,
    showPercent: true,
    chartArea: { fill: { color: WHITE } },
  });
}

// ── Title ────────────────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: LIGHTBG };
  s.addShape("roundRect", {
    x: 0, y: 0, w: SW, h: 0.12, fill: { color: YELLOW }, line: { type: "none" },
  });
  s.addText("RAPIDO DATA SCIENCE ASSESSMENT", {
    x: 0.7, y: 1.35, w: 11, h: 0.32,
    fontFace: "Calibri", fontSize: 13, bold: true, color: TEAL, charSpacing: 2.5, margin: 0,
  });
  s.addText("Captain onboarding leak\n& overnight airport supply", {
    x: 0.65, y: 1.72, w: 10.5, h: 1.55,
    fontFace: "Cambria", fontSize: 32, bold: true, color: NAVY, margin: 0,
  });
  s.addText("For the Head of Supply: ~180 extra approved captains a month from two photo-quality fixes, and why overnight airport supply is an economics problem, not a hiring push.", {
    x: 0.7, y: 3.4, w: 9.2, h: 0.7,
    fontFace: "Calibri", fontSize: 14, color: "444C6A", margin: 0,
  });
  s.addShape("line", { x: 0.7, y: 4.25, w: 2.6, h: 0, line: { color: YELLOW, width: 3 } });
  s.addText("Ramanathan K R", {
    x: 0.7, y: 4.45, w: 8, h: 0.4,
    fontFace: "Cambria", fontSize: 20, bold: true, color: NAVY, margin: 0,
  });
  s.addText("10 September 2026  ·  extract 30 Jun 2026, 23:59 IST  ·  25k captains", {
    x: 0.7, y: 4.9, w: 10, h: 0.3,
    fontFace: "Calibri", fontSize: 12, color: GREY, margin: 0,
  });
  s.addImage({ data: SCOOTY, x: 0.7, y: 5.55, h: 1.05, w: 1.05 });
  s.addImage({ data: AUTO, x: 2.0, y: 5.62, h: 0.95, w: 0.95 });
  s.addImage({ data: CAB, x: 3.25, y: 5.58, h: 1.0, w: 1.0 });
  s.addImage({ data: BIKE, x: 4.55, y: 5.62, h: 0.95, w: 0.95 });
}

// ── 1 Headline ────────────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: LIGHTBG };
  kicker(s, "The headline", TEAL);
  s.addText("Two photo fixes recover ~180 approved captains a month", {
    x: 0.55, y: 0.58, w: 12.2, h: 0.5,
    fontFace: "Cambria", fontSize: 22, bold: true, color: NAVY, margin: 0,
  });

  card(s, 0.5, 1.2, 6.15, 3.55);
  s.addText("Split of the ~180  (disjoint C1a + C1b)", {
    x: 0.7, y: 1.3, w: 5.8, h: 0.28, fontFace: "Calibri", fontSize: 11, bold: true, color: NAVY, margin: 0,
  });
  addPie180(s, 0.6, 1.55, 5.9, 3.05);

  card(s, 6.85, 1.2, 5.95, 3.55);
  s.addText("RC loss: only the capture slice is C1a", {
    x: 7.05, y: 1.3, w: 5.55, h: 0.28, fontFace: "Calibri", fontSize: 11, bold: true, color: NAVY, margin: 0,
  });
  s.addChart(pres.ChartType.doughnut, [
    { name: "RC lost", labels: ["Capture-only 1,637", "Other RC 3,768"], values: [1637, 3768] },
  ], {
    x: 6.95, y: 1.55, w: 5.7, h: 3.05,
    chartColors: [CORAL, ICE],
    showLegend: true, legendPos: "b", legendFontSize: 9, legendColor: NAVY,
    showPercent: true,
    chartArea: { fill: { color: WHITE } },
  });

  const stats = [
    ["98.7%", "of mature approved take a first trip (3,895 / 3,946)", CORAL],
    ["~134/mo", "C1a RC 10-day grace · 60% show-up assumed", TEAL],
    ["~50/mo", "C1b Insurance camera UX · no deferral", GREEN],
    ["~180", "bank these two only — do not add fos 128–256", NAVY],
  ];
  stats.forEach(([n, d, c], i) => {
    const x = 0.5 + (i % 4) * 3.18;
    card(s, x, 4.9, 3.05, 1.55);
    s.addText(n, { x: x + 0.12, y: 5.0, w: 2.8, h: 0.55, fontFace: "Cambria", fontSize: 22, bold: true, color: c, margin: 0 });
    s.addText(d, { x: x + 0.12, y: 5.55, w: 2.8, h: 1.0, fontFace: "Calibri", fontSize: 11, color: "444C6A", margin: 0 });
  });
  footer(s, 1);
  s.addNotes("~180 medium confidence. 98.7% first trip. Documents are the bottleneck.");
}

// ── 2 Root cause ─────────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: LIGHTBG };
  kicker(s, "Root cause", CORAL);
  s.addText("RC and Insurance fail as photographs, not documents", {
    x: 0.55, y: 0.58, w: 12.2, h: 0.48,
    fontFace: "Cambria", fontSize: 22, bold: true, color: NAVY, margin: 0,
  });

  card(s, 0.5, 1.18, 6.2, 3.7);
  s.addText("Volume lost by stage (mature ∩ events)", {
    x: 0.68, y: 1.28, w: 5.85, h: 0.26, fontFace: "Calibri", fontSize: 11, bold: true, color: NAVY, margin: 0,
  });
  addLostChart(s, 0.55, 1.5, 6.05, 3.25);

  card(s, 6.9, 1.18, 5.9, 3.7);
  s.addText("Retry pass rates rise — capture, not eligibility", {
    x: 7.08, y: 1.28, w: 5.55, h: 0.26, fontFace: "Calibri", fontSize: 11, bold: true, color: NAVY, margin: 0,
  });
  addRetryChart(s, 6.95, 1.5, 5.75, 3.25);

  s.addShape("roundRect", {
    x: 0.5, y: 5.05, w: 12.3, h: 1.55, rectRadius: 0.1,
    fill: { color: WHITE }, line: { color: BORDER, width: 1 },
  });
  s.addText("1,637 RC  +  411 Insurance  = capture-only (blur / OCR / illegible). DL 1,166 is 100% uploaded-fail and cannot be deferred. Aadhaar / Permit / Fitness are mostly never-upload or eligibility — a camera does not fix those.", {
    x: 0.7, y: 5.18, w: 12.0, h: 1.25, fontFace: "Calibri", fontSize: 13, color: NAVY, margin: 0,
  });
  footer(s, 2);
}

// ── 3 Fix ────────────────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: LIGHTBG };
  kicker(s, "The fix", TEAL);
  s.addText("C1b ships this week. C1a waits on Legal. Same camera is not extra 180.", {
    x: 0.55, y: 0.58, w: 12.2, h: 0.45,
    fontFace: "Cambria", fontSize: 20, bold: true, color: NAVY, margin: 0,
  });

  function fixCard(x, tag, title, img, rows) {
    card(s, x, 1.15, 6.1, 5.4);
    s.addShape("roundRect", {
      x: x + 0.25, y: 1.35, w: 1.55, h: 0.34, rectRadius: 0.16,
      fill: { color: TEAL }, line: { type: "none" },
    });
    s.addText(tag, {
      x: x + 0.25, y: 1.35, w: 1.55, h: 0.34,
      fontFace: "Calibri", fontSize: 11, bold: true, color: WHITE, align: "center", valign: "middle", margin: 0,
    });
    s.addImage({ data: img, x: x + 5.15, y: 1.28, h: 0.52, w: 0.52 });
    s.addText(title, {
      x: x + 0.25, y: 1.82, w: 5.55, h: 0.55,
      fontFace: "Cambria", fontSize: 15, bold: true, color: NAVY, margin: 0,
    });
    let ry = 2.5;
    rows.forEach(([lab, val]) => {
      s.addText(lab, { x: x + 0.28, y: ry, w: 1.5, h: 0.55, fontFace: "Calibri", fontSize: 11, bold: true, color: TEAL, margin: 0 });
      s.addText(val, { x: x + 1.75, y: ry, w: 4.05, h: 0.55, fontFace: "Calibri", fontSize: 12, color: "333333", margin: 0 });
      ry += 0.62;
    });
  }

  fixCard(0.5, "C1a  RC", "Provisional RC · 10-day in-person", SCOOTY, [
    ["Who", "1,637 capture-only · ~300/mo flow"],
    ["Why defer", "Vehicle ID, not passenger liability"],
    ["Maths", "~300 × 60% show-up × 74% pass ≈ 134"],
    ["Risk", "Show-up unobserved. Legal must treat as activation."],
    ["Watch", "If remaining docs bind → ~36/month"],
  ]);
  fixCard(6.8, "C1b  INS", "Guided capture UX · no deferral", CAB, [
    ["Who", "411 capture-only · must clear before a ride"],
    ["Why not", "Liability document — cannot defer"],
    ["Maths", "67→76% pass × 91% approved-if-cleared"],
    ["Central", "~46–52 extra approved / month"],
    ["Needs", "Engineering only — ship this week"],
  ]);
  footer(s, 3);
}

// ── 4 Airport ────────────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: LIGHTBG };
  kicker(s, "Airport supply", TEAL);
  s.addText("Do not hire the catchment. Price the deadhead.", {
    x: 0.55, y: 0.58, w: 12.2, h: 0.42,
    fontFace: "Cambria", fontSize: 21, bold: true, color: NAVY, margin: 0,
  });

  card(s, 0.5, 1.12, 6.15, 3.55);
  s.addText("When the pain sits (unfulfilled volume)", {
    x: 0.68, y: 1.22, w: 5.8, h: 0.26, fontFace: "Calibri", fontSize: 11, bold: true, color: NAVY, margin: 0,
  });
  addPieNight(s, 0.55, 1.45, 5.95, 3.1);

  card(s, 6.85, 1.12, 5.95, 3.55);
  s.addText("ARA sample cost at ₹35.4 / eligible leg", {
    x: 7.02, y: 1.22, w: 5.6, h: 0.26, fontFace: "Calibri", fontSize: 11, bold: true, color: NAVY, margin: 0,
  });
  addARAChart(s, 6.95, 1.45, 5.75, 3.1);

  [
    ["40%", "unfulfilled at terminals vs ~3% elsewhere"],
    ["~13 vs ~37", "captains online nights vs rest of day"],
    ["₹35.4", "derived / unpaid night-suburban leg — not 30% of fare (₹105)"],
  ].forEach(([n, d], i) => {
    const x = 0.5 + i * 4.2;
    card(s, x, 4.85, 4.05, 1.7);
    s.addText(n, { x: x + 0.15, y: 4.95, w: 3.75, h: 0.55, fontFace: "Cambria", fontSize: 22, bold: true, color: CORAL, margin: 0 });
    s.addText(d, { x: x + 0.15, y: 5.5, w: 3.75, h: 0.85, fontFace: "Calibri", fontSize: 12, color: "444C6A", margin: 0 });
  });
  footer(s, 4);
  s.addNotes("Two independent penalties. Mix does not shift. ARA first. Hire only if 4-week run-rate is not falling.");
}

// ── 5 Traps ──────────────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: LIGHTBG };
  kicker(s, "What not to do", CORAL);
  s.addText("0 pp campaign lift. Do not bank the field gap.", {
    x: 0.55, y: 0.58, w: 12.2, h: 0.42,
    fontFace: "Cambria", fontSize: 21, bold: true, color: NAVY, margin: 0,
  });

  card(s, 0.5, 1.12, 6.2, 4.55);
  s.addText("CAMP_WA_002 — naive vs honest", {
    x: 0.68, y: 1.22, w: 5.85, h: 0.28, fontFace: "Calibri", fontSize: 12, bold: true, color: NAVY, margin: 0,
  });
  addCampaignChart(s, 0.55, 1.5, 6.0, 3.15);
  s.addText("Clicked vs not (delivered): −1.5pp, CI [−3.6, +0.6] → 0 pp. The 29% vs 11% gap is targeting after RC. Do not scale 5×.", {
    x: 0.68, y: 4.7, w: 5.85, h: 0.8, fontFace: "Calibri", fontSize: 12, color: "444C6A", margin: 0,
  });

  card(s, 6.9, 1.12, 5.9, 4.55);
  s.addText("Do not add these to 180", {
    x: 7.08, y: 1.22, w: 5.55, h: 0.28, fontFace: "Calibri", fontSize: 12, bold: true, color: NAVY, margin: 0,
  });
  const traps = [
    "Field vs app 128–256/month is selection, not a product lift.",
    "726 C1a captains already sit in that self-serve gap.",
    "Never-upload RC ~2,388 / Insurance ~2,530 is not another WhatsApp (CAMP was 0 pp).",
    "ARA at 30% of fare (₹105) overpays vs ₹35.4.",
    "Test: assist RCT on app/paid (~900/arm for a 5pp approval lift).",
  ];
  traps.forEach((t, i) => {
    s.addText("▸  " + t, {
      x: 7.1, y: 1.65 + i * 0.72, w: 5.5, h: 0.7,
      fontFace: "Calibri", fontSize: 13, color: "333333", margin: 0,
    });
  });
  footer(s, 5);
}

// ── 6 Ask ────────────────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: LIGHTBG };
  kicker(s, "Ask of the room", TEAL);
  s.addText("Ranked by monthly impact. Campaign stop is the fastest yes.", {
    x: 0.55, y: 0.58, w: 12.2, h: 0.4,
    fontFace: "Cambria", fontSize: 20, bold: true, color: NAVY, margin: 0,
  });

  const rows = [
    ["1", "C1b camera this week, then C1a RC grace after Legal", "~180/mo", "Legal on C1a; C1b is engineering", SCOOTY],
    ["2", "ARA ₹35.4 / unpaid night-suburban leg · 4 weeks", "₹69–103k sample", "Do not hire. Not city-core.", CAB],
    ["3", "Kill CAMP 5×; send/no-send RCT on RC-cleared app/paid", "Cost avoided + 4–6 wks", "Near zero", AUTO],
  ];
  rows.forEach((r, i) => {
    const y = 1.12 + i * 1.22;
    card(s, 0.5, y, 12.3, 1.12);
    s.addImage({ data: r[4], x: 0.7, y: y + 0.22, h: 0.7, w: 0.7 });
    s.addShape("ellipse", {
      x: 1.55, y: y + 0.32, w: 0.42, h: 0.42,
      fill: { color: TEAL }, line: { type: "none" },
    });
    s.addText(r[0], {
      x: 1.55, y: y + 0.32, w: 0.42, h: 0.42,
      fontFace: "Cambria", fontSize: 14, bold: true, color: WHITE, align: "center", valign: "middle", margin: 0,
    });
    s.addText(r[1], {
      x: 2.15, y: y + 0.18, w: 5.5, h: 0.78,
      fontFace: "Calibri", fontSize: 13, bold: true, color: NAVY, valign: "middle", margin: 0,
    });
    s.addText(r[2], {
      x: 7.7, y: y + 0.18, w: 2.3, h: 0.78,
      fontFace: "Calibri", fontSize: 13, bold: true, color: CORAL, valign: "middle", margin: 0,
    });
    s.addText(r[3], {
      x: 10.05, y: y + 0.18, w: 2.5, h: 0.78,
      fontFace: "Calibri", fontSize: 12, color: GREY, valign: "middle", margin: 0,
    });
  });

  s.addShape("roundRect", {
    x: 0.5, y: 4.9, w: 12.3, h: 1.65, rectRadius: 0.1,
    fill: { color: WHITE }, line: { color: BORDER, width: 1 },
  });
  s.addText("This week: ship Insurance UX · scope RC deferral · kill 5× paper · start 4-week ARA at ₹35.4, not 30% of fare.", {
    x: 0.7, y: 5.05, w: 12.0, h: 1.35,
    fontFace: "Calibri", fontSize: 16, color: NAVY, margin: 0,
  });
  footer(s, 6);
  s.addNotes("If interrupted: slides 1, 4, 5.");
}

const outPptx = path.join(__dirname, "DECK.pptx");
pres.writeFile({ fileName: outPptx })
  .then(() => console.log("wrote", outPptx))
  .catch((e) => { console.error(e); process.exit(1); });
