"""Evaluation: AUROC, AUPRC, and the clinical error rates used in AST.

very major error (VME): truly resistant, reported susceptible  -> FN / #R
major error (ME):       truly susceptible, reported resistant  -> FP / #S
"""
import math

import numpy as np
from sklearn.metrics import average_precision_score, balanced_accuracy_score, roc_auc_score


def threshold_for_sensitivity(y, p, target):
    """Largest threshold t with sensitivity(R) >= target when predicting R for p >= t."""
    pos = np.sort(p[y == 1])[::-1]
    if len(pos) == 0:
        return 0.5
    k = max(1, math.ceil(target * len(pos)))
    return float(pos[k - 1])


def evaluate(y, p, t):
    out = dict(n=int(len(y)), n_R=int((y == 1).sum()))
    if len(y) == 0:
        return out
    both = len(np.unique(y)) == 2
    out["auroc"] = float(roc_auc_score(y, p)) if both else float("nan")
    out["auprc"] = float(average_precision_score(y, p)) if both else float("nan")
    pred = (p >= t).astype(int)
    R, S = y == 1, y == 0
    out["vme"] = float((pred[R] == 0).mean()) if R.any() else float("nan")
    out["me"] = float((pred[S] == 1).mean()) if S.any() else float("nan")
    out["bal_acc"] = float(balanced_accuracy_score(y, pred)) if both else float("nan")
    out["threshold"] = float(t)
    return out


def error_counts(y, p, t):
    """Raw counts, for isolates whose model result would be used without a lab test."""
    pred = (p >= t).astype(int)
    return dict(n=int(len(y)), n_R=int((y == 1).sum()),
                vme_count=int(((y == 1) & (pred == 0)).sum()),
                me_count=int(((y == 0) & (pred == 1)).sum()))
