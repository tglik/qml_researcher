Paper replay candidate review

For Tsahi, Adi and Meir  |  13 October 2026

Review which papers we should use to evaluate the lab, what each component receives, and what a good output should contain. The 36 candidates below are proposals. No paper-based packet or expected answer here has been independently adjudicated.

# What to review

Comment on any candidate title or component row using its ID, for example qml-03 / Verdict. Mark KEEP, CHANGE or DROP, and give a correction or source passage. Review the scientific expectation before implementation details.

For each card, decide: Is this claim worth testing? Is the input sufficient and free of outcomes? Is the expected conclusion fair? Which table, figure, theorem or review passage should establish the answer?

# How to read the cards

The overview gives one selection reason per paper. Each card then gives an outcome-free question, required evidence and expected outputs for all components. I0–I11 refer to the shared input contracts on the next page; each component receives curated upstream material, so an earlier failure cannot contaminate its score.

Historical mode: intake, retrieval and design see only sources available before the target paper. Later challenges are evaluator-only. Current mode: the target and follow-up papers may be visible; the task is critique, not rediscovery. Card verdicts propose current evidence assessment; a separate historical key must be written.

# Important limits

All expected outputs are review proposals, not gold labels. Source links come from the existing inventory; this document does not claim a new full-text review. Famous papers can be memorized, so use them as development cases and perturbation parents. No clean holdout is established here.

Positive results, negative results and conditional limitations all matter. A valid theorem or physics observation need not establish near-term commercial quantum advantage. We will score those claims separately.

Do not force non-QML cases through QML hardware or commercial gates. Formal, physics and classical-ML profiles need explicit adapters; these cards describe target responsibilities, not proof that native skills accept the inputs.

# How non-QML cases are used

Our lab criteria assume one claim type: a quantum method beats classical alternatives at industrial scale on real data. A classical or physics paper gives the classical-twin, hardware, readout and scale checks nothing to act on. The same is true of some quantum and physics cards: qml-07, qml-10, qc-07 and phys-04 are formal, foundational or observational claims, not advantage claims.

We therefore score in two layers. The general layer (N1–N5, evidence class, scope, claim-level splitting, matched resources, baseline adequacy) applies to every card. The QML layer (the five domain criteria, classical twin, hardware fit, readout cost, industrial operating point) applies only to advantage-type quantum claims; elsewhere it is N/A, never a failure.

Non-QML cards are kept when they test the general reasoning behind a lab rule:

| Lab rule | General form | Proxy cards |
| --- | --- | --- |
| Criterion 5 / N1 baseline adequacy | A tuned strong baseline closes the claimed gap | ml-01, ml-02, ml-05, ml-07; qc-05 |
| Rule 4 matched constraints | Unequal tuning or compute budget produces the gap | ml-06, ml-07 |
| Rule 1 classical twin | A cheaper method with the same access gives the same answer | qc-01, qc-03; qml-03, qml-04 |
| N3 discriminating power | Data selection, or evidence that cannot separate explanations | phys-01, phys-02 |
| N4 mechanism named | Performance survives while the mechanism claim fails | ml-03, ml-11, phys-04 |

Non-QML cards test verdict, review panel, audit, baseline champion and design only. Full-pipeline and native intake/screen runs use quantum cards. Results are reported per domain and profile, never as one lab score, and no QML rule is loosened because of a non-QML failure.

Proposed first 12: about six quantum advantage-type claims, four classical-ML method-versus-baseline claims, and two formal or physics claims. ml-09, ml-10, ml-12 and phys-05 map to no lab rule and are heavily memorized; they are proposed as perturbation parents only. Mark DROP or CHANGE on their cards if you disagree, or name a mapping we missed.

# Shared component input contracts

I0 is written on each card. I1–I11 specify what must be assembled before a component test. None includes this document, the answer key, prestige or citation-count scores. Methods and evidence arrive only at the appropriate stage.

| Component | Given input | Expected artifact |
| --- | --- | --- |
| Intake | I0: the outcome-free question below. | Scoped claim, regime, assumptions and falsifier. |
| Screen analyst | I1: reviewed scope + allowed literature. | Interpret the case-specific issue; request decisive missing evidence. |
| Literature retrieval | I2: research request + dated corpus. | Find relevant predecessors, strongest comparators and accurately described challenges. |
| Prereg / designer | I3: curated scope, literature and budget. | A discriminating plan with controls, useful-effect criteria and outcome interpretations. |
| Baseline champion | I4: task/access definition + plan. | A strong comparator under matched information, error and compute assumptions. |
| Review panel | I5: plan, or results before verdict. | Identify material flaws and repairs without blocking sound work. |
| Run / implementer | I6: frozen plan + data/code/environment. | Correct metrics, validity checks and provenance; full execution only where reproducible. |
| Verdict | I7: methods + evidence packet, no answer key. | A licensed, claim-specific conclusion with scope and uncertainty. |
| Audit | I8: proposed verdict + underlying evidence. | Verify decisive facts and independently recompute available numbers. |
| Variants | I9: adjudicated result + budget. | A changed assumption and cheapest discriminating follow-up. |
| Promote | I10: approved, audited source + disposable workspace. | Faithful scoped record and links; no production exclusions. |
| Lab orchestration | I11: stage state, approvals and budgets. | Valid handoffs, honest blocked states and reproducible logs. |

Screen analyst + literature retrieval together test qml-screen and its research handoff. Prereg maps to qml-prereg; the other stage names map to qml-intake, qml-review-panel, qml-run, qml-verdict, qml-audit, qml-variants, qml-promote and qml-lab. Baseline champion is tested separately inside the design/execution workflow.

Execution/audit readiness is not established. Full-skill tests also need native state, approval records, retrospective benchmark locks, raw evidence and runnable code. If absent, mark BLOCKED or use an explicitly adapted interpretation test. Hardware experiments do not become local reproductions.

# Quantum machine learning overview

| ID and paper | Why selected |
| --- | --- |
| qml-01  Quantum feature spaces | Tests whether a hardware demonstration is mistaken for learning advantage. |
| qml-02  Quantum convolutional networks | Tests whether simulability limits are applied without discarding quantum-data results. |
| qml-03  Quantum recommendation | Provides a clear test of dequantization under comparable input access. |
| qml-04  Quantum PCA | Tests whether quantum-input and classical-input claims remain distinct. |
| qml-05  Data re-uploading | Separates mathematical expressivity from benchmark competitiveness. |
| qml-06  Power of data | Tests whether a positive result is preserved within its engineered-data scope. |
| qml-07  Rigorous supervised speedup | A positive theoretical case tests rejection based solely on impractical hardware. |
| qml-08  Barren plateaus | A rigorous negative theorem tests whether scope survives broad generalization. |
| qml-09  Classical shadows | A positive measurement result tests preservation of observable-specific sample benefits. |
| qml-10  Learning from experiments | Adds a positive quantum-learning claim with an explicit uncertainty about independent confirmation. |

# Quantum computing overview

| ID and paper | Why selected |
| --- | --- |
| qc-01  Sycamore sampling | Tests correction of a classical cost estimate without erasing hardware achievements. |
| qc-02  IBM utility experiment | Tests whether improved simulation narrows an advantage claim while leaving mitigation evidence intact. |
| qc-03  Photonic sampling | Tests whether benchmark spoofing is confused with exact-sampling dequantization. |
| qc-04  Annealing dynamics | A disputed claim tests calibrated disagreement rather than forced agreement with one side. |
| qc-05  Finite-range tunneling | Tests a large gain against a weak comparator. |
| qc-06  HHL linear systems | Tests an important theorem with restrictive input and output assumptions. |
| qc-07  Loophole-free Bell tests | An established positive quantum result tests unnecessary rejection and shared-component awareness. |
| qc-08  Below-threshold error correction | A positive QEC case tests the distinction between logical suppression and usable fault tolerance. |
| qc-09  Logical neutral-atom processor | Adds a hardware success relevant to neutral-atom work while testing postselection accounting. |

Details follow in the candidate cards. Selection reasons describe evaluation value, not a validated answer key.

# Physics overview

| ID and paper | Why selected |
| --- | --- |
| phys-01  Majorana conductance | Tests whether retraction and data-selection problems invalidate a mechanism inference. |
| phys-02  LK-99 superconductivity | Tests extraordinary-claim validation and alternative explanations for apparent success. |
| phys-03  Neural quantum states | A positive computational-physics case tests fair numerical benchmarking. |
| phys-04  Rydberg revivals | Tests preservation of an anomalous observation before a mechanism is established. |
| phys-05  Gravitational waves | An externally reanalyzed success tests statistical and instrumental scrutiny without reflexive rejection. |

# Classical machine learning overview

| ID and paper | Why selected |
| --- | --- |
| ml-01  Neural collaborative filtering | A clear weak-baseline example tests tuned comparator selection. |
| ml-02  TabNet | Tests whether tabular neural gains persist against strong tree baselines. |
| ml-03  Batch normalization | Separates a successful method from its proposed causal explanation. |
| ml-04  Graph isomorphism networks | Separates an expressivity theorem from empirical benchmark margins. |
| ml-05  Multi-similarity loss | Tests retrieval claims under equalized training protocols. |
| ml-06  WGAN gradient penalty | Tests whether tuning effort is mistaken for objective superiority. |
| ml-07  Reinforcement-learning NAS | Tests whether architecture gains survive equal tuning and search accounting. |
| ml-08  Residual networks | A pivotal success tests preservation of a result with appropriate controls. |
| ml-09  AlphaFold | A blind external assessment provides a strong positive calibration case. |
| ml-10  Transformer | A pivotal independently implemented method provides a positive case and perturbation parent. |
| ml-11  BERT | Preserves pretraining gains while isolating an unsupported component claim. |
| ml-12  Language model scaling | A mixed pivotal case tests revision of one claim while preserving another. |

Details follow in the candidate cards. Selection reasons describe evaluation value, not a validated answer key.

# qml-01 Quantum feature spaces

Havlicek et al. 2019, quantum-enhanced feature spaces

Selected because: Tests whether a hardware demonstration is mistaken for learning advantage.

Given input I0: Can a quantum feature-map kernel improve classification on a specified distribution?

I7 evidence to assemble: Accuracy, kernel spectra and variance, tuning budgets, shots and noise. Do not invent missing uncertainty, numerical values or preregistration.

| Component | Input | Expected output proposal |
| --- | --- | --- |
| Intake | I0 | Scope: Can a quantum feature-map kernel improve classification on a specified distribution? |
| Screen analyst | I1 | Kernel concentration, bandwidth and classical approximation. |
| Literature retrieval | I2 | Find pre-cutoff predecessors and strong comparators; in current mode, retrieve the sources below if decisive. |
| Prereg / designer | I3 | Compare tuned classical kernels and approximations across data and circuit sizes. |
| Baseline champion | I4 | Implement or justify the strongest comparator in the design, with matched access, error and budget. |
| Review panel | I5 | Challenge kernel concentration, bandwidth and classical approximation. Name a repair, or explain why the control is adequate. |
| Run / implementer | I6 | Recompute a tractable subset of accuracy. If raw data/code are absent, mark execution blocked. |
| Verdict | I7 | Separate demonstrated classification from unestablished general advantage; apply concentration limits only in their stated regime. |
| Audit | I8 | Check the decisive comparison/proof against sources and accuracy. Flag evidence that cannot be recomputed. |
| Variants | I9 | Test structured feature maps that avoid concentration. |
| Promote | I10 | Preserve this verdict's exact scope, uncertainty and provenance in a disposable record. |
| Lab orchestration | I11 | Request required approvals; stop honestly at missing evidence, state, code or hardware. |

Original: https://arxiv.org/abs/1804.11326

External sources to check: Thanasilp et al., exponential concentration in quantum kernel methods — https://arxiv.org/abs/2208.11060; Shaydulin & Wild, importance of kernel bandwidth — https://arxiv.org/abs/2111.05451

Review gap: Hardware demo on a synthetic dataset; the advantage claim is conjectural in the paper itself. Test whether the verdict separates the demonstration from the advantage claim.

Comment anchors: qml-01 / Input · Screen · Design · Verdict · Sources. Verdicts and source relations remain provisional.

# qml-02 Quantum convolutional networks

Cong, Choi, Lukin 2019, quantum convolutional neural networks

Selected because: Tests whether simulability limits are applied without discarding quantum-data results.

Given input I0: Can a hierarchical quantum circuit classify phases with few parameters and favorable sample cost?

I7 evidence to assemble: Phase labels, sample counts, observables, circuit sizes and simulator accuracy. Do not invent missing uncertainty, numerical values or preregistration.

| Component | Input | Expected output proposal |
| --- | --- | --- |
| Intake | I0 | Scope: Can a hierarchical quantum circuit classify phases with few parameters and favorable sample cost? |
| Screen analyst | I1 | Low-bodyness simulability versus quantum state acquisition. |
| Literature retrieval | I2 | Find pre-cutoff predecessors and strong comparators; in current mode, retrieve the sources below if decisive. |
| Prereg / designer | I3 | Compare QCNN, local-observable and classical simulation methods at matched acquisition cost. |
| Baseline champion | I4 | Implement or justify the strongest comparator in the design, with matched access, error and budget. |
| Review panel | I5 | Challenge low-bodyness simulability versus quantum state acquisition. Name a repair, or explain why the control is adequate. |
| Run / implementer | I6 | Recompute a tractable subset of phase labels. If raw data/code are absent, mark execution blocked. |
| Verdict | I7 | Preserve phase-recognition results; restrict advantage claims in classically simulable regimes. |
| Audit | I8 | Check the decisive comparison/proof against sources and phase labels. Flag evidence that cannot be recomputed. |
| Variants | I9 | Probe inputs outside the locally easy regime. |
| Promote | I10 | Preserve this verdict's exact scope, uncertainty and provenance in a disposable record. |
| Lab orchestration | I11 | Request required approvals; stop honestly at missing evidence, state, code or hardware. |

Original: https://arxiv.org/abs/1810.03787

External sources to check: Bermejo et al., QCNNs are effectively classically simulable — https://arxiv.org/abs/2408.12739

Review gap: Simulability holds for the locally easy, low-bodyness regimes studied; quantum data acquisition may still be needed. Score the exact claim.

Comment anchors: qml-02 / Input · Screen · Design · Verdict · Sources. Verdicts and source relations remain provisional.

# qml-03 Quantum recommendation

Kerenidis & Prakash 2016, quantum recommendation systems

Selected because: Provides a clear test of dequantization under comparable input access.

Given input I0: Does a quantum recommendation algorithm reduce cost under specified matrix-access assumptions?

I7 evidence to assemble: Theorem assumptions, complexity bounds, accuracy and data-structure costs. Do not invent missing uncertainty, numerical values or preregistration.

| Component | Input | Expected output proposal |
| --- | --- | --- |
| Intake | I0 | Scope: Does a quantum recommendation algorithm reduce cost under specified matrix-access assumptions? |
| Screen analyst | I1 | QRAM versus classical sampling/query access and output costs. |
| Literature retrieval | I2 | Find pre-cutoff predecessors and strong comparators; in current mode, retrieve the sources below if decisive. |
| Prereg / designer | I3 | Compare quantum and classical recommendation complexity under the same access, error and preprocessing assumptions. |
| Baseline champion | I4 | Implement or justify the strongest comparator in the design, with matched access, error and budget. |
| Review panel | I5 | Challenge qRAM versus classical sampling/query access and output costs. Name a repair, or explain why the control is adequate. |
| Run / implementer | I6 | Check proof dependencies and small numerical examples; no numerical result can certify the theorem. |
| Verdict | I7 | Algorithm correctness can survive while exponential separation fails under matched sampling access. |
| Audit | I8 | Check the decisive comparison/proof against sources and theorem assumptions. Flag evidence that cannot be recomputed. |
| Variants | I9 | Change the access model and identify whether a separation remains. |
| Promote | I10 | Preserve this verdict's exact scope, uncertainty and provenance in a disposable record. |
| Lab orchestration | I11 | Request required approvals; stop honestly at missing evidence, state, code or hardware. |

Original: https://arxiv.org/abs/1603.08675

External sources to check: Tang, quantum-inspired classical algorithm for recommendation systems — https://arxiv.org/abs/1807.04271

Review gap: Algorithm correctness survives; the exponential separation does not under comparable sampling access. Overlaps synthetic eval5.

Comment anchors: qml-03 / Input · Screen · Design · Verdict · Sources. Verdicts and source relations remain provisional.

# qml-04 Quantum PCA

Lloyd, Mohseni, Rebentrost 2014, quantum principal component analysis

Selected because: Tests whether quantum-input and classical-input claims remain distinct.

Given input I0: Can principal components of a low-rank state be estimated efficiently?

I7 evidence to assemble: Rank, spectral gaps, access assumptions, output type and approximation bounds. Do not invent missing uncertainty, numerical values or preregistration.

| Component | Input | Expected output proposal |
| --- | --- | --- |
| Intake | I0 | Scope: Can principal components of a low-rank state be estimated efficiently? |
| Screen analyst | I1 | Copies of quantum states versus classical sampling access. |
| Literature retrieval | I2 | Find pre-cutoff predecessors and strong comparators; in current mode, retrieve the sources below if decisive. |
| Prereg / designer | I3 | Analyze estimation error and copy complexity separately from classical-data preparation costs. |
| Baseline champion | I4 | Implement or justify the strongest comparator in the design, with matched access, error and budget. |
| Review panel | I5 | Challenge copies of quantum states versus classical sampling access. Name a repair, or explain why the control is adequate. |
| Run / implementer | I6 | Check proof dependencies and small numerical examples; no numerical result can certify the theorem. |
| Verdict | I7 | Limit classical-data speedup claims; do not transfer that conclusion to an unmatched quantum-state input model. |
| Audit | I8 | Check the decisive comparison/proof against sources and rank. Flag evidence that cannot be recomputed. |
| Variants | I9 | Study genuinely quantum states with costly classical descriptions. |
| Promote | I10 | Preserve this verdict's exact scope, uncertainty and provenance in a disposable record. |
| Lab orchestration | I11 | Request required approvals; stop honestly at missing evidence, state, code or hardware. |

Original: https://arxiv.org/abs/1307.0401

External sources to check: Tang, QPCA only achieves an exponential speedup because of its state preparation assumptions — https://arxiv.org/abs/1811.00414

Review gap: Speedup on classical data is dequantized; the quantum-data-input setting is a different access model. Good scope test.

Comment anchors: qml-04 / Input · Screen · Design · Verdict · Sources. Verdicts and source relations remain provisional.

# qml-05 Data re-uploading

Perez-Salinas et al. 2020, data re-uploading for a universal quantum classifier

Selected because: Separates mathematical expressivity from benchmark competitiveness.

Given input I0: Can repeated data encoding yield a universal classifier and useful predictive performance?

I7 evidence to assemble: Approximation assumptions, dataset splits, accuracies, tuning budgets and seed variation. Do not invent missing uncertainty, numerical values or preregistration.

| Component | Input | Expected output proposal |
| --- | --- | --- |
| Intake | I0 | Scope: Can repeated data encoding yield a universal classifier and useful predictive performance? |
| Screen analyst | I1 | Universality does not establish advantage over tuned classical models. |
| Literature retrieval | I2 | Find pre-cutoff predecessors and strong comparators; in current mode, retrieve the sources below if decisive. |
| Prereg / designer | I3 | Separate proof checks from repeated-seed comparisons with tuned classical baselines. |
| Baseline champion | I4 | Implement or justify the strongest comparator in the design, with matched access, error and budget. |
| Review panel | I5 | Challenge universality does not establish advantage over tuned classical models. Name a repair, or explain why the control is adequate. |
| Run / implementer | I6 | Recompute a tractable subset of approximation assumptions. If raw data/code are absent, mark execution blocked. |
| Verdict | I7 | Universality may stand independently of weak or mixed empirical competitiveness. |
| Audit | I8 | Check the decisive comparison/proof against sources and approximation assumptions. Flag evidence that cannot be recomputed. |
| Variants | I9 | Test a structured dataset with a justified classical bottleneck. |
| Promote | I10 | Preserve this verdict's exact scope, uncertainty and provenance in a disposable record. |
| Lab orchestration | I11 | Request required approvals; stop honestly at missing evidence, state, code or hardware. |

Original: https://arxiv.org/abs/1907.02085

External sources to check: Bowles, Ahmed, Schuld, better than classical? benchmarking QML models — https://arxiv.org/abs/2403.07059

Review gap: Universality is formal and survives; competitiveness against tuned classical baselines is the adjudicated part. Confirm the benchmark includes this model.

Comment anchors: qml-05 / Input · Screen · Design · Verdict · Sources. Verdicts and source relations remain provisional.

# qml-06 Power of data

Huang et al. 2021, power of data in quantum machine learning

Selected because: Tests whether a positive result is preserved within its engineered-data scope.

Given input I0: When does geometric difference permit a projected quantum kernel to improve prediction?

I7 evidence to assemble: Dataset construction, geometric differences, predictive errors and baseline tuning. Do not invent missing uncertainty, numerical values or preregistration.

| Component | Input | Expected output proposal |
| --- | --- | --- |
| Intake | I0 | Scope: When does geometric difference permit a projected quantum kernel to improve prediction? |
| Screen analyst | I1 | Constructed-label dependence and limitations of the comparator set. |
| Literature retrieval | I2 | Find pre-cutoff predecessors and strong comparators; in current mode, retrieve the sources below if decisive. |
| Prereg / designer | I3 | Compare high- and low-geometric-difference datasets with matched classical kernels. |
| Baseline champion | I4 | Implement or justify the strongest comparator in the design, with matched access, error and budget. |
| Review panel | I5 | Challenge constructed-label dependence and limitations of the comparator set. Name a repair, or explain why the control is adequate. |
| Run / implementer | I6 | Recompute a tractable subset of dataset construction. If raw data/code are absent, mark execution blocked. |
| Verdict | I7 | Support the demonstrated engineered-data result only if matched evidence confirms it; broader usefulness remains open. |
| Audit | I8 | Check the decisive comparison/proof against sources and dataset construction. Flag evidence that cannot be recomputed. |
| Variants | I9 | Test non-engineered datasets and stronger kernel approximations. |
| Promote | I10 | Preserve this verdict's exact scope, uncertainty and provenance in a disposable record. |
| Lab orchestration | I11 | Request required approvals; stop honestly at missing evidence, state, code or hardware. |

Original: https://arxiv.org/abs/2011.01938

External sources to check: Bowles, Ahmed, Schuld, better than classical? benchmarking QML models — https://arxiv.org/abs/2403.07059

Review gap: Positive case within an engineered-data scope. Confirm what the benchmark says about projected kernels before assigning a tier.

Comment anchors: qml-06 / Input · Screen · Design · Verdict · Sources. Verdicts and source relations remain provisional.

# qml-07 Rigorous supervised speedup

Liu, Arunachalam, Temme 2021, rigorous and robust quantum speed-up in supervised learning

Selected because: A positive theoretical case tests rejection based solely on impractical hardware.

Given input I0: Can a kernel learner solve a discrete-log-based task efficiently under a stated hardness assumption?

I7 evidence to assemble: Theorem statements, proof dependencies and end-to-end complexity. Do not invent missing uncertainty, numerical values or preregistration.

| Component | Input | Expected output proposal |
| --- | --- | --- |
| Intake | I0 | Scope: Can a kernel learner solve a discrete-log-based task efficiently under a stated hardness assumption? |
| Screen analyst | I1 | Formal separation versus NISQ feasibility; do not conflate them. |
| Literature retrieval | I2 | Find pre-cutoff predecessors and strong comparators; in current mode, retrieve the sources below if decisive. |
| Prereg / designer | I3 | Check the reduction, noise tolerance, learner complexity and classical hardness assumption. |
| Baseline champion | I4 | Implement or justify the strongest comparator in the design, with matched access, error and budget. |
| Review panel | I5 | Challenge formal separation versus NISQ feasibility; do not conflate them. Name a repair, or explain why the control is adequate. |
| Run / implementer | I6 | Check proof dependencies and small numerical examples; no numerical result can certify the theorem. |
| Verdict | I7 | A conditional formal separation may be supported without a useful near-term implementation. |
| Audit | I8 | Check the decisive comparison/proof against sources and theorem statements. Flag evidence that cannot be recomputed. |
| Variants | I9 | Quantify realistic resource requirements separately. |
| Promote | I10 | Preserve this verdict's exact scope, uncertainty and provenance in a disposable record. |
| Lab orchestration | I11 | Request required approvals; stop honestly at missing evidence, state, code or hardware. |

Original: https://arxiv.org/abs/2010.02174

External sources to check: None identified in the inventory; external validation remains open.

Review gap: Formal positive control. No external adjudication identified yet; tier C until one is found. Mining found discussion (e.g. 2406.07072 on trainability vs dequantization) but no claim-level adjudication. Formal positive control; tier C unless an independent proof check is found.

Comment anchors: qml-07 / Input · Screen · Design · Verdict · Sources. Verdicts and source relations remain provisional.

# qml-08 Barren plateaus

McClean et al. 2018, barren plateaus in quantum neural network training landscapes

Selected because: A rigorous negative theorem tests whether scope survives broad generalization.

Given input I0: How does gradient variance scale for circuits approaching a specified random ensemble?

I7 evidence to assemble: Variance scaling, ensemble definitions, sampling uncertainty and proof conditions. Do not invent missing uncertainty, numerical values or preregistration.

| Component | Input | Expected output proposal |
| --- | --- | --- |
| Intake | I0 | Scope: How does gradient variance scale for circuits approaching a specified random ensemble? |
| Screen analyst | I1 | Randomness, circuit depth, locality and cost-function assumptions. |
| Literature retrieval | I2 | Find pre-cutoff predecessors and strong comparators; in current mode, retrieve the sources below if decisive. |
| Prereg / designer | I3 | Measure gradient variance versus size for random and structured circuits with local and global costs. |
| Baseline champion | I4 | Implement or justify the strongest comparator in the design, with matched access, error and budget. |
| Review panel | I5 | Challenge randomness, circuit depth, locality and cost-function assumptions. Name a repair, or explain why the control is adequate. |
| Run / implementer | I6 | Check proof dependencies and small numerical examples; no numerical result can certify the theorem. |
| Verdict | I7 | Support exponential suppression in the covered regime; do not reject all variational circuits. |
| Audit | I8 | Check the decisive comparison/proof against sources and variance scaling. Flag evidence that cannot be recomputed. |
| Variants | I9 | Test structured circuits or local costs outside that regime. |
| Promote | I10 | Preserve this verdict's exact scope, uncertainty and provenance in a disposable record. |
| Lab orchestration | I11 | Request required approvals; stop honestly at missing evidence, state, code or hardware. |

Original: https://arxiv.org/abs/1803.11173

External sources to check: Cerezo et al., cost function dependent barren plateaus — https://arxiv.org/abs/2001.00550; Larocca et al., review of barren plateaus — https://arxiv.org/abs/2405.00781

Review gap: Cerezo et al. is independent of the original authors; the 2024 review includes McClean and does not count toward independence.

Comment anchors: qml-08 / Input · Screen · Design · Verdict · Sources. Verdicts and source relations remain provisional.

# qml-09 Classical shadows

Huang, Kueng, Preskill 2020, predicting many properties of a quantum system from very few measurements (classical shadows)

Selected because: A positive measurement result tests preservation of observable-specific sample benefits.

Given input I0: Can randomized quantum measurements estimate many specified observables efficiently?

I7 evidence to assemble: Shot counts, estimation errors, confidence coverage and observable norms. Do not invent missing uncertainty, numerical values or preregistration.

| Component | Input | Expected output proposal |
| --- | --- | --- |
| Intake | I0 | Scope: Can randomized quantum measurements estimate many specified observables efficiently? |
| Screen analyst | I1 | Shadow norms and locality determine cost; logarithmic dependence alone is insufficient. |
| Literature retrieval | I2 | Find pre-cutoff predecessors and strong comparators; in current mode, retrieve the sources below if decisive. |
| Prereg / designer | I3 | Vary observable count and locality; compare shadow estimation with direct measurement at matched error. |
| Baseline champion | I4 | Implement or justify the strongest comparator in the design, with matched access, error and budget. |
| Review panel | I5 | Challenge shadow norms and locality determine cost; logarithmic dependence alone is insufficient. Name a repair, or explain why the control is adequate. |
| Run / implementer | I6 | Recompute a tractable subset of shot counts. If raw data/code are absent, mark execution blocked. |
| Verdict | I7 | Support scoped estimation guarantees; an experimental instance alone does not verify all scaling claims. |
| Audit | I8 | Check the decisive comparison/proof against sources and shot counts. Flag evidence that cannot be recomputed. |
| Variants | I9 | Test difficult observables and noise-robust estimators. |
| Promote | I10 | Preserve this verdict's exact scope, uncertainty and provenance in a disposable record. |
| Lab orchestration | I11 | Request required approvals; stop honestly at missing evidence, state, code or hardware. |

Original: https://arxiv.org/abs/2002.08953

External sources to check: Struchalin et al., experimental estimation of quantum state properties from classical shadows — https://arxiv.org/abs/2008.05234

Review gap: Quantum-learning positive with an independent experiment. Check author overlap and whether the experiment tests the scaling claim or one instance.

Comment anchors: qml-09 / Input · Screen · Design · Verdict · Sources. Verdicts and source relations remain provisional.

# qml-10 Learning from experiments

Huang et al. 2022, quantum advantage in learning from experiments

Selected because: Adds a positive quantum-learning claim with an explicit uncertainty about independent confirmation.

Given input I0: Can quantum memory reduce experiment counts for a specified learning task?

I7 evidence to assemble: Task definitions, sample counts, prediction errors, hardware results and theorem assumptions. Do not invent missing uncertainty, numerical values or preregistration.

| Component | Input | Expected output proposal |
| --- | --- | --- |
| Intake | I0 | Scope: Can quantum memory reduce experiment counts for a specified learning task? |
| Screen analyst | I1 | Sample-complexity advantage versus runtime advantage. |
| Literature retrieval | I2 | Find pre-cutoff predecessors and strong comparators; in current mode, retrieve the sources below if decisive. |
| Prereg / designer | I3 | Compare quantum-memory and classical-memory protocols under the same task and error target. |
| Baseline champion | I4 | Implement or justify the strongest comparator in the design, with matched access, error and budget. |
| Review panel | I5 | Challenge sample-complexity advantage versus runtime advantage. Name a repair, or explain why the control is adequate. |
| Run / implementer | I6 | Recompute a tractable subset of task definitions. If raw data/code are absent, mark execution blocked. |
| Verdict | I7 | Preserve any established task-specific sample advantage; independent replication and runtime advantage are separate questions. |
| Audit | I8 | Check the decisive comparison/proof against sources and task definitions. Flag evidence that cannot be recomputed. |
| Variants | I9 | Design an independent replication with matched information access. |
| Promote | I10 | Preserve this verdict's exact scope, uncertainty and provenance in a disposable record. |
| Lab orchestration | I11 | Request required approvals; stop honestly at missing evidence, state, code or hardware. |

Original: https://arxiv.org/abs/2112.00778

External sources to check: None identified in the inventory; external validation remains open.

Review gap: Positive quantum-advantage claim (sample complexity, not runtime). No independent replication identified; tier C. Theory companions share authors.

Comment anchors: qml-10 / Input · Screen · Design · Verdict · Sources. Verdicts and source relations remain provisional.

# qc-01 Sycamore sampling

Arute et al. 2019, quantum supremacy using a programmable superconducting processor

Selected because: Tests correction of a classical cost estimate without erasing hardware achievements.

Given input I0: How costly is matching a random-circuit sampler at a specified fidelity?

I7 evidence to assemble: Circuit specs, fidelity tests, classical time/memory and hardware sampling rates. Do not invent missing uncertainty, numerical values or preregistration.

| Component | Input | Expected output proposal |
| --- | --- | --- |
| Intake | I0 | Scope: How costly is matching a random-circuit sampler at a specified fidelity? |
| Screen analyst | I1 | Exact versus approximate sampling, verification strength and hardware accounting. |
| Literature retrieval | I2 | Find pre-cutoff predecessors and strong comparators; in current mode, retrieve the sources below if decisive. |
| Prereg / designer | I3 | Compare best samplers at matched fidelity, circuit instances and full compute cost. |
| Baseline champion | I4 | Implement or justify the strongest comparator in the design, with matched access, error and budget. |
| Review panel | I5 | Challenge exact versus approximate sampling, verification strength and hardware accounting. Name a repair, or explain why the control is adequate. |
| Run / implementer | I6 | Recompute a tractable subset of circuit specs. If raw data/code are absent, mark execution blocked. |
| Verdict | I7 | Revise the historical cost estimate when comparable classical evidence warrants it; preserve hardware results. |
| Audit | I8 | Check the decisive comparison/proof against sources and circuit specs. Flag evidence that cannot be recomputed. |
| Variants | I9 | Strengthen validation against approximate spoofing. |
| Promote | I10 | Preserve this verdict's exact scope, uncertainty and provenance in a disposable record. |
| Lab orchestration | I11 | Request required approvals; stop honestly at missing evidence, state, code or hardware. |

Original: https://doi.org/10.1038/s41586-019-1666-5

External sources to check: Pan, Chen, Zhang, solving the sampling problem of the Sycamore quantum circuits — https://arxiv.org/abs/2111.03011

Review gap: The classical-cost estimate is refuted; the hardware fidelity results stand. Claim-level split. arXiv 1910.11333 is the supplementary information, not the paper; use the Nature DOI.

Comment anchors: qc-01 / Input · Screen · Design · Verdict · Sources. Verdicts and source relations remain provisional.

# qc-02 IBM utility experiment

Kim et al. 2023, evidence for the utility of quantum computing before fault tolerance

Selected because: Tests whether improved simulation narrows an advantage claim while leaving mitigation evidence intact.

Given input I0: Can error mitigation estimate observables of a large kicked-Ising circuit accurately?

I7 evidence to assemble: Observable curves, uncertainty, mitigation overhead and simulator convergence. Do not invent missing uncertainty, numerical values or preregistration.

| Component | Input | Expected output proposal |
| --- | --- | --- |
| Intake | I0 | Scope: Can error mitigation estimate observables of a large kicked-Ising circuit accurately? |
| Screen analyst | I1 | Observable-specific classical simulation versus brute-force simulation. |
| Literature retrieval | I2 | Find pre-cutoff predecessors and strong comparators; in current mode, retrieve the sources below if decisive. |
| Prereg / designer | I3 | Compare tensor-network and other simulators with mitigated estimates at matched observable error. |
| Baseline champion | I4 | Implement or justify the strongest comparator in the design, with matched access, error and budget. |
| Review panel | I5 | Challenge observable-specific classical simulation versus brute-force simulation. Name a repair, or explain why the control is adequate. |
| Run / implementer | I6 | Recompute a tractable subset of observable curves. If raw data/code are absent, mark execution blocked. |
| Verdict | I7 | Preserve validated mitigation accuracy; beyond-classical usefulness requires stronger matched evidence. |
| Audit | I8 | Check the decisive comparison/proof against sources and observable curves. Flag evidence that cannot be recomputed. |
| Variants | I9 | Identify observables or regimes where classical convergence fails. |
| Promote | I10 | Preserve this verdict's exact scope, uncertainty and provenance in a disposable record. |
| Lab orchestration | I11 | Request required approvals; stop honestly at missing evidence, state, code or hardware. |

Original: https://doi.org/10.1038/s41586-023-06096-3

External sources to check: Tindall et al., efficient tensor network simulation of IBM's Eagle kicked Ising experiment — https://arxiv.org/abs/2306.14887; Begusic & Chan, fast classical simulation of evidence for the utility of quantum computing — https://arxiv.org/abs/2306.16372

Review gap: Error-mitigation accuracy survives; beyond-classical framing does not in the reported regime. Begusic & Chan citation not found in Semantic Scholar or OpenAlex reference lists; the paper's subject is this experiment, so treat as an index gap and confirm in the PDF.

Comment anchors: qc-02 / Input · Screen · Design · Verdict · Sources. Verdicts and source relations remain provisional.

# qc-03 Photonic sampling

Zhong et al. 2020, quantum computational advantage using photons (Jiuzhang)

Selected because: Tests whether benchmark spoofing is confused with exact-sampling dequantization.

Given input I0: Can a photonic sampler generate a specified Gaussian-boson distribution beyond classical rates?

I7 evidence to assemble: Photon losses, sample tests, validation statistics and approximation costs. Do not invent missing uncertainty, numerical values or preregistration.

| Component | Input | Expected output proposal |
| --- | --- | --- |
| Intake | I0 | Scope: Can a photonic sampler generate a specified Gaussian-boson distribution beyond classical rates? |
| Screen analyst | I1 | Passing finite validation tests is different from matching the full distribution. |
| Literature retrieval | I2 | Find pre-cutoff predecessors and strong comparators; in current mode, retrieve the sources below if decisive. |
| Prereg / designer | I3 | Compare classical approximations using stronger held-out distributional tests and equal cost. |
| Baseline champion | I4 | Implement or justify the strongest comparator in the design, with matched access, error and budget. |
| Review panel | I5 | Challenge passing finite validation tests is different from matching the full distribution. Name a repair, or explain why the control is adequate. |
| Run / implementer | I6 | Recompute a tractable subset of photon losses. If raw data/code are absent, mark execution blocked. |
| Verdict | I7 | Weaken claims licensed only by spoofable tests; do not infer that exact sampling hardness is disproved. |
| Audit | I8 | Check the decisive comparison/proof against sources and photon losses. Flag evidence that cannot be recomputed. |
| Variants | I9 | Add discriminating validation tests. |
| Promote | I10 | Preserve this verdict's exact scope, uncertainty and provenance in a disposable record. |
| Lab orchestration | I11 | Request required approvals; stop honestly at missing evidence, state, code or hardware. |

Original: https://arxiv.org/abs/2012.01625

External sources to check: Villalonga et al., efficient approximation of experimental Gaussian boson sampling — https://arxiv.org/abs/2109.11525

Review gap: Rebuttal spoofs the benchmark tests used; exact sampling hardness is not refuted. Claim-level. Author-overlap flag 'L. Li' is a name collision (Google vs USTC), not shared authorship.

Comment anchors: qc-03 / Input · Screen · Design · Verdict · Sources. Verdicts and source relations remain provisional.

# qc-04 Annealing dynamics

King et al. 2025, beyond-classical computation in quantum simulation (D-Wave)

Selected because: A disputed claim tests calibrated disagreement rather than forced agreement with one side.

Given input I0: Can an annealer reproduce spin-glass dynamics outside a declared classical accuracy budget?

I7 evidence to assemble: Original and challenge results, convergence checks, replies and unmatched regimes. Do not invent missing uncertainty, numerical values or preregistration.

| Component | Input | Expected output proposal |
| --- | --- | --- |
| Intake | I0 | Scope: Can an annealer reproduce spin-glass dynamics outside a declared classical accuracy budget? |
| Screen analyst | I1 | Matched observables, regimes, errors and competing simulation methods. |
| Literature retrieval | I2 | Find pre-cutoff predecessors and strong comparators; in current mode, retrieve the sources below if decisive. |
| Prereg / designer | I3 | Reconcile both sides on identical instances, observables and tolerance. |
| Baseline champion | I4 | Implement or justify the strongest comparator in the design, with matched access, error and budget. |
| Review panel | I5 | Challenge matched observables, regimes, errors and competing simulation methods. Name a repair, or explain why the control is adequate. |
| Run / implementer | I6 | Recompute a tractable subset of original and challenge results. If raw data/code are absent, mark execution blocked. |
| Verdict | I7 | Record supported subclaims and unresolved comparisons; no mandatory winner before adjudication. |
| Audit | I8 | Check the decisive comparison/proof against sources and original and challenge results. Flag evidence that cannot be recomputed. |
| Variants | I9 | Run the cheapest comparison that resolves the remaining mismatch. |
| Promote | I10 | Preserve this verdict's exact scope, uncertainty and provenance in a disposable record. |
| Lab orchestration | I11 | Request required approvals; stop honestly at missing evidence, state, code or hardware. |

Original: https://arxiv.org/abs/2403.00910

External sources to check: Tindall et al., dynamics of disordered quantum systems with 2D tensor networks — https://arxiv.org/abs/2503.05693; Mauron & Carleo, challenging the quantum advantage frontier with large-scale classical simulations of annealing dynamics — https://arxiv.org/abs/2503.08247

Review gap: Live dispute with replies; good test that the verdict stays INCONCLUSIVE rather than picking a side. Mauron & Carleo citation not found in either index; confirm in the PDF.

Comment anchors: qc-04 / Input · Screen · Design · Verdict · Sources. Verdicts and source relations remain provisional.

# qc-05 Finite-range tunneling

Denchev et al. 2016, what is the computational value of finite-range tunneling?

Selected because: Tests a large gain against a weak comparator.

Given input I0: Does quantum annealing improve time to solution for weak-strong cluster instances?

I7 evidence to assemble: Runtime distributions, success probabilities, preprocessing and tuning costs. Do not invent missing uncertainty, numerical values or preregistration.

| Component | Input | Expected output proposal |
| --- | --- | --- |
| Intake | I0 | Scope: Does quantum annealing improve time to solution for weak-strong cluster instances? |
| Screen analyst | I1 | Simulated annealing is not the strongest available classical solver. |
| Literature retrieval | I2 | Find pre-cutoff predecessors and strong comparators; in current mode, retrieve the sources below if decisive. |
| Prereg / designer | I3 | Compare multiple classical solvers using matched success probability, tuning and instance families. |
| Baseline champion | I4 | Implement or justify the strongest comparator in the design, with matched access, error and budget. |
| Review panel | I5 | Challenge simulated annealing is not the strongest available classical solver. Name a repair, or explain why the control is adequate. |
| Run / implementer | I6 | Recompute a tractable subset of runtime distributions. If raw data/code are absent, mark execution blocked. |
| Verdict | I7 | Preserve a gain against the named comparator; do not infer advantage over all classical methods. |
| Audit | I8 | Check the decisive comparison/proof against sources and runtime distributions. Flag evidence that cannot be recomputed. |
| Variants | I9 | Test less tailored instances against the strongest solver. |
| Promote | I10 | Preserve this verdict's exact scope, uncertainty and provenance in a disposable record. |
| Lab orchestration | I11 | Request required approvals; stop honestly at missing evidence, state, code or hardware. |

Original: https://arxiv.org/abs/1512.02206

External sources to check: Mandra et al., strengths and weaknesses of weak-strong cluster problems — https://arxiv.org/abs/1604.01746

Review gap: Speedup holds against simulated annealing; not against the strongest classical solvers. Weak-baseline lesson, directly relevant to criterion 5.

Comment anchors: qc-05 / Input · Screen · Design · Verdict · Sources. Verdicts and source relations remain provisional.

# qc-06 HHL linear systems

Harrow, Hassidim, Lloyd 2009, quantum algorithm for linear systems of equations

Selected because: Tests an important theorem with restrictive input and output assumptions.

Given input I0: Can a quantum algorithm prepare a solution state for sparse, well-conditioned linear systems efficiently?

I7 evidence to assemble: Access model, sparsity, conditioning, error bounds and output requirements. Do not invent missing uncertainty, numerical values or preregistration.

| Component | Input | Expected output proposal |
| --- | --- | --- |
| Intake | I0 | Scope: Can a quantum algorithm prepare a solution state for sparse, well-conditioned linear systems efficiently? |
| Screen analyst | I1 | State preparation, condition number, precision and readout. |
| Literature retrieval | I2 | Find pre-cutoff predecessors and strong comparators; in current mode, retrieve the sources below if decisive. |
| Prereg / designer | I3 | Account for the full task cost; compare observable estimation and full-vector output separately. |
| Baseline champion | I4 | Implement or justify the strongest comparator in the design, with matched access, error and budget. |
| Review panel | I5 | Challenge state preparation, condition number, precision and readout. Name a repair, or explain why the control is adequate. |
| Run / implementer | I6 | Check proof dependencies and small numerical examples; no numerical result can certify the theorem. |
| Verdict | I7 | Preserve the conditional algorithmic result; reject an unsupported full classical-vector speedup. |
| Audit | I8 | Check the decisive comparison/proof against sources and access model. Flag evidence that cannot be recomputed. |
| Variants | I9 | Study quantum-native inputs and limited-observable outputs. |
| Promote | I10 | Preserve this verdict's exact scope, uncertainty and provenance in a disposable record. |
| Lab orchestration | I11 | Request required approvals; stop honestly at missing evidence, state, code or hardware. |

Original: https://arxiv.org/abs/0811.3171

External sources to check: Aaronson, read the fine print — https://doi.org/10.1038/nphys3272

Review gap: Algorithm stands; end-to-end advantage depends on input/output caveats. Matches the deprioritized-HHL rule in CLAUDE.md.

Comment anchors: qc-06 / Input · Screen · Design · Verdict · Sources. Verdicts and source relations remain provisional.

# qc-07 Loophole-free Bell tests

Hensen et al. 2015, loophole-free Bell inequality violation using electron spins

Selected because: An established positive quantum result tests unnecessary rejection and shared-component awareness.

Given input I0: Can a separated entangled system violate a Bell inequality with key loopholes closed?

I7 evidence to assemble: Trial-level events, timing, setting records, test statistics and independent experiments. Do not invent missing uncertainty, numerical values or preregistration.

| Component | Input | Expected output proposal |
| --- | --- | --- |
| Intake | I0 | Scope: Can a separated entangled system violate a Bell inequality with key loopholes closed? |
| Screen analyst | I1 | Detection, locality, setting randomness and valid sequential statistics. |
| Literature retrieval | I2 | Find pre-cutoff predecessors and strong comparators; in current mode, retrieve the sources below if decisive. |
| Prereg / designer | I3 | Specify event selection, timing, random settings and a valid hypothesis test before inspection. |
| Baseline champion | I4 | Implement or justify the strongest comparator in the design, with matched access, error and budget. |
| Review panel | I5 | Challenge detection, locality, setting randomness and valid sequential statistics. Name a repair, or explain why the control is adequate. |
| Run / implementer | I6 | Recompute a tractable subset of trial-level events. If raw data/code are absent, mark execution blocked. |
| Verdict | I7 | Support a violation under tested assumptions; record shared random-generator dependencies. |
| Audit | I8 | Check the decisive comparison/proof against sources and trial-level events. Flag evidence that cannot be recomputed. |
| Variants | I9 | Replicate with independently implemented setting generation. |
| Promote | I10 | Preserve this verdict's exact scope, uncertainty and provenance in a disposable record. |
| Lab orchestration | I11 | Request required approvals; stop honestly at missing evidence, state, code or hardware. |

Original: https://arxiv.org/abs/1508.05949

External sources to check: Giustina et al., significant-loophole-free test of Bell's theorem with entangled photons — https://arxiv.org/abs/1511.03190; Shalm et al., strong loophole-free test of local realism — https://arxiv.org/abs/1511.03189

Review gap: Three independent groups, different platforms. Positive quantum claim, foundations rather than advantage. Verified overlap: Abellan, Mitchell, Pruneri, Amaya (ICFO) co-author all three tests as suppliers of the random-number generators. Core experimental groups are independent, but the setting-choice component is shared; record it as a common-mode dependency when assigning the tier.

Comment anchors: qc-07 / Input · Screen · Design · Verdict · Sources. Verdicts and source relations remain provisional.

# qc-08 Below-threshold error correction

Google Quantum AI 2024, quantum error correction below the surface code threshold

Selected because: A positive QEC case tests the distinction between logical suppression and usable fault tolerance.

Given input I0: Does logical error decrease as surface-code distance increases under a fixed operating regime?

I7 evidence to assemble: Logical error rates and uncertainty, distances, cycles, decoder costs and correlations. Do not invent missing uncertainty, numerical values or preregistration.

| Component | Input | Expected output proposal |
| --- | --- | --- |
| Intake | I0 | Scope: Does logical error decrease as surface-code distance increases under a fixed operating regime? |
| Screen analyst | I1 | Decoder comparability, correlated errors and resource overhead. |
| Literature retrieval | I2 | Find pre-cutoff predecessors and strong comparators; in current mode, retrieve the sources below if decisive. |
| Prereg / designer | I3 | Compare code distances using matched decoding and cycle definitions; test rare error bursts. |
| Baseline champion | I4 | Implement or justify the strongest comparator in the design, with matched access, error and budget. |
| Review panel | I5 | Challenge decoder comparability, correlated errors and resource overhead. Name a repair, or explain why the control is adequate. |
| Run / implementer | I6 | Recompute a tractable subset of logical error rates and uncertainty. If raw data/code are absent, mark execution blocked. |
| Verdict | I7 | Support demonstrated suppression if the packet warrants it; do not infer complete fault tolerance or replication. |
| Audit | I8 | Check the decisive comparison/proof against sources and logical error rates and uncertainty. Flag evidence that cannot be recomputed. |
| Variants | I9 | Test longer runs and independently replicated scaling. |
| Promote | I10 | Preserve this verdict's exact scope, uncertainty and provenance in a disposable record. |
| Lab orchestration | I11 | Request required approvals; stop honestly at missing evidence, state, code or hardware. |

Original: https://arxiv.org/abs/2408.13687

External sources to check: None identified in the inventory; external validation remains open.

Review gap: Positive QEC claim, no independent replication identified on another platform for the same claim. Tier C until one is found.

Comment anchors: qc-08 / Input · Screen · Design · Verdict · Sources. Verdicts and source relations remain provisional.

# qc-09 Logical neutral-atom processor

Bluvstein et al. 2024, logical quantum processor based on reconfigurable atom arrays

Selected because: Adds a hardware success relevant to neutral-atom work while testing postselection accounting.

Given input I0: Can encoded neutral-atom circuits improve task fidelity over physical-qubit implementations?

I7 evidence to assemble: Circuit fidelities, acceptance rates, resource counts and logical error detection. Do not invent missing uncertainty, numerical values or preregistration.

| Component | Input | Expected output proposal |
| --- | --- | --- |
| Intake | I0 | Scope: Can encoded neutral-atom circuits improve task fidelity over physical-qubit implementations? |
| Screen analyst | I1 | Postselection acceptance, error detection versus correction and comparator fairness. |
| Literature retrieval | I2 | Find pre-cutoff predecessors and strong comparators; in current mode, retrieve the sources below if decisive. |
| Prereg / designer | I3 | Compare logical and physical circuits at matched tasks while charging discarded shots. |
| Baseline champion | I4 | Implement or justify the strongest comparator in the design, with matched access, error and budget. |
| Review panel | I5 | Challenge postselection acceptance, error detection versus correction and comparator fairness. Name a repair, or explain why the control is adequate. |
| Run / implementer | I6 | Recompute a tractable subset of circuit fidelities. If raw data/code are absent, mark execution blocked. |
| Verdict | I7 | Support the demonstrated encoded regime; do not equate postselected detection with fault-tolerant correction. |
| Audit | I8 | Check the decisive comparison/proof against sources and circuit fidelities. Flag evidence that cannot be recomputed. |
| Variants | I9 | Reduce postselection cost or demonstrate active correction. |
| Promote | I10 | Preserve this verdict's exact scope, uncertainty and provenance in a disposable record. |
| Lab orchestration | I11 | Request required approvals; stop honestly at missing evidence, state, code or hardware. |

Original: https://arxiv.org/abs/2312.03982

External sources to check: None identified in the inventory; external validation remains open.

Review gap: Neutral-atom positive, relevant to the Q-Factor track. No independent replication identified; tier C.

Comment anchors: qc-09 / Input · Screen · Design · Verdict · Sources. Verdicts and source relations remain provisional.

# phys-01 Majorana conductance

Zhang et al. 2018, quantized Majorana conductance (retracted 2021)

Selected because: Tests whether retraction and data-selection problems invalidate a mechanism inference.

Given input I0: Can conductance measurements distinguish Majorana modes from alternative explanations?

I7 evidence to assemble: Unselected conductance data, processing history, retraction notice and competing explanations. Do not invent missing uncertainty, numerical values or preregistration.

| Component | Input | Expected output proposal |
| --- | --- | --- |
| Intake | I0 | Scope: Can conductance measurements distinguish Majorana modes from alternative explanations? |
| Screen analyst | I1 | Selective data presentation and non-unique conductance signatures. |
| Literature retrieval | I2 | Find pre-cutoff predecessors and strong comparators; in current mode, retrieve the sources below if decisive. |
| Prereg / designer | I3 | Require full sweeps, alternative-model controls and robust criteria for the plateau. |
| Baseline champion | I4 | Implement or justify the strongest comparator in the design, with matched access, error and budget. |
| Review panel | I5 | Challenge selective data presentation and non-unique conductance signatures. Name a repair, or explain why the control is adequate. |
| Run / implementer | I6 | Recompute a tractable subset of unselected conductance data. If raw data/code are absent, mark execution blocked. |
| Verdict | I7 | The retracted evidence cannot establish the mechanism; this does not refute every Majorana hypothesis. |
| Audit | I8 | Check the decisive comparison/proof against sources and unselected conductance data. Flag evidence that cannot be recomputed. |
| Variants | I9 | Acquire independently controlled spectroscopy. |
| Promote | I10 | Preserve this verdict's exact scope, uncertainty and provenance in a disposable record. |
| Lab orchestration | I11 | Request required approvals; stop honestly at missing evidence, state, code or hardware. |

Original: https://arxiv.org/abs/1710.10701

External sources to check: Retraction note: Quantized Majorana conductance — https://doi.org/10.1038/s41586-021-03373-x; Yu et al., non-Majorana states yield nearly quantized conductance — https://arxiv.org/abs/2004.08583

Review gap: Retracted after data-selection issues. Verify the retraction notice DOI. The retraction note is by the original authors (self-retraction): authoritative for the claim's evidential status but not an independent replication. Yu et al. shares Bakkers (device growth). Confirm whether independent critics (e.g. published data-selection concerns) triggered the retraction before assigning tier A.

Comment anchors: phys-01 / Input · Screen · Design · Verdict · Sources. Verdicts and source relations remain provisional.

# phys-02 LK-99 superconductivity

Lee et al. 2023, LK-99 room-temperature ambient-pressure superconductor

Selected because: Tests extraordinary-claim validation and alternative explanations for apparent success.

Given input I0: Does a specified synthesized material exhibit ambient-pressure room-temperature superconductivity?

I7 evidence to assemble: Transport curves, magnetic measurements, phase analysis and independent synthesis reports. Do not invent missing uncertainty, numerical values or preregistration.

| Component | Input | Expected output proposal |
| --- | --- | --- |
| Intake | I0 | Scope: Does a specified synthesized material exhibit ambient-pressure room-temperature superconductivity? |
| Screen analyst | I1 | Impurities and magnetism can mimic individual signatures. |
| Literature retrieval | I2 | Find pre-cutoff predecessors and strong comparators; in current mode, retrieve the sources below if decisive. |
| Prereg / designer | I3 | Measure resistivity, magnetic response and composition with independent synthesis controls. |
| Baseline champion | I4 | Implement or justify the strongest comparator in the design, with matched access, error and budget. |
| Review panel | I5 | Challenge impurities and magnetism can mimic individual signatures. Name a repair, or explain why the control is adequate. |
| Run / implementer | I6 | Recompute a tractable subset of transport curves. If raw data/code are absent, mark execution blocked. |
| Verdict | I7 | Do not accept the claim from isolated signatures; freeze a final negative label only after sourcing the relevant replications. |
| Audit | I8 | Check the decisive comparison/proof against sources and transport curves. Flag evidence that cannot be recomputed. |
| Variants | I9 | Test purified samples and impurity controls. |
| Promote | I10 | Preserve this verdict's exact scope, uncertainty and provenance in a disposable record. |
| Lab orchestration | I11 | Request required approvals; stop honestly at missing evidence, state, code or hardware. |

Original: https://arxiv.org/abs/2307.12008

External sources to check: None identified in the inventory; external validation remains open.

Review gap: Multiple independent replications attributed effects to Cu2S impurities. Adjudicator IDs to be found by citation mining. Citation mining found no challenger: Semantic Scholar has few citation passages for this preprint. Find replication papers manually (independent synthesis attributing the transition to Cu2S).

Comment anchors: phys-02 / Input · Screen · Design · Verdict · Sources. Verdicts and source relations remain provisional.

# phys-03 Neural quantum states

Carleo & Troyer 2017, solving the quantum many-body problem with artificial neural networks

Selected because: A positive computational-physics case tests fair numerical benchmarking.

Given input I0: Can a neural variational wavefunction approximate spin-model ground states accurately?

I7 evidence to assemble: Model definitions, energies, reference values, optimization seeds and convergence. Do not invent missing uncertainty, numerical values or preregistration.

| Component | Input | Expected output proposal |
| --- | --- | --- |
| Intake | I0 | Scope: Can a neural variational wavefunction approximate spin-model ground states accurately? |
| Screen analyst | I1 | Matched ansatz resources, optimization reliability and finite-size scope. |
| Literature retrieval | I2 | Find pre-cutoff predecessors and strong comparators; in current mode, retrieve the sources below if decisive. |
| Prereg / designer | I3 | Compare energies and observables with exact and strong variational methods on tractable sizes. |
| Baseline champion | I4 | Implement or justify the strongest comparator in the design, with matched access, error and budget. |
| Review panel | I5 | Challenge matched ansatz resources, optimization reliability and finite-size scope. Name a repair, or explain why the control is adequate. |
| Run / implementer | I6 | Recompute a tractable subset of model definitions. If raw data/code are absent, mark execution blocked. |
| Verdict | I7 | Support accuracy only for tested models and tolerances; broader superiority needs stronger evidence. |
| Audit | I8 | Check the decisive comparison/proof against sources and model definitions. Flag evidence that cannot be recomputed. |
| Variants | I9 | Probe difficult regimes and independently benchmark convergence. |
| Promote | I10 | Preserve this verdict's exact scope, uncertainty and provenance in a disposable record. |
| Lab orchestration | I11 | Request required approvals; stop honestly at missing evidence, state, code or hardware. |

Original: https://arxiv.org/abs/1606.02318

External sources to check: Wu et al., variational benchmarks for quantum many-body problems — https://arxiv.org/abs/2302.04919

Review gap: Positive physics case. Benchmark compares many variational methods; check what it says about NQS accuracy in the original models. Variational benchmarks paper includes Carleo as co-author: not independent, so tier B at most unless an unrelated benchmark is found.

Comment anchors: phys-03 / Input · Screen · Design · Verdict · Sources. Verdicts and source relations remain provisional.

# phys-04 Rydberg revivals

Bernien et al. 2017, probing many-body dynamics on a 51-atom quantum simulator

Selected because: Tests preservation of an anomalous observation before a mechanism is established.

Given input I0: Does a constrained Rydberg chain retain coherent revivals for specified initial states?

I7 evidence to assemble: Population dynamics, revival metrics, errors and later theoretical explanations. Do not invent missing uncertainty, numerical values or preregistration.

| Component | Input | Expected output proposal |
| --- | --- | --- |
| Intake | I0 | Scope: Does a constrained Rydberg chain retain coherent revivals for specified initial states? |
| Screen analyst | I1 | An observed revival alone does not prove a scar mechanism. |
| Literature retrieval | I2 | Find pre-cutoff predecessors and strong comparators; in current mode, retrieve the sources below if decisive. |
| Prereg / designer | I3 | Compare initial states, detunings, chain sizes and decoherence controls. |
| Baseline champion | I4 | Implement or justify the strongest comparator in the design, with matched access, error and budget. |
| Review panel | I5 | Challenge an observed revival alone does not prove a scar mechanism. Name a repair, or explain why the control is adequate. |
| Run / implementer | I6 | Recompute a tractable subset of population dynamics. If raw data/code are absent, mark execution blocked. |
| Verdict | I7 | Support the observed revivals; distinguish original evidence from later mechanism support. |
| Audit | I8 | Check the decisive comparison/proof against sources and population dynamics. Flag evidence that cannot be recomputed. |
| Variants | I9 | Test scar-specific predictions on new states. |
| Promote | I10 | Preserve this verdict's exact scope, uncertainty and provenance in a disposable record. |
| Lab orchestration | I11 | Request required approvals; stop honestly at missing evidence, state, code or hardware. |

Original: https://arxiv.org/abs/1707.04344

External sources to check: Turner et al., weak ergodicity breaking from quantum many-body scars — https://arxiv.org/abs/1711.03528

Review gap: Observation reported as an anomaly, explained later by independent theory. Calibration case: the original evidence supports the observation, not a mechanism. Neutral-atom relevant.

Comment anchors: phys-04 / Input · Screen · Design · Verdict · Sources. Verdicts and source relations remain provisional.

# phys-05 Gravitational waves

LIGO/Virgo 2016, observation of gravitational waves from a binary black hole merger (GW150914)

Selected because: An externally reanalyzed success tests statistical and instrumental scrutiny without reflexive rejection.

Given input I0: Does a detector transient match a binary-black-hole gravitational-wave signal?

I7 evidence to assemble: Strain data, calibration, signal-to-noise, false-alarm estimates and reanalysis. Do not invent missing uncertainty, numerical values or preregistration.

| Component | Input | Expected output proposal |
| --- | --- | --- |
| Intake | I0 | Scope: Does a detector transient match a binary-black-hole gravitational-wave signal? |
| Screen analyst | I1 | Background estimation, instrumental artifacts and shared calibration. |
| Literature retrieval | I2 | Find pre-cutoff predecessors and strong comparators; in current mode, retrieve the sources below if decisive. |
| Prereg / designer | I3 | Compare matched-filter pipelines, off-source backgrounds and detector coincidence. |
| Baseline champion | I4 | Implement or justify the strongest comparator in the design, with matched access, error and budget. |
| Review panel | I5 | Challenge background estimation, instrumental artifacts and shared calibration. Name a repair, or explain why the control is adequate. |
| Run / implementer | I6 | Recompute a tractable subset of strain data. If raw data/code are absent, mark execution blocked. |
| Verdict | I7 | Support detection if statistical and instrumental checks hold; keep source inferences within their uncertainty. |
| Audit | I8 | Check the decisive comparison/proof against sources and strain data. Flag evidence that cannot be recomputed. |
| Variants | I9 | Reanalyze with alternative waveform and noise assumptions. |
| Promote | I10 | Preserve this verdict's exact scope, uncertainty and provenance in a disposable record. |
| Lab orchestration | I11 | Request required approvals; stop honestly at missing evidence, state, code or hardware. |

Original: https://arxiv.org/abs/1602.03837

External sources to check: Nitz et al., 1-OGC: the first open gravitational-wave catalog — https://arxiv.org/abs/1811.01921

Review gap: Independent reanalysis of open data by a group outside the collaboration. Check author overlap (some may be LVC members).

Comment anchors: phys-05 / Input · Screen · Design · Verdict · Sources. Verdicts and source relations remain provisional.

# ml-01 Neural collaborative filtering

He et al. 2017, neural collaborative filtering

Selected because: A clear weak-baseline example tests tuned comparator selection.

Given input I0: Does an MLP interaction improve implicit-feedback recommendation over matrix factorization?

I7 evidence to assemble: Ranking scores, negatives, splits, hyperparameter searches and repeated runs. Do not invent missing uncertainty, numerical values or preregistration.

| Component | Input | Expected output proposal |
| --- | --- | --- |
| Intake | I0 | Scope: Does an MLP interaction improve implicit-feedback recommendation over matrix factorization? |
| Screen analyst | I1 | Tuning, sampled evaluation and information-access equality. |
| Literature retrieval | I2 | Find pre-cutoff predecessors and strong comparators; in current mode, retrieve the sources below if decisive. |
| Prereg / designer | I3 | Compare tuned matrix factorization and MLP on identical splits and ranking metrics. |
| Baseline champion | I4 | Implement or justify the strongest comparator in the design, with matched access, error and budget. |
| Review panel | I5 | Challenge tuning, sampled evaluation and information-access equality. Name a repair, or explain why the control is adequate. |
| Run / implementer | I6 | Recompute a tractable subset of ranking scores. If raw data/code are absent, mark execution blocked. |
| Verdict | I7 | Limit the superiority claim if tuned factorization matches or exceeds it; retain the implemented model. |
| Audit | I8 | Check the decisive comparison/proof against sources and ranking scores. Flag evidence that cannot be recomputed. |
| Variants | I9 | Test non-dot-product tasks with matched tuning. |
| Promote | I10 | Preserve this verdict's exact scope, uncertainty and provenance in a disposable record. |
| Lab orchestration | I11 | Request required approvals; stop honestly at missing evidence, state, code or hardware. |

Original: https://arxiv.org/abs/1708.05031

External sources to check: Rendle et al., neural collaborative filtering vs. matrix factorization revisited — https://arxiv.org/abs/2005.09683; Ferrari Dacrema et al., are we really making much progress? — https://arxiv.org/abs/1907.06902

Review gap: Weak-baseline case: a properly tuned dot product beats the MLP. Relevant to the lab's recsys experiments.

Comment anchors: ml-01 / Input · Screen · Design · Verdict · Sources. Verdicts and source relations remain provisional.

# ml-02 TabNet

Arik & Pfister 2021, TabNet

Selected because: Tests whether tabular neural gains persist against strong tree baselines.

Given input I0: Can an attentive tabular network improve prediction and useful feature selection?

I7 evidence to assemble: Per-dataset scores, search budgets, seeds and feature-selection checks. Do not invent missing uncertainty, numerical values or preregistration.

| Component | Input | Expected output proposal |
| --- | --- | --- |
| Intake | I0 | Scope: Can an attentive tabular network improve prediction and useful feature selection? |
| Screen analyst | I1 | Dataset selection, tuning budgets and interpretation claims. |
| Literature retrieval | I2 | Find pre-cutoff predecessors and strong comparators; in current mode, retrieve the sources below if decisive. |
| Prereg / designer | I3 | Compare tuned tree and neural models on diverse shared splits; test feature-selection fidelity separately. |
| Baseline champion | I4 | Implement or justify the strongest comparator in the design, with matched access, error and budget. |
| Review panel | I5 | Challenge dataset selection, tuning budgets and interpretation claims. Name a repair, or explain why the control is adequate. |
| Run / implementer | I6 | Recompute a tractable subset of per-dataset scores. If raw data/code are absent, mark execution blocked. |
| Verdict | I7 | Avoid blanket superiority; specify datasets and comparisons where evidence supports a gain. |
| Audit | I8 | Check the decisive comparison/proof against sources and per-dataset scores. Flag evidence that cannot be recomputed. |
| Variants | I9 | Identify a reproducible regime where attention helps. |
| Promote | I10 | Preserve this verdict's exact scope, uncertainty and provenance in a disposable record. |
| Lab orchestration | I11 | Request required approvals; stop honestly at missing evidence, state, code or hardware. |

Original: https://arxiv.org/abs/1908.07442

External sources to check: Shwartz-Ziv & Armon, tabular data: deep learning is not all you need — https://arxiv.org/abs/2106.03253; Grinsztajn et al., why do tree-based models still outperform deep learning on tabular data? — https://arxiv.org/abs/2207.08815

Review gap: Tabular baseline case aligned with criterion 5 (XGBoost/TabPFN).

Comment anchors: ml-02 / Input · Screen · Design · Verdict · Sources. Verdicts and source relations remain provisional.

# ml-03 Batch normalization

Ioffe & Szegedy 2015, batch normalization

Selected because: Separates a successful method from its proposed causal explanation.

Given input I0: Does batch normalization improve training, and is reduced covariate shift the cause?

I7 evidence to assemble: Training curves, covariate-shift measures, ablations and controls. Do not invent missing uncertainty, numerical values or preregistration.

| Component | Input | Expected output proposal |
| --- | --- | --- |
| Intake | I0 | Scope: Does batch normalization improve training, and is reduced covariate shift the cause? |
| Screen analyst | I1 | Performance improvement and mechanism need different tests. |
| Literature retrieval | I2 | Find pre-cutoff predecessors and strong comparators; in current mode, retrieve the sources below if decisive. |
| Prereg / designer | I3 | Measure training gains and manipulate covariate shift while controlling optimization settings. |
| Baseline champion | I4 | Implement or justify the strongest comparator in the design, with matched access, error and budget. |
| Review panel | I5 | Challenge performance improvement and mechanism need different tests. Name a repair, or explain why the control is adequate. |
| Run / implementer | I6 | Recompute a tractable subset of training curves. If raw data/code are absent, mark execution blocked. |
| Verdict | I7 | Preserve demonstrated training gains while questioning the proposed mechanism when counterevidence warrants it. |
| Audit | I8 | Check the decisive comparison/proof against sources and training curves. Flag evidence that cannot be recomputed. |
| Variants | I9 | Test alternative optimization explanations. |
| Promote | I10 | Preserve this verdict's exact scope, uncertainty and provenance in a disposable record. |
| Lab orchestration | I11 | Request required approvals; stop honestly at missing evidence, state, code or hardware. |

Original: https://arxiv.org/abs/1502.03167

External sources to check: Santurkar et al., how does batch normalization help optimization? — https://arxiv.org/abs/1805.11604

Review gap: Performance claim supported; mechanism claim contradicted. Tests claim-level scoring.

Comment anchors: ml-03 / Input · Screen · Design · Verdict · Sources. Verdicts and source relations remain provisional.

# ml-04 Graph isomorphism networks

Xu et al. 2019, how powerful are graph neural networks? (GIN)

Selected because: Separates an expressivity theorem from empirical benchmark margins.

Given input I0: Can a graph network match WL expressivity and improve graph classification?

I7 evidence to assemble: Proof assumptions, graph splits, tuned scores and structure-agnostic baselines. Do not invent missing uncertainty, numerical values or preregistration.

| Component | Input | Expected output proposal |
| --- | --- | --- |
| Intake | I0 | Scope: Can a graph network match WL expressivity and improve graph classification? |
| Screen analyst | I1 | Formal distinguishability differs from predictive generalization. |
| Literature retrieval | I2 | Find pre-cutoff predecessors and strong comparators; in current mode, retrieve the sources below if decisive. |
| Prereg / designer | I3 | Check theorem assumptions and compare graph models with structure-agnostic controls. |
| Baseline champion | I4 | Implement or justify the strongest comparator in the design, with matched access, error and budget. |
| Review panel | I5 | Challenge formal distinguishability differs from predictive generalization. Name a repair, or explain why the control is adequate. |
| Run / implementer | I6 | Recompute a tractable subset of proof assumptions. If raw data/code are absent, mark execution blocked. |
| Verdict | I7 | Preserve a valid expressivity theorem while limiting empirical superiority to fair comparisons. |
| Audit | I8 | Check the decisive comparison/proof against sources and proof assumptions. Flag evidence that cannot be recomputed. |
| Variants | I9 | Test graphs that specifically require structural distinctions. |
| Promote | I10 | Preserve this verdict's exact scope, uncertainty and provenance in a disposable record. |
| Lab orchestration | I11 | Request required approvals; stop honestly at missing evidence, state, code or hardware. |

Original: https://arxiv.org/abs/1810.00826

External sources to check: Errica et al., a fair comparison of graph neural networks for graph classification — https://arxiv.org/abs/1912.09893

Review gap: Expressivity theorem survives; empirical margins shrink under fair evaluation with structure-agnostic baselines. Graph domain matches lab directions.

Comment anchors: ml-04 / Input · Screen · Design · Verdict · Sources. Verdicts and source relations remain provisional.

# ml-05 Multi-similarity loss

Wang et al. 2019, multi-similarity loss for deep metric learning

Selected because: Tests retrieval claims under equalized training protocols.

Given input I0: Does multi-similarity training improve metric-learning retrieval?

I7 evidence to assemble: Recall scores, split policy, backbones, samplers and training budgets. Do not invent missing uncertainty, numerical values or preregistration.

| Component | Input | Expected output proposal |
| --- | --- | --- |
| Intake | I0 | Scope: Does multi-similarity training improve metric-learning retrieval? |
| Screen analyst | I1 | Backbone, sampling, splits and tuning can explain reported margins. |
| Literature retrieval | I2 | Find pre-cutoff predecessors and strong comparators; in current mode, retrieve the sources below if decisive. |
| Prereg / designer | I3 | Hold the pipeline fixed and vary only the loss with matched searches and seeds. |
| Baseline champion | I4 | Implement or justify the strongest comparator in the design, with matched access, error and budget. |
| Review panel | I5 | Challenge backbone, sampling, splits and tuning can explain reported margins. Name a repair, or explain why the control is adequate. |
| Run / implementer | I6 | Recompute a tractable subset of recall scores. If raw data/code are absent, mark execution blocked. |
| Verdict | I7 | Do not credit the loss with gains explained by protocol differences; verify inclusion in the external benchmark. |
| Audit | I8 | Check the decisive comparison/proof against sources and recall scores. Flag evidence that cannot be recomputed. |
| Variants | I9 | Test genuinely loss-sensitive regimes. |
| Promote | I10 | Preserve this verdict's exact scope, uncertainty and provenance in a disposable record. |
| Lab orchestration | I11 | Request required approvals; stop honestly at missing evidence, state, code or hardware. |

Original: https://arxiv.org/abs/1904.06627

External sources to check: Musgrave et al., a metric learning reality check — https://arxiv.org/abs/2003.08505

Review gap: Gains largely vanish under fair comparison. Confirm the reality check includes this loss.

Comment anchors: ml-05 / Input · Screen · Design · Verdict · Sources. Verdicts and source relations remain provisional.

# ml-06 WGAN gradient penalty

Gulrajani et al. 2017, improved training of Wasserstein GANs

Selected because: Tests whether tuning effort is mistaken for objective superiority.

Given input I0: Does gradient-penalized Wasserstein training improve GAN stability and quality?

I7 evidence to assemble: Quality metrics, failure rates, searches, seeds and compute budgets. Do not invent missing uncertainty, numerical values or preregistration.

| Component | Input | Expected output proposal |
| --- | --- | --- |
| Intake | I0 | Scope: Does gradient-penalized Wasserstein training improve GAN stability and quality? |
| Screen analyst | I1 | Tuning budget and metric choice can confound objective comparisons. |
| Literature retrieval | I2 | Find pre-cutoff predecessors and strong comparators; in current mode, retrieve the sources below if decisive. |
| Prereg / designer | I3 | Compare objectives under equal searches and repeated seeds; measure collapse separately from quality. |
| Baseline champion | I4 | Implement or justify the strongest comparator in the design, with matched access, error and budget. |
| Review panel | I5 | Challenge tuning budget and metric choice can confound objective comparisons. Name a repair, or explain why the control is adequate. |
| Run / implementer | I6 | Recompute a tractable subset of quality metrics. If raw data/code are absent, mark execution blocked. |
| Verdict | I7 | Restrict universal quality claims; evaluate stability as a distinct supported or unresolved claim. |
| Audit | I8 | Check the decisive comparison/proof against sources and quality metrics. Flag evidence that cannot be recomputed. |
| Variants | I9 | Test stability under deliberately limited tuning budgets. |
| Promote | I10 | Preserve this verdict's exact scope, uncertainty and provenance in a disposable record. |
| Lab orchestration | I11 | Request required approvals; stop honestly at missing evidence, state, code or hardware. |

Original: https://arxiv.org/abs/1704.00028

External sources to check: Lucic et al., are GANs created equal? — https://arxiv.org/abs/1711.10337

Review gap: With enough tuning budget, objectives reach similar scores. Tuning-budget confound.

Comment anchors: ml-06 / Input · Screen · Design · Verdict · Sources. Verdicts and source relations remain provisional.

# ml-07 Reinforcement-learning NAS

Zoph & Le 2017, neural architecture search with reinforcement learning

Selected because: Tests whether architecture gains survive equal tuning and search accounting.

Given input I0: Can a searched recurrent cell improve language modeling relative to LSTM?

I7 evidence to assemble: Perplexities, seeds, regularization settings and full search/training costs. Do not invent missing uncertainty, numerical values or preregistration.

| Component | Input | Expected output proposal |
| --- | --- | --- |
| Intake | I0 | Scope: Can a searched recurrent cell improve language modeling relative to LSTM? |
| Screen analyst | I1 | Comparator tuning and architecture-search compute. |
| Literature retrieval | I2 | Find pre-cutoff predecessors and strong comparators; in current mode, retrieve the sources below if decisive. |
| Prereg / designer | I3 | Tune both architectures comparably and include search cost in efficiency metrics. |
| Baseline champion | I4 | Implement or justify the strongest comparator in the design, with matched access, error and budget. |
| Review panel | I5 | Challenge comparator tuning and architecture-search compute. Name a repair, or explain why the control is adequate. |
| Run / implementer | I6 | Recompute a tractable subset of perplexities. If raw data/code are absent, mark execution blocked. |
| Verdict | I7 | Reject a superiority claim unsupported against a well-tuned LSTM; preserve the search procedure itself. |
| Audit | I8 | Check the decisive comparison/proof against sources and perplexities. Flag evidence that cannot be recomputed. |
| Variants | I9 | Test search gains under a fixed total compute budget. |
| Promote | I10 | Preserve this verdict's exact scope, uncertainty and provenance in a disposable record. |
| Lab orchestration | I11 | Request required approvals; stop honestly at missing evidence, state, code or hardware. |

Original: https://arxiv.org/abs/1611.01578

External sources to check: Melis, Dyer, Blunsom, on the state of the art of evaluation in neural language models — https://arxiv.org/abs/1707.05589

Review gap: A well-tuned LSTM outperforms the searched cell. Hyperparameter-budget asymmetry.

Comment anchors: ml-07 / Input · Screen · Design · Verdict · Sources. Verdicts and source relations remain provisional.

# ml-08 Residual networks

He et al. 2016, deep residual learning

Selected because: A pivotal success tests preservation of a result with appropriate controls.

Given input I0: Do residual connections improve optimization and accuracy of deep image classifiers?

I7 evidence to assemble: Optimization curves, validation error, depths, training settings and reproductions. Do not invent missing uncertainty, numerical values or preregistration.

| Component | Input | Expected output proposal |
| --- | --- | --- |
| Intake | I0 | Scope: Do residual connections improve optimization and accuracy of deep image classifiers? |
| Screen analyst | I1 | Residual connection effects versus other training improvements. |
| Literature retrieval | I2 | Find pre-cutoff predecessors and strong comparators; in current mode, retrieve the sources below if decisive. |
| Prereg / designer | I3 | Compare plain and residual networks at equal depth and recipe; separate later training tricks. |
| Baseline champion | I4 | Implement or justify the strongest comparator in the design, with matched access, error and budget. |
| Review panel | I5 | Challenge residual connection effects versus other training improvements. Name a repair, or explain why the control is adequate. |
| Run / implementer | I6 | Recompute a tractable subset of optimization curves. If raw data/code are absent, mark execution blocked. |
| Verdict | I7 | Support depth-specific optimization and accuracy gains if controlled evidence warrants them; a later ResNet result alone is not a causal replication. |
| Audit | I8 | Check the decisive comparison/proof against sources and optimization curves. Flag evidence that cannot be recomputed. |
| Variants | I9 | Test the contribution at new depths and matched recipes. |
| Promote | I10 | Preserve this verdict's exact scope, uncertainty and provenance in a disposable record. |
| Lab orchestration | I11 | Request required approvals; stop honestly at missing evidence, state, code or hardware. |

Original: https://arxiv.org/abs/1512.03385

External sources to check: He et al., bag of tricks for image classification — https://arxiv.org/abs/1812.01187

Review gap: Positive control. Bag of tricks (Amazon) is an independent re-implementation; confirm it re-tests the residual-vs-plain claim rather than only building on ResNet.

Comment anchors: ml-08 / Input · Screen · Design · Verdict · Sources. Verdicts and source relations remain provisional.

# ml-09 AlphaFold

Jumper et al. 2021, highly accurate protein structure prediction with AlphaFold

Selected because: A blind external assessment provides a strong positive calibration case.

Given input I0: Can a structure predictor achieve high accuracy on unseen protein targets?

I7 evidence to assemble: CASP target-level scores, target definitions, coverage and assessor reports. Do not invent missing uncertainty, numerical values or preregistration.

| Component | Input | Expected output proposal |
| --- | --- | --- |
| Intake | I0 | Scope: Can a structure predictor achieve high accuracy on unseen protein targets? |
| Screen analyst | I1 | Target leakage, per-target variability and limits beyond static structures. |
| Literature retrieval | I2 | Find pre-cutoff predecessors and strong comparators; in current mode, retrieve the sources below if decisive. |
| Prereg / designer | I3 | Use blind targets and compare assessors' structural metrics against appropriate methods. |
| Baseline champion | I4 | Implement or justify the strongest comparator in the design, with matched access, error and budget. |
| Review panel | I5 | Challenge target leakage, per-target variability and limits beyond static structures. Name a repair, or explain why the control is adequate. |
| Run / implementer | I6 | Recompute a tractable subset of casp target-level scores. If raw data/code are absent, mark execution blocked. |
| Verdict | I7 | Support high accuracy on assessed targets; do not imply universal accuracy or complete biological function prediction. |
| Audit | I8 | Check the decisive comparison/proof against sources and casp target-level scores. Flag evidence that cannot be recomputed. |
| Variants | I9 | Test failure modes and distribution shifts. |
| Promote | I10 | Preserve this verdict's exact scope, uncertainty and provenance in a disposable record. |
| Lab orchestration | I11 | Request required approvals; stop honestly at missing evidence, state, code or hardware. |

Original: https://doi.org/10.1038/s41586-021-03819-2

External sources to check: Pereira et al., high-accuracy protein structure prediction in CASP14 — https://doi.org/10.1002/prot.26171

Review gap: Blind assessment by independent CASP assessors. Strongly memorized: use mainly as a perturbation parent. CASP14 assessment citation not found in either index (journal reference-list gap); confirm in the PDF.

Comment anchors: ml-09 / Input · Screen · Design · Verdict · Sources. Verdicts and source relations remain provisional.

# ml-10 Transformer

Vaswani et al. 2017, attention is all you need

Selected because: A pivotal independently implemented method provides a positive case and perturbation parent.

Given input I0: Can an attention-only encoder-decoder improve translation quality and training efficiency?

I7 evidence to assemble: BLEU scores, evaluation scripts, training costs, seeds and reimplementation. Do not invent missing uncertainty, numerical values or preregistration.

| Component | Input | Expected output proposal |
| --- | --- | --- |
| Intake | I0 | Scope: Can an attention-only encoder-decoder improve translation quality and training efficiency? |
| Screen analyst | I1 | BLEU comparability, tokenization and hardware-dependent cost. |
| Literature retrieval | I2 | Find pre-cutoff predecessors and strong comparators; in current mode, retrieve the sources below if decisive. |
| Prereg / designer | I3 | Compare strong translation models under matched preprocessing, scoring and resource accounting. |
| Baseline champion | I4 | Implement or justify the strongest comparator in the design, with matched access, error and budget. |
| Review panel | I5 | Challenge bLEU comparability, tokenization and hardware-dependent cost. Name a repair, or explain why the control is adequate. |
| Run / implementer | I6 | Recompute a tractable subset of bleu scores. If raw data/code are absent, mark execution blocked. |
| Verdict | I7 | Support the reported translation regime when evidence matches; do not infer superiority on every sequence task. |
| Audit | I8 | Check the decisive comparison/proof against sources and bleu scores. Flag evidence that cannot be recomputed. |
| Variants | I9 | Test robustness to changed sequence length or data budget. |
| Promote | I10 | Preserve this verdict's exact scope, uncertainty and provenance in a disposable record. |
| Lab orchestration | I11 | Request required approvals; stop honestly at missing evidence, state, code or hardware. |

Original: https://arxiv.org/abs/1706.03762

External sources to check: Ott et al., scaling neural machine translation — https://arxiv.org/abs/1806.00187

Review gap: Independent re-implementation that reproduces and improves the results. Strongly memorized: perturbation parent.

Comment anchors: ml-10 / Input · Screen · Design · Verdict · Sources. Verdicts and source relations remain provisional.

# ml-11 BERT

Devlin et al. 2019, BERT

Selected because: Preserves pretraining gains while isolating an unsupported component claim.

Given input I0: Does masked-language pretraining improve downstream language tasks, and does sentence prediction help?

I7 evidence to assemble: Task scores, compute/data budgets, ablations and replication settings. Do not invent missing uncertainty, numerical values or preregistration.

| Component | Input | Expected output proposal |
| --- | --- | --- |
| Intake | I0 | Scope: Does masked-language pretraining improve downstream language tasks, and does sentence prediction help? |
| Screen analyst | I1 | Training duration, data and sentence-objective effects are entangled. |
| Literature retrieval | I2 | Find pre-cutoff predecessors and strong comparators; in current mode, retrieve the sources below if decisive. |
| Prereg / designer | I3 | Ablate sentence prediction with matched tokens, data and downstream evaluation. |
| Baseline champion | I4 | Implement or justify the strongest comparator in the design, with matched access, error and budget. |
| Review panel | I5 | Challenge training duration, data and sentence-objective effects are entangled. Name a repair, or explain why the control is adequate. |
| Run / implementer | I6 | Recompute a tractable subset of task scores. If raw data/code are absent, mark execution blocked. |
| Verdict | I7 | Support scoped pretraining gains; assess sentence-prediction contribution separately. |
| Audit | I8 | Check the decisive comparison/proof against sources and task scores. Flag evidence that cannot be recomputed. |
| Variants | I9 | Test objective changes under matched training budgets. |
| Promote | I10 | Preserve this verdict's exact scope, uncertainty and provenance in a disposable record. |
| Lab orchestration | I11 | Request required approvals; stop honestly at missing evidence, state, code or hardware. |

Original: https://arxiv.org/abs/1810.04805

External sources to check: Liu et al., RoBERTa: a robustly optimized BERT pretraining approach — https://arxiv.org/abs/1907.11692

Review gap: Replication confirms the gains and finds BERT undertrained; the next-sentence-prediction component is not supported. Claim-level split.

Comment anchors: ml-11 / Input · Screen · Design · Verdict · Sources. Verdicts and source relations remain provisional.

# ml-12 Language model scaling

Kaplan et al. 2020, scaling laws for neural language models

Selected because: A mixed pivotal case tests revision of one claim while preserving another.

Given input I0: How should parameters and tokens scale under a fixed language-model training budget?

I7 evidence to assemble: Loss curves, allocation grids, fit uncertainty and external reevaluation. Do not invent missing uncertainty, numerical values or preregistration.

| Component | Input | Expected output proposal |
| --- | --- | --- |
| Intake | I0 | Scope: How should parameters and tokens scale under a fixed language-model training budget? |
| Screen analyst | I1 | Power-law fit and compute-optimal allocation are distinct claims. |
| Literature retrieval | I2 | Find pre-cutoff predecessors and strong comparators; in current mode, retrieve the sources below if decisive. |
| Prereg / designer | I3 | Sweep parameter/token allocations at fixed compute and test held-out predictions. |
| Baseline champion | I4 | Implement or justify the strongest comparator in the design, with matched access, error and budget. |
| Review panel | I5 | Challenge power-law fit and compute-optimal allocation are distinct claims. Name a repair, or explain why the control is adequate. |
| Run / implementer | I6 | Recompute a tractable subset of loss curves. If raw data/code are absent, mark execution blocked. |
| Verdict | I7 | Preserve supported scaling patterns while revising the allocation rule where matched evidence warrants it. |
| Audit | I8 | Check the decisive comparison/proof against sources and loss curves. Flag evidence that cannot be recomputed. |
| Variants | I9 | Test scaling predictions at new budgets and data regimes. |
| Promote | I10 | Preserve this verdict's exact scope, uncertainty and provenance in a disposable record. |
| Lab orchestration | I11 | Request required approvals; stop honestly at missing evidence, state, code or hardware. |

Original: https://arxiv.org/abs/2001.08361

External sources to check: Hoffmann et al., training compute-optimal large language models (Chinchilla) — https://arxiv.org/abs/2203.15556

Review gap: Power-law form supported; the compute-optimal allocation revised (parameters and tokens scale about equally).

Comment anchors: ml-12 / Input · Screen · Design · Verdict · Sources. Verdicts and source relations remain provisional.
