const pptxgen = require("pptxgenjs");
const fs = require("fs");
const path = require("path");

const NAVY     = "1E2761";
const CORAL    = "E85D4C";
const ORANGE   = "FF8A3D";
const TEAL     = "C45C26";
const ICE      = "FFE8C2";
const GREY     = "6B4A2A";
const LIGHTBG  = "FFC400";
const BORDER   = "E07A2F";
const WHITE    = "FFFFFF";
const YELLOW   = "FFC400";
const GREEN    = "E85D4C";
const REDBG    = "E85D4C";
const ORANGEBG = "FF8A3D";

function png(rel) {
  return "image/png;base64," + fs.readFileSync(path.join(__dirname, rel)).toString("base64");
}
const PIE180 = png("figures/pie_c1.png");
const PIEAIR = png("figures/pie_airport_night.png");
const PIERC  = png("figures/pie_rc_capture.png");
const PIEC1B = png("figures/pie_c1b.png");
const BARVL  = png("figures/bar_volume_lost.png");

const FOOTER_L = "Rapido Supply  ·  Captain Onboarding & Airport Supply";
const FOOTER_R = "Ramanathan K R   ·   Rapido Data Science Assessment";

let pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
const SW = 13.333, SH = 7.5;

function footer(slide, pageNum) {
  slide.addText(FOOTER_L, { x: 0.5, y: SH - 0.42, w: 7.0, h: 0.3, fontFace: "Calibri", fontSize: 8.5, color: GREY, align: "left", isTextBox: true, margin: 0 });
  slide.addText(FOOTER_R + "     " + pageNum + " / 6", { x: SW - 6.5, y: SH - 0.42, w: 6.0, h: 0.3, fontFace: "Calibri", fontSize: 8.5, color: GREY, align: "right", isTextBox: true, margin: 0 });
}

function kicker(slide, text, color, x, y) {
  slide.addText(text.toUpperCase(), {
    x: x || 0.6, y: y || 0.38, w: 12, h: 0.28,
    fontFace: "Calibri", fontSize: 11, bold: true,
    color: color, charSpacing: 2.5, align: "left", isTextBox: true, margin: 0
  });
}

function statCard(slide, x, y, w, h, num, label, color, dark) {
  const bg = dark ? NAVY : WHITE;
  const border = dark ? { type: "none" } : { color: BORDER, width: 1 };
  slide.addShape("roundRect", { x, y, w, h, rectRadius: 0.09,
    fill: { color: bg }, line: border });
  slide.addText(num, { x: x + 0.15, y: y + 0.12, w: w - 0.3, h: h * 0.52,
    fontFace: "Cambria", fontSize: h > 1.0 ? 28 : 22, bold: true,
    color: color, valign: "middle", isTextBox: true, margin: 0 });
  slide.addText(label, { x: x + 0.15, y: y + h * 0.52, w: w - 0.3, h: h * 0.44,
    fontFace: "Calibri", fontSize: 9, color: dark ? ICE : "555555",
    lineSpacingMultiple: 1.1, isTextBox: true, margin: 0 });
}

function addPie180(slide, x, y, w, h) {
  slide.addChart(pres.ChartType.doughnut, [
    { name: "of ~180/mo", labels: ["C1a RC ~134", "C1b Insurance ~50"], values: [134, 50] },
  ], {
    x, y, w, h,
    chartColors: [TEAL, CORAL],
    showLegend: true, legendPos: "b", legendFontSize: 9, legendColor: "444444",
    showPercent: true,
    chartArea: { fill: { color: WHITE } },
  });
}

function addPieNight(slide, x, y, w, h) {
  slide.addChart(pres.ChartType.pie, [
    { name: "Airport unfulfilled", labels: ["21:00–03:59", "Rest of day"], values: [84, 16] },
  ], {
    x, y, w, h,
    chartColors: [CORAL, YELLOW],
    showLegend: true, legendPos: "b", legendFontSize: 9, legendColor: "444444",
    showPercent: true,
    chartArea: { fill: { color: WHITE } },
  });
}

function addPieRc(slide, x, y, w, h) {
  slide.addChart(pres.ChartType.doughnut, [
    { name: "RC lost", labels: ["Capture-only 1,637", "Other RC 3,768"], values: [1637, 3768] },
  ], {
    x, y, w, h,
    chartColors: [CORAL, ICE],
    showLegend: true, legendPos: "b", legendFontSize: 9, legendColor: "444444",
    showPercent: true,
    chartArea: { fill: { color: WHITE } },
  });
}

function addFunnelChart(slide, x, y, w, h) {
  const data = [
    { name: "Approved", labels: ["RC","Insurance","DL","Aadhaar","Permit","Fitness"], values: [3946, 3289, 2283, 2045, 1428, 775] },
    { name: "Lost",     labels: ["RC","Insurance","DL","Aadhaar","Permit","Fitness"], values: [5405, 3289, 1166, 1540, 2616, 2653] }
  ];
  slide.addChart(pres.ChartType.bar, data, {
    x, y, w, h,
    barDir: "bar",
    barGrouping: "stacked",
    chartColors: [TEAL, CORAL],
    showLegend: true, legendPos: "b", legendFontSize: 9, legendColor: "444444",
    showValue: false,
    catAxisLabelColor: "444444", catAxisLabelFontSize: 9,
    valAxisLabelColor: "888888", valAxisLabelFontSize: 8,
    valGridLine: { color: "E8E8E8", size: 0.5 },
    catGridLine: { style: "none" },
    plotAreaBorderColor: "FFFFFF",
    dataLabelColor: WHITE, dataLabelFontSize: 8,
  });
}

function addWaterfallChart(slide, x, y, w, h) {
  const data = [
    { name: "Captain Recovery Estimate (/month)",
      labels: ["Baseline\nApproved", "RC Grace\nWindow (+)", "Insurance\nUX (+)", "New\nTotal"],
      values: [3946, 134, 50, 4130] }
  ];
  slide.addChart(pres.ChartType.bar, data, {
    x, y, w, h,
    barDir: "col",
    barGrouping: "clustered",
    chartColors: [NAVY, GREEN, GREEN, TEAL],
    showLegend: false,
    showValue: true, dataLabelFontSize: 9, dataLabelColor: "333333",
    catAxisLabelColor: "444444", catAxisLabelFontSize: 8,
    valAxisLabelColor: "888888", valAxisLabelFontSize: 8,
    valGridLine: { color: "E8E8E8", size: 0.5 },
    catGridLine: { style: "none" },
    plotAreaBorderColor: "FFFFFF",
  });
}

function addRetryChart(slide, x, y, w, h) {
  const data = [
    { name: "RC Pass Rate (%)",        labels: ["1st try","2nd try","3rd try"], values: [65.3, 68.4, 74.1] },
    { name: "Insurance Pass Rate (%)", labels: ["1st try","2nd try","3rd try"], values: [67, 74, 76] }
  ];
  slide.addChart(pres.ChartType.line, data, {
    x, y, w, h,
    chartColors: [CORAL, TEAL],
    showLegend: true, legendPos: "b", legendFontSize: 9, legendColor: "444444",
    showValue: true, dataLabelFontSize: 8.5, dataLabelColor: "333333",
    lineSize: 2.5,
    catAxisLabelColor: "444444", catAxisLabelFontSize: 9,
    valAxisLabelColor: "888888", valAxisLabelFontSize: 8,
    valAxisMinVal: 55, valAxisMaxVal: 85,
    valGridLine: { color: "E8E8E8", size: 0.5 },
    catGridLine: { style: "none" },
    plotAreaBorderColor: "FFFFFF",
  });
}

function addAirportHourlyChart(slide, x, y, w, h) {
  const hours = ["18","19","20","21","22","23","00","01","02","03","04","05"];
  const data = [
    { name: "Captains Online", labels: hours, values: [37, 34, 28, 18, 14, 13, 13, 12, 11, 13, 18, 29] },
    { name: "Demand Index",    labels: hours, values: [45, 50, 55, 70, 75, 72, 65, 60, 55, 50, 40, 35] }
  ];
  slide.addChart(pres.ChartType.line, data, {
    x, y, w, h,
    chartColors: [YELLOW, CORAL],
    showLegend: true, legendPos: "b", legendFontSize: 9, legendColor: "444444",
    showValue: false,
    lineSize: 2.5,
    catAxisLabelColor: "444444", catAxisLabelFontSize: 8.5,
    valAxisLabelColor: "888888", valAxisLabelFontSize: 8,
    valGridLine: { color: "E8E8E8", size: 0.5 },
    catGridLine: { style: "none" },
    plotAreaBorderColor: "FFFFFF",
  });
}

function addCampaignChart(slide, x, y, w, h) {
  const data = [
    { name: "Completion Rate (%)",
      labels: ["Naive: got\ncampaign","Naive: never\ngot it","Honest: clicked","Honest:\nnot clicked"],
      values: [29, 11, 28.3, 29.8] }
  ];
  slide.addChart(pres.ChartType.bar, data, {
    x, y, w, h,
    barDir: "col",
    barGrouping: "clustered",
    chartColors: [CORAL, GREY, TEAL, GREY],
    showLegend: false,
    showValue: true, dataLabelFontSize: 9, dataLabelColor: "333333",
    catAxisLabelColor: "444444", catAxisLabelFontSize: 8,
    valAxisLabelColor: "888888", valAxisLabelFontSize: 8,
    valAxisMinVal: 0, valAxisMaxVal: 40,
    valGridLine: { color: "E8E8E8", size: 0.5 },
    catGridLine: { style: "none" },
    plotAreaBorderColor: "FFFFFF",
  });
}

function addARAChart(slide, x, y, w, h) {
  const data = [
    { name: "₹/leg payout scenario",
      labels: ["Low\n(80%)", "Central\n(100%)", "High\n(120%)"],
      values: [69, 86, 103] }
  ];
  slide.addChart(pres.ChartType.bar, data, {
    x, y, w, h,
    barDir: "col",
    barGrouping: "clustered",
    chartColors: [TEAL, NAVY, CORAL],
    showLegend: false,
    showValue: true, dataLabelFontSize: 9.5, dataLabelColor: WHITE,
    catAxisLabelColor: "444444", catAxisLabelFontSize: 9,
    valAxisLabelColor: "888888", valAxisLabelFontSize: 8,
    valAxisMinVal: 0, valAxisMaxVal: 130,
    valGridLine: { color: "E8E8E8", size: 0.5 },
    catGridLine: { style: "none" },
    plotAreaBorderColor: "FFFFFF",
  });
}

{
  let s = pres.addSlide();
  s.background = { color: YELLOW };

  s.addShape("ellipse", { x: 10.2, y: -2.0, w: 6.0, h: 6.0, fill: { color: ORANGE }, line: { type: "none" } });
  s.addShape("ellipse", { x: -2.2, y: 4.8, w: 5.0, h: 5.0, fill: { color: CORAL }, line: { type: "none" } });
  s.addShape("ellipse", { x: 7.8, y: 3.5, w: 2.5, h: 2.5, fill: { color: ORANGE }, line: { type: "none" } });

  s.addText("RAPIDO DATA SCIENCE ASSESSMENT", {
    x: 0.9, y: 1.45, w: 10.0, h: 0.38,
    fontFace: "Calibri", fontSize: 13.5, bold: true,
    color: NAVY, charSpacing: 3, isTextBox: true, margin: 0
  });

  s.addText("Captain onboarding leak\n& overnight airport supply", {
    x: 0.85, y: 1.88, w: 9.5, h: 1.7,
    fontFace: "Cambria", fontSize: 36, bold: true, color: NAVY,
    align: "left", lineSpacingMultiple: 1.15, isTextBox: true, margin: 0
  });

  s.addText("Findings and recommendations for the Head of Supply — where the extra ~180 approved captains a month come from, and why overnight airport supply is an economics problem, not a headcount one.", {
    x: 0.9, y: 3.55, w: 8.8, h: 0.85,
    fontFace: "Calibri", fontSize: 13.5, color: NAVY,
    align: "left", lineSpacingMultiple: 1.3, isTextBox: true, margin: 0
  });

  s.addShape("line", { x: 0.9, y: 4.6, w: 3.0, h: 0, line: { color: YELLOW, width: 2.5 } });

  s.addText("Ramanathan K R", {
    x: 0.9, y: 4.78, w: 6, h: 0.48,
    fontFace: "Cambria", fontSize: 20, bold: true, color: NAVY, isTextBox: true, margin: 0
  });
  s.addText("Data Science Assessment  ·  10 September 2026  ·  Data extract as of 30 Jun 2026, 23:59 IST", {
    x: 0.9, y: 5.28, w: 9.5, h: 0.32,
    fontFace: "Calibri", fontSize: 11, color: GREY, isTextBox: true, margin: 0
  });

  const iconY = 5.78, iconSz = 1.1;

  s.addText("25k signups  ·  RC  ·  Insurance  ·  Airport nights", {
    x: 8.3, y: iconY + 0.38, w: 4.5, h: 0.45,
    fontFace: "Calibri", fontSize: 10.5, italic: true, color: GREY,
    align: "right", isTextBox: true, margin: 0
  });
}

{
  let s = pres.addSlide();
  s.background = { color: ORANGEBG };
  kicker(s, "Captain onboarding — the headline", NAVY);

  s.addText("One broken capture step costs ~180 captains/month.", {
    x: 0.6, y: 0.72, w: 9.5, h: 0.82,
    fontFace: "Cambria", fontSize: 26, bold: true, color: NAVY, isTextBox: true, margin: 0
  });

  s.addText([
    { text: "Two capture-quality fixes on RC and Insurance ", options: { color: NAVY, bold: true } },
    { text: "— not a mix of five things — recover ", options: { color: "3A2208" } },
    { text: "~180 additional approved captains/month", options: { color: NAVY, bold: true } },
    { text: " at medium confidence.", options: { color: "3A2208" } }
  ], { x: 0.6, y: 1.5, w: 9.2, h: 0.58, fontFace: "Calibri", fontSize: 13, lineSpacingMultiple: 1.25, isTextBox: true, margin: 0 });

  s.addShape("roundRect", { x: 0.55, y: 2.2, w: 7.5, h: 4.35,
    rectRadius: 0.09, fill: { color: WHITE }, line: { type: "none" } });
  s.addText("Split of the ~180  (disjoint C1a + C1b)", {
    x: 0.75, y: 2.3, w: 7.1, h: 0.32,
    fontFace: "Calibri", fontSize: 10, bold: true, color: NAVY, isTextBox: true, margin: 0
  });
  s.addImage({ data: PIE180, x: 0.75, y: 2.55, w: 7.1, h: 3.8 });

  const statX = 8.3, statW = 4.45;
  statCard(s, statX, 2.2, statW, 1.35, "98.7%", "of mature approved captains take a first trip (3,895 / 3,946) — documents are the bottleneck, not first-order.", CORAL, true);
  statCard(s, statX, 3.68, statW, 1.18, "~134/mo", "Recovered from an RC in-person grace window (C1a)", YELLOW, true);
  statCard(s, statX, 4.98, statW, 1.18, "~50/mo", "Recovered from Insurance guided capture UX fix (C1b)", GREEN, true);

  footer(s, 1, true);
  s.addNotes("Talk track (2 min): ~180, medium confidence (~134 RC + ~50 Insurance). These are not hollow approvals — 98.7% of approved captains take a first trip. Documents are the bottleneck.");
}

{
  let s = pres.addSlide();
  s.background = { color: LIGHTBG };
  kicker(s, "Root cause", CORAL);

  s.addText("RC and Insurance are failing as photographs, not documents", {
    x: 0.6, y: 0.72, w: 12.0, h: 0.62,
    fontFace: "Cambria", fontSize: 23, bold: true, color: NAVY, isTextBox: true, margin: 0
  });
  s.addText("Capture-class failures (blur, weak OCR, illegibility) dominate RC and Insurance, and later attempts pass MORE often. That is the signature of a capture / UX problem, not an eligibility one.", {
    x: 0.6, y: 1.36, w: 12.0, h: 0.52,
    fontFace: "Calibri", fontSize: 12.5, color: "444444",
    lineSpacingMultiple: 1.2, isTextBox: true, margin: 0
  });

  s.addShape("roundRect", { x: 0.55, y: 2.0, w: 6.0, h: 4.25,
    rectRadius: 0.08, fill: { color: WHITE }, line: { color: BORDER, width: 1 } });
  s.addText("RC loss: only the photo slice is C1a", {
    x: 0.72, y: 2.1, w: 5.65, h: 0.28,
    fontFace: "Calibri", fontSize: 9.5, bold: true, color: NAVY, isTextBox: true, margin: 0
  });
  s.addImage({ data: PIERC, x: 0.7, y: 2.38, w: 5.7, h: 3.7 });

  s.addShape("roundRect", { x: 6.75, y: 2.0, w: 6.05, h: 4.25,
    rectRadius: 0.08, fill: { color: WHITE }, line: { color: BORDER, width: 1 } });
  s.addText("Insurance leftovers — only 411 are C1b", {
    x: 6.92, y: 2.1, w: 5.7, h: 0.28,
    fontFace: "Calibri", fontSize: 9.5, bold: true, color: NAVY, isTextBox: true, margin: 0
  });
  s.addImage({ data: PIEC1B, x: 6.9, y: 2.38, w: 5.75, h: 3.7 });

  s.addShape("roundRect", { x: 0.55, y: 6.42, w: 12.25, h: 0.62,
    rectRadius: 0.06, fill: { color: NAVY }, line: { type: "none" } });
  s.addText([
    { text: "1,637 RC ", options: { bold: true, color: YELLOW } },
    { text: "and ", options: { color: ICE } },
    { text: "411 Insurance ", options: { bold: true, color: YELLOW } },
    { text: "captains are capture-only fails — isolated from eligibility reasons (expired, duplicate, wrong type). DL (1,166) is 100% uploaded-fail and cannot be deferred.", options: { color: ICE } }
  ], { x: 0.75, y: 6.42, w: 11.85, h: 0.62,
    fontFace: "Calibri", fontSize: 10.5, valign: "middle",
    lineSpacingMultiple: 1.1, isTextBox: true, margin: 0 });

  footer(s, 2, false);
  s.addNotes("RC and Insurance failures are photos/OCR. Retry pass rates rise each attempt — that is the capture signature. Other stages are real loss, different fix.");
}

{
  let s = pres.addSlide();
  s.background = { color: LIGHTBG };
  kicker(s, "The fix", CORAL);

  s.addText("One recommendation, two sub-actions — RC defers, Insurance doesn't", {
    x: 0.6, y: 0.72, w: 12.0, h: 0.58,
    fontFace: "Cambria", fontSize: 22, bold: true, color: NAVY, isTextBox: true, margin: 0
  });

  function fixCard(x, tag, tagColor, title, rows, footerNote) {
    s.addShape("roundRect", { x, y: 1.48, w: 6.0, h: 5.25,
      rectRadius: 0.1, fill: { color: WHITE }, line: { color: BORDER, width: 1 } });

    s.addShape("roundRect", { x: x + 0.3, y: 1.7, w: 1.6, h: 0.38,
      rectRadius: 0.19, fill: { color: NAVY }, line: { type: "none" } });
    s.addText(tag, { x: x + 0.3, y: 1.7, w: 1.6, h: 0.38,
      fontFace: "Calibri", fontSize: 11.5, bold: true,
      color: tagColor, align: "center", valign: "middle", isTextBox: true, margin: 0 });

    s.addText(title, { x: x + 0.3, y: 2.18, w: 5.45, h: 0.55,
      fontFace: "Cambria", fontSize: 14.5, bold: true, color: NAVY,
      lineSpacingMultiple: 1.1, isTextBox: true, margin: 0 });

    let ry = 2.82;
    rows.forEach(([label, val, valColor]) => {
      s.addText([
        { text: label + ":  ", options: { bold: true, color: TEAL } },
        { text: val, options: { color: valColor || "333333" } }
      ], { x: x + 0.3, y: ry, w: 5.45, h: 0.56,
        fontFace: "Calibri", fontSize: 10.5, lineSpacingMultiple: 1.15, isTextBox: true, margin: 0 });
      ry += 0.58;
    });

    if (footerNote) {
      s.addShape("roundRect", { x: x + 0.15, y: 6.12, w: 5.7, h: 0.48,
        rectRadius: 0.06, fill: { color: LIGHTBG }, line: { type: "none" } });
      s.addText(footerNote, { x: x + 0.3, y: 6.12, w: 5.5, h: 0.48,
        fontFace: "Calibri", fontSize: 8.8, italic: true, color: GREY,
        valign: "middle", lineSpacingMultiple: 1.1, isTextBox: true, margin: 0 });
    }
  }

  fixCard(0.55, "C1a — RC", YELLOW, "Provisional activation\n10-day in-person grace window", [
    ["Who",          "1,637 RC capture-only fails (~300/mo)"],
    ["Why defer",    "Vehicle identity — no passenger-liability exposure"],
    ["Show-up",      "40 / 60 / 80% × 74–78% pass rate"],
    ["Central case", "~134/month additional approved", CORAL],
    ["Needs",        "Legal + Trust & Safety sign-off on deferral"]
  ], "If remaining docs still bind: P(approved | passed RC) = 27% → ~36/month (Legal ask)");

  fixCard(6.78, "C1b — Insurance", GREEN, "Guided capture UX\n— no deferral possible", [
    ["Who",          "411 Insurance capture-only fails (~75/mo)"],
    ["Why no defer", "Liability document — must clear before first ride"],
    ["Retry rates",  "67.4% → 73.8% → 76.4% pass on own retry"],
    ["Central case", "~46–52/month additional approved", CORAL],
    ["Needs",        "Engineering UX only — no sign-off required"]
  ], "Ship C1b this week. Start Legal scoping on C1a in parallel. Same camera UX can reuse on DL / Aadhaar / Permit / Fitness — not added to 180.");

  footer(s, 3, false);
  s.addNotes("C1b this week — no Legal needed. C1a needs Legal. If remaining docs bind after RC, C1a shrinks toward ~36/month — that is the question to scope.");
}

{
  let s = pres.addSlide();
  s.background = { color: REDBG };
  kicker(s, "Airport supply", YELLOW);

  s.addText("Overnight airport is a compounding economics problem, not a headcount problem", {
    x: 0.6, y: 0.72, w: 12.0, h: 0.72,
    fontFace: "Cambria", fontSize: 21, bold: true, color: WHITE, isTextBox: true, margin: 0
  });

  s.addShape("roundRect", { x: 0.55, y: 1.62, w: 6.0, h: 3.85,
    rectRadius: 0.08, fill: { color: WHITE }, line: { type: "none" } });
  s.addText("When the pain sits (unfulfilled volume)", {
    x: 0.72, y: 1.72, w: 5.65, h: 0.28,
    fontFace: "Calibri", fontSize: 9, bold: true, color: NAVY, isTextBox: true, margin: 0 });
  s.addImage({ data: PIEAIR, x: 0.7, y: 1.95, w: 5.7, h: 3.35 });

  s.addShape("roundRect", { x: 6.75, y: 1.62, w: 6.05, h: 3.85,
    rectRadius: 0.08, fill: { color: WHITE }, line: { type: "none" } });
  s.addText("ARA monthly payout estimate (₹k/month) at ₹35.4/leg", {
    x: 6.92, y: 1.72, w: 5.7, h: 0.28,
    fontFace: "Calibri", fontSize: 9, bold: true, color: NAVY, isTextBox: true, margin: 0 });
  addARAChart(s, 6.85, 1.95, 5.8, 3.3);

  const sy = 5.62;
  const sW = 3.88;
  [
    ["40%", "airport demand unfulfilled vs ~3% elsewhere", CORAL],
    ["84%", "of night gap sits in 21:00–03:59 — only ~13 captains vs ~37 by day", YELLOW],
    ["₹35.4", "per eligible leg = derived ARA payout (not 30% of fare = ₹105)", ICE]
  ].forEach(([n, d, c], i) => {
    const sx = 0.55 + i * (sW + 0.17);
    s.addShape("roundRect", { x: sx, y: sy, w: sW, h: 1.42,
      rectRadius: 0.07, fill: { color: NAVY }, line: { type: "none" } });
    s.addText(n, { x: sx + 0.15, y: sy + 0.1, w: sW - 0.3, h: 0.55,
      fontFace: "Cambria", fontSize: 24, bold: true, color: c, isTextBox: true, margin: 0 });
    s.addText(d, { x: sx + 0.15, y: sy + 0.6, w: sW - 0.3, h: 0.72,
      fontFace: "Calibri", fontSize: 9.2, color: ICE,
      lineSpacingMultiple: 1.15, isTextBox: true, margin: 0 });
  });

  footer(s, 4, true);
  s.addNotes("Airport: the answer is ARA, not headcount. Two independent penalties — suburban backhaul and overnight return collapse. Mix does not shift after dark. New hires inherit both penalties.");
}

{
  let s = pres.addSlide();
  s.background = { color: LIGHTBG };
  kicker(s, "What doesn't work — and how easy it is to be fooled", CORAL);

  s.addText("A campaign with 0pp lift, and a gap we must not bank", {
    x: 0.6, y: 0.72, w: 12.0, h: 0.56,
    fontFace: "Cambria", fontSize: 22, bold: true, color: NAVY, isTextBox: true, margin: 0
  });

  s.addShape("roundRect", { x: 0.55, y: 1.45, w: 5.95, h: 4.55,
    rectRadius: 0.1, fill: { color: WHITE }, line: { color: BORDER, width: 1 } });
  s.addText("CAMP_WA_002 — WhatsApp campaign", {
    x: 0.75, y: 1.58, w: 4.75, h: 0.45,
    fontFace: "Cambria", fontSize: 14, bold: true, color: NAVY, isTextBox: true, margin: 0 });
  s.addText("The 29% vs 11% headline is targeting, not effect.", {
    x: 0.75, y: 2.0, w: 5.5, h: 0.35,
    fontFace: "Calibri", fontSize: 10.5, bold: true, color: CORAL, isTextBox: true, margin: 0 });
  addCampaignChart(s, 0.65, 2.32, 5.7, 2.7);
  s.addText("Honest comparison: clicked vs not-clicked (delivered only) = −1.5pp; 95% CI [−3.6, +0.6]. That is 0pp lift. Do not fund 5×.", {
    x: 0.75, y: 5.05, w: 5.5, h: 0.65,
    fontFace: "Calibri", fontSize: 9.5, color: "444444",
    lineSpacingMultiple: 1.2, isTextBox: true, margin: 0 });
  s.addText("~30% of recipients also got another campaign — confounding further inflated.", {
    x: 0.75, y: 5.65, w: 5.5, h: 0.28,
    fontFace: "Calibri", fontSize: 9, italic: true, color: GREY, isTextBox: true, margin: 0 });

  s.addShape("roundRect", { x: 6.75, y: 1.45, w: 6.05, h: 4.55,
    rectRadius: 0.1, fill: { color: WHITE }, line: { color: BORDER, width: 1 } });
  s.addText("Field vs. self-serve gap — do not double-count", {
    x: 6.95, y: 1.58, w: 4.9, h: 0.45,
    fontFace: "Cambria", fontSize: 14, bold: true, color: NAVY, isTextBox: true, margin: 0 });

  const bullets = [
    ["Mechanical ceiling if app/paid converted like field:", "128–256 additional/month", CORAL],
    ["But field teams recruit in person —", "extract cannot separate who they recruit from how they onboard", "333333"],
    ["726 of the C1a RC group are the same self-serve captains this gap already counts —", "do not add 180 + 128–256", CORAL],
    ["Fos abandonment after Fitness:", "26% vs paid 43% — in-person assist, not WhatsApp", "333333"],
    ["Correct move:", "Randomised assisted-onboarding pilot on app/paid signups (~900 per arm to detect a 5pp lift)", TEAL],
  ];

  let by = 2.15;
  bullets.forEach(([label, val, vc]) => {
    s.addShape("ellipse", { x: 6.85, y: by + 0.08, w: 0.13, h: 0.13, fill: { color: CORAL }, line: { type: "none" } });
    s.addText([
      { text: label + " ", options: { bold: true, color: "333333" } },
      { text: val, options: { color: vc } }
    ], { x: 7.08, y: by, w: 5.5, h: 0.62,
      fontFace: "Calibri", fontSize: 10.2,
      lineSpacingMultiple: 1.12, isTextBox: true, margin: 0 });
    by += 0.66;
  });

  s.addShape("roundRect", { x: 0.55, y: 6.12, w: 12.25, h: 0.9,
    rectRadius: 0.07, fill: { color: NAVY }, line: { type: "none" } });
  s.addText([
    { text: "Correct move:  ", options: { bold: true, color: YELLOW } },
    { text: "Send/no-send RCT on RC-cleared self-serve captains, excl. overlap.  ", options: { color: ICE } },
    { text: "Randomised assisted-onboarding pilot", options: { bold: true, color: YELLOW } },
    { text: " on app/paid signups (~900/arm to detect a 5pp lift).", options: { color: ICE } }
  ], { x: 0.78, y: 6.12, w: 11.75, h: 0.9,
    fontFace: "Calibri", valign: "middle",
    lineSpacingMultiple: 1.15, isTextBox: true, margin: 0 });

  footer(s, 5, false);
  s.addNotes("Trap: 29% vs 11% is targeting, not lift. Honest contrast = 0pp. 128–256 field gap overlaps 726 of the C1a captains. Do not add these numbers.");
}

{
  let s = pres.addSlide();
  s.background = { color: ORANGEBG };
  kicker(s, "Recommendations & decision points", NAVY);

  s.addText("Ranked by monthly impact. The campaign call is the fastest yes.", {
    x: 0.6, y: 0.72, w: 12.0, h: 0.56,
    fontFace: "Cambria", fontSize: 22, bold: true, color: NAVY, isTextBox: true, margin: 0
  });

  const rows = [
    {
      num: "1", color: CORAL,
      what: "C1a: 10-day RC in-person grace window\nC1b: Insurance upload UX (ship this week)",
      impact: "~180/mo approved",
      risk: "C1a: Legal + T&S sign-off\nC1b: engineering only, no sign-off",
      watch: "Approved split by cohort"
    },
    {
      num: "2", color: YELLOW,
      what: "Airport Return Assurance at ₹35.4/leg (derived payout — not 30% of fare)",
      impact: "₹69k–103k/mo payout; night gap closed",
      risk: "Sampled trips ≠ city P&L. Rest-suburban only.",
      watch: "Return-in-20min, cancel rate, 4-wk payout run-rate"
    },
    {
      num: "3", color: GREEN,
      what: "Stop CAMP_WA_002 5× scaling; run send/no-send RCT on RC-cleared self-serve captains",
      impact: "Cost avoided + causal answer in 4–6 weeks",
      risk: "Near zero — a redirection, not new spend",
      watch: "Aadhaar-pass, approved (ITT)"
    }
  ];

  let ry = 1.52;
  const rh = 1.2;
  rows.forEach(({ num, color, what, impact, risk, watch }) => {
    s.addShape("roundRect", { x: 0.55, y: ry, w: 12.25, h: rh - 0.12,
      rectRadius: 0.08, fill: { color: NAVY }, line: { type: "none" } });
    s.addShape("ellipse", { x: 0.75, y: ry + 0.32, w: 0.42, h: 0.42,
      fill: { color: color }, line: { type: "none" } });
    s.addText(num, { x: 0.75, y: ry + 0.32, w: 0.42, h: 0.42,
      fontFace: "Cambria", fontSize: 15, bold: true,
      color: WHITE, align: "center", valign: "middle", isTextBox: true, margin: 0 });
    s.addText(what, { x: 1.4, y: ry + 0.06, w: 5.05, h: rh - 0.2,
      fontFace: "Calibri", fontSize: 10.8, bold: true,
      color: WHITE, valign: "middle", lineSpacingMultiple: 1.1, isTextBox: true, margin: 0 });
    s.addText(impact, { x: 6.6, y: ry + 0.06, w: 2.35, h: rh - 0.2,
      fontFace: "Calibri", fontSize: 10.5, bold: true,
      color: color, valign: "middle", lineSpacingMultiple: 1.1, isTextBox: true, margin: 0 });
    s.addText(risk, { x: 9.05, y: ry + 0.06, w: 2.2, h: rh - 0.2,
      fontFace: "Calibri", fontSize: 9, color: ICE,
      valign: "middle", lineSpacingMultiple: 1.1, isTextBox: true, margin: 0 });
    s.addText(watch, { x: 11.35, y: ry + 0.06, w: 1.42, h: rh - 0.2,
      fontFace: "Calibri", fontSize: 8.2, italic: true, color: GREY,
      valign: "middle", lineSpacingMultiple: 1.1, isTextBox: true, margin: 0 });
    ry += rh;
  });

  const hY = 1.38;
  [["Action", 2.45, 4.0], ["Monthly impact", 6.6, 2.35], ["Cost / risk", 9.05, 2.2], ["Watch", 11.35, 1.42]].forEach(([t, x, w]) => {
    s.addText(t.toUpperCase(), { x, y: hY, w, h: 0.22,
      fontFace: "Calibri", fontSize: 7.5, bold: true,
      color: GREY, charSpacing: 1.5, isTextBox: true, margin: 0 });
  });

  const askY = ry + 0.08;
  s.addShape("roundRect", { x: 0.55, y: askY, w: 12.25, h: 1.08,
    rectRadius: 0.07, fill: { color: CORAL }, line: { type: "none" } });
  s.addText([
    { text: "Ask of the room:  ", options: { bold: true, color: WHITE, fontSize: 11.5 } },
    { text: "(1) Ship Insurance capture UX — no need to wait.   (2) Legal scoping on RC deferral, this week.   (3) Kill the 5× WhatsApp paper; stand up the RCT.   (4) Four-week ARA pilot at the derived ₹35.4, not 30% of fare.", options: { color: WHITE, fontSize: 10.5 } }
  ], { x: 0.8, y: askY, w: 11.7, h: 1.08,
    fontFace: "Calibri", valign: "middle",
    lineSpacingMultiple: 1.2, isTextBox: true, margin: 0 });

  footer(s, 6, true);
  s.addNotes("Ask: C1b → Legal C1a → 4-week ARA → kill 5×. Queue: other-doc camera, then assisted-onboarding RCT.\nIf interrupted twice: show slides 1, 4, and 5.");
}

const outPptx = path.join(__dirname, "DECK.pptx");
pres.writeFile({ fileName: outPptx })
  .then(() => console.log("wrote", outPptx))
  .catch(e => { console.error(e); process.exit(1); });
