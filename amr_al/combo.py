"""Combination strategies from the active-learning catalogues (added 5 Oct 2026).

A combination = selection rule + random share of the budget + retraining weights + calibration source
+ pseudo-labels. Codes and their parts are in config.COMBOS; the catalogue PDF explains each part.

sel     uncertainty  closest to the threshold, |p - t| smallest
        vmerisk      called susceptible (p < t) and closest to the threshold: where a missed resistance can happen
        hybrid       as strategies.hybrid, on the non-random part
        novelty      farthest from everything labelled so far in PCA space (the new regions created by drift)
        random       uniform at random (only with mix = 0)
mix     share of each round's budget bought uniformly at random (picked first, so it is an unbiased sample)
w_new   sample weight of bought labels; iw = also re-weight them so they look like the arriving isolates
cal     old        threshold and conformal bounds from the 2015-16 validation set (as E1)
        holdout    25% of bought labels (fixed mask) kept out of training, used to re-calibrate (as E5)
        rand_hold  the random share kept out of training, used only to re-calibrate
        rand_preq  the random share used for training AND re-calibration; its scores come from the model in use
                   when it was bought (before it was trained on them), so they are out-of-sample
        weighted   validation isolates re-weighted by a density ratio new/old estimated from unlabelled
                   arriving spectra (weighted conformal, Tibshirani et al., NeurIPS 2019)
        aci        target error levels nudged after every lab result (adaptive conformal, Gibbs & Candes, NeurIPS 2021)
pseudo  none | conformal  (untested isolates whose re-calibrated 95% prediction set holds one label)
"""
import json
import time

import numpy as np

from . import config, conformal, data, metrics, models, runner, strategies

ACI_GAMMA = 0.02


def _weighted_threshold(y, p, w, target):
    pos, wp = p[y == 1], w[y == 1]
    if len(pos) == 0:
        return 0.5
    o = np.argsort(-pos, kind="stable")
    cum = np.cumsum(wp[o]) / wp.sum()
    return float(pos[o][min(np.searchsorted(cum, target - 1e-12), len(o) - 1)])


def _weighted_q(p, y, w, alpha):
    q = {}
    for c in (0, 1):
        m = y == c
        s = 1 - (p[m] if c == 1 else 1 - p[m])
        if m.sum() == 0:
            q[c] = 1.0
            continue
        o = np.argsort(s, kind="stable")
        cum = np.cumsum(w[m][o]) / (w[m].sum() + w[m].max())      # + max weight: finite-sample correction
        k = np.searchsorted(cum, 1 - alpha)
        q[c] = float(s[o][k]) if k < len(o) else 1.0
    return q


def _q_two_alpha(p, y, a_s, a_r):
    qs, qr = conformal.fit(p, y, a_s), conformal.fit(p, y, a_r)
    return {0: qs[0], 1: qr[1]}


def _domain_weights(E_old, E_new, clip):
    """Density ratio new/old at E_old, from a logistic classifier old (0) vs new (1)."""
    from sklearn.linear_model import LogisticRegression
    X = np.concatenate([E_old, E_new])
    y = np.r_[np.zeros(len(E_old)), np.ones(len(E_new))]
    clf = LogisticRegression(C=0.1, max_iter=2000).fit(X, y)
    pr = np.clip(clf.predict_proba(E_old)[:, 1], 1e-4, 1 - 1e-4)
    w = pr / (1 - pr) * len(E_old) / len(E_new)
    w = np.clip(w / w.mean(), *clip)
    return w / w.mean()


def choose(c, b, p, t, E, E_lab, rng):
    """Returns (random positions, targeted positions) into the round's candidates."""
    n = len(p)
    if b >= n:
        return np.arange(n), np.zeros(0, int)
    n_r = int(round(c["mix"] * b))
    rand = np.sort(rng.choice(n, size=n_r, replace=False)) if n_r else np.zeros(0, int)
    rest = np.setdiff1d(np.arange(n), rand)
    k = b - n_r
    if k <= 0:
        return rand, np.zeros(0, int)
    pr = p[rest]
    if c["sel"] == "random":
        tgt = rng.choice(rest, size=k, replace=False)
    elif c["sel"] == "uncertainty":
        tgt = rest[np.argsort(np.abs(pr - t), kind="stable")[:k]]
    elif c["sel"] == "vmerisk":
        below = np.where(pr < t)[0]
        first = below[np.argsort(-pr[below], kind="stable")][:k]
        if len(first) < k:
            others = np.setdiff1d(np.arange(len(rest)), first)
            first = np.r_[first, others[np.argsort(np.abs(pr[others] - t), kind="stable")[:k - len(first)]]]
        tgt = rest[first]
    elif c["sel"] == "hybrid":
        tgt = rest[strategies.select("hybrid", k, pr, t, E[rest], E_lab, rng)]
    elif c["sel"] == "novelty":
        d = np.full(len(rest), np.inf)
        for i in range(0, len(E_lab), 2048):
            d = np.minimum(d, strategies._min_dist(E[rest], E_lab[i:i + 2048]))
        tgt = rest[np.argsort(-d, kind="stable")[:k]]
    else:
        raise ValueError(c["sel"])
    return rand, np.sort(np.asarray(tgt, int))


def run(j, log=print, _stop_after=None):
    t0 = time.time()
    c = dict(config.COMBO_DEFAULTS, **config.COMBOS[j["strategy"]])
    split = (data.dev_split(j["pair"], j["seed"]) if j["setting"] == "dev"
             else data.temporal_split(j["pair"], j["seed"]))
    X_tr, y_tr, X_val, y_val = split["X_tr"], split["y_tr"], split["X_val"], split["y_val"]
    X_pool, y_pool, rnd, X_te, y_te = split["X_pool"], split["y_pool"], split["round_pool"], split["X_te"], split["y_te"]
    R = split["n_rounds"]
    sens, alpha = config.TARGET_SENSITIVITY, config.CONFORMAL_ALPHA
    need_emb = c["sel"] in ("hybrid", "novelty") or c["iw"] or c["cal"] == "weighted"
    if need_emb:
        pca = runner._embedding(j, split)
        E_pool, E_tr, E_val = pca.transform(X_pool), pca.transform(X_tr), pca.transform(X_val)
    hold_mask = (np.random.default_rng([j["seed"], 7]).random(len(y_pool)) < config.RECAL_FRACTION
                 if c["cal"] == "holdout" else None)

    # state (all indices are into the pool); restored from the checkpoint after a crash
    st = dict(rand=[], tgt=[], p_acq=[], ps_idx=[], ps_y=[], a_thr=1 - sens, a_s=alpha, a_r=alpha, recs=[])
    ck = runner._read(runner._f("ckpt", j))
    if ck and ck.get("fingerprint") == split["fingerprint"]:
        st = ck["state"]
        log(f"    resuming from round {len(st['rand'])}/{R}")

    def flat(key):
        return np.array([i for r in st[key] for i in r], int)

    def train():
        rand, tgt, ps_i, ps_y = flat("rand"), flat("tgt"), flat("ps_idx"), flat("ps_y")
        bought = np.r_[rand, tgt]
        if c["cal"] == "holdout":
            fit_idx, cal_idx = bought[~hold_mask[bought]], bought[hold_mask[bought]]
        elif c["cal"] == "rand_hold":
            fit_idx, cal_idx = tgt, rand
        else:
            fit_idx, cal_idx = bought, np.zeros(0, int)
        wb = np.full(len(fit_idx), c["w_new"], float)
        if c["iw"] and len(fit_idx) >= 10:
            seen = np.where(rnd < len(st["rand"]))[0]
            wb *= _domain_weights(E_pool[fit_idx], E_pool[seen], (0.2, 5.0))
        X = np.concatenate([X_tr, X_pool[fit_idx], X_pool[ps_i]])
        y = np.concatenate([y_tr, y_pool[fit_idx], ps_y]).astype(int)
        w = np.concatenate([np.ones(len(y_tr)), wb, np.full(len(ps_i), config.SSL_WEIGHT)])
        m = models.make(j["pair"], j["seed"]).fit(X, y, w)
        pv = m.predict_proba(X_val)
        pc, yc = pv, y_val
        if c["cal"] in ("holdout", "rand_hold") and len(cal_idx):
            pn, yn = m.predict_proba(X_pool[cal_idx]), y_pool[cal_idx]
            pc, yc = (pn, yn) if yn.sum() >= config.RECAL_MIN_R else (np.r_[pv, pn], np.r_[y_val, yn])
        elif c["cal"] == "rand_preq" and len(rand):
            pn, yn = np.array([v for r in st["p_acq"] for v in r], float), y_pool[rand]
            pc, yc = (pn, yn) if yn.sum() >= config.RECAL_MIN_R else (np.r_[pv, pn], np.r_[y_val, yn])
        if c["cal"] == "weighted" and len(st["rand"]):
            seen = np.where(rnd < len(st["rand"]))[0]
            wv = _domain_weights(E_val, E_pool[seen], (0.05, 20.0))
            t = _weighted_threshold(y_val, pv, wv, sens)
            q = _weighted_q(pv, y_val, wv, alpha)
            q_ps = _weighted_q(pv, y_val, wv, config.PSEUDO_ALPHA)
        elif c["cal"] == "aci":
            t = metrics.threshold_for_sensitivity(y_val, pv, 1 - st["a_thr"])
            q = _q_two_alpha(pv, y_val, st["a_s"], st["a_r"])
            q_ps = conformal.fit(pv, y_val, config.PSEUDO_ALPHA)
        else:
            t = metrics.threshold_for_sensitivity(yc, pc, sens)
            q = conformal.fit(pc, yc, alpha)
            q_ps = conformal.fit(pc, yc, config.PSEUDO_ALPHA)
        return m, t, q, q_ps, len(yc), int(yc.sum())

    def evaluate(m, t, q):
        pt = m.predict_proba(X_te)
        has_s, has_r = conformal.sets(pt, q)
        out = metrics.evaluate(y_te, pt, t)
        out.update(cov_R=float(has_r[y_te == 1].mean()) if (y_te == 1).any() else None,
                   cov_S=float(has_s[y_te == 0].mean()) if (y_te == 0).any() else None)
        return out

    m, t, q, q_ps, cal_n, cal_R = train()
    if not st["recs"]:
        st["recs"].append(dict(round=0, labels_total=0, **evaluate(m, t, q)))

    for r in range(len(st["rand"]), R):
        cand = np.where(rnd == r)[0]
        p = m.predict_proba(X_pool[cand])
        rng = np.random.default_rng([j["seed"], r, int.from_bytes(j["strategy"].encode()[:4].ljust(4, b"_"), "little")])
        if c["sel"] == "none":
            rp, tp = np.zeros(0, int), np.zeros(0, int)
        elif c["sel"] == "all":
            rp, tp = np.arange(len(cand)), np.zeros(0, int)
        else:
            b = runner._per_round(j["budget"], R, r)
            E_lab = np.concatenate([E_tr, E_pool[flat("rand")], E_pool[flat("tgt")]]) if need_emb else None
            rp, tp = choose(c, b, p, t, E_pool[cand] if need_emb else None, E_lab, rng)
        untested = np.ones(len(cand), bool)
        untested[rp] = False
        untested[tp] = False
        op = metrics.error_counts(y_pool[cand][untested], p[untested], t)
        # adaptive levels: nudge after every lab result, in arrival order (scores from the model in use)
        if c["cal"] == "aci":
            for pos in np.sort(np.r_[rp, tp]):
                yy, pp = y_pool[cand[pos]], p[pos]
                if yy == 1:
                    st["a_thr"] = float(np.clip(st["a_thr"] + ACI_GAMMA * ((1 - sens) - float(pp < t)), 0.005, 0.5))
                    st["a_r"] = float(np.clip(st["a_r"] + ACI_GAMMA * (alpha - float(1 - pp > q[1])), 0.005, 0.5))
                else:
                    st["a_s"] = float(np.clip(st["a_s"] + ACI_GAMMA * (alpha - float(pp > q[0])), 0.005, 0.5))
        ps_i, ps_y = np.zeros(0, int), np.zeros(0, int)
        if c["pseudo"] == "conformal":
            has_s, has_r = conformal.sets(p, q_ps)
            one_s, one_r = untested & has_s & ~has_r, untested & has_r & ~has_s
            ps_i, ps_y = np.r_[cand[one_s], cand[one_r]], np.r_[np.zeros(one_s.sum(), int), np.ones(one_r.sum(), int)]
        st["rand"].append(cand[rp].tolist())
        st["tgt"].append(cand[tp].tolist())
        st["p_acq"].append(p[rp].tolist())
        st["ps_idx"].append(ps_i.tolist())
        st["ps_y"].append(ps_y.tolist())
        if len(rp) or len(tp) or len(ps_i):
            m, t, q, q_ps, cal_n, cal_R = train()
        bought = np.r_[flat("rand"), flat("tgt")]
        rec = dict(round=r + 1, n_candidates=int(len(cand)), labels_round=int(len(rp) + len(tp)),
                   labels_total=int(len(bought)), n_random=int(len(flat("rand"))), R_bought_total=int(y_pool[bought].sum()),
                   n_ambiguous=int(conformal.ambiguous(p, q).sum()), cal_n=cal_n, cal_R=cal_R,
                   a_thr=st["a_thr"], n_pseudo=int(len(ps_i)),
                   pseudo_acc=float((y_pool[ps_i] == ps_y).mean()) if len(ps_i) else None,
                   op_untested=op["n"], op_vme_count=op["vme_count"], op_me_count=op["me_count"], op_R=op["n_R"],
                   **evaluate(m, t, q))
        st["recs"].append(rec)
        runner._write(runner._f("ckpt", j), dict(fingerprint=split["fingerprint"], state=st))
        if _stop_after is not None and r + 1 >= _stop_after:
            raise runner._SimulatedCrash(f"stopped after round {r + 1} (test)")

    import platform, socket, os, sklearn, xgboost
    recs = st["recs"]
    return dict(job={k: v for k, v in j.items()}, combo=c, metrics=recs, final=recs[-1],
                rounds_mode=split["rounds_mode"], fingerprint=split["fingerprint"],
                sizes=dict(train=int(len(y_tr)), val=int(len(y_val)), pool=int(len(y_pool)), test=int(len(y_te)),
                           train_R=int(y_tr.sum()), pool_R=int(y_pool.sum()), test_R=int(y_te.sum())),
                device=models.device(), model=config.MODEL, params=models.best_params(j["pair"]),
                seconds=round(time.time() - t0, 1), finished=time.strftime("%Y-%m-%d %H:%M:%S"),
                worker=os.environ.get("AMR_WORKER", ""), host=socket.gethostname(),
                versions=dict(python=platform.python_version(), xgboost=xgboost.__version__, sklearn=sklearn.__version__))
