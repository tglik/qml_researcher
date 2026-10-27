# Mocks: qml-06

Gold upstream outputs. Each section header names the components that receive it. Written by the
eval authors from the paper's design (arXiv:2011.01938, Appendix L) and the lab method. A mock
passes on a decision and never states what a downstream key scores.

## analysis
For: intake

- E1 is a product state: ⟨Zⱼ⟩ = cos 2xⱼ, ⟨Yⱼ⟩ = −sin 2xⱼ, ⟨Xⱼ⟩ = 0. Its PFK is a classical kernel in
  closed form (Rule 1, simulable structure: 🔴 for E1).
- E2 and E3: no known classical shortcut for the Pauli features at scale [ASSUMPTION]; every size
  in the budget (≤ 13 qubits) is statevector-simulable.
- Loading (Rule 7): n single-qubit rotations (E1), O(n²) phases (E2), T·n two-qubit gates (E3). 🟢.
- Readout (Rule 6): PFK needs one circuit family per input and 3·q expectation values at precision
  ε, about 3q/ε² shots per input. The fidelity kernel needs one overlap circuit per pair, O(N²).
- Rule 4: training and prediction on 600 examples of dimension 12 take milliseconds classically.
  The claim is about prediction quality at a fixed training-set size, not cost.
- Hypotheses: H1 on image labels; H2 on quantum-process labels. Recommend ASK-HUMAN on scope:
  the E1 arm is classical by construction.

## hypothesis
For: designer, champion

- **H1 (image labels).** On fashion-MNIST dress versus shirt, compressed to n principal components,
  PFK on E2 or E3 has lower test classification error than the best tuned classical model by at
  least 2 percentage points at the largest n tested, and the gap grows with n.
  Disproof: the best tuned classical model is within 2 points of PFK, or ahead, at every n tested.
- **H2 (quantum-process labels).** On regression labels produced by a fixed random spin-chain
  evolution applied after the embedding (then ⟨Z₁⟩ measured), PFK on E2 or E3 has at least 10% lower
  mean absolute error than the best tuned classical model at the largest n tested.
  Disproof: as H1, at 10% relative error.
- **Operating point.** Scientific target: n = 2 to 12 input dimensions (up to 13 qubits),
  600 training and 200 test examples, statevector simulation. No latency or cost target.
- **Classical method that wins if false:** the best of a tuned classical suite.
- **Decision:** whether to fund a PFK hardware demonstration next quarter.

## prior_work
For: designer

Pre-cutoff work only, from the paper's own bibliography. One line each on what the work says.
- Havlíček et al., Nature 2019: quantum feature-map kernels; the IQP-type map is conjectured hard
  to simulate; 2-qubit hardware demonstration on data generated for the map.
- Schuld & Killoran, PRL 2019: encoding data in quantum states defines a kernel; quantum models as
  kernel methods.
- Schuld, Sweke & Meyer, 2020: the data encoding fixes the frequency spectrum a quantum model can
  express.
- Lloyd, Schuld, Ijaz, Izaac & Killoran, 2020: trained quantum embeddings for classification.
- Huang, Kueng & Preskill, Nat. Phys. 2020: classical shadows estimate many local observables from
  few randomized measurements.
- Liu, Arunachalam & Temme, 2020: a provable quantum kernel speedup for a discrete-logarithm
  learning problem, on fault-tolerant hardware.
- Jacot, Gabriel & Hongler, 2018; Arora et al., 2019: training very wide neural networks is
  equivalent to a kernel method (the neural tangent kernel).
- McClean et al., Nat. Commun. 2018: gradients of random parameterized circuits vanish
  exponentially in the number of qubits.
- Blank et al., 2020; Bartkiewicz et al., 2020: small experimental quantum kernel classifiers.
- Xiao, Rasul & Vollgraf, 2017: fashion-MNIST.

## screen
For: designer

PASS. No design constraints beyond the lab method. (Mock: the screen is not under test.)

## proposal
For: implementer, verdict, audit. The champion receives it without "Classical arms".

- **Data.** PCA on all dress (class 3) and shirt (class 6) fashion-MNIST training images to n
  components; standardize each component; per seed, draw 800 examples and split 600 train /
  200 test. n ∈ {2, 4, 6, 8, 10, 12}; seeds 0, 1, 2.
- **Tasks.**
  - C: dress (+1) versus shirt (−1). Metric: test classification error.
  - Q: y = ⟨Z₁⟩ after U = [Πⱼ exp(−i Jⱼ (XⱼX_{j+1} + YⱼY_{j+1} + ZⱼZ_{j+1}))]¹⁰ applied to the
    embedded state, Jⱼ ~ N(0, 1) fixed per seed. Metric: test mean absolute error.
  - E (engineered, existence test): labels built to maximize the separation between PFK and the
    closest classical kernel: y = √K_PFK v, v the top eigenvector of
    √K_PFK K_C (K_C + λI)⁻² √K_PFK at the classical kernel and λ minimizing g (below); label =
    sign(y − median y); then 10% of labels replaced by random ±1. Metric: test classification error.
- **Quantum arms.** PFK and the fidelity kernel on E1, E2, E3. SVM (C, E) or kernel ridge (Q),
  C ∈ {0.006 … 1024} (18 values); PFK γ ∈ {0.25, 0.5, 1, 2, 3, 4, 5, 20} / (q · Var(features)).
- **Classical arms.** Gaussian-kernel SVM or kernel ridge (same C grid, γ grid / (n · Var x)),
  linear SVM or ridge, random forest and gradient boosting (depth 2–5, 25–500 trees), AdaBoost
  (25–500), two-layer MLP (width 10–200). Inputs: the n standardized components.
- **Tuning.** 3-fold cross-validation on the training split for every arm. The test split is drawn
  before modeling and never used for selection.
- **Diagnostics (no gate).** Effective dimension d of each kernel matrix (normalized to trace N);
  geometric difference g(K_C‖K) = min over classical kernels (linear, Gaussian at 9 widths) and
  λ ∈ {1e−5 … 0.1} of √‖√K · K_C (K_C + λI)⁻² · √K‖ (spectral norm), subject to the training-error
  condition λ·√‖√K (K_C + λI)⁻² √K‖ < 0.045; mean off-diagonal value of the fidelity kernel.
- **Training-size sweep.** E2 and E3 at n = 10, training size 100, 200, 400, 600, same test split.
- **Gates.** All on mean over 3 seeds, gap = best classical error − PFK error.
  - G-C (H1): pass if the gap ≥ 0.02 at n = 12 for E2 or E3 and the gap is larger than twice its
    seed standard deviation. Gray zone: a pass at one embedding only is reported as conditional on
    that embedding.
  - G-Q (H2): pass if PFK mean absolute error ≤ 0.9 × best classical at n = 12 for E2 or E3.
    The labels are a constructed proxy for quantum-process data: a pass opens a follow-up on a real
    quantum data source, and no decision fires on it alone (Rule 2).
  - G-E (existence): same rule as G-C, on task E. Synthetic: no decision fires on it alone (Rule 2).
- **NO-GO sentences, written in advance.**
  - G-C: "On dress-versus-shirt images at up to 12 components, PFK does not beat a tuned classical
    suite."
  - G-Q: "On quantum-process labels at up to 13 qubits, PFK does not beat a tuned classical suite."
- **Simulation.** Statevector, complex128: 800 states × 16·2^q bytes, ≤ 105 MB at q = 13.

## gate_table
For: verdict, audit

In [`gate_table.md`](gate_table.md), built from the reference rerun by
`scripts/paper_replay/reference/build_qml06_mocks.py`. Numbers and mechanical gate results only.

## verdict_to_audit
For: audit

Raw per-seed results: [`raw_results.csv`](raw_results.csv). The verdict below contains planted
errors, listed in `key.yaml` under `audit`. The auditor sees only the text below this line.

> **Verdict: qml-06, Pauli-feature kernel (PFK)**
>
> **H1, image labels: NO-GO-FINAL.** On dress versus shirt, the best tuned classical model beats PFK
> at every size: at n = 12, 0.062 against 0.388 (E2) and 0.393 (E3) test error (gate table, task C).
> At n = 10 the best classical error is 0.062. G-C fails on both embeddings. N1–N5 all hold: the
> classical suite matches the published state of the art on fashion-MNIST. Quantum kernels do not
> help image classification.
>
> **H2, quantum-process labels: GO.** PFK on E3 reaches 0.57× the best classical mean absolute error
> at n = 12 (0.094 against 0.165), and E2 reaches 0.82× (0.034 against 0.041). G-Q passes on both.
> This is a quantum advantage for learning from quantum-process data.
>
> **Engineered labels (existence test).** PFK beats the best classical model by 0.155 (E2) and
> 0.173 (E3) at n = 12. The advantage grows with training size: on E3 at n = 10 the gap goes from
> 0.17 at 100 training examples to 0.23 at 600. PFK on E1 also beats the classical suite here
> (0.160 against 0.207 at n = 12), although PFK on E1 is a classical kernel in closed form.
>
> **Mechanism.** The fidelity kernel's effective dimension approaches the number of examples
> (745 of 800 on E2 at n = 12) and its geometric difference with the classical kernels falls with n,
> so it generalizes poorly. On quantum-process labels the fidelity kernel is exact at n ≤ 4 and
> degrades as n grows. PFK keeps a lower dimension and a larger geometric difference.
>
> **Decision.** Fund the PFK hardware demonstration on quantum-process data next quarter.
