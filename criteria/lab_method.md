# Lab Method — how the lab decides whether an idea earns compute, and what a verdict means

Loaded by every QML Lab role and skill (placeholder `LAB_METHOD`). Companion to
[`qml_domain.md`](qml_domain.md), which says how to judge *papers*; this file says how to judge
*our own experiments*. Sources: `experiments/spectral_graph/INSIGHTS.md` (the six rules, from 11
closed experiments), Adi's *Quantum Algorithm Evaluation Protocol* (global rules, warning
tables), and the lab design (`docs/lab/`).

Contents: 1 · The six rules · 2 · Gate ladder · 3 · Global rules · 4 · Scaling warnings ·
5 · Simulation limits · 6 · Verdicts and the Negative Verdict Standard · 7 · Glossary

---

## 1. The six rules

Ordered the way they are applied to a new idea: cheapest kill first. Each rule keeps the
painful specific that produced it — the number is the argument; do not drop it.

### Rule 1 — Start with the classical twin
**Rule.** Before any quantum work: once the quantum step's input is fixed, can an ordinary
computer given *exactly the same input and access model* produce the same answer at comparable
cost? If yes, there is no quantum claim.
**Precedent.** Exp 04: a plain classical random walk matched the quantum pipeline's rankings
(agreement 0.999) and beat its modeled cost at every catalog size from 256 to 10⁹ items — the
gap *widened* with scale, 13× → 424×. Exp 12: the "quantum" operator diagonalised on the full
203,769-node graph in 4.5 s — the twin *is* the step. Exp 13: importance sampling needs a flat
~2,000 calls from p=1e-3 to 1e-12 while QAE grows as 1/√p — 3,925× cheaper classically.
Exp 07 compared against the wrong object and was caught only in review.
**Paper trigger.** A small classical description as input + a smoothing/diffusion task (no
cancellation between positive and negative contributions) ⇒ a twin almost certainly exists.
Check this before building anything.
**Screen.** Green: named reason no same-access twin exists (sign structure, genuine
interference, hardness result that survives the access model). Amber: no twin known, none
ruled out. Red: twin exists on paper or in code.
**Keep in mind.** A twin kills the *quantum* claim, not the idea — quantum-inspired classical
results are assets (exp 09: a 0.15 MB classical index reaches 80–87% of a full retriever). The
twin then doubles as the cheap stand-in for the quantum arm in later phases.

### Rule 2 — Verdicts only on real data
**Rule.** Synthetic data may explain mechanisms and build scaling ladders; a decision gate never
fires on it.
**Precedent.** Exp 05 (planted synthetic graphs): same quality as classical at 0.1 ms/query flat
vs classical 1.5 s at 16K nodes — a "resource win". Exp 06 (real catalogs): NO-GO, 24.5 ms vs
19.9 ms, never pays back. Exp 07: the *tightest* statistical fits (15–60× lower error) produced
the *worst* structural answers — off by 8–14 orders of magnitude.
**Screen.** Green: named real dataset at a relevant regime is available. Amber: only proxies.
Red: the claim only exists on constructed data.
**Discipline.** When a synthetic generator is used, write down what it grants the method for free
(spectral gap, balanced communities, …) — that list is the risk register for the real run.

### Rule 3 — Think in industrial scale; put the extrapolation in the metric
**Rule.** Name the industrial operating point *in the design*, measure a ladder (≥4 points), fit
the trend, and report the extrapolated value at that point. Never extrapolate from one point.
**Precedent.** Test sets were 5–9 orders of magnitude below the operating point (Yelp2018: 38K
items; target: ~10⁹ items, ~100 ms p99). At scale the classical control changes shape (a 1–3 ms
retrieval funnel, not a full scan) — our baseline was simultaneously too slow and too strong.
**Screen.** Green: operating point named with its latency/memory/cost budget. Red: "large scale"
with no number.

### Rule 4 — Compare under the constraints industry actually runs under
**Rule.** The question is not "quantum vs classical SOTA" but "which method gives the best
quality at a given resource cap" — and **the cap is charged to both arms, including everything
the quantum arm needs in order to serve.**
**Precedent.** The fitted operator was ~24 KB, but the item→address map is ~4 GB at 10⁹ items and
is not optional. Exp 09 charged it honestly and lost to byte-matched k-means by 25–38% and to
product quantization by 36–49%. Materials Amendment A killed a whole deployment architecture
(Q-FEAT-screen) once mandatory per-candidate preprocessing was charged.
**Screen.** Green: a cap under which the classical option is genuinely degraded, charged to both
arms. Red: the advantage appears only when the quantum arm's mandatory costs are left out.

### Rule 5 — Report a Pareto front, not a point
**Rule.** Sweep the resource axis; the gate is "does the quantum curve sit above the classical
curve across the range", not "does it beat one configuration". A win at one budget and losses
at four is a loss.
**Precedent.** Exp 11: an early +18% at one budget on the best of three datasets collapsed, on
the full sweep, to 1/3 datasets — the largest a dead tie across every arm.

### Rule 6 — Count readout as a first-class cost
**Rule.** A circuit returns samples, not answers. The shape and cadence of the output is part of
choosing the problem, checked at selection time, not discovered in design.
**Precedent.** Retrieval readout grows ~√(candidate set) vs classical ~log(catalog): even the most
generous scenario was ~10⁶× over the latency budget. Exp 09 killed three readout schemes on paper
— the highest-leverage hour of that experiment. Fraud/AML: every layer with a hard resource cap
emits a per-event output at high frequency, and every layer with a small infrequent output has
no cap — rules 4 and 6 are anti-correlated there, which is why that screen came out empty.
**Screen.** Green: one number (or a small summary) read rarely. Red: a full vector, a ranked list
over a large set, or a per-event output at high frequency.

**The screen in one line.** An idea worth compute needs all three: a resource cap under which
classical is genuinely degraded, an output that is small and read infrequently, and no
classical twin.

---

## 2. Gate ladder — ordered by cost × fatality

| Gate | Question | Cost | Where it runs | Precedent |
|---|---|---|---|---|
| **G0** | Does it fall inside an exclusion-ledger entry, by mechanism? | minutes | screen | — |
| **G1** | Readout shape and cadence (rule 6) | ~1 h | screen | fraud/AML; exp 09 |
| **G2** | Resource cap charged to both arms incl. mandatory preprocessing (rule 4) | ~1 h | screen | Amendment A |
| **G3** | Classical twin (rule 1) | hours on paper → days in code | screen → P1 | exps 04, 12, 13 |
| **G4** | Target headroom: is there error to win, *where the quantum step acts*? | one classical run | P1, P3 | exp 03; M01 |
| **G5** | Baseline adequacy: is our classical arm strong enough to license a verdict? | same run | P1 → P3 | M01 H0 |
| **G6** | Real-data transfer (rule 2) | one real run | P3 | exp 05 → 06 |
| **G7** | Pareto front across the resource axis (rule 5) | a sweep | P2, P3 | exp 11 |
| **G8** | Modeled quantum vs measured classical at the named operating point (rule 3) | modeling | P3 | exps 04, 08 |
| **G9** | Hardware envelope: noise threshold, compiled resources, break-even N* | modeling | P4, P5 | Adi P4/P5 |

- **G1 and G2 come before the twin** — both are paper exercises and have historically killed
  more than the twin did.
- **G5 is a license gate, not an idea gate.** Failing it neither kills nor saves the idea; it
  downgrades whatever verdict follows to provisional, with a named reopening condition (M01:
  baseline 0.216 eV MAE vs a 0.1275 eV adequacy bar → provisional stop).
- **Gray-zone policies are written before data.** "A second failure stops the program" must be
  in the pre-registration, or it becomes negotiable afterwards.

**Execution phases** (Adi's ladder; milestones of a pre-registration, cheapest-fatal first):
P1 toy noiseless 6–16 qubits (correctness, first scaling, tuning) · P2 medium noiseless 18–26
qubits (scaling stability) · P3 real data at simulable size + classical at full industrial size
+ resource estimate at industrial size · P4 noisy simulation (error threshold, mitigation
overhead) · P5 hardware plan (compilation, platform comparison, minimal demonstration).
V1 executes P1–P3 locally; P4 is small noise sweeps; P5 is modeling only; no QPU, no cloud spend
before G4/G5 pass.

---

## 3. Global rules (every stage)

1. **Pause at gates.** An unplanned gate failure stops and asks a human, in plain language: what
   failed, the evidence, what continuing would cost. A pre-registered stop is not an escalation.
2. **Criteria before runs.** Metrics, thresholds and baselines are fixed and locked before any
   result is seen. Later changes are dated, logged amendments that precede data access.
3. **Same variables everywhere.** Report **N** (problem size) and **q** (qubits) with the mapping
   written down. Compare quantum and classical cost in the *same* variable, and only end-to-end:
   loading the input (≈N operations for N classical numbers unless already quantum), readout, and
   shots are part of the quantum cost; the classical baseline gets the same access to the input.
4. **Classify every scaling**: constant, log, polynomial (with exponent), quasi-polynomial,
   exponential.
5. **Simulation cost is not quantum cost.** Report projected quantum cost (gates, depth, shots,
   estimated hardware time) separately from simulator wall-clock. Never substitute one for the other.
6. **Strongest classical baseline, tuned fairly** — at least the same tuning budget as the quantum
   arm. A weak baseline makes the result invalid, not negative.
7. **Statistics.** Several instances and seeds; means with confidence intervals; scaling exponents
   with uncertainty.
8. **Reproducibility.** Code version, library versions, seeds, hardware, time and memory for every
   number; raw data kept, not only plots.
9. **Decision log.** One line per decision: date, stage, decision, reason, who decided.
10. **Honesty about bad results.** A clear negative is a product. Never tune, cherry-pick or
    redefine success after the fact.

---

## 4. Scaling warnings (write these in a box at the top of the analysis)

| Observation | Warning to write |
|---|---|
| A **quantum** resource (depth, gates, shots, loading, readout, iterations) grows **exponentially** in q or N | ⚠️ "The quantum cost grows exponentially. At most a polynomial speedup (as Grover); may be simulable or matched classically. Unlikely to give practical advantage — may still be worth studying as a quantum-inspired classical algorithm." |
| The circuit is classically simulable in polynomial time (Clifford, low entanglement, known twin) | ⚠️ "Classically simulable or dequantizable — no quantum advantage expected." |
| Best **classical** is exponential and quantum is polynomial, same variable | ✅ "Potential exponential advantage — *provided* the quantum cost is end-to-end (loading, readout, shots polynomial) and the classical baseline has the same input access." |
| Advantage relies on a compressed encoding (q = log N) of classical data | ⚠️ "Check that loading the N inputs does not itself cost ≈N, and that no same-access twin (dequantized sampling) matches it." |
| Both polynomial | ℹ️ "At most a polynomial advantage. Check that the exponent gap survives error-correction overhead and slower quantum clocks — see break-even." |

Polynomial quantum resources do **not** prove classical hardness — always also run the twin check.
**Break-even (required for any polynomial speedup):** combine projected gate times and
error-correction overhead into the problem size N* where quantum overtakes classical in
wall-clock. If N* is unrealistic, say so.

---

## 5. Simulation limits (plan with these)

| Method | Memory | Practical limit |
|---|---|---|
| Statevector (complex128) | 16·2^q bytes | q=26 → 1 GiB · q=30 → 16 GiB · q=32 → 64 GiB |
| Density matrix | 16·4^q bytes | q=12 → 256 MiB · q=14 → 4 GiB |
| Noisy trajectories | ≈ statevector × trajectories in time | q ≲ 24–28 |
| Tensor network / MPS | entanglement-dependent | large — **but easy MPS simulation is itself a warning sign** |
| Clifford / stabilizer | polynomial | any q — **no quantum advantage** |

---

## 6. Verdicts and the Negative Verdict Standard

**Vocabulary.**
| Verdict | Meaning |
|---|---|
| **GO** | Correct, and a named *type* of advantage (provable asymptotic / heuristic asymptotic / practical) survives the twin, the strongest baselines, end-to-end loading/readout/shots, and noise or a credible fault-tolerant path. States resource and confidence. |
| **CONDITIONAL-GO** | Correct and advantage plausible under explicit, testable conditions (p < p*, N > N*, an instance class, a complexity assumption). |
| **NO-GO-FINAL** | Incorrect, or no advantage, or overheads cancel it, or classically simulable — and N1–N5 all hold. |
| **NO-GO-PROVISIONAL** | As NO-GO but at least one of N1–N5 fails. Names a reopening condition. Blocks quantum spend; never blocks the reopening experiment. |
| **BLOCKED** | Could not be evaluated. Names the blocker and the exact failing command. Not a failure of the researcher. |

Every verdict says, per hypothesis, whether an advantage was **"not shown in the tested range"**
or **"shown to be absent"**. They are different claims.

**Negative Verdict Standard** — a NO-GO that prunes future search must clear a higher bar than a
GO, because nobody will re-litigate it. All five for FINAL:
- **N1 Baseline adequacy** — classical arm within a pre-registered factor of published SOTA on the same metric and data.
- **N2 Gate integrity** — evaluated against the lock; zero post-hoc threshold movement; amendments dated before data access.
- **N3 Discriminating power** — point estimates at the null (not wide intervals straddling it); every oracle/ablation gate has its size-matched control (M01's H2 "passed" until a random subset of the same size did the same).
- **N4 Mechanism named** — the failure is explained structurally, with the narrowest class it generalizes to.
- **N5 Independent audit CONFIRMED** — fresh context, artifacts only, ≥2 numbers recomputed.

**The inverted pathology.** Agents overclaim by default. In a kill-oriented lab the cheap failure
flips: *over-killing* — a NO-GO that is really a bug, a weak baseline, or an underpowered test.
N1, N3 and N5 exist to catch it. When in doubt, provisional.

**Scope discipline.** An exclusion is scoped to the narrowest class the mechanism licenses, and
always says what it does *not* exclude. "This construction fails as a recsys ranker for this
mechanism" is never recorded as "graph QML is dead."

---

## 7. Glossary

- **Correctness** — output matches a known right answer (exact, brute force, trusted solver) within stated tolerance and success probability.
- **Classical twin** — a classical algorithm with the *same input and the same access model* as the quantum algorithm (same samples, same oracle, same low-rank structure), attempting the same task. Includes dequantized and quantum-inspired methods.
- **Shots** — circuit repetitions to estimate an output; ≈1/ε² for sampling precision ε, ≈1/ε with amplitude estimation.
- **Advantage types** — *provable asymptotic* (proven better scaling than any classical algorithm, under stated assumptions) · *heuristic asymptotic* (better fitted scaling than the best known classical, in the tested range) · *practical* (better end-to-end time, cost, energy or accuracy at a size that matters, counting loading, error correction and readout).
- **Potential quantum advantage** — evidence consistent with at least one advantage type and not ruled out by a twin, simulability or overheads. Not yet shown in practice.
- **Operating point** — the named industrial setting (size, latency, memory, cost budget) at which a claim must hold.
- **Claim ladder** — `speculative → plausible → observed → supported → strong → published` (↘ `refuted`), from `SOUL.md`. A single self-run experiment is capped at `observed`.
