#!/usr/bin/env python3
"""Figures for the BioHackrXiv MIE-redesign report.

All numbers are transcribed from the durable FINDINGS.md records in the
TogoMCP repository:
  benchmark/ablation/FINDINGS.md           (Figs 1-2)
  benchmark/redesign/release/FINDINGS.md   (Fig 3)
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

OUT = Path(__file__).resolve().parent

INK = "#1c1c1c"
MUTED = "#8a8a8a"
ACCENT = "#0b5394"
HOT = "#a61c1c"
GRID = "#dcdcdc"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 9,
    "axes.edgecolor": INK,
    "axes.labelcolor": INK,
    "text.color": INK,
    "xtick.color": INK,
    "ytick.color": INK,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.dpi": 200,
})


# ---------------------------------------------------------------- Figure 2
def redundancy_arc():
    """Forest plot: the four ablation families on one axis."""
    # (label, estimate, half-CI, family)
    sections = [
        ("common_errors",          +0.65, 0.65),
        ("cross_database_queries", +0.25, 0.77),
        ("architectural_notes",    +0.23, 0.51),
        ("schema_info †",          +0.20, 0.50),
        ("critical_warnings",      +0.14, 0.62),
        ("data_statistics",        +0.07, 0.66),
        ("anti_patterns",          +0.04, 0.40),
        ("cross_references",       -0.06, 0.52),
        ("sample_rdf_entries",     -0.08, 0.63),
        ("sparql_query_examples",  -0.13, 0.57),
        ("shape_expressions",      -0.15, 0.54),
    ]
    groups = [
        ("query †",      +0.20, 0.40),
        ("orientation",  +0.10, 0.52),
        ("guardrails",   +0.04, 0.45),
    ]
    whole = [("whole MIE (no_mie)", +0.93, 0.68)]
    keeps = [
        ("keep query only",       +0.92, 0.54),
        ("keep orientation only", +0.41, 0.89),
        ("keep guardrails only",  +0.12, 0.66),
    ]

    blocks = [
        ("LEAVE ONE SECTION OUT   · necessity, k=11", sections, MUTED),
        ("LEAVE ONE GROUP OUT   · necessity, k=3", groups, MUTED),
        ("REMOVE THE WHOLE MIE   · total value, k=1", whole, HOT),
        ("KEEP ONE GROUP ONLY   · sufficiency, k=3", keeps, ACCENT),
    ]

    rows, labels, weights, data, seps = [], [], [], [], []
    y = 0.0
    for bi, (title, items, colour) in enumerate(blocks):
        if bi:
            seps.append(y + 0.5)
            y -= 0.55
        rows.append(y); labels.append(title); weights.append(("bold", colour))
        y -= 1.0
        for lab, est, ci in items:
            rows.append(y); labels.append("   " + lab); weights.append(("normal", INK))
            data.append((y, est, ci, colour))
            y -= 0.92
        if bi == 1:                       # Σ annotation, directly under the groups
            data.append((y + 0.22, 0.34, None, INK))
        y -= 0.30

    fig, ax = plt.subplots(figsize=(7.4, 7.8))
    ax.axvline(0, color=INK, lw=1.0, zorder=2)
    ax.axvspan(0.88, 0.93, color=HOT, alpha=0.09, zorder=0)

    for yy, est, ci, c in data:
        if ci is None:                    # the sum-of-groups diamond
            ax.plot([est], [yy], "D", ms=5.5, color=c, zorder=4)
            ax.text(est + 0.10, yy, "Σ of the 3 groups = +0.34", fontsize=7.6,
                    va="center", ha="left", style="italic", color=c)
            continue
        sig = (est - ci) > 0
        ax.plot([est - ci, est + ci], [yy, yy], color=c,
                lw=2.2 if sig else 1.3, alpha=1.0 if sig else 0.7,
                solid_capstyle="round", zorder=3)
        ax.plot([est], [yy], "o", ms=7 if sig else 5, color=c,
                mec="white", mew=1.1, zorder=4)
        if sig:
            ax.text(est + ci + 0.10, yy, "✱", color=c, va="center",
                    fontsize=10, fontweight="bold")

    for s in seps:
        ax.axhline(s, color=GRID, lw=0.8, zorder=0)

    ax.set_yticks(rows)
    ax.set_yticklabels(labels, fontsize=8)
    for tick, (w, c) in zip(ax.get_yticklabels(), weights):
        tick.set_fontweight(w)
        tick.set_color(c)
        if w == "bold":
            tick.set_fontsize(7.6)
    ax.set_ylim(min(rows) - 0.8, max(rows) + 0.8)
    ax.set_xlim(-1.0, 1.85)
    ax.set_xticks([-0.5, 0, 0.5, 1.0, 1.5])
    ax.set_xlabel("Effect on judge score (points out of 20) — paired per question, 95% CI",
                  fontsize=8.5)
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="x", color=GRID, lw=0.6, zorder=0)
    ax.set_axisbelow(True)

    ax.set_title("The whole MIE is worth ~2.7× the sum of its parts",
                 fontsize=11.5, fontweight="bold", loc="left", pad=44)
    ax.text(0, 1.028,
            "No single section and no single group is necessary. Removing everything is —\n"
            "and keeping the query group alone recovers 99% of it.   ✱ = 95% CI excludes 0.",
            transform=ax.transAxes, fontsize=8.2, color="#555555", va="bottom",
            linespacing=1.5)
    ax.text(0, -0.095,
            "† schema_info — and the query group that contains it — also disables the "
            "find_databases discovery tool, making these dual ablations\n"
            "rather than clean leave-one-outs. Shaded band = the whole-MIE effect "
            "(+0.88 to +0.93).",
            transform=ax.transAxes, fontsize=7.2, color="#666666",
            va="top", linespacing=1.6)

    fig.tight_layout()
    fig.savefig(OUT / "redundancy_arc.png", bbox_inches="tight",
                facecolor="white")
    plt.close(fig)


# ---------------------------------------------------------------- Figure 3
def ci_ladder():
    """Equivalence delta vs n, with the pre-declared non-regression margin."""
    n = [50, 75, 85, 100]
    est = [0.341, 0.293, 0.301, 0.293]
    lo = [-0.14, -0.11, -0.09, -0.09]
    hi = [+0.82, +0.70, +0.69, +0.68]

    fig, ax = plt.subplots(figsize=(6.6, 3.9))

    ax.axhspan(-0.5, 0.5, color=ACCENT, alpha=0.055, zorder=0)
    ax.axhline(0, color=INK, lw=1.0, zorder=2)
    ax.axhline(-0.5, color=HOT, lw=1.2, ls="--", zorder=2)
    ax.text(101.5, -0.47, "non-regression margin", fontsize=7.4, color=HOT,
            va="bottom", ha="right")

    ax.fill_between(n, lo, hi, color=ACCENT, alpha=0.16, zorder=1)
    ax.plot(n, hi, color=ACCENT, lw=0.9, alpha=0.6, zorder=3)
    ax.plot(n, lo, color=ACCENT, lw=0.9, alpha=0.6, zorder=3)
    ax.plot(n, est, "o-", color=ACCENT, lw=1.8, ms=6, mec="white", mew=1.1,
            zorder=4, label="paired Δ (v3 − v2), refusal-clean")

    for x, e in zip(n, est):
        ax.annotate(f"+{e:.2f}", (x, e), textcoords="offset points",
                    xytext=(0, 10), ha="center", fontsize=7.8, color=ACCENT,
                    fontweight="bold")

    ax.set_xlabel("benchmark questions completed (n), ×3 replicates ×2 corpora",
                  fontsize=8.5)
    ax.set_ylabel("Δ judge score (/20)", fontsize=8.5)
    ax.set_xlim(42, 112)
    ax.set_ylim(-0.75, 1.05)
    ax.set_xticks(n)
    ax.grid(axis="y", color=GRID, lw=0.6, zorder=0)
    ax.set_axisbelow(True)

    ax.set_title("Equivalence, not improvement — and never a regression",
                 fontsize=10.5, fontweight="bold", loc="left", pad=22)
    ax.text(0, 1.06,
            "The interval tightens monotonically and keeps straddling zero; its lower "
            "bound stays far inside the −0.5 margin.",
            transform=ax.transAxes, fontsize=8.0, color="#555555", va="bottom")

    fig.tight_layout()
    fig.savefig(OUT / "ci_ladder.png", bbox_inches="tight",
                facecolor="white")
    plt.close(fig)


# ---------------------------------------------------------------- Figure 1
def format_map():
    """v2.3's 11 author-function sections -> v3's 5 need-based parts."""
    v2 = [
        ("schema_info", "query", 0),
        ("shape_expressions", "query", 1),
        ("sparql_query_examples", "query", 2),
        ("cross_references", "query", 3),
        ("cross_database_queries", "query", 4),
        ("critical_warnings", "guardrails", 5),
        ("common_errors", "guardrails", 6),
        ("anti_patterns", "guardrails", 7),
        ("architectural_notes", "orientation", 8),
        ("data_statistics", "orientation", 9),
        ("sample_rdf_entries", "orientation", 10),
    ]
    v3 = [
        ("discovery", 0.35),
        ("header\nendpoint · graphs · entity_counts\n· global_gotchas", 1.85),
        ("examples\nverified, executable\n— the atomic unit —", 4.30),
        ("schema_delta", 7.05),
        ("id_join_map", 8.30),
    ]
    gcol = {"query": ACCENT, "guardrails": HOT, "orientation": "#6b6b6b"}
    # v2 section index -> v3 part index
    edges = {0: [0, 1], 1: [2], 2: [2], 3: [4], 4: [2],
             5: [1], 6: [2], 7: [2], 8: [3], 9: [1], 10: [2]}
    # sections with no surviving section of their own — absorbed into an example
    absorbed = {1, 10}

    fig, ax = plt.subplots(figsize=(7.6, 5.2))
    ax.axis("off")
    ax.set_xlim(0, 9.9)
    ax.set_ylim(-1.15, 12.1)

    LX, RX, BW, BH = 0.15, 6.35, 3.30, 0.72
    ly = {}
    for name, grp, i in v2:
        y = 10.4 - i * 0.96
        ly[i] = y
        ax.add_patch(FancyBboxPatch((LX, y - BH / 2), BW, BH,
                                    boxstyle="round,pad=0.02,rounding_size=0.08",
                                    fc="white", ec=gcol[grp], lw=1.1, zorder=3))
        ax.text(LX + 0.14, y, name, fontsize=7.9, va="center", zorder=4,
                family="DejaVu Sans Mono")

    ry = {}
    heights = [0.72, 1.70, 2.10, 0.72, 0.72]
    for j, ((name, top), h) in enumerate(zip(v3, heights)):
        y = 10.75 - top - h / 2
        ry[j] = y
        ax.add_patch(FancyBboxPatch((RX, y - h / 2), BW, h,
                                    boxstyle="round,pad=0.02,rounding_size=0.08",
                                    fc="#eef3fa" if j == 2 else "white",
                                    ec=ACCENT if j == 2 else INK,
                                    lw=1.8 if j == 2 else 1.0, zorder=3))
        if j == 2:
            ax.text(RX + BW / 2, y + 0.55, "examples", fontsize=9.6,
                    va="center", ha="center", zorder=4, fontweight="bold")
            ax.text(RX + BW / 2, y - 0.22, "verified · executable\n— the atomic unit —",
                    fontsize=7.8, va="center", ha="center", zorder=4,
                    linespacing=1.6, color="#333333")
        else:
            ax.text(RX + BW / 2, y, name, fontsize=8.0, va="center", ha="center",
                    zorder=4, linespacing=1.7)

    for i, targets in edges.items():
        grp = next(g for _, g, k in v2 if k == i)
        for t in targets:
            ax.add_patch(FancyArrowPatch(
                (LX + BW + 0.04, ly[i]), (RX - 0.04, ry[t]),
                connectionstyle="arc3,rad=0.12", arrowstyle="-|>",
                mutation_scale=8, lw=1.1 if i in absorbed else 0.7,
                linestyle=(0, (2.2, 1.6)) if i in absorbed else "solid",
                color=gcol[grp], alpha=0.85 if i in absorbed else 0.45, zorder=2))

    ax.text(LX, 11.75, "MIE v2.3 — 11 author-function sections",
            fontsize=9.4, fontweight="bold")
    ax.text(RX, 11.75, "MIE v3 — 5 need-based parts",
            fontsize=9.4, fontweight="bold")
    # Lay the group legend out left-to-right using measured text widths, so the
    # items can never collide regardless of font metrics.
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    inv = ax.transData.inverted()
    x = LX
    for lbl, c in [("query (53% of bytes)", ACCENT),
                   ("guardrails (25%)", HOT),
                   ("orientation (22%)", "#6b6b6b")]:
        t = ax.text(x, 11.30, lbl, fontsize=6.8, color=c, fontweight="bold")
        bb = t.get_window_extent(renderer=renderer)
        x = inv.transform((bb.x1, bb.y0))[0] + 0.30

    ax.text(LX, -0.55,
            "Dashed = no section of its own survives. shape_expressions and "
            "sample_rdf_entries are dropped outright,\nabsorbed into the examples: "
            "one verified query IS the shape, the sample triple, and the annotated trap.",
            fontsize=7.4, color="#555555", va="top", linespacing=1.6, style="italic")

    fig.savefig(OUT / "format_map.png", bbox_inches="tight",
                facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    format_map()
    redundancy_arc()
    ci_ladder()
    print(f"ok — three PNGs written to {OUT}")
