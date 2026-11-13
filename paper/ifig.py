# Figures for the six page IEEE version. Column widths: 3.4 in single, 7.2 in across both.
# f2_curves  label efficiency curves with the two bounds shaded and a share-of-gain axis
# f3_errors  both clinical error types during the pool year, side by side
# f4_shap    which spectral bins each fitted model relies on
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
# AMR_CSV_DIR: folder with all_results.csv and e1_rounds.csv written by paper_data.py
# AMR_SHAP_DIR: folder with the SHAP tables written by notebook 05
S = os.environ.get("AMR_CSV_DIR", os.path.join(HERE, "_data")) + "/"
SHAP = os.environ.get("AMR_SHAP_DIR", os.path.join(HERE, "..", "..", "Results", "tables")) + "/"
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
MK = {"random": "o", "uncertainty": "s", "diversity": "^", "hybrid": "D"}
PAIR = {"ecoli_cro": "E. coli / ceftriaxone", "kpneu_cro": "K. pneumoniae / ceftriaxone",
        "saur_oxa": "S. aureus / oxacillin"}
SHORT = {"ecoli_cro": "E. coli", "kpneu_cro": "K. pneumoniae", "saur_oxa": "S. aureus"}
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
    """AUROC with no retraining ('0') or after retraining on the whole pool ('all')."""
    return A[(A.pair == pair) & (A.budget == which)].auroc.mean()


def f_curves():
    """AUROC against label budget, one panel per pair, with the reachable band shaded."""
    fig, axes = plt.subplots(1, 3, figsize=(7.2, 1.95))
    for k, (ax, pair) in enumerate(zip(axes, ORDER)):
        lo, hi = bound(pair, "0"), bound(pair, "all")
        ax.axhspan(lo, hi, color="#eef1f5", zorder=0)
        ax.axhline(hi, color=C["full"], lw=0.9, dashes=(5, 2), zorder=1)
        ax.axhline(lo, color=C["none"], lw=0.9, dashes=(1.5, 1.6), zorder=1)
        for st in ["random", "uncertainty", "diversity", "hybrid"]:
            g = A[(A.pair == pair) & (A.strategy == st)]
            m = [g[g.budget == str(b)].auroc.mean() for b in BUD]
            e = [g[g.budget == str(b)].auroc.std(ddof=1) / np.sqrt(10) for b in BUD]
            ax.errorbar(BUD, m, yerr=e, color=C[st], lw=1.0, marker=MK[st], ms=2.6,
                        mfc="white" if st != "random" else C["random"], mew=0.8,
                        elinewidth=0.7, capsize=1.4,
                        dashes=(4, 2) if st == "random" else (None, None), zorder=3)
        ax.set_xscale("log")
        ax.set_xticks(BUD)
        ax.set_xticklabels([str(b) for b in BUD])
        ax.minorticks_off()
        ax.set_title(PAIR[pair], style="italic")
        ax.set_xlabel("susceptibility tests bought during 2017")
        pad = (hi - lo) * 0.30
        ax.set_ylim(lo - pad, hi + pad)
        # the size of the band, written where the reader is looking
        ax.set_xlim(33, 1000)
        ax.text(36, hi - (hi - lo) * 0.06, f"reachable gain {hi - lo:.3f}", fontsize=6.3,
                color="#555", ha="left", va="top")
        # right hand axis: the same thing as a share of the reachable gain
        tw = ax.twinx()
        tw.set_ylim(-0.30, 1.30)
        tw.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
        tw.grid(False)
        tw.spines["right"].set_visible(True)
        tw.spines["right"].set_linewidth(0.55)
        tw.tick_params(width=0.55, length=2.2)
        if k < 2:
            tw.set_yticklabels([])
        else:
            tw.set_ylabel("share of the reachable gain", fontsize=7.2)
    axes[0].set_ylabel("AUROC on 2018 isolates")
    from matplotlib.lines import Line2D
    keys = [("full", "retrain on everything"), ("none", "no retraining"),
            ("random", "random"), ("uncertainty", "uncertainty"),
            ("diversity", "diversity"), ("hybrid", "hybrid")]
    h = [Line2D([], [], color=C[k], lw=1.0,
                dashes={"full": (5, 2), "none": (1.5, 1.6), "random": (4, 2)}.get(k, (None, None)),
                marker=MK.get(k, ""), ms=2.6, mew=0.8,
                mfc="white" if k in ("uncertainty", "diversity", "hybrid") else C[k], label=v)
         for k, v in keys]
    fig.legend(handles=h, ncol=6, frameon=False, loc="lower center", bbox_to_anchor=(0.5, -0.15),
               columnspacing=1.3, handlelength=2.1)
    fig.tight_layout(w_pad=1.4)
    save(fig, "f2_curves")


def f_errors():
    """Both clinical error types over the pool year, so that one cannot hide the other."""
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 1.38))
    xs = np.arange(3)
    w, gap = 0.19, 0.06
    combos = [("random", "400"), ("uncertainty", "400"), ("random", "800"), ("uncertainty", "800")]
    for ax, (col, lab, top) in zip(axes, [("opvme", "resistant isolates reported susceptible", 92),
                                          ("opme", "susceptible isolates reported resistant", 500)]):
        for i, (st, b) in enumerate(combos):
            v = [A[(A.pair == p) & (A.strategy == st) & (A.budget == b)][col].mean() for p in ORDER]
            off = (i - 1.5) * (w + gap / 2)
            ax.bar(xs + off, v, w, color=C[st], edgecolor="white", linewidth=0.5,
                   hatch="" if b == "800" else "////", zorder=3)
            for x, y in zip(xs + off, v):
                ax.text(x, y + top * 0.015, f"{y:.0f}", ha="center", fontsize=5.8, color="#333")
        ax.set_xticks(xs)
        ax.set_xticklabels([SHORT[p] for p in ORDER], style="italic")
        ax.set_ylabel(lab, fontsize=6.9)
        ax.set_ylim(0, top)
    axes[0].set_title("(a) very major errors", fontsize=7.4)
    axes[1].set_title("(b) major errors", fontsize=7.4)
    from matplotlib.patches import Patch
    h = [Patch(facecolor=C["random"], hatch="////", edgecolor="white", label="random, 400"),
         Patch(facecolor=C["uncertainty"], hatch="////", edgecolor="white", label="uncertainty, 400"),
         Patch(facecolor=C["random"], edgecolor="white", label="random, 800"),
         Patch(facecolor=C["uncertainty"], edgecolor="white", label="uncertainty, 800")]
    fig.legend(handles=h, ncol=4, frameon=False, loc="lower center", bbox_to_anchor=(0.5, -0.13),
               handlelength=1.4, columnspacing=1.4)
    fig.tight_layout(w_pad=2.0)
    save(fig, "f3_errors")


COND = ["no retraining", "random 400", "uncertainty 400", "random 800", "uncertainty 800",
        "retrain on everything"]
CLAB = ["none", "rand\n400", "unc\n400", "rand\n800", "unc\n800", "all"]


def f_shap():
    """Which bins each model leans on. Rows are bins, columns are the six fitted models."""
    T = pd.read_csv(SHAP + "shap_top_bins.csv")
    fig, axes = plt.subplots(1, 3, figsize=(7.2, 1.75),
                             gridspec_kw={"width_ratios": [1, 1, 1]})
    for ax, pair in zip(axes, ORDER):
        t = T[T.pair == pair]
        count = t.groupby("bin").size()
        keep = count[count >= 4].index
        imp = t[t.bin.isin(keep)].groupby("bin").mean_abs_shap.mean().sort_values()
        bins = list(imp.index)[-11:]
        lbl = {b: t[t.bin == b].mz_range.iloc[0].replace(" Da", "") for b in bins}
        direc = {b: t[t.bin == b].high_intensity_means.mode()[0] for b in bins}
        for j, cond in enumerate(COND):
            sub = t[t.condition == cond].set_index("bin")
            for i, b in enumerate(bins):
                if b in sub.index:
                    v = sub.loc[b, "mean_abs_shap"]
                    ax.scatter(j, i, s=8 + 300 * v, color=C["uncertainty"] if direc[b] == "resistant"
                               else C["diversity"], alpha=0.85, linewidths=0, zorder=3)
                else:
                    ax.scatter(j, i, s=3.2, color="#cfcfcf", linewidths=0, zorder=2)
        ax.set_yticks(range(len(bins)))
        ax.set_yticklabels([lbl[b] for b in bins], fontsize=6.0)
        ax.set_xticks(range(6))
        ax.set_xticklabels(CLAB, fontsize=6.0)
        ax.set_xlim(-0.6, 5.6)
        ax.set_ylim(-0.8, len(bins) - 0.2)
        ax.grid(axis="y", color="#f0f0f0", lw=0.4)
        ax.grid(axis="x", visible=False)
        n_all = int((count == 6).sum())
        ax.set_title(f"{PAIR[pair]}\n{n_all} of {len(count)} bins in all six", style="italic",
                     fontsize=7.0)
    axes[0].set_ylabel("spectral bin, daltons", fontsize=7.0)
    from matplotlib.lines import Line2D
    h = [Line2D([], [], ls="", marker="o", ms=4.0, color=C["uncertainty"],
                label="higher intensity pushes towards resistant"),
         Line2D([], [], ls="", marker="o", ms=4.0, color=C["diversity"],
                label="higher intensity pushes towards susceptible"),
         Line2D([], [], ls="", marker="o", ms=1.8, color="#cfcfcf",
                label="bin not in that model's top 20")]
    fig.legend(handles=h, ncol=3, frameon=False, loc="lower center", bbox_to_anchor=(0.5, -0.10),
               handlelength=1.0, columnspacing=1.6)
    fig.tight_layout(w_pad=1.6)
    save(fig, "f4_shap")


if __name__ == "__main__":
    print("writing figures to", OUT)
    f_curves()
    f_errors()
    f_shap()
