"""Which arriving isolates get sent for a lab test.

Every strategy returns positions (into the current round's candidates) of the
isolates to label. Inputs come from the model in use when the isolates arrive.

random       uniform at random
uncertainty  closest to the decision threshold, |p - t| smallest
diversity    k-center greedy in PCA space: farthest from everything already labelled
hybrid       the 4b most uncertain, then k-means into b clusters, one isolate per cluster
routing      conformal safety rule: only isolates whose prediction set is ambiguous;
             if more than b, a random subset of them (never fills up with others)
routing_all  every ambiguous isolate, no budget cap
"""
import numpy as np

from . import config, conformal


def select(name, b, p, t, emb_cand, emb_labelled, rng, q=None):
    n = len(p)
    if b is None or n == 0:
        pass
    elif b <= 0:
        return np.zeros(0, int)
    elif b >= n and not name.startswith("routing"):
        return np.arange(n)
    if name == "random":
        return np.sort(rng.choice(n, size=b, replace=False))
    if name == "uncertainty":
        return np.sort(np.argsort(np.abs(p - t), kind="stable")[:b])
    if name == "diversity":
        return np.sort(k_center(emb_cand, emb_labelled, b))
    if name == "hybrid":
        m = min(n, config.HYBRID_POOL_FACTOR * b)
        top = np.argsort(np.abs(p - t), kind="stable")[:m]
        return np.sort(top[_kmeans_pick(emb_cand[top], b, rng)])
    if name in ("routing", "routing_all"):
        amb = np.where(conformal.ambiguous(p, q))[0]
        if name == "routing" and b is not None and len(amb) > b:
            amb = rng.choice(amb, size=b, replace=False)
        return np.sort(amb)
    raise ValueError(f"unknown strategy {name}")


def k_center(cand, labelled, b, chunk=2048):
    """Greedy k-center (Sener & Savarese, ICLR 2018)."""
    d = np.full(len(cand), np.inf)
    for i in range(0, len(labelled), chunk):
        d = np.minimum(d, _min_dist(cand, labelled[i:i + chunk]))
    chosen = []
    for _ in range(b):
        j = int(np.argmax(d))
        chosen.append(j)
        d = np.minimum(d, np.linalg.norm(cand - cand[j], axis=1))
        d[j] = -1
    return np.array(chosen, int)


def _min_dist(a, b):
    aa = (a * a).sum(1)[:, None]
    bb = (b * b).sum(1)[None, :]
    return np.sqrt(np.maximum(aa + bb - 2 * a @ b.T, 0)).min(1)


def _kmeans_pick(emb, b, rng):
    from sklearn.cluster import KMeans
    if b >= len(emb):
        return np.arange(len(emb))
    km = KMeans(n_clusters=b, n_init=3, random_state=int(rng.integers(1 << 31))).fit(emb)
    picks = []
    for c in range(b):
        idx = np.where(km.labels_ == c)[0]
        if len(idx):
            picks.append(idx[np.argmin(np.linalg.norm(emb[idx] - km.cluster_centers_[c], axis=1))])
    return np.array(sorted(set(picks)), int)


def split_name(strategy):
    """'uncertainty+ssl' -> ('uncertainty', True); 'ssl_only' -> (None, True)."""
    if strategy == "ssl_only":
        return None, True
    if strategy.endswith("+ssl"):
        return strategy[:-4], True
    return strategy, False
