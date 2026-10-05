# Build one tidy table per experiment from the saved results, for the paper figures.
import os, sys, json, glob, numpy as np, pandas as pd
os.environ["AMR_AL_ROOT"] = "~/Research/Baterial-AMR/Results"
sys.path.insert(0, "~/Research/Baterial-AMR/AMR_AL")
from amr_al import analysis

def tidy(exp):
    df = analysis.load(exp)
    key = ["pair", "site", "strategy", "budget", "seed"]
    op = df.groupby(key).agg(opvme=("op_vme_count", "sum"), opme=("op_me_count", "sum"),
                             opR=("op_R", "sum"), opn=("op_untested", "sum")).reset_index()
    keep = [c for c in ["auroc", "auprc", "vme", "me", "bal_acc", "threshold", "labels_total", "cov_R", "cov_S"] if c in df.columns]
    fin = df[df.final][key + keep]
    f = op.merge(fin, on=key)
    f["sens"] = 1 - f.vme
    f["opS"] = f.opn - f.opR
    f["op_vme_rate"] = f.opvme / f.opR.replace(0, np.nan)
    f["op_me_rate"] = f.opme / f.opS.replace(0, np.nan)
    f["exp"] = exp
    return f

out = {}
for e in ["E1_temporal", "E2_semisup", "E3_routing", "E4_crosssite", "E5_recal", "D1_dev"]:
    out[e] = tidy(e)
    print(e, len(out[e]), "jobs")
pd.concat(out.values(), ignore_index=True).to_csv("/tmp/work/project/7fb83f58-8ee1-4d80-abd0-7a5cdba3f0f3/scratchpad/all_results.csv", index=False)

# round-by-round curves for E1 (learning curves over the year)
df = analysis.load("E1_temporal")
df.to_csv("/tmp/work/project/7fb83f58-8ee1-4d80-abd0-7a5cdba3f0f3/scratchpad/e1_rounds.csv", index=False)
print("cols:", list(df.columns))
