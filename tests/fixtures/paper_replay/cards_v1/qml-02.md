id: qml-02
title: Quantum convolutional networks
paper: Cong, Choi & Lukin, Quantum Convolutional Neural Networks (arXiv Oct 2018; Nature Physics 2019)
link: https://arxiv.org/abs/1810.03787
type: Mechanism
cutoff: 2018-10-09
domain: qml
profile: advantage

## expected_verdict
Supported (scoped) for phase recognition and sample complexity on quantum inputs; Conditional limitation on any claim of classical hardness. All results are numerical (MPS simulation); later work shows that randomly initialized QCNNs on locally easy data are classically simulable from shadows of the input states.

## I0
Can a hierarchical quantum circuit classify phases with few parameters and favorable sample cost?

## evidence
- Architecture: translation-invariant convolution + measurement-based pooling + fully connected layer; O(log N) parameters for N qubits; QCNN = MERA run in reverse + nested QEC.
- Task 1 (phase recognition): Z2×Z2 SPT phase of H = −JΣZXZ − h1ΣX − h2ΣXX. An exact analytical QCNN reproduces the phase diagram (N = 45, Fig. 2a); depth d = 2 is already accurate; N = 135 output sharpens with d = 1–4 (Fig. 2c, MPS simulation).
- Sample complexity (copies of the input state) vs string order parameters at N = 135: the QCNN advantage grows ~1.73 e^(0.28d) with depth near h1/J = 0.3918 (Fig. 2d inset), "in numerically accessible regimes" and limited by finite-size effects.
- Trained QCNN: N = 15, d = 1, 40 training points on the solvable line h2 = 0, h1 ∈ [0, 2]; reproduces the phase diagram (Fig. 4).
- Task 2 (QEC): 9 qubits, 126 parameters; matches the Shor code under isotropic noise, cuts the logical error rate by 14% (px = 1.8py) or 50% (px = 0.4py) under anisotropic noise, and beats the Shor code (which is worse than no correction) under correlated XX errors (Fig. 5b).
- No hardware run; Rydberg-atom implementation proposed.

## intake
- Scope: classify unknown many-body quantum states (no classical description) into a phase, with fewer input copies than string-order-parameter measurement.
- Regime: 1D Z2×Z2 SPT vs paramagnet / antiferromagnet; N = 15–135 in simulation; noiseless circuits.
- Assumptions: the input arrives as a physical quantum state; the target phase has a MERA-like representative; errors relative to it are local and correctable layer by layer.
- Falsifiers: a classical method with the same number of state copies (e.g. classical shadows + local observables) matches QCNN accuracy and sample cost; or trained QCNNs fail beyond the solvable training line.

## screen
- Must flag: the sample-complexity gain is against string order parameters only, not against all measurement strategies; results are noiseless simulations; the phases are separable by low-weight observables.
- Must request: comparison to shadow-based classical post-processing at matched copies; noise robustness.

## retrieval
- Pre-cutoff must-finds: MERA (Vidal); string order parameters for SPT phases (Pollmann & Turner; Haegeman et al.); classical ML for phases (Carrasquilla & Melko); generic quantum circuit classifiers (Farhi & Neven).
- Current-mode critique: Bermejo et al. 2024: randomly initialized QCNNs only use low-bodyness information, standard benchmarks are "locally easy", and a classical surrogate (Pauli propagation, tensor networks, classical shadows) matches or beats QCNNs up to 1,024 qubits.

## designer
- Arms: exact QCNN, trained QCNN, string order parameter, classical shadows + classical classifier, all at the same number of input copies.
- Datasets: the paper's SPT family plus a phase requiring high-bodyness observables (not locally easy).
- Outcome: QCNN keeps an advantage only where low-bodyness classical surrogates fail.

## champion
- Classical shadows of the input states feeding a classical model of low-weight Pauli features (Bermejo et al.'s surrogate), at matched copies. String order parameters alone are too weak a baseline.

## panel
- Flaw: "sample complexity advantage" is relative to one measurement strategy.
- Repair: add the shadow-based baseline; keep the exact-circuit and QEC results as stated.

## run
- Recompute in simulation: exact QCNN output for N = 15–45 along h1 = 0.5J; trained QCNN on the 40-point solvable line.
- Expected: phase boundary near h2/J ≈ 0.423 (DMRG value in Fig. 2d caption).

## verdict
- Label: Supported (scoped) for phase recognition with O(log N) parameters and fewer copies than SOPs; Conditional limitation for any implied quantum advantage.
- Must say: the quantum-data setting (inputs as states) still needs a quantum device to acquire the data, so simulability of the QCNN's action does not erase that.
- Must not say: QCNNs are refuted; or QCNNs give classical-hardness advantage on these benchmarks.

## audit
- Check: O(log N) parameters; N = 45 / 135 / 15; 40 training points on h2 = 0; 1.73 e^(0.28d) trend; 126 parameters for the QEC case; 14% and 50% reductions.
- Check that Bermejo et al. analyse randomly initialized trained QCNNs, not the paper's exact analytical circuit.

## variants
- Phase-recognition tasks whose order parameter is high-bodyness or nonlocal beyond strings, where shadow surrogates need exponentially many samples.
