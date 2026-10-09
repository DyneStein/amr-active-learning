"""A readable record of every choice the selection rule made.

For each round the model scores every isolate that arrived in that round. This
module replays a run and writes one line per isolate per round:

  isolate                 the DRIAMS isolate code
  p_resistant             the model's probability of resistance for it
  threshold               the decision threshold in force that round
  distance_to_threshold   |p - threshold|; uncertainty sampling buys the smallest
  uncertainty_rank        0 = closest to the threshold in that round
  sent_for_testing        whether the rule bought a lab test for it
  true_label              R or S, from DRIAMS (the model never saw this unless bought)
  model_would_report      what the model would have said without a test

The replay uses the same seeds and the same code path as the real runs, so the
lines describe exactly what happened in the published results.
"""
import os

import numpy as np

from . import config, paths, runner


def trace_jobs(jobs, log=print):
    """Replay the given jobs and return the per-isolate rows as a DataFrame."""
    import pandas as pd
    rows = []
    for j in jobs:
        log(f"tracing {j['id']}")
        runner.run_job(j, log=lambda *_: None, trace=rows)
    return pd.DataFrame(rows)


def jobs_for(pairs=None, strategies=("random", "uncertainty", "diversity", "hybrid"),
             budgets=(400,), seeds=(0,), exp="E1_temporal", site="DRIAMS-A"):
    pairs = list(pairs or config.PAIRS)
    return [dict(exp=exp, setting="temporal", pair=p, site=site, seed=s, strategy=st, budget=b,
                 id=f"{exp}__{p}__{site}__{st}__b{b}__s{s}")
            for p in pairs for st in strategies for b in budgets for s in seeds]


def summarise(df):
    """Per job and round: what was bought, and what that did to the resistant isolates."""
    import pandas as pd
    out = []
    for (job, rnd), g in df.groupby(["job", "round"]):
        bought, left = g[g.sent_for_testing], g[~g.sent_for_testing]
        missed = left[(left.true_label == "R") & (left.model_would_report == "S")]
        out.append(dict(
            job=job, pair=g.pair.iloc[0], strategy=g.strategy.iloc[0], budget=g.budget.iloc[0],
            seed=g.seed.iloc[0], round=rnd,
            arrived=len(g), arrived_resistant=int((g.true_label == "R").sum()),
            tested=len(bought), tested_resistant=int((bought.true_label == "R").sum()),
            resistant_share_arrived=round(float((g.true_label == "R").mean()), 4),
            resistant_share_tested=round(float((bought.true_label == "R").mean()), 4) if len(bought) else None,
            median_distance_tested=round(float(bought.distance_to_threshold.median()), 5) if len(bought) else None,
            median_distance_untested=round(float(left.distance_to_threshold.median()), 5) if len(left) else None,
            resistant_missed_untested=len(missed)))
    return pd.DataFrame(out)


def examples(df, n=15):
    """The isolates closest to the threshold in the first round of each uncertainty run,
    which is what a reviewer asks to see: the actual isolates the rule reached for."""
    import pandas as pd
    out = []
    for job, g in df[df.strategy == "uncertainty"].groupby("job"):
        g1 = g[g["round"] == g["round"].min()].nsmallest(n, "uncertainty_rank")
        out.append(g1)
    return pd.concat(out, ignore_index=True) if out else pd.DataFrame()


def run(out_dir=None, log=print, **kw):
    """Write the three files: full log, per-round summary, closest-to-threshold examples."""
    out_dir = out_dir or paths.LOGS
    os.makedirs(out_dir, exist_ok=True)
    df = trace_jobs(jobs_for(**kw), log=log)
    full = os.path.join(out_dir, "selection_log.csv")
    df.to_csv(full, index=False)
    summarise(df).to_csv(os.path.join(out_dir, "selection_summary.csv"), index=False)
    examples(df).to_csv(os.path.join(out_dir, "selection_examples_uncertainty.csv"), index=False)
    log(f"{len(df)} isolate decisions written to {out_dir}")
    return df
