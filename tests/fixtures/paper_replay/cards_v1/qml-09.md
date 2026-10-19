id: qml-09
title: Classical shadows
paper: Huang, Kueng & Preskill, Predicting many properties of a quantum system from very few measurements (arXiv Feb 2020; Nature Physics 16, 1050, 2020)
link: https://arxiv.org/abs/2002.08953
type: Mechanism
cutoff: 2020-02-18
domain: qml
profile: formal

## expected_verdict
Supported (strong), with its norm conditions. N ~ log(M)·max‖O_i‖²_shadow/ε² measurements predict M observables, with matching lower bounds. Cost is cheap only when the shadow norm is small: local observables (Pauli shadows) or bounded Hilbert–Schmidt norm (Clifford shadows). An independent photonic experiment confirms one instance, not the scaling law.

## I0
Can randomized quantum measurements estimate many specified observables efficiently?

## evidence
- Theorem 1: N ≳ log(M) max_i ‖O_i‖²_shadow / ε² suffices to predict tr(O_iρ) for M observables to additive error ε; N does not depend directly on qubit count.
- Shadow norm: random Clifford measurements → ‖O‖²_shadow ~ tr(O²) (good for fidelity with pure states); random Pauli measurements → ≤ 4^k ‖O‖²_∞ for k-local O.
- Stated limit: a non-local Pauli string (k = n, tr(O²) = 2^n) may need exponentially many shadows, while direct measurement needs ~1/ε².
- Lower bounds: information-theoretic, matched (main text section on lower bounds).
- Numerics up to 160 qubits: fidelity (GHZ, toric code), 2-point correlations, entanglement entropy, energy variance; beats neural-network tomography and direct fidelity estimation (which needs O(2^n/ε⁴) worst case).
- Clifford shadows need ~n²/log n entangling gates per sample.

## intake
- Scope: predicting many linear (and some nonlinear) properties of an unknown state from randomized single-shot measurements.
- Regime: observables with small shadow norm; M up to large; noiseless measurement model in the theory.
- Assumptions: tomographically complete random unitary ensemble; i.i.d. copies of the state; median-of-means estimation.
- Falsifiers: an observable class with small shadow norm needing more than log(M) scaling; or experiments where the error does not track the bound.

## screen
- Must flag: "log M" is only cheap when ‖O‖_shadow is small; Pauli shadows scale as 4^k in locality; global observables can be exponential.
- Must request: the shadow norm for each target observable; hardware noise in the random unitaries.

## retrieval
- Pre-cutoff must-finds: Aaronson's shadow tomography; direct fidelity estimation (Flammia & Liu); generative-model / neural-network tomography (Carrasquilla, Torlai, Melko & Aolita); MPS tomography (Cramer et al.); randomized-measurement Rényi entropy (Brydges et al.).
- Current mode: Struchalin et al. 2020: photonic high-dimensional spatial states; shadows outperform conventional reconstruction for fidelity estimation with limited measurements. Different group (Moscow State), no author overlap.

## designer
- Vary M, locality k and ε; compare shadow estimation with direct per-observable measurement and grouping strategies at matched shots. Pre-register the predicted N from Theorem 1.

## champion
- Direct measurement with commuting-group partitioning of the M observables; for fidelity, direct fidelity estimation.

## panel
- Accept; require each claim to state the measurement ensemble and observable class it covers.

## run
- Fully reproducible in simulation: Pauli shadows on a 10–20 qubit state; estimate many 2-local observables; check error vs log M scaling and the 4^k dependence.

## verdict
- Label: Supported (strong) for the theorem and numerics; independent experimental confirmation of one instance.
- Must say: efficiency is observable-specific (shadow norm); the experiment does not test asymptotic scaling.
- Must not say: any property can be predicted from log M samples; or shadows beat direct measurement for a single global Pauli string.

## audit
- Check: the N bound expression; 4^k Pauli norm; up to 160 qubits; O(2^n/ε⁴) for direct fidelity estimation; Struchalin et al. is a different group.

## variants
- Noisy random unitaries (robust shadows); high-weight observables; derandomized measurements. Cheapest: simulate shadow error for k = 1–6 local observables.
