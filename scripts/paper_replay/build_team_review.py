"""Build a commentable team review proposal from the existing candidate inventory."""
import json
from pathlib import Path
from collections import Counter
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'artifacts/paper_replay'

# Draft review choices, not extracted or independently adjudicated answer keys.
# Each row: short name; selection reason; outcome-free question; screen issue;
# distinguishing design; required evidence; scoped verdict proposal; follow-up.
DATA = {
'qml-01': ('Quantum feature spaces', 'Tests whether a hardware demonstration is mistaken for learning advantage.', 'Can a quantum feature-map kernel improve classification on a specified distribution?', 'Kernel concentration, bandwidth and classical approximation.', 'Compare tuned classical kernels and approximations across data and circuit sizes.', 'Accuracy, kernel spectra and variance, tuning budgets, shots and noise.', 'Separate demonstrated classification from unestablished general advantage; apply concentration limits only in their stated regime.', 'Test structured feature maps that avoid concentration.'),
'qml-02': ('Quantum convolutional networks', 'Tests whether simulability limits are applied without discarding quantum-data results.', 'Can a hierarchical quantum circuit classify phases with few parameters and favorable sample cost?', 'Low-bodyness simulability versus quantum state acquisition.', 'Compare QCNN, local-observable and classical simulation methods at matched acquisition cost.', 'Phase labels, sample counts, observables, circuit sizes and simulator accuracy.', 'Preserve phase-recognition results; restrict advantage claims in classically simulable regimes.', 'Probe inputs outside the locally easy regime.'),
'qml-03': ('Quantum recommendation', 'Provides a clear test of dequantization under comparable input access.', 'Does a quantum recommendation algorithm reduce cost under specified matrix-access assumptions?', 'QRAM versus classical sampling/query access and output costs.', 'Compare quantum and classical recommendation complexity under the same access, error and preprocessing assumptions.', 'Theorem assumptions, complexity bounds, accuracy and data-structure costs.', 'Algorithm correctness can survive while exponential separation fails under matched sampling access.', 'Change the access model and identify whether a separation remains.'),
'qml-04': ('Quantum PCA', 'Tests whether quantum-input and classical-input claims remain distinct.', 'Can principal components of a low-rank state be estimated efficiently?', 'Copies of quantum states versus classical sampling access.', 'Analyze estimation error and copy complexity separately from classical-data preparation costs.', 'Rank, spectral gaps, access assumptions, output type and approximation bounds.', 'Limit classical-data speedup claims; do not transfer that conclusion to an unmatched quantum-state input model.', 'Study genuinely quantum states with costly classical descriptions.'),
'qml-05': ('Data re-uploading', 'Separates mathematical expressivity from benchmark competitiveness.', 'Can repeated data encoding yield a universal classifier and useful predictive performance?', 'Universality does not establish advantage over tuned classical models.', 'Separate proof checks from repeated-seed comparisons with tuned classical baselines.', 'Approximation assumptions, dataset splits, accuracies, tuning budgets and seed variation.', 'Universality may stand independently of weak or mixed empirical competitiveness.', 'Test a structured dataset with a justified classical bottleneck.'),
'qml-06': ('Power of data', 'Tests whether a positive result is preserved within its engineered-data scope.', 'When does geometric difference permit a projected quantum kernel to improve prediction?', 'Constructed-label dependence and limitations of the comparator set.', 'Compare high- and low-geometric-difference datasets with matched classical kernels.', 'Dataset construction, geometric differences, predictive errors and baseline tuning.', 'Support the demonstrated engineered-data result only if matched evidence confirms it; broader usefulness remains open.', 'Test non-engineered datasets and stronger kernel approximations.'),
'qml-07': ('Rigorous supervised speedup', 'A positive theoretical case tests rejection based solely on impractical hardware.', 'Can a kernel learner solve a discrete-log-based task efficiently under a stated hardness assumption?', 'Formal separation versus NISQ feasibility; do not conflate them.', 'Check the reduction, noise tolerance, learner complexity and classical hardness assumption.', 'Theorem statements, proof dependencies and end-to-end complexity.', 'A conditional formal separation may be supported without a useful near-term implementation.', 'Quantify realistic resource requirements separately.'),
'qml-08': ('Barren plateaus', 'A rigorous negative theorem tests whether scope survives broad generalization.', 'How does gradient variance scale for circuits approaching a specified random ensemble?', 'Randomness, circuit depth, locality and cost-function assumptions.', 'Measure gradient variance versus size for random and structured circuits with local and global costs.', 'Variance scaling, ensemble definitions, sampling uncertainty and proof conditions.', 'Support exponential suppression in the covered regime; do not reject all variational circuits.', 'Test structured circuits or local costs outside that regime.'),
'qml-09': ('Classical shadows', 'A positive measurement result tests preservation of observable-specific sample benefits.', 'Can randomized quantum measurements estimate many specified observables efficiently?', 'Shadow norms and locality determine cost; logarithmic dependence alone is insufficient.', 'Vary observable count and locality; compare shadow estimation with direct measurement at matched error.', 'Shot counts, estimation errors, confidence coverage and observable norms.', 'Support scoped estimation guarantees; an experimental instance alone does not verify all scaling claims.', 'Test difficult observables and noise-robust estimators.'),
'qml-10': ('Learning from experiments', 'Adds a positive quantum-learning claim with an explicit uncertainty about independent confirmation.', 'Can quantum memory reduce experiment counts for a specified learning task?', 'Sample-complexity advantage versus runtime advantage.', 'Compare quantum-memory and classical-memory protocols under the same task and error target.', 'Task definitions, sample counts, prediction errors, hardware results and theorem assumptions.', 'Preserve any established task-specific sample advantage; independent replication and runtime advantage are separate questions.', 'Design an independent replication with matched information access.'),
'qc-01': ('Sycamore sampling', 'Tests correction of a classical cost estimate without erasing hardware achievements.', 'How costly is matching a random-circuit sampler at a specified fidelity?', 'Exact versus approximate sampling, verification strength and hardware accounting.', 'Compare best samplers at matched fidelity, circuit instances and full compute cost.', 'Circuit specs, fidelity tests, classical time/memory and hardware sampling rates.', 'Revise the historical cost estimate when comparable classical evidence warrants it; preserve hardware results.', 'Strengthen validation against approximate spoofing.'),
'qc-02': ('IBM utility experiment', 'Tests whether improved simulation narrows an advantage claim while leaving mitigation evidence intact.', 'Can error mitigation estimate observables of a large kicked-Ising circuit accurately?', 'Observable-specific classical simulation versus brute-force simulation.', 'Compare tensor-network and other simulators with mitigated estimates at matched observable error.', 'Observable curves, uncertainty, mitigation overhead and simulator convergence.', 'Preserve validated mitigation accuracy; beyond-classical usefulness requires stronger matched evidence.', 'Identify observables or regimes where classical convergence fails.'),
'qc-03': ('Photonic sampling', 'Tests whether benchmark spoofing is confused with exact-sampling dequantization.', 'Can a photonic sampler generate a specified Gaussian-boson distribution beyond classical rates?', 'Passing finite validation tests is different from matching the full distribution.', 'Compare classical approximations using stronger held-out distributional tests and equal cost.', 'Photon losses, sample tests, validation statistics and approximation costs.', 'Weaken claims licensed only by spoofable tests; do not infer that exact sampling hardness is disproved.', 'Add discriminating validation tests.'),
'qc-04': ('Annealing dynamics', 'A disputed claim tests calibrated disagreement rather than forced agreement with one side.', 'Can an annealer reproduce spin-glass dynamics outside a declared classical accuracy budget?', 'Matched observables, regimes, errors and competing simulation methods.', 'Reconcile both sides on identical instances, observables and tolerance.', 'Original and challenge results, convergence checks, replies and unmatched regimes.', 'Record supported subclaims and unresolved comparisons; no mandatory winner before adjudication.', 'Run the cheapest comparison that resolves the remaining mismatch.'),
'qc-05': ('Finite-range tunneling', 'Tests a large gain against a weak comparator.', 'Does quantum annealing improve time to solution for weak-strong cluster instances?', 'Simulated annealing is not the strongest available classical solver.', 'Compare multiple classical solvers using matched success probability, tuning and instance families.', 'Runtime distributions, success probabilities, preprocessing and tuning costs.', 'Preserve a gain against the named comparator; do not infer advantage over all classical methods.', 'Test less tailored instances against the strongest solver.'),
'qc-06': ('HHL linear systems', 'Tests an important theorem with restrictive input and output assumptions.', 'Can a quantum algorithm prepare a solution state for sparse, well-conditioned linear systems efficiently?', 'State preparation, condition number, precision and readout.', 'Account for the full task cost; compare observable estimation and full-vector output separately.', 'Access model, sparsity, conditioning, error bounds and output requirements.', 'Preserve the conditional algorithmic result; reject an unsupported full classical-vector speedup.', 'Study quantum-native inputs and limited-observable outputs.'),
'qc-07': ('Loophole-free Bell tests', 'An established positive quantum result tests unnecessary rejection and shared-component awareness.', 'Can a separated entangled system violate a Bell inequality with key loopholes closed?', 'Detection, locality, setting randomness and valid sequential statistics.', 'Specify event selection, timing, random settings and a valid hypothesis test before inspection.', 'Trial-level events, timing, setting records, test statistics and independent experiments.', 'Support a violation under tested assumptions; record shared random-generator dependencies.', 'Replicate with independently implemented setting generation.'),
'qc-08': ('Below-threshold error correction', 'A positive QEC case tests the distinction between logical suppression and usable fault tolerance.', 'Does logical error decrease as surface-code distance increases under a fixed operating regime?', 'Decoder comparability, correlated errors and resource overhead.', 'Compare code distances using matched decoding and cycle definitions; test rare error bursts.', 'Logical error rates and uncertainty, distances, cycles, decoder costs and correlations.', 'Support demonstrated suppression if the packet warrants it; do not infer complete fault tolerance or replication.', 'Test longer runs and independently replicated scaling.'),
'qc-09': ('Logical neutral-atom processor', 'Adds a hardware success relevant to neutral-atom work while testing postselection accounting.', 'Can encoded neutral-atom circuits improve task fidelity over physical-qubit implementations?', 'Postselection acceptance, error detection versus correction and comparator fairness.', 'Compare logical and physical circuits at matched tasks while charging discarded shots.', 'Circuit fidelities, acceptance rates, resource counts and logical error detection.', 'Support the demonstrated encoded regime; do not equate postselected detection with fault-tolerant correction.', 'Reduce postselection cost or demonstrate active correction.'),
'phys-01': ('Majorana conductance', 'Tests whether retraction and data-selection problems invalidate a mechanism inference.', 'Can conductance measurements distinguish Majorana modes from alternative explanations?', 'Selective data presentation and non-unique conductance signatures.', 'Require full sweeps, alternative-model controls and robust criteria for the plateau.', 'Unselected conductance data, processing history, retraction notice and competing explanations.', 'The retracted evidence cannot establish the mechanism; this does not refute every Majorana hypothesis.', 'Acquire independently controlled spectroscopy.'),
'phys-02': ('LK-99 superconductivity', 'Tests extraordinary-claim validation and alternative explanations for apparent success.', 'Does a specified synthesized material exhibit ambient-pressure room-temperature superconductivity?', 'Impurities and magnetism can mimic individual signatures.', 'Measure resistivity, magnetic response and composition with independent synthesis controls.', 'Transport curves, magnetic measurements, phase analysis and independent synthesis reports.', 'Do not accept the claim from isolated signatures; freeze a final negative label only after sourcing the relevant replications.', 'Test purified samples and impurity controls.'),
'phys-03': ('Neural quantum states', 'A positive computational-physics case tests fair numerical benchmarking.', 'Can a neural variational wavefunction approximate spin-model ground states accurately?', 'Matched ansatz resources, optimization reliability and finite-size scope.', 'Compare energies and observables with exact and strong variational methods on tractable sizes.', 'Model definitions, energies, reference values, optimization seeds and convergence.', 'Support accuracy only for tested models and tolerances; broader superiority needs stronger evidence.', 'Probe difficult regimes and independently benchmark convergence.'),
'phys-04': ('Rydberg revivals', 'Tests preservation of an anomalous observation before a mechanism is established.', 'Does a constrained Rydberg chain retain coherent revivals for specified initial states?', 'An observed revival alone does not prove a scar mechanism.', 'Compare initial states, detunings, chain sizes and decoherence controls.', 'Population dynamics, revival metrics, errors and later theoretical explanations.', 'Support the observed revivals; distinguish original evidence from later mechanism support.', 'Test scar-specific predictions on new states.'),
'phys-05': ('Gravitational waves', 'An externally reanalyzed success tests statistical and instrumental scrutiny without reflexive rejection.', 'Does a detector transient match a binary-black-hole gravitational-wave signal?', 'Background estimation, instrumental artifacts and shared calibration.', 'Compare matched-filter pipelines, off-source backgrounds and detector coincidence.', 'Strain data, calibration, signal-to-noise, false-alarm estimates and reanalysis.', 'Support detection if statistical and instrumental checks hold; keep source inferences within their uncertainty.', 'Reanalyze with alternative waveform and noise assumptions.'),
'ml-01': ('Neural collaborative filtering', 'A clear weak-baseline example tests tuned comparator selection.', 'Does an MLP interaction improve implicit-feedback recommendation over matrix factorization?', 'Tuning, sampled evaluation and information-access equality.', 'Compare tuned matrix factorization and MLP on identical splits and ranking metrics.', 'Ranking scores, negatives, splits, hyperparameter searches and repeated runs.', 'Limit the superiority claim if tuned factorization matches or exceeds it; retain the implemented model.', 'Test non-dot-product tasks with matched tuning.'),
'ml-02': ('TabNet', 'Tests whether tabular neural gains persist against strong tree baselines.', 'Can an attentive tabular network improve prediction and useful feature selection?', 'Dataset selection, tuning budgets and interpretation claims.', 'Compare tuned tree and neural models on diverse shared splits; test feature-selection fidelity separately.', 'Per-dataset scores, search budgets, seeds and feature-selection checks.', 'Avoid blanket superiority; specify datasets and comparisons where evidence supports a gain.', 'Identify a reproducible regime where attention helps.'),
'ml-03': ('Batch normalization', 'Separates a successful method from its proposed causal explanation.', 'Does batch normalization improve training, and is reduced covariate shift the cause?', 'Performance improvement and mechanism need different tests.', 'Measure training gains and manipulate covariate shift while controlling optimization settings.', 'Training curves, covariate-shift measures, ablations and controls.', 'Preserve demonstrated training gains while questioning the proposed mechanism when counterevidence warrants it.', 'Test alternative optimization explanations.'),
'ml-04': ('Graph isomorphism networks', 'Separates an expressivity theorem from empirical benchmark margins.', 'Can a graph network match WL expressivity and improve graph classification?', 'Formal distinguishability differs from predictive generalization.', 'Check theorem assumptions and compare graph models with structure-agnostic controls.', 'Proof assumptions, graph splits, tuned scores and structure-agnostic baselines.', 'Preserve a valid expressivity theorem while limiting empirical superiority to fair comparisons.', 'Test graphs that specifically require structural distinctions.'),
'ml-05': ('Multi-similarity loss', 'Tests retrieval claims under equalized training protocols.', 'Does multi-similarity training improve metric-learning retrieval?', 'Backbone, sampling, splits and tuning can explain reported margins.', 'Hold the pipeline fixed and vary only the loss with matched searches and seeds.', 'Recall scores, split policy, backbones, samplers and training budgets.', 'Do not credit the loss with gains explained by protocol differences; verify inclusion in the external benchmark.', 'Test genuinely loss-sensitive regimes.'),
'ml-06': ('WGAN gradient penalty', 'Tests whether tuning effort is mistaken for objective superiority.', 'Does gradient-penalized Wasserstein training improve GAN stability and quality?', 'Tuning budget and metric choice can confound objective comparisons.', 'Compare objectives under equal searches and repeated seeds; measure collapse separately from quality.', 'Quality metrics, failure rates, searches, seeds and compute budgets.', 'Restrict universal quality claims; evaluate stability as a distinct supported or unresolved claim.', 'Test stability under deliberately limited tuning budgets.'),
'ml-07': ('Reinforcement-learning NAS', 'Tests whether architecture gains survive equal tuning and search accounting.', 'Can a searched recurrent cell improve language modeling relative to LSTM?', 'Comparator tuning and architecture-search compute.', 'Tune both architectures comparably and include search cost in efficiency metrics.', 'Perplexities, seeds, regularization settings and full search/training costs.', 'Reject a superiority claim unsupported against a well-tuned LSTM; preserve the search procedure itself.', 'Test search gains under a fixed total compute budget.'),
'ml-08': ('Residual networks', 'A pivotal success tests preservation of a result with appropriate controls.', 'Do residual connections improve optimization and accuracy of deep image classifiers?', 'Residual connection effects versus other training improvements.', 'Compare plain and residual networks at equal depth and recipe; separate later training tricks.', 'Optimization curves, validation error, depths, training settings and reproductions.', 'Support depth-specific optimization and accuracy gains if controlled evidence warrants them; a later ResNet result alone is not a causal replication.', 'Test the contribution at new depths and matched recipes.'),
'ml-09': ('AlphaFold', 'A blind external assessment provides a strong positive calibration case.', 'Can a structure predictor achieve high accuracy on unseen protein targets?', 'Target leakage, per-target variability and limits beyond static structures.', 'Use blind targets and compare assessors\' structural metrics against appropriate methods.', 'CASP target-level scores, target definitions, coverage and assessor reports.', 'Support high accuracy on assessed targets; do not imply universal accuracy or complete biological function prediction.', 'Test failure modes and distribution shifts.'),
'ml-10': ('Transformer', 'A pivotal independently implemented method provides a positive case and perturbation parent.', 'Can an attention-only encoder-decoder improve translation quality and training efficiency?', 'BLEU comparability, tokenization and hardware-dependent cost.', 'Compare strong translation models under matched preprocessing, scoring and resource accounting.', 'BLEU scores, evaluation scripts, training costs, seeds and reimplementation.', 'Support the reported translation regime when evidence matches; do not infer superiority on every sequence task.', 'Test robustness to changed sequence length or data budget.'),
'ml-11': ('BERT', 'Preserves pretraining gains while isolating an unsupported component claim.', 'Does masked-language pretraining improve downstream language tasks, and does sentence prediction help?', 'Training duration, data and sentence-objective effects are entangled.', 'Ablate sentence prediction with matched tokens, data and downstream evaluation.', 'Task scores, compute/data budgets, ablations and replication settings.', 'Support scoped pretraining gains; assess sentence-prediction contribution separately.', 'Test objective changes under matched training budgets.'),
'ml-12': ('Language model scaling', 'A mixed pivotal case tests revision of one claim while preserving another.', 'How should parameters and tokens scale under a fixed language-model training budget?', 'Power-law fit and compute-optimal allocation are distinct claims.', 'Sweep parameter/token allocations at fixed compute and test held-out predictions.', 'Loss curves, allocation grids, fit uncertainty and external reevaluation.', 'Preserve supported scaling patterns while revising the allocation rule where matched evidence warrants it.', 'Test scaling predictions at new budgets and data regimes.'),
}

CONTRACTS = [
('Intake', 'I0: the outcome-free question below.', 'Scoped claim, regime, assumptions and falsifier.'),
('Screen analyst', 'I1: reviewed scope + allowed literature.', 'Interpret the case-specific issue; request decisive missing evidence.'),
('Literature retrieval', 'I2: research request + dated corpus.', 'Find relevant predecessors, strongest comparators and accurately described challenges.'),
('Prereg / designer', 'I3: curated scope, literature and budget.', 'A discriminating plan with controls, useful-effect criteria and outcome interpretations.'),
('Baseline champion', 'I4: task/access definition + plan.', 'A strong comparator under matched information, error and compute assumptions.'),
('Review panel', 'I5: plan, or results before verdict.', 'Identify material flaws and repairs without blocking sound work.'),
('Run / implementer', 'I6: frozen plan + data/code/environment.', 'Correct metrics, validity checks and provenance; full execution only where reproducible.'),
('Verdict', 'I7: methods + evidence packet, no answer key.', 'A licensed, claim-specific conclusion with scope and uncertainty.'),
('Audit', 'I8: proposed verdict + underlying evidence.', 'Verify decisive facts and independently recompute available numbers.'),
('Variants', 'I9: adjudicated result + budget.', 'A changed assumption and cheapest discriminating follow-up.'),
('Promote', 'I10: approved, audited source + disposable workspace.', 'Faithful scoped record and links; no production exclusions.'),
('Lab orchestration', 'I11: stage state, approvals and budgets.', 'Valid handoffs, honest blocked states and reproducible logs.'),
]

def url(s):
    return 'https://arxiv.org/abs/'+s['arxiv'] if 'arxiv' in s else 'https://doi.org/'+s['doi']

def rows(c):
    x=DATA[c['id']]
    formal=c['profile']=='formal'
    run='Check proof dependencies and small numerical examples; no numerical result can certify the theorem.' if formal else 'Recompute a tractable subset of '+x[5].split(',')[0].lower()+'. If raw data/code are absent, mark execution blocked.'
    return [
      ('Intake','I0', 'Scope: '+x[2]),
      ('Screen analyst','I1', x[3]),
      ('Literature retrieval','I2', 'Find pre-cutoff predecessors and strong comparators; in current mode, retrieve the sources below if decisive.'),
      ('Prereg / designer','I3',x[4]),
      ('Baseline champion','I4', 'Implement or justify the strongest comparator in the design, with matched access, error and budget.'),
      ('Review panel','I5', 'Challenge '+x[3][0].lower()+x[3][1:]+' Name a repair, or explain why the control is adequate.'),
      ('Run / implementer','I6',run),
      ('Verdict','I7',x[6]),
      ('Audit','I8','Check the decisive comparison/proof against sources and '+x[5].split(',')[0].lower()+'. Flag evidence that cannot be recomputed.'),
      ('Variants','I9',x[7]),
      ('Promote','I10','Preserve this verdict\'s exact scope, uncertainty and provenance in a disposable record.'),
      ('Lab orchestration','I11','Request required approvals; stop honestly at missing evidence, state, code or hardware.'),
    ]

def build():
    seed=json.loads((OUT/'candidate_seed.json').read_text(encoding='utf-8'))
    candidates=sorted(seed['candidates'],key=lambda c: (['qml','qc','physics','ml'].index(c['domain']),int(c['id'].split('-')[1])))
    assert set(DATA)=={c['id'] for c in candidates}
    doc=Document()
    sec=doc.sections[0]
    sec.page_height=Inches(11.7); sec.page_width=Inches(8.3)
    sec.top_margin=sec.bottom_margin=Inches(.6)
    sec.left_margin=sec.right_margin=Inches(.65)
    for name in ['Normal','Title','Subtitle','Heading 1','Heading 2','Heading 3']:
        sty=doc.styles[name]; sty.font.name='Calibri'; sty.font.color.rgb=RGBColor(0,0,0)
        for border in list(sty.element.iter(qn('w:pBdr'))):
            border.getparent().remove(border)
    doc.styles['Normal'].font.size=Pt(10)
    doc.styles['Normal'].paragraph_format.space_after=Pt(4)
    doc.styles['Title'].font.size=Pt(23)
    doc.styles['Heading 1'].font.size=Pt(17)
    doc.styles['Heading 2'].font.size=Pt(13)
    footer=sec.footer.paragraphs[0]; footer.alignment=2
    footer.add_run('Team review draft  |  ')
    field=OxmlElement('w:fldSimple'); field.set(qn('w:instr'),'PAGE'); footer._p.append(field)
    md=[]
    def para(t,style=None):
        doc.add_paragraph(t,style); md.append(t+'\n')
    def heading(t,level=1):
        doc.add_heading(t,level); md.append('#'*level+' '+t+'\n')
    def table(headers, data, widths=None, font=9.5):
        t=doc.add_table(rows=1,cols=len(headers)); t.style='Table Grid'; t.autofit=False
        md.append('| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |')
        for cell,h in zip(t.rows[0].cells,headers): cell.text=h
        hprop=t.rows[0]._tr.get_or_add_trPr(); rep=OxmlElement('w:tblHeader'); hprop.append(rep)
        for vals in data:
            cells=t.add_row().cells
            for cell,txt in zip(cells,vals): cell.text=str(txt)
            md.append('| '+' | '.join(str(v).replace('|','/').replace('\n',' ') for v in vals)+' |')
        for idx,row in enumerate(t.rows):
            prop=row._tr.get_or_add_trPr(); no=OxmlElement('w:cantSplit');prop.append(no)
            for j,cell in enumerate(row.cells):
                if widths: cell.width=Inches(widths[j])
                for p in cell.paragraphs:
                    p.paragraph_format.space_after=Pt(3);p.paragraph_format.space_before=Pt(2)
                    for r in p.runs: r.font.size=Pt(font);r.bold=idx==0
                if idx==0:
                    sh=OxmlElement('w:shd');sh.set(qn('w:fill'),'E8EEF3');cell._tc.get_or_add_tcPr().append(sh)
        md.append('')
    def br(): doc.add_page_break()

    para('Paper replay candidate review','Title')
    para('For Tsahi, Adi and Meir  |  13 October 2026','Subtitle')
    para('Review which papers we should use to evaluate the lab, what each component receives, and what a good output should contain. The 36 candidates below are proposals. No paper-based packet or expected answer here has been independently adjudicated.')
    heading('What to review')
    para('Comment on any candidate title or component row using its ID, for example qml-03 / Verdict. Mark KEEP, CHANGE or DROP, and give a correction or source passage. Review the scientific expectation before implementation details.')
    para('For each card, decide: Is this claim worth testing? Is the input sufficient and free of outcomes? Is the expected conclusion fair? Which table, figure, theorem or review passage should establish the answer?')
    heading('How to read the cards')
    para('The overview gives one selection reason per paper. Each card then gives an outcome-free question, required evidence and expected outputs for all components. I0–I11 refer to the shared input contracts on the next page; each component receives curated upstream material, so an earlier failure cannot contaminate its score.')
    para('Historical mode: intake, retrieval and design see only sources available before the target paper. Later challenges are evaluator-only. Current mode: the target and follow-up papers may be visible; the task is critique, not rediscovery. Card verdicts propose current evidence assessment; a separate historical key must be written.')
    heading('Important limits')
    para('All expected outputs are review proposals, not gold labels. Source links come from the existing inventory; this document does not claim a new full-text review. Famous papers can be memorized, so use them as development cases and perturbation parents. No clean holdout is established here.')
    para('Positive results, negative results and conditional limitations all matter. A valid theorem or physics observation need not establish near-term commercial quantum advantage. We will score those claims separately.')
    para('Do not force non-QML cases through QML hardware or commercial gates. Formal, physics and classical-ML profiles need explicit adapters; these cards describe target responsibilities, not proof that native skills accept the inputs.')
    heading('How non-QML cases are used')
    para('Our lab criteria assume one claim type: a quantum method beats classical alternatives at industrial scale on real data. A classical or physics paper gives the classical-twin, hardware, readout and scale checks nothing to act on. The same is true of some quantum and physics cards: qml-07, qml-10, qc-07 and phys-04 are formal, foundational or observational claims, not advantage claims.')
    para('We therefore score in two layers. The general layer (N1–N5, evidence class, scope, claim-level splitting, matched resources, baseline adequacy) applies to every card. The QML layer (the five domain criteria, classical twin, hardware fit, readout cost, industrial operating point) applies only to advantage-type quantum claims; elsewhere it is N/A, never a failure.')
    para('Non-QML cards are kept when they test the general reasoning behind a lab rule:')
    table(['Lab rule','General form','Proxy cards'],[
        ('Criterion 5 / N1 baseline adequacy','A tuned strong baseline closes the claimed gap','ml-01, ml-02, ml-05, ml-07; qc-05'),
        ('Rule 4 matched constraints','Unequal tuning or compute budget produces the gap','ml-06, ml-07'),
        ('Rule 1 classical twin','A cheaper method with the same access gives the same answer','qc-01, qc-03; qml-03, qml-04'),
        ('N3 discriminating power','Data selection, or evidence that cannot separate explanations','phys-01, phys-02'),
        ('N4 mechanism named','Performance survives while the mechanism claim fails','ml-03, ml-11, phys-04'),
    ],[1.9,3.1,2.0],9.5)
    para('Non-QML cards test verdict, review panel, audit, baseline champion and design only. Full-pipeline and native intake/screen runs use quantum cards. Results are reported per domain and profile, never as one lab score, and no QML rule is loosened because of a non-QML failure.')
    para('Proposed first 12: about six quantum advantage-type claims, four classical-ML method-versus-baseline claims, and two formal or physics claims. ml-09, ml-10, ml-12 and phys-05 map to no lab rule and are heavily memorized; they are proposed as perturbation parents only. Mark DROP or CHANGE on their cards if you disagree, or name a mapping we missed.')
    br()
    heading('Shared component input contracts')
    para('I0 is written on each card. I1–I11 specify what must be assembled before a component test. None includes this document, the answer key, prestige or citation-count scores. Methods and evidence arrive only at the appropriate stage.')
    table(['Component','Given input','Expected artifact'],CONTRACTS,[1.2,2.5,3.3],9.5)
    para('Screen analyst + literature retrieval together test qml-screen and its research handoff. Prereg maps to qml-prereg; the other stage names map to qml-intake, qml-review-panel, qml-run, qml-verdict, qml-audit, qml-variants, qml-promote and qml-lab. Baseline champion is tested separately inside the design/execution workflow.')
    para('Execution/audit readiness is not established. Full-skill tests also need native state, approval records, retrospective benchmark locks, raw evidence and runnable code. If absent, mark BLOCKED or use an explicitly adapted interpretation test. Hardware experiments do not become local reproductions.')
    br()
    for domain,title in [('qml','Quantum machine learning'),('qc','Quantum computing'),('physics','Physics'),('ml','Classical machine learning')]:
        heading(title+' overview')
        cs=[c for c in candidates if c['domain']==domain]
        table(['ID and paper','Why selected'],[(c['id']+'  '+DATA[c['id']][0],DATA[c['id']][1]) for c in cs],[2.05,4.95],10)
        if domain in ('qc','ml'):
            para('Details follow in the candidate cards. Selection reasons describe evaluation value, not a validated answer key.')
            br()
    for idx,c in enumerate(candidates):
        x=DATA[c['id']]
        heading(c['id']+' '+x[0])
        para(c['original']['label'])
        para('Selected because: '+x[1])
        para('Given input I0: '+x[2])
        para('I7 evidence to assemble: '+x[5]+' Do not invent missing uncertainty, numerical values or preregistration.')
        table(['Component','Input','Expected output proposal'],rows(c),[1.2,.65,5.15],10)
        para('Original: '+url(c['original']))
        sources=c['adjudicators']
        para('External sources to check: '+('; '.join(a['label']+' — '+url(a) for a in sources) if sources else 'None identified in the inventory; external validation remains open.'))
        para('Review gap: '+c['notes'])
        para('Comment anchors: '+c['id']+' / Input · Screen · Design · Verdict · Sources. Verdicts and source relations remain provisional.')
        if idx<len(candidates)-1: br()
    doc.core_properties.title='Paper replay candidate review'
    doc.core_properties.subject='Team review of inputs and expected component outputs for 36 proposed evaluation cases'
    doc.save(OUT/'team_review_2026-10-13.docx')
    (OUT/'team_review_2026-10-13.md').write_text('\n'.join(md),encoding='utf-8')
    print('Built 36 candidate cards, all 12 component responsibilities per card. Draft expectations only.')

if __name__=='__main__': build()
