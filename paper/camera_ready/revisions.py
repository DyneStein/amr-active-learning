"""Everything the camera ready version changes relative to the submitted paper (../ieee.py).

CHANGES maps a section of ieee.py to (old passage, new passage) pairs. Whitespace is normalised before
matching. Text is in the same light HTML as ieee.py (<i>, &lt;) and is converted to LaTeX by build.py.
Numbers quoted here come from Results/extra/camera_ready_stats.py and camera_ready_robust.py.
"""

# ----------------------------------------------------------------------------- front matter
AUTHORS = [
    ("Muhammad Dyen Asif", "i240608@isb.nu.edu.pk"),
    ("Hira Mastoor", "hira.mastoor@nu.edu.pk"),
    ("Maryam Shahbaz", "maryam.shahbaz@nu.edu.pk"),
]


def _author(name, email):
    return ("\\IEEEauthorblockN{%s}\n\\IEEEauthorblockA{\\textit{Department of Computer Science} \\\\\n"
            "\\textit{National University of Computer}\\\\\n\\textit{and Emerging Sciences}\\\\\n"
            "Islamabad, Pakistan \\\\\n%s}" % (name, email))


PREAMBLE = r"""\documentclass[conference,a4paper]{IEEEtran}
\IEEEoverridecommandlockouts
\usepackage[T1]{fontenc}
\usepackage{newtxtext,newtxmath}
\usepackage{cite}
\usepackage{amsmath}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{array}
\renewcommand\IEEEkeywordsname{Keywords}
\setlength{\tabcolsep}{3pt}

\begin{document}

\title{Cost and Safety of Label Acquisition Strategies for\\
MALDI-TOF Antimicrobial Resistance Prediction}

\author{""" + "\n\\and\n".join(_author(n, e) for n, e in AUTHORS) + r"""}

\IEEEpubid{\makebox[\columnwidth]{979-8-3195-2818-6/26/\$31.00~\copyright2026 IEEE\hfill}
\hspace{\columnsep}\makebox[\columnwidth]{ }}

\maketitle
\IEEEpubidadjcol

"""

ACK = r"""\section*{Acknowledgment}
An AI assistant (Claude, Anthropic) was used to support the writing of the analysis code and the
recomputation of the statistical tests. The authors take full responsibility for the content of the paper.

"""


# ----------------------------------------------------------------------------- tables
def _t1(cap):
    rows = [("Weis \\textit{et al.} \\cite{r2}", "AMR from MALDI-TOF, DRIAMS", "4", "no", "no", "no", "no"),
            ("Weis \\textit{et al.} \\cite{r5}", "Topological and kernel methods", "1", "no", "no", "no", "no"),
            ("Duroux \\textit{et al.} \\cite{r6}", "Generalisation to unseen sites", "4", "yes", "no", "no", "no"),
            ("Corvelo Benz \\textit{et al.} \\cite{r7}", "Conformal guarantees, DRIAMS", "4", "no", "no", "partly", "no"),
            ("Schmidt-Santiago \\textit{et al.} \\cite{r4}", "Review of 115 MALDI-TOF ML studies", "n/a", "rare", "none", "rare", "21/115"),
            ("Chen \\textit{et al.} \\cite{r8}", "AL with selective prediction, images", "n/a", "no", "yes", "no", "no"),
            ("Chen \\textit{et al.} \\cite{r9}", "Continuous learning, malware", "n/a", "yes", "yes", "no", "no")]
    body = "\n".join(" & ".join(r) + " \\\\" for r in rows)
    return ("\\begin{table}[!t]\n\\caption{@CAP@}\n\\label{tab:position}\n\\centering\\footnotesize\n"
            "\\begin{tabular}{@{}>{\\raggedright}p{1.62cm}>{\\raggedright}p{2.5cm}c@{\\hspace{4pt}}c@{\\hspace{4pt}}c@{\\hspace{4pt}}c@{\\hspace{4pt}}c@{}}\n\\toprule\n"
            "\\textit{Study} & \\textit{Task and data} & \\textit{Sites} & \\textit{Temp.} & \\textit{Cost} & "
            "\\textit{Errors} & \\textit{XAI} \\\\\n\\midrule\n" + body +
            "\n\\midrule\nThis work & AL for AMR from MALDI-TOF, DRIAMS & 4 & yes & yes & yes & yes \\\\\n"
            "\\bottomrule\n\\end{tabular}\n\\end{table}\n").replace("@CAP@", cap)


def _t2(cap):
    rows = [("\\textit{E. coli}", "400", "2094", "80.9\\%", "0.50", "0.43", "0.54", "0.38"),
            ("", "800", "2094", "61.8\\%", "0.66", "0.52", "0.70", "0.90"),
            ("\\textit{K. pneumoniae}", "400", "1273", "68.6\\%", "0.77", "0.28", "0.65", "0.60"),
            ("", "800", "1273", "37.2\\%", "0.66", "0.02", "0.82", "0.67"),
            ("\\textit{S. aureus}", "400", "1445", "72.3\\%", "0.60", "0.38", "0.41", "0.57"),
            ("", "800", "1445", "44.6\\%", "0.77", "0.52", "0.65", "0.85")]
    body = ""
    for i, r in enumerate(rows):
        body += ("\\midrule\n" if i in (2, 4) else "") + " & ".join(r) + " \\\\\n"
    return ("\\begin{table}[!t]\n\\caption{@CAP@}\n\\label{tab:cost}\n\\centering\\footnotesize\n"
            "\\setlength{\\tabcolsep}{2.3pt}\n\\begin{tabular}{@{}lrrrrrrr@{}}\n\\toprule\n"
            "\\textit{Pair} & \\textit{\\shortstack[r]{Tests\\\\bought}} & \\textit{Of pool} & "
            "\\textit{\\shortstack[r]{Tests\\\\saved}} & \\textit{Random} & \\textit{Uncert.} & \\textit{Divers.} & "
            "\\textit{Hybrid} \\\\\n\\midrule\n" + body + "\\bottomrule\n\\end{tabular}\n\\end{table}\n").replace("@CAP@", cap)


def _t3(cap):
    rows = [("Random 400 vs uncertainty 400", "0.60", "0.38", "0.38", "0.44", "0.54", "0.44"),
            ("Random 800 vs uncertainty 800", "0.60", "0.39", "0.29", "0.44", "0.43", "0.48"),
            ("Random 800 vs retrain on all", "0.67", "0.40", "0.38", "0.52", "0.60", "0.54"),
            ("Uncertainty 800 vs retrain on all", "0.60", "0.39", "0.38", "0.48", "0.43", "0.47"),
            ("No retraining vs retrain on all", "0.43", "0.24", "0.11", "0.22", "0.29", "0.30"),
            ("Mean over all 15 model pairs", "0.60", "0.36", "0.31", "0.40", "0.49", "0.44")]
    body = ""
    for i, r in enumerate(rows):
        body += ("\\midrule\n" if i in (2, 4) else "") + " & ".join(r) + " \\\\\n"
    return ("\\begin{table}[!t]\n\\caption{@CAP@}\n\\label{tab:shap}\n\\centering\\footnotesize\n"
            "\\begin{tabular}{@{}lrrrrrr@{}}\n\\toprule\n"
            " & \\multicolumn{2}{c}{\\textit{E. coli}} & \\multicolumn{2}{c}{\\textit{K. pneu.}} & "
            "\\multicolumn{2}{c}{\\textit{S. aureus}} \\\\\n\\cmidrule(lr){2-3}\\cmidrule(lr){4-5}\\cmidrule(l){6-7}\n"
            "\\textit{Models compared} & \\textit{J} & $\\rho$ & \\textit{J} & $\\rho$ & \\textit{J} & $\\rho$ \\\\\n"
            "\\midrule\n" + body + "\\bottomrule\n\\end{tabular}\n\\end{table}\n").replace("@CAP@", cap)


TABLES = {"I": _t1, "II": _t2, "III": _t3}

# Table IV: cross site sizes, bounds and pooled differences (Results/extra/camera_ready_stats.txt and the
# per site block computed on 12 Nov 2026 from Results/results/E4_crosssite).
T4 = r"""\begin{table}[!t]
\caption{Cross site experiment. Pool and test are the 2 halves of the 2018 isolates of the target site, with
the resistant isolates of the test half in parentheses. None and All are the test AUROC of the source model
used unchanged and of the model refitted on the whole pool. The last 3 columns are the mean paired AUROC
difference of each rule against random selection over the budgets smaller than the pool, and a dagger marks
a 95\% confidence interval that excludes zero.}
\label{tab:cross}
\centering\footnotesize
\setlength{\tabcolsep}{2.2pt}
\begin{tabular}{@{}llrrrrrrr@{}}
\toprule
\textit{Pair} & \textit{Site} & \textit{Pool} & \textit{Test} & \textit{None} & \textit{All} & \textit{Unc.} & \textit{Div.} & \textit{Hyb.} \\
\midrule
\textit{E. coli} & B & 107 & 106 (22) & 0.835 & 0.860 & $-0.007$ & $+0.002$ & $-0.007$ \\
 & C & 458 & 458 (76) & 0.659 & 0.705 & $-0.006$ & $+0.001$ & $-0.006$ \\
 & D & 997 & 997 (99) & 0.777 & 0.788 & $-0.002$ & $-0.004$ & $-0.000$ \\
\midrule
\textit{K. pneu.} & B & 76 & 76 (9) & 0.477 & 0.614 & $-0.020$ & $-0.059^{\dagger}$ & $-0.049^{\dagger}$ \\
 & C & 182 & 184 (28) & 0.585 & 0.682 & $-0.031^{\dagger}$ & $-0.014$ & $-0.007$ \\
 & D & 1075 & 1076 (62) & 0.616 & 0.638 & $-0.004$ & $-0.007$ & $-0.003$ \\
\midrule
\textit{S. aureus} & B & 174 & 172 (10) & 0.800 & 0.829 & $+0.000$ & $-0.006$ & $-0.013$ \\
 & C & 370 & 368 (20) & 0.648 & 0.691 & $+0.010$ & $+0.006$ & $-0.001$ \\
\bottomrule
\end{tabular}
\end{table}
"""

# Table V: Results/extra/camera_ready_robust.txt (notebook 06, 1800 runs, 13 Nov 2026).
T5 = r"""\begin{table}[!t]
\caption{The temporal comparison under other divisions of the 2017 pool into arrival batches (27 comparisons per
division, budgets of 100, 400 and 800 labels). Min and Max are the smallest and largest mean paired AUROC
difference of a rule against random selection, Neg. counts the negative ones, and Against and For count the
comparisons below 0.05 after correction within each pair. The last 3 columns are the change in resistant isolates
reported susceptible under uncertainty sampling at 800 labels.}
\label{tab:robust}
\centering\footnotesize
\setlength{\tabcolsep}{2.0pt}
\begin{tabular}{@{}lrrrrrrrr@{}}
\toprule
\textit{Division} & \textit{Min} & \textit{Max} & \textit{Neg.} & \textit{Against} & \textit{For} & \textit{E. c.} & \textit{K. p.} & \textit{S. a.} \\
\midrule
Main experiment & $-0.029$ & $+0.011$ & 18 & 1 & 0 & $-33\%$ & $-73\%$ & $-51\%$ \\
Redrawn 1 & $-0.024$ & $+0.025$ & 16 & 1 & 1 & $-35\%$ & $-58\%$ & $-51\%$ \\
Redrawn 2 & $-0.044$ & $+0.011$ & 19 & 1 & 0 & $-34\%$ & $-68\%$ & $-67\%$ \\
Redrawn 3 & $-0.021$ & $+0.009$ & 20 & 2 & 0 & $-43\%$ & $-52\%$ & $-65\%$ \\
Single round & $-0.062$ & $+0.009$ & 17 & 3 & 0 & $-33\%$ & $-60\%$ & $-53\%$ \\
\bottomrule
\end{tabular}
\end{table}
"""

RAW = {"T4": T4, "T5": T5}

# ----------------------------------------------------------------------------- text changes
CHANGES = {}

CHANGES["FRONT"] = [
    ("during 2017 in 4 quarterly rounds, and were tested on 2018.",
     "during 2017 in 4 rounds, and were tested on 2018."),
    ("Across 165 paired comparisons no uncertainty, diversity or hybrid rule beat random selection after "
     "correction for multiple testing, and 2 were worse.",
     "Across 135 comparisons no uncertainty, diversity or hybrid rule beat random selection after "
     "correction for multiple testing, and none did consistently once the batches were redrawn."),
]

CHANGES["S1"] = [
    ("2017 are offered to an acquisition rule in 4 quarterly rounds under a fixed budget",
     "2017 are offered to an acquisition rule in 4 rounds under a fixed budget"),
    ("The main result is negative and holds across 165 paired comparisons",
     "The main result is negative and holds across 135 paired comparisons"),
]

CHANGES["S3"] = [
    ("Diversity sampling applies a <i>k</i>-center greedy procedure in the spectral space so that the selected "
     "isolates are spread out rather than clustered [11]. The hybrid rule splits the round budget evenly between "
     "the uncertainty and diversity criteria [14].",
     "Diversity sampling applies a <i>k</i>-center greedy procedure to the first 50 principal components of the "
     "spectra so that the selected isolates are spread out rather than clustered [11]. The hybrid rule takes the "
     "4<i>b</i> isolates closest to the threshold, where <i>b</i> is the number bought in the round, groups them "
     "into <i>b</i> clusters by <i>k</i>-means on the same components, and buys the isolate nearest the centre of "
     "each cluster [14]."),
]

CHANGES["S4"] = [
    # IV-A: what the hash is, and the cross site protocol as its own subsection
    ("The released spectra carry no acquisition dates, so the 4 arrival batches were formed by a deterministic "
     "hash of the isolate code rather than by calendar quarter. The cross site experiment moves a model trained "
     "at DRIAMS-A to each of DRIAMS-B, DRIAMS-C and DRIAMS-D.</p>",
     "The released spectra carry no acquisition dates, so the 4 arrival batches were formed by a deterministic "
     "hash of the isolate code rather than by calendar quarter (the MD5 digest of the code modulo 4, which is the "
     "same for every rule and seed and gives batches of about a quarter of the pool each). The batches decide "
     "which isolates compete for the budget of a round, but their order carries no calendar information.</p>\n\n"
     "<h3>B. Cross site protocol</h3>\n"
     "<p class=\"ni\">The cross site experiment moves a model trained at DRIAMS-A to each of DRIAMS-B, DRIAMS-C "
     "and DRIAMS-D. The source model was fitted on the DRIAMS-A isolates of all 4 years (4961, 2860 and 3790 for "
     "the 3 pairs, a fifth of them held out for the threshold). The 2018 isolates of the target site were divided "
     "in half, stratified by label and redrawn for every seed, into a pool from which labels could be bought and "
     "a test set (Table IV). The budget (25, 50, 100, 200 or 400 labels) was spent in a single round, the model "
     "was refitted on the source isolates together with the bought ones at equal weight, and the 2 bounds are the "
     "source model used unchanged and the model refitted on the whole pool. <i>S. aureus</i> with oxacillin has "
     "no labelled isolates at DRIAMS-D, which leaves 8 combinations of pair and target site.</p>\n@@RAW|T4@@"),
    ("<h3>B. Model and protocol</h3>", "<h3>C. Model and protocol</h3>"),
    ("to set the threshold <i>t</i> at the lowest value achieving 90% sensitivity to resistance",
     "to set the threshold <i>t</i> at the highest value that still gave 90% sensitivity to resistance"),
    ("Every configuration was repeated with 10 random seeds, and the cross site configurations with 5, giving "
     "1540 retraining simulations in total.",
     "Every configuration was repeated with 10 random seeds, and the cross site configurations with 5, giving "
     "1540 retraining simulations in total (660 temporal, from 3 pairs, 22 configurations made of 4 rules at 5 "
     "budgets and the 2 bounds, and 10 seeds, and 880 cross site, from 8 combinations of pair and site, 22 "
     "configurations and 5 seeds). A seed fixes the held out fifth of the training data, the draws of random "
     "selection, the subsampling inside the model and, in the cross site setting, the division of the target "
     "site into pool and test set, so a rule and random selection at the same seed differ only in which isolates "
     "were bought."),
    ("<h3>C. Statistics and availability</h3>", "<h3>D. Statistics and availability</h3>"),
    ("Each rule was compared with random selection on matched seeds using the Wilcoxon signed rank test, and the "
     "resulting p values were corrected across the whole family of comparisons with the Holm procedure [20]. "
     "Only the corrected values are reported below.",
     "Each rule was compared with random selection on matched seeds, the paired quantity being the difference in "
     "test AUROC between the rule and random selection at the same pair, site, budget and seed. The test is the "
     "exact two sided Wilcoxon signed rank test, with 10 pairs of runs per comparison in the temporal setting and "
     "5 in the cross site setting, and the resulting p values were corrected with the Holm procedure [20] within "
     "each species and antibiotic pair (15 comparisons, from 3 rules and 5 budgets) and also across all 45 "
     "temporal comparisons. An exact test on 10 seeds cannot return a value below 0.002, so no temporal "
     "comparison can fall below 0.029 after correction within a pair or below 0.088 after correction across all "
     "45, and on 5 seeds the floor is 0.0625 before any correction, which means that the cross site tests could "
     "not have reached 0.05 whatever the data. The effect size is therefore given for every comparison as the "
     "mean paired difference in AUROC with its 95% confidence interval (Student <i>t</i>, 9 or 4 degrees of "
     "freedom)."),
]

CHANGES["S5"] = [
    ("The temporal setting gives 45 comparisons against random selection (3 pairs, 5 budgets and 3 competing "
     "rules), of which 14 reached p &lt; 0.05 before correction and 2 survived the Holm procedure, both of them "
     "in favour of random selection. Uncertainty sampling on <i>K. pneumoniae</i> at 800 labels was worse by "
     "0.029 AUROC (p = 0.029 corrected) and diversity sampling on <i>S. aureus</i> at 40 labels was worse by "
     "0.008 (p = 0.029 corrected). The cross site experiment adds 120 further comparisons across DRIAMS-B, "
     "DRIAMS-C and DRIAMS-D, and none of those reached significance in either direction, before or after "
     "correction. These 165 paired comparisons produce no evidence that an informed rule helps, and 2 instances "
     "in which it hurts.",
     "The temporal setting gives 45 comparisons against random selection (3 pairs, 5 budgets and 3 competing "
     "rules), in which the mean paired difference ran from 0.029 AUROC below random selection to 0.012 above it. "
     "Before correction 14 of them reached p &lt; 0.05, 12 in favour of random selection and 2 in favour of the "
     "rule (diversity sampling on <i>K. pneumoniae</i> at 200 labels and the hybrid rule on <i>E. coli</i> at "
     "800, each better by about 0.01). Corrected within each pair, 2 remained below 0.05 and both favoured random "
     "selection. Uncertainty sampling on <i>K. pneumoniae</i> at 800 labels was worse by 0.029 AUROC (95% "
     "confidence interval 0.014 to 0.045) and diversity sampling on <i>S. aureus</i> at 40 labels was worse by "
     "0.008 (0.003 to 0.013), each at a corrected p of 0.029, which is the floor of the design. Corrected across "
     "all 45 the smallest value is 0.088, so under the stricter family no comparison is significant in either "
     "direction, and the 2 losses are the largest effects observed rather than established ones. Averaged over "
     "the 5 budgets, no rule had an interval above zero for any pair, and uncertainty sampling on "
     "<i>K. pneumoniae</i> was worse by 0.017 (0.010 to 0.025).</p>\n\n"
     "<p>The cross site experiment adds 120 further comparisons across DRIAMS-B, DRIAMS-C and DRIAMS-D. In 30 of "
     "them the budget was at least as large as the pool of the target site, so every rule bought the same "
     "isolates and the difference is zero by construction, which leaves 90 that are informative. None of these "
     "can reach significance on 5 seeds, so they are read as effect sizes. The mean difference was negative in "
     "64 of the 90 and positive in 26, it ran from 0.073 below random selection to 0.019 above it, and its 95% "
     "interval excluded zero in 7 comparisons (6 against the rule and 1 for it), against the 4 or 5 that chance "
     "would produce at that level. Averaged over the informative budgets, 3 of the 24 combinations of pair, site "
     "and rule had an interval below zero and none had one above it (Table IV). These 135 paired comparisons "
     "produce no evidence that an informed rule helps, and where a difference can be detected it favours random "
     "selection."),
]

CHANGES["S5"] += [
    ("<h3>C. Cost of a partial test budget</h3>",
     "<h3>C. Sensitivity to the arrival batches</h3>\n"
     "<p class=\"ni\">Because the batches are a pseudo ordering, the comparison was repeated with the same data, "
     "model and seeds but with the 2017 pool divided differently (Table V). Three further divisions were drawn "
     "from independent hashes of the isolate code, and in a fourth setting the sequence was removed altogether and "
     "the whole budget was bought in a single round. Budgets of 100, 400 and 800 labels were used, which gives 27 "
     "comparisons per division, each corrected within its pair (9 comparisons). The division of the main "
     "experiment was rerun alongside as a reference, and it reproduced all 360 of the corresponding runs exactly. "
     "The picture did not change. The mean difference was negative in 16 to 20 of the 27 comparisons of every "
     "division, and after correction 8 comparisons across the 5 divisions favoured random selection against 1 "
     "that favoured a rule (diversity sampling on <i>K. pneumoniae</i> at 800 labels in one redrawn division, "
     "better by 0.025, 95% confidence interval 0.014 to 0.036). That comparison was positive in all 5 divisions, "
     "by 0.004 to 0.025, and it is the only advantage of any rule that recurred. Uncertainty sampling on "
     "<i>K. pneumoniae</i> at 800 labels was worse in every division, by 0.021 to 0.062. The operational result "
     "was equally stable. Uncertainty sampling at 800 labels reduced the resistant isolates reported susceptible "
     "in every division and for every pair (by 33% to 43% for <i>E. coli</i>, 52% to 73% for "
     "<i>K. pneumoniae</i> and 51% to 67% for <i>S. aureus</i>), with a 95% interval that excluded zero in all 15 "
     "cases.</p>\n@@RAW|T5@@\n\n<h3>D. Cost of a partial test budget</h3>"),
]

CHANGES["S6"] = [
    # VI-B: the AUROC cost of uncertainty sampling, stated with the intervals now reported
    ("since it costs the least, it is no worse than random selection by AUROC in all but one configuration, and "
     "it substantially reduces",
     "since it costs the least, it gives up little AUROC against random selection (0.017 on average over the "
     "budgets for <i>K. pneumoniae</i>, 0.006 for <i>S. aureus</i> and nothing measurable for <i>E. coli</i>), and "
     "it substantially reduces"),
    # VI-B: practical meaning of the major errors (Reviewer 1, point 3)
    ("and a laboratory working on that organism would be buying a 73% reduction in very major errors at the "
     "price of 66 additional major errors over the year.</p>",
     "and a laboratory working on that organism would be buying a 73% reduction in very major errors at the "
     "price of 66 additional major errors over the year.</p>\n\n"
     "<p>A major error puts a patient on a broader agent than was needed until the culture based result arrives 1 "
     "to 3 days later, and it adds to the selection pressure that stewardship tries to limit, whereas a very "
     "major error leaves an infection on a drug that does not work. About 5 additional major errors for each "
     "very major error avoided (66 against 14) is a trade that a laboratory may accept, but it is a trade rather "
     "than a free gain. Its origin is visible in the first round, in which both rules face the same model and "
     "the same threshold. With <i>t</i> as low as 0.014 the isolates nearest to it are those the model would "
     "report susceptible, so a budget that covers 63% of the pool (800 of 1273) confirms nearly all of the "
     "susceptible reports by testing and leaves the resistant reports unconfirmed, and 75% of the untested "
     "susceptible isolates then lay above the threshold, against 42% under random selection. The model handed to "
     "the following year shows a related shift. On the 2018 isolates the models maintained by uncertainty "
     "sampling made more very major errors and fewer major errors than those maintained by random selection in "
     "14 of the 15 configurations (at 400 labels for <i>E. coli</i>, rates of 0.22 against 0.14 and of 0.29 "
     "against 0.45), so the rule moves the operating point as well as the training set, and a laboratory that "
     "adopts it should set <i>t</i> again on recent labels rather than keep the value fitted to the training "
     "years.</p>"),
    # VI-C: limits of the simulated ordering (Reviewer 1, point 1) and need for real time validation (point 4)
    ("The released spectra carry no acquisition dates, so the arrival batches within 2017 are a deterministic "
     "pseudo ordering rather than true calendar quarters, although the year boundaries themselves are real.",
     "The released spectra carry no acquisition dates, so the arrival batches within 2017 are a deterministic "
     "pseudo ordering rather than true calendar quarters, although the year boundaries themselves are real. The "
     "simulation therefore represents drift between years but not within a year, and anything that changes "
     "during a year (the seasonal mix of isolates, an outbreak, a serviced or replaced instrument) reaches every "
     "batch in equal measure. A rule that adapts to recent isolates could gain from a real ordering in a way "
     "these experiments cannot show, and redrawing the batches establishes only that the result does not depend on "
     "one particular division."),
    ("All of this is a retrospective simulation on stored spectra, and a prospective study would have to contend "
     "with laboratory turnaround, with clinicians who may override the model, and with instrument changes that "
     "our protocol holds fixed.",
     "All of this is a retrospective simulation on stored spectra from the hospitals of a single country, in "
     "which a bought label is available at once, and a prospective study would have to contend with laboratory "
     "turnaround (the result of a susceptibility test returns after the report has been issued), with clinicians "
     "who may override the model, and with instrument changes that our protocol holds fixed. The operational "
     "counts are what the reports would have been rather than what happened to patients, so the safety result in "
     "particular needs confirmation on isolates collected in real time, with their dates, before it is used to "
     "set a testing policy."),
    # VII
    ("Across 165 paired comparisons spanning 3 species and antibiotic pairs, 4 hospitals and 5 budgets, no "
     "uncertainty, diversity or hybrid rule outperformed random selection, and 2 performed worse.",
     "Across 135 paired comparisons spanning 3 species and antibiotic pairs, 4 hospitals and 5 budgets, no "
     "uncertainty, diversity or hybrid rule outperformed random selection, and the differences that could be "
     "detected favoured random selection. The same held when the pool year was divided into batches in 4 other "
     "ways."),
    ("Future work should test whether these conclusions hold prospectively, and",
     "Future work should test whether these conclusions hold prospectively, on isolates with real acquisition "
     "dates, and"),
]
