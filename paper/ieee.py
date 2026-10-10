# Six page conference version, IEEE two column format. Writes ieee.html (-> PDF via Chrome).
import os

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, "ifig") + "/"
S = os.environ.get("IEEE_OUT", HERE) + "/"

# IEEE conference layout: US Letter, 0.625 in side margins, two 3.5 in columns with a
# 0.25 in gutter, 10 pt Times body, 8 pt captions and references.
CSS = """
@page { size: Letter; margin: 0.75in 0.625in 0.9in 0.625in; }
* { box-sizing: border-box; }
body { font-family:"Times New Roman",Times,serif; font-size:9.6pt; line-height:1.14; color:#000;
       background:#fff; margin:0; text-align:justify; hyphens:none; -webkit-hyphens:none;
       column-count:2; column-gap:0.25in; }
.span { column-span:all; }
.ttl { text-align:center; font-size:20pt; line-height:1.15; margin:0 0 9pt; font-weight:400; }
.au { text-align:center; font-size:10.5pt; line-height:1.3; margin:0 0 2pt; }
.af { text-align:center; font-size:9pt; line-height:1.3; margin:0; font-style:italic; }
.em { text-align:center; font-size:9pt; line-height:1.3; margin:0 0 11pt; }
h2 { font-size:9.6pt; font-weight:400; font-variant:small-caps; text-align:center;
     margin:9pt 0 3pt; break-after:avoid; letter-spacing:0.02em; }
h3 { font-size:9.6pt; font-weight:400; font-style:italic; text-align:left;
     margin:6pt 0 1pt; break-after:avoid; }
p { margin:0; text-indent:0.17in; }
p.ni { text-indent:0; }
.abs { font-size:9pt; text-indent:0.17in; margin:0 0 5pt; }
.abs b, .idx b { font-style:italic; font-weight:700; }
.idx { font-size:9pt; text-indent:0.17in; margin:0 0 4pt; }
figure { margin:7pt 0 7pt; break-inside:avoid; }
figure.w { column-span:all; margin:4pt 0 9pt; }
figure img, figure .art { display:block; width:100%; }
figcaption { font-size:8pt; line-height:1.22; margin-top:3.5pt; text-align:justify; text-indent:0; }
table { border-collapse:collapse; width:100%; font-size:7.9pt; margin:0 0 2pt; }
table.w { }
.tw { column-span:all; margin:4pt 0 9pt; break-inside:avoid; }
.tbl { margin:7pt 0 7pt; break-inside:avoid; }
.tn { text-align:center; font-size:8pt; font-variant:small-caps; margin:0; letter-spacing:0.02em; }
.tc { text-align:center; font-size:8pt; line-height:1.2; margin:0 0 3pt; text-indent:0; }
table th { font-weight:400; font-style:italic; text-align:left; padding:1.4pt 3pt 1.4pt 0;
           border-bottom:0.5px solid #000; vertical-align:bottom; }
table td { padding:1.1pt 3pt 1.1pt 0; vertical-align:top; }
table .n { text-align:right; white-space:nowrap; padding-left:4pt; }
table .c { text-align:center; white-space:nowrap; padding-left:5pt; padding-right:2pt; }
table td:first-child, table th:first-child { padding-right:6pt; }
table.top { border-top:1px solid #000; }
table.bot tr:last-child td { border-bottom:1px solid #000; }
tr.r td { border-top:0.4px solid #999; }
.refs { font-size:8pt; line-height:1.2; }
.refs ol { margin:0; padding-left:11pt; }
.refs li { margin:0.9pt 0; text-align:justify; }
em, i { font-style:italic; }
sup { font-size:7pt; vertical-align:super; line-height:0; }
.fn { font-size:7.6pt; line-height:1.2; margin:5pt 0 0; text-indent:0; border-top:0.4px solid #000;
      padding-top:2.5pt; }
"""


def svg(name):
    return open(FIG + name + ".svg").read()


def fig(name, num, cap, wide=False):
    return (f'<figure class="{"w" if wide else ""}"><div class="art">{svg(name)}</div>'
            f'<figcaption>Fig. {num}. {cap}</figcaption></figure>')


def table(num, cap, body, wide=False):
    return (f'<div class="{"tw" if wide else "tbl"}"><p class="tn">Table {num}</p>'
            f'<p class="tc">{cap}</p>{body}</div>')


# ----------------------------------------------------------------- front matter
FRONT = """<div class="span">
<p class="ttl">Cost and Safety of Label Acquisition Strategies for<br>
MALDI-TOF Antimicrobial Resistance Prediction</p>
<p class="au">Dyen Asif, Hira Mastoor, Maryam Shahbaz</p>
<p class="af">Department of Computer Science, National University of Computer and Emerging Sciences, Islamabad, Pakistan</p>
<p class="em">i240608@isb.nu.edu.pk, hira.mastoor@nu.edu.pk, maryam.shahbaz@nu.edu.pk</p>
</div>

<p class="abs"><b>Abstract</b>&mdash;Machine learning (ML) applied to matrix-assisted laser desorption
ionization time-of-flight (MALDI-TOF) mass spectra can predict antimicrobial resistance (AMR) in hours
rather than days. A deployed model decays as the local bacterial population changes, so it has to be
retrained, and every training label is a laboratory antimicrobial susceptibility test (AST) that someone
pays for. Active learning (AL) is the usual answer to that problem. A 2026 systematic review of 115 ML
studies on clinical MALDI-TOF spectra reports none that treat label acquisition as a cost. We ran 1540
retraining simulations on the Database of Resistance Information on Antimicrobials and MALDI-TOF
Mass Spectra (DRIAMS) over three species and antibiotic pairs, four hospitals,
five budgets and ten seeds, using a temporal protocol in which a model trained on 2015 and 2016 buys
labels during 2017 and is tested on 2018. Across 165 paired comparisons, no uncertainty, diversity or
hybrid rule beat random selection after correction for multiple testing, and two were worse. The reason
is that little accuracy is available to compete for: the area under the receiver operating characteristic
curve (AUROC) between never retraining and retraining on every isolate spans only 0.044 to 0.051. The
budget buys cost rather than accuracy. Four hundred tests, which is 19 to 31 percent of a year of
isolates, recover 50 to 77 percent of that gain. Uncertainty sampling is the weakest rule by AUROC but
cuts resistant isolates that go untested and are reported susceptible by 33 to 73 percent. An analysis using SHapley
Additive exPlanations (SHAP) for trees indicates why the rules tie, since models trained under different rules rely on the same small
set of spectral bins.</p>

<p class="idx"><b>Index Terms</b>&mdash;antimicrobial resistance, active learning, MALDI-TOF mass
spectrometry, model maintenance, explainable machine learning.</p>
"""

# ----------------------------------------------------------------- 1 introduction
S1 = """<h2>I.&nbsp;&nbsp;Introduction</h2>
<p class="ni">Antimicrobial resistance is among the largest threats to public health, and an estimated
1.27 million deaths were attributable to bacterial AMR in 2019 [1]. Treatment depends on knowing which
drugs still work, which in routine practice means culture based AST. That takes up to 72 hours. MALDI-TOF
mass spectrometry is already present in most clinical microbiology laboratories for species
identification, and the same spectrum acquired for that purpose can be reused to predict resistance with
ML, which reduces the delay from days to hours [2], [3].</p>

<p>Such a model does not stay accurate on its own. The population of isolates in a hospital changes, the
instrument is serviced or replaced, and the resistance mechanisms in circulation shift. In our own data a
model trained on isolates from 2015 and 2016 reaches an AUROC of 0.881 under cross validation inside those
years for <i>Escherichia coli</i> with ceftriaxone, but only 0.824 when it is applied to isolates from
2018. Keeping the model useful therefore requires periodic retraining, and retraining requires labels.
A label here is not an annotation that a person can supply in a few seconds. It is a susceptibility test
with reagent and technician costs, and a laboratory that is willing to fund only a few hundred extra tests
in a year has to decide which isolates receive them.</p>

<p>This is the setting that AL was designed for [4]. The model ranks the isolates that arrive and asks for
labels only where they are expected to be most informative, usually near the decision boundary or spread
across the feature space. AL is well studied in medical imaging and in text, and it is routinely reported
to reach a target accuracy with a fraction of the labels. Whether it does so for MALDI-TOF resistance
prediction has not been established. A systematic review published in 2026, covering 115 studies that
apply ML to clinical MALDI-TOF spectra, groups the field by task, preprocessing, model family and
evaluation, and does not identify a single study in which label acquisition cost is a variable [5].
Prior work on this modality either assumes that all labels are already present or evaluates a fixed
training set.</p>

<p>We examine that gap directly. The experiments use the Database of Resistance Information on Antimicrobials
and MALDI-TOF Mass Spectra (DRIAMS), a public collection of clinical MALDI-TOF spectra with matched susceptibility results from four Swiss hospitals, released under a CC0 public domain
waiver and available from Dryad at doi:10.5061/dryad.bzkh1899q. The protocol is temporal rather than a random split. A model
is trained on isolates from 2015 and 2016, isolates arriving during 2017 are offered to an acquisition
rule in four quarterly rounds under a fixed budget, and the maintained model is evaluated on isolates
from 2018. This mirrors how a laboratory would actually operate the system, and it keeps the test year
strictly after every label that was bought.</p>

<p>The contributions of this paper are as follows. We provide the first evaluation of label acquisition
cost for MALDI-TOF resistance prediction, covering three species and antibiotic pairs, four hospitals and
five budgets, with ten seeds per configuration. We report a negative result that holds across 165 paired
comparisons, namely that no acquisition rule outperforms random selection, and we explain it by measuring
how little accuracy retraining makes available in the first place. We reframe the useful quantity as
cost, and quantify how much of the benefit of retraining a partial test budget recovers. We separate
model quality next year from patient exposure this year, and show that the two disagree about which rule
is best. Finally, we use TreeSHAP to show that models trained under different acquisition rules rely on
the same spectral regions, which accounts for the absence of a difference between them.</p>
"""

# ----------------------------------------------------------------- 2 related work
T1 = """<table class="top bot">
<thead><tr><th>Study</th><th>Task and data</th><th class="c">Sites</th>
<th class="c">Temp.</th><th class="c">Cost</th><th class="c">Errors</th><th class="c">XAI</th></tr></thead>
<tbody>
<tr><td>Weis <i>et al.</i> [2]</td><td>AMR from MALDI-TOF, DRIAMS</td><td class="c">4</td>
    <td class="c">no</td><td class="c">no</td><td class="c">no</td><td class="c">no</td></tr>
<tr><td>Weis <i>et al.</i> [6]</td><td>Topological and kernel methods</td><td class="c">1</td>
    <td class="c">no</td><td class="c">no</td><td class="c">no</td><td class="c">no</td></tr>
<tr><td>Duroux <i>et al.</i> [7]</td><td>Generalisation to unseen sites</td><td class="c">4</td>
    <td class="c">yes</td><td class="c">no</td><td class="c">no</td><td class="c">no</td></tr>
<tr><td>Corvelo Benz <i>et al.</i> [8]</td><td>Conformal guarantees, DRIAMS</td><td class="c">4</td>
    <td class="c">no</td><td class="c">no</td><td class="c">partly</td><td class="c">no</td></tr>
<tr><td>Schmidt-Santiago <i>et al.</i> [5]</td><td>Review of 115 MALDI-TOF ML studies</td>
    <td class="n">n/a</td><td class="c">rare</td><td class="c">none</td><td class="c">rare</td><td class="c">21/115</td></tr>
<tr><td>Chen <i>et al.</i> [9]</td><td>AL with selective prediction, images</td><td class="c">n/a</td>
    <td class="c">no</td><td class="c">yes</td><td class="c">no</td><td class="c">no</td></tr>
<tr><td>Chen <i>et al.</i> [10]</td><td>Continuous learning, malware</td><td class="c">n/a</td>
    <td class="c">yes</td><td class="c">yes</td><td class="c">no</td><td class="c">no</td></tr>
<tr class="r"><td>This work</td><td>AL for AMR from MALDI-TOF, DRIAMS</td><td class="c">4</td>
    <td class="c">yes</td><td class="c">yes</td><td class="c">yes</td><td class="c">yes</td></tr>
</tbody></table>"""

S2 = """<h2>II.&nbsp;&nbsp;Related Work</h2>
<p class="ni">Resistance prediction from MALDI-TOF spectra became a practical proposition with the release
of DRIAMS, which pairs more than 300000 routine spectra with susceptibility results and established that
gradient boosted trees and shallow networks reach clinically interesting discrimination on several
species and antibiotic combinations [2]. Later work improved the representation with topological and
kernel methods [6], extended prediction to several antibiotics at once, and added statistical guarantees
through conformal prediction [8]. The systematic review of Schmidt-Santiago <i>et al.</i> covers 115
studies in this area and reports that SHAP values are used for interpretation
in 21 of them, so model explanation is established practice on this modality, while temporal evaluation
remains uncommon [5]. Generalisation across hospitals has been studied directly, and performance drops
sharply when a model is moved to a site it was not trained on [7].</p>

<p>Active learning has a long history. Uncertainty sampling selects the instances closest to the decision
boundary [11], core set and diversity methods instead cover the input space [12], and importance weighted
and cost sensitive variants correct the bias that selective querying introduces [13], [14]. Hybrid rules
combine the two signals [15]. The literature is not uniformly positive. Random selection is a stronger
baseline than it is often given credit for, and injecting randomness into uncertainty sampling has been
reported to improve its robustness [16]. In security, where models are retrained continuously against a
moving target, label acquisition under budget has been studied in its own right [10], [17], and work
bridging AL and selective prediction shows that the two interact [9]. These settings resemble ours in
that labels are expensive and the data distribution moves, but none of them involves mass spectra or
susceptibility testing.</p>

<p>Table I places the present study against this background. Prior work on MALDI-TOF resistance
prediction has not treated the acquisition of labels as a cost, has largely not used temporal splits,
and has rarely reported the two clinical error types separately. Work on AL under budget has not been
applied to this modality. The combination of a temporal protocol, an explicit test budget, both error
types, and an explanation of why the acquisition rules behave as they do is what this paper
contributes.</p>
"""


# ----------------------------------------------------------------- 3 method
def S3():
    return """<h2>III.&nbsp;&nbsp;Method</h2>
<h3>A. Problem setting</h3>
<p class="ni">Let a spectrum be a vector <i>x</i> of 6000 binned intensities and let <i>y</i> be 1 if the
isolate is resistant or intermediate to the antibiotic of interest and 0 if it is susceptible. A model
<i>f</i> is trained on the isolates available at the start of the period and outputs an estimated
probability of resistance. A threshold <i>t</i> turns that probability into a report: resistant when
<i>f</i>(<i>x</i>) is at least <i>t</i>, susceptible otherwise.</p>

<p>Isolates then arrive over a year in four batches. In each round the model scores every arriving
isolate, an acquisition rule selects <i>B</i>/4 of them for laboratory testing, where <i>B</i> is the
budget for the whole year, and the true labels of those isolates are revealed and added to the training
set. The model and the threshold are refitted. Isolates that were not selected are reported using the
model's own output, which is the operational situation that matters clinically, because those reports
reach clinicians without a confirmatory test. Fig. 1 shows the whole procedure.</p>

""" + fig("f1_pipeline", 1,
          "Study pipeline. A classifier is trained on isolates from 2015 and 2016 and a decision "
          "threshold is fixed on held out data. Isolates arriving in 2017 are scored in four quarterly "
          "rounds. In each round the acquisition rule buys susceptibility tests for a quarter of the "
          "budget; those isolates return a true label and join the training set, while the remaining "
          "isolates are reported using the model's own call and contribute to the error counts. The "
          "maintained model is evaluated on isolates from 2018.", wide=True) + """

<h3>B. Acquisition rules</h3>
<p class="ni">Four rules are compared. Random selection draws uniformly from the isolates that arrived in
the round and serves as the baseline. Uncertainty sampling takes the isolates whose predicted probability
is closest to the threshold <i>t</i>, measured as the absolute difference between the two. Diversity
sampling applies a <i>k</i>-center greedy procedure in the spectral space so that the selected isolates
are spread out rather than clustered. The hybrid rule splits the round budget evenly between the
uncertainty and diversity criteria. Two bounds frame all of these. The lower bound never retrains at all,
and the upper bound retrains on every isolate that arrived, which is what a laboratory would obtain if it
tested everything.</p>

<h3>C. Error types and reported quantities</h3>
<p class="ni">Clinical microbiology distinguishes two kinds of mistake, and they are not interchangeable.
A very major error (VME) is a resistant isolate reported as susceptible, which can send a patient home on
a drug that will not work. A major error (ME) is a susceptible isolate reported as resistant, which
wastes a broader spectrum agent and contributes to selection pressure. The definitions follow the International Organization
for Standardization (ISO) standard 20776-2 [18]. Both are reported throughout, because a rule that lowers one while raising the other has
not improved anything.</p>

<p>We separate two views that are often conflated. The predictive view is the usual one, namely how well
next year's model discriminates, which we measure as AUROC on the 2018 isolates. The operational view
counts what happened during the pool year itself: among the isolates that were not selected for testing,
how many were resistant and were nonetheless reported susceptible. These are counts of patients affected,
not rates, and the two views do not have to agree.</p>

<h3>D. Explaining the fitted models</h3>
<p class="ni">To understand why the rules behave similarly we compute SHAP values [19], which distribute a
single prediction across the input features in the unique way that satisfies local accuracy, missingness
and consistency. For tree ensembles these values have an exact polynomial time solution, so no
sampling approximation is involved. We use the TreeSHAP implementation inside the gradient boosting
library itself, which removes any possibility of a mismatch between the explained model and the deployed
one. Six models are explained per pair: the two bounds, and random and uncertainty acquisition at budgets
of 400 and 800. All six are explained on the same 2018 isolates, so any difference is a difference between
models rather than between evaluation sets. Two models are then compared by the overlap of their twenty
most used bins and by the rank correlation over all 6000 bins. Importance of a bin is its mean absolute
SHAP value. Its direction is obtained by splitting the isolates at the median intensity of that bin and
taking the difference in mean SHAP between the halves, because averaging signed values over all isolates
simply follows the majority class, which here is susceptible.</p>
"""


# ----------------------------------------------------------------- 4 setup
def S4():
    return """<h2>IV.&nbsp;&nbsp;Experimental Setup</h2>
<h3>A. Data and splits</h3>
<p class="ni">DRIAMS provides spectra preprocessed to 6000 bins of 3 daltons each, spanning 2000 to 20000
daltons. Labels follow the convention of the original release, in which resistant and intermediate are
coded together as 1. We study three species and antibiotic pairs that have enough labelled isolates for a
temporal analysis: <i>E. coli</i> with ceftriaxone, <i>Klebsiella pneumoniae</i> with ceftriaxone, and
<i>Staphylococcus aureus</i> with oxacillin. At the primary site these give 1481, 812 and 1141 training
isolates from 2015 and 2016, pools of 2094, 1273 and 1445 isolates arriving in 2017, and test sets of
1386, 775 and 1204 isolates from 2018, with resistance prevalence in the test year of 18.5, 13.9 and 14.6
percent. The released spectra carry no acquisition dates, so the four arrival batches are formed by a
deterministic hash of the isolate code rather than by calendar quarter. The cross-site experiment moves a
model trained at the primary site to each of the other three hospitals.</p>

<h3>B. Model, protocol and statistics</h3>
<p class="ni">The classifier is a gradient boosted tree ensemble [20], tuned once on the 2015 and 2016
data only and then held fixed, so that no information from the pool or test years enters the
configuration. Twenty percent of the training years is held out to set the threshold <i>t</i> at the
lowest value achieving 90 percent sensitivity to resistance, which reflects the clinical preference for
avoiding very major errors. Budgets of 40, 100, 200, 400 and 800 labels are spread evenly over the four
rounds. Every configuration is repeated with ten random seeds, and the cross-site configurations with
five, giving 1540 retraining simulations in total.</p>

<p>Strategies are compared with random selection on matched seeds using the Wilcoxon signed rank test,
and the resulting p values are corrected across the whole family of comparisons with the Holm procedure
[21]. We report the corrected values only. The DRIAMS release used here is archived at doi:10.5061/dryad.bzkh1899q, and our code, the per
isolate acquisition log and the per run result records are released with the paper.</p>
"""


# ----------------------------------------------------------------- 5 results
T2 = """<table class="top bot">
<thead><tr><th>Pair</th><th class="n">Tests<br>bought</th><th class="n">Of pool</th>
<th class="n">Tests<br>saved</th><th class="n">Random</th><th class="n">Uncert.</th>
<th class="n">Divers.</th><th class="n">Hybrid</th></tr></thead>
<tbody>
<tr><td><i>E. coli</i></td><td class="n">400</td><td class="n">2094</td><td class="n">80.9%</td>
    <td class="n">0.50</td><td class="n">0.43</td><td class="n">0.54</td><td class="n">0.38</td></tr>
<tr><td></td><td class="n">800</td><td class="n">2094</td><td class="n">61.8%</td>
    <td class="n">0.66</td><td class="n">0.52</td><td class="n">0.70</td><td class="n">0.90</td></tr>
<tr class="r"><td><i>K. pneumoniae</i></td><td class="n">400</td><td class="n">1273</td>
    <td class="n">68.6%</td><td class="n">0.77</td><td class="n">0.28</td><td class="n">0.65</td>
    <td class="n">0.60</td></tr>
<tr><td></td><td class="n">800</td><td class="n">1273</td><td class="n">37.2%</td>
    <td class="n">0.66</td><td class="n">0.02</td><td class="n">0.82</td><td class="n">0.67</td></tr>
<tr class="r"><td><i>S. aureus</i></td><td class="n">400</td><td class="n">1445</td>
    <td class="n">72.3%</td><td class="n">0.60</td><td class="n">0.38</td><td class="n">0.41</td>
    <td class="n">0.57</td></tr>
<tr><td></td><td class="n">800</td><td class="n">1445</td><td class="n">44.6%</td>
    <td class="n">0.77</td><td class="n">0.52</td><td class="n">0.65</td><td class="n">0.85</td></tr>
</tbody></table>"""

T3 = """<table class="top bot">
<thead><tr><th>Models compared</th><th class="n"><i>E. coli</i></th>
<th class="n"><i>K. pneu.</i></th><th class="n"><i>S. aureus</i></th></tr></thead>
<tbody>
<tr><td>Random 400 vs uncertainty 400</td><td class="n">0.60</td><td class="n">0.38</td>
    <td class="n">0.54</td></tr>
<tr><td>Random 800 vs uncertainty 800</td><td class="n">0.60</td><td class="n">0.29</td>
    <td class="n">0.43</td></tr>
<tr class="r"><td>Random 800 vs retrain on all</td><td class="n">0.67</td><td class="n">0.38</td>
    <td class="n">0.60</td></tr>
<tr><td>Uncertainty 800 vs retrain on all</td><td class="n">0.60</td><td class="n">0.38</td>
    <td class="n">0.43</td></tr>
<tr class="r"><td>No retraining vs retrain on all</td><td class="n">0.43</td><td class="n">0.11</td>
    <td class="n">0.29</td></tr>
<tr><td>Mean over all fifteen model pairs</td><td class="n">0.60</td><td class="n">0.31</td>
    <td class="n">0.49</td></tr>
</tbody></table>"""


def S5():
    return """<h2>V.&nbsp;&nbsp;Results</h2>
<h3>A. Retraining is necessary but its total benefit is small</h3>
<p class="ni">Two bounds define the space in which any acquisition rule has to operate. A model that is
never retrained reaches an AUROC on the 2018 isolates of 0.823, 0.742 and 0.799 for the three pairs. A
model retrained on every isolate that arrived in 2017 reaches 0.867, 0.788 and 0.850. Retraining
therefore helps, and the direction of the effect is consistent across all three pairs, which confirms
the premise of the study. However, the size of the effect is modest. The difference between the two
bounds is 0.044, 0.046 and 0.051 of AUROC. Every acquisition rule competes inside a window of about five
points, and the standard error over ten seeds is of a similar order at the smaller budgets.</p>

""" + fig("f2_curves", 2,
          "Test AUROC on 2018 isolates against the number of susceptibility tests bought during 2017, "
          "for each species and antibiotic pair. Points are means over ten seeds and bars are standard "
          "errors. The upper dashed line is retraining on every arriving isolate and the lower dotted "
          "line is never retraining. All four rules lie inside a narrow band and their intervals overlap "
          "at almost every budget.", wide=True) + """

<h3>B. No acquisition rule outperforms random selection</h3>
<p class="ni">Fig. 2 shows the label efficiency curves. All rules improve with budget, and all of them
remain between the two bounds, but they are not separable from one another. The paired tests make this
precise. In the temporal setting there are 45 comparisons against random selection, given by three pairs,
five budgets and three competing rules. None of them favours a competing rule once the Holm correction is
applied. Two favour random: uncertainty sampling on <i>K. pneumoniae</i> at 800 labels is worse by 0.029
AUROC, and diversity sampling on <i>S. aureus</i> at 40 labels is worse by 0.008. The cross-site
experiment adds 120 further comparisons across the three remaining hospitals, and none of those reaches
significance in either direction. Taken together, 165 paired comparisons produce no evidence that an
informed rule helps, and two instances in which it hurts.</p>

<p>This is not an artefact of one dataset or one organism. The finding holds over three species, two
antibiotic classes, four hospitals and two deployment settings, including the cross-site case in which
the new data differs most from the training data and in which AL would be expected to help most.</p>

<h3>C. What a partial test budget buys</h3>
""" + table("II",
            "Share of the available AUROC gain recovered at each budget, averaged over ten seeds. "
            "A value of 1.00 would match retraining on every isolate and 0.00 would match never "
            "retraining. The antibiotic is ceftriaxone for the first two pairs and oxacillin for the third.", T2) + """
<p class="ni">If the rules are interchangeable, the question worth asking is not which rule to use but how
many tests to buy. Table II expresses the result as a price. Testing every isolate that arrives in a year
costs 2094, 1273 and 1445 susceptibility tests at this hospital. Four hundred tests, which is between 19
and 31 percent of those totals, recovers about half of the available gain for <i>E. coli</i> and roughly
three quarters for <i>K. pneumoniae</i>. The curve of benefit against labels is steep at the start and
flat later. Most of the value therefore lies in the decision to retrain at all, not in the decision about
which isolates to retrain on.</p>

<h3>D. The rules differ in who is exposed, not in accuracy</h3>
""" + fig("f3_safety", 3,
          "Resistant isolates that were not selected for testing and would have been reported "
          "susceptible, summed over the pool year and averaged over ten seeds. Hatched bars are a budget "
          "of 400 tests and solid bars 800. Uncertainty sampling is consistently lower than random "
          "selection even though it is the weaker rule by AUROC.") + """
<p class="ni">AUROC describes next year's model. It says nothing about the patients whose isolates were
reported during the year in which the labels were being collected. Fig. 3 counts those cases. At a budget
of 800 tests, the number of resistant isolates that went untested and would have been reported
susceptible falls from 49.8 to 33.6 for <i>E. coli</i> under uncertainty sampling rather than random
selection, from 19.4 to 5.2 for <i>K. pneumoniae</i>, and from 18.8 to 9.2 for <i>S. aureus</i>. These
are reductions of 33, 73 and 51 percent. Major errors do not rise to compensate.</p>

<p>The mechanism is visible in the acquisition log, which records one line per isolate per round. Contrary
to what might be expected, uncertainty sampling buys fewer resistant isolates than random selection does.
At a budget of 400 the resistant share of what it bought was 17.2, 10.2 and 12.8 percent against arrival
rates of 22.2, 14.2 and 18.8 percent. An isolate that the model confidently calls resistant lies far from
the threshold, so the rule declines to pay for it. The isolates it does buy sit two to four times closer
to the threshold than those it skips. It is therefore not a resistance detector. It finds the cases the
model was about to get wrong, which is a different and more useful thing, and it does so while spending
less of the budget on cases the model already handles correctly.</p>

<h3>E. Why the rules agree</h3>
""" + table("III",
            "Overlap of the twenty most used spectral bins between fitted models, as a Jaccard index. "
            "A value of 1.00 means identical lists and 0.00 means no bin in common.", T3) + """
<p class="ni">Table III compares the fitted models through their SHAP profiles. Models that differ only in
how their labels were chosen agree with each other about as much as either agrees with the model
retrained on everything. The comparison that stands out is the last one before the mean. The model that
was never retrained is the outlier in every pair, and on <i>K. pneumoniae</i> it shares only two of twenty
bins with the fully retrained model. Retraining changes what a model looks at; changing the acquisition
rule at a fixed amount of retraining largely does not.</p>

<p>Counting how many of the six models place a given bin in their top twenty makes the structure clearer.
For <i>E. coli</i>, 9 bins appear in all six lists out of 32 that appear anywhere, and the strongest lies
at 2150 to 2156 daltons. For <i>S. aureus</i> the figure is 8 of 40, at 2405 to 2411 and 2852 to 2858
daltons. For <i>K. pneumoniae</i> it is only 2 of 57, which matches that pair having the fewest isolates,
the lowest AUROC and the least stable explanations. A small shared core is found by every model, and the
tail shifts with the training set. Because all six models are fitted to the same underlying relationship
and the easily located part of it is located by all of them, similar accuracy is the expected outcome. We
do not assign these masses to particular proteins. The low mass region is crowded, several known markers
fall within a few daltons of one another, and a 3 dalton bin cannot separate them.</p>
"""


# ----------------------------------------------------------------- 6 discussion, 7 conclusion
def S6():
    return """<h2>VI.&nbsp;&nbsp;Discussion</h2>
<p class="ni">The natural reading of a negative result is that the method was implemented badly. We think
the better reading here is that label efficiency is the wrong objective for this problem. AL promises to
reach a given accuracy with fewer labels. That promise is only valuable when the accuracy at stake is
large. On this modality the entire gap between never retraining and retraining on everything is around
five points of AUROC, and the training years already contain thousands of examples of the few spectral
peaks that carry the signal. One more year of isolates adds mostly repetition. Choosing which repetitions
to buy is a small lever on a problem whose bottleneck is elsewhere. The SHAP analysis supports this
reading, since the models converge on the same bins regardless of how their labels were selected.</p>

<p>That does not make the acquisition rule irrelevant, but it moves the reason for choosing one. The rules
differ in which patients are exposed to an error while the labels are being gathered, and that difference
is large where the accuracy difference is not. A laboratory choosing a policy should therefore decide
whether it is optimising next year's model or this year's reports. Our results suggest that a budget of a
few hundred tests, selected by uncertainty, is a reasonable default: it costs the least, it is no worse
than random by AUROC in all but one configuration, and it substantially reduces the resistant isolates
that would otherwise be reported susceptible.</p>

<p>Several limitations qualify these conclusions. The released spectra carry no acquisition dates, so the
arrival batches within 2017 are a deterministic pseudo ordering rather than true calendar quarters; the
year boundaries themselves are real. The three pairs studied are those with enough labelled isolates for
a temporal analysis, and the conclusions may not transfer to rarer organisms or to antibiotics with very
low resistance prevalence. <i>S. aureus</i> with oxacillin has almost no resistant isolates at two of the
four hospitals, which limits the power of the cross-site comparisons for that pair. The explanations are
computed from one seed per configuration, so some of the disagreement in the tail of the ranking is
sampling noise. Finally, all of this is a retrospective simulation on stored spectra. A prospective study
would have to contend with laboratory turnaround, with clinicians who may override the model, and with
instrument changes that our protocol holds fixed.</p>

<h2>VII.&nbsp;&nbsp;Conclusion</h2>
<p class="ni">We evaluated label acquisition strategies for the maintenance of MALDI-TOF resistance
prediction models under a temporal protocol on DRIAMS. Across 165 paired comparisons spanning three
species and antibiotic pairs, four hospitals and five budgets, no uncertainty, diversity or hybrid rule
outperformed random selection, and two performed worse. The explanation is that retraining makes only
0.044 to 0.051 of AUROC available in total, and that models trained under different rules rely on the
same small set of spectral bins. The quantity worth reporting is cost rather than label efficiency:
roughly a third of a year of susceptibility tests recovers between half and three quarters of the benefit
of testing everything. Uncertainty sampling remains worth using, not because it produces a better model,
but because it reduces by a third to three quarters the resistant isolates that are reported susceptible
while the labels are being collected. Future work should test whether these conclusions hold
prospectively, and whether acquisition rules that target the clinical error directly, rather than model
uncertainty, do better on the operational view.</p>
"""


REFS = """<h2>References</h2>
<div class=&ldquo;refs&rdquo;><ol>
<li>Antimicrobial Resistance Collaborators, &ldquo;Global burden of bacterial antimicrobial resistance in
2019: a systematic analysis,&rdquo; <i>The Lancet</i>, vol. 399, no. 10325, pp. 629-655, 2022.</li>
<li>C. Weis <i>et al.</i>, &ldquo;Direct antimicrobial resistance prediction from clinical MALDI-TOF mass
spectra using machine learning,&rdquo; <i>Nature Medicine</i>, vol. 28, pp. 164-174, 2022.</li>
<li>G. De Waele, G. Menschaert, and W. Waegeman, &ldquo;An antimicrobial drug recommender system using
MALDI-TOF MS and dual-branch neural networks,&rdquo; <i>eLife</i>, vol. 13, e93242, 2024.</li>
<li>B. Settles, &ldquo;Active learning literature survey,&rdquo; Computer Sciences Technical Report 1648, University
of Wisconsin-Madison, 2009.</li>
<li>L. Schmidt-Santiago, A. Guerrero-Lopez, C. Sevilla-Salcedo, D. Rodriguez-Temporal, B.
Rodriguez-Sanchez, and V. Gomez-Verdejo, &ldquo;A systematic review of machine learning on clinical MALDI-TOF
MS,&rdquo; <i>Briefings in Bioinformatics</i>, vol. 27, 2026, doi:10.1093/bib/bbag208.</li>
<li>C. Weis, M. Horn, B. Rieck, A. Cuenod, A. Egli, and K. Borgwardt, &ldquo;Topological and kernel-based
microbial phenotype prediction from MALDI-TOF mass spectra,&rdquo; <i>Bioinformatics</i>, vol. 36, no. S1,
pp. i30-i38, 2020.</li>
<li>D. Duroux, P. P. Meyer, G. Visona, and N. Beerenwinkel, &ldquo;Generalizable machine learning models for
rapid antimicrobial resistance prediction in unseen health care settings,&rdquo; <i>GigaScience</i>, 2026,
doi:10.1093/gigascience/giaf156.</li>
<li>N. Corvelo Benz, L. Miranda, D. Chen, J. Sattler, and K. Borgwardt, &ldquo;Detecting antimicrobial
resistance through MALDI-TOF mass spectrometry with statistical guarantees using conformal prediction,&rdquo;
in <i>Research in Computational Molecular Biology (RECOMB)</i>, Springer, 2025, doi:10.1007/978-3-031-90252-9_5.</li>
<li>J. Chen, J. Yoon, S. Ebrahimi, S. O. Arik, S. Jha, and T. Pfister, &ldquo;ASPEST: bridging the gap between
active learning and selective prediction,&rdquo; <i>Transactions on Machine Learning Research</i>, 2024.</li>
<li>Y. Chen, Z. Ding, and D. Wagner, &ldquo;Continuous learning for Android malware detection,&rdquo; in
<i>USENIX Security Symposium</i>, 2023.</li>
<li>D. D. Lewis and W. A. Gale, &ldquo;A sequential algorithm for training text classifiers,&rdquo; in <i>ACM SIGIR</i>,
1994, pp. 3-12.</li>
<li>O. Sener and S. Savarese, &ldquo;Active learning for convolutional neural networks: a core set approach,&rdquo;
in <i>International Conference on Learning Representations (ICLR)</i>, 2018.</li>
<li>A. Beygelzimer, S. Dasgupta, and J. Langford, &ldquo;Importance weighted active learning,&rdquo; in
<i>International Conference on Machine Learning (ICML)</i>, 2009, pp. 49-56.</li>
<li>A. Krishnamurthy, A. Agarwal, T.-K. Huang, H. Daum&eacute; III, and J. Langford, &ldquo;Active learning for
cost-sensitive classification,&rdquo; <i>Journal of Machine Learning Research</i>, vol. 20, no. 65, pp. 1-50,
2019.</li>
<li>W.-N. Hsu and H.-T. Lin, &ldquo;Active learning by learning,&rdquo; in <i>AAAI Conference on Artificial
Intelligence</i>, 2015, pp. 2659-2665.</li>
<li>P.-Y. Lu, C.-L. Li, and H.-T. Lin, &ldquo;A more robust baseline for active learning by injecting randomness
to uncertainty sampling,&rdquo; in <i>AI and HCI Workshop at ICML</i>, 2023.</li>
<li>F. Barbero, F. Pendlebury, F. Pierazzi, and L. Cavallaro, &ldquo;Transcending Transcend: revisiting malware
classification in the presence of concept drift,&rdquo; in <i>IEEE Symposium on Security and Privacy</i>, 2022,
pp. 805-823.</li>
<li>International Organization for Standardization, <i>ISO 20776-2:2021, Susceptibility testing of
infectious agents and evaluation of performance of antimicrobial susceptibility test devices</i>, 2021.</li>
<li>S. M. Lundberg <i>et al.</i>, &ldquo;From local explanations to global understanding with explainable AI for
trees,&rdquo; <i>Nature Machine Intelligence</i>, vol. 2, pp. 56-67, 2020.</li>
<li>T. Chen and C. Guestrin, &ldquo;XGBoost: a scalable tree boosting system,&rdquo; in <i>ACM SIGKDD</i>, 2016,
pp. 785-794.</li>
<li>S. Holm, &ldquo;A simple sequentially rejective multiple test procedure,&rdquo; <i>Scandinavian Journal of
Statistics</i>, vol. 6, pp. 65-70, 1979.</li>
</ol></div>

"""


def build():
    html = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            "<title>Cost and Safety of Label Acquisition Strategies</title>"
            f"<style>{CSS}</style></head><body>"
            + FRONT + S1 + table("I", "Position of this study relative to representative prior work. "
                                      "Explainable artificial intelligence (XAI) here means any "
                                      "reported feature attribution.", T1)
            + S2 + S3() + S4() + S5() + S6() + REFS + "</body></html>")
    open(S + "ieee.html", "w").write(html)
    print("wrote ieee.html", len(html) // 1024, "KB")


if __name__ == "__main__":
    build()
