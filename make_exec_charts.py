"""Light Claude-palette pies/bars for the memo and deck."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent
FIG = ROOT / "figures"
FIG.mkdir(exist_ok=True)

PAPER = "#FAF7F2"
PEACH = "#F6E4D4"
CREAM = "#F8F1E3"
APRICOT = "#F0C9A0"
GOLD = "#E8B86D"
INK = "#1C1917"
MUTED = "#57534E"

plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["axes.facecolor"] = PAPER
plt.rcParams["savefig.facecolor"] = PAPER
plt.rcParams["figure.facecolor"] = PAPER


def _pie(path: Path, labels, sizes, colors, title: str | None = None) -> None:
    fig, ax = plt.subplots(figsize=(4.6, 3.5), dpi=150, facecolor=PAPER)
    ax.set_facecolor(PAPER)
    wedges, _, autotexts = ax.pie(
        sizes,
        labels=None,
        colors=colors,
        startangle=90,
        wedgeprops={"width": 0.52, "edgecolor": PAPER, "linewidth": 3},
        autopct=lambda p: f"{p:.0f}%",
        pctdistance=0.72,
    )
    for t in autotexts:
        t.set_fontsize(13)
        t.set_color(INK)
        t.set_fontweight("bold")
    ax.legend(
        wedges,
        labels,
        loc="center left",
        bbox_to_anchor=(0.96, 0.5),
        frameon=False,
        fontsize=11,
        labelcolor=INK,
    )
    if title:
        ax.set_title(title, color=INK, fontsize=13, fontweight="bold", pad=10)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight", pad_inches=0.08)
    plt.close()


def _bar_lost(path: Path) -> None:
    labels = ["DL", "RC", "Aadhaar", "Permit", "Fitness", "Insurance"]
    vals = [1166, 5405, 1540, 2616, 2653, 3289]
    colors = [PEACH, GOLD, PEACH, PEACH, PEACH, APRICOT]
    fig, ax = plt.subplots(figsize=(6.4, 3.35), dpi=150, facecolor=PAPER)
    ax.set_facecolor(PAPER)
    ax.barh(labels[::-1], vals[::-1], color=colors[::-1], height=0.72)
    ax.set_xlabel("Captains lost (mature ∩ events)", color=MUTED, fontsize=11)
    ax.tick_params(colors=INK, labelsize=11)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(APRICOT)
    ax.spines["bottom"].set_color(APRICOT)
    ax.set_title(
        "Where volume is lost — RC and Insurance dominate",
        color=INK,
        fontsize=13,
        fontweight="bold",
    )
    for y, v in enumerate(vals[::-1]):
        ax.text(v + 80, y, f"{v:,}", va="center", fontsize=11, color=INK, fontweight="bold")
    ax.set_xlim(0, 6400)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight", pad_inches=0.1)
    plt.close()


def _waterfall() -> None:
    labels = [
        "Started\ndocs",
        "Lost\nDL",
        "Lost RC\n(1,637 C1a)",
        "Lost\nAadhaar",
        "Lost\nPermit",
        "Lost\nFitness",
        "Lost Ins.\n(411 C1b)",
        "Rejected\nafter clear",
        "Approved\ntoday",
    ]
    deltas = [21024, -1166, -5405, -1540, -2616, -2653, -3289, -409, 3946]
    colors = [
        "#1C1917",
        "#C4B5A5",
        GOLD,
        "#C4B5A5",
        "#C4B5A5",
        "#C4B5A5",
        APRICOT,
        "#C4B5A5",
        "#6B8F71",
    ]
    bottoms, heights, running = [], [], 0
    for i, d in enumerate(deltas):
        if i == 0 or i == len(deltas) - 1:
            bottoms.append(0)
            heights.append(d)
            if i == 0:
                running = d
        else:
            bottoms.append(running + d)
            heights.append(-d)
            running = running + d

    fig, ax = plt.subplots(figsize=(13.2, 5.15), dpi=120)
    fig.patch.set_facecolor(PAPER)
    ax.set_facecolor(PAPER)
    x = np.arange(len(labels))
    ax.bar(x, heights, bottom=bottoms, color=colors, width=0.74, zorder=3)
    y_conn = deltas[0]
    for i in range(1, len(deltas) - 1):
        ax.plot([i - 1 + 0.37, i - 0.37], [y_conn, y_conn], color=MUTED, lw=0.7, zorder=2)
        y_conn = y_conn + deltas[i]
    ax.plot(
        [len(deltas) - 2 + 0.37, len(deltas) - 1 - 0.37],
        [y_conn, y_conn],
        color=MUTED,
        lw=0.7,
        zorder=2,
    )
    for i, d in enumerate(deltas):
        ax.text(
            i,
            (d + 350) if i in (0, len(deltas) - 1) else bottoms[i] + heights[i] + 280,
            f"{d:,}",
            ha="center",
            fontsize=9,
            fontweight="bold",
            color=INK,
        )
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=8, color=INK)
    ax.set_ylim(0, 24500)
    ax.set_ylabel("Captains", color=MUTED)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_title(
        "21,024 started documents  →  3,946 approved (18.8%)   ·   recover the coloured slices, not the whole bar",
        loc="left",
        fontsize=11,
        fontweight="bold",
        color=INK,
        pad=8,
    )
    fig.tight_layout()
    fig.savefig(FIG / "funnel_waterfall.png", bbox_inches="tight", facecolor=PAPER)
    plt.close()


def main() -> None:
    _pie(
        FIG / "pie_c1.png",
        ["C1a RC grace ~134/mo", "C1b Insurance UX ~50/mo"],
        [134, 50],
        [GOLD, APRICOT],
    )
    _pie(
        FIG / "pie_airport_night.png",
        ["21:00–03:59 (84%)", "Rest of day (16%)"],
        [84, 16],
        [APRICOT, GOLD],
    )
    _pie(
        FIG / "pie_rc_capture.png",
        ["Capture-only (1,637)", "Other RC loss (3,768)"],
        [1637, 3768],
        [GOLD, PEACH],
    )
    _pie(
        FIG / "pie_c1b.png",
        ["C1b UX (411)", "Other Insurance (2,878)"],
        [411, 3289 - 411],
        [GOLD, PEACH],
    )
    _bar_lost(FIG / "bar_volume_lost.png")
    _waterfall()
    print("wrote figures/pie_*.png, bar_volume_lost.png, funnel_waterfall.png")


if __name__ == "__main__":
    main()
