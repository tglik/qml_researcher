id: qml-04
title: Quantum PCA
paper: Lloyd, Mohseni & Rebentrost, Quantum principal component analysis (arXiv Jul 2013; Nature Physics 10, 631, 2014)
link: https://arxiv.org/abs/1307.0401
type: Theory
cutoff: 2013-07-01
domain: qml
profile: advantage

## expected_verdict
Supported for density-matrix exponentiation on quantum-state inputs; Conditional limitation for classical data. When the input is classical data loaded via qRAM, matched ℓ2-sampling classical algorithms are only polynomially slower. When the input is genuine copies of an unknown quantum state, that critique does not apply.

## I0
Can principal components of a low-rank state be estimated efficiently?

## evidence
- Density-matrix exponentiation: n = O(t²/ε) copies of ρ implement e^(−iρt) to accuracy ε by repeated infinitesimal swaps (Eq. 1).
- Phase estimation with e^(−iρt) gives eigenvectors/eigenvalues to accuracy ε with t = O(1/ε), so n = O(1/ε³) copies.
- Works when ρ is dominated by a few large eigenvalues (rank R ≪ d); if all eigenvalues are O(1/d), time O(d) is needed.
- Claimed scaling: eigenvectors in O(R log d) vs O(Rd log d) for compressive tomography; non-sparse low-rank Hamiltonians exponentiated in O(log d) vs O(d log d).
- Classical-data application assumes qRAM access to columns |ai⟩ and their norms to build ρ as a covariance matrix.
- Output is quantum: eigenvectors in quantum form; "cannot reveal all the d² entries of ρ in time R log d".
- Pure theory: no numerics, no hardware.

## intake
- Scope: two distinct claims. (A) Quantum input: given copies of ρ, sample its principal eigenvectors/eigenvalues in time polylog(d). (B) Classical input: PCA of a classical covariance matrix exponentially faster, via qRAM.
- Regime: low-rank or spectrally dominated ρ; accuracy ε with O(1/ε³) copies.
- Assumptions: many identical copies are available; qRAM state preparation for claim B; the user is satisfied with quantum-form or sampled output.
- Falsifiers: for B, a classical algorithm with matched ℓ2-sampling access is polylog(d); for A, a lower bound showing copy complexity must grow with d.

## screen
- Must flag: claims A and B have different input models and must be scored separately; the output is a quantum state, not the eigenvector entries; the exponential claim for B rests on qRAM.
- Must request: the end-to-end cost including data loading and readout.

## retrieval
- Pre-cutoff must-finds: HHL and its input/output caveats; quantum compressive tomography (Gross et al.); spectrum estimation by group-representation methods (Keyl–Werner); qRAM (Giovannetti, Lloyd, Maccone).
- Current-mode critique: Tang 2018/2021: classical analogues of qPCA and nearest-centroid clustering under ℓ2 sampling, polynomially slower; "exponential speedups … are simply an artifact of state preparation assumptions".

## designer
- Two separate analyses: (A) copy complexity vs d and ε for quantum-state input, compared with tomography / shadow-based spectrum estimation; (B) end-to-end complexity for classical data, compared with ℓ2-sampling algorithms.
- Report output type for every arm (sample, quantum state, explicit vector).

## champion
- For B: Tang's sampling-based classical PCA (FKV-style). For A: the best quantum-learning baseline that does not exponentiate ρ (measurement-based spectrum estimation, randomized measurements) at matched copies.

## panel
- Flaw: one "exponential speedup" sentence covers both input models. Repair: state that the speedup holds against classical algorithms without sampling access, and separately for quantum inputs.

## run
- Theory check: Eq. 1 swap trick to O(t²/ε); copy count O(1/ε³). Optional small simulation (d = 4–16) of density-matrix exponentiation error vs n.

## verdict
- Label: Conditional limitation. Supported for quantum-state input (claim A); exponential speedup on classical data dequantized (claim B).
- Must say: the dequantization applies because qRAM implies ℓ2-sampling access; it does not transfer to genuinely quantum inputs.
- Must not say: qPCA is refuted outright; or qPCA gives an exponential speedup for classical PCA.

## audit
- Check: n = O(t²/ε); O(1/ε³) copies; O(R log d) vs O(Rd log d); Tang's abstract wording on "state preparation assumptions".

## variants
- Quantum data with no efficient classical description (e.g. outputs of quantum simulation) where ℓ2 sampling is not available, and test whether a separation survives.
