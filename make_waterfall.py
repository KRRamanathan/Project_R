#!/usr/bin/env python3
"""Funnel waterfall for slide 1. Step 2 volumes, mature ∩ has-doc_events."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

OUT = Path(__file__).resolve().parent / "figures"
OUT.mkdir(exist_ok=True)


def main() -> None:
    # (label, signed delta, color) — first and last are totals from zero
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
        "#1f3a5f",
        "#9a9a9a",
        "#c45c26",
        "#9a9a9a",
        "#9a9a9a",
        "#9a9a9a",
        "#2a6f97",
        "#9a9a9a",
        "#2d6a4f",
    ]

    bottoms = []
    heights = []
    running = 0
    for i, d in enumerate(deltas):
        if i == 0 or i == len(deltas) - 1:
            bottoms.append(0)
            heights.append(d)
            if i == 0:
                running = d
        else:
            bottoms.append(running + d)  # d negative
            heights.append(-d)
            running = running + d

    fig, ax = plt.subplots(figsize=(13.2, 5.15), dpi=120)
    fig.patch.set_facecolor("#f7f4ee")
    ax.set_facecolor("#f7f4ee")
    x = np.arange(len(labels))
    ax.bar(x, heights, bottom=bottoms, color=colors, width=0.74, zorder=3)

    y_conn = deltas[0]
    for i in range(1, len(deltas) - 1):
        ax.plot([i - 1 + 0.37, i - 0.37], [y_conn, y_conn], color="#444", lw=0.7, zorder=2)
        y_conn = y_conn + deltas[i]
    ax.plot(
        [len(deltas) - 2 + 0.37, len(deltas) - 1 - 0.37],
        [y_conn, y_conn],
        color="#444",
        lw=0.7,
        zorder=2,
    )

    for i, d in enumerate(deltas):
        if i == 0 or i == len(deltas) - 1:
            ax.text(i, d + 350, f"{d:,}", ha="center", fontsize=9, fontweight="bold")
        else:
            ax.text(
                i,
                bottoms[i] + heights[i] + 280,
                f"{d:,}",
                ha="center",
                fontsize=8.5,
                fontweight="bold",
                color="#c45c26" if i == 2 else ("#2a6f97" if i == 6 else "#333"),
            )

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylim(0, 24500)
    ax.set_ylabel("Captains")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_title(
        "21,024 started documents  →  3,946 approved (18.8%)   ·   recover the coloured slices, not the whole bar",
        loc="left",
        fontsize=11,
        fontweight="bold",
        pad=8,
    )
    fig.tight_layout()
    path = OUT / "funnel_waterfall.png"
    fig.savefig(path, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
