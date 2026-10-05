"""Load the compact DRIAMS copy and build the train / validation / pool / test splits."""
import hashlib
import os
import shutil

import numpy as np
import pandas as pd

from . import config, paths

_cache = {}


# ------------------------------------------------------------------ storage
def data_root():
    """Local copy if staged (much faster than reading from Drive), else the Drive copy."""
    local = os.path.join(paths.LOCAL_CACHE, "driams_compact")
    return local if os.path.isdir(local) else paths.DATA


def stage_to_local(sites=None):
    """Copy the compact data from Drive to the Colab disk once per session."""
    src_root = paths.DATA
    dst_root = os.path.join(paths.LOCAL_CACHE, "driams_compact")
    sites = sites or sorted(d for d in os.listdir(src_root) if os.path.isdir(os.path.join(src_root, d)))
    for site in sites:
        src, dst = os.path.join(src_root, site), os.path.join(dst_root, site)
        if os.path.isdir(dst) and _size(dst) == _size(src):
            continue
        if os.path.isdir(dst):
            shutil.rmtree(dst)
        print(f"copying {site} to local disk ({_size(src)/1e9:.2f} GB) ...", flush=True)
        shutil.copytree(src, dst)
    return dst_root


def _size(d):
    return sum(os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk(d) for f in fs)


def available():
    root = data_root()
    if not os.path.isdir(root):
        return {}
    out = {}
    for site in sorted(os.listdir(root)):
        sdir = os.path.join(root, site)
        if os.path.isdir(sdir):
            out[site] = sorted(y for y in os.listdir(sdir) if os.path.isfile(os.path.join(sdir, y, "X.npy")))
    return out


def load_site_year(site, year):
    key = ("sy", site, year, data_root())
    if key not in _cache:
        d = os.path.join(data_root(), site, year)
        X = np.load(os.path.join(d, "X.npy"), mmap_mode="r")
        meta = pd.read_csv(os.path.join(d, "meta.csv"), low_memory=False)
        meta["code"] = meta["code"].astype(str)
        _cache[key] = (X, meta)
    return _cache[key]


def encode(series):
    """R/I -> 1, S -> 0, anything else (missing, '-', 'R(1)', ...) -> NaN."""
    return series.map(lambda v: config.LABEL_MAP.get(str(v).strip(), np.nan)).astype(float)


def load_pair(site, years, species, antibiotic):
    """All labelled spectra of one species/antibiotic at a site over some years."""
    key = ("pair", site, tuple(years), species, antibiotic, data_root())
    if key in _cache:
        return _cache[key]
    Xs, ys, codes, yrs, dates = [], [], [], [], []
    for year in years:
        X, meta = load_site_year(site, year)
        if antibiotic not in meta.columns:
            raise KeyError(f"{antibiotic} not in {site} {year} columns")
        y = encode(meta[antibiotic])
        keep = (meta["species"] == species).values & ~np.isnan(y.values)
        idx = np.where(keep)[0]
        Xs.append(np.asarray(X[idx], dtype=np.float32))
        ys.append(y.values[idx].astype(int))
        codes += list(meta["code"].values[idx])
        yrs += [year] * len(idx)
        if "acquisition_date" in meta.columns:
            dates += list(pd.to_datetime(meta["acquisition_date"].values[idx], errors="coerce"))
        else:
            dates += [pd.NaT] * len(idx)
    out = dict(X=np.concatenate(Xs) if Xs else np.zeros((0, config.N_BINS), np.float32),
               y=np.concatenate(ys) if ys else np.zeros(0, int),
               code=np.array(codes), year=np.array(yrs), date=pd.to_datetime(pd.Series(dates)).values)
    _cache[key] = out
    return out


# ------------------------------------------------------------------ rounds (arrival batches)
def assign_rounds(codes, dates, n_rounds):
    """Arrival batch of each pool isolate.

    If acquisition dates exist for all isolates and n_rounds == 4: calendar quarters.
    If dates exist but n_rounds != 4: equal-sized chunks in date order.
    Otherwise: a fixed pseudo-random batch from a hash of the isolate code (not seed-dependent).
    """
    dates = pd.to_datetime(pd.Series(dates))
    if len(dates) and dates.notna().all():
        if n_rounds == 4:
            return ((dates.dt.month.values - 1) // 3).astype(int), "calendar_quarter"
        order = np.argsort(dates.values, kind="stable")
        r = np.empty(len(dates), int)
        r[order] = np.minimum(np.arange(len(dates)) * n_rounds // len(dates), n_rounds - 1)
        return r, "date_order"
    h = np.array([int(hashlib.md5(c.encode()).hexdigest(), 16) % n_rounds for c in codes], int)
    return h, "hash_of_code (no acquisition dates)"


def _stratified_split(y, frac, seed):
    rng = np.random.default_rng(seed)
    held = np.zeros(len(y), bool)
    for c in np.unique(y):
        idx = np.where(y == c)[0]
        rng.shuffle(idx)
        held[idx[: int(round(frac * len(idx)))]] = True
    return held


# ------------------------------------------------------------------ splits
def temporal_split(pair, seed, site="DRIAMS-A"):
    species, ab = config.PAIRS[pair]
    tr = load_pair(site, config.TRAIN_YEARS, species, ab)
    po = load_pair(site, [config.POOL_YEAR], species, ab)
    te = load_pair(site, [config.TEST_YEAR], species, ab)
    val = _stratified_split(tr["y"], config.VAL_FRACTION, seed)
    rounds, mode = assign_rounds(po["code"], po["date"], config.N_ROUNDS)
    return dict(X_tr=tr["X"][~val], y_tr=tr["y"][~val], X_val=tr["X"][val], y_val=tr["y"][val],
                X_pool=po["X"], y_pool=po["y"], round_pool=rounds, code_pool=po["code"],
                X_te=te["X"], y_te=te["y"], n_rounds=config.N_ROUNDS, rounds_mode=mode,
                X_emb_fit=tr["X"], fingerprint=_fp(po["code"], te["code"]))


def dev_split(pair, seed, site="DRIAMS-A"):
    """Development split for the combination search (never touches 2018).

    Train/validation as in temporal_split; the 2017 isolates of arrival batches 1-2 form the pool
    (re-divided into N_ROUNDS rounds), batches 3-4 form the test set.
    """
    species, ab = config.PAIRS[pair]
    tr = load_pair(site, config.TRAIN_YEARS, species, ab)
    po = load_pair(site, [config.POOL_YEAR], species, ab)
    val = _stratified_split(tr["y"], config.VAL_FRACTION, seed)
    batch, mode = assign_rounds(po["code"], po["date"], 4)
    pool, test = np.isin(batch, [0, 1]), np.isin(batch, [2, 3])
    rounds = np.random.default_rng(2017).permutation(int(pool.sum())) % config.N_ROUNDS
    return dict(X_tr=tr["X"][~val], y_tr=tr["y"][~val], X_val=tr["X"][val], y_val=tr["y"][val],
                X_pool=po["X"][pool], y_pool=po["y"][pool], round_pool=rounds, code_pool=po["code"][pool],
                X_te=po["X"][test], y_te=po["y"][test], n_rounds=config.N_ROUNDS, rounds_mode="dev: " + mode,
                X_emb_fit=tr["X"], fingerprint=_fp(po["code"][pool], po["code"][test]))


def crosssite_split(pair, target_site, seed):
    species, ab = config.PAIRS[pair]
    src = load_pair(config.SOURCE_SITE, config.SOURCE_YEARS, species, ab)
    tgt = load_pair(target_site, [config.TARGET_YEAR], species, ab)
    val = _stratified_split(src["y"], config.VAL_FRACTION, seed)
    test = _stratified_split(tgt["y"], config.TARGET_TEST_FRACTION, seed + 1000)
    return dict(X_tr=src["X"][~val], y_tr=src["y"][~val], X_val=src["X"][val], y_val=src["y"][val],
                X_pool=tgt["X"][~test], y_pool=tgt["y"][~test], round_pool=np.zeros((~test).sum(), int),
                code_pool=tgt["code"][~test], X_te=tgt["X"][test], y_te=tgt["y"][test],
                n_rounds=1, rounds_mode="single_batch", X_emb_fit=src["X"],
                fingerprint=_fp(tgt["code"][~test], tgt["code"][test]))


def _fp(*arrays):
    h = hashlib.sha1()
    for a in arrays:
        h.update("\n".join(map(str, a)).encode())
    return h.hexdigest()[:12]


def clear_cache():
    _cache.clear()
