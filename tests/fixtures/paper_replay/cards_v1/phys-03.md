id: phys-03
title: Neural quantum states
paper: Carleo & Troyer, Solving the quantum many-body problem with artificial neural networks (arXiv Jun 2016; Science 355, 602, 2017)
link: https://arxiv.org/abs/1606.02318
type: Mechanism
cutoff: 2016-06-07
domain: physics
profile: method-benchmark

## expected_verdict
Supported (scoped), tier B at most. RBM neural quantum states reach controllable, very high ground-state accuracy on 1D TFI/AFH (80 spins) and the 2D AFH (10×10), beating Jastrow, EPS and PEPS at the reported hidden-unit densities. The benchmark adjudicator includes Carleo as an author, so it is not independent.

## I0
Can a neural variational wavefunction approximate spin-model ground states accurately?

## evidence
- Ansatz: restricted Boltzmann machine Ψ(s) with hidden-unit density α = M/N; translation symmetry imposed; optimized by stochastic reconfiguration (variational Monte Carlo); cost comparable to ground-state QMC.
- Models: transverse-field Ising (1D, h = 1/2, 1, 2), antiferromagnetic Heisenberg (1D, 2D), periodic boundaries.
- Accuracy (Fig. 3): relative energy error ε_rel = (E_NQS − E_exact)/|E_exact| decreases systematically with α; 1D TFI on 80 spins reaches below 10⁻⁸ at some h; 1D AFH (80 spins) beats Jastrow; 2D AFH on 10×10 beats EPS and PEPS reference values at α up to 16 (2D reference from QMC, which is sign-free here).
- Dynamics: unitary time evolution after quenches via time-dependent VMC, compared to exact results.

## intake
- Scope: RBM-based NQS as variational ground states (and dynamics) for 1D/2D spin models.
- Regime: sign-free (or exactly solvable) benchmark models; system sizes up to 100 spins; hidden density α ≤ 16.
- Assumptions: exact or QMC references are correct; stochastic optimization converges; symmetry projection is legitimate.
- Falsifiers: on frustrated or fermionic models, NQS fails to beat strong variational methods at matched cost; or energy errors do not shrink with α.

## screen
- Must flag: benchmarks are sign-problem-free or integrable; comparison to EPS/PEPS uses literature values, not matched compute; optimization reliability not characterized across seeds.
- Must request: frustrated-model tests (J1–J2); compute-matched comparisons with DMRG/PEPS.

## retrieval
- Pre-cutoff must-finds: variational Monte Carlo and stochastic reconfiguration (Sorella); PEPS and EPS benchmarks for 2D Heisenberg; Jastrow wavefunctions; Le Roux & Bengio RBM universality; Carrasquilla & Melko (ML phases, 2016).
- Current mode: Wu et al. 2023: V-score benchmark across tensor networks, NQS, PQCs and physically motivated ansatzes on many models; Carleo is corresponding author, so not independent.

## designer
- Compare NQS, DMRG/PEPS and VMC-Jastrow on the paper's models and on a frustrated model, at matched wall-clock; report energy, variance (V-score) and seed spread.

## champion
- DMRG in 1D; PEPS / DMRG on cylinders and QMC (sign-free) in 2D; for frustrated models, state-of-the-art PEPS or DMRG.

## panel
- Accept the accuracy claims for the models shown; flag "solving the many-body problem" as broader than the evidence.

## run
- NetKet reproduces the 1D TFI / AFH ground states (N ≤ 40 on a laptop); verify ε_rel falls with α. 10×10 2D runs need a cluster.

## verdict
- Label: Supported (scoped) for tested models and tolerances; tier B (non-independent benchmark).
- Must say: accuracy shown on sign-free/integrable benchmarks; broader superiority needs independent, compute-matched benchmarks.
- Must not say: NQS solve the many-body problem in general; or the result is unverified (exact/QMC references exist).

## audit
- Check: 80-spin 1D chains, 10×10 2D lattice, α values (4, 16), Fig. 3 comparisons to Jastrow/EPS/PEPS; Wu et al. author list includes Carleo.

## variants
- J1–J2 Heisenberg at maximal frustration with an independent group's benchmark; convergence across seeds.
