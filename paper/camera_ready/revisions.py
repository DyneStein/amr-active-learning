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
recomputation of the statistical tests.

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

# Table IV: every temporal comparison against random selection, read from stats/camera_ready_E1_vs_random.csv
# (output of camera_ready_stats.py), so each number in the table traces to the per run records.
def _effects():
    import csv
    import os
    rows = list(csv.DictReader(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "stats",
                                                   "camera_ready_E1_vs_random.csv"))))
    key = {(r["pair"], int(r["budget"]), r["rule"]): r for r in rows}
    assert len(key) == 45

    def cell(r):
        m, lo, hi = (100 * float(r[k]) for k in ("mean_diff", "ci_lo", "ci_hi"))
        assert abs((hi - m) - (m - lo)) < 1e-3          # Student t interval, so mean +/- half width is exact
        mark = r"$^{\dagger}$" if (lo > 0 or hi < 0) else ""
        return ("$-$" if m < -0.05 else "") + f"{abs(m):.1f}{mark}" + r"$\pm$" + f"{hi - m:.1f}"

    body = ""
    names = {"ecoli_cro": "\\textit{E. coli}", "kpneu_cro": "\\textit{K. pneu.}", "saur_oxa": "\\textit{S. aureus}"}
    for i, pair in enumerate(names):
        if i:
            body += "\\midrule\n"
        for j, rule in enumerate(("uncertainty", "diversity", "hybrid")):
            body += (names[pair] if j == 0 else "") + f" & {rule[:3].capitalize()}. & " + \
                " & ".join(cell(key[(pair, b, rule)]) for b in (40, 100, 200, 400, 800)) + " \\\\\n"
    return ("\\begin{table}[!t]\n\\caption{Mean paired AUROC difference ($\\times$100) between each rule and random "
            "selection on the 2018 isolates, $\\pm$ the half width of its 95\\% confidence interval (10 seeds). "
            "A dagger marks an interval excluding zero.}\n\\label{tab:effects}\n"
            "\\centering\\scriptsize\n\\setlength{\\tabcolsep}{1.6pt}\n\\begin{tabular}{@{}llrrrrr@{}}\n\\toprule\n"
            "\\textit{Pair} & \\textit{Rule} & \\textit{40} & \\textit{100} & \\textit{200} & \\textit{400} & "
            "\\textit{800} \\\\\n\\midrule\n" + body + "\\bottomrule\n\\end{tabular}\n\\end{table}\n")


RAW = {"T4": _effects()}

# ----------------------------------------------------------------------------- text changes
# Rules for this 6 page version: the submitted sentences are kept word for word; space is found only by deleting
# sentences that repeat something said elsewhere, and the reviewer changes are kept as short as accuracy allows.
CHANGES = {}

CHANGES["FRONT"] = [
    ("5 budgets and 10 seeds per configuration.", "5 budgets and 10 seeds per configuration (5 across hospitals)."),
    ("during 2017 in 4 quarterly rounds, and were tested on 2018.", "during 2017 in 4 rounds, and were tested on 2018."),
    ("Across 165 paired comparisons no uncertainty, diversity or hybrid rule beat random selection after correction "
     "for multiple testing, and 2 were worse.",
     "Across 135 paired comparisons no uncertainty, diversity or hybrid rule beat random selection after correction "
     "for multiple testing."),
]

CHANGES["S1"] = [
    ("2017 are offered to an acquisition rule in 4 quarterly rounds under a fixed budget",
     "2017 are offered to an acquisition rule in 4 rounds under a fixed budget"),
    ("The main result is negative and holds across 165 paired comparisons",
     "The main result is negative and holds across 135 paired comparisons"),
    # deletions for length
    ("for MALDI-TOF resistance prediction, covering 3 species and antibiotic pairs, 4 hospitals and 5 budgets, with "
     "10 seeds per configuration.", "for MALDI-TOF resistance prediction."),
    ("rely on the same spectral regions (Fig. 4 and Table III), which is consistent with the absence of a difference "
     "between them.", "rely on the same spectral regions (Table III)."),
    (", but whether it does so for MALDI-TOF resistance prediction has not been established", ""),
    (", which turns the useful quantity into cost,", ","),
    (" Work on this modality either assumes that all labels are already present or evaluates a fixed training set.", ""),
    (" [2], released under a CC0 public domain waiver and archived at Dryad (doi:10.5061/<wbr>dryad.<wbr>bzkh1899q).",
     " [2]."),
]

CHANGES["S2"] = [
    (" prediction was extended to several antibiotics at once,", ""),
    (" Those settings resemble ours in that labels are expensive and the data distribution moves, but none of them "
     "involves mass spectra or susceptibility testing.", ""),
    ("has rarely reported the 2 clinical error types separately (Table I).",
     "has rarely reported the 2 clinical error types separately."),
    (" The combination of a temporal protocol, an explicit test budget, both error types, and an explanation of why "
     "the acquisition rules behave as they do is what this paper contributes.", ""),
]

CHANGES["S3"] = [
    (", measured as the absolute difference between the 2 [10].", " [10]."),
    # the descriptions now match the code that produced the results
    ("Diversity sampling applies a <i>k</i>-center greedy procedure in the spectral space so that the selected "
     "isolates are spread out rather than clustered [11]. The hybrid rule splits the round budget evenly between "
     "the uncertainty and diversity criteria [14].",
     "Diversity sampling applies a <i>k</i>-center greedy procedure to the first 50 principal components of the "
     "spectra so that the selected isolates are spread out rather than clustered [11]. The hybrid rule takes the "
     "4<i>b</i> isolates closest to the threshold, where <i>b</i> is the number bought in the round, and buys one "
     "from each of <i>b</i> clusters formed by <i>k</i>-means [14]."),
    # deletions for length
    ("They distribute a single prediction across the input features in the unique way that satisfies local accuracy, "
     "missingness and consistency, and for tree ensembles they have an exact polynomial time solution, so no "
     "sampling approximation is involved. ", ""),
    ("library itself [19], which removes any possibility of a mismatch between the explained model and the deployed "
     "one.", "library itself [19]."),
    ("Importance of a bin is its mean absolute SHAP value, and its direction was obtained by splitting the isolates "
     "at the median intensity of that bin and taking the difference in mean SHAP between the halves, because "
     "averaging signed values over all isolates simply follows the majority class (here susceptible).",
     "Importance of a bin is its mean absolute SHAP value."),
]

CHANGES["S4"] = [
    # Reviewer 1 point 1 and Reviewer 2 point 3
    ("rather than by calendar quarter. The cross site experiment moves a model trained at DRIAMS-A to each of "
     "DRIAMS-B, DRIAMS-C and DRIAMS-D.",
     "rather than by calendar quarter (the MD5 digest of the code modulo 4). The batches decide which isolates "
     "compete for the budget of a round, but their order carries no calendar information. The cross site "
     "experiment moves a model trained at DRIAMS-A to each of DRIAMS-B, DRIAMS-C and DRIAMS-D. The source model "
     "was fitted on the DRIAMS-A isolates of 2015 to 2018, the 2018 isolates of the target site were divided in "
     "half, stratified by label and redrawn for every seed, into a pool and a test set, the budget (25 to 400 "
     "labels) was spent in a single round, and the model was refitted on the source isolates together with the "
     "bought ones. <i>S. aureus</i> with oxacillin has no labelled isolates at DRIAMS-D, which leaves 8 "
     "combinations of pair and site."),
    (", and labels follow the convention of the original release, in which resistant and intermediate are coded "
     "together as 1", ""),
    ("to set the threshold <i>t</i> at the lowest value achieving 90% sensitivity to resistance",
     "to set the threshold <i>t</i> at the highest value that still gave 90% sensitivity to resistance"),
    ("giving 1540 retraining simulations in total.",
     "giving 1540 retraining simulations in total (660 temporal and 880 cross site)."),
    # Reviewer 2 point 1 and the editor's note
    ("Each rule was compared with random selection on matched seeds using the Wilcoxon signed rank test, and the "
     "resulting p values were corrected across the whole family of comparisons with the Holm procedure [20]. "
     "Only the corrected values are reported below.",
     "Each rule was compared with random selection on matched seeds using the exact two sided Wilcoxon signed rank "
     "test on the paired difference in test AUROC, and the resulting p values were corrected with the Holm "
     "procedure [20], both within each species and antibiotic pair (15 comparisons) and across all 45 temporal "
     "comparisons. With 10 seeds no value can fall below 0.002 before correction, 0.029 after correction within a "
     "pair or 0.088 across all 45, and with the 5 seeds of the cross site setting no test can reach 0.05, so every "
     "comparison is also given as the mean paired difference with its 95% confidence interval (Table IV)."),
]

CHANGES["S5"] = [
    ("of which 14 reached p &lt; 0.05 before correction and 2 survived the Holm procedure, both of them in favour of "
     "random selection. Uncertainty sampling on <i>K. pneumoniae</i> at 800 labels was worse by 0.029 AUROC "
     "(p = 0.029 corrected) and diversity sampling on <i>S. aureus</i> at 40 labels was worse by 0.008 "
     "(p = 0.029 corrected). The cross site experiment adds 120 further comparisons across DRIAMS-B, DRIAMS-C and "
     "DRIAMS-D, and none of those reached significance in either direction, before or after correction. These 165 "
     "paired comparisons produce no evidence that an informed rule helps, and 2 instances in which it hurts. The "
     "result held over 3 species, 2 antibiotic classes, 4 hospitals and 2 deployment settings, including the cross "
     "site case in which the new data differs most from the training data and in which AL would be expected to "
     "help most.</p>",
     "of which 14 reached p &lt; 0.05 before correction (12 against the rule and 2 for it, as Table IV "
     "shows) and 2 survived the Holm procedure within their pair, both of them in "
     "favour of random selection. Uncertainty sampling on <i>K. pneumoniae</i> at 800 labels was worse by 0.029 "
     "AUROC (95% confidence interval 0.014 to 0.045) and diversity sampling on <i>S. aureus</i> at 40 labels was "
     "worse by 0.008 (0.003 to 0.013), each at p = 0.029. Corrected across all 45 instead, no comparison stays "
     "below 0.05 (smallest 0.088). The cross site experiment adds 120 further comparisons, but in 30 of them the "
     "budget was at least as large as the pool of the target site, so every rule bought the same isolates. Of the "
     "other 90 the mean difference was negative in 64, and its interval excluded zero in 7, 6 against the rule and "
     "1 for it. These 135 paired comparisons produce no evidence that an informed rule helps, and the differences "
     "that can be detected mostly favour random selection.</p>\n@@RAW|T4@@\n\n"
     # Reviewer 2 point 2
     "<p>Because the batches are a pseudo ordering, the comparison at 100, 400 and 800 labels was repeated with 3 "
     "further divisions of the 2017 pool drawn from independent hashes and once with the whole budget bought in a "
     "single round, and a rerun of the original division reproduced all 360 published runs exactly. After "
     "correction within each pair, 8 comparisons across the 5 divisions favoured random selection and 1 favoured a "
     "rule (diversity sampling on <i>K. pneumoniae</i> at 800 labels, better by 0.025, 0.014 to 0.036, and positive "
     "in every division), and uncertainty sampling at 800 labels reduced the resistant isolates reported "
     "susceptible in every division and for every pair.</p>"),
    # deletions for length
    (" The antibiotic is ceftriaxone for the first 2 pairs and oxacillin for the third.", ""),
    ("Contrary to what might be expected, uncertainty", "Uncertainty"),
    (" The paired tests make this precise.", ""),
    (" It finds the cases the model was about to get wrong, and it does so while spending less of the budget on "
     "cases the model already handles correctly.", ""),
    (" A small shared core is found by every model and the tail shifts with the training set.", ""),
    (", where 1.00 means identical lists and 0.00 means no bin in common", ""),
    ("The comparison that stands out is the last one before the mean. ", ""),
    ("Because all 6 models are fitted to the same underlying relationship, and the easily located part of it is "
     "located by all of them, similar accuracy is the expected outcome. ", ""),
    ("makes the structure clearer (Fig. 4).", "makes the structure clearer."),
    (" We do not assign these masses to particular proteins. The low mass region is crowded, several known markers "
     "fall within a few daltons of one another, and a 3 dalton bin cannot separate them.", ""),
    (" Retraining helps, and the direction of the effect was consistent across all 3 pairs, which confirms the "
     "premise of the study. The size of the effect is modest.", ""),
]

CHANGES["S6"] = [
    (" The SHAP analysis supports this reading, since the models converged on the same bins regardless of how their "
     "labels were selected (Fig. 4).", ""),
    (" A laboratory choosing a policy has to decide whether it is optimising next year's model or this year's "
     "reports.", ""),
    # consistent with Table IV
    ("since it costs the least, it is no worse than random selection by AUROC in all but one configuration, and",
     "since it costs the least, it gives up little AUROC against random selection (0.017 on average over the "
     "budgets for <i>K. pneumoniae</i>, 0.006 for <i>S. aureus</i> and nothing measurable for <i>E. coli</i>), and"),
    ("because it is the one configuration where uncertainty sampling lost AUROC outright",
     "because it is the configuration where uncertainty sampling lost the most AUROC"),
    # Reviewer 1 point 3
    ("price of 66 additional major errors over the year.</p>",
     "price of 66 additional major errors over the year. A major error lasts only until the culture based result "
     "arrives, so about 5 additional major errors for each very major error avoided is a trade that a laboratory may "
     "accept, but it is a trade rather than a free gain. On the 2018 isolates the models maintained by uncertainty sampling also made more very "
     "major errors and fewer major errors than those maintained by random selection in 14 of the 15 "
     "configurations, so a laboratory adopting the rule should set <i>t</i> again on recent labels.</p>"),
    # Reviewer 1 points 1 and 4
    ("although the year boundaries themselves are real.",
     "although the year boundaries themselves are real. The simulation therefore represents drift between years "
     "but not within a year, and a rule that adapts to recent isolates could gain from a real ordering in a way "
     "these experiments cannot show."),
    ("All of this is a retrospective simulation on stored spectra, and",
     "All of this is a retrospective simulation on stored spectra, in which a bought label is available at once, "
     "and the safety result needs confirmation on isolates collected in real time before it is used to set a "
     "testing policy. Beyond that,"),
    ("Label acquisition rules for the maintenance of MALDI-TOF resistance prediction models were evaluated under a "
     "temporal protocol on DRIAMS. ", ""),
    ("Across 165 paired comparisons spanning 3 species and antibiotic pairs, 4 hospitals and 5 budgets, no "
     "uncertainty, diversity or hybrid rule outperformed random selection, and 2 performed worse.",
     "Across 135 paired comparisons spanning 3 species and antibiotic pairs, 4 hospitals and 5 budgets, no "
     "uncertainty, diversity or hybrid rule outperformed random selection."),
    ("Future work should test whether these conclusions hold prospectively, and",
     "Future work should test whether these conclusions hold prospectively, on isolates with real acquisition "
     "dates, and"),
]
