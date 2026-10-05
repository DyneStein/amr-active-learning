# Conference paper: active learning for maintaining MALDI-TOF resistance models. Writes paper.html.
import os

S = "/tmp/work/project/7fb83f58-8ee1-4d80-abd0-7a5cdba3f0f3/scratchpad/"
FIG = S + "fig/"


def svg(name):
    return open(FIG + name + ".svg").read()


def figure(name, num, cap, wide=False, width="100%"):
    body = (f'<figure class="fig"><div class="art" style="width:{width}">{svg(name)}</div>'
            f'<figcaption><b>Fig. {num}.</b> {cap}</figcaption></figure>')
    return f"@@WIDE@@{body}@@/WIDE@@" if wide else body


CSS = """
@page { size: A4; margin: 15mm 14mm 14mm 14mm; }
* { box-sizing: border-box; }
body { font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; color:#0b0b0b; background:#fcfcfb;
       font-size:9pt; line-height:1.42; margin:0; }
.head { text-align:center; margin-bottom:10px; }
h1 { font-size:17.5pt; line-height:1.2; margin:0 0 7px; letter-spacing:-0.1px; }
.head p { text-align:center; }
.auth { font-size:10pt; margin:0 0 2px; }
.aff { font-size:8.6pt; color:#52514e; margin:0; }
.cols { column-count:2; column-gap:7mm; }
.wideblock { margin:8px 0 9px; break-inside:avoid; }
h2 { font-size:10.2pt; margin:11px 0 4px; text-transform:uppercase; letter-spacing:0.4px; color:#0b0b0b;
     border-bottom:1.2px solid #4a3aa7; padding-bottom:2px; break-after:avoid; }
h3 { font-size:9.3pt; margin:8px 0 2px; color:#3b2f86; break-after:avoid; }
p { margin:0 0 5px; text-align:justify; hyphens:auto; }
p.first { text-indent:0; }
.abs { background:#f4f3fb; border-left:3px solid #4a3aa7; padding:7px 10px; margin:0 0 9px; font-size:8.9pt; }
.abs b.k { display:block; margin-top:4px; font-size:8.4pt; color:#52514e; font-weight:600; }
ul, ol { margin:2px 0 6px; padding-left:15px; } li { margin:1.5px 0; }
figure { margin:7px 0 9px; break-inside:avoid; }
figure.wide { column-span:all; margin:9px 0 10px; }
.art { margin:0 auto; }
.art svg { display:block; width:100%; height:auto; }
figcaption { font-size:7.9pt; color:#52514e; margin-top:3px; line-height:1.35; text-align:justify; }
table { border-collapse:collapse; width:100%; table-layout:fixed; margin:4px 0 7px; font-size:7.2pt; break-inside:avoid; }
caption { caption-side:top; text-align:left; font-size:7.9pt; color:#52514e; margin-bottom:3px; }
caption b { color:#0b0b0b; }
th { background:#2b2a28; color:#fcfcfb; text-align:left; padding:2.5px 3px; font-weight:600; font-size:7pt; overflow-wrap:anywhere; }
td { border-bottom:1px solid #e0dfda; padding:2.4px 3px; vertical-align:top; overflow-wrap:anywhere; }
tr.sep td { border-top:1.2px solid #b9b8b2; }
td.n, th.n { text-align:right; font-variant-numeric:tabular-nums; white-space:nowrap; }
.hi { background:#e6f6ef; } .lo { background:#fdecec; } .mid { background:#fdf6e3; }
.box { background:#f6f6f4; border:1px solid #dcdbd5; border-radius:5px; padding:6px 9px; margin:6px 0; font-size:8.5pt; break-inside:avoid; }
.box.key { background:#f4f3fb; border-color:#c3bdea; }
.box.warn { background:#fdf6e3; border-color:#e8d49a; }
.box b.t { display:block; font-size:8.8pt; margin-bottom:2px; }
.eq { text-align:center; font-family:"Times New Roman", Times, serif; font-size:10.5pt; margin:5px 0; }
.ref { font-size:7.7pt; }
.ref ol { padding-left:14px; } .ref li { margin:1.5px 0; }
.tier { display:inline-block; border-radius:2px; padding:0 3px; font-size:6.8pt; font-weight:700;
        vertical-align:1px; margin-left:2px; }
.tA { background:#dcf2e7; color:#0f5c3f; } .tB { background:#e8e6f7; color:#3b2f86; } .tC { background:#f0efea; color:#6b6a64; }
code { font-family:"SF Mono", Menlo, monospace; font-size:8pt; background:#f0efea; padding:0 2px; border-radius:2px; }
sup { font-size:7pt; }
.small { font-size:8.2pt; color:#52514e; }
"""


def head():
    return f"""<div class="head">
<h1>Which isolates should the laboratory test?<br>Active learning, drift and calibration for MALDI-TOF resistance prediction</h1>
<p class="auth">Muhammad Dyen Asif</p>
<p class="aff">[Department, Institution, City, Country] · i240608@isb.nu.edu.pk</p>
</div>"""


ABSTRACT = """<div class="abs">
<b>Abstract.</b> Machine-learning models that predict antibiotic resistance from MALDI-TOF mass spectra lose accuracy as
bacterial populations drift, so they must be retrained on freshly phenotyped isolates. Phenotyping is the expensive step,
which raises a practical question that has not been studied for this modality: <i>given a fixed number of susceptibility
tests per year, which arriving isolates should the laboratory test?</i> We run 2 859 retraining simulations on DRIAMS
(three species–antibiotic pairs, 10 seeds, label budgets of 40–800, four hospitals) comparing random selection with
uncertainty, diversity and hybrid active learning, with conformal safety routing, with pseudo-labelling, and with
re-calibration of the decision rule. Three findings stand out. (1) <b>No selection strategy produced a better model than
random sampling</b> in any of 45 pre-planned comparisons; the number of labels needed to recover 95&nbsp;% of the full
retraining gain was never reached within 800 labels. (2) <b>Selection nonetheless matters for patients</b>: because a
tested isolate receives a laboratory answer, sending the uncertain isolates to the laboratory reduced the resistant
isolates that were wrongly reported susceptible during the year by 33–73&nbsp;% (p&nbsp;&lt;&nbsp;0.01 for all three
pairs), with a species-dependent effect on the opposite error. (3) <b>The safety machinery silently breaks under drift</b>:
a decision threshold set for 90&nbsp;% sensitivity delivered 73–80&nbsp;%, and a conformal rule promising at most
10&nbsp;% miscoverage on resistant isolates delivered 14–19&nbsp;%. Re-calibrating on freshly bought labels restored the
sensitivity target but roughly doubled the opposite error, exposing the real operating cost of that promise at
AUROC&nbsp;0.75–0.85. A pre-registered search over 16 method combinations on a held-out development split reproduced the
same picture and found no combination that improved both error types beyond uncertainty sampling itself. We argue that
label-efficiency is the wrong objective for this problem, and that selection policies should be reported with
deployment-time error counts and with calibration that is maintained, not assumed.
<b class="k">Keywords: antimicrobial resistance · MALDI-TOF mass spectrometry · active learning · dataset shift · conformal prediction · model calibration</b>
</div>"""


S1 = """<h2>1 Introduction</h2>
<p class="first">Antimicrobial resistance is diagnosed in routine practice by phenotypic susceptibility testing, which takes
a day or more after the organism has been identified. Identification itself is nearly instantaneous, because clinical
laboratories already acquire a MALDI-TOF mass spectrum of every isolate. Weis <i>et al.</i> showed that those same spectra
carry a usable resistance signal, and released DRIAMS, a four-hospital collection of spectra paired with laboratory
susceptibility labels <span class="ref">[1]<span class="tier tA">A</span></span>. A model that reads the spectrum can
therefore offer a provisional resistance call hours before the phenotype is available.</p>
<p>Such a model is not a static artefact. Bacterial populations, laboratory workflows and instruments change, and the
same study documented that predictive accuracy decays over time. Keeping the model useful therefore means retraining it
on recently phenotyped isolates — and phenotyping is exactly the cost the model was meant to avoid. A laboratory that
can afford, say, 400 extra susceptibility tests per year faces a concrete choice: <i>which</i> 400 of the thousands of
arriving isolates should be tested?</p>
<p>This is the classical active-learning question <span class="ref">[2]<span class="tier tC">C</span></span>, and the
obvious hypothesis is that an informative subset buys more accuracy per test than a random subset. We set out to measure
how much. The answer, across 2 859 simulated retraining runs, is <i>none that we could detect</i>. That negative result
is worth reporting on its own, because the opposite is widely assumed. But it is not the whole story, and the rest of
this paper is about what the negative result conceals.</p>
<p>The selection rule determines not only what the model learns but <b>who receives a laboratory answer instead of a model
answer</b>. An isolate that is sent for testing is, from the patient's point of view, protected: its true phenotype is
known. An isolate that is not tested is reported with the model's call, errors included. Selection policy is therefore a
patient-safety decision during the year, independent of what it does for next year's model — and on that axis the
strategies differ sharply.</p>
<p>A third thread runs through the results. Both the decision threshold and the conformal prediction sets used in this
setting are calibrated on historical data, and both make explicit promises (90&nbsp;% sensitivity; at most 10&nbsp;%
miscoverage). Under drift, both promises failed quietly while the headline AUROC looked healthy. We quantify the failure,
repair it by re-calibrating on newly bought labels, and show that the repair exposes an operating cost that the broken
calibration had been hiding.</p>
<p><b>Contributions.</b></p>
<ul>
<li>The first study, to our knowledge, of <b>active isolate selection for MALDI-TOF resistance model maintenance</b>:
five experiments, 2 859 runs, three species–antibiotic pairs, four hospitals, full seed replication.</li>
<li>A clear <b>negative result</b> on label efficiency, reported with the statistical power to support it, together with a
<b>positive deployment-time result</b> on the errors that reach patients.</li>
<li>Quantified <b>failure of threshold and conformal calibration under temporal drift</b>, and a measurement of what
restoring the sensitivity promise actually costs.</li>
<li>A <b>pre-registered combination search</b> over 16 method variants on a development split that never touches the test
year, which reproduces the same conclusions and rules out the obvious fixes.</li>
<li>An explicit account of a <b>design flaw in our own pseudo-labelling experiment</b>, reported rather than silently
dropped, so the corresponding question is left open rather than answered wrongly.</li>
</ul>"""


S2 = """<h2>2 Related work</h2>
<h3>Resistance prediction from MALDI-TOF spectra</h3>
<p class="first">DRIAMS established the task and the standard baselines, reporting AUROC near 0.80, 0.74 and 0.74 for
<i>E. coli</i>, <i>K. pneumoniae</i> and <i>S. aureus</i> on the antibiotics we study <span class="ref">[1]<span class="tier tA">A</span></span>.
Subsequent work has improved representations and extended the approach to further organisms. Temporal decay of these
models is documented in the same line of work, so demonstrating decay is not a contribution here; it is the premise we
build on, and we re-verify it (Fig. 3).</p>
<h3>Uncertainty in this modality</h3>
<p class="first">Corvelo Benz <i>et al.</i> applied conformal prediction to MALDI-TOF resistance, obtaining prediction sets
with statistical guarantees <span class="ref">[3]<span class="tier tA">A</span></span>. Our use of conformal sets as a
<i>selection</i> rule (test the isolates the model cannot resolve) builds directly on that work; our contribution is the
observation that its guarantee does not survive a year of drift unless it is re-calibrated, and the measurement of by how
much it fails.</p>
<h3>Active learning</h3>
<p class="first">Uncertainty sampling <span class="ref">[4]<span class="tier tA">A</span></span>, k-center diversity
<span class="ref">[5]<span class="tier tA">A</span></span> and hybrids of the two are the standard pool-based strategies;
importance-weighted <span class="ref">[6]<span class="tier tA">A</span></span>, bandit-selected <span class="ref">[7]<span class="tier tA">A</span></span>
and cost-sensitive <span class="ref">[8]<span class="tier tA">A</span></span> variants address bias, strategy choice and
asymmetric error costs respectively. That random sampling is a stubborn baseline is itself a recurring finding in
benchmark studies, and injecting randomness into uncertainty sampling is a known stabiliser
<span class="ref">[9]<span class="tier tB">B</span></span>. Active learning under distribution shift has been studied in
malware detection, where label-efficient update policies and the decay of conformal evaluation are both documented
<span class="ref">[10, 11]<span class="tier tA">A</span></span>, and in the active–selective-prediction setting
<span class="ref">[12]<span class="tier tA">A</span></span>. None of this literature addresses which bacterial isolates a
clinical laboratory should phenotype, and none of it, to our knowledge, uses the random share of an active-learning budget
as the calibration set for the deployed decision rule.</p>
<h3>Calibration under shift</h3>
<p class="first">Weighted conformal prediction handles covariate shift when a density ratio can be estimated
<span class="ref">[13]<span class="tier tA">A</span></span>, and adaptive conformal inference tracks shift online by
adjusting the target level from feedback <span class="ref">[14]<span class="tier tA">A</span></span>. We implement both as
candidate repairs in the combination search of Section 6.7.</p>"""


S3 = """<h2>3 The maintenance loop</h2>
<p class="first">We simulate exactly the loop a laboratory would run (Fig. 1). A model trained on historical isolates is
in use. New isolates arrive through the year in batches. For each batch the model in use scores every isolate; a selection
rule spends part of a fixed annual budget <i>b</i> on susceptibility tests; the tested isolates return true labels and the
model, its decision threshold and its conformal bounds are refitted. Untested isolates receive the model's call, and any
error there is an error a clinician acts on. At the end of the year the model is evaluated on the following year's
isolates, which are never available during the loop.</p>
<p>Two error types are distinguished throughout, following standard susceptibility-testing terminology
<span class="ref">[15]<span class="tier tA">A</span></span>:</p>
<div class="box"><b class="t">The two errors</b>
<b style="color:#b02a2a">Very major error (VME)</b> — a resistant isolate reported susceptible. The patient may receive an
antibiotic that does not work.<br>
<b style="color:#8a5c08">Major error (ME)</b> — a susceptible isolate reported resistant. The patient may receive an
unnecessarily broad antibiotic, which carries its own harm and cost.<br>
<span class="small">We report both as <i>rates on the following year's isolates</i> (how good the model is) and as
<i>counts among the untested isolates of the current year</i> (how many patients were actually affected while the loop ran).</span>
</div>
<p>This second, operational view is the one that distinguishes selection policies, and it is reported for every run.</p>"""


def s4():
    return f"""<h2>4 Data and protocol</h2>
<p class="first">All experiments use DRIAMS <span class="ref">[1]<span class="tier tA">A</span></span>: each isolate is one
MALDI-TOF spectrum binned into 6 000 intensity features, paired with a laboratory S/I/R label; I and R are both treated as
resistant, following the reference implementation. We study the three species–antibiotic pairs with enough labelled
isolates for repeated simulation: <i>E. coli</i>–ceftriaxone, <i>K. pneumoniae</i>–ceftriaxone and <i>S. aureus</i>–oxacillin.</p>
<p>The temporal protocol (Fig. 2) trains on 2015–2016 isolates from hospital DRIAMS-A (80&nbsp;% training, 20&nbsp;%
validation for the threshold and the conformal bounds), spends the label budget on 2017 isolates arriving in four rounds,
and tests on 2018. DRIAMS carries no acquisition dates, so the four arrival rounds are a fixed pseudo-random partition of
the 2017 isolates derived from a hash of the isolate code; this reproduces the budget-over-time structure but <b>cannot</b>
reproduce within-year drift, a limitation we return to in Section 8. The cross-site protocol moves the 2015–2016 model to
hospitals B, C and D and lets each buy local labels from its own 2018 isolates, holding out a test split.</p>
<p>The classifier is gradient-boosted trees (XGBoost <span class="ref">[16]<span class="tier tA">A</span></span>) with
hyper-parameters tuned once per pair on the training years and then frozen, so that every strategy is compared at equal
model capacity. The decision threshold is set on the validation set as the largest threshold achieving 90&nbsp;%
sensitivity to resistance; class-conditional (Mondrian) split conformal prediction supplies per-class prediction sets at
&alpha;&nbsp;=&nbsp;0.10. Every configuration is run with 10 random seeds (5 for cross-site), and strategies are compared
to random by a paired Wilcoxon signed-rank test over seeds with Holm correction within each pair.</p>
{figure("f1_loop", 1, "The loop that every run simulates. The selection rule decides both what the model learns next (upper path) and which patients get a laboratory answer rather than a model answer (lower path). Errors on the lower path are counted as they occur, not only at the end of the year.", wide=True)}
{figure("f2_data", 2, "Data and splits. Isolate counts are per species–antibiotic pair. The 2018 isolates of hospital A are used only for final evaluation; the development split used for the combination search of Section 6.7 never touches them.", wide=True)}
<div class="box"><b class="t">Experiments (2 859 runs in total)</b>
<b>E1</b> label efficiency: random, uncertainty, diversity, hybrid × budgets 40–800 (660 runs).<br>
<b>E2</b> pseudo-labelling added to each strategy (390).<br>
<b>E3</b> conformal routing as a selection rule (180).<br>
<b>E4</b> cross-site adoption at three hospitals (880).<br>
<b>E5</b> re-calibration of threshold and conformal bounds on freshly bought labels (239).<br>
<b>D1</b> pre-registered search over 16 method combinations on a development split (510).
</div>"""


def s5():
    return f"""<h2>5 Selection strategies</h2>
<p class="first">Let <i>p</i> be the model's probability of resistance for an arriving isolate and <i>t</i> the current
decision threshold. Each round, the rule picks <i>b</i>/4 isolates from that round's arrivals.</p>
<ul>
<li><b>Random</b> — uniform, the control.</li>
<li><b>Uncertainty</b> — smallest |<i>p</i>&nbsp;&minus;&nbsp;<i>t</i>|, i.e. the isolates whose call is closest to flipping
<span class="ref">[4]<span class="tier tA">A</span></span>.</li>
<li><b>Diversity</b> — greedy k-center in a 50-dimensional PCA space, maximising coverage of spectrum space
<span class="ref">[5]<span class="tier tA">A</span></span>.</li>
<li><b>Hybrid</b> — the 4<i>b</i> most uncertain isolates, then k-means into <i>b</i> clusters, one per cluster.</li>
<li><b>Conformal routing</b> — only isolates whose prediction set is ambiguous ({{S,&nbsp;R}} or empty), i.e. the ones the
model declines to call <span class="ref">[3]<span class="tier tA">A</span></span>. Reported both capped at <i>b</i> and
uncapped.</li>
<li><b>Bounds</b> — <i>no retraining</i> (budget 0) and <i>full retraining</i> (every arriving isolate labelled).</li>
</ul>
<p>The primary pre-planned endpoint was the number of labels needed to recover 95&nbsp;% of the AUROC gap between the two
bounds. Secondary endpoints, fixed before the runs, were AUROC against random and the operational error counts of
Section 3.</p>

<h2>6 Results</h2>
<h3>6.1 The premise holds: drift is real and retraining helps</h3>
<p class="first">A model frozen after 2016 loses ground on 2018 isolates that full retraining on the 2017 labels recovers:
+0.044, +0.046 and +0.051 AUROC for the three pairs (Fig. 3). The gap is modest but consistent across all seeds, and it is
the gap that every selection strategy is competing to close cheaply.</p>
{figure("f3_drift", 3, "Retraining recovers accuracy lost to drift. Bars are mean AUROC on 2018 isolates over 10 seeds; whiskers are 95&nbsp;% confidence intervals. Labels above the right bars give the gain over not retraining.", width="88%")}

<h3>6.2 No strategy beat random</h3>
<p class="first">Fig. 4 shows the learning curves and Fig. 5 the paired differences. Across 45 pre-planned comparisons
(3 pairs × 5 budgets × 3 strategies) <b>not one strategy was significantly better than random after Holm correction</b>.
The only significant results run the other way: uncertainty sampling was <i>worse</i> than random for
<i>K. pneumoniae</i> at 800 labels (&minus;0.029, Holm p&nbsp;=&nbsp;0.029) and for <i>S. aureus</i> at 800
(&minus;0.013, p&nbsp;=&nbsp;0.088 after correction, p&nbsp;=&nbsp;0.006 raw). The pre-planned primary endpoint was never
reached: no strategy recovered 95&nbsp;% of the retraining gap within 800 labels, and random itself recovered only
66–77&nbsp;% at that budget.</p>
{figure("f4_curves", 4, "Label-efficiency curves. Mean AUROC on 2018 over 10 seeds, shaded 95&nbsp;% confidence intervals, log-scaled budget. The dashed black line is full retraining (using 1 273–2 094 labels), the dotted grey line no retraining. All four selection rules sit inside each other's confidence bands at every budget.", wide=True)}
{figure("f5_forest", 5, "Paired differences against random, by pair and budget. Points are mean AUROC difference over 10 matched seeds with 95&nbsp;% confidence intervals; the shaded band marks a difference we pre-specified as negligible (±0.005). No interval excludes zero in a direction favouring the strategy after Holm correction.", wide=True)}
<table>
<caption><b>Table 1.</b> AUROC on 2018 isolates at the largest budget (800 labels), mean over 10 seeds, with the two
bounds. 95&nbsp;% confidence intervals are ≤&nbsp;0.014 throughout and are drawn in Figs. 4–5. Best active-learning
result per row in bold; no difference from random is statistically significant.</caption>
<tr><th style="width:21%">Pair</th><th class="n">No&nbsp;retr.</th><th class="n">Random</th><th class="n">Uncert.</th><th class="n">Divers.</th><th class="n">Hybrid</th><th class="n">Full&nbsp;retr.</th></tr>
<tr><td><i>E. coli</i>–CRO</td><td class="n">0.823</td><td class="n">0.852</td><td class="n">0.846</td><td class="n">0.854</td><td class="n"><b>0.863</b></td><td class="n">0.867</td></tr>
<tr><td><i>K. pneu.</i>–CRO</td><td class="n">0.742</td><td class="n">0.772</td><td class="n">0.743</td><td class="n"><b>0.779</b></td><td class="n">0.772</td><td class="n">0.788</td></tr>
<tr><td><i>S. aureus</i>–OXA</td><td class="n">0.799</td><td class="n">0.838</td><td class="n">0.825</td><td class="n">0.832</td><td class="n"><b>0.842</b></td><td class="n">0.850</td></tr>
</table>
<div class="box warn"><b class="t">Reading the negative result</b>
With 10 seeds the paired design detects an AUROC difference of about 0.008 at 80&nbsp;% power for these variances. We can
therefore exclude <i>large</i> gains from these strategies in this setting, not gains of any size. The practical reading
is that a laboratory choosing isolates at random gives up nothing measurable in model quality.</div>"""


def s6():
    return f"""<h3>6.3 Selection decides who gets hurt</h3>
<p class="first">The picture changes completely when the measurement moves from next year's model to this year's patients.
Because uncertainty sampling spends the budget exactly where the model's call is least trustworthy, the isolates it sends
to the laboratory are disproportionately the ones the model would have got wrong — and those isolates then receive a true
phenotype instead. Summed over the year, at 800 labels, uncertainty sampling reduced the resistant isolates wrongly
reported susceptible by 33&nbsp;%, 73&nbsp;% and 51&nbsp;% relative to random (Fig. 6; all p&nbsp;&lt;&nbsp;0.01, paired
Wilcoxon over seeds).</p>
<p>This benefit must be reported together with its cost on the opposite error, and here the species differ (Table 2):
major errors fell by 25&nbsp;% for <i>E. coli</i>, were unchanged for <i>S. aureus</i>, and rose by 54&nbsp;% for
<i>K. pneumoniae</i> — the pair where uncertainty sampling also produced the worst model. We therefore claim a reliable
reduction of the dangerous error and an organism-dependent effect on the other one, not a uniform improvement.</p>
{figure("f6_safety", 6, "Resistant isolates wrongly reported susceptible during the year, among isolates that were not sent to the laboratory. Bars are means over 10 seeds with 95&nbsp;% confidence intervals; hatched = random, solid = uncertainty. Labels give the relative change, with * marking p&nbsp;&lt;&nbsp;0.01 (paired Wilcoxon). At small budgets the strategies are indistinguishable; the gap opens as the budget grows.", wide=True)}
<table>
<caption><b>Table 2.</b> Both error types among untested isolates at 800 labels, summed over the year (mean over 10 seeds).
Green = fewer errors than random, red = more. p-values are paired Wilcoxon, uncorrected.</caption>
<tr><th style="width:20%">Pair</th><th class="n">VME rand.</th><th class="n">VME unc.</th><th class="n">&Delta;</th><th class="n">ME rand.</th><th class="n">ME unc.</th><th class="n">&Delta;</th></tr>
<tr><td><i>E. coli</i></td><td class="n">49.8</td><td class="n">33.6</td><td class="n hi">&minus;33%*</td><td class="n">347.8</td><td class="n">259.8</td><td class="n hi">&minus;25%*</td></tr>
<tr><td><i>K. pneumoniae</i></td><td class="n">19.4</td><td class="n">5.2</td><td class="n hi">&minus;73%*</td><td class="n">123.7</td><td class="n">190.1</td><td class="n lo">+54%*</td></tr>
<tr><td><i>S. aureus</i></td><td class="n">18.8</td><td class="n">9.2</td><td class="n hi">&minus;51%*</td><td class="n">134.6</td><td class="n">140.0</td><td class="n">+4% n.s.</td></tr>
</table>
<p class="small">* p&nbsp;&lt;&nbsp;0.01. VME = resistant called susceptible; ME = susceptible called resistant.</p>

<h3>6.4 The safety machinery breaks under drift</h3>
<p class="first">Both calibrated components failed, and neither failure is visible in AUROC. The decision threshold was
chosen on 2015–2016 validation isolates to catch 90&nbsp;% of resistant isolates; on 2018 isolates the same threshold
caught 80&nbsp;%, 73&nbsp;% and 79&nbsp;% (Fig. 7a). The conformal rule promises that at most 10&nbsp;% of resistant
isolates receive a confident "susceptible" set; measured over the 2017 isolates it delivered 15.5&nbsp;%, 18.9&nbsp;% and
14.3&nbsp;% (Fig. 7b).</p>
<p>This explains an otherwise puzzling result in E3: conformal routing matched random on AUROC while using fewer labels
(428–650 instead of 800), yet left <i>more</i> missed resistances than random at the same budget (78 vs 50, 33 vs 19 and
39 vs 19; Holm p&nbsp;&lt;&nbsp;0.01). A routing rule is only as good as the uncertainty estimate it routes on, and that
estimate had quietly expired.</p>
{figure("f7_calib", 7, "Two broken promises. (a) The decision threshold was set for 90&nbsp;% sensitivity to resistance on historical validation data; on 2018 isolates it delivers 0.10–0.18 less. (b) The class-conditional conformal rule promises at most 10&nbsp;% of resistant isolates receive a confident susceptible set; it delivers 14–19&nbsp;% over the 2017 isolates. Whiskers are 95&nbsp;% CIs over seeds.", wide=True)}

<h3>6.5 Re-calibration restores the promise and reveals its price</h3>
<p class="first">E5 keeps a quarter of the bought labels out of training and uses them, each round, to reset both the
threshold and the conformal bounds. Sensitivity on 2018 moves back towards the target (0.82→0.88, 0.64→0.77, 0.72→0.79,
averaged over strategies and budgets), but the major-error rate rises correspondingly (0.37→0.52, 0.27→0.49, 0.26→0.39),
and balanced accuracy falls (Fig. 8). AUROC is essentially unchanged, slightly lower because a quarter of the labels no
longer trains the model.</p>
<p>The right interpretation is not that re-calibration is harmful. It is that <b>the drifted threshold had silently moved
to a different operating point</b> — one that looked better on major errors only because it had stopped keeping its
sensitivity promise. Restoring the promise reveals what 90&nbsp;% sensitivity genuinely costs on a model with
AUROC&nbsp;0.75–0.85. A laboratory wanting both numbers to be acceptable needs a better model, not a better threshold.</p>
{figure("f8_recal", 8, "Re-calibrating moves each configuration up and to the right: closer to the sensitivity target, at the cost of more susceptible isolates called resistant. Arrows run from the stale calibration (E1, hollow) to re-calibration on freshly bought labels (E5, filled); marker shape is the species, colour the selection rule. Each point averages 10 seeds and three budgets.", width="78%")}

<h3>6.6 Moving the model to another hospital</h3>
<p class="first">Transfer is where the largest effects in the whole study appear, and they are not about selection.
A model trained at hospital A and applied unchanged elsewhere ranged from unaffected (<i>E. coli</i> at hospital B,
AUROC 0.835) to worse than chance (<i>K. pneumoniae</i> at hospital B, 0.477). Local labels repair most of the damage
quickly: 100 locally bought labels took that worst case from 0.477 to 0.614, which is the full-retraining value
(Fig. 9). Which isolates were bought again made no significant difference, in any of 120 comparisons — though the target
sites are small and this test has correspondingly little power.</p>
{figure("f9_site", 9, "Adopting the model at a new hospital. Hollow markers at zero are the transferred model with no local labels; lines show random local-label purchase. The <i>K. pneumoniae</i> collapse at hospital B (below chance) and its repair by 25–100 local labels is the strongest effect in the study.", wide=True)}"""


def s7():
    return f"""<h3>6.7 A pre-registered search over method combinations</h3>
<p class="first">A single negative result invites the objection that a cleverer combination would have worked. We
therefore decomposed the method into five slots — selection rule, split of the budget between targeted and random
purchase, retraining weights, calibration source, and use of unlabelled spectra — enumerated 2 430 combinations, removed
those that are incoherent or dominated (leaving 1 424 valid and 559 both robust and affordable), and selected 16 to run.
Among these was a family we expected to win: spend half the budget on targeted isolates and half at random, and use the
random half — an unbiased sample of the drifted distribution, scored before it enters training — to reset the threshold
and conformal bounds.</p>
<p>To keep the search honest, all 510 runs used a <b>development split that never touches 2018</b> (train on 2015–2016,
buy labels from the first half of the 2017 arrivals, test on the second half), and the rule for choosing winners was
written into the version-controlled log before any of them were executed. As a reproducibility check, 110 of the runs were
executed independently on two machines and returned bit-identical metrics.</p>
<p>The pre-registered rule selected a combination that reduced missed resistances by 63&nbsp;% and brought sensitivity to
0.92. <b>It achieved this by calling roughly two-thirds of susceptible isolates resistant.</b> Fig. 10 shows why: every
combination that re-calibrates slides along the same error trade-off rather than improving it, and our pre-registered rule
had scored only one end of that trade-off. We report this as a failure of our own decision rule, not as a method result.</p>
<p>Judged on both error types at once, only one family lies strictly inside the baseline on both axes: <b>uncertainty
sampling</b>, alone (ratio 0.87 on missed resistances, p&nbsp;=&nbsp;0.017; 0.84 on major errors, p&nbsp;=&nbsp;0.002;
AUROC +0.002) or mixed half-and-half with random (0.95, p&nbsp;=&nbsp;0.16; 0.89, p&nbsp;=&nbsp;0.006; AUROC
&minus;0.001). No combination of re-calibration, recency weighting, importance weighting, drift-novelty selection or
conformal pseudo-labelling improved on it. Mean AUROC across all 16 combinations spanned 0.815–0.839, i.e. the model
quality was flat no matter what we did.</p>
{figure("f10_tradeoff", 10, "The error trade-off on the development split; each point is one of 16 method combinations, averaged over 3 pairs × 2 budgets × 5 seeds. Only points in the shaded quadrant beat the random baseline (D01) on both error types. The combination chosen by our pre-registered rule (D14) sits far to the right: it buys its low missed-resistance rate by calling most susceptible isolates resistant.", width="86%")}

<h3>6.8 A question we cannot answer: pseudo-labelling</h3>
<p class="first">E2 added self-training: isolates the model was confident about were given pseudo-labels (p&nbsp;≤&nbsp;0.05
treated as susceptible, p&nbsp;≥&nbsp;0.95 as resistant) and added to the training set. The results were poor — pseudo-labels
alone fell below no retraining at all, and major errors rose sharply at small budgets.</p>
<p>They are also uninterpretable, because of an error in our own design. The decision threshold for these models is
0.010–0.030, i.e. <b>below the pseudo-susceptible cut-off of 0.05</b>. Isolates in that band were labelled susceptible for
training while the deployed model was simultaneously calling them resistant (Fig. 11). The procedure therefore injected
systematically contradictory labels: 62–66&nbsp;% of each round's arrivals were pseudo-labelled, at 89–92&nbsp;% accuracy,
i.e. 60–240 wrong labels per run. We report the experiment as invalid and leave the semi-supervised question open rather
than publish a negative result that our own implementation caused. A corrected design ties the cut-offs to the threshold —
or, better, derives them from re-calibrated conformal sets.</p>
{figure("f11_pseudo", 11, "Why the pseudo-labelling experiment is not a fair test. (a) Most arrivals received a pseudo-label, roughly one in ten of them wrong. (b) The fixed cut-off p&nbsp;≤&nbsp;0.05 for “susceptible” lies above the deployed decision threshold t for all three pairs, so every isolate in the shaded band was trained on as susceptible while being reported as resistant.", wide=True)}"""


S8 = """<h2>7 Discussion</h2>
<h3>Label efficiency is the wrong objective here</h3>
<p class="first">Active learning is usually evaluated by how few labels are needed to reach a target accuracy. On this task
that number is dominated by factors the selection rule does not control: the signal available in a 6 000-bin spectrum, the
size of the resistant class, and the amount of drift between years. Our strategies moved it by less than the seed-to-seed
noise. Meanwhile the same choice moved the count of patients who received a wrong susceptible report by up to a factor of
four. For a clinical deployment the second quantity is the one worth optimising, and it is invisible to the standard
evaluation.</p>
<h3>Calibration is not a one-off step</h3>
<p class="first">Both of our calibrated components were fitted once and then trusted for two years, which is exactly what
a deployed system does by default. Both failed quietly: the threshold lost 10–18 points of sensitivity, and the conformal
rule exceeded its own error budget by a factor of 1.4–1.9, while AUROC — the number that would be monitored — barely moved.
Any deployment of this kind of model needs a stream of freshly phenotyped isolates reserved for calibration, and our
results suggest a cheap way to obtain one: a random share of the testing budget is an unbiased sample of the current
distribution and can be scored before it enters training.</p>
<h3>Practical recommendation</h3>
<div class="box key"><b class="t">What we would tell a laboratory</b>
<b>1.</b> Choose isolates for retraining however is operationally easiest; random is not worse.<br>
<b>2.</b> If the budget allows, bias the choice towards isolates the model is unsure about — not for the model, but because
those are the isolates whose wrong calls would otherwise reach patients. Expect the effect on over-calling to vary by
organism and measure it.<br>
<b>3.</b> Re-calibrate the threshold and any uncertainty sets on recent labels, and treat a drifting sensitivity as an alarm.<br>
<b>4.</b> When adopting a model from another hospital, buy 25–100 local labels first. This is the single highest-value
intervention we measured.</div>

<h2>8 Limitations</h2>
<ul>
<li><b>No acquisition dates.</b> DRIAMS does not provide them, so within-year arrival order is simulated by a hash-based
partition. Seasonal and outbreak structure is therefore absent, and the within-year drift that would most favour adaptive
selection cannot be tested here. This is the limitation we would most like to remove.</li>
<li><b>Three pairs, four hospitals, one dataset.</b> The organisms with enough labelled isolates for this design are few,
and all data come from one country and one study.</li>
<li><b>Simulation, not deployment.</b> Labels are revealed from an existing database rather than produced by a laboratory,
so turnaround time, batch effects of real re-testing and clinician response are out of scope.</li>
<li><b>Power.</b> Ten seeds support detection of AUROC differences around 0.008; the cross-site tests, with five seeds and
small target sites, are weaker still. Absence of evidence here is not strong evidence of absence for small effects.</li>
<li><b>One classifier family.</b> All results use tuned gradient-boosted trees; a representation with better-behaved
uncertainty could change the ranking of selection rules.</li>
<li><b>The semi-supervised question is open</b>, by our own admission (Section 6.8).</li>
</ul>

<h2>9 Conclusion</h2>
<p class="first">Across 2 859 retraining simulations on DRIAMS, no active-learning strategy produced a better resistance
model than buying labels at random, and the standard label-efficiency endpoint was never reached. The same experiments
show that the choice is far from irrelevant: sending the uncertain isolates to the laboratory cut the resistant isolates
wrongly reported susceptible by a third to three-quarters, and the decision threshold and conformal guarantees that were
supposed to bound such errors had both quietly expired under two years of drift. A pre-registered search over 16 method
combinations, run on a development split that never touched the test year, reproduced these conclusions and — by selecting
a combination that merely traded one error for another — illustrated how easily a safety metric read in isolation can
mislead. We recommend that selection policies for this task be reported with deployment-time error counts of both types,
and that calibration be treated as a maintained component rather than a property of the training run.</p>
<p><b>Reproducibility.</b> All experiments are driven by a single configuration file; each run writes a self-describing
record with its seed, data fingerprint, library versions and per-round metrics. 110 runs were executed independently on
two machines and returned identical metrics. Code and result records will be released on publication.</p>"""


REFS = """<h2>References</h2>
<div class="ref"><ol>
<li>Weis, C., Cuénod, A., Rieck, B., <i>et al.</i> Direct antimicrobial resistance prediction from clinical MALDI-TOF mass
spectra using machine learning. <i>Nature Medicine</i> <b>28</b>, 164–174 (2022).<span class="tier tA">A</span></li>
<li>Settles, B. Active learning literature survey. Technical Report 1648, University of Wisconsin–Madison (2009).<span class="tier tC">C</span></li>
<li>Corvelo Benz, N., Miranda, J., Chen, Z., Sattler, A., Borgwardt, K. Detecting antimicrobial resistance through MALDI-TOF
mass spectrometry with statistical guarantees using conformal prediction. In <i>RECOMB 2025</i>, LNCS, Springer.<span class="tier tA">A</span></li>
<li>Lewis, D. D., Gale, W. A. A sequential algorithm for training text classifiers. In <i>SIGIR 1994</i>, 3–12.<span class="tier tA">A</span></li>
<li>Sener, O., Savarese, S. Active learning for convolutional neural networks: a core-set approach. In <i>ICLR 2018</i>.<span class="tier tA">A</span></li>
<li>Beygelzimer, A., Dasgupta, S., Langford, J. Importance weighted active learning. In <i>ICML 2009</i>, 49–56.<span class="tier tA">A</span></li>
<li>Hsu, W.-N., Lin, H.-T. Active learning by learning. In <i>AAAI 2015</i>, 2659–2665.<span class="tier tA">A</span></li>
<li>Krishnamurthy, A., Agarwal, A., Huang, T.-K., Daumé III, H., Langford, J. Active learning for cost-sensitive
classification. In <i>ICML 2017</i>, 1915–1924.<span class="tier tA">A</span></li>
<li>Lu, P.-Y., Li, C.-L., Lin, H.-T. A more robust baseline for active learning by injecting randomness to uncertainty
sampling. <i>ICML 2023 Workshop on AI &amp; HCI</i>.<span class="tier tB">B</span></li>
<li>Chen, Y., Ding, Z., Wagner, D. Continuous learning for Android malware detection. In <i>USENIX Security 2023</i>.<span class="tier tA">A</span></li>
<li>Barbero, F., Pendlebury, F., Pierazzi, F., Cavallaro, L. Transcending Transcend: revisiting malware classification in the
presence of concept drift. In <i>IEEE S&amp;P 2022</i>, 805–823.<span class="tier tA">A</span></li>
<li>Chen, J., Yoon, J., Ebrahimi, S., Arik, S. Ö., Pfister, T., Jha, S. ASPEST: bridging the gap between active learning and
selective prediction. <i>Transactions on Machine Learning Research</i> (2024).<span class="tier tA">A</span></li>
<li>Tibshirani, R. J., Barber, R. F., Candès, E. J., Ramdas, A. Conformal prediction under covariate shift. In
<i>NeurIPS 2019</i>, 2530–2540.<span class="tier tA">A</span></li>
<li>Gibbs, I., Candès, E. J. Adaptive conformal inference under distribution shift. In <i>NeurIPS 2021</i>, 1660–1672.<span class="tier tA">A</span></li>
<li>ISO 20776-2:2021. Susceptibility testing of infectious agents — Part 2: Evaluation of performance of antimicrobial
susceptibility test devices. International Organization for Standardization.<span class="tier tA">A</span></li>
<li>Chen, T., Guestrin, C. XGBoost: a scalable tree boosting system. In <i>KDD 2016</i>, 785–794.<span class="tier tA">A</span></li>
<li>Vovk, V., Gammerman, A., Shafer, G. <i>Algorithmic Learning in a Random World</i>. Springer (2005).<span class="tier tA">A</span></li>
<li>Holm, S. A simple sequentially rejective multiple test procedure. <i>Scandinavian Journal of Statistics</i> <b>6</b>,
65–70 (1979).<span class="tier tA">A</span></li>
</ol>
<p class="small"><b>Evidence tiers.</b> <span class="tier tA">A</span> peer-reviewed venue or standard, verified ·
<span class="tier tB">B</span> peer-reviewed workshop · <span class="tier tC">C</span> technical report / preprint.
Tiers are shown because two claims in Section 2 rest on non-archival sources.</p></div>"""


def build():
    body = "\n".join([ABSTRACT, S1, S2, S3, s4(), s5(), s6(), s7(), S8, REFS])
    parts, out = body.split("@@WIDE@@"), []
    out.append('<div class="cols">' + parts[0] + "</div>")
    for seg in parts[1:]:
        figpart, rest = seg.split("@@/WIDE@@", 1)
        out.append('<div class="wideblock">' + figpart + "</div>")
        out.append('<div class="cols">' + rest + "</div>")
    html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>Which isolates should the laboratory test?</title><style>{CSS}</style></head><body>
{head()}
{"".join(out)}
</body></html>"""
    open(S + "paper.html", "w").write(html)
    print("wrote paper.html", len(html) // 1024, "KB")


if __name__ == "__main__":
    build()
