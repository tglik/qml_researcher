id: phys-04
title: Rydberg revivals
paper: Bernien et al., Probing many-body dynamics on a 51-atom quantum simulator (arXiv Jul 2017; Nature 551, 579, 2017)
link: https://arxiv.org/abs/1707.04344
type: Mechanism
cutoff: 2017-07-13
domain: physics
profile: observation

## expected_verdict
Supported (strong) for the observation; mechanism attributed later. The paper reports robust, persistent oscillations (revivals) of Z₂ order after a quench, with only a qualitative dimer / TDVP picture. "Quantum many-body scars" is a later, independent theoretical explanation. The verdict must keep the observation separate from the mechanism. Neutral-atom relevant.

## I0
Does a constrained Rydberg chain retain coherent revivals for specified initial states?

## evidence
- Platform: up to 51 individually trapped ⁸⁷Rb atoms in a 1D array, Rydberg blockade, programmable Ising-type Hamiltonian with tunable detuning Δ(t) and Rabi frequency Ω.
- Phases: Z₂, Z₃, Z₄ crystals prepared adiabatically; perfect Z₂ state measured with 54(4)% probability, 77(6)% after correcting for detection infidelity (Fig. 3c); domain-wall statistics vs DMRG (D = 256) without free parameters.
- Non-thermal state: measured correlation length 3.03(6) vs thermal prediction 4.48(3) at the same domain-wall density.
- Quench: sudden jump to Δ = 0 from deep Z₂; oscillations between the crystal and its complement persist over several periods, frequency "largely independent of system size" (9 and 51 atoms); revival period 1.38(1)× slower than the single-atom Rabi period (Fig. 6).
- Explanation offered: dimer spin-1 picture + MPS/TDVP variational ansatz; the Z₂ state is at infinite effective temperature, so persistence is unexpected.

## intake
- Scope: (A) programmable Rydberg simulator up to 51 atoms prepares ordered phases; (B) after a quench from Z₂, order revives coherently and persistently.
- Regime: 1D chains, nearest-neighbour blockade, quench to Δ = 0, ~µs timescales.
- Assumptions: state preparation and detection fidelities are accounted for; revival is intrinsic, not a finite-size or control artifact.
- Falsifiers: revivals absent for larger arrays or other initial states predicted to revive; revivals explained by experimental imperfections.

## screen
- Must flag: revival is an observation; the paper does not establish a mechanism; finite coherence limits the number of periods.
- Must request: initial-state dependence (Z₂ vs other product states), size scaling, and numerics with the full 1/R⁶ potential.

## retrieval
- Pre-cutoff must-finds: eigenstate thermalization review (D'Alessio, Kafri, Polkovnikov & Rigol); Rydberg gates and blockade (Jaksch et al.); interacting Fibonacci / constrained chains (Lesanovsky & Katsura); 2D Rydberg arrays (Labuhn et al.).
- Current mode: Turner et al. 2017: "quantum many-body scars" in the PXP / Fibonacci chain; special eigenstates explain the revivals; single-particle Hilbert-space hopping model up to L = 32. Different group, theory only.

## designer
- Vary initial state (Z₂ vs random product states), detuning, chain length and decoherence; pre-register predicted revival periods from exact diagonalization / TDVP.

## champion
- Exact diagonalization (≤ 25 atoms) and MPS/TDVP simulation of the PXP and full 1/R⁶ models; a thermalizing initial state as control.

## panel
- Accept the observation; require that any "scar" wording is attributed to later work, not to this paper's evidence.

## run
- ED of the PXP chain at N = 16–24 from Z₂: reproduce revivals and a period ~1.3–1.5× the free Rabi period; compare to a non-revival initial state.

## verdict
- Label: Supported (strong) observation; mechanism supported by later independent theory.
- Must say: the original evidence supports revivals, not scars; scars arrived via Turner et al.
- Must not say: this paper discovered quantum many-body scars; or the oscillations were an artifact.

## audit
- Check: 51 atoms; 54(4)% raw / 77(6)% corrected; ξ = 3.03 vs 4.48; period ratio 1.38(1); Turner et al. L = 32.

## variants
- Test scar-specific predictions on new initial states (e.g. Z₃) or 2D arrays.
