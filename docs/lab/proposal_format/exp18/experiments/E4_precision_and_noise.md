---
thread: materials_configuration_space/18_config_space_features
experiment: E4 (PROPOSAL.md phase P4)
tests: H2 precision (gain at ±0.01, on the measured noise); measures the shot and error inputs of H5
status: not started
depends_on: E3 (Q1n results to re-read); E2.1 pilot clusters
feeds: E3 (re-read of the precision check), E5 (measurement groups, noise factor, error budget)
budget: 800 core-h simulation + 5 core-h models; 8 GB peak; 6 wall-days; halt at 2×
code: P4_noise/
date: 2026-10-28
---

# E4 — Does the gain survive realistic measurement noise, and what does measurement cost?

## Question and why
E3's precision check uses a simple noise model: Gaussian noise of ±ε on each feature. E4 checks
that model against real measurement, and measures three numbers that E5's cost depends on:
1. **Shot noise per feature.** We sample the 23 features from the exact 24-qubit state, the way
   hardware would measure them. Some features combine many Pauli terms, so they may be noisier
   than the model assumes.
2. **Measurement groups.** How many separate measurement settings does the full set need (B)?
3. **Hardware error bias.** How much does each feature drift as gate errors accumulate? This sets
   the logical error rate per operation (p_L*) the hardware must reach.

Two rules require this. The lab requires finite-shot results to be checked against exact ones
before a cost is quoted. And the "noise" item of the classical-competitor checklist stays open
until a noisy simulation has run.

## What we expect, and why
- **Shot noise close to the model.** The median noise factor V should be ≤ 4. The spin-correlation
  features combine many Pauli terms, so they will sit above the median.
- **About 10 measurement groups.**
- **Bias coefficient a between 0.3 and 3:** small for single-orbital occupations, near 1 for spin
  correlations.

## Design
**State.** The exact 12-orbital solution from E3, written as a 24-qubit state (256 MiB). The
noisy runs use quantum trajectories, because a full density matrix at 24 qubits does not fit in
memory.

| Step | What | Instances | Output |
|---|---|---|---|
| E4.1 shot noise | measure the 23 features in commuting groups at 10², 10⁴ and 10⁶ shots per group; compare with exact values. Also emulate amplitude estimation (a quadratically cheaper readout) to measure its real overhead | 20 clusters | noise factor V per feature; amplitude-estimation overhead |
| E4.2 groups | count the commuting groups; compute each feature's Pauli 1-norm (sets amplitude-estimation cost) | same | B; 1-norm per feature |
| E4.3 noisy proxy | a ~10³-gate circuit (mean-field preparation + 2 time steps) with depolarizing error p ∈ {10⁻⁵, 3 × 10⁻⁵, 10⁻⁴, 3 × 10⁻⁴}; ≥ 400 trajectories per cluster and rate | 5 clusters | bias per feature vs total error; fitted coefficient a |

## Decision rules
**Shot noise (E4.1).**
- The model holds if the median V across features is ≤ 4.
- Whatever V is, E3's noisy-feature results are re-read at the measured V for each feature, without
  re-tuning, and E3's precision check is decided on that re-read.

| Measured V | What happens |
|---|---|
| ≤ 4 | the planned shot count stands (within 4×) |
| 4–10 | re-read E3; if the precision check flips from pass to fail, the result is "fails at the measured shot noise", not "shown absent" |
| > 10 | regroup the measurements once (B grows); features and ε unchanged |

**Error budget (E4.3).**
- We fit bias = a · (1 − e^(−p·L)) for each feature, using only points with p·L ≤ 0.3.
- If the largest a lies in [0.1, 10] with R² ≥ 0.9 on ≥ 4 of 5 clusters, the required logical error
  is p_L* = 0.01 / (a × operations per circuit). It goes to E5 and becomes a stated condition of any
  CONDITIONAL-GO.
- Otherwise E5 uses a = 10, and the noise item stays open in the verdict.

**What ends the quantum claim:**
- The re-read gain fails at every precision down to ±0.001, on every holdout that passed in E3.
- Or the measured groups × noise factor raises E0's runtime by another ≥ 10×. E5 then produces only
  its sensitivity table.

E4 never stops the classical program. E4.1 runs even if E3 ended the quantum claim, for the
record.

**Why these thresholds.**
- **V ≤ 4:** keeps the planned shot count within 4× of the truth. At that resolution, E0's 4,200×
  verdict cannot change.
- **p·L ≤ 0.3:** the error budget lives near p_L × operations ≈ 0.01. Higher error rates saturate
  every feature and say nothing about it.

## Pitfalls and controls
- **The proxy circuit is not the algorithm.** E4.3 tests how errors accumulate on a 10³-gate
  circuit. The real algorithm's circuit is very different, so a is carried into E5 as an assumption
  in the band [0.1, 10], and p_L* is labelled "projected".
- **Rare errors are hard to sample.** At p·L = 0.01 most trajectories have no error at all. We
  sample trajectories that contain at least one error and weight the error-free branch exactly;
  otherwise 400 trajectories would not resolve the bias.
- **Simulation time is not hardware time.** Trajectory wall-clock is never reported as quantum
  runtime.

## Budget and fallbacks
- **Plan:** 800 core-h simulation (8,000 trajectories at ~0.1 core-h each, plus ~20 for E4.1 and
  E4.2); 5 core-h to re-read E3; 8 GB peak; 6 wall-days.
- **Fallback:** if trajectories at 24 qubits exceed 2× the plan, run E4.3 at 20 qubits (10
  orbitals) with the same error rates and trajectory count. E4.1 is never cut.

## Do not
- Re-tune ε or the precision ladder.
- Change E3's noisy-feature results other than by substituting the measured V.
- Report trajectory time as hardware time.
- Extend the proxy circuit to the full algorithm; it tests the accumulation law only.

## Locked rules this experiment reads
Rule text lives in `PROPOSAL.md` (P4 section) and `frozen_definitions.md`; it is never restated
here. `P4.shot_model` · `P4.noise_model` · `P4.gray_zone` · `P4.stop_rule` ·
`P3.H4.threshold` · `def.epsilon_ladder` · `def.resource_model`
