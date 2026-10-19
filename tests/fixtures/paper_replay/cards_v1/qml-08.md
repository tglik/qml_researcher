id: qml-08
title: Barren plateaus
paper: McClean et al., Barren plateaus in quantum neural network training landscapes (arXiv Mar 2018; Nature Communications 9, 4812, 2018)
link: https://arxiv.org/abs/1803.11173
type: Theory
cutoff: 2018-03-29
domain: qml
profile: formal

## expected_verdict
Supported (strong), scoped to circuits that approximate 2-designs. Gradient variance decays exponentially in qubit count for sufficiently deep random parameterized circuits. Independent follow-up (Cerezo et al.) confirms it and sharpens the scope: global costs plateau even when shallow; local costs at O(log n) depth do not.

## I0
How does gradient variance scale for circuits approaching a specified random ensemble?

## evidence
- Setting: random parameterized quantum circuits (RPQCs), U(θ) = Π U_l(θ_l)W_l, cost = expectation of a Hermitian H.
- Theorem (appendix): if either part U− or U+ around a parameter forms a 2-design, then E[∂_k E] = 0 and Var[∂_k E] shrinks exponentially in n (scale ~2^(−n), with explicit expressions for the three 2-design cases).
- Mechanism: concentration of measure (Levy's lemma) in the 2^n-dimensional space.
- Numerics: 1D circuits of random Pauli rotations + CZ ladders; gradient of a 2-local Pauli term; variance decays exponentially with n (Fig. 3); vs layers L up to ~500 for even n = 2–24, the variance converges to an n-dependent plateau (Fig. 4).
- Gradient estimation on hardware costs O(1/ε^α) measurements for a small power α, vs O(log 1/ε) classically, so a random walk cannot escape in polynomial time.
- Authors' remedy: structured initial guesses, pre-training, physically motivated ansatzes.

## intake
- Scope: gradients of RPQCs deep enough to approximate 2-designs vanish exponentially in qubit number.
- Regime: random initialization; hardware-efficient ansatzes; depth sufficient for 2-design statistics; noiseless.
- Assumptions: 2-design property of the circuit blocks around each parameter; cost is an observable expectation.
- Falsifier: a circuit family meeting the 2-design condition with gradient variance decaying only polynomially.

## screen
- Must flag: the theorem is conditional on the 2-design assumption; it does not cover shallow, structured, or local-cost circuits by itself.
- Must request: depth at which the 2-design transition happens for the ansatz in question; cost locality.

## retrieval
- Pre-cutoff must-finds: unitary 2-designs from random circuits (Harrow & Low, cited); Levy's lemma / concentration of measure; vanishing gradients in classical deep nets (Hochreiter; Bengio et al.); VQE (Peruzzo et al.).
- Current mode: Cerezo et al. 2020 (independent): global costs give barren plateaus even for shallow circuits; local costs give at worst polynomial vanishing at O(log n) depth; simulations up to 100 qubits. Larocca et al. 2024 review includes McClean as co-author, so it does not count toward independence.

## designer
- Measure Var[∂θ C] vs n (e.g. 4–20 qubits) for: deep random circuits, shallow circuits, local vs global costs. Pre-register exponential vs polynomial fits.

## champion
- Not a performance comparison: the control is a shallow, local-cost ansatz (Cerezo et al.) that should not plateau.

## panel
- Accept the theorem in its stated regime; flag any reading that extends it to all variational circuits.

## run
- Reproduce Fig. 3–4 qualitatively in simulation: exponential decay in n, convergence in L. Feasible locally up to ~16–20 qubits.

## verdict
- Label: Supported (strong), scoped.
- Must say: conditional on 2-design-like randomness; global costs and depth matter (later work); not a ban on all PQCs.
- Must not say: variational QML is impossible; or barren plateaus come from noise (this paper is noiseless).

## audit
- Check: n = 2–24 range; L up to ~500; O(1/ε^α) measurement scaling statement; Cerezo et al. authors share no one with McClean et al.

## variants
- Structured or equivariant ansatzes and local costs outside the 2-design regime; warm starts. Cheapest: local vs global cost at fixed shallow depth, 4–16 qubits.
