---
thread: {thread}
algorithm: {name}
source: {00_inputs/… paper, notes or code}
date: {YYYY-MM-DD}
recommendation: {PROCEED | ASK-HUMAN | STOP}
---

# Algorithm analysis — {algorithm name}

> **Warnings** (copy every applicable box from lab_method §4 verbatim; write "none" if none apply)
> ⚠️ …

## 1. Summary
{Five sentences, including any warnings.}

## 2. Task
- **Formal task:** input → output, objective/cost function.
- **Correct solution means:** exact | approximate (tolerance) | probabilistic (success probability).
- **Size:** N = {…}; q = {…}; mapping: {q = log₂N | q = N | …}.

## 3. The quantum algorithm
- **Input & loading:** encoding, loading cost (gates, depth, QRAM, classical preprocessing). {Data loading often cancels the speedup — state it explicitly.}
- **Circuits:** registers, subroutines (QFT, QPE, amplitude amplification, ansatz, oracle…), classical feedback loop. Pseudocode or diagram.
- **Depth & gates:** depth, two-qubit count, T-count (fault-tolerant) — as functions of q and N.
- **Measurement & post-processing:** what is measured, how the output is computed from it.
- **Shots:** formula for precision ε, success 1−δ; does it grow with q or N? {exponential = red flag}
- **Output:** full vector | sample | scalar | expectation value. {Reading a full N-vector costs ≥ N shots.}
- **Hyperparameters:** each one and how it is chosen.
- **Trainability** (variational/heuristic): barren plateaus, local minima, iteration count.

## 4. The competition
### Classical algorithms
| Algorithm | Exact/approx | Time (N, q) | Memory | Scaling class | Used in industry? (tools) | Limitations | Reference |
|---|---|---|---|---|---|---|---|

### Quantum algorithms
| Algorithm | FT / NISQ | Qubits | Depth | Shots | Time | Scaling class | Limitations | Reference |
|---|---|---|---|---|---|---|---|---|

## 5. Classical twin
{Same input, same access model. Check at least: dequantization / quantum-inspired sampling;
tensor network / MPS (low entanglement); Clifford / matchgate / restricted-geometry simulability;
classical methods exploiting the same structure (sparsity, low rank, symmetry). Verdict per check.}

## 6. Resources
### Quantum (end-to-end)
| Resource | Formula | Class in q | Class in N |
|---|---|---|---|
| Qubits (incl. ancillas) | | | |
| Depth | | | |
| Two-qubit / T gates | | | |
| Shots | | | |
| Classical pre/post-processing | | | |
| Classical memory | | | |
| **Total time to solution** | | | |

### Best classical (same variables)
{same table}

### Brute-force simulation of the circuit
{statevector ≈ 2^q time and memory; tensor network if applicable}

## 7. Claimed source of advantage, trade-offs, break-even
- **Source:** which step, and why a classical method cannot copy it.
- **Trade-offs:** time vs accuracy, qubits vs depth, shots vs precision, noise sensitivity.
- **Break-even N\*:** {required for any polynomial speedup; say if unrealistic}

## 8. Open questions and assumptions
- [ASSUMPTION] …  · [UNVERIFIED] …

## 9. Recommendation
{PROCEED — no exponential quantum resource, no known twin, plausible source of advantage ·
ASK-HUMAN — any ⚠️ warning; options: stop / continue as quantum-inspired study / continue for
empirical evidence · STOP — task ill-defined or algorithm incorrect as described (say what is missing).}
