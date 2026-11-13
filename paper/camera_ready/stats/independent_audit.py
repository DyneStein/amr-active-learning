"""Independent audit of every number in the 6 page camera ready, recomputed from the raw per run JSON records with
SciPy (exact Wilcoxon, Student t) and a fresh Holm implementation. Usage: python -I audit.py <Results dir> <main.tex>"""
import csv
import glob
import json
import os
import re
import sys
from collections import defaultdict

import numpy as np
from scipy import stats

RES, TEX = sys.argv[1], sys.argv[2]
PAIRS = ["ecoli_cro", "kpneu_cro", "saur_oxa"]
RULES = ["uncertainty", "diversity", "hybrid"]
issues = []


def check(name, got, want, tol):
    ok = abs(got - want) <= tol
    print(f"  {'OK ' if ok else 'BAD'} {name}: recomputed {got:.4f}, paper {want}")
    if not ok:
        issues.append(name)


def load(exp):
    runs = {}
    for f in glob.glob(os.path.join(RES, "results", exp, "*.json")):
        d = json.load(open(f))
        j = d["job"]
        if d["sizes"]["test"] == 0:
            continue
        runs[(j["pair"], j["site"], j["strategy"], j["budget"], j["seed"])] = d
    return runs


def holm(p):
    p = np.asarray(p, float)
    o = np.argsort(p)
    m = len(p)
    adj = np.empty(m)
    run = 0.0
    for k, i in enumerate(o):
        run = max(run, min(1.0, (m - k) * p[i]))
        adj[i] = run
    return adj


def wil(d):
    d = np.asarray(d)
    if np.all(d == 0):
        return 1.0
    return stats.wilcoxon(d, method="exact", alternative="two-sided", zero_method="wilcox").pvalue


def ci(d):
    d = np.asarray(d)
    h = stats.t.ppf(0.975, len(d) - 1) * d.std(ddof=1) / np.sqrt(len(d))
    return d.mean(), d.mean() - h, d.mean() + h


E1 = load("E1_temporal")
E4 = load("E4_crosssite")
auc = lambda r: r["final"]["auroc"]
print("run counts: temporal", len(E1), "cross site", len(E4), "total", len(E1) + len(E4))
check("total simulations", len(E1) + len(E4), 1540, 0)
check("temporal simulations", len(E1), 660, 0)

# ---------------------------------------------------------------- sizes and bounds
print("\nData sizes (IV-A)")
for pair, tr, po, te, prev in zip(PAIRS, (1481, 812, 1141), (2094, 1273, 1445), (1386, 775, 1204), (18.5, 13.9, 14.6)):
    s = E1[(pair, "DRIAMS-A", "random", 400, 0)]["sizes"]
    check(f"{pair} train", s["train"] + s["val"], tr, 0)
    check(f"{pair} pool", s["pool"], po, 0)
    check(f"{pair} test", s["test"], te, 0)
    check(f"{pair} test prevalence %", 100 * s["test_R"] / s["test"], prev, 0.05)
print("\nBounds (V-A, abstract)")
B = {}
for pair, lo, hi, gap in zip(PAIRS, (0.823, 0.742, 0.799), (0.867, 0.788, 0.850), (0.044, 0.046, 0.051)):
    none = np.mean([auc(r) for k, r in E1.items() if k[0] == pair and k[2] == "none"])
    full = np.mean([auc(r) for k, r in E1.items() if k[0] == pair and k[2] == "full"])
    B[pair] = (none, full)
    check(f"{pair} never retrained", none, lo, 0.0005)
    check(f"{pair} retrained on all", full, hi, 0.0005)
    check(f"{pair} gap", full - none, gap, 0.0006)

# ---------------------------------------------------------------- temporal paired tests
print("\nTemporal paired comparisons (IV-C, V-B, Table I)")
rows = []
for pair in PAIRS:
    for b in (40, 100, 200, 400, 800):
        for rule in RULES:
            d = [auc(E1[(pair, "DRIAMS-A", rule, b, s)]) - auc(E1[(pair, "DRIAMS-A", "random", b, s)]) for s in range(10)]
            m, lo, hi = ci(d)
            rows.append(dict(pair=pair, b=b, rule=rule, m=m, lo=lo, hi=hi, p=wil(d)))
for pair in PAIRS:
    idx = [i for i, r in enumerate(rows) if r["pair"] == pair]
    for i, a in zip(idx, holm([rows[i]["p"] for i in idx])):
        rows[i]["hp"] = a
for r, a in zip(rows, holm([r["p"] for r in rows])):
    r["h45"] = a
raw = [r for r in rows if r["p"] < 0.05]
check("comparisons", len(rows), 45, 0)
check("raw p<0.05", len(raw), 14, 0)
check("raw p<0.05 against the rule", sum(r["m"] < 0 for r in raw), 12, 0)
excl = [r for r in rows if r["lo"] > 0 or r["hi"] < 0]
check("intervals excluding zero", len(excl), 14, 0)
same = {(r["pair"], r["b"], r["rule"]) for r in raw} == {(r["pair"], r["b"], r["rule"]) for r in excl}
print(f"  {'OK ' if same else 'BAD'} the 14 with raw p<0.05 are the 14 whose interval excludes zero: {same}")
if not same:
    issues.append("raw set vs interval set")
surv = [r for r in rows if r["hp"] < 0.05]
print("  survivors within pair:", [(r["pair"], r["b"], r["rule"], round(r["m"], 4), round(r["lo"], 3), round(r["hi"], 3), round(r["hp"], 4)) for r in surv])
check("survivors within pair", len(surv), 2, 0)
check("smallest Holm across 45", min(r["h45"] for r in rows), 0.088, 0.0005)
check("exact floor on 10 seeds", 2 / 2 ** 10, 0.002, 0.0001)
check("floor x15", 15 * 2 / 2 ** 10, 0.029, 0.0005)
check("floor x45", 45 * 2 / 2 ** 10, 0.088, 0.0005)
check("floor on 5 seeds", 2 / 2 ** 5, 0.0625, 0)
k8 = [r for r in rows if r["pair"] == "kpneu_cro" and r["b"] == 800 and r["rule"] == "uncertainty"][0]
s40 = [r for r in rows if r["pair"] == "saur_oxa" and r["b"] == 40 and r["rule"] == "diversity"][0]
check("K.pneu unc 800 mean", -k8["m"], 0.029, 0.0005); check("  lo", -k8["hi"], 0.014, 0.0005); check("  hi", -k8["lo"], 0.045, 0.0005)
check("S.aur div 40 mean", -s40["m"], 0.008, 0.0005); check("  lo", -s40["hi"], 0.003, 0.0005); check("  hi", -s40["lo"], 0.013, 0.0005)

# Table I cells in main.tex
tex = open(TEX).read()
tab = tex[tex.index("\\label{tab:effects}"):tex.index("\\end{tabular}", tex.index("\\label{tab:effects}"))]
cells = re.findall(r"(\$-\$)?(\d+\.\d)(?:\$\^\{\\dagger\}\$)?\$\\pm\$(\d+\.\d)", tab)
daggers = tab.count("dagger")
vals = [(-1 if s else 1) * float(m) for s, m, _ in cells]
want = [100 * r["m"] for pair in PAIRS for rule in RULES for b in (40, 100, 200, 400, 800)
        for r in rows if (r["pair"], r["rule"], r["b"]) == (pair, rule, b)]
bad = [(a, b) for a, b in zip(vals, want) if abs(a - round(b, 1)) > 0.051]
print(f"  {'OK ' if not bad and len(vals) == 45 else 'BAD'} Table I: {len(vals)} cells, mismatches {bad}, daggers {daggers}")
if bad or len(vals) != 45 or daggers != 14:
    issues.append("Table I")

# VI-B averages of uncertainty sampling
print("\nAverage AUROC cost of uncertainty sampling (VI-B)")
for pair, want_ in zip(PAIRS, (None, 0.017, 0.006)):
    d = [np.mean([auc(E1[(pair, "DRIAMS-A", "uncertainty", b, s)]) - auc(E1[(pair, "DRIAMS-A", "random", b, s)])
                  for b in (40, 100, 200, 400, 800)]) for s in range(10)]
    m, lo, hi = ci(d)
    print(f"  {pair}: mean {m:+.4f} [{lo:+.4f}, {hi:+.4f}]  p={wil(d):.4f}")
    if want_:
        check(f"{pair} average cost", -m, want_, 0.0005)
    else:
        print(f"  {'OK ' if lo < 0 < hi else 'BAD'} E. coli 'nothing measurable': interval includes zero")

# ---------------------------------------------------------------- cost table
print("\nTable II (share of the gain)")
T2 = {("ecoli_cro", 400): (0.50, 0.43, 0.54, 0.38), ("ecoli_cro", 800): (0.66, 0.52, 0.70, 0.90),
      ("kpneu_cro", 400): (0.77, 0.28, 0.65, 0.60), ("kpneu_cro", 800): (0.66, 0.02, 0.82, 0.67),
      ("saur_oxa", 400): (0.60, 0.38, 0.41, 0.57), ("saur_oxa", 800): (0.77, 0.52, 0.65, 0.85)}
for (pair, b), w in T2.items():
    none, full = B[pair]
    for rule, ww in zip(["random"] + RULES, w):
        got = (np.mean([auc(E1[(pair, "DRIAMS-A", rule, b, s)]) for s in range(10)]) - none) / (full - none)
        check(f"{pair} b{b} {rule}", got, ww, 0.0051)
    po = E1[(pair, "DRIAMS-A", "random", b, 0)]["sizes"]["pool"]
    print(f"     tests saved {100 * (1 - b / po):.1f}%")
print("  400 as share of pool:", [round(100 * 400 / E1[(p, 'DRIAMS-A', 'random', 400, 0)]['sizes']['pool'], 1) for p in PAIRS])

# ---------------------------------------------------------------- operational errors
print("\nOperational errors over the pool year (V-D, VI-B)")
op = lambda r, k: sum(x[k] for x in r["metrics"][1:])
for pair, vr, vu, mr, mu in zip(PAIRS, (49.8, 19.4, 18.8), (33.6, 5.2, 9.2), (347.8, 123.7, 134.6), (259.8, 190.1, 140.0)):
    g = lambda rule, k: np.mean([op(E1[(pair, "DRIAMS-A", rule, 800, s)], k) for s in range(10)])
    check(f"{pair} VME random", g("random", "op_vme_count"), vr, 0.05)
    check(f"{pair} VME uncertainty", g("uncertainty", "op_vme_count"), vu, 0.05)
    check(f"{pair} ME random", g("random", "op_me_count"), mr, 0.05)
    check(f"{pair} ME uncertainty", g("uncertainty", "op_me_count"), mu, 0.05)
    print(f"     VME reduction {100 * (1 - g('uncertainty', 'op_vme_count') / g('random', 'op_vme_count')):.1f}%")
print("  K. pneumoniae trade: ME +", round(190.1 - 123.7, 1), "VME -", round(19.4 - 5.2, 1), "ratio", round((190.1 - 123.7) / (19.4 - 5.2), 2))
print("\nResistant share bought by uncertainty at 400 (V-D)")
for pair, w, arr in zip(PAIRS, (14.9, 9.7, 10.8), (22.2, 14.2, 18.8)):
    rs = [E1[(pair, "DRIAMS-A", "uncertainty", 400, s)]["final"] for s in range(10)]
    check(f"{pair} bought resistant %", 100 * np.mean([r["R_bought_total"] / r["labels_total"] for r in rs]), w, 0.05)
    sz = E1[(pair, "DRIAMS-A", "random", 400, 0)]["sizes"]
    check(f"{pair} arrival rate %", 100 * sz["pool_R"] / sz["pool"], arr, 0.05)
print("\n2018 operating point, uncertainty vs random (VI-B)")
n = 0
for pair in PAIRS:
    for b in (40, 100, 200, 400, 800):
        f = lambda rule, k: np.mean([E1[(pair, "DRIAMS-A", rule, b, s)]["final"][k] for s in range(10)])
        if f("uncertainty", "vme") > f("random", "vme") and f("uncertainty", "me") < f("random", "me"):
            n += 1
        else:
            print(f"     exception: {pair} b{b} vme {f('uncertainty', 'vme'):.3f} vs {f('random', 'vme'):.3f}, me {f('uncertainty', 'me'):.3f} vs {f('random', 'me'):.3f}")
check("configurations with higher VME and lower ME", n, 14, 0)
th = np.mean([E1[("kpneu_cro", "DRIAMS-A", "uncertainty", 800, s)]["metrics"][1]["threshold"] for s in range(10)])
print(f"  K. pneumoniae threshold in round 1: {th:.4f} (not quoted in the paper)")

# ---------------------------------------------------------------- cross site
print("\nCross site (IV-A, V-B)")
combos = sorted({(k[0], k[1]) for k in E4})
check("pair and site combinations", len(combos), 8, 0)
check("cross site simulations", len(E4), 880, 0)
cr = []
for pair, site in combos:
    for b in (25, 50, 100, 200, 400):
        for rule in RULES:
            d = np.array([auc(E4[(pair, site, rule, b, s)]) - auc(E4[(pair, site, "random", b, s)]) for s in range(5)])
            pool = E4[(pair, site, "random", b, 0)]["sizes"]["pool"]
            cr.append(dict(zero=bool(np.all(d == 0)), big=b >= pool, d=d, ci=ci(d) if not np.all(d == 0) else (0, 0, 0), p=wil(d)))
check("comparisons", len(cr), 120, 0)
check("zero by construction", sum(c["zero"] for c in cr), 30, 0)
print(f"  {'OK ' if all(c['zero'] == c['big'] for c in cr) else 'BAD'} zero exactly when budget >= target pool")
inf = [c for c in cr if not c["zero"]]
check("negative means", sum(c["d"].mean() < 0 for c in inf), 64, 0)
ex = [c for c in inf if c["ci"][1] > 0 or c["ci"][2] < 0]
check("intervals excluding zero", len(ex), 7, 0)
check("of which against the rule", sum(c["d"].mean() < 0 for c in ex), 6, 0)
check("smallest cross site p", min(c["p"] for c in inf), 0.0625, 0)
print("  total informative comparisons:", 45 + len(inf))

# ---------------------------------------------------------------- robustness rerun
print("\nRobustness to the arrival batches (V-B)")
R = defaultdict(dict)
for r in csv.DictReader(open(os.path.join(RES, "tables", "R1_batching_runs.csv"))):
    R[r["variant"]][(r["pair"], int(r["budget"]), r["rule"], int(r["seed"]))] = r
check("runs", sum(len(v) for v in R.values()), 1800, 0)
ident = sum(abs(float(R["hash"][(p, b, rule, s)]["auroc"]) - auc(E1[(p, "DRIAMS-A", rule, b, s)])) < 1e-12
            for p in PAIRS for b in (100, 400, 800) for rule in ["random"] + RULES for s in range(10))
check("reference division reproduces published runs", ident, 360, 0)
against = forr = 0
for v in ["hash", "salt1", "salt2", "salt3", "single"]:
    res = []
    for p in PAIRS:
        ps, ms = [], []
        for b in (100, 400, 800):
            for rule in RULES:
                d = [float(R[v][(p, b, rule, s)]["auroc"]) - float(R[v][(p, b, "random", s)]["auroc"]) for s in range(10)]
                ps.append(wil(d)); ms.append((np.mean(d), b, rule))
        for a, (m, b, rule) in zip(holm(ps), ms):
            res.append((m, a, p, b, rule))
    neg = sum(m < 0 for m, *_ in res)
    ag = sum(a < 0.05 and m < 0 for m, a, *_ in res)
    fo = [(p, b, rule, round(m, 4)) for m, a, p, b, rule in res if a < 0.05 and m > 0]
    against += ag; forr += len(fo)
    kd = [m for m, a, p, b, rule in res if (p, b, rule) == ("kpneu_cro", 800, "diversity")][0]
    print(f"  {v:6s} negative {neg}/27, against {ag}, for {fo}, K.pneu diversity 800 {kd:+.4f}")
check("against the rule across divisions", against, 8, 0)
check("for a rule across divisions", forr, 1, 0)
for p in PAIRS:
    for v in R:
        d = [op(None, None) if False else 0 for _ in range(0)]
print("  (VME reduction per division is in the paper only as 'in every division and for every pair'; checked below)")
allneg = True
for v in R:
    for p in PAIRS:
        d = [float(R[v][(p, 800, "uncertainty", s)]["op_vme"]) - float(R[v][(p, 800, "random", s)]["op_vme"]) for s in range(10)]
        m, lo, hi = ci(d)
        allneg &= hi < 0
print(f"  {'OK ' if allneg else 'BAD'} uncertainty at 800 reduced operational VME with an interval below zero in all 15 cases")

print("\nISSUES:", issues if issues else "none")
