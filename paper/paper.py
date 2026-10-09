# Conference paper, single column, Computer Modern, LaTeX-style. Writes paper.html (+ paper.pdf via Chrome).
import base64
import os

HERE = os.path.dirname(os.path.abspath(__file__))
FIG, FONTS = os.path.join(HERE, "fig") + "/", os.path.join(HERE, "fonts") + "/"
S = os.environ.get("PAPER_OUT", HERE) + "/"          # where paper.html is written


def font_face(name, weight, style, fname):
    b64 = base64.b64encode(open(FONTS + fname, "rb").read()).decode()
    return (f"@font-face{{font-family:'CMU';font-weight:{weight};font-style:{style};font-display:block;"
            f"src:url(data:font/woff2;base64,{b64}) format('woff2');}}")


FONTCSS = "".join([font_face("CMU", 400, "normal", "KaTeX_Main-Regular.woff2"),
                   font_face("CMU", 700, "normal", "KaTeX_Main-Bold.woff2"),
                   font_face("CMU", 400, "italic", "KaTeX_Main-Italic.woff2"),
                   font_face("CMU", 700, "italic", "KaTeX_Main-BoldItalic.woff2")])

CSS = FONTCSS + """
@page { size: A4; margin: 30mm 38.5mm 28mm 38.5mm; }
* { box-sizing: border-box; }
body { font-family:'CMU','Latin Modern Roman','Times New Roman',Times,serif; color:#000; background:#fff;
       font-size:9.6pt; line-height:1.44; margin:0; text-align:justify; hyphens:none; -webkit-hyphens:none;
       -webkit-font-feature-settings:"liga" 1; }
.title { text-align:center; font-size:15.5pt; line-height:1.3; margin:18mm 0 7mm; font-weight:400; }
.authors { text-align:center; font-size:10.8pt; margin:0 0 4mm; line-height:1.5; }
.affil { text-align:center; font-size:9pt; line-height:1.45; margin:0 0 1.5mm; }
.emails { text-align:center; font-size:9pt; line-height:1.5; margin:4mm 0 0; }
a, .lnk { color:#1a4b8c; text-decoration:none; }
.abswrap { margin:9mm 4mm 0; }
.abshead { text-align:center; font-weight:700; font-size:10.4pt; margin:0 0 2mm; }
.abswrap p { font-size:9pt; line-height:1.42; text-indent:0; margin:0 0 2.5mm; }
.kw { font-size:9pt; line-height:1.42; text-indent:0; margin:3mm 0 0; }
h2 { font-size:12.2pt; font-weight:700; margin:7mm 0 2.5mm; text-align:left; break-after:avoid; }
h3 { font-size:10.4pt; font-weight:700; margin:5mm 0 1.5mm; text-align:left; break-after:avoid; }
h2 .num { margin-right:2.6mm; } h3 .num { margin-right:2.2mm; }
p { margin:0 0 0; text-indent:1.6em; }
p.noind, li p { text-indent:0; }
p + p { margin-top:0.6mm; }
ul, ol { margin:1.5mm 0 2mm; padding-left:6mm; text-align:justify; }
li { margin:0.9mm 0; }
ul { list-style-type:none; } ul > li::before { content:"\\2022"; display:inline-block; width:4mm; margin-left:-4mm; }
figure { margin:5mm 0 5mm; break-inside:avoid; text-align:center; }
figure img, figure .art { display:block; margin:0 auto; }
figure .art svg { display:block; width:100%; height:auto; }
figcaption { font-size:8.8pt; line-height:1.38; margin-top:2mm; text-align:justify; text-indent:0; }
figcaption .lab { font-weight:700; }
table { border-collapse:collapse; width:100%; margin:1.5mm 0 4mm; font-size:8.7pt; break-inside:avoid; }
table.bt { border-top:1.1px solid #000; border-bottom:1.1px solid #000; }
table.bt thead th { border-bottom:0.7px solid #000; font-weight:700; text-align:left; padding:1.1mm 0 1.1mm 0; }
table.bt td { padding:0.72mm 0 0.72mm 0; vertical-align:top; }
table.bt td.n, table.bt th.n { text-align:right; padding-left:4mm; white-space:nowrap; }
table.bt td:first-child, table.bt th:first-child { white-space:nowrap; hyphens:none; padding-right:3mm; }
table.bt tr.rule td { border-top:0.5px solid #999; }
.tcap { font-size:8.8pt; line-height:1.38; margin:4mm 0 0; text-indent:0; text-align:justify; }
.tcap .lab { font-weight:700; }
.eq { text-align:center; margin:3mm 0; font-size:10pt; }
.refs { font-size:8.6pt; line-height:1.36; }
.refs ol { padding-left:7mm; margin:0; }
.refs li { margin:1.1mm 0; text-align:justify; }
em, i { font-style:italic; }
.sc { font-variant:small-caps; }
"""


def svg(name):
    return open(FIG + name + ".svg").read()


def fig(name, num, cap, width="100%"):
    return (f'<figure><div class="art" style="width:{width}">{svg(name)}</div>'
            f'<figcaption><span class="lab">Fig. {num}</span>: {cap}</figcaption></figure>')


def tcap(num, text):
    return f'<p class="tcap"><span class="lab">Table {num}</span>: {text}</p>'


def R(*ns):
    """Citation marks, e.g. R(1) -> [1]; R(10,11) -> [10, 11]."""
    return '<span class="lnk">[' + ", ".join(str(n) for n in ns) + "]</span>"


def ref(kind, n):
    return f'<span class="lnk">{kind} {n}</span>'


# ------------------------------------------------------------------ front matter
FRONT = f"""<div class="title">Which Isolates Should the Laboratory Test?<br>
Active Learning, Drift and Calibration for<br>MALDI-TOF Antimicrobial Resistance Prediction</div>
<div class="authors">Dyen Asif<sup>1*</sup>,&nbsp; Hira Mastoor<sup>1</sup>,&nbsp; Maryam Shahbaz<sup>1</sup></div>
<div class="affil"><sup>1</sup>Department of Computer Science, National University of Computer
and Emerging Sciences, Islamabad, Pakistan.</div>
<div class="emails"><sup>*</sup>Corresponding author. Email: <span class="lnk">i240608@isb.nu.edu.pk</span><br>
Contributing authors: <span class="lnk">hira.mastoor@nu.edu.pk</span>;
<span class="lnk">maryam.shahbaz@nu.edu.pk</span></div>

<div class="abswrap">
<div class="abshead">Abstract</div>
<p>Models that read antibiotic resistance directly from MALDI-TOF mass spectra are attractive because the spectrum is
already acquired during routine identification, but their accuracy falls away as bacterial populations and laboratory
conditions change, and keeping them useful means retraining them on isolates that have been freshly phenotyped.
Phenotyping is the expensive step. A laboratory that can pay for only a limited number of susceptibility tests in a year
therefore has to decide which of the arriving isolates to send, and as far as we are aware this question has not been
examined for this modality. We report 2&thinsp;859 retraining simulations on DRIAMS covering three organism and
antibiotic pairs, four hospitals, label budgets between 40 and 800, and ten random seeds. Random selection is compared
against uncertainty, diversity and hybrid acquisition, against conformal safety routing, against pseudo labelling, and
against recalibration of the deployed decision rule. None of the acquisition strategies produced a better model than
random sampling in any of the 45 preplanned comparisons, and the primary endpoint that we had specified in advance, the
number of labels needed to recover 95&thinsp;% of the gain from full retraining, was not reached within 800 labels by
any strategy. The choice of rule still matters, however, since an isolate that is tested receives a laboratory answer
rather than a model answer. Acquiring the isolates the model was least sure about reduced the resistant isolates that
were wrongly reported susceptible during the year by 33 to 73&thinsp;% (<i>p</i>&thinsp;&lt;&thinsp;0.01 for all three
pairs), although the effect on the opposite error turned out to depend on the organism. A third result concerns the
safety machinery itself. A decision threshold calibrated for 90&thinsp;% sensitivity was delivering 73 to 80&thinsp;%
two years later, and a conformal rule that promised at most 10&thinsp;% miscoverage on resistant isolates delivered 14
to 19&thinsp;%, in neither case with any warning sign in the discrimination metric. Recalibrating on freshly acquired
labels brought the sensitivity target back, but it roughly doubled the opposite error, which is what 90&thinsp;%
sensitivity actually costs at an AUROC between 0.75 and 0.85. A preregistered search over 16 method combinations, run on
a development split that never touches the test year, gave the same picture and found no combination that improved both
error types beyond uncertainty acquisition on its own. We argue from this that label efficiency is the wrong objective
for the problem, and that acquisition policies should be reported with counts of both error types at deployment, with
calibration treated as a component that has to be maintained rather than as a property of the training run.</p>
<p class="kw"><b>Keywords:</b> Antimicrobial resistance, MALDI-TOF mass spectrometry, Active learning, Dataset shift,
Conformal prediction, Model calibration, Clinical decision support</p>
</div>"""

# ------------------------------------------------------------------ 1 Introduction
S1 = f"""<h2><span class="num">1</span>Introduction</h2>
<p class="noind">In routine practice, antimicrobial resistance is established by phenotypic susceptibility testing, and
the result takes a day or more to come back once the organism has been identified. Identification itself is almost
immediate, because clinical laboratories already acquire a MALDI-TOF mass spectrum of every isolate as part of that
step. Weis et al. {R(1)} showed that those same spectra carry a usable resistance signal, and released DRIAMS, a
collection of spectra from four hospitals paired with laboratory susceptibility labels. Areas under the receiver
operating characteristic curve of approximately 0.80, 0.74 and 0.74 were reported for <i>Escherichia coli</i>,
<i>Klebsiella pneumoniae</i> and <i>Staphylococcus aureus</i> on clinically important antibiotics. A model that reads
the spectrum can therefore offer a provisional resistance call several hours before the phenotype is available.</p>
<p>Such a model is not a static artefact. Bacterial populations change, and so do laboratory workflows and instruments,
and the same study documented that predictive accuracy decays over time. Keeping the model useful therefore means
retraining it on recently phenotyped isolates, and phenotyping is precisely the cost that the model was meant to avoid
in the first place. A laboratory that can afford, say, four hundred extra susceptibility tests in a year is then left
with a concrete operational question: <i>which</i> four hundred of the several thousand arriving isolates should be
tested?</p>
<p>This is the classical pool based active learning problem {R(2)}, and the natural expectation is that a well chosen
subset buys more accuracy per test than an arbitrary one. Our aim was to measure how much more. Over 2&thinsp;859
simulated retraining runs we found no measurable advantage at all. The negative result seems to us worth reporting in
its own right, since the opposite is widely assumed in applied work. It is not the whole story, though, and much of what
follows is concerned with what that result hides.</p>
<p>The acquisition rule decides more than what the model learns next. It also decides <i>who receives a laboratory
answer instead of a model answer</i>. An isolate that is sent for testing is, from the patient's point of view,
protected, because its true phenotype becomes known before treatment decisions are finalised. An isolate that is not
tested is reported with the model's call, errors and all. Acquisition is in that sense a patient safety decision taken
while the year is running, and it is largely separate from what the same decision does for next year's model. On that
axis the strategies do differ, and they differ sharply.</p>
<p>A third thread runs through the results. The decision threshold and the conformal prediction sets used in this
setting are both calibrated on historical data, and both make explicit numerical promises: 90&thinsp;% sensitivity to
resistance in the first case, and at most 10&thinsp;% miscoverage per class in the second. Under drift the two promises
failed without any obvious symptom, while the headline discrimination metric remained healthy. We measure how large the
failure becomes, repair it by recalibrating on newly acquired labels, and show that the repair uncovers an operating
cost which the broken calibration had been hiding.</p>
<p>The contributions of this work can be summarised as follows.</p>
<ul>
<li>To our knowledge this is the first study of active isolate acquisition for the maintenance of MALDI-TOF resistance
models. It comprises six experiments and 2&thinsp;859 simulated retraining runs over three organism and antibiotic
pairs and four hospitals, with full seed replication and paired statistical testing.</li>
<li>We report a clearly stated negative result on label efficiency, together with the statistical power that supports
it, and we set it beside a positive result at deployment concerning the errors that actually reach patients.</li>
<li>We quantify how far threshold calibration and conformal calibration decay under temporal drift, and measure what
restoring the sensitivity promise costs in terms of the opposite error.</li>
<li>We carry out a preregistered search over sixteen method variants on a development split that never touches the test
year, which reproduces our conclusions and eliminates the obvious remedies.</li>
<li>We give an explicit account of a design flaw in our own semisupervised experiment, which is reported rather than
quietly discarded, so that the corresponding question is left open instead of answered incorrectly.</li>
</ul>
<p>The rest of the paper is organised as follows. Section 2 reviews related work on resistance prediction from mass
spectra, on active learning and on calibration under shift. Section 3 formalises the maintenance loop, the error
taxonomy and the acquisition strategies. Section 4 describes the data, the experimental matrix and the statistical
protocol. Section 5 reports the results. Section 6 discusses what they imply, Section 7 states the limitations and
Section 8 concludes.</p>"""

# ------------------------------------------------------------------ 2 Related work
S2 = f"""<h2><span class="num">2</span>Related Work</h2>
<p class="noind">In this section we summarise the relevant progress in resistance prediction from mass spectra, in
uncertainty quantification for that modality, in active learning and its behaviour under distribution shift, and in the
maintenance of calibration, and we identify the gap that motivates the present study.</p>

<h3><span class="num">2.1</span>Resistance Prediction from MALDI-TOF Spectra</h3>
<p class="noind">DRIAMS established the task, the standard preprocessing and the reference baselines. It assembles more
than 300&thinsp;000 spectra with laboratory confirmed resistance profiles collected at four Swiss diagnostic
laboratories {R(1)}. Later work has extended the approach to further organisms and to improved spectral
representations. The temporal decay of these models is documented within the same line of work, so demonstrating decay
is not a contribution of the present paper. It is the premise on which our study rests, and we verify it once more
under our own protocol in Section 5.1.</p>

<h3><span class="num">2.2</span>Uncertainty Quantification for This Modality</h3>
<p class="noind">A classifier intended for clinical microbiology has to be able to decline a prediction when it cannot
make one reliably. Corvelo Benz et al. {R(3)} applied conformal prediction to MALDI-TOF resistance classification and
obtained prediction sets carrying distribution free statistical guarantees, while earlier work had introduced kernels
tailored to mass spectra together with well calibrated uncertainty estimates {R(4)}. Our use of conformal sets as an
<i>acquisition</i> rule, that is, as a way of testing exactly those isolates that the model cannot resolve, builds
directly on that work. What we add to it is the observation that the guarantee does not survive a year of drift unless
it is recalibrated, along with a measurement of how large the violation becomes.</p>

<h3><span class="num">2.3</span>Active Learning and Query Strategies</h3>
<p class="noind">Pool based active learning requests expert annotation for the most informative unlabelled samples in an
iterative fashion {R(2)}. Uncertainty sampling {R(5)}, core set and k-center diversity {R(6)}, and hybrids of the two
make up the standard families. Importance weighted {R(7)}, bandit selected {R(8)} and cost sensitive {R(9)} variants
have been proposed to deal with sampling bias, strategy selection and asymmetric misclassification cost respectively.
It has also been observed repeatedly in benchmark studies that random acquisition is a stubborn baseline, and that
deliberately injecting randomness into uncertainty sampling works as a stabiliser {R(10)}. In medical imaging the
annotation burden has been reduced substantially by active learning, even though the evaluation in those studies is
almost always label efficiency on a held out set rather than the errors that are incurred while the loop is running.</p>

<h3><span class="num">2.4</span>Active Learning under Distribution Shift</h3>
<p class="noind">Malware detection has the same structure as our problem, namely a deployed classifier, a continuous
arrival of new samples, a bounded analyst budget and continuous drift. Label efficient update policies {R(11)} and the
decay of conformal evaluation under drift {R(12)} are both documented in that setting. The active selective prediction
setting combines acquisition with the option to abstain and hand the case to a human {R(13)}. None of this literature
deals with the question of which bacterial isolates a clinical laboratory should phenotype, and as far as we are aware
none of it uses the random share of an active learning budget as the calibration set for the deployed decision
rule.</p>

<h3><span class="num">2.5</span>Calibration under Shift</h3>
<p class="noind">Weighted conformal prediction restores coverage under covariate shift provided that a density ratio can
be estimated {R(14)}, and adaptive conformal inference tracks shift online by adjusting the target level in response to
observed feedback {R(15)}. Both are implemented as candidate remedies in the combination search of Section 5.7. The
underlying split conformal framework is standard {R(16)}.</p>"""

# ------------------------------------------------------------------ 3 Problem setting
def S3():
    return f"""<h2><span class="num">3</span>Problem Setting and Method</h2>

<h3><span class="num">3.1</span>The Maintenance Loop</h3>
<p class="noind">We simulate the loop that a laboratory would actually run, which is shown in {ref("Fig.", 1)}. A model
trained on historical isolates is in service. New isolates arrive through the year in <i>R</i>&thinsp;=&thinsp;4 rounds.
In round <i>r</i> the model currently in service scores every arriving isolate, an acquisition rule spends
<i>b</i>/<i>R</i> of a fixed annual budget <i>b</i> on susceptibility tests, the tested isolates come back with their
true labels, and the model together with its decision threshold and its conformal bounds is refitted on everything that
has been acquired so far. Isolates that were not tested are reported with the model's call, and an error there is an
error a clinician may act on. At the end of the year the model is evaluated on the following year's isolates, which are
never visible while the loop is running.</p>
{fig("f1_loop", 1, "The loop that every run simulates. The acquisition rule determines both what the model learns next "
     "(upper path) and which patients receive a laboratory answer rather than a model answer (lower path). Errors on the "
     "lower path are counted as they occur, not only at the end of the year. VME and ME are defined in Section 3.2.")}

<h3><span class="num">3.2</span>Error Taxonomy and Reported Quantities</h3>
<p class="noind">Two error types are distinguished throughout the paper, following the terminology that is used to
evaluate susceptibility testing devices {R(17)}. A <b>very major error</b> (VME) is a resistant isolate that is reported
as susceptible, so the patient may be given an antibiotic that does not work. A <b>major error</b> (ME) is a
susceptible isolate reported as resistant, so the patient may be given an unnecessarily broad antibiotic, which carries
its own harm and its own cost. The two are not interchangeable. A method that lowers one of them while raising the
other has not made anything safer; it has only moved along a tradeoff.</p>
<p>We report both error types in two different views, and this distinction is central to the paper. The
<i>predictive</i> view gives rates on the following year's isolates and measures how good the retrained model is. The
<i>operational</i> view gives counts among the untested isolates of the current year and measures how many patients
were actually affected while the loop was running. Writing <i>U<sub>r</sub></i> for the isolates of round <i>r</i> that
the rule did not acquire, the operational very major error count is</p>
<div class="eq">VME<sub>op</sub> = &Sigma;<sub>r=1..R</sub> | {{ i &isin; U<sub>r</sub> : y<sub>i</sub> = R and
p<sub>i</sub> &lt; t<sub>r</sub> }} |,</div>
<p class="noind">where <i>y<sub>i</sub></i> is the true phenotype, <i>p<sub>i</sub></i> the probability that was
assigned by the model in service when isolate <i>i</i> arrived, and <i>t<sub>r</sub></i> the threshold in force at that
moment; ME<sub>op</sub> is defined symmetrically. Since the rule and the model both change between rounds, these counts
cannot be recovered from metrics that are computed at the end of the year, and it is on these counts that the
acquisition strategies separate.</p>

<h3><span class="num">3.3</span>Acquisition Strategies</h3>
<p class="noind">Let <i>p</i> be the model's probability of resistance for an arriving isolate and <i>t</i> the current
decision threshold. In each round the rule selects <i>b</i>/<i>R</i> isolates out of that round's arrivals.</p>
<ul>
<li><b>Random.</b> Uniform selection without replacement; this is the control condition.</li>
<li><b>Uncertainty.</b> Smallest |<i>p</i>&thinsp;&minus;&thinsp;<i>t</i>|, that is, the isolates whose call is closest
to flipping {R(5)}.</li>
<li><b>Diversity.</b> Greedy k-center selection in a 50-dimensional principal component space, which maximises coverage
of spectrum space relative to what has already been labelled {R(6)}.</li>
<li><b>Hybrid.</b> The 4<i>b</i> most uncertain isolates are clustered by k-means into <i>b</i> groups, and the isolate
nearest each centroid is acquired.</li>
<li><b>Conformal routing.</b> Only isolates whose per class prediction set is ambiguous, that is
{{S,&thinsp;R}} or empty, are acquired {R(3)}. We report this both capped at the budget and uncapped.</li>
<li><b>Bounds.</b> <i>No retraining</i> (budget zero) and <i>full retraining</i> (every arriving isolate labelled)
bracket what any rule can achieve.</li>
</ul>

<h3><span class="num">3.4</span>Decision Threshold and Conformal Bounds</h3>
<p class="noind">The operating threshold is taken to be the largest <i>t</i> that achieves a target sensitivity
&tau;&thinsp;=&thinsp;0.90 to resistance on held out data, since that is the quantity a laboratory would specify.
Mondrian (per class) split conformal prediction supplies prediction sets at &alpha;&thinsp;=&thinsp;0.10, calibrated
separately on the susceptible and the resistant validation isolates so that the minority class receives a guarantee of
its own {R(16)}. In the baseline configuration both are fitted once on the 2015 and 2016 validation split and then left
untouched, which is what a deployed system does by default; Section 5.5 reports what happens when they are instead
refitted each round on freshly acquired labels.</p>"""


# ------------------------------------------------------------------ 4 Experimental setup
def S4():
    exp_rows = [("E1", "Label efficiency and acquisition family", "random, uncertainty, diversity, hybrid", "40 to 800", "10", "660"),
                ("E2", "Value of unlabelled spectra", "the above + pseudo labelling", "100 to 800", "10", "390"),
                ("E3", "Conformal routing as an acquisition rule", "routing, routing (uncapped)", "40 to 800", "10", "180"),
                ("E4", "Adoption at a different hospital", "random, uncertainty, diversity, hybrid", "25 to 400", "5", "880"),
                ("E5", "Recalibration on acquired labels", "random, uncertainty", "100 to 800", "10", "239"),
                ("D1", "Preregistered combination search", "16 combinations (Section 5.7)", "100, 300", "5", "510")]
    rows = "".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td><td class='n'>{d}</td><td class='n'>{e}</td><td class='n'>{f}</td></tr>"
                   for a, b, c, d, e, f in exp_rows)
    hp = [("Organism and antibiotic pairs", "<i>E. coli</i> with ceftriaxone, <i>K. pneumoniae</i> with ceftriaxone, <i>S. aureus</i> with oxacillin"),
          ("Features", "6&thinsp;000 binned spectral intensities"),
          ("Label convention", "intermediate and resistant both treated as resistant"),
          ("Training years / test year", "2015 and 2016 (80&thinsp;% train, 20&thinsp;% validation) / 2018"),
          ("Acquisition pool", "2017 isolates, divided into R = 4 arrival rounds"),
          ("Classifier", "gradient boosted trees (XGBoost), tuned once per pair and then frozen"),
          ("Target sensitivity &tau;", "0.90, used to set the decision threshold"),
          ("Conformal level &alpha;", "0.10, per class (Mondrian) split conformal"),
          ("Embedding for diversity", "50 principal components fitted on the training years"),
          ("Pseudo label cutoffs (E2)", "p &le; 0.05 susceptible, p &ge; 0.95 resistant, weight 0.5"),
          ("Recalibration share (E5)", "25&thinsp;% of acquired labels withheld from training"),
          ("Seeds", "10 (5 for transfer and for the development search)"),
          ("Statistical test", "paired Wilcoxon signed rank over seeds, Holm correction within each pair")]
    hrows = "".join(f"<tr><td>{a}</td><td>{b}</td></tr>" for a, b in hp)
    return f"""<h2><span class="num">4</span>Experimental Setup</h2>

<h3><span class="num">4.1</span>Dataset and Splits</h3>
<p class="noind">All of the experiments use DRIAMS {R(1)}. Each isolate is represented by one MALDI-TOF spectrum binned
into 6&thinsp;000 intensity features and paired with a laboratory susceptibility label. Intermediate and resistant are
both treated as resistant, following the reference implementation that was released with the dataset. We study the
three organism and antibiotic pairs that have enough labelled isolates for repeated simulation.</p>
<p>The temporal protocol is shown in {ref("Fig.", 2)}. It trains on the 2015 and 2016 isolates of hospital DRIAMS-A,
holding out 20&thinsp;% as the validation split that is used for the threshold and the conformal bounds, spends the
label budget on 2017 isolates arriving in four rounds, and evaluates on 2018. DRIAMS does not record acquisition dates,
so the four arrival rounds are a fixed pseudo random partition of the 2017 isolates derived from a hash of the isolate
identifier. This reproduces the structure of a budget that is spent over time, but it <i>cannot</i> reproduce drift
within the year, a limitation we return to in Section 7. The transfer protocol moves the model trained on 2015 and 2016
to hospitals B, C and D, and allows each of them to acquire local labels from its own 2018 isolates, holding out a
stratified test split at each site.</p>
{fig("f2_data", 2, "Data and splits. Counts are isolates per organism and antibiotic pair. The 2018 isolates of "
     "hospital A are reserved for final evaluation, and the development split used for the combination search of "
     "Section 5.7 never touches them. <i>S. aureus</i> has no labelled oxacillin isolates at hospital D, so that "
     "combination is not run.")}

<h3><span class="num">4.2</span>Experimental Matrix</h3>
<p class="noind">Six experiments were executed, and they are summarised in {ref("Table", 1)}. Every configuration is
replicated across seeds, and the data split, the hyperparameters and the random seed are held fixed within a comparison,
so that any difference can be attributed to the acquisition rule and the calibration policy alone.</p>
{tcap(1, "Experimental matrix. Budgets are total labels acquired over the year, divided evenly across the four arrival "
      "rounds. Runs include the no retraining and full retraining bounds where applicable. One E5 run was lost in "
      "transfer, giving 239 of 240.")}
<table class="bt"><thead><tr><th>Id</th><th>Question</th><th>Acquisition rules</th><th class="n">Budgets</th>
<th class="n">Seeds</th><th class="n">Runs</th></tr></thead><tbody>{rows}
<tr class="rule"><td colspan="5"><b>Total</b></td><td class="n"><b>2&thinsp;859</b></td></tr></tbody></table>

<h3><span class="num">4.3</span>Protocol Constants</h3>
<p class="noind">{ref("Table", 2)} lists the quantities that are held constant across all runs. Hyperparameters were
tuned once per organism and antibiotic pair on the training years by cross validation and then frozen, so that every
acquisition rule is compared at equal model capacity.</p>
{tcap(2, "Protocol constants, held fixed across every run.")}
<table class="bt"><thead><tr><th style="width:38%">Parameter</th><th>Value</th></tr></thead><tbody>{hrows}</tbody></table>

<h3><span class="num">4.4</span>Evaluation Metrics and Statistical Analysis</h3>
<p class="noind">Model quality is reported as AUROC on the following year's isolates, with the area under the precision
and recall curve and balanced accuracy as secondary measures. Safety is reported in the operational view of
Section 3.2, as counts of both error types among the untested isolates. Calibration is reported as realised sensitivity
against the 0.90 target, and as per class conformal coverage against the 0.90 guarantee. The primary endpoint, which
was specified before any run was executed, was the number of labels required to recover 95&thinsp;% of the AUROC gap
between the two bounds, estimated by bootstrap over seeds. Strategies are compared against random acquisition with a
paired Wilcoxon signed rank test over matched seeds, and the Holm procedure is applied within each organism and
antibiotic pair in order to control the family wise error rate at 0.05.</p>"""


# ------------------------------------------------------------------ 5 Results
def S5():
    t3 = [("<i>E. coli</i> / CRO", "0.823", "0.852", "0.846", "0.854", "<b>0.863</b>", "0.867"),
          ("<i>K. pneumoniae</i> / CRO", "0.742", "0.772", "0.743", "<b>0.779</b>", "0.772", "0.788"),
          ("<i>S. aureus</i> / OXA", "0.799", "0.838", "0.825", "0.832", "<b>0.842</b>", "0.850")]
    r3 = "".join("<tr><td>" + r[0] + "</td>" + "".join(f"<td class='n'>{v}</td>" for v in r[1:]) + "</tr>" for r in t3)
    t4 = [("<i>E. coli</i>", "49.8", "33.6", "&minus;33", "0.008", "347.8", "259.8", "&minus;25", "0.002"),
          ("<i>K. pneumoniae</i>", "19.4", "5.2", "&minus;73", "0.002", "123.7", "190.1", "+54", "0.002"),
          ("<i>S. aureus</i>", "18.8", "9.2", "&minus;51", "0.008", "134.6", "140.0", "+4", "0.432")]
    r4 = "".join("<tr><td>" + r[0] + "</td>" + "".join(f"<td class='n'>{v}</td>" for v in r[1:]) + "</tr>" for r in t4)
    return f"""<h2><span class="num">5</span>Results</h2>

<h3><span class="num">5.1</span>Premise: Temporal Decay and the Value of Retraining</h3>
<p class="noind">A model that is frozen after 2016 loses ground on the 2018 isolates, and full retraining on the 2017
labels recovers it: AUROC rises by 0.044, 0.046 and 0.051 for the three pairs ({ref("Fig.", 3)}). The gap is modest, but
it is entirely consistent across seeds, and it is this gap that every acquisition strategy is competing to close
cheaply. All of the results that follow are expressed relative to these two bounds.</p>
{fig("f3_drift", 3, "Retraining recovers accuracy lost to drift. Bars show mean AUROC on 2018 isolates over ten seeds; "
     "whiskers are 95&thinsp;% confidence intervals. Labels above the right hand bars give the gain over not "
     "retraining at all.", width="70%")}

<h3><span class="num">5.2</span>Primary Outcome: No Strategy Outperformed Random</h3>
<p class="noind">{ref("Fig.", 4)} shows the label efficiency curves and {ref("Fig.", 5)} the paired differences against
random acquisition. Across the 45 preplanned comparisons, that is three pairs by five budgets by three strategies,
<b>no strategy was significantly better than random once the Holm correction had been applied</b>. The only significant
results run in the opposite direction: uncertainty sampling was worse than random for <i>K. pneumoniae</i> at 800
labels (&minus;0.029, Holm <i>p</i>&thinsp;=&thinsp;0.029) and for <i>S. aureus</i> at the same budget
(&minus;0.013, raw <i>p</i>&thinsp;=&thinsp;0.006, Holm <i>p</i>&thinsp;=&thinsp;0.088). The primary endpoint we had
specified in advance was never reached. No strategy recovered 95&thinsp;% of the retraining gap within 800 labels, and
random acquisition itself recovered only 66 to 77&thinsp;% at that budget. {ref("Table", 3)} gives the values at the
final budget.</p>
{fig("f4_curves", 4, "Label efficiency curves. Mean AUROC on 2018 isolates over ten seeds, with shaded 95&thinsp;% "
     "confidence intervals, against a logarithmic budget axis. The dashed upper line is full retraining, which consumes "
     "1&thinsp;273 to 2&thinsp;094 labels, and the dotted lower line is no retraining. All four acquisition rules lie "
     "within one another's confidence bands at every budget.")}
{fig("f5_forest", 5, "Paired differences against random acquisition, by pair and budget. Points are mean AUROC "
     "differences over ten matched seeds with 95&thinsp;% confidence intervals; the shaded band marks the difference of "
     "&plusmn;0.005 prespecified as negligible. No interval excludes zero in a direction favouring the strategy once "
     "Holm correction is applied.")}
{tcap(3, "AUROC on 2018 isolates at the largest budget of 800 labels, mean over ten seeds, with the two bounds. "
      "Confidence intervals at 95&thinsp;% are at most 0.014 throughout and are drawn in Figs. 4 and 5. The best "
      "active learning entry per row is set in bold; no difference from random is statistically significant.")}
<table class="bt"><thead><tr><th style="width:30%">Pair</th><th class="n">No retraining</th><th class="n">Random</th>
<th class="n">Uncertainty</th><th class="n">Diversity</th><th class="n">Hybrid</th><th class="n">Full retraining</th>
</tr></thead><tbody>{r3}</tbody></table>
<p>Because the design is paired over seeds it is reasonably sensitive: with ten seeds it detects an AUROC difference of
about 0.008 at 80&thinsp;% power for the variances we observed. Large gains from these strategies can therefore be
excluded in this setting, even though gains of any size cannot. In practical terms, a laboratory that acquires isolates
at random gives up nothing measurable in model quality.</p>

<h3><span class="num">5.3</span>Acquisition Determines Which Patients Are Exposed</h3>
<p class="noind">The picture changes once the measurement moves from next year's model to this year's patients.
Uncertainty sampling spends the budget exactly where the model's call is least trustworthy, so the isolates it sends to
the laboratory are disproportionately the ones the model would have got wrong, and those isolates then receive a true
phenotype instead of a predicted one. Summed over the year at 800 labels, uncertainty acquisition reduced the resistant
isolates that were wrongly reported susceptible by 33, 73 and 51&thinsp;% relative to random ({ref("Fig.", 6)}; all
<i>p</i>&thinsp;&lt;&thinsp;0.01, paired Wilcoxon over seeds).</p>
<p>This benefit has to be reported together with its cost on the opposite error, and here the species behave
differently ({ref("Table", 4)}). Major errors fell by 25&thinsp;% for <i>E. coli</i>, were unchanged for
<i>S. aureus</i>, and rose by 54&thinsp;% for <i>K. pneumoniae</i>, which is also the pair for which uncertainty
acquisition produced the weakest model. What we claim is therefore a reliable reduction in the dangerous error,
together with an effect on the other error that depends on the organism, and not a uniform improvement in safety.</p>
{fig("f6_safety", 6, "Resistant isolates wrongly reported susceptible during the year, counted among isolates that were "
     "not sent to the laboratory. Bars are means over ten seeds with 95&thinsp;% confidence intervals; hatched bars are "
     "random acquisition and solid bars uncertainty acquisition. Labels give the relative change, with an asterisk "
     "marking <i>p</i>&thinsp;&lt;&thinsp;0.01. At small budgets the strategies are indistinguishable; the gap opens as "
     "the budget grows.")}
{tcap(4, "Both error types among untested isolates at a budget of 800 labels, summed over the year, mean over ten "
      "seeds. The relative change is uncertainty acquisition against random; <i>p</i>-values are paired Wilcoxon, "
      "uncorrected. VME denotes resistant reported susceptible and ME susceptible reported resistant.")}
<table class="bt"><thead><tr><th>Pair</th><th class="n">VME random</th><th class="n">VME unc.</th>
<th class="n">change</th><th class="n"><i>p</i></th><th class="n">ME random</th><th class="n">ME unc.</th>
<th class="n">change</th><th class="n"><i>p</i></th></tr></thead><tbody>{r4}</tbody></table>

<h3><span class="num">5.4</span>Both Calibrated Components Had Expired</h3>
<p class="noind">Both of the calibrated components failed, and neither failure shows up in the discrimination metric
that would normally be monitored. The decision threshold had been chosen on the 2015 and 2016 validation isolates so as
to catch 90&thinsp;% of resistant isolates; on the 2018 isolates the same threshold caught 80, 73 and 79&thinsp;%
({ref("Fig.", 7)}a). The conformal rule promises that at most 10&thinsp;% of resistant isolates will receive a
confident susceptible prediction set, and measured over the 2017 isolates it delivered 15.5, 18.9 and 14.3&thinsp;%
({ref("Fig.", 7)}b).</p>
<p>This also explains a result in E3 that is otherwise puzzling. Conformal routing matched random acquisition on AUROC
while using fewer labels, between 428 and 650 rather than 800, and yet it left <i>more</i> missed resistances than
random at the same budget: 78 against 50, 33 against 19 and 39 against 19, with Holm
<i>p</i>&thinsp;&lt;&thinsp;0.01 in every case. A routing rule can only be as good as the uncertainty estimate it
routes on, and that estimate had quietly expired.</p>
{fig("f7_calib", 7, "Two broken promises. (a) The decision threshold was set for 90&thinsp;% sensitivity to resistance "
     "on historical validation data; on 2018 isolates it delivers between 0.10 and 0.18 less. (b) The "
     "per class conformal rule promises that at most 10&thinsp;% of resistant isolates receive a confident "
     "susceptible set, and delivers 14 to 19&thinsp;% over the 2017 isolates. Whiskers are 95&thinsp;% confidence "
     "intervals over seeds.")}

<h3><span class="num">5.5</span>Recalibration Restores the Target and Exposes Its Cost</h3>
<p class="noind">Experiment E5 withholds a quarter of the acquired labels from training and uses them, in each round, to
reset both the decision threshold and the conformal bounds. Sensitivity on the 2018 isolates moves back towards the
target, from 0.82 to 0.88, from 0.64 to 0.77 and from 0.72 to 0.79 when averaged over strategies and budgets. The major
error rate rises correspondingly, from 0.37 to 0.52, from 0.27 to 0.49 and from 0.26 to 0.39, and balanced accuracy
falls ({ref("Fig.", 8)}). AUROC is essentially unchanged, and marginally lower, because a quarter of the acquired
labels no longer contributes to training.</p>
<p>The right reading of this is not that recalibration does harm. It is that the drifted threshold had silently moved to
a different operating point, one that looked better on major errors only because it had stopped keeping its sensitivity
promise. Restoring the promise shows what 90&thinsp;% sensitivity really costs on a model whose AUROC lies between
0.75 and 0.85. A laboratory that finds both of those numbers unacceptable needs a better model, not a better
threshold.</p>
{fig("f8_recal", 8, "Recalibration moves every configuration up and to the right: closer to the sensitivity target, at "
     "the cost of more susceptible isolates reported resistant. Arrows run from the stale calibration of E1, drawn "
     "hollow, to recalibration on freshly acquired labels in E5, drawn filled. Marker shape denotes the species and "
     "colour the acquisition rule; each point averages ten seeds and three budgets.", width="74%")}

<h3><span class="num">5.6</span>Adoption at a Different Hospital</h3>
<p class="noind">The largest effects in the whole study come from transfer, and they have nothing to do with
acquisition. A model trained at hospital A and applied unchanged elsewhere ranged from unaffected, for <i>E. coli</i> at
hospital B with an AUROC of 0.835, to worse than chance, for <i>K. pneumoniae</i> at hospital B with an AUROC of 0.477.
Local labels repair most of the damage, and they do so quickly: one hundred locally acquired labels moved that worst
case from 0.477 to 0.614, which is the full retraining value at that site ({ref("Fig.", 9)}). Which isolates were
acquired again made no significant difference in any of the 120 comparisons, although the target sites are small and
this test has correspondingly little power.</p>
{fig("f9_site", 9, "Adoption of the model at a new hospital. Hollow markers at zero show the transferred model with no "
     "local labels; lines show random local acquisition. The collapse for <i>K. pneumoniae</i> at hospital B, to below "
     "chance, and its repair by 25 to 100 local labels, is the strongest effect observed in the study.")}"""


def S5b():
    return f"""<h3><span class="num">5.7</span>A Preregistered Search over Method Combinations</h3>
<p class="noind">A single negative result invites the objection that some better combination would have succeeded. We
therefore decomposed the method into five slots, namely the acquisition rule, the split of the budget between targeted
and random purchase, the retraining weights, the calibration source, and the use of unlabelled spectra. Enumerating
these gave 2&thinsp;430 combinations. Removing the ones that are incoherent or dominated left 1&thinsp;424 valid
combinations, of which 559 were both robust and affordable, and from those we selected sixteen to execute. One family
among them was the family we had expected to win: spend half of the budget on targeted isolates and half at random,
then use the random half, which is an unbiased sample of the drifted distribution and is scored before it enters
training, to reset the threshold and the conformal bounds.</p>
<p>To keep the search honest, all 510 runs were carried out on a <b>development split that never touches 2018</b>.
Training used 2015 and 2016, labels were acquired from the first half of the 2017 arrivals, and testing was done on the
second half. The rule for selecting winners was written into the version controlled log before any run was executed. As
a reproducibility check, 110 of the runs were executed independently on two machines and returned identical
metrics.</p>
<p>The preregistered rule selected a combination that reduced missed resistances by 63&thinsp;% and brought sensitivity
up to 0.92. It achieved this by reporting roughly two thirds of susceptible isolates as resistant. {ref("Fig.", 10)}
shows the reason: every combination that recalibrates slides along the same error tradeoff rather than improving on it,
and our rule had scored only one end of that tradeoff. We report this as a failure of our own decision rule and not as
a method result. It is the clearest illustration in the study of how badly a safety metric can mislead when it is read
in isolation.</p>
<p>Judged on both error types at once, only one family lies strictly inside the baseline on both axes, and that family
is uncertainty acquisition. On its own it gives a ratio of 0.87 on missed resistances
(<i>p</i>&thinsp;=&thinsp;0.017) and 0.84 on major errors (<i>p</i>&thinsp;=&thinsp;0.002), at an AUROC difference of
+0.002. Mixed half and half with random it gives ratios of 0.95 (<i>p</i>&thinsp;=&thinsp;0.16) and 0.89
(<i>p</i>&thinsp;=&thinsp;0.006) at &minus;0.001 AUROC. No combination of recalibration, recency weighting, importance
weighting, drift novelty acquisition or conformal pseudo labelling improved on it. Mean AUROC across all sixteen
combinations spanned 0.815 to 0.839, so model quality was flat whatever the configuration.</p>
{fig("f10_tradeoff", 10, "The error tradeoff on the development split. Each point is one of sixteen method "
     "combinations, averaged over three pairs, two budgets and five seeds. Only points in the shaded quadrant improve "
     "on the random baseline D01 on both error types. The combination selected by our preregistered rule, D14, lies "
     "far to the right: it purchases a low missed resistance rate by reporting most susceptible isolates as "
     "resistant.", width="76%")}

<h3><span class="num">5.8</span>An Invalid Experiment: Pseudo labelling</h3>
<p class="noind">Experiment E2 added self training. Isolates that the model was confident about received pseudo labels,
with <i>p</i>&thinsp;&le;&thinsp;0.05 treated as susceptible and <i>p</i>&thinsp;&ge;&thinsp;0.95 as resistant, and
were then added to the training set at a reduced weight. The results were poor. Pseudo labels on their own fell below
no retraining at all, and major errors rose sharply at the smaller budgets.</p>
<p>They are also uninterpretable, and the reason is an error in our own design. The decision threshold for these models
lies between 0.010 and 0.030, that is, <b>below the pseudo susceptible cutoff of 0.05</b>. Isolates falling in that
band were labelled susceptible for training at the same time as the deployed model was reporting them as resistant
({ref("Fig.", 11)}). The procedure was therefore injecting systematically contradictory labels: between 62 and
66&thinsp;% of each round's arrivals were pseudo labelled, at an accuracy of 89 to 92&thinsp;%, which works out at 60
to 240 incorrect labels per run. We report the experiment as invalid and leave the semisupervised question open, rather
than publish a negative result that was caused by our own implementation. A corrected design would tie the cutoffs to
the operating threshold, or better still derive them from recalibrated conformal sets.</p>
{fig("f11_pseudo", 11, "Why the pseudo labelling experiment is not a fair test. (a) Most arrivals received a "
     "pseudo label, roughly one in ten of which was wrong. (b) The fixed cutoff <i>p</i>&thinsp;&le;&thinsp;0.05 for "
     "“susceptible” lies above the deployed decision threshold <i>t</i> for all three pairs, so every isolate in the "
     "shaded band was trained on as susceptible while being reported as resistant.")}"""


# ------------------------------------------------------------------ 6-8 Discussion, limitations, conclusion
def S6():
    return f"""<h2><span class="num">6</span>Discussion</h2>

<h3><span class="num">6.1</span>Label Efficiency Is the Wrong Objective Here</h3>
<p class="noind">Active learning is conventionally evaluated by asking how few labels are needed to reach a target
accuracy. On this task that number turns out to be dominated by factors the acquisition rule has no control over: the
signal that is available in a 6&thinsp;000 bin spectrum, the prevalence of the resistant class, and the size of the
drift between years. Our strategies moved it by less than the variation between seeds. The very same choice, however,
moved the number of patients who received a wrong susceptible report by as much as a factor of four. For a clinical
deployment it is the second quantity that is worth optimising, and it is invisible to the standard evaluation.</p>

<h3><span class="num">6.2</span>Calibration Is a Maintained Component, Not a Training Artefact</h3>
<p class="noind">Both of the calibrated components in our system were fitted once and then trusted for two years, which
is exactly what a deployed system does by default. Both failed quietly. The threshold lost between 10 and 18 points of
sensitivity, and the conformal rule exceeded its own error budget by a factor of 1.4 to 1.9, while AUROC, which is the
number that would ordinarily be monitored, barely moved at all. Any deployment of this kind of model needs a stream of
freshly phenotyped isolates set aside for calibration, and our results point to an inexpensive way of obtaining one: a
random share of the testing budget is an unbiased sample of the current distribution and can be scored before it enters
training. In our experiments this did not improve the error tradeoff. It remains worth doing all the same, because it
is what keeps a stated guarantee true.</p>

<h3><span class="num">6.3</span>Practical Recommendations</h3>
<p class="noind">The findings translate into four concrete recommendations for a laboratory that maintains such a
model.</p>
<ol>
<li>Acquire isolates for retraining by whatever means is operationally simplest. Random acquisition is not worse in
model quality.</li>
<li>Where the budget allows, bias acquisition towards the isolates the model is uncertain about, not for the model's
benefit, but because those are the isolates whose incorrect calls would otherwise reach patients. The effect on the
number of susceptible isolates reported as resistant should be expected to vary by organism, and it should be measured
rather than assumed.</li>
<li>Recalibrate the decision threshold and any uncertainty sets on recent labels, and treat a drifting realised
sensitivity as an alarm in its own right.</li>
<li>When adopting a model that was developed at another hospital, acquire 25 to 100 local labels before relying on it.
This was the single most valuable intervention we measured.</li>
</ol>

<h2><span class="num">7</span>Limitations</h2>
<p class="noind">There are several limitations which qualify these conclusions.</p>
<ul>
<li><b>No acquisition dates.</b> DRIAMS does not provide them, so the arrival order within the year has to be simulated
by a hash based partition. Seasonal structure and outbreak dynamics are therefore absent, and the drift within the year
that would most favour adaptive acquisition cannot be tested here. This is the limitation we would most like to remove,
and removing it requires a dataset with timestamps.</li>
<li><b>Three pairs, four hospitals, one source.</b> The organisms with enough labelled isolates for this design are few,
and all of the data originate from one country and one collection effort.</li>
<li><b>Simulation rather than deployment.</b> Labels are revealed from an existing database instead of being produced by
a laboratory, so turnaround time, the batch effects of repeating a test in practice, and clinician response are all out
of scope.</li>
<li><b>Statistical power.</b> Ten seeds support the detection of AUROC differences of about 0.008; the transfer tests,
with five seeds and small target sites, are weaker. Absence of evidence here is not strong evidence of absence for
small effects.</li>
<li><b>One classifier family.</b> All of the results use tuned gradient boosted trees. A representation with better
behaved predictive uncertainty could change the ranking of the acquisition rules, and uncertainty sampling in
particular.</li>
<li><b>The semisupervised question remains open</b> by our own admission, for the reason given in Section 5.8.</li>
</ul>

<h2><span class="num">8</span>Conclusion</h2>
<p class="noind">Across 2&thinsp;859 retraining simulations on DRIAMS, no active learning strategy produced a better
resistance model than simply acquiring labels at random, and the standard label efficiency endpoint was never reached.
The same experiments nevertheless show that the choice is consequential. Acquiring the uncertain isolates reduced the
resistant isolates that were wrongly reported susceptible by between a third and three quarters, while the decision
threshold and the conformal guarantees that were supposed to bound such errors had both quietly expired after two years
of drift. A preregistered search over sixteen method combinations, executed on a development split that never touched
the test year, reproduced these conclusions, and by selecting a combination that merely exchanged one error for the
other it illustrated how readily a safety metric misleads when it is read in isolation. We recommend that acquisition
policies for this task be reported with counts of both error types at deployment, and that calibration be treated as a
maintained component rather than a property of the training run.</p>
<p><b>Reproducibility.</b> Every experiment is driven by a single configuration file, and each run writes a
self describing record containing its seed, a fingerprint of the data split, library versions and per round metrics.
110 runs were executed independently on two machines and returned identical metrics. Code and result records will be
released on publication.</p>"""


REFS = """<h2>References</h2>
<div class="refs"><ol>
<li>Weis, C., Cuénod, A., Rieck, B., Dubuis, O., Graf, S., Lang, C., et al.: Direct antimicrobial resistance prediction
from clinical MALDI-TOF mass spectra using machine learning. Nature Medicine <b>28</b>, 164-174 (2022).</li>
<li>Settles, B.: Active learning literature survey. Computer Sciences Technical Report 1648, University of
Wisconsin-Madison (2009).</li>
<li>Corvelo Benz, N., Miranda, J., Chen, Z., Sattler, A., Borgwardt, K.: Detecting antimicrobial resistance through
MALDI-TOF mass spectrometry with statistical guarantees using conformal prediction. In: Research in Computational
Molecular Biology (RECOMB 2025), Lecture Notes in Computer Science, Springer (2025).</li>
<li>Weis, C., Horn, M., Rieck, B., Cuénod, A., Egli, A., Borgwardt, K.: Topological and kernel based microbial phenotype
prediction from MALDI-TOF mass spectra. Bioinformatics <b>36</b>(S1), i30-i38 (2020).</li>
<li>Lewis, D.D., Gale, W.A.: A sequential algorithm for training text classifiers. In: SIGIR 1994, pp. 3-12 (1994).</li>
<li>Sener, O., Savarese, S.: Active learning for convolutional neural networks: a core set approach. In: International
Conference on Learning Representations (ICLR 2018).</li>
<li>Beygelzimer, A., Dasgupta, S., Langford, J.: Importance weighted active learning. In: International Conference on
Machine Learning (ICML 2009), pp. 49-56.</li>
<li>Hsu, W.-N., Lin, H.-T.: Active learning by learning. In: AAAI Conference on Artificial Intelligence (AAAI 2015),
pp. 2659-2665.</li>
<li>Krishnamurthy, A., Agarwal, A., Huang, T.-K., Daumé III, H., Langford, J.: Active learning for cost sensitive
classification. In: International Conference on Machine Learning (ICML 2017), pp. 1915-1924.</li>
<li>Lu, P.-Y., Li, C.-L., Lin, H.-T.: A more robust baseline for active learning by injecting randomness to uncertainty
sampling. ICML 2023 Workshop on Artificial Intelligence and Human-Computer Interaction (2023).</li>
<li>Chen, Y., Ding, Z., Wagner, D.: Continuous learning for Android malware detection. In: USENIX Security Symposium
(2023).</li>
<li>Barbero, F., Pendlebury, F., Pierazzi, F., Cavallaro, L.: Transcending Transcend: revisiting malware classification
in the presence of concept drift. In: IEEE Symposium on Security and Privacy (2022), pp. 805-823.</li>
<li>Chen, J., Yoon, J., Ebrahimi, S., Arık, S.Ö., Pfister, T., Jha, S.: ASPEST: bridging the gap between active learning
and selective prediction. Transactions on Machine Learning Research (2024).</li>
<li>Tibshirani, R.J., Barber, R.F., Candès, E.J., Ramdas, A.: Conformal prediction under covariate shift. In: Advances
in Neural Information Processing Systems (NeurIPS 2019), pp. 2530-2540.</li>
<li>Gibbs, I., Candès, E.J.: Adaptive conformal inference under distribution shift. In: Advances in Neural Information
Processing Systems (NeurIPS 2021), pp. 1660-1672.</li>
<li>Vovk, V., Gammerman, A., Shafer, G.: Algorithmic Learning in a Random World. Springer (2005).</li>
<li>International Organization for Standardization: ISO 20776-2:2021, Susceptibility testing of infectious agents, Part 2: Evaluation of performance of antimicrobial susceptibility test devices (2021).</li>
<li>Chen, T., Guestrin, C.: XGBoost: a scalable tree boosting system. In: ACM SIGKDD International Conference on
Knowledge Discovery and Data Mining (KDD 2016), pp. 785-794.</li>
<li>Holm, S.: A simple sequentially rejective multiple test procedure. Scandinavian Journal of Statistics <b>6</b>,
65-70 (1979).</li>
</ol></div>"""


def build():
    html = ("<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
            "<title>Which isolates should the laboratory test?</title>"
            f"<style>{CSS}</style></head><body>"
            + FRONT + S1 + S2 + S3() + S4() + S5() + S5b() + S6() + REFS +
            "</body></html>")
    open(S + "paper.html", "w").write(html)
    print("wrote paper.html", len(html) // 1024, "KB")


if __name__ == "__main__":
    build()
