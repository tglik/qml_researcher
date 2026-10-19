id: phys-01
title: Majorana conductance
paper: Zhang et al., Quantized Majorana conductance (arXiv Oct 2017; Nature 556, 74, 2018; retracted 2021)
link: https://arxiv.org/abs/1710.10701
type: Replication
cutoff: 2017-10-29
domain: physics
profile: observation

## expected_verdict
Refuted (evidence withdrawn) for the quantized-plateau claim. The retraction note itself says the authors "can no longer claim the observation of a quantized Majorana conductance". Independent work shows near-2e²/h peaks can arise from non-Majorana states. The verdict must not extend this to "Majoranas do not exist".

## I0
Can conductance measurements distinguish Majorana modes from alternative explanations?

## evidence
- From the paper — Devices: InSb nanowires with epitaxial Al shell; tunnelling spectroscopy; zero-bias peak (ZBP) height.
- From the paper — Claim: a ZBP plateau at 2e²/h that stays constant while magnetic field and tunnel coupling vary; temperature and gate dependence argued to exclude non-Majorana origins; "strongly supports" non-Abelian Majorana zero modes (Abstract).
- From the paper — Theory basis: Majorana symmetry protects quantization against disorder, interactions and tunnel-coupling changes.
- From the retraction (Nature 591, E30, 2021) — Inconsistencies raised by Sergey Frolov and Vincent Mourik (outside the team) between raw data and figures.
- From the retraction — Fig. 2a and ED Fig. 4b had undisclosed charge-jump corrections; Fig. 4b axis mislabelled.
- From the retraction — Re-calibration shifted plateau values +8% above 2e²/h; replotted full-range data fall outside 2σ error bars.
- From the retraction — Expert report: Brouwer, Ensslin, Goldhaber-Gordon, Lee; raw data on Zenodo (10.5281/zenodo.4545577); Expression of Concern, Nature 581, E4 (2020).

## intake
- Scope: whether ZBP-height quantization at 2e²/h, robust across parameters, identifies Majorana zero modes.
- Regime: InSb–Al nanowires, specific gate and field ranges, low temperature.
- Assumptions: the plateau is robust over the full parameter range (not a selected window); calibration is correct; no trivial mechanism gives quantized peaks.
- Falsifiers: full-range data leaving the plateau; trivial (Andreev) bound states producing near-quantized peaks; calibration errors.

## screen
- Must flag: plateau shown over selected ranges; ZBP height alone is not a unique Majorana signature; need for end-to-end correlation (Majoranas come in pairs).
- Must request: unselected raw data over the full sweep; nonlocal / two-end measurements.

## retrieval
- Pre-cutoff must-finds: Mourik et al. 2012 (first ZBPs); Lutchyn et al. / Oreg et al. 2010 proposals; Liu, Sau, Stanescu & Das Sarma 2017 on trivial Andreev bound states mimicking Majorana signatures; Nichele et al. 2017 (near-2e²/h peak).
- Current mode: retraction note 2021; Yu et al. 2020: nearly quantized ZBPs only at one end of the wire, with dips at the other end, undermining the Majorana explanation. Yu et al. includes Bakkers (wire growth) and Frolov/Mourik; the retraction is by the original authors but was triggered by outside critics.

## designer
- Pre-specify plateau criteria (range, tolerance) before analysis; full parameter sweeps; two-end nonlocal conductance; controls with trivial-state simulations.

## champion
- The trivial explanation: smooth-potential / Andreev bound-state models that reproduce near-quantized ZBPs (Liu et al. 2017; Yu et al. 2020).

## panel
- Material flaw: selective data presentation and undisclosed corrections. Repair is not possible within the original claim; require full data and nonlocal tests.

## run
- Zenodo raw data are public: replot ZBP height over the full gate range with the corrected calibration; check the 8% shift and 2σ excursions.

## verdict
- Label: Refuted (quantized-plateau evidence); mechanism unestablished.
- Must say: retracted for data-handling problems; near-quantized peaks have non-Majorana explanations; the general Majorana hypothesis is untested by this retraction.
- Must not say: Majorana zero modes are disproven; or the retraction was purely self-initiated without outside critique.

## audit
- Check: retraction DOI 10.1038/s41586-021-03373-x; Frolov and Mourik named; 8% shift; Fig. 2a / ED Fig. 4b / Fig. 4b issues; Yu et al. one-end-only peaks.

## variants
- Three-terminal nonlocal conductance or topological-gap protocols on independently grown devices.
