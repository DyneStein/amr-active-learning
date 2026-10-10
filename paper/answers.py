# Replies to the review questions, laid out like the paper: single column, Computer Modern.
# Every number here comes from the files shipped in the same folder; the source file is named
# next to each table so a reader can check it.  Writes answers.html (-> PDF via Chrome).
import os

from paper import CSS, tcap                      # same stylesheet and caption helper as the paper

S = os.environ.get("ANS_OUT", os.path.dirname(os.path.abspath(__file__))) + "/"


def q(n, title):
    return f'<h2><span class="num">{n}.</span>{title}</h2>'


def f(src):
    return f'<p class="tcap" style="margin-top:1.5mm">Source: <i>{src}</i>.</p>'


FRONT = """
<p class="title">Replies to the review questions on the<br>active learning study</p>
<p class="authors">Dyen Asif, Hira Mastoor, Maryam Shahbaz</p>
<p class="affil">Department of Computer Science, FAST NUCES Islamabad</p>
<p class="emails">i240608@isb.nu.edu.pk</p>
<div class="abswrap">
<p class="abshead">Note</p>
<p>This document answers the points raised in the review, one section each, and points to the file in
the shared folder that each answer rests on. Nothing here is new work. Every figure comes from the runs
already reported in the draft paper, replayed with the same seeds so that the records match the published
tables line for line. Where the answer contradicts the premise of the question, which happens once, the
evidence is laid out rather than the conclusion asserted.</p>
</div>
"""

MAP = q(1, "What was asked, and where each answer lives") + """
<p class="noind">The folder <i>AMR_Final</i> has seven parts. Section numbers below refer to this document.</p>
<table class="bt">
<thead><tr><th>Question raised</th><th>Answered in</th><th>Evidence in the folder</th></tr></thead>
<tbody>
<tr><td>What is SHAP?</td><td>Section 2</td><td>05_Explainability_SHAP</td></tr>
<tr><td>Active learning and traditional learning come out the same, why?</td><td>Section 3</td>
    <td>04_Results/tables</td></tr>
<tr><td>Does the dataset matter?</td><td>Section 3.2</td><td>04_Results/tables</td></tr>
<tr><td>Same accuracy, so what is gained?</td><td>Section 4</td><td>E1_temporal_cost.csv</td></tr>
<tr><td>Do the two give the same features under XAI?</td><td>Section 5</td><td>shap_agreement.csv</td></tr>
<tr><td>If the same features are prominent, why, and what does it mean?</td><td>Section 6</td>
    <td>shap_top_bins.csv</td></tr>
<tr><td>Log file: how do we know what uncertainty picked?</td><td>Section 7</td><td>03_Logs</td></tr>
<tr><td>Dataset share</td><td>Section 8</td><td>02_Dataset</td></tr>
</tbody></table>
"""

SHAP = q(2, "What SHAP is") + """
<p class="noind">A trained model takes a spectrum and returns one number, the probability that the isolate is
resistant. SHAP answers a different question: of that one number, how much came from each part of the
spectrum. The name comes from the Shapley value in cooperative game theory. The idea there is to split a
payout fairly among players who worked together. Here the players are the 6000 intensity bins of the mass
spectrum and the payout is the prediction.</p>

<p>The fair split is defined by an experiment that is never actually run. Take a bin, hide it from the model,
and see how much the prediction moves. Do that for every possible subset of the other bins, hiding the bin or
revealing it, and average the movement across all of those subsets. That average is the bin's SHAP value for
that isolate. Doing it by brute force is impossible, since 6000 bins give more subsets than there are atoms in
anything worth counting, but for a tree model the same quantity has an exact shortcut. Gradient boosted trees
are what we use, so we get the exact answer, not an approximation. We call XGBoost's own contribution routine
rather than a separate library, which rules out any mismatch between the explained model and the deployed
one.</p>

<p>Three properties are worth stating because they are what makes the output trustworthy rather than
suggestive. The values for one isolate add up exactly to that isolate's prediction, minus the average
prediction over the data. A bin the model never looks at gets exactly zero. And if two bins play identical
roles they get identical credit. No other way of splitting the credit has all three.</p>

<p>Two summaries are used in the tables. The first is the mean absolute SHAP value of a bin over the test
isolates, which says how much the model leans on that bin overall, regardless of direction. The second is
direction: we split the isolates at the median intensity of that bin and take the difference in mean SHAP
between the two halves. If the high intensity half is pushed towards resistance, the bin is marked
<i>resistant</i>. This is not the same as averaging the signed value, which was our first attempt and which is
misleading: most isolates in the data are susceptible, so a simple average just follows the majority and
labels a genuine resistance marker as susceptible. The fix was checked on synthetic spectra with a marker
planted at a known position, where the corrected measure recovers the right direction and the naive one does
not.</p>

<p>One caution that belongs with any SHAP table. A bin with a large SHAP value is a bin the model relies on.
That is a statement about the model, not about the bacterium. It becomes a biological claim only when the mass
is matched to a known protein and confirmed independently.</p>
"""

SAME = q(3, "Why active learning and traditional learning come out the same") + """
<p class="noind">They do come out the same, and the reason is that there is very little room between them to
begin with.</p>

<h3><span class="num">3.1</span>The whole argument fits in five points of AUROC</h3>
<p class="noind">Two extremes bound every strategy. The lower one is a model trained in 2015 and 2016 and then
never touched again, scored on 2018. The upper one is the same model retrained on every isolate that arrived
in 2017, which is what a laboratory would get if it tested everything and paid for all of it. Any selection
rule, however clever, has to land between the two.</p>
<table class="bt">
<thead><tr><th>Species and drug</th><th class="n">No retraining</th><th class="n">Retrain on everything</th>
<th class="n">Total headroom</th><th class="n">Pool size</th></tr></thead>
<tbody>
<tr><td><i>E. coli</i>, ceftriaxone</td><td class="n">0.8232</td><td class="n">0.8669</td>
    <td class="n">0.0437</td><td class="n">2094</td></tr>
<tr><td><i>K. pneumoniae</i>, ceftriaxone</td><td class="n">0.7417</td><td class="n">0.7878</td>
    <td class="n">0.0461</td><td class="n">1273</td></tr>
<tr><td><i>S. aureus</i>, oxacillin</td><td class="n">0.7988</td><td class="n">0.8498</td>
    <td class="n">0.0510</td><td class="n">1445</td></tr>
</tbody></table>
""" + tcap(1, "Test AUROC on 2018, averaged over ten seeds. The headroom column is the difference between "
              "never retraining and retraining on the entire 2017 pool. Every selection strategy competes "
              "inside that difference.") + f("04_Results/tables/E1_temporal_cost.csv") + """

<p>Four to five points of AUROC is the entire prize. The four rules then split that prize, and the gap between
the best and worst rule at a fixed budget is smaller still: it never exceeds 0.037 and is usually under 0.02.
Run ten seeds and the seed to seed variation is of the same order. So the honest reading is not that active
learning failed; it is that the question was decided before the strategies were allowed to compete. When the
contested margin is narrower than the noise, no rule can separate from another.</p>

<h3><span class="num">3.2</span>This is not an artefact of one dataset</h3>
<p class="noind">The obvious objection is that the dataset was unlucky. We tested that directly. Three
species and drug pairs, four hospitals, ten random seeds, five budgets and four strategies give 45 paired
comparisons against random selection, each a Wilcoxon signed rank test over the seeds with Holm correction
across the family. None of the 45 shows a strategy beating random. Two show a strategy losing to it:
uncertainty sampling on <i>K. pneumoniae</i> at 800 labels, worse by 0.029 AUROC, and diversity sampling on
<i>S. aureus</i> at 40 labels, worse by 0.008.</p>

<p>The cross site experiment is the stronger version of the same test. There a model trained at one hospital
is moved to another, which is the situation where the new data looks least like the training data and where
active learning is supposed to help most. It does not help there either. A result that holds across three
organisms, two drug classes, four hospitals and two deployment settings is a property of the problem, not of a
file.</p>

<p>The explanation we give in the paper is that MALDI-TOF resistance prediction is label limited rather than
selection limited. The signal that separates resistant from susceptible lives in a handful of peaks, the
training years already contain thousands of examples of those peaks, and one more year of isolates adds mostly
repetition. Choosing which repetitions to buy is a small lever on a problem whose bottleneck is elsewhere.</p>
"""

COST = q(4, "If the accuracy is the same, what is actually gained") + """
<p class="noind">The gain is not accuracy, it is money, and the right way to state the result is as a price.
Testing every isolate that arrives in a year costs 2094 susceptibility tests for <i>E. coli</i> at this
hospital, 1273 for <i>K. pneumoniae</i> and 1445 for <i>S. aureus</i>. The question a laboratory actually
faces is how much of the benefit survives if it buys only a fraction of those tests.</p>

<p>Table 2 gives that directly. The column headed <i>gain captured</i> is the share of the headroom from
Table 1 that a budget recovers. A value of 1.00 would mean the budget matched full retraining; 0.00 would
mean it was no better than never retraining at all.</p>

<table class="bt">
<thead>
<tr><th></th><th class="n"></th><th class="n"></th><th class="n"></th>
    <th class="n" colspan="4" style="text-align:center">Share of the gain captured</th></tr>
<tr><th>Species and drug</th><th class="n">Labels</th><th class="n">Pool</th>
<th class="n">Tests saved</th><th class="n">Random</th><th class="n">Uncertainty</th>
<th class="n">Diversity</th><th class="n">Hybrid</th></tr></thead>
<tbody>
<tr><td><i>E. coli</i>, ceftriaxone</td><td class="n">400</td><td class="n">2094</td><td class="n">80.9%</td>
    <td class="n">0.50</td><td class="n">0.43</td><td class="n">0.54</td><td class="n">0.38</td></tr>
<tr><td></td><td class="n">800</td><td class="n">2094</td><td class="n">61.8%</td>
    <td class="n">0.66</td><td class="n">0.52</td><td class="n">0.70</td><td class="n">0.90</td></tr>
<tr class="rule"><td><i>K. pneumoniae</i>, ceftriaxone</td><td class="n">400</td><td class="n">1273</td>
    <td class="n">68.6%</td><td class="n">0.77</td><td class="n">0.28</td><td class="n">0.65</td>
    <td class="n">0.60</td></tr>
<tr><td></td><td class="n">800</td><td class="n">1273</td><td class="n">37.2%</td>
    <td class="n">0.66</td><td class="n">0.02</td><td class="n">0.82</td><td class="n">0.67</td></tr>
<tr class="rule"><td><i>S. aureus</i>, oxacillin</td><td class="n">400</td><td class="n">1445</td>
    <td class="n">72.3%</td><td class="n">0.60</td><td class="n">0.38</td><td class="n">0.41</td>
    <td class="n">0.57</td></tr>
<tr><td></td><td class="n">800</td><td class="n">1445</td><td class="n">44.6%</td>
    <td class="n">0.77</td><td class="n">0.52</td><td class="n">0.65</td><td class="n">0.85</td></tr>
</tbody></table>
""" + tcap(2, "Share of the available AUROC gain recovered at each budget, averaged over ten seeds. "
              "The budget is the total number of susceptibility tests bought across the whole pool year, "
              "spread over four quarterly rounds.") + f("04_Results/tables/E1_temporal_cost.csv") + """

<p>Read along the <i>E. coli</i> row at 400 labels: a fifth of the year's tests recovers about half of what
testing everything would have given. For <i>K. pneumoniae</i>, 400 of 1273 tests, a third of the year, recovers
roughly three quarters. This is the result worth presenting, and it holds whichever rule is used, which is
precisely why the rule does not matter much. The curve of benefit against labels is steep at the start and flat
later, so most of the value is in deciding to retrain at all rather than in deciding cleverly what to retrain
on.</p>

<p>There is a second gain that the AUROC column hides, and it is the one a microbiologist cares about. Table 3
counts missed resistances in operational terms: isolates that were in fact resistant, were not bought for
testing, and would have been reported susceptible by the model. These are the cases where a patient receives a
drug that will not work.</p>

<table class="bt">
<thead><tr><th>Species and drug</th><th class="n">Labels</th><th class="n">Random</th>
<th class="n">Uncertainty</th><th class="n">Change</th></tr></thead>
<tbody>
<tr><td><i>E. coli</i>, ceftriaxone</td><td class="n">400</td><td class="n">75.6</td><td class="n">67.9</td>
    <td class="n">-10%</td></tr>
<tr><td></td><td class="n">800</td><td class="n">49.8</td><td class="n">33.6</td><td class="n">-33%</td></tr>
<tr class="rule"><td><i>K. pneumoniae</i>, ceftriaxone</td><td class="n">400</td><td class="n">34.8</td>
    <td class="n">29.4</td><td class="n">-16%</td></tr>
<tr><td></td><td class="n">800</td><td class="n">19.4</td><td class="n">5.2</td><td class="n">-73%</td></tr>
<tr class="rule"><td><i>S. aureus</i>, oxacillin</td><td class="n">400</td><td class="n">36.7</td>
    <td class="n">28.8</td><td class="n">-22%</td></tr>
<tr><td></td><td class="n">800</td><td class="n">18.8</td><td class="n">9.2</td><td class="n">-33%</td></tr>
</tbody></table>
""" + tcap(3, "Resistant isolates left untested and reported susceptible during the pool year, counted "
              "rather than expressed as a rate, averaged over ten seeds.") + \
    f("04_Results/tables/E1_temporal_cost.csv") + """

<p>Uncertainty sampling is the weakest rule in Table 2 and the strongest in Table 3. That is not a
contradiction once the two tables are read as answers to different questions. AUROC asks how good next year's
model will be. Table 3 asks how many patients were served wrongly this year, while the labels were being
bought. A rule that concentrates its testing where the model is unsure fixes those cases as it goes, and pays
for it with a training set that is skewed and therefore slightly worse for the following year. Whether that
trade is worth making is a laboratory's decision, not ours, but it should be made knowingly.</p>
"""

FEAT = q(5, "Do active learning and traditional learning rely on the same features") + """
<p class="noind">Mostly yes, and the degree of overlap is itself informative. We fitted six models per species
and drug pair: no retraining, retraining on everything, and random and uncertainty selection at 400 and 800
labels. Each was explained on the same 2018 test isolates, so differences are differences between models and
not between test sets. Two models are then compared by the overlap of their top twenty bins and by the rank
correlation of all 6000 bins.</p>

<table class="bt">
<thead><tr><th>Comparison</th><th class="n"><i>E. coli</i></th><th class="n"><i>K. pneumoniae</i></th>
<th class="n"><i>S. aureus</i></th></tr></thead>
<tbody>
<tr><td>Random 400 against uncertainty 400</td><td class="n">0.60</td><td class="n">0.38</td>
    <td class="n">0.54</td></tr>
<tr><td>Random 800 against uncertainty 800</td><td class="n">0.60</td><td class="n">0.29</td>
    <td class="n">0.43</td></tr>
<tr class="rule"><td>Random 800 against retrain on everything</td><td class="n">0.67</td><td class="n">0.38</td>
    <td class="n">0.60</td></tr>
<tr><td>Uncertainty 800 against retrain on everything</td><td class="n">0.60</td><td class="n">0.38</td>
    <td class="n">0.43</td></tr>
<tr class="rule"><td>No retraining against retrain on everything</td><td class="n">0.43</td>
    <td class="n">0.11</td><td class="n">0.29</td></tr>
<tr><td>Mean over all fifteen pairs of models</td><td class="n">0.60</td><td class="n">0.31</td>
    <td class="n">0.49</td></tr>
</tbody></table>
""" + tcap(4, "Overlap of the twenty most used bins, as a Jaccard index: 1.00 means identical lists, "
              "0.00 means no bin in common.") + f("05_Explainability_SHAP/shap_agreement.csv") + """

<p>The pattern in that table is the point. Models that differ only in how their labels were chosen agree with
each other at roughly the same level as either agrees with full retraining. The one comparison that stands
apart is the last row: the model that was never retrained is the odd one out everywhere, and on
<i>K. pneumoniae</i> it shares only two of twenty bins with the fully retrained model. Retraining changes what
a model looks at. Changing the selection rule, at a fixed amount of retraining, largely does not.</p>

<p>Rank correlations across all 6000 bins tell the same story at a lower level, between 0.24 and 0.54
depending on the pair, with the no retraining comparisons again at the bottom of the range. Two honest
qualifications. First, <i>K. pneumoniae</i> is visibly less stable than the other two, which matches its being
the pair with the fewest isolates and the weakest AUROC. Second, these are single seed explanations, so some
of the disagreement in the tail of the ranking is sampling noise rather than a real difference in what the
models use.</p>
"""

WHY = q(6, "Why the same bins come out on top, and what follows from it") + """
<p class="noind">Counting how many of the six models put a given bin in its top twenty makes the structure
clear. For <i>E. coli</i>, 9 bins appear in all six lists out of 32 distinct bins that appear anywhere. For
<i>S. aureus</i>, 8 of 40. For <i>K. pneumoniae</i>, only 2 of 57, which is the same instability seen in
Table 4. So there is a small shared core that every model finds, and a long tail that shifts with the training
set.</p>

<table class="bt">
<thead><tr><th>Species and drug</th><th>Most used bin, averaged over the six models</th>
<th class="n">Direction</th><th class="n">In all six</th></tr></thead>
<tbody>
<tr><td><i>E. coli</i>, ceftriaxone</td><td>2150 to 2156 Da, two adjacent bins</td><td class="n">resistant</td>
    <td class="n">9 of 32</td></tr>
<tr><td><i>K. pneumoniae</i>, ceftriaxone</td><td>2135 to 2153 Da, with 9827 to 9830 Da in three models</td>
    <td class="n">resistant</td><td class="n">2 of 57</td></tr>
<tr><td><i>S. aureus</i>, oxacillin</td><td>2405 to 2411 Da and 2852 to 2858 Da</td><td class="n">resistant</td>
    <td class="n">8 of 40</td></tr>
</tbody></table>
""" + tcap(5, "The core of the explanation. Direction is the sign of the shift when intensity in that bin is "
              "above the median: resistant means a high peak there pushes the prediction towards resistance.") + \
    f("05_Explainability_SHAP/shap_top_bins.csv") + """

<p>Why would the lists agree? Because all six models are fitted to the same underlying relationship, and the
part of that relationship that is easy to find is found by all of them. The bins in the shared core are the
ones where the resistant and susceptible spectra differ most plainly. A model needs only a few hundred
examples to locate them. What the extra labels buy is not a different core but a better calibrated use of it,
plus a few more marginal bins in the tail. This is the same fact as Section 3, seen from the explanation side:
if the models look at the same evidence, they will reach similar accuracy, and no amount of cleverness in
choosing labels will change that.</p>

<p>Two consequences follow, and they are the practical value of having done the SHAP analysis rather than just
asserting the point. The first is a safety argument. Because the shared core is stable, a laboratory can
monitor it. If next quarter's model suddenly stops using 2150 to 2156 Da for <i>E. coli</i>, something has
changed in the instrument or the population, and that is a signal to check before trusting the output. The
second is a limit on the claim. <i>K. pneumoniae</i> has no stable core to monitor, so that pair does not
support this kind of oversight, and we say so rather than averaging the three pairs into a comfortable
number.</p>

<p>We deliberately do not name proteins. The low mass region where most of the core sits is crowded, several
known markers fall within a few daltons of each other, and a 3 Da bin cannot separate them. Matching these
masses to proteins requires targeted confirmation that is outside what this study can support.</p>
"""

LOG = q(7, "The selection log, and what uncertainty sampling actually bought") + """
<p class="noind">The question as put was how we know that uncertainty sampling picked fully resistant
isolates. The log shows that it did not, and that this is the correct behaviour rather than a fault. The
reasoning is worth following because it changes what the method is understood to be for.</p>

<h3><span class="num">7.1</span>What is in the log</h3>
<p class="noind">Every run was replayed with the same seeds and the same code path, recording one line for
every isolate the model scored in every round. The replay produced 19248 decisions over 12 runs, which is
three species and drug pairs by four strategies, at 400 labels and seed 0, across four quarterly rounds. Each
line carries the isolate code, the predicted probability of resistance, the decision threshold in force that
round, the distance between the two, the isolate's rank by that distance, whether it was bought, its true
label from DRIAMS, and what the model would have reported without a test. The files are
<i>selection_log.csv</i>, a per round summary in <i>selection_summary.csv</i>, and the fifteen isolates
closest to the threshold in each uncertainty run in <i>selection_examples_uncertainty.csv</i>.</p>

<h3><span class="num">7.2</span>Uncertainty sampling buys fewer resistant isolates, not more</h3>
<table class="bt">
<thead><tr><th>Species and drug</th><th class="n">Resistant in<br>the stream</th>
<th class="n">Random<br>bought</th><th class="n">Uncertainty<br>bought</th>
<th class="n">Distance,<br>bought</th><th class="n">Distance,<br>left</th></tr></thead>
<tbody>
<tr><td><i>E. coli</i>, ceftriaxone</td><td class="n">22.2%</td><td class="n">21.5%</td>
    <td class="n">17.2%</td><td class="n">0.0076</td><td class="n">0.0307</td></tr>
<tr><td><i>K. pneumoniae</i>, ceftriaxone</td><td class="n">14.2%</td><td class="n">17.0%</td>
    <td class="n">10.2%</td><td class="n">0.0047</td><td class="n">0.0118</td></tr>
<tr><td><i>S. aureus</i>, oxacillin</td><td class="n">18.8%</td><td class="n">15.8%</td>
    <td class="n">12.8%</td><td class="n">0.0125</td><td class="n">0.0272</td></tr>
</tbody></table>
""" + tcap(6, "What each rule bought at 400 labels, seed 0, summed over the four rounds. The last two "
              "columns are the median distance to the decision threshold among the isolates uncertainty "
              "sampling bought and among those it left alone.") + f("03_Logs/selection_summary.csv") + """

<p>Random selection buys resistant isolates at roughly the rate they arrive, as it must. Uncertainty sampling
buys them at a lower rate on all three pairs. The mechanism is in the last two columns: the isolates it buys
sit two to four times closer to the decision threshold than those it skips, and an isolate the model is
confident is resistant is by definition far from that threshold. Confident resistance is exactly what
uncertainty sampling declines to pay for.</p>

<p>So the premise of the question does not hold, and it should not. Buying an isolate the model already calls
resistant teaches the model nothing and spends a test that could have gone elsewhere. The rule is not a
resistance detector. It is a rule for finding the cases the model is about to get wrong.</p>

<h3><span class="num">7.3</span>What it does find</h3>
<p class="noind">The clearest single line in the log is from the <i>K. pneumoniae</i> run, round one. The
threshold that round was 0.013587. The isolate ranked second closest to it, code
<i>ad840636-42d1-4740-a017-74174683b774</i>, had a predicted probability of 0.013468, which is 0.000118 below
the threshold. The model would have reported it susceptible. It was in fact resistant. Uncertainty sampling
bought it. Random selection would have had roughly one chance in three of doing the same, since it
draws 100 tests from the 305 isolates that arrived that round.</p>

<p>That is the whole method in one isolate. Across the full log, counting resistant isolates left untested
that the model would have reported susceptible, uncertainty sampling leaves fewer than random does on every
pair: 67 against 74 for <i>E. coli</i>, 31 against 36 for <i>K. pneumoniae</i>, and 34 against 49 for
<i>S. aureus</i>. It gets there while buying fewer resistant isolates in total, which is only possible because
the ones it buys are the ones near the line.</p>

<p>Anyone can check this. Open <i>selection_log.csv</i>, filter to one job and one round, sort by
<i>distance_to_threshold</i>, and the rows with <i>sent_for_testing</i> true will be exactly the first 100.
Our own test suite asserts that property on every run rather than comparing averages, so a rule that merely
tended towards the threshold would fail the check.</p>
"""

DATA = q(8, "The dataset") + """
<p class="noind">The study uses DRIAMS, a public collection of MALDI-TOF mass spectra with matched
susceptibility results from four Swiss hospitals, released on Dryad under CC0. CC0 is a waiver of copyright
rather than a licence with conditions, so the spectra can be redistributed and reanalysed without permission
or attribution requirements, though we cite the source paper as a matter of practice. Nothing in the folder is
restricted and no patient identifiers are present; isolates carry opaque codes assigned by the original
depositors.</p>

<p>Each spectrum is preprocessed to a fixed vector of 6000 numbers. Bin <i>i</i> covers 2000 plus 3<i>i</i>
daltons up to 2003 plus 3<i>i</i>, so the whole range from 2000 to 20000 Da is divided into 3 Da steps. That
mapping is what turns a bin index in the SHAP tables into a mass.</p>

<p>Two things are supplied rather than one. The first is <i>isolate_manifest.csv</i>, which lists all 18487
isolates the study touches, one row each, with the species, the antibiotic, the hospital, the year, which
split it fell into under seed 0, which quarterly arrival batch if it was in the pool, and its label. This is
the file to use for checking that the splits are what the paper claims. Resistant and intermediate are both
coded as 1 and susceptible as 0, following the DRIAMS convention; the manifest spells that out in a column
rather than leaving it to be inferred.</p>

<p>The second is the spectra themselves, 244 MB, cut down to only the three species and drug pairs in the
study. The full DRIAMS release is far larger and most of it is irrelevant here. Anyone wanting the original can
take it from Dryad at doi 10.5061/dryad.bzkh1899q; the subset here is a convenience, not a substitute.</p>

<p>The folder also carries the code that produced everything, in 06_Code, including the module that writes the
selection log and the one that computes the SHAP values. The results in 04_Results are the tables and figures
of the paper plus the raw per run records in JSON, so any number in any table can be traced back to the run
that produced it.</p>
"""

CLOSE = q(9, "Summary") + """
<p class="noind">Active learning and traditional retraining give the same accuracy here because the gap
between never retraining and retraining on everything is only four to five points of AUROC, and no selection
rule can manufacture a difference larger than the margin it is competing for. This was checked across 45
paired comparisons at four hospitals and holds in the cross site setting too, so it is a property of the
problem rather than of this dataset. The result that is worth reporting is the price: roughly a third of a
year's susceptibility tests recovers between a half and three quarters of the benefit of testing everything.
The SHAP analysis explains why the rules tie, since all six models converge on the same small set of spectral
bins, and it also supplies something a laboratory can monitor over time, on two of the three pairs. The
selection log answers the audit question directly and overturns its premise: uncertainty sampling buys fewer
resistant isolates than random, yet leaves fewer resistant isolates misreported, because it spends its budget
at the decision boundary rather than on cases the model already has right.</p>
"""


def build():
    html = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            "<title>Replies to the review questions</title>"
            f"<style>{CSS}</style></head><body>"
            + FRONT + MAP + SHAP + SAME + COST + FEAT + WHY + LOG + DATA + CLOSE +
            "</body></html>")
    open(S + "answers.html", "w").write(html)
    print("wrote answers.html", len(html) // 1024, "KB")


if __name__ == "__main__":
    build()
