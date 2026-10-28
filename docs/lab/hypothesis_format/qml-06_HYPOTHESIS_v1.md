---
thread: paper_replay/qml-06
entry_path: algorithm
source: tests/fixtures/paper_replay/cards_v2/qml-06/input.md + intake_answers.md + mocks.md §analysis
source_hypothesis_card: none
checklist: 5/5
status: complete
date: 2026-10-27
---

# Hypothesis — does a quantum "Pauli fingerprint" kernel beat classical ML on small datasets?

## In one paragraph
We encode each data point into a quantum state, measure a few simple numbers from it, and use
those numbers as features for a standard kernel classifier. The proposer believes these features
capture structure that classical models miss, because the states that produce them are hard to
simulate. We will test this on two tasks (image classification and labels produced by a quantum
process) against the strongest tuned classical models. **If a tuned classical model matches the
quantum kernel at every size we can simulate, we drop the idea and do not fund a hardware
demonstration.**

## Background the reader needs
- **Kernel method.** A model that learns from a similarity score k(x, x′) between pairs of inputs.
  An SVM with a Gaussian (RBF) kernel is the standard example. Swapping the kernel swaps which
  patterns the model can learn. (Schölkopf & Smola, *Learning with Kernels*, 2002.)
- **Quantum kernel.** A kernel whose similarity score is computed on a quantum computer: each input
  is turned into a quantum state by a circuit (the *embedding*), and the states are compared.
  (Havlíček et al., Nature 2019; Schuld & Killoran, PRL 2019.)
- **Pauli expectation ⟨X⟩, ⟨Y⟩, ⟨Z⟩.** Three numbers between −1 and 1 that summarize one qubit,
  estimated by repeating the circuit and averaging measurements. q qubits give 3q numbers.
- **Classical simulation.** A computer can track q qubits exactly with 2^q numbers. At 13 qubits
  that is 8,192 numbers, which a laptop handles in milliseconds. Quantum hardness only begins
  around 50 qubits and above, and only for some circuits.

## The algorithm
```
image ─► PCA to n numbers ─► encode into n qubits ─► measure ⟨X⟩,⟨Y⟩,⟨Z⟩ of every qubit
                                                      = fingerprint vector f(x), length 3q
       ─► Gaussian kernel on fingerprints: k(x,x′) = exp(−γ‖f(x) − f(x′)‖²) ─► SVM / kernel ridge
```
In short, **the quantum computer is a feature extractor and everything after it is a standard
RBF-kernel model.** Three embeddings are proposed:
- **E1:** rotate each qubit by its own input value. The qubits never interact.
- **E2:** two layers of rotations with pairwise products xⱼxₖ between qubits (Havlíček's
  embedding, conjectured hard to simulate at scale).
- **E3:** a spin chain whose couplings are set by the input, evolved over time from random
  starting states (n + 1 qubits).

Also proposed, as an alternative: the **fidelity kernel**, which compares whole states directly,
k(x, x′) = |⟨x|x′⟩|².

## Why this algorithm, and why built this way
**The proposer's reason:** the fingerprint comes from states that are hard to simulate at scale, so
the kernel should capture structure classical kernels miss.

**Why fingerprints instead of comparing whole states** [analysis]: the fidelity kernel compares
states with 2^q entries. As qubits grow, two different inputs tend to give nearly unrelated states,
so the kernel matrix approaches the identity and the model can only memorize. The fingerprint
compares only per-qubit summaries, which stay comparable as q grows. It is also cheaper to
measure: one circuit per input instead of one per pair of inputs.

**What must be true for the claim to hold.** Each link is tested by the hypothesis in brackets:
1. The fingerprint is a different function of x from anything a tuned classical model already
   uses. (H1, H2)
2. That difference matters for the labels, so it lowers test error. (H1 for images, H2 for
   quantum-process labels)
3. The advantage grows with the number of qubits rather than shrinking. (H3)
4. At hardware size (50–100 qubits) the fingerprint is still hard to compute classically.
   (Not testable here: every size we can run is classically simulable. See the known risks.)

## Hypotheses
**H1 — Image labels.** On fashion-MNIST dress vs shirt, compressed to n PCA components, the
quantum kernel (E2 or E3) has a test classification error at least **2 percentage points lower**
than the best tuned classical model at the largest n tested (n ≈ 12).
*Disproof:* the best classical model is within 2 points, or ahead, at every n tested.

**H2 — Quantum-process labels.** When labels come from a quantum process (a fixed random spin-chain
evolution applied after the embedding, then one qubit measured), the quantum kernel has at least
**10 % lower mean absolute error** than the best tuned classical model at the largest n tested.
*Disproof:* the best classical model is within 10 %, or ahead, at every n tested.

**H3 — The gap grows with size.** Wherever H1 or H2 holds, the gap at the largest n is larger than
at the smallest n, by more than the seed-to-seed spread.
*Disproof:* the gap is flat or shrinks as n grows.

## What we compare against
The **best of a tuned classical suite**, with the same inputs and the same tuning budget as the
quantum arm. At minimum this includes an RBF-kernel SVM, gradient boosting and a small neural
network. The designer and the classical-competitor champion fix the final list. The proposer's
"a tuned SVM or gradient boosting, I suppose" is a starting point, not the bar.
Note: the quantum kernel on **E1 counts as a classical model** (see the known risks).

## Where the claim must hold
| | |
|---|---|
| Input size | n = 2 to 12 PCA components (up to 13 qubits) |
| Data | about 600 training and 200 test examples per task |
| Metric | test classification error (H1); mean absolute error (H2) |
| Compute | statevector simulation on one workstation; no hardware |
| Cost / latency target | none; this is a prediction-quality question |
| Hardware | none chosen; a later demonstration would use 50–100 qubits |

## Decision this changes
Whether we spend next quarter on a hardware demonstration of the Pauli-fingerprint kernel.
- H1 or H2 holds **and** H3 holds → fund the demonstration.
- Otherwise → drop it and record the result as a negative finding.

## Known risks (raised before any data)
- **E1 is classical by construction.** Its qubits never interact, so its fingerprint is
  (cos 2xⱼ, −sin 2xⱼ) for each input value. Its kernel is a classical kernel in closed form.
- **A win here would not show a quantum advantage.** At ≤ 13 qubits every arm is classically
  simulable, so a win shows that the *model* is good, not that quantum hardware is needed.
  Link 4 stays an assumption, and H3 is our only weak evidence about larger sizes.
- **The fidelity kernel may flatten as qubits grow**, which would work against H3 for that arm.
- **There is no known reason for image labels to line up with quantum fingerprints.** H2's labels
  are built from a quantum process, so H2 is the likelier to succeed but the less useful
  commercially.

## Open points
- [ASSUMPTION] E2 and E3 fingerprints are hard to compute classically at 50–100 qubits. Nobody has
  shown it; it is a conjecture for E2 and untested for E3.
- [OPEN] The exact quantum process used for the H2 labels. The proposer left it to us; the designer
  fixes it before any data.

## Sources
- `cards_v2/qml-06/input.md` — algorithm, task, proposer's claim
- `cards_v2/qml-06/intake_answers.md` — proposer's answers
- `cards_v2/qml-06/mocks.md` §analysis — algorithm analysis
