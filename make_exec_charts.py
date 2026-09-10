"""Light Claude-palette pies/bars for the memo and deck."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt

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


def _blend_vehicles() -> None:
    """Paint cream JPEG backdrops to the same paper colour so they sit on slides cleanly."""
    from PIL import Image
    import numpy as np

    dest = FIG / "vehicles"
    paper = np.array([0xFA, 0xF7, 0xF2], dtype=np.int16)
    for name in ("auto.png", "cab.png", "scooty.png", "bike.png"):
        p = dest / name
        if not p.exists():
            continue
        im = Image.open(p).convert("RGB")
        arr = np.array(im, dtype=np.int16)
        dist = np.abs(arr - np.array([250, 245, 235])).sum(axis=2)
        mask = dist < 42
        arr[mask] = paper
        Image.fromarray(arr.astype(np.uint8)).resize((512, 512), Image.Resampling.LANCZOS).save(p, format="PNG")


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
    _blend_vehicles()
    print("wrote figures/pie_*.png and bar_volume_lost.png")


if __name__ == "__main__":
    main()
