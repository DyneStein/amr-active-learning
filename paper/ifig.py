# Figures for the six page IEEE version. Column widths: 3.4 in single, 7.2 in across both.
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np, pandas as pd

S = "/tmp/work/project/7fb83f58-8ee1-4d80-abd0-7a5cdba3f0f3/scratchpad/"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "ifig") + "/"
os.makedirs(OUT, exist_ok=True)

# IEEE body text is 10 pt Times; captions 8 pt. Figure text sits just under the caption size
# so that it never looks larger than the prose around it.
plt.rcParams.update({
    "font.family": "serif", "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
    "font.size": 7.0, "axes.labelsize": 7.2, "axes.titlesize": 7.6, "legend.fontsize": 6.6,
    "xtick.labelsize": 6.8, "ytick.labelsize": 6.8, "axes.linewidth": 0.55,
    "xtick.major.width": 0.55, "ytick.major.width": 0.55,
    "xtick.major.size": 2.2, "ytick.major.size": 2.2,
    "axes.spines.top": False, "axes.spines.right": False, "svg.fonttype": "none",
    "axes.grid": True, "grid.color": "#e6e6e6", "grid.linewidth": 0.4,
    "axes.facecolor": "white", "figure.facecolor": "white", "savefig.facecolor": "white",
})

C = {"uncertainty": "#2a78d6", "diversity": "#eb6834", "hybrid": "#1baf7a",
     "random": "#52514e", "none": "#a8a7a1", "full": "#0b0b0b"}
PAIR = {"ecoli_cro": "E. coli / ceftriaxone", "kpneu_cro": "K. pneumoniae / ceftriaxone",
        "saur_oxa": "S. aureus / oxacillin"}
ORDER = ["ecoli_cro", "kpneu_cro", "saur_oxa"]
BUD = [40, 100, 200, 400, 800]

A = pd.read_csv(S + "all_results.csv")
A = A[(A.exp == "E1_temporal") & (A.site == "DRIAMS-A")]
A["budget"] = A.budget.astype(str)


def save(fig, name):
    fig.savefig(OUT + name + ".svg", bbox_inches="tight", pad_inches=0.012)
    plt.close(fig)
    print("  ", name)


def bound(pair, which):
    """AUROC with no retraining ('none') or after retraining on the whole pool ('all')."""
    g = A[(A.pair == pair) & (A.budget == which)]
    return g.auroc.mean()


def f_curves():
    """AUROC against label budget, one panel per pair, with both bounds drawn flat."""
    fig, axes = plt.subplots(1, 3, figsize=(7.2, 1.95))
    for ax, pair in zip(axes, ORDER):
        lo, hi = bound(pair, "0"), bound(pair, "all")
        ax.axhline(hi, color=C["full"], lw=0.9, dashes=(5, 2), zorder=1)
        ax.axhline(lo, color=C["none"], lw=0.9, dashes=(1.5, 1.6), zorder=1)
        for st in ["random", "uncertainty", "diversity", "hybrid"]:
            g = A[(A.pair == pair) & (A.strategy == st)]
            m = [g[g.budget == str(b)].auroc.mean() for b in BUD]
            e = [g[g.budget == str(b)].auroc.std(ddof=1) / np.sqrt(10) for b in BUD]
            ax.errorbar(BUD, m, yerr=e, color=C[st], lw=1.0, marker="o", ms=2.3,
                        elinewidth=0.7, capsize=1.4,
                        dashes=(4, 2) if st == "random" else (None, None), zorder=3)
        ax.set_xscale("log"); ax.set_xticks(BUD)
        ax.set_xticklabels([str(b) for b in BUD])
        ax.minorticks_off()
        ax.set_title(PAIR[pair], style="italic")
        ax.set_xlabel("susceptibility tests bought during 2017")
        pad = (hi - lo) * 0.28
        ax.set_ylim(lo - pad, hi + pad)
    axes[0].set_ylabel("AUROC on 2018 isolates")
    # one shared legend, placed where no panel loses space to it
    from matplotlib.lines import Line2D
    keys = [("full", "retrain on everything"), ("none", "no retraining"),
            ("random", "random"), ("uncertainty", "uncertainty"),
            ("diversity", "diversity"), ("hybrid", "hybrid")]
    h = [Line2D([], [], color=C[k], lw=1.0,
                dashes={"full": (5, 2), "none": (1.5, 1.6), "random": (4, 2)}.get(k, (None, None)),
                marker="" if k in ("full", "none") else "o", ms=2.3, label=v) for k, v in keys]
    fig.legend(handles=h, ncol=6, frameon=False, loc="lower center", bbox_to_anchor=(0.5, -0.17),
               columnspacing=1.3, handlelength=2.1)
    fig.tight_layout(w_pad=1.1)
    save(fig, "f2_curves")


def f_safety():
    """Resistant isolates left untested and reported susceptible, counted over the year."""
    fig, ax = plt.subplots(figsize=(3.4, 1.85))
    w, gap = 0.19, 0.06
    xs = np.arange(3)
    combos = [("random", "400"), ("uncertainty", "400"), ("random", "800"), ("uncertainty", "800")]
    for i, (st, b) in enumerate(combos):
        v = [A[(A.pair == p) & (A.strategy == st) & (A.budget == b)].opvme.mean() for p in ORDER]
        off = (i - 1.5) * (w + gap / 2)
        ax.bar(xs + off, v, w, color=C[st], edgecolor="white", linewidth=0.5,
               hatch="" if b == "800" else "////", zorder=3)
        for x, y in zip(xs + off, v):
            ax.text(x, y + 1.2, f"{y:.0f}", ha="center", fontsize=5.8, color="#333")
    ax.set_xticks(xs)
    ax.set_xticklabels(["E. coli", "K. pneumoniae", "S. aureus"], style="italic")
    ax.set_ylabel("missed resistant isolates")
    ax.set_ylim(0, 92)
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(facecolor=C["random"], hatch="////", edgecolor="white", label="random, 400"),
                       Patch(facecolor=C["uncertainty"], hatch="////", edgecolor="white", label="uncertainty, 400"),
                       Patch(facecolor=C["random"], edgecolor="white", label="random, 800"),
                       Patch(facecolor=C["uncertainty"], edgecolor="white", label="uncertainty, 800")],
              ncol=2, frameon=False, loc="upper right", fontsize=5.9,
              handlelength=1.3, columnspacing=0.8, labelspacing=0.25)
    fig.tight_layout()
    save(fig, "f3_safety")


if __name__ == "__main__":
    print("writing figures to", OUT)
    f_curves()
    f_safety()
