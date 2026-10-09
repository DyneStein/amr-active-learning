"""Run experiments as small resumable jobs that several Colab accounts can share.

One job = (experiment, pair, site, strategy, budget, seed). While a job runs,
its progress is saved after every round to checkpoints/, so a disconnect
loses at most one round. A finished job writes results/<exp>/<job_id>.json.

Several accounts can run workers at the same time on the same Drive folder:
a worker first writes a claim file; other workers skip claimed jobs until the
claim is older than CLAIM_TTL_HOURS (then the job is assumed abandoned and
resumes from its checkpoint). Giving each account its own shard (0..N-1)
avoids two workers ever picking the same job at the same moment.
"""
import hashlib
import json
import os
import platform
import socket
import time

import numpy as np

from . import config, conformal, data, metrics, models, paths, strategies

_pca_cache = {}
_init_cache = {}          # the round-0 model is identical for every strategy/budget of a pair+seed


# ------------------------------------------------------------------ job list
def job_id(j):
    b = "none" if j["budget"] is None else j["budget"]
    return f"{j['exp']}__{j['pair']}__{j['site']}__{j['strategy'].replace('+', 'P')}__b{b}__s{j['seed']}"


def all_jobs(experiments=None):
    exps = experiments or config.PRIORITY
    jobs = []
    for exp in exps:
        e = config.EXPERIMENTS[exp]
        sites = e.get("sites", ["DRIAMS-A"]) if e["setting"] == "crosssite" else ["DRIAMS-A"]
        skip = {tuple(x) for x in e.get("skip", [])}
        for pair in e["pairs"]:
            for site in sites:
                if (pair, site) in skip:
                    continue
                for seed in e["seeds"]:
                    base = dict(exp=exp, setting=e["setting"], pair=pair, site=site, seed=seed)
                    if e.get("include_bounds"):
                        jobs.append(dict(base, strategy="none", budget=0))
                        jobs.append(dict(base, strategy="full", budget="all"))
                    for s in e["strategies"]:
                        if s == "ssl_only":
                            jobs.append(dict(base, strategy=s, budget=0))
                        elif s == "routing_all":
                            jobs.append(dict(base, strategy=s, budget=None))
                        else:
                            for b in e["budgets"]:
                                jobs.append(dict(base, strategy=s, budget=b))
    for j in jobs:
        j["id"] = job_id(j)
    return jobs


def _f(kind, j):
    root = {"result": paths.RESULTS, "ckpt": paths.CHECKPOINTS, "claim": paths.CLAIMS}[kind]
    return os.path.join(root, j["exp"], j["id"] + ".json")


def _read(path):
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def _write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + f".tmp{os.getpid()}"
    with open(tmp, "w") as f:
        json.dump(obj, f, default=_jsonable)
    os.replace(tmp, path)


def _jsonable(o):
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    return str(o)


# ------------------------------------------------------------------ one job
def _per_round(budget, n_rounds, r):
    base, rem = divmod(int(budget), n_rounds)
    return base + (1 if r < rem else 0)


def _embedding(j, split):
    key = (j["setting"], j["pair"], j["site"], data.data_root())
    if key not in _pca_cache:
        from sklearn.decomposition import PCA
        X = split["X_emb_fit"]
        rng = np.random.default_rng(0)
        fit_rows = X if len(X) <= 20000 else X[rng.choice(len(X), 20000, replace=False)]
        _pca_cache[key] = PCA(n_components=min(config.PCA_DIM, len(fit_rows) - 1),
                              svd_solver="randomized", random_state=0).fit(fit_rows)
    return _pca_cache[key]


class _SimulatedCrash(Exception):
    pass


def run_job(j, log=print, _stop_after=None, trace=None, want_model=False):
    """Run one job. `trace` (a list) collects one row per candidate isolate per round,
    so the choices can be audited; `want_model` returns the final fitted model and threshold.
    Both force a fresh run (checkpoints are ignored) so that every round is replayed."""
    if j["strategy"] in config.COMBOS:
        from . import combo
        return combo.run(j, log=log, _stop_after=_stop_after)
    t0 = time.time()
    split = (data.temporal_split(j["pair"], j["seed"]) if j["setting"] == "temporal"
             else data.dev_split(j["pair"], j["seed"]) if j["setting"] == "dev"
             else data.crosssite_split(j["pair"], j["site"], j["seed"]))
    X_tr, y_tr, X_val, y_val = split["X_tr"], split["y_tr"], split["X_val"], split["y_val"]
    X_pool, y_pool, rnd, X_te, y_te = split["X_pool"], split["y_pool"], split["round_pool"], split["X_te"], split["y_te"]
    R = split["n_rounds"]
    code_pool = split["code_pool"]
    base, ssl = strategies.split_name(j["strategy"])
    new_w = config.TARGET_LABEL_WEIGHT if j["setting"] == "crosssite" else config.NEW_LABEL_WEIGHT
    need_emb = base in ("diversity", "hybrid")
    if need_emb:
        pca = _embedding(j, split)
        E_pool, E_tr = pca.transform(X_pool), pca.transform(X_tr)

    recal = config.EXPERIMENTS.get(j["exp"], {}).get("recal", False)
    # E5: a fixed, seed-dependent quarter of the pool is "calibration only" if bought (same for every strategy)
    cal_mask = (np.random.default_rng([j["seed"], 7]).random(len(y_pool)) < config.RECAL_FRACTION) if recal else None

    def train(acq, ps_idx, ps_y):
        cal = np.zeros(0, int)
        if recal:
            acq, cal = acq[~cal_mask[acq]], acq[cal_mask[acq]]
        X = np.concatenate([X_tr, X_pool[acq], X_pool[ps_idx]])
        y = np.concatenate([y_tr, y_pool[acq], ps_y]).astype(int)
        w = np.concatenate([np.ones(len(y_tr)), np.full(len(acq), new_w), np.full(len(ps_idx), config.SSL_WEIGHT)])
        m = models.make(j["pair"], j["seed"]).fit(X, y, w)
        pv, yv = m.predict_proba(X_val), y_val
        if len(cal):                                   # E5: re-calibrate on recent held-out labels
            pc, yc = m.predict_proba(X_pool[cal]), y_pool[cal]
            pv, yv = (pc, yc) if yc.sum() >= config.RECAL_MIN_R else (np.concatenate([pv, pc]), np.concatenate([yv, yc]))
        t = metrics.threshold_for_sensitivity(yv, pv, config.TARGET_SENSITIVITY)
        return m, t, conformal.fit(pv, yv, config.CONFORMAL_ALPHA)

    ck = None if (trace is not None or want_model) else _read(_f("ckpt", j))
    if ck and ck.get("fingerprint") == split["fingerprint"]:
        acq_rounds = [np.array(a, int) for a in ck["acquired"]]
        ps_rounds = [(np.array(a, int), np.array(b, int)) for a, b in ck["pseudo"]]
        recs = ck["metrics"]
        log(f"    resuming from round {len(acq_rounds)}/{R}")
    else:
        acq_rounds, ps_rounds, recs = [], [], []

    def flat():
        acq = np.concatenate(acq_rounds) if acq_rounds else np.zeros(0, int)
        pi = np.concatenate([a for a, _ in ps_rounds]) if ps_rounds else np.zeros(0, int)
        py = np.concatenate([b for _, b in ps_rounds]) if ps_rounds else np.zeros(0, int)
        return acq, pi, py

    init_key = (j["setting"], j["pair"], j["site"], j["seed"], json.dumps(models.best_params(j["pair"]), sort_keys=True),
                split["fingerprint"], data.data_root())
    if not acq_rounds and init_key in _init_cache:
        m, t, q = _init_cache[init_key]
    else:
        m, t, q = train(*flat())
        if not acq_rounds:
            _init_cache.clear()
            _init_cache[init_key] = (m, t, q)
    if not recs:
        recs.append(dict(round=0, labels_total=0, **metrics.evaluate(y_te, m.predict_proba(X_te), t)))

    for r in range(len(acq_rounds), R):
        cand = np.where(rnd == r)[0]
        p = m.predict_proba(X_pool[cand])
        rng = np.random.default_rng([j["seed"], r, int(hashlib.md5(j["strategy"].encode()).hexdigest()[:8], 16)])
        if j["strategy"] == "full":
            sel = np.arange(len(cand))
        elif j["strategy"] == "none" or base is None:
            sel = np.zeros(0, int)
        else:
            b = None if j["budget"] is None else _per_round(j["budget"], R, r)
            acq_so_far = flat()[0]
            E_lab = np.concatenate([E_tr, E_pool[acq_so_far]]) if need_emb else None
            sel = strategies.select(base, b, p, t, E_pool[cand] if need_emb else None, E_lab, rng, q)
        chosen = cand[sel]
        untested = np.ones(len(cand), bool)
        untested[sel] = False
        op = metrics.error_counts(y_pool[cand][untested], p[untested], t)
        if trace is not None:
            order = np.argsort(np.abs(p - t), kind="stable")     # 0 = closest to the threshold
            rank = np.empty(len(p), int)
            rank[order] = np.arange(len(p))
            picked = np.zeros(len(cand), bool)
            picked[sel] = True
            for i in range(len(cand)):
                trace.append(dict(job=j["id"], exp=j["exp"], pair=j["pair"], site=j["site"],
                                  strategy=j["strategy"], budget=j["budget"], seed=j["seed"],
                                  round=r + 1, isolate=str(code_pool[cand[i]]),
                                  p_resistant=round(float(p[i]), 6), threshold=round(float(t), 6),
                                  distance_to_threshold=round(float(abs(p[i] - t)), 6),
                                  uncertainty_rank=int(rank[i]),
                                  sent_for_testing=bool(picked[i]),
                                  true_label="R" if y_pool[cand[i]] == 1 else "S",
                                  model_would_report="R" if p[i] >= t else "S"))
        ps_idx, ps_y = np.zeros(0, int), np.zeros(0, int)
        if ssl:
            hi, lo = untested & (p >= config.SSL_P_HIGH), untested & (p <= config.SSL_P_LOW)
            ps_idx = np.concatenate([cand[hi], cand[lo]])
            ps_y = np.concatenate([np.ones(hi.sum(), int), np.zeros(lo.sum(), int)])
        acq_rounds.append(chosen)
        ps_rounds.append((ps_idx, ps_y))
        if len(chosen) or len(ps_idx):
            m, t, q = train(*flat())
        acq = flat()[0]
        rec = dict(round=r + 1, n_candidates=int(len(cand)), labels_round=int(len(chosen)),
                   labels_total=int(len(acq)), R_bought_total=int(y_pool[acq].sum()),
                   n_ambiguous=int(conformal.ambiguous(p, q).sum()),
                   n_pseudo=int(len(ps_idx)),
                   pseudo_acc=float((y_pool[ps_idx] == ps_y).mean()) if len(ps_idx) else None,
                   op_untested=op["n"], op_vme_count=op["vme_count"], op_me_count=op["me_count"], op_R=op["n_R"],
                   **metrics.evaluate(y_te, m.predict_proba(X_te), t))
        recs.append(rec)
        if trace is None and not want_model:
            _write(_f("ckpt", j), dict(fingerprint=split["fingerprint"], acquired=acq_rounds,
                                       pseudo=[(a, b) for a, b in ps_rounds], metrics=recs))
        if _stop_after is not None and r + 1 >= _stop_after:
            raise _SimulatedCrash(f"stopped after round {r + 1} (test)")

    import sklearn
    import xgboost
    extra = dict(model_object=m, threshold=t, X_te=X_te, y_te=y_te) if want_model else {}
    return dict(**extra, job={k: v for k, v in j.items()}, metrics=recs, final=recs[-1],
                rounds_mode=split["rounds_mode"], fingerprint=split["fingerprint"],
                sizes=dict(train=int(len(y_tr)), val=int(len(y_val)), pool=int(len(y_pool)), test=int(len(y_te)),
                           train_R=int(y_tr.sum()), pool_R=int(y_pool.sum()), test_R=int(y_te.sum())),
                device=models.device(), model=config.MODEL, params=models.best_params(j["pair"]),
                seconds=round(time.time() - t0, 1), finished=time.strftime("%Y-%m-%d %H:%M:%S"),
                worker=os.environ.get("AMR_WORKER", ""), host=socket.gethostname(),
                versions=dict(python=platform.python_version(), xgboost=xgboost.__version__,
                              sklearn=sklearn.__version__))


# ------------------------------------------------------------------ claims + worker loop
def _shard(jid, n):
    return int(hashlib.md5(jid.encode()).hexdigest(), 16) % max(n, 1)


def try_claim(j, worker):
    if os.path.isfile(_f("result", j)):
        return False
    c = _read(_f("claim", j))
    if c and c.get("worker") != worker and time.time() - c.get("time", 0) < config.CLAIM_TTL_HOURS * 3600:
        return False
    _write(_f("claim", j), dict(worker=worker, time=time.time(), host=socket.gethostname()))
    time.sleep(config.CLAIM_CONFIRM_SECONDS)
    c = _read(_f("claim", j))
    return bool(c and c.get("worker") == worker)


def run_worker(worker, shard=0, n_shards=1, experiments=None, hours=4.0, max_jobs=None, log_file=True):
    """Keep running unfinished jobs until the time budget or the job list runs out."""
    os.environ["AMR_WORKER"] = worker
    paths.ensure_dirs()
    t_start, durations, done = time.time(), [], 0
    logf = open(os.path.join(paths.LOGS, f"{worker}.log"), "a") if log_file else None

    def log(msg):
        line = f"[{time.strftime('%H:%M:%S')}] {msg}"
        print(line, flush=True)
        if logf:
            logf.write(line + "\n")
            logf.flush()

    jobs = all_jobs(experiments)
    rng = np.random.default_rng(int(hashlib.md5(worker.encode()).hexdigest()[:8], 16))
    mine = [j for j in jobs if _shard(j["id"], n_shards) == shard]
    others = [j for j in jobs if _shard(j["id"], n_shards) != shard]
    order = mine + [others[i] for i in rng.permutation(len(others))]     # own shard first, then help others
    log(f"worker {worker}: shard {shard}/{n_shards}, {len(mine)} own jobs, device={models.device()}, "
        f"budget {hours:.1f} h")
    for j in order:
        elapsed = (time.time() - t_start) / 3600
        avg = (np.mean(durations[-20:]) / 3600) if durations else 0
        if elapsed + 1.5 * avg > hours:
            log("time budget reached, stopping cleanly")
            break
        if max_jobs is not None and done >= max_jobs:
            break
        if not try_claim(j, worker):
            continue
        log(f"start {j['id']}")
        try:
            t0 = time.time()
            res = run_job(j, log=log)
            _write(_f("result", j), res)
            for kind in ("ckpt", "claim"):
                try:
                    os.remove(_f(kind, j))
                except OSError:
                    pass
            durations.append(time.time() - t0)
            done += 1
            fm = res["final"]
            log(f"done  {j['id']}  {durations[-1]:.0f}s  AUROC={fm.get('auroc', float('nan')):.3f}  "
                f"labels={fm['labels_total']}")
        except Exception as e:
            log(f"FAIL  {j['id']}: {e!r}")
            import traceback
            traceback.print_exc()
    log(f"finished {done} jobs in {(time.time()-t_start)/3600:.2f} h")
    if logf:
        logf.close()
    return done


def status(experiments=None, verbose=True):
    rows = {}
    now = time.time()
    for j in all_jobs(experiments):
        r = rows.setdefault(j["exp"], dict(total=0, done=0, running=0, stale=0))
        r["total"] += 1
        if os.path.isfile(_f("result", j)):
            r["done"] += 1
        else:
            c = _read(_f("claim", j))
            if c:
                if now - c.get("time", 0) < config.CLAIM_TTL_HOURS * 3600:
                    r["running"] += 1
                else:
                    r["stale"] += 1
    if verbose:
        print(f"{'experiment':16s} {'done':>6s} {'total':>6s} {'running':>8s} {'stale':>6s}")
        for k, r in rows.items():
            print(f"{k:16s} {r['done']:6d} {r['total']:6d} {r['running']:8d} {r['stale']:6d}")
    return rows
