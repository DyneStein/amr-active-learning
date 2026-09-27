"""Class-conditional (Mondrian) split conformal prediction for a binary classifier.

Score = 1 - p(true class). Calibrated separately on the S and R validation
isolates, so each class gets its own coverage guarantee (important because
resistant isolates are the minority).
"""
import math

import numpy as np


def fit(p_cal, y_cal, alpha):
    q = {}
    for c in (0, 1):
        pc = p_cal[y_cal == c]
        s = 1 - (pc if c == 1 else 1 - pc)
        n = len(s)
        if n == 0:
            q[c] = 1.0
            continue
        level = min(1.0, math.ceil((n + 1) * (1 - alpha)) / n)
        q[c] = float(np.quantile(s, level, method="higher"))
    return q


def sets(p, q):
    """Returns (contains_S, contains_R) boolean arrays.

    Score of S is 1 - p(S) = p; score of R is 1 - p(R) = 1 - p.
    """
    return p <= q[0], (1 - p) <= q[1]


def ambiguous(p, q):
    """Isolates the model cannot call with confidence: both labels in the set, or neither."""
    has_s, has_r = sets(p, q)
    return has_s == has_r
