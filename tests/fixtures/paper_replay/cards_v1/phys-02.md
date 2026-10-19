id: phys-02
title: LK-99 superconductivity
paper: Lee, Kim & Kwon, The First Room-Temperature Ambient-Pressure Superconductor (arXiv Jul 2023; not peer-reviewed)
link: https://arxiv.org/abs/2307.12008
type: Replication
cutoff: 2023-07-22
domain: physics
profile: observation

## expected_verdict
Refuted. Independent groups reproduced the resistivity drop near ~385 K and traced it to a first-order structural transition in the Cu₂S impurity, without zero resistance. Phase-pure single crystals are insulating and diamagnetic.

## I0
Does a specified synthesized material exhibit ambient-pressure room-temperature superconductivity?

## evidence
- Material: Cu-doped lead apatite Pb₁₀₋ₓCuₓ(PO₄)₆O ("LK-99"), polycrystalline; claimed Tc ≥ 400 K (127 °C) at ambient pressure.
- Claimed signatures: zero resistivity (thin film, 1 µV/cm criterion), critical current (7 mA still at 400 K), critical field, Meissner effect (ZFC/FC magnetization under 10 Oe up to 400 K), heat capacity.
- Mechanism claim: 0.48% volume shrinkage from Cu²⁺ substituting Pb²⁺(2), creating "superconducting quantum wells".
- XRD (Fig. 2): matches lead apatite with "few Cu₂S impurities also shown".
- Non-uniform resistivity attributed to polycrystalline morphology.

## intake
- Scope: bulk superconductivity of LK-99 at ≥ 400 K and ambient pressure.
- Regime: polycrystalline samples from the described solid-state synthesis; thin-film measurement for zero resistivity.
- Assumptions: the observed transport and magnetic signatures come from the apatite phase, not impurities; signatures are simultaneous in the same sample.
- Falsifiers: impurity phases reproducing each signature; phase-pure samples without superconductivity; no true zero resistance or bulk Meissner fraction.

## screen
- Must flag: extraordinary claim; multi-phase samples with Cu₂S named in the paper's own XRD; magnetization under 10 Oe is not a bulk Meissner fraction; no independent lab data; non-peer-reviewed.
- Must request: phase-pure single crystals; signatures measured on the same sample; Cu₂S control.

## retrieval
- Pre-cutoff must-finds: hydride superconductors under pressure (H₃S, LaH₁₀) cited by the paper; the known β→γ structural phase transition of Cu₂S (materials literature); criteria for establishing superconductivity (zero resistance + bulk diamagnetism).
- Current mode (found for this card): Zhu, Wu, Li & Luo 2023: sharp superconducting-like drop with thermal hysteresis, no zero resistance, explained by the first-order β→γ Cu₂S transition near 385 K; Puphal et al. 2023 (MPI Stuttgart): phase-pure single crystals are highly insulating, transparent, diamagnetic; superconductivity ruled out.

## designer
- Independent synthesis; phase analysis (XRD, EDX) per sample; four-probe resistivity to zero within noise; ZFC/FC magnetization with superconducting volume fraction; Cu₂S-only control sample through 300–420 K.

## champion
- The impurity explanation: Cu₂S structural transition (transport) plus ferromagnetic / diamagnetic insulating apatite (magnetism).

## panel
- Material flaws: multi-phase samples; no simultaneous signatures; mechanism asserted without evidence. Not repairable without phase-pure data.

## run
- No raw data released. Recompute only from digitized figures; otherwise BLOCKED. Check that the Cu₂S transition temperature overlaps the claimed transition.

## verdict
- Label: Refuted.
- Must say: the resistivity drop has a known impurity explanation; pure crystals are insulators; no zero resistance in replications.
- Must not say: room-temperature superconductivity in apatites is impossible in principle (only this claim is refuted).

## audit
- Check: Tc 400 K; 0.48% shrinkage; Cu₂S in Fig. 2; Zhu et al. 385 K and no zero resistance; Puphal et al. insulating crystals.

## variants
- Purified samples with controlled Cu₂S content, mapping the transition magnitude vs impurity fraction.
