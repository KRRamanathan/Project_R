"""Light-theme pies/bars for the memo and pptxgen deck."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
FIG = ROOT / "figures"
FIG.mkdir(exist_ok=True)

NAVY = "#1E2761"
CORAL = "#F96167"
TEAL = "#1C7293"
ICE = "#CADCFC"
LIGHT = "#F2F4FA"
YELLOW = "#FFC400"
GREY = "#6B7084"
GREEN = "#2A9D8F"

plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["axes.facecolor"] = LIGHT
plt.rcParams["savefig.facecolor"] = LIGHT
plt.rcParams["figure.facecolor"] = LIGHT


def _pie(path: Path, labels, sizes, colors, title: str) -> None:
    fig, ax = plt.subplots(figsize=(4.2, 3.4), dpi=140, facecolor=LIGHT)
    ax.set_facecolor(LIGHT)
    wedges, texts, autotexts = ax.pie(
        sizes,
        labels=None,
        colors=colors,
        startangle=90,
        wedgeprops={"width": 0.52, "edgecolor": "white", "linewidth": 2},
        autopct=lambda p: f"{p:.0f}%",
        pctdistance=0.72,
    )
    for t in autotexts:
        t.set_fontsize(9)
        t.set_color(NAVY)
        t.set_fontweight("bold")
    ax.legend(
        wedges,
        labels,
        loc="center left",
        bbox_to_anchor=(0.98, 0.5),
        frameon=False,
        fontsize=8,
        labelcolor=NAVY,
    )
    ax.set_title(title, color=NAVY, fontsize=11, fontweight="bold", pad=8)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight", pad_inches=0.08)
    plt.close()


def _bar_lost(path: Path) -> None:
    labels = ["DL", "RC", "Aadhaar", "Permit", "Fitness", "Insurance"]
    vals = [1166, 5405, 1540, 2616, 2653, 3289]
    colors = [GREY, CORAL, GREY, GREY, GREY, TEAL]
    fig, ax = plt.subplots(figsize=(6.2, 3.2), dpi=140, facecolor=LIGHT)
    ax.set_facecolor(LIGHT)
    ax.barh(labels[::-1], vals[::-1], color=colors[::-1], height=0.72)
    ax.set_xlabel("Captains lost (mature ∩ events)", color=GREY, fontsize=9)
    ax.tick_params(colors=NAVY, labelsize=9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(ICE)
    ax.spines["bottom"].set_color(ICE)
    ax.set_title("Where volume is lost — RC and Insurance dominate", color=NAVY, fontsize=11, fontweight="bold")
    for y, v in enumerate(vals[::-1]):
        ax.text(v + 80, y, f"{v:,}", va="center", fontsize=8, color=NAVY)
    ax.set_xlim(0, 6200)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight", pad_inches=0.08)
    plt.close()


def main() -> None:
    _pie(
        FIG / "pie_c1.png",
        ["C1a RC grace ~134/mo", "C1b Insurance UX ~50/mo"],
        [134, 50],
        [TEAL, CORAL],
        "Of the ~180 extra approved / month",
    )
    _pie(
        FIG / "pie_airport_night.png",
        ["21:00–03:59 (84%)", "Rest of day (16%)"],
        [84, 16],
        [CORAL, ICE],
        "Airport unfulfilled volume by clock",
    )
    _pie(
        FIG / "pie_rc_capture.png",
        ["Capture-only (1,637)", "Other RC loss (3,768)"],
        [1637, 3768],
        [CORAL, ICE],
        "RC stage loss — only the photo slice is C1a",
    )
    _pie(
        FIG / "pie_ara_elig.png",
        ["No return in 20m (89%)", "Got a return (11%)"],
        [89.31, 10.69],
        [TEAL, YELLOW],
        "ARA pays only the unpaid night-suburban legs",
    )
    _pie(
        FIG / "pie_c1b.png",
        ["C1b UX (411)", "Other Insurance (2,878)"],
        [411, 3289 - 411],
        [TEAL, ICE],
        "Insurance leftovers — only the photo slice is C1b",
    )
    _bar_lost(FIG / "bar_volume_lost.png")
    print("wrote figures/pie_*.png and bar_volume_lost.png")


if __name__ == "__main__":
    main()
