# Six page conference version, IEEE two column format. Writes ieee.html (-> PDF via Chrome).
#
# Prose written against the Human Writing Kit. The twelve measures this paper deliberately
# holds away from the middle of the human range, consistently from the first page to the last:
#   1  long sentences, high within paragraph variance   2  heavy parentheses
#   3  no semicolons                                    4  no colons in body prose
#   5  low first person                                 6  figure and table references
#                                                          parenthetical only, never as subjects
#   7  citations at the end of the sentence             8  few, long paragraphs
#   9  digits for every number                         10  no signposting of any kind
#  11  many short subsections                          12  flat declaratives, light hedging
# Everything else is held near the kit's biomedical median.
import os

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, "ifig") + "/"
S = os.environ.get("IEEE_OUT", HERE) + "/"

# IEEE conference layout: US Letter, 0.625 in side margins, two 3.5 in columns with a
# 0.25 in gutter, 10 pt Times body, 8 pt captions and references.
CSS = """
@page { size: Letter; margin: 0.75in 0.63in 1in 0.63in; }
* { box-sizing: border-box; }
body { font-family:"Times New Roman",Times,serif; font-size:9.6pt; line-height:1.14; color:#000;
       background:#fff; margin:0; text-align:justify; hyphens:none; -webkit-hyphens:none;
       column-count:2; column-gap:0.25in; column-width:3.38in; }
.span { column-span:all; }
.ttl { text-align:center; font-size:24pt; line-height:1.15; margin:0 0 9pt; font-weight:400; }
.auwrap { display:flex; justify-content:center; gap:0.22in; margin:0 0 12pt; }
.aublk { font-size:9pt; line-height:1.28; text-align:center; flex:0 1 2.2in; }
.aublk .nm { font-size:10pt; }
.af { text-align:center; font-size:9pt; line-height:1.3; margin:0; font-style:italic; }
.em { text-align:center; font-size:9pt; line-height:1.3; margin:0 0 11pt; }
h2 { font-size:10pt; font-weight:400; font-variant:small-caps; text-align:center;
     margin:9pt 0 3pt; break-after:avoid; letter-spacing:0.02em; }
h3 { font-size:10pt; font-weight:400; font-style:italic; text-align:left;
     margin:6pt 0 1pt; break-after:avoid; }
p { margin:0 0 6pt; text-indent:0.2in; }
p.ni { text-indent:0; }
.abs { font-size:9pt; text-indent:0.19in; margin:0 0 10pt; }
.abs b, .idx b { font-style:italic; font-weight:700; }
.idx { font-size:9pt; text-indent:0.19in; margin:0 0 6pt; }
figure { margin:7pt 0 7pt; break-inside:avoid; }
figure.w { column-span:all; margin:4pt 0 9pt; }
figure img, figure .art { display:block; width:100%; }
figcaption { font-size:8pt; line-height:1.22; margin-top:3.5pt; text-align:justify; text-indent:0; }
table { border-collapse:collapse; width:100%; font-size:8pt; margin:0 0 2pt; }
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
th.g { text-align:center; font-style:italic; border-bottom:0.4px solid #000; }
.refs { font-size:8pt; line-height:1.2; }
.refs ol { margin:0; padding-left:0; list-style:none; counter-reset:r; }
.refs li { margin:0.9pt 0; text-align:justify; counter-increment:r;
           padding-left:13pt; text-indent:-13pt; }
.refs li::before { content:"[" counter(r) "] "; }
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
# ICIC runs single blind review and its template names the authors, so the author block stays by
# default. ANON=1 replaces it with an anonymous block for a venue that asks for a blind copy; the
# body carries no self-citations, acknowledgements or funding note, so nothing else has to change.
ANON = os.environ.get("ANON") == "1"

AUTHORS = """<div class="auwrap">
<div class="aublk"><span class="nm">Dyen Asif</span><br><i>Department of Computer Science</i><br>
<i>National University of Computer and Emerging Sciences</i><br>Islamabad, Pakistan<br>
i240608@isb.nu.edu.pk</div>
<div class="aublk"><span class="nm">Hira Mastoor</span><br><i>Department of Computer Science</i><br>
<i>National University of Computer and Emerging Sciences</i><br>Islamabad, Pakistan<br>
hira.mastoor@nu.edu.pk</div>
<div class="aublk"><span class="nm">Maryam Shahbaz</span><br><i>Department of Computer Science</i><br>
<i>National University of Computer and Emerging Sciences</i><br>Islamabad, Pakistan<br>
maryam.shahbaz@nu.edu.pk</div>
</div>"""

ANON_AUTHORS = """<div class="auwrap">
<div class="aublk"><span class="nm">Anonymous Author(s)</span><br>
<i>Affiliation withheld for review</i></div>
</div>"""

FRONT = """<div class="span">
<p class="ttl">Cost and Safety of Label Acquisition Strategies for<br>
MALDI-TOF Antimicrobial Resistance Prediction</p>
""" + (ANON_AUTHORS if ANON else AUTHORS) + """
</div>
</div>

<p class="abs"><b>Abstract</b>&mdash;Machine learning (ML) applied to matrix-assisted laser
desorption ionization time-of-flight (MALDI-TOF) mass spectra predicts antimicrobial resistance (AMR)
in hours rather than the 1 to 3 days that culture based susceptibility testing takes. A deployed model
decays as the local population of isolates changes, so it has to be retrained, and every label is a
laboratory susceptibility test that someone pays for. Active learning (AL) is the standard
answer to an expensive label, yet a 2026 review of 115 ML studies on clinical MALDI-TOF spectra
identified none in which the cost of acquiring labels was a variable. We ran 1540 retraining simulations on the Database of Resistance Information on
Antimicrobials and MALDI-TOF Mass Spectra (DRIAMS), covering 3 species and antibiotic pairs, 4
hospitals, 5 budgets and 10 seeds per configuration. Models were fitted on 2015 and 2016, bought labels
during 2017 in 4 quarterly rounds, and were tested on 2018. Across 165 paired comparisons no uncertainty,
diversity or hybrid rule beat random selection after correction for multiple testing, and 2 were worse. Little accuracy was available, since the interval between never retraining and
retraining on every arriving isolate spans 0.044 to 0.051 of the area under the receiver operating
characteristic curve (AUROC). A budget buys cost rather than accuracy, and 400 tests (19% to 31% of a
year of isolates) recovered 50% to 77% of that interval. Uncertainty sampling, the weakest rule by
AUROC, cut the resistant isolates reported susceptible during the pool year by 33% to 73%.</p>

<p class="idx"><b>Keywords</b>&mdash;antimicrobial resistance, active learning, MALDI-TOF mass
spectrometry, model maintenance, explainable machine learning.</p>
"""

# ----------------------------------------------------------------- 1 introduction
S1 = """<h2>I.&nbsp;&nbsp;Introduction</h2>
<p class="ni">Antimicrobial resistance is among the largest threats to public health, and an estimated
1.27 million deaths were attributable to bacterial AMR in 2019 [1]. Treatment depends on knowing which
drugs still work, which in routine practice means culture based AST, and that takes up to 72 hours.
MALDI-TOF mass spectrometry is already present in most clinical microbiology laboratories for species
identification, and the spectrum acquired for that purpose can be reused to predict resistance with ML,
which reduces the delay from days to hours [2].</p>

<p>Such a model does not stay accurate on its own. The population of isolates in a hospital changes, the
instrument is serviced or replaced, and the resistance mechanisms in circulation shift. A model trained
here on isolates from 2015 and 2016 reached an AUROC of 0.881 under cross validation inside those years
for <i>Escherichia coli</i> with ceftriaxone, but only 0.824 on isolates from 2018, a drop of 0.057.
Keeping the model useful therefore requires periodic retraining, and retraining requires labels. A label
here is a susceptibility test with reagent and technician costs rather than an annotation that a person
supplies in seconds, and a laboratory willing to fund only a few hundred extra tests in a year has to
decide which isolates receive them.</p>

<p>This is the setting AL was designed for [3]. The arriving isolates are ranked by the model and labels
are bought only where they are expected to be most informative, usually near the decision boundary [10]
or spread across the feature space [11]. AL is well studied in medical imaging and in text, where it is
routinely reported to reach a target accuracy with a fraction of the labels, but whether it does so for
MALDI-TOF resistance prediction has not been established. A systematic review published in 2026, which
covers 115 studies that apply ML to clinical MALDI-TOF spectra and groups them by task, preprocessing,
model family and evaluation, does not identify a single study in which label acquisition cost is a
variable [4]. Work on this modality either assumes that all labels are already present or evaluates a
fixed training set.</p>

<p>We examine that gap directly. The experiments use DRIAMS, a public collection of clinical MALDI-TOF
spectra with matched susceptibility results from 4 Swiss hospitals [2], released under a CC0 public
domain waiver and archived at Dryad (doi:10.5061/<wbr>dryad.<wbr>bzkh1899q). The protocol is temporal
rather than a random split. A model is fitted on isolates from 2015 and 2016, isolates arriving during
2017 are offered to an acquisition rule in 4 quarterly rounds under a fixed budget, and the maintained
model is evaluated on isolates from 2018 (Fig. 1), which keeps the test year strictly after every label
that was bought.</p>

<p>The contributions are as follows. This is the first evaluation of label acquisition cost for
MALDI-TOF resistance prediction, covering 3 species and antibiotic pairs, 4 hospitals and 5 budgets,
with 10 seeds per configuration. The main result is negative and holds across 165 paired comparisons, in
that no acquisition rule outperformed random selection. We account for that result by measuring how
little accuracy retraining makes available in the first place, which turns the useful quantity into cost,
and we report how much of the benefit of retraining a partial test budget recovers (Table II). Model
quality next year and patient exposure this year are then separated, and the two disagree about which
rule is preferable (Fig. 3). TreeSHAP finally shows that models trained under different acquisition
rules rely on the same spectral regions (Fig. 4 and Table III), which is consistent with the absence
of a difference between them.</p>
"""

# ----------------------------------------------------------------- 2 related work
T1 = """<table class="top bot">
<thead><tr><th>Study</th><th>Task and data</th><th class="c">Sites</th>
<th class="c">Temp.</th><th class="c">Cost</th><th class="c">Errors</th><th class="c">XAI</th></tr></thead>
<tbody>
<tr><td>Weis <i>et al.</i> [2]</td><td>AMR from MALDI-TOF, DRIAMS</td><td class="c">4</td>
    <td class="c">no</td><td class="c">no</td><td class="c">no</td><td class="c">no</td></tr>
<tr><td>Weis <i>et al.</i> [5]</td><td>Topological and kernel methods</td><td class="c">1</td>
    <td class="c">no</td><td class="c">no</td><td class="c">no</td><td class="c">no</td></tr>
<tr><td>Duroux <i>et al.</i> [6]</td><td>Generalisation to unseen sites</td><td class="c">4</td>
    <td class="c">yes</td><td class="c">no</td><td class="c">no</td><td class="c">no</td></tr>
<tr><td>Corvelo Benz <i>et al.</i> [7]</td><td>Conformal guarantees, DRIAMS</td><td class="c">4</td>
    <td class="c">no</td><td class="c">no</td><td class="c">partly</td><td class="c">no</td></tr>
<tr><td>Schmidt-Santiago <i>et al.</i> [4]</td><td>Review of 115 MALDI-TOF ML studies</td>
    <td class="n">n/a</td><td class="c">rare</td><td class="c">none</td><td class="c">rare</td><td class="c">21/115</td></tr>
<tr><td>Chen <i>et al.</i> [8]</td><td>AL with selective prediction, images</td><td class="c">n/a</td>
    <td class="c">no</td><td class="c">yes</td><td class="c">no</td><td class="c">no</td></tr>
<tr><td>Chen <i>et al.</i> [9]</td><td>Continuous learning, malware</td><td class="c">n/a</td>
    <td class="c">yes</td><td class="c">yes</td><td class="c">no</td><td class="c">no</td></tr>
<tr class="r"><td>This work</td><td>AL for AMR from MALDI-TOF, DRIAMS</td><td class="c">4</td>
    <td class="c">yes</td><td class="c">yes</td><td class="c">yes</td><td class="c">yes</td></tr>
</tbody></table>"""

S2 = """<h2>II.&nbsp;&nbsp;Related Work</h2>
<h3>A. Resistance prediction from mass spectra</h3>
<p class="ni">Resistance prediction from MALDI-TOF spectra became a practical proposition with the
release of DRIAMS, which pairs more than 300000 routine spectra with susceptibility results and
established that gradient boosted trees and shallow networks reach clinically interesting discrimination
on several species and antibiotic combinations [2]. The representation was later improved with
topological and kernel methods [5], prediction was extended to several antibiotics at once, and
statistical guarantees were added through conformal prediction [7]. SHAP values were used for
interpretation in 21 of the 115 studies covered by the review of Schmidt-Santiago <i>et al.</i>, so model
explanation is established practice on this modality, while temporal evaluation remains uncommon [4].
Generalisation across hospitals has been studied directly, and performance dropped sharply when a model
was moved to a site it was not trained on [6].</p>

<h3>B. Label acquisition under a budget</h3>
<p class="ni">Active learning has a long history. Uncertainty sampling selects the instances closest to
the decision boundary [10], core set and diversity methods instead cover the input space [11], and
importance weighted and cost sensitive variants correct the bias that selective querying introduces
[12], [13]. Hybrid rules combine the two signals [14]. The literature is not uniformly positive. Random
selection is a stronger baseline than it is often given credit for, and injecting randomness into
uncertainty sampling improved its robustness [15]. In security, where models are retrained continuously
against a moving target, label acquisition under budget has been studied in its own right [9], [16], and
work bridging AL and selective prediction shows that the two interact [8]. Those settings resemble ours
in that labels are expensive and the data distribution moves, but none of them involves mass spectra or
susceptibility testing.</p>

<h3>C. Position of this study</h3>
<p class="ni">Prior work on MALDI-TOF resistance prediction has not treated the acquisition of labels as
a cost, has largely not used temporal splits, and has rarely reported the 2 clinical error types
separately (Table I). Work on AL under budget, in turn, has not been applied to this modality. The
combination of a temporal protocol, an explicit test budget, both error types, and an explanation of why
the acquisition rules behave as they do is what this paper contributes.</p>
"""


# ----------------------------------------------------------------- 3 method
def S3():
    return """<h2>III.&nbsp;&nbsp;Method</h2>
<h3>A. Problem setting</h3>
<p class="ni">Let a spectrum be a vector <i>x</i> of 6000 binned intensities and let <i>y</i> be 1 if
the isolate is resistant or intermediate to the antibiotic of interest and 0 if it is susceptible. A
model <i>f</i> is fitted to the isolates available at the start of the period and outputs an estimated
probability of resistance, and a threshold <i>t</i> turns that probability into a report (resistant when
<i>f</i>(<i>x</i>) is at least <i>t</i>, susceptible otherwise). Isolates then arrive over a year in 4
batches. The model scores every arriving isolate in each round, an acquisition rule selects <i>B</i>/4 of
them for laboratory testing, where <i>B</i> is the budget for the whole year, and the true labels of those
isolates are revealed and added to the training set before <i>f</i> and <i>t</i> are refitted. Isolates
that were not selected are reported using the model's own output, which is the operational situation that
matters clinically, because those reports reach clinicians without a confirmatory test (Fig. 1).</p>

""" + fig("f1_pipeline", 1,
          "Study pipeline. The 3 counts in each box are the isolates available for <i>E. coli</i>, "
          "<i>K. pneumoniae</i> and <i>S. aureus</i> at DRIAMS-A. One of the 4 rounds of 2017 is drawn, "
          "in which a quarter of the annual budget B is spent on laboratory susceptibility testing (AST) "
          "and those labels enter the training set. Isolates that are not bought are reported from the "
          "model output alone, and the dashed arms are the 2 bounds.", wide=True) + """

<h3>B. Acquisition rules</h3>
<p class="ni">Four acquisition rules were compared. Random selection draws uniformly from the isolates that
arrived in the round and serves as the baseline. Uncertainty sampling takes the isolates whose predicted
probability is closest to the threshold <i>t</i>, measured as the absolute difference between the 2 [10].
Diversity sampling applies a <i>k</i>-center greedy procedure in the spectral space so that the selected
isolates are spread out rather than clustered [11]. The hybrid rule splits the round budget evenly between
the uncertainty and diversity criteria [14]. Two bounds frame all four. The lower bound never retrains at all,
and the upper bound retrains on every isolate that arrived, which is what a laboratory would obtain if it
tested everything.</p>

<h3>C. Error types</h3>
<p class="ni">Clinical microbiology distinguishes two kinds of mistake, and they are not interchangeable. A
very major error (VME) is a resistant isolate reported as susceptible, which can send a patient home on a
drug that will not work. A major error (ME) is a susceptible isolate reported as resistant, which wastes a
broader spectrum agent and contributes to selection pressure. The definitions follow the International
Organization for Standardization (ISO) standard 20776-2 [17]. Both are reported throughout, because a rule
that lowers one while raising the other has not improved anything.</p>

<h3>D. Predictive and operational views</h3>
<p class="ni">Two views that are often conflated are kept apart here. The predictive view is the usual one,
namely how well next year's model discriminates, measured as AUROC on the 2018 isolates. The operational
view counts what happened during the pool year itself, namely how many of the isolates that were not
selected for testing were resistant and were nonetheless reported susceptible. These are counts of
patients affected rather than rates, and the two views do not have to agree.</p>

<h3>E. Explaining the fitted models</h3>
<p class="ni">SHAP values were computed to understand why the rules behave similarly [18]. They
distribute a single prediction across the input features in the unique way that satisfies local accuracy,
missingness and consistency, and for tree ensembles they have an exact polynomial time solution, so no
sampling approximation is involved. We used the TreeSHAP implementation inside the gradient boosting
library itself [19], which removes any possibility of a mismatch between the explained model and the
deployed one. Six models were explained per pair (the two bounds, and random and uncertainty acquisition at
budgets of 400 and 800 labels) on the same 2018 isolates, so any difference is a difference between models
rather than between evaluation sets. Two models were then compared by the overlap of their 20 most used bins
and by the rank correlation over all 6000 bins. Importance of a bin is its mean absolute SHAP value, and
its direction was obtained by splitting the isolates at the median intensity of that bin and taking the
difference in mean SHAP between the halves, because averaging signed values over all isolates simply
follows the majority class (here susceptible).</p>
"""


# ----------------------------------------------------------------- 4 setup
def S4():
    return """<h2>IV.&nbsp;&nbsp;Experimental Setup</h2>
<h3>A. Data and splits</h3>
<p class="ni">DRIAMS provides spectra preprocessed to 6000 bins of 3 daltons each, spanning 2000 to 20000
daltons, and labels follow the convention of the original release, in which resistant and intermediate are
coded together as 1. Three species and antibiotic pairs have enough labelled isolates for a temporal
analysis and were studied here, namely <i>E. coli</i> with ceftriaxone, <i>Klebsiella pneumoniae</i> with
ceftriaxone, and <i>Staphylococcus aureus</i> with oxacillin. At the primary site (DRIAMS-A) these gave
1481, 812 and 1141 training isolates from 2015 and 2016, pools of 2094, 1273 and 1445 isolates arriving in
2017, and test sets of 1386, 775 and 1204 isolates from 2018, with resistance prevalence in the test year
of 18.5%, 13.9% and 14.6% respectively. The released spectra carry no acquisition dates, so the 4 arrival
batches were formed by a deterministic hash of the isolate code rather than by calendar quarter. The cross
site experiment moves a model trained at DRIAMS-A to each of DRIAMS-B, DRIAMS-C and DRIAMS-D.</p>

<h3>B. Model and protocol</h3>
<p class="ni">The classifier is a gradient boosted tree ensemble [19], tuned once on the 2015 and 2016
data only and then held fixed, so that no information from the pool or test years entered the
configuration. Of the training years, 20% was held out to set the threshold <i>t</i> at the lowest
value achieving 90% sensitivity to resistance, which reflects the clinical preference for avoiding very major
errors. Budgets of 40, 100, 200, 400 and 800 labels were spread evenly over the 4 rounds. Every
configuration was repeated with 10 random seeds, and the cross site configurations with 5, giving 1540
retraining simulations in total.</p>

<h3>C. Statistics and availability</h3>
<p class="ni">Each rule was compared with random selection on matched seeds using the Wilcoxon signed
rank test, and the resulting p values were corrected across the whole family of comparisons with the Holm
procedure [20]. Only the corrected values are reported below. The DRIAMS release used here is archived at
doi:10.5061/<wbr>dryad.<wbr>bzkh1899q, and our code, the per isolate acquisition log and the per run
result records are released with the paper.</p>
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

# Table III: top-20 overlap and the rank correlation over all 6000 bins, side by side.
T3 = """<table class="top bot">
<thead>
<tr><th rowspan="2">Models compared</th><th class="g" colspan="2"><i>E. coli</i></th>
    <th class="g" colspan="2"><i>K. pneu.</i></th><th class="g" colspan="2"><i>S. aureus</i></th></tr>
<tr><th class="n">J</th><th class="n">&rho;</th><th class="n">J</th><th class="n">&rho;</th>
    <th class="n">J</th><th class="n">&rho;</th></tr>
</thead>
<tbody>
<tr><td>Random 400 vs uncertainty 400</td><td class="n">0.60</td><td class="n">0.38</td>
    <td class="n">0.38</td><td class="n">0.44</td><td class="n">0.54</td><td class="n">0.44</td></tr>
<tr><td>Random 800 vs uncertainty 800</td><td class="n">0.60</td><td class="n">0.39</td>
    <td class="n">0.29</td><td class="n">0.44</td><td class="n">0.43</td><td class="n">0.48</td></tr>
<tr class="r"><td>Random 800 vs retrain on all</td><td class="n">0.67</td><td class="n">0.40</td>
    <td class="n">0.38</td><td class="n">0.52</td><td class="n">0.60</td><td class="n">0.54</td></tr>
<tr><td>Uncertainty 800 vs retrain on all</td><td class="n">0.60</td><td class="n">0.39</td>
    <td class="n">0.38</td><td class="n">0.48</td><td class="n">0.43</td><td class="n">0.47</td></tr>
<tr class="r"><td>No retraining vs retrain on all</td><td class="n">0.43</td><td class="n">0.24</td>
    <td class="n">0.11</td><td class="n">0.22</td><td class="n">0.29</td><td class="n">0.30</td></tr>
<tr><td>Mean over all 15 model pairs</td><td class="n">0.60</td><td class="n">0.36</td>
    <td class="n">0.31</td><td class="n">0.40</td><td class="n">0.49</td><td class="n">0.44</td></tr>
</tbody></table>"""

def S5():
    return """<h2>V.&nbsp;&nbsp;Results</h2>
<h3>A. Bounds on the available gain</h3>
<p class="ni">Two bounds define the space in which any acquisition rule has to operate. A model that was
never retrained reached an AUROC on the 2018 isolates of 0.823, 0.742 and 0.799 for the 3 pairs, while a
model retrained on every isolate that arrived in 2017 reached 0.867, 0.788 and 0.850. Retraining helps,
and the direction of the effect was consistent across all 3 pairs, which confirms the premise of the
study. The size of the effect is modest. The difference between the 2 bounds was 0.044 (<i>E. coli</i>),
0.046 (<i>K. pneumoniae</i>) and 0.051 (<i>S. aureus</i>) of AUROC, so every acquisition rule competes
inside a window of about 5 points, and the standard error over 10 seeds was of a similar order at the
smaller budgets (Fig. 2).</p>

""" + fig("f2_curves", 2,
          "Test AUROC on 2018 isolates against the number of susceptibility tests bought during 2017, "
          "for each species and antibiotic pair. Points are means over 10 seeds and bars are standard "
          "errors. The shaded band runs from never retraining (dotted line) to retraining on every "
          "arriving isolate (dashed line), and its height is printed inside each panel. The right hand "
          "axis reads the same band as a share of the gain retraining makes available. All 4 rules lie "
          "inside the band and their intervals overlap at almost every budget.", wide=True) + """

<h3>B. Comparison against random selection</h3>
<p class="ni">All 4 rules improved with budget and all of them stayed between the 2 bounds, but they were
not separable from one another (Fig. 2). The paired tests make this precise. The temporal setting gives 45
comparisons against random selection (3 pairs, 5 budgets and 3 competing rules), of which 14 reached
p &lt; 0.05 before correction and 2 survived the Holm procedure, both of them in favour of random
selection. Uncertainty sampling on <i>K. pneumoniae</i> at 800 labels was worse by 0.029 AUROC
(p = 0.029 corrected) and diversity sampling on <i>S. aureus</i> at 40 labels was worse by 0.008
(p = 0.029 corrected). The cross site experiment adds 120 further comparisons across DRIAMS-B, DRIAMS-C
and DRIAMS-D, and none of those reached significance in either direction, before or after correction.
These 165 paired comparisons produce no evidence that an informed rule helps, and 2 instances in which it
hurts. The result held over 3 species, 2 antibiotic classes, 4 hospitals and 2 deployment settings,
including the cross site case in which the new data differs most from the training data and in which AL
would be expected to help most.</p>

<h3>C. Cost of a partial test budget</h3>
""" + table("II",
            "Share of the available AUROC gain recovered at each budget, averaged over 10 seeds. "
            "A value of 1.00 would match retraining on every isolate and 0.00 would match never "
            "retraining. The antibiotic is ceftriaxone for the first 2 pairs and oxacillin for the third.", T2) + """
<p class="ni">If the rules are interchangeable, the question worth asking is how many tests to buy rather
than which rule to use. Testing every isolate that arrives in a year costs 2094, 1273 and 1445
susceptibility tests at DRIAMS-A, and a budget of 400 tests (19% to 31% of those totals) recovered about
half of the available gain for <i>E. coli</i> (0.50) and roughly three quarters for <i>K. pneumoniae</i>
(0.77), which is what Table II expresses as a price. The curve of benefit against labels is steep at the
start and flat later (Fig. 2), so most of the value lies in the decision to retrain at all, and
comparatively little in the decision about which isolates to retrain on.</p>

<h3>D. Operational errors during the pool year</h3>
""" + fig("f3_errors", 3,
          "Clinical errors on the isolates that were not selected for testing, summed over the pool year "
          "and averaged over 10 seeds. Hatched bars are a budget of 400 tests and solid bars 800. Panel "
          "(a) counts resistant isolates that would have been reported susceptible, panel (b) susceptible "
          "isolates that would have been reported resistant.", wide=True) + """
<p class="ni">AUROC describes next year's model and says nothing about the patients whose isolates were
reported during the year in which the labels were being collected, which is what Fig. 3 counts. At a
budget of 800 tests the number of resistant isolates that went untested and would have been reported
susceptible fell from 49.8 to 33.6 for <i>E. coli</i> under uncertainty sampling rather than random
selection, from 19.4 to 5.2 for <i>K. pneumoniae</i>, and from 18.8 to 9.2 for <i>S. aureus</i>,
reductions of 33%, 73% and 51%. Major errors moved in the same direction for 2 of the 3 pairs, falling
from 347.8 to 259.8 for <i>E. coli</i> and staying level for <i>S. aureus</i> (134.6 to 140.0), but they
rose from 123.7 to 190.1 for <i>K. pneumoniae</i>, which is the one configuration in which the safety gain
is paid for in broad spectrum prescribing.</p>

<p>The mechanism is visible in the acquisition log, which records one line per isolate per round. Contrary
to what might be expected, uncertainty sampling bought fewer resistant isolates than random selection did.
The resistant share of what it bought at a budget of 400 labels was 14.9%, 9.7% and 10.8%, against arrival
rates of 22.2%, 14.2% and 18.8%. An isolate that the model confidently calls resistant lies far from the
threshold, so the rule declines to pay for it, and the isolates it does buy sit 2 to 4 times closer to the
threshold (median absolute distance 0.008 against 0.030 for <i>E. coli</i>) than those it skips.
Uncertainty sampling is therefore a detector of impending mistakes rather than a detector of resistance.
It finds the cases the model was about to get wrong, and it does so while spending less of the budget on
cases the model already handles correctly.</p>

<h3>E. SHAP profiles of the fitted models</h3>
""" + fig("f4_shap", 4,
          "Spectral bins the 6 explained models rely on, for the 11 most important bins that reached the "
          "top 20 of at least 4 of them. Marker area is the mean absolute SHAP value of that bin for that "
          "model, colour is the direction of the effect, and grey dots mark bins outside that model's top "
          "20. Columns are the 2 bounds (none, all) and random and uncertainty acquisition at 400 and 800 "
          "labels.", wide=True) + """
<p class="ni">Models that differ only in how their labels were chosen agreed with each other about as much
as either agreed with the model retrained on everything (Table III). The comparison that stands out is the
last one before the mean. The model that was never retrained was the outlier in every pair, and on
<i>K. pneumoniae</i> it shared only 2 of 20 bins with the fully retrained model (Jaccard index 0.11,
&rho; = 0.22). Retraining changes what a model looks at, whereas changing the acquisition rule at a fixed
amount of retraining largely does not.</p>

""" + table("III",
            "Agreement between fitted models in their SHAP profiles. J is the Jaccard overlap of the 20 "
            "most used spectral bins, where 1.00 means identical lists and 0.00 means no bin in common. "
            "&rho; is the Spearman rank correlation of importance over all 6000 bins.", T3) + """

<p class="ni">Counting how many of the 6 models placed a given bin in their top 20 makes the structure
clearer (Fig. 4). Nine bins appeared in all 6 lists for <i>E. coli</i>, out of 32 that appeared
anywhere, and the strongest lay at 2150 to 2156 daltons. The figure was 8 of 40 for <i>S. aureus</i>, at
2405 to 2411 and 2852 to 2858 daltons, and only 2 of 57 for <i>K. pneumoniae</i>, which matches that pair
having the fewest isolates, the lowest AUROC and the least stable explanations. A small shared core is
found by every model and the tail shifts with the training set. Because all 6 models are fitted to the
same underlying relationship, and the easily located part of it is located by all of them, similar
accuracy is the expected outcome. We do not assign these masses to particular proteins. The low mass
region is crowded, several known markers fall within a few daltons of one another, and a 3 dalton bin
cannot separate them.</p>

"""


# ----------------------------------------------------------------- 6 discussion, 7 conclusion
def S6():
    return """<h2>VI.&nbsp;&nbsp;Discussion</h2>
<h3>A. Why label efficiency is the wrong objective here</h3>
<p class="ni">The natural reading of a negative result is that the method was implemented badly. The
better reading here is that label efficiency is the wrong objective for this problem. AL promises to reach
a given accuracy with fewer labels, and that promise is only valuable when the accuracy at stake is large.
On this modality the entire gap between never retraining and retraining on everything is around 5 points
of AUROC (0.044 to 0.051), and the training years already contain thousands of examples of the few
spectral peaks that carry the signal. One more year of isolates adds mostly repetition, and choosing which
repetitions to buy is a small lever on a problem whose bottleneck lies elsewhere. The SHAP analysis
supports this reading, since the models converged on the same bins regardless of how their labels were
selected (Fig. 4).</p>

<h3>B. What a laboratory should take from this</h3>
<p class="ni">The acquisition rule still matters, although for a different reason. The rules differ in
which patients are exposed to an error while the labels are being gathered, and that difference is large
where the accuracy difference is small. A laboratory choosing a policy has to decide whether it is
optimising next year's model or this year's reports. A budget of a few hundred tests selected by
uncertainty is a reasonable default on these data, since it costs the least, it is no worse than random
selection by AUROC in all but one configuration, and it substantially reduces the resistant isolates that
would otherwise be reported susceptible. The <i>K. pneumoniae</i> result at 800 labels is the caveat, both
because it is the one configuration where uncertainty sampling lost AUROC outright and because it is the
one where major errors rose (Fig. 3), and a laboratory working on that organism would be buying a 73%
reduction in very major errors at the price of 66 additional major errors over the year.</p>

<h3>C. Limitations</h3>
<p class="ni">The released spectra carry no acquisition dates, so the arrival batches within 2017 are a
deterministic pseudo ordering rather than true calendar quarters, although the year boundaries themselves
are real. The 3 pairs studied are those with enough labelled isolates for a temporal analysis, and the
conclusions may not transfer to rarer organisms or to antibiotics with very low resistance prevalence.
<i>S. aureus</i> with oxacillin has almost no resistant isolates at 2 of the 4 hospitals, which limits the
power of the cross site comparisons for that pair. The explanations were computed from 1 seed per
configuration, so some of the disagreement in the tail of the ranking is sampling noise. All of this is a
retrospective simulation on stored spectra, and a prospective study would have to contend with laboratory
turnaround, with clinicians who may override the model, and with instrument changes that our protocol
holds fixed.</p>

<h2>VII.&nbsp;&nbsp;Conclusion</h2>
<p class="ni">Label acquisition rules for the maintenance of MALDI-TOF resistance prediction models were
evaluated under a temporal protocol on DRIAMS. Across 165 paired comparisons spanning 3 species and
antibiotic pairs, 4 hospitals and 5 budgets, no uncertainty, diversity or hybrid rule outperformed random
selection, and 2 performed worse. The explanation is that retraining makes only 0.044 to 0.051 of AUROC
available in total, and that models trained under different rules rely on the same small set of spectral
bins (Table III). The quantity worth reporting is therefore cost rather than label efficiency, in that
roughly a third of a year of susceptibility tests recovers between half and three quarters of the benefit
of testing everything (Table II). Uncertainty sampling remains worth using for a different reason, since
it reduced by a third to three quarters the resistant isolates that were reported susceptible while the
labels were being collected. Future work should test whether these conclusions hold prospectively, and
whether acquisition rules that target the clinical error directly, rather than model uncertainty, do
better on the operational view.</p>
"""


REFS = """<h2>References</h2>
<div class="refs"><ol>
<li>Antimicrobial Resistance Collaborators, &ldquo;Global burden of bacterial antimicrobial resistance in
2019: a systematic analysis,&rdquo; <i>The Lancet</i>, vol. 399, no. 10325, pp. 629-655, 2022.</li>
<li>C. Weis <i>et al.</i>, &ldquo;Direct antimicrobial resistance prediction from clinical MALDI-TOF mass
spectra using machine learning,&rdquo; <i>Nature Medicine</i>, vol. 28, pp. 164-174, 2022.</li>
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
