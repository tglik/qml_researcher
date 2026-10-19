id: qml-05
title: Data re-uploading
paper: Pérez-Salinas et al., Data re-uploading for a universal quantum classifier (arXiv Jul 2019; Quantum 4, 226, 2020)
link: https://arxiv.org/abs/1907.02085
type: Benchmark
cutoff: 2019-07-03
domain: qml
profile: advantage

## expected_verdict
Mixed. The universality argument stands (a single qubit with re-uploading maps onto the universal approximation theorem). The empirical claim of being "at least comparable" to classical methods rests on default-hyperparameter baselines. Under a large tuned benchmark, out-of-the-box classical models outperform it.

## I0
Can repeated data encoding yield a universal classifier and useful predictive performance?

## evidence
- Model: layers L(i) = U(φi)·U(wi∘x) on one qubit (or 2 / 4 qubits, with or without CZ entanglement); (3 + d)N parameters for one qubit, N layers (§5).
- Universality: mapped to the Universal Approximation Theorem (§3.1–3.2); authors state the single-qubit classifier "cannot carry any quantum advantage" over neural networks.
- Training: L-BFGS-B, fidelity and weighted-fidelity costs; L = 1–10 layers; test set an order of magnitude larger than the training set, fixed seed; code released.
- Results (simulation only): circle problem >90% with 2 layers (12 parameters, Table 1); 3-circles 92% max with 10 layers, single qubit (Table 2); annulus 93% single qubit, up to 96% with more qubits (Table 4).
- Classical comparison (Table 5, §6.5): scikit-learn MLP (1 hidden layer, 100 ReLU units, lbfgs) and default SVC; "some changes in the initialization parameters were tested with no significant differences". Claim: single-qubit classifier "at least comparable" on all nine problems.
- All datasets are synthetic, low-dimensional (2D–4D).

## intake
- Scope: (A) formal: re-uploading makes a 1-qubit circuit a universal approximator; (B) empirical: competitive accuracy on synthetic low-dimensional tasks.
- Regime: 1–4 qubits, noiseless simulation, 2D–4D synthetic data.
- Assumptions: UAT analogy holds for the chosen layer form; trainable classical rescaling wi is part of the model; default classical baselines are representative.
- Falsifier for B: tuned classical models (MLP, SVC with tuned C/γ, gradient boosting) beat it on the same data or on standard benchmarks.

## screen
- Must flag: universality ≠ advantage (authors say so); baselines are untuned defaults; datasets are toy and synthetic.
- Must request: tuned baselines with equal search budget; repeated seeds (the paper uses one fixed seed).

## retrieval
- Pre-cutoff must-finds: Cybenko / Hornik universal approximation; Schuld et al. circuit-centric classifiers; Havlíček et al. and Schuld & Killoran quantum feature spaces; Mitarai et al. quantum circuit learning.
- Current-mode critique: Bowles, Ahmed & Schuld 2024: 12 QML models, 160 datasets; out-of-the-box classical models outperform; DataReuploadingClassifier "performs relatively well" among QNNs; removing entanglement lowers its accuracy; ablation of rescaling, mixing and cost function (Fig. 15).
- Not found by inventory but relevant: Schuld, Sweke & Meyer 2021 (re-uploading models are truncated Fourier series), a direct follow-up on expressivity.

## designer
- Separate a proof check (A) from an empirical comparison (B).
- For B: same splits, ≥ 5 seeds, equal hyperparameter-search budget for quantum and classical models, include real datasets.

## champion
- Tuned MLP and RBF-SVC (grid over C, γ), plus gradient boosting. Default SVC alone is a weak baseline.

## panel
- Flaw: comparability claim rests on untuned baselines and one seed. Repair: rerun Table 5 with tuned baselines; keep the universality result.

## run
- Code is public: rerun the circle and annulus problems; reproduce ~90% (circle, 2 layers) and ~93% (annulus, 10 layers). Then add tuned classical baselines on the same seeds.

## verdict
- Label: Mixed. Universality: Supported. Competitive performance: not supported beyond untuned toy comparisons.
- Must say: the formal result and the benchmark result are separate claims; the authors themselves deny quantum advantage.
- Must not say: data re-uploading beats classical models; or the universality proof is wrong.

## audit
- Check: (3 + d)N parameter count; Table 5 baseline settings (100-unit MLP, default SVC); 92% and 93% figures; Bowles et al. include a model named DataReuploadingClassifier citing this paper.

## variants
- Rerun the paper's 9 problems with tuned baselines and 10 seeds. Cheapest discriminating test: one problem (3-circles) with a tuned RBF-SVC.
