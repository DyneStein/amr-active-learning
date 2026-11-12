"""Camera ready recomputation of the paired comparisons against random selection (12 Nov 2026).

Reads the raw per run records and recomputes, with no dependence on amr_al.analysis:
  exact two sided Wilcoxon signed rank p, Holm correction under three family definitions,
  mean paired AUROC difference with a 95% t interval, and the matched pairs rank biserial correlation.
Run: /usr/bin/python3 camera_ready_stats.py <Results/results dir> <out dir>
"""
import sys, os, json, glob, itertools, csv
import numpy as np
from scipy import stats

RES, OUT = sys.argv[1], sys.argv[2]
RULES = ["uncertainty", "diversity", "hybrid"]


def load(exp, skip=()):
    rows = {}
    for f in glob.glob(os.path.join(RES, exp, "*.json")):
        d = json.load(open(f)); j = d["job"]
        if (j["pair"], j["site"]) in skip:
            continue
        rows[(j["pair"], j["site"], j["strategy"], j["budget"], j["seed"])] = d["final"]
    return rows


def exact_wilcoxon(d):
    """Exact two sided signed rank p by full enumeration of sign patterns (handles ties in |d| by midranks)."""
    d = np.asarray(d, float); d = d[d != 0]; n = len(d)
    if n == 0:
        return 1.0, 0.0, n
    r = stats.rankdata(np.abs(d))
    w_plus = r[d > 0].sum(); total = r.sum()
    stat = min(w_plus, total - w_plus)
    cnt = 0
    for signs in itertools.product((0, 1), repeat=n):
        w = float(np.dot(signs, r))
        if min(w, total - w) <= stat + 1e-12:
            cnt += 1
    rb = (w_plus - (total - w_plus)) / total          # matched pairs rank biserial correlation
    return cnt / 2 ** n, rb, n


def holm(p):
    p = np.asarray(p, float); order = np.argsort(p); adj = np.empty_like(p); m = len(p); run = 0.0
    for rank, i in enumerate(order):
        run = max(run, (m - rank) * p[i]); adj[i] = min(1.0, run)
    return adj


def compare(rows, metric="auroc"):
    keys = sorted({(p, s, b) for (p, s, st, b, sd) in rows if st in RULES})
    out = []
    for (pair, site, b) in keys:
        seeds = sorted({sd for (p, s, st, bb, sd) in rows if (p, s, st, bb) == (pair, site, "random", b)})
        for rule in RULES:
            d = np.array([rows[(pair, site, rule, b, sd)][metric] - rows[(pair, site, "random", b, sd)][metric]
                          for sd in seeds if (pair, site, rule, b, sd) in rows])
            n = len(d); m = d.mean(); sd_ = d.std(ddof=1)
            half = stats.t.ppf(0.975, n - 1) * sd_ / np.sqrt(n)
            p, rb, n_nz = exact_wilcoxon(d)
            out.append(dict(pair=pair, site=site, budget=b, rule=rule, n=n, mean_diff=m, ci_lo=m - half, ci_hi=m + half,
                            sd=sd_, p=p, rank_biserial=rb, n_nonzero=n_nz))
    return out


def add_holm(out, name, keyf):
    groups = {}
    for i, r in enumerate(out):
        groups.setdefault(keyf(r), []).append(i)
    for idx in groups.values():
        adj = holm([out[i]["p"] for i in idx])
        for i, a in zip(idx, adj):
            out[i][name] = a


def write(out, fn):
    cols = list(out[0].keys())
    with open(os.path.join(OUT, fn), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader()
        for r in out:
            w.writerow({k: (f"{v:.6g}" if isinstance(v, float) else v) for k, v in r.items()})


e1 = compare(load("E1_temporal"))
e4 = compare(load("E4_crosssite", skip={("saur_oxa", "DRIAMS-D")}))
add_holm(e1, "holm_pair15", lambda r: r["pair"]); add_holm(e1, "holm_all45", lambda r: 0)
add_holm(e4, "holm_pairsite15", lambda r: (r["pair"], r["site"])); add_holm(e4, "holm_all120", lambda r: 0)
both = e1 + e4
adj = holm([r["p"] for r in both])
for r, a in zip(both, adj):
    r["holm_all165"] = a
write(e1, "camera_ready_E1_vs_random.csv"); write(e4, "camera_ready_E4_vs_random.csv")

print("E1 temporal: comparisons", len(e1), " n per comparison", sorted({r['n'] for r in e1}))
print("  smallest possible exact two sided p with n=10:", 2 / 2 ** 10)
print("  raw p<0.05:", sum(r["p"] < 0.05 for r in e1), " of which rule worse:", sum(r["p"] < 0.05 and r["mean_diff"] < 0 for r in e1),
      " rule better:", sum(r["p"] < 0.05 and r["mean_diff"] > 0 for r in e1))
print("  Holm within pair (15) <0.05:", sum(r["holm_pair15"] < 0.05 for r in e1), "| Holm across 45 <0.05:", sum(r["holm_all45"] < 0.05 for r in e1),
      "| min Holm45:", min(r["holm_all45"] for r in e1), "| Holm across 165 <0.05:", sum(r["holm_all165"] < 0.05 for r in e1))
print("  CI excludes 0:", sum(r["ci_lo"] > 0 or r["ci_hi"] < 0 for r in e1), " above 0:", sum(r["ci_lo"] > 0 for r in e1), " below 0:", sum(r["ci_hi"] < 0 for r in e1))
print("  mean diff range: %.4f to %.4f; largest CI upper bound %.4f; smallest CI lower bound %.4f" % (
    min(r["mean_diff"] for r in e1), max(r["mean_diff"] for r in e1), max(r["ci_hi"] for r in e1), min(r["ci_lo"] for r in e1)))
for r in sorted(e1, key=lambda r: r["p"])[:16]:
    print("   %-10s b%-4d %-11s diff %+.4f [%+.4f, %+.4f] p %.5f holm15 %.4f holm45 %.4f rb %+.2f" % (
        r["pair"], r["budget"], r["rule"], r["mean_diff"], r["ci_lo"], r["ci_hi"], r["p"], r["holm_pair15"], r["holm_all45"], r["rank_biserial"]))

print("\nE4 cross site: comparisons", len(e4), " n per comparison", sorted({r['n'] for r in e4}))
print("  smallest possible exact two sided p with n=5:", 2 / 2 ** 5)
print("  raw p<0.05:", sum(r["p"] < 0.05 for r in e4), "| p at the floor 0.0625:", sum(abs(r["p"] - 0.0625) < 1e-9 for r in e4),
      " of which rule better:", sum(abs(r["p"] - 0.0625) < 1e-9 and r["mean_diff"] > 0 for r in e4),
      " worse:", sum(abs(r["p"] - 0.0625) < 1e-9 and r["mean_diff"] < 0 for r in e4))
print("  CI excludes 0:", sum(r["ci_lo"] > 0 or r["ci_hi"] < 0 for r in e4), " above 0:", sum(r["ci_lo"] > 0 for r in e4), " below 0:", sum(r["ci_hi"] < 0 for r in e4))
print("  mean diff range: %.4f to %.4f" % (min(r["mean_diff"] for r in e4), max(r["mean_diff"] for r in e4)))
for r in sorted(e4, key=lambda r: r["p"])[:14]:
    print("   %-10s %-9s b%-4d %-11s diff %+.4f [%+.4f, %+.4f] p %.4f" % (
        r["pair"], r["site"], r["budget"], r["rule"], r["mean_diff"], r["ci_lo"], r["ci_hi"], r["p"]))

# Pooled over budgets: one value per seed (mean over the 5 budgets), per pair (and site) and rule
print("\nPooled over the 5 budgets (seed level mean difference, 95% t interval)")
for name, rows_, skip in (("E1", load("E1_temporal"), ()), ("E4", load("E4_crosssite", skip={("saur_oxa", "DRIAMS-D")}), ())):
    ps = sorted({(p, s) for (p, s, st, b, sd) in rows_})
    for (pair, site) in ps:
        for rule in RULES:
            bs = sorted({b for (p, s, st, b, sd) in rows_ if (p, s, st) == (pair, site, rule)})
            seeds = sorted({sd for (p, s, st, b, sd) in rows_ if (p, s, st) == (pair, site, rule)})
            d = np.array([np.mean([rows_[(pair, site, rule, b, sd)]["auroc"] - rows_[(pair, site, "random", b, sd)]["auroc"] for b in bs]) for sd in seeds])
            n = len(d); half = stats.t.ppf(0.975, n - 1) * d.std(ddof=1) / np.sqrt(n); p, rb, _ = exact_wilcoxon(d)
            print("   %s %-10s %-9s %-11s n=%d  %+.4f [%+.4f, %+.4f]  p %.4f" % (name, pair, site, rule, n, d.mean(), d.mean() - half, d.mean() + half, p))
