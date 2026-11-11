# Advantage potential — seven upfront questions

**Status:** working hypothesis, added 2026-11-11. Recorded at the ingest gate as a profile. It does
not kill a candidate and does not enter the rank. `python -m lab.tools.backlog report` shows whether
candidates with a higher profile reach further; section 5 says when to adopt it or delete it.

**Source:** *The Compendium of Super-Quadratic Computational Quantum Advantages* (Kammerlander,
O'Brien, King, Somma, … Babbush; arXiv:2610.32595, Oct 2026). The compendium lists 25 problems with
credible speedups beyond quadratic and, for each, the conditions an instance must meet ("Regimes of
Advantage"). The seven questions are the conditions that recur across those entries. They are our
reading of the paper, not a list the paper states.

**What it is for.** The seven lab rules (`criteria/lab_method.md`) ask whether a quantum method can
pay for its input, its readout and its classical competitor. They say little about *why* a speedup
should exist in the first place. These questions ask that, before any experiment.

---

## 1. The questions

Rate each 2 (yes, with the argument), 1 (unclear or partly), 0 (no). Order and keys are fixed; the
tool stores them under these names.

### Q1 `mechanism` — Is there a named quantum mechanism that classical methods cannot reuse?
Every strong entry has one, and can say why the same structure does not help classically.

| Mechanism | What it exploits | Entries |
|---|---|---|
| Fourier sampling | a hidden period or subgroup of an algebraic function | factoring, discrete log, Pell, point counting, isogeny |
| Interference plus decoding (DQI) | a constraint matrix whose dual code decodes efficiently | optimal polynomial intersection |
| Guiding state plus phase estimation | a cheap state whose overlap with the planted eigenvector is quadratically boosted | tensor PCA, planted k-XOR, hypergraph communities |
| Short-path jump | a guiding state with exponentially boosted overlap on optima | structured exact optimization (Stage I) |
| Native quantum dynamics | the system being computed is itself quantum | OTOC, ground states, spectra, dynamics |
| Unitary group representations | a quantity that is a trace of a unitary representation | Jones polynomial |
| Kernel of a combinatorial Laplacian | homology as a ground space | Betti numbers (TDA) |

The planted-inference entry is the cleanest statement: the guiding state is available classically
too, "but does not yield a similar improvement there".
- **2** the mechanism is named and the reason classical cannot use the same structure is stated.
- **1** a mechanism is named, the classical argument is missing.
- **0** "a quantum model on a hard problem": no mechanism.

### Q2 `band` — Is the structure in the middle band?
Too little structure and there is nothing to exploit: for unstructured max-LINSAT, beating a random
assignment is NP-hard for classical and quantum alike. Too much and classical methods exploit it:
matrix PCA (order 2) is solved optimally by classical spectral methods; pairwise community
detection has efficient classical algorithms; low-entanglement or integrable dynamics fall to
tensor networks; the short-path threshold structure gave a classical conditioning-and-search
algorithm (Le Gall–Tamaki, arXiv:2604.12131).
- **2** the candidate names the structure, why it is not generic, and why the known classical
  methods cannot use it.
- **1** structured, but the classical side has not been argued.
- **0** generic instances, or structure a standard classical method already exploits.

### Q3 `window` — Is there a known hard-but-solvable window?
Strong areas have a mapped regime where the problem is solvable in principle and hard for known
efficient classical methods, backed by classical theory: the statistical-computational gap with
low-degree and sum-of-squares lower bounds (planted inference), the satisfiability threshold
(k-SAT), decades of subexponential cryptanalysis (number theory). Quantum simulation lacks such a
map, which is the stated reason nearly all of it is Stage I.
- **2** a named regime with classical hardness evidence (lower bounds in restricted models, or a
  long record of failed attacks).
- **1** hardness is believed, with no formal or empirical map.
- **0** no regime named, or the regime is classically easy.

### Q4 `ensemble` — Can you generate instances at will?
Stage II requires "efficient generation of specific problem instances". A single showcase instance
cannot be defended: one cannot "draw a new problem from the ensemble" to check that a tuned
classical heuristic still fails.
- **2** a sampler for instances at any size, in the hard window.
- **1** a fixed benchmark set with several instances.
- **0** one instance or one dataset.

### Q5 `work` — Is the classical work a high power of the input size?
Loading classical data is not fatal by itself. Planted inference reads a classical tensor with
about n^p entries and still gains a quartic speedup, because the classical method works in a space
of dimension n^ℓ with ℓ well above p. Linear systems and coupled oscillators lose the speedup as
soon as the input needs a database of size N: there the classical cost is close to linear in the
data. This refines Rule 7: charge loading, then compare it with the classical work.
- **2** classical cost is a high power of (or exponential in) the input size, so loading is a
  vanishing share.
- **1** classical cost is a low polynomial above the input size.
- **0** classical cost is near-linear in the data that must be loaded.

### Q6 `output` — Is the answer small, checkable and not predictable?
Three ways the compendium loses a speedup at the output: the answer is a full vector or needs
tomography (linear systems); the precision needed is too high (additive-error Betti numbers drop to
a quadratic speedup; spectra at 1 cm⁻¹); the quantity concentrates to a value one can predict
without computing it (local observables of chaotic dynamics, kernel values that concentrate).
The paper also requires an efficient check of the output, classical where possible.
- **2** a decision, a scalar or a short witness, at modest precision, that varies across instances
  and can be checked.
- **1** small output, but concentration or verification has not been examined.
- **0** a large output, an exponentially small quantity, or a value that concentrates.

### Q7 `baseline` — How long has the classical side been attacked?
The paper repeats that classical baselines are moving targets. Factoring has withstood decades. The
quartic k-XOR speedup lost half its exponent for large k within about a year (Gupta, He, O'Donnell,
Singer, SODA 2026). The first short-path regimes were dequantized (arXiv:2604.12131). The
exponential-advantage claim for chemistry is disputed.
- **2** the classical problem has a long record of strong attacks, or matching lower bounds in the
  relevant restricted models.
- **1** a recent baseline with some hardness evidence.
- **0** the classical comparison is a method nobody has tried hard to beat, or a toy baseline.

---

## 2. Evidence class

One label for the kind of evidence behind the claimed speedup. The compendium separates an
algorithm with a guarantee from a heuristic, and worst-case evidence from average-case instances.

| Class | Meaning |
|---|---|
| `none` | no asymptotic speedup is claimed (most near-term learning studies; a negative-result or classical-method candidate) |
| `heuristic` | an empirical scaling comparison between heuristics under matched criteria (QAOA on random 8-SAT) |
| `stage1` | a quantum algorithm with worst-case evidence; no hard instance family yet |
| `stage2` | an instance family that can be generated, with average-case evidence of a speedup beyond quadratic |

`none` is not a fault. A sharp negative result or a quantum-inspired classical method is a
legitimate publishable step (rungs 1–2) and will carry `none`.

---

## 3. How the questions relate to the existing rules

| Question | Existing coverage |
|---|---|
| Q1 mechanism | none (Rule 1's note on phase interference is the closest) |
| Q2 band | partly Rule 1 (twin) and Rule 7 ("structure that helps quantum usually helps classical") |
| Q3 window | none |
| Q4 ensemble | none (Rule 2 asks for real data, which pulls the other way; see below) |
| Q5 work | Rules 4 and 7, refined: compare loading with the classical work, not with zero |
| Q6 output | Rule 6, plus concentration and verifiability |
| Q7 baseline | Rule 1 asks for the strongest competitor today; this asks how tested it is |

**Tension with Rule 2.** Rule 2 says decide on real data. Q4 says an advantage claim needs an
ensemble. Both hold at different stages: an ensemble establishes that the speedup exists; real data
then decides whether real instances fall inside the regime (the paper's Stage III).

**Problem-first versus algorithms-first.** The paper's introduction states that starting from a
real-world problem and looking for a quantum algorithm "is seldom successful because quantum
advantages typically rely on highly specific mathematical structure that most real-world problems
do not possess". It recommends starting from a known mechanism and looking for problems that fit.
Source C of the backlog (the combination grid) is where this lab does that; the mechanisms table
under Q1 is part of its input.

---

## 4. Recording

At the ingest gate, in triage mode, after G0–G3:

```
python -m lab.tools.backlog score <CID> --gate potential \
    --answers m,b,w,e,k,o,a --evidence-class none|heuristic|stage1|stage2 \
    --note "<the mechanism, and the weakest answer with its reason>"
```

Answers are in the order `mechanism,band,window,ensemble,work,output,baseline`. The queue prints the
total out of 14 next to each candidate. The screen analyst sets the value probability after
answering the questions and cites the deciding answer in the value note.

For a candidate that claims no quantum advantage (a negative result, a classical method), rate the
questions for the *advantage claim it tests*, and say so in the note.

## 5. When to adopt or delete this profile

- **Adopt as an input to the rank** once at least 10 scored candidates have closed and
  `backlog report` shows the high band reaching a rung clearly more often than the low band.
- **Delete it** if, at 10 closed candidates, the bands do not differ. Record that as a result.
- **Never a kill rule on its own.** A kill needs a 🔴 lab rule with its mechanism.

## 6. Limits

- It is a checklist written with hindsight from about 25 successes. It filters; it will not invent
  a new mechanism, and an idea with a new mechanism will score low on Q3 and Q7 by construction.
- The compendium covers time speedups on fault-tolerant machines only. It excludes sample-complexity
  advantages for learning from quantum data, communication and space advantages, and anything
  near-term. A low profile there means "outside the paper's scope", not "no potential".
- The authors hold the prior that quadratic speedups will not pay for error correction
  (Babbush et al., PRX Quantum 2, 010103). The threshold is their working assumption, not a theorem.
