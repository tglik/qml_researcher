# Lab method

How the QML Lab decides whether an idea earns compute, and what a verdict means. Every lab role
and skill loads this file. Each rule is stated here once; role files point to it by number.

**Scope.** This file governs every program that enters the lab through intake: an algorithm Adi
brings, a hypothesis card from paper review, a transfer card, or a use-case idea. Judging
published papers is [`qml_domain.md`](qml_domain.md)'s job; a paper reaches this file only when
someone opens a lab program on it.

**Contents:** 1 Who does what · 2 The seven rules · 3 Gates and phases · 4 Global rules ·
5 Scaling warnings · 6 Simulation methods · 7 Verdicts · 8 Glossary

---

## 1. Who does what

| Stage | Role | Produces | Next |
|---|---|---|---|
| Intake, algorithm path | Algorithm analyst | End-to-end resource analysis, paper competitor check, warnings, numbered hypotheses | Scoping interviewer |
| Intake, both paths | Scoping interviewer | A falsifiable hypothesis at a named operating point | Screen |
| Screen | Lab archivist (prior-work lookup), then screen analyst | Prior-work brief; screen verdict with design constraints | Human, CP1 |
| Pre-registration | Experiment designer, classical competitor champion; review panel pass 1 | Locked proposal | Human freeze, CP2 |
| Run (per phase) | Classical competitor champion first, then implementer | Gate table, phase report | Human, CP3 |
| Review | Review panel pass 2, on raw results | Issues, before any verdict exists | Verdict |
| Verdict | Verdict writer | The verdict | Audit |
| Audit | Verdict auditor | CONFIRMED / OVERTURNED / INSUFFICIENT | Human, CP4 |
| Variants | Variant generator | Up to 10 ranked variants and salvage | Promote |
| Promote | Lab archivist | Ledger entry, hypothesis status, proposed rule changes | Human merge, CP5 |

The lab director runs the pipeline: it checks order and budget and decides when to wake a human.

- **Algorithm analyst vs screen analyst.** The algorithm analyst understands one algorithm in
  depth and states what it really costs. The screen analyst decides whether a hypothesis deserves
  compute. The screen reads the analysis; neither role calls the other.
- **Paper checks vs built baselines.** The algorithm analyst and the screen analyst check
  classical competitors on paper (Rule 1). The classical competitor champion builds and tunes them
  in code.
- **Writer vs auditor.** The verdict writer writes the verdict. The auditor only checks it.
- **Where new rules come from.** When a closed program teaches a transferable lesson, the lab
  archivist proposes a change to this file and a human merges it. The seven rules below came from
  eleven closed experiments and the team's review.

---

## 2. The seven rules

Each rule gives the rule, how the screen rates it (🟢 / 🟠 / 🔴), and examples from closed
experiments. Section 3 sets the order in which they are applied.

### Rule 1 — Start with the classical competitor

Before any quantum work, ask whether any classical method gives the same answer at comparable
cost. The quantum claim survives only if every item on this checklist fails:

- **Twin.** A classical algorithm with the same input and the same access model (the same
  samples, oracle or low-rank structure). Includes dequantized and quantum-inspired sampling.
- **Best classical method for the task.** Any other method, using the input classical would
  really have (often the full data, not samples), including heuristics that do well on the
  instances that matter.
- **Direct simulation.** Simulating the quantum scheme costs about the same as running it.
- **Simulable structure.** Clifford or near-Clifford, low entanglement (MPS, tensor networks),
  free-fermion or Gaussian, shallow circuits with small light cones.
- **Noise.** Realistic noise makes the circuit simulable. Keep this item open until noisy
  simulation (P4) has run.
- **Learned surrogate.** A classical model trained on data or on quantum measurements reproduces
  the output.
- **Easy output.** The task needs only a quantity that classical methods approximate well, even if
  the full quantum state is hard.

**Sign-free problems are a warning, not a verdict.** If the Hamiltonian is stoquastic (possibly
after a simple basis or gauge change), or the task is diffusion with no cancellation between
positive and negative contributions, test a Monte Carlo or random-walk competitor. Classical wins
only if it uses the same compressed input at comparable cost (for example, the walk mixes fast);
glued trees and sign-free adiabatic separations show quantum can still be exponentially faster.
Prefer problems whose advantage depends on phase interference no simple basis change removes, and
for sign-free problems require separate evidence of classical hardness.

**Screen.** 🟢 every item has a named reason it fails. 🟠 some items are open. 🔴 any item
matches the quantum method.

**Examples.**
- Recommendation filter (exp 04): a random walk on the same compressed graph description matched
  the quantum rankings (agreement 0.999) and was cheaper at every size from 256 to 10⁹ items, by
  13× growing to 424×.
- Graph operator (exp 12): classical diagonalization of the full 203,769-node graph took 4.5 s.
- Rare-event estimation (exp 13): importance sampling needs ~2,000 calls at any p, while amplitude
  estimation grows as 1/√p: 3,925× cheaper classically at p = 1e-12. The quadratic speedup was
  real, but measured against crude Monte Carlo, which nobody deploys.

A competitor kills the quantum claim, not the idea: quantum-inspired classical results are assets
(a 0.15 MB index reached 80–87% of a full retriever).

### Rule 2 — Decide on real data

Synthetic data may explain a mechanism and build a scaling ladder. No decision gate fires on
synthetic data alone.

- When you use a synthetic generator, list what it gives the method for free (a spectral gap,
  balanced communities, …). That list is the risk register for the real run.
- When real data at full scale is impossible (a 10⁹-item catalog), run real data at the largest
  simulable size, run the classical methods at full size, and model the quantum cost at full size
  (phase P3). The gate fires on that real-data run.
- When synthetic succeeds and real fails, write down why: which property of the real data broke
  the method. Then decide explicitly whether another real dataset is worth trying, and whether the
  finding is worth a paper.

**Screen.** 🟢 a named real dataset at a relevant regime. 🟠 only proxies. 🔴 the claim exists only
on constructed data.

**Example.** On planted synthetic graphs (exp 05) the quantum filter matched classical quality at
0.1 ms per query versus 1.5 s for classical at 16K nodes. On real catalogs (exp 06) it took 24.5 ms
versus 19.9 ms and never paid back. The reason: on real data, recommendation quality comes from the
linear term of the classical model, not from the coarse community structure the generator planted.

### Rule 3 — Name the target scale and count the cost there

- Name the operating point in the design: size, latency, memory, cost, and the value metrics that
  matter (glossary). Industrial scale is preferred. A scientific target or an asymptotic claim is
  acceptable when stated explicitly. "Large scale" with no number is not a target.
- At the operating point, count the quantum cost analytically (gates, depth, shots, loading,
  readout) and measure the classical cost directly wherever possible.
- Fit trends only for what cannot be counted or measured. A fit uses at least 4 points over the
  widest range you can reach. It states the scaling class with uncertainty and the alternative fits
  it rejected. Extrapolated numbers are labeled "projected" and never mixed with measured ones.

**Screen.** 🟢 an operating point with its budgets. 🔴 no number.

**Example.** Our recommendation test sets were 5–9 orders of magnitude below the target (38K items
versus ~10⁹ items at ~100 ms p99). At the target, industry runs a 1–3 ms retrieval funnel, not a
full scan, so our classical baseline was too slow and too strong at the same time.

### Rule 4 — Classical must be a real bottleneck

- The classical computation must be expensive at the target size and workload. Turning 2⁶⁰ steps
  into 2³⁰ can make an impossible search practical; turning 10 ms into 3 ms cannot pay for a
  fault-tolerant machine.
- Compare under a resource limit that applies to both sides. Charge the quantum method for
  everything it needs to work in practice: per-input preprocessing, encoding tables, calibration.
- The projected gain must stay meaningful after error-correction overhead and slower quantum
  clocks (break-even, section 5).

**Screen.** 🟢 a named limit under which classical is genuinely worse, charged to both sides, with
the gain surviving overhead. 🔴 classical is already cheap, or the advantage appears only when
hidden quantum costs are left out.

**Examples.**
- Quantum walk (exp 08): 61 steps versus 1,252, a genuine speedup, but classical never took more
  than 10 ms.
- Compressed retrieval (exp 09): the quantum model of a 10⁹-item catalog took 24 KB but needed a
  ~4 GB item-to-encoding table. Charged honestly, it lost to byte-matched k-means by 25–38%.
- Materials screening: running the quantum step per candidate died on paper once per-candidate
  preprocessing was charged; computing the feature once per material survived.

### Rule 5 — Compare across the resource range, by the size of the gap

Sweep the resource axis and judge the whole curve, not one configuration.

- Report how much, not just who won: at each budget, the gap with a confidence interval. A gap
  within the noise is a tie.
- Before running, fix the smallest gain that matters in practice and what counts as a tie.
- Weight the budgets that matter. A clear win near the operating point outweighs small losses at
  budgets nobody uses. Report where quantum is ahead or behind, and by how much.
- A clear win in one range only is a CONDITIONAL-GO candidate, with that range as the condition,
  and a lead for the variant generator.
- Report every dataset, the full sweep and every method compared. If several resources matter, sweep each.

**Example.** An early +18% at one budget on the best of three datasets (exp 11) shrank, on the full
sweep, to a win on one dataset in three; on the largest dataset every method tied.

### Rule 6 — Count readout as a first-class cost

A circuit returns samples, not answers. Readout cost = (state preparation + circuit) × shots × how
often an answer is needed. Precision sets the shots: about 1/ε² per estimated quantity (1/ε with
amplitude estimation), so one high-precision number can cost as much as a large output. Error
mitigation multiplies shots, often by a lot; count it here. Judge by shots needed, not output size.
Check this when choosing the problem, not during design.

**Screen.** 🟢 a few quantities at modest precision, read rarely. 🔴 a full vector, a ranked list
over a large set, a per-event output at high frequency, or a precision whose shots exceed the
budget.

**Examples.**
- Retrieval (exp 09): readout grows with √(candidate set) versus log(catalog) for classical, ~10⁶×
  over the latency budget even in the best case. Three readout schemes died on paper in an hour.
- Fraud and AML: layers with a hard resource limit need an answer per event; layers with a small,
  infrequent output have no resource limit. Rules 4 and 6 never pass at the same layer, so the
  domain came out empty, with a reason that transfers.

### Rule 7 — Count input loading as a first-class cost

The quantum method has to receive its input, and that cost is part of the method. Check it when
choosing the problem, together with readout.

- Loading N classical numbers costs about N operations, unless the data is already quantum or is
  generated on the device.
- Building the encoding counts: the classical preprocessing that produces a compact description,
  and re-encoding whenever the data changes.
- Structure that helps the quantum method usually helps classical too. If the input has a compact
  description, check whether a classical method can use the same description (Rule 1).
- Prefer inputs generated implicitly (an oracle, a circuit, a physical process, a Hamiltonian, an
  exponentially large configuration space) over stored classical datasets. When the algorithm
  assumes strong access to a stored classical matrix, treat a dequantized sample-and-query
  algorithm as a competitor: Tang's dequantization of the Kerenidis–Prakash recommender removed its
  exponential advantage this way.

- Compare loading with the classical work, not with zero. Planted inference (tensor PCA, planted
  k-XOR) reads a classical tensor of about n^p numbers and keeps a quartic speedup, because the
  classical method works in dimension n^ℓ with ℓ well above p (arXiv:2610.32595, sec. 4). Stored
  classical data is fatal when the classical cost is close to linear in it, not otherwise. See Q5
  of `criteria/advantage_potential.md`.

**Screen.** 🟢 the input is generated implicitly, or loading is provably small next to the classical
cost. 🟠 it relies on QRAM or a loader that does not exist yet. 🔴 loading costs ≈ N and cancels the
speedup, or classical sample-and-query access is cheap.

**The screen in one line.** An idea is worth compute only if all four hold: classical is genuinely
worse under a realistic resource limit applied to both sides; the input can be loaded cheaply; the
answer can be read out cheaply at the precision needed; and no classical competitor matches it.

---

## 3. Gates and phases

Gates in the order they are applied: cheapest fatal question first.

| Gate | Question | Rule | Cost | Runs in |
|---|---|---|---|---|
| **G0** | Does an exclusion-ledger entry already cover it, by mechanism rather than wording? | — | minutes | screen |
| **G1** | Can the input be loaded and the answer read out cheaply, at the precision and frequency needed? | 6, 7 | ~1 h | screen |
| **G2** | Is classical a real bottleneck under a limit charged to both sides? | 4 | ~1 h | screen |
| **G3** | Does any classical competitor match it? | 1 | hours on paper, days in code | screen, then P1 |
| **G4** | Headroom: is there error left to win where the quantum step acts? | — | one classical run | P1, P3 |
| **G5** | Baseline adequacy: is our classical side strong enough to license a verdict? | — | same run | P1 to P3 |
| **G6** | Does the result hold on real data? | 2 | one real run | P3 |
| **G7** | Is quantum ahead across the resource range, by a margin that matters? | 5 | a sweep | P2, P3 |
| **G8** | Counted or modeled quantum cost vs measured classical cost at the operating point | 3 | modeling | P0, P3 |
| **G9** | Hardware envelope: noise threshold, compiled resources, break-even N* | — | modeling | P4, P5 |

- G1 and G2 come before G3. Both are paper exercises and have killed more ideas than the competitor
  check has.
- G5 licenses a verdict; it does not judge the idea. Failing it makes any following NO-GO
  provisional, with a named reopening condition. Example: a materials baseline at 0.216 eV error
  against a pre-registered 0.1275 eV bar led to a provisional stop, not a final one.
- Gray-zone policies are written before data. "A second failure stops the program" must be in the
  pre-registration, or it becomes negotiable afterwards.

**Phases.** The pre-registration picks the phases a program needs and orders them cheapest-fatal
first.

| Phase | What | Size | Gates |
|---|---|---|---|
| **P0** | Analytic resource count at the operating point: gates, depth, shots, loading, readout, break-even N*. Paper only; part of the pre-registration, not a run. | operating point | G8 first pass |
| **P1** | Toy, noiseless: correctness, first scaling, tuning | 6–16 qubits | G3 in code, G4, G5 |
| **P2** | Medium, noiseless: scaling stability | 18–26 qubits | G7 |
| **P3** | Real data at simulable size; classical at full size; quantum cost modeled at full size | up to the operating point | G4–G8 |
| **P4** | Noisy simulation: error threshold, mitigation overhead | ≤ 24–28 qubits | G9; Rule 1 noise item |
| **P5** | Hardware plan: compilation, platform comparison, minimal demonstration | modeling | G9 |

In V1, P1–P3 run locally, P4 is small noise sweeps, and P5 is modeling only. No QPU or cloud spend
before G4 and G5 pass.

**Hardware modality.** The hypothesis names the target modality, or says it has none. Without one,
P0 counts hardware-agnostic resources (logical gates, depth, shots) and P5 maps them onto each
modality that fits, using the hardware roadmap reference. Simulation is modality-neutral unless a
gate depends on a modality-native capability (reconfigurable connectivity, parallel gates,
mid-circuit measurement); then the simulation models that capability and its constraints.

---

## 4. Global rules (every stage)

1. **Pause at gates.** An unplanned gate failure stops and asks a human. A pre-registered stop is
   the design working, not an escalation.
2. **Give the human options.** When a human must decide, state what is being decided and the
   evidence, list 2–4 options with what each costs, and recommend one with the reason.
3. **Criteria before runs.** Metrics, thresholds and baselines are locked before any result is
   seen. Later changes are dated amendments that precede access to the data they touch.
4. **Same variables everywhere.** Report N (problem size) and q (qubits) with the mapping. Compare
   quantum and classical cost in the same variable, end to end, including loading, readout and
   shots (Rules 6 and 7).
5. **Classify every scaling:** constant, log, polynomial (with exponent), quasi-polynomial,
   exponential.
6. **Simulation time is not quantum time.** Report projected quantum cost (gates, depth, shots,
   estimated hardware time) separately from simulator wall-clock and never substitute one for the
   other. Simulated quality is valid evidence: if a noiseless simulation already loses to classical
   on quality, that can reject the method.
7. **Strongest classical competitor, tuned fairly,** with at least the quantum side's tuning
   budget. A weak baseline makes the result invalid, not negative.
8. **Budget both sides.** Each phase plan estimates CPU-hours, peak memory, wall-days and tokens for
   the quantum side and the classical side separately. Estimates are for planning. A phase whose
   peak memory exceeds the machine it runs on, or whose spend passes 2× its plan, stops and asks a
   human with options: shrink the ladder, switch the simulation method, or cut or reorder the phase.
9. **Statistics.** Several instances and seeds; means with confidence intervals; scaling exponents
   with uncertainty.
10. **Reproducibility.** Code version, library versions, seeds, hardware, time and memory for every
    number; raw data kept, not only plots.
11. **Decision log.** One line per decision: date, stage, decision, reason, who decided.
12. **Honesty about bad results.** A clear negative is a product. Never tune, cherry-pick or
    redefine success after the fact.

---

## 5. Scaling warnings

Put every warning that applies in a box at the top of the analysis, worded as below.

| Observation | Warning to write |
|---|---|
| A **quantum** resource (depth, gates, shots, loading, readout, iterations) grows **exponentially** in q or N | ⚠️ "The quantum cost grows exponentially. At most a polynomial speedup (as Grover); may be simulable or matched classically. Unlikely to give practical advantage — may still be worth studying as a quantum-inspired classical algorithm." |
| The circuit has classically simulable structure, or a known competitor matches it (Rule 1) | ⚠️ "Classically simulable or dequantizable — no quantum advantage expected." |
| Best **classical** is exponential and quantum is polynomial, in the same variable | ✅ "Potential exponential advantage — *provided* the quantum cost is end-to-end (loading, readout, shots polynomial) and the classical competitor has the same input access." |
| The advantage relies on a compressed encoding (q = log N) of classical data | ⚠️ "Check that loading the N inputs does not itself cost ≈N (Rule 7), and that no same-access twin (dequantized sampling) matches it." |
| Both polynomial | ℹ️ "At most a polynomial advantage. Check that the exponent gap survives error-correction overhead and slower quantum clocks — see break-even." |

Polynomial quantum resources do not prove classical hardness; always run the Rule 1 checklist too.

**Break-even** is required for any polynomial speedup: combine projected gate times and
error-correction overhead into the problem size N* at which quantum overtakes classical in
wall-clock. If N* is unrealistic, say so.

---

## 6. Simulation methods

| Method | Memory | Practical limit |
|---|---|---|
| Statevector (complex128) | 16·2^q bytes | q=26 → 1 GiB · q=30 → 16 GiB · q=32 → 64 GiB |
| Density matrix | 16·4^q bytes | q=12 → 256 MiB · q=14 → 4 GiB |
| Noisy trajectories | ≈ statevector × number of trajectories, in time | q ≲ 24–28 |
| Tensor network / MPS | depends on entanglement | large, but easy MPS simulation is itself a Rule 1 warning |
| Clifford / stabilizer | polynomial | any q; the circuit fails Rule 1 |

**Choosing a method.** The experiment designer picks, per phase, the cheapest method that is
faithful for the gates that phase decides, and writes the choice and the reason into the
pre-registration:
- Noiseless and it fits in memory: statevector.
- Noisy: density matrix up to about 12–14 qubits, noisy trajectories beyond.
- Entanglement known to stay low: MPS, reporting the bond dimension.
- Clifford circuits: stabilizer simulation, and Rule 1 is red.
- On small sizes, always check finite-shot results against exact ones.

---

## 7. Verdicts

| Verdict | Meaning |
|---|---|
| **GO** | Correct, and a named advantage type (below) survives the Rule 1 checklist, the strongest baselines, end-to-end loading, readout and shots, and noise or a credible fault-tolerant path. States the resource and the confidence. |
| **CONDITIONAL-GO** | Correct, and advantage is plausible under explicit, testable conditions: a physical error rate p below a threshold p*, a size N above N*, an instance class, a resource range, or a complexity assumption. |
| **NO-GO-FINAL** | Incorrect, or no advantage, or overheads cancel it, or classically simulable — and N1–N5 all hold. |
| **NO-GO-PROVISIONAL** | As NO-GO, but at least one of N1–N5 fails. Names a reopening condition. Blocks quantum spend; never blocks the reopening experiment. |
| **BLOCKED** | Could not be evaluated. Names the blocker and the exact failing command. Not a failure of the researcher. |

Every verdict says, per hypothesis, whether an advantage was **"not shown in the tested range"**
or **"shown to be absent"**. The first is about our experiment; the second is about the world.

**Advantage types.** Most of our programs will target heuristic asymptotic or practical advantage.

| Type | What must be shown | Evidence | Usually licenses |
|---|---|---|---|
| **Provable asymptotic** | Better scaling than any classical algorithm, under stated complexity assumptions, end to end | A proof that survives the access model and Rule 7 | GO |
| **Heuristic asymptotic** | Better fitted scaling than the best known classical competitor, in the tested range | Ladders for both sides, fits with uncertainty, Rule 1 checklist complete | CONDITIONAL-GO, with the range and the competitors tried as conditions |
| **Practical** | Better value metrics at the operating point, end to end, including loading, readout and error correction | Measured classical vs counted or modeled quantum cost; P4/P5 credible | GO if the hardware path is credible, else CONDITIONAL-GO |

**Negative Verdict Standard.** A NO-GO prunes the search for everyone after us and nobody will
re-litigate it, so it must clear a higher bar than a GO. All five hold for NO-GO-FINAL; if any
fails, the NO-GO is provisional.

| Standard | Holds when | Fails, for example, when |
|---|---|---|
| **N1 Baseline adequacy** | Our classical side is within a pre-registered factor of the published state of the art, on the same metric and data | Our baseline is weaker than published results, so beating or losing to it means little |
| **N2 Gate integrity** | The verdict uses the locked thresholds, splits and stop rules; every amendment is dated before the data it touches | A threshold moved after results were seen |
| **N3 Discriminating power** | The test could have seen the effect: point estimates at the null with tight intervals, and a size-matched control for every oracle or ablation gate | An "oracle repair" recovered 71% of the gap, but repairing a random subset of the same size recovered 68% |
| **N4 Mechanism named** | The failure is explained structurally, with the narrowest class it generalizes to | "It just didn't work" |
| **N5 Independent audit** | A fresh auditor, reading artifacts only, recomputed at least two numbers and CONFIRMED | No audit, or the audit is INSUFFICIENT |

**Over-killing.** Agents overclaim by default, so GO verdicts get checked hard. But this lab
rewards kills, so the cheap failure flips: a NO-GO that is really a bug, a weak baseline or an
underpowered test. N1, N3 and N5 exist to catch it. When in doubt, provisional.

**Scope discipline.** An exclusion covers the narrowest class the mechanism licenses and always
says what it does not exclude. "This construction fails as a recommendation ranker, for this
mechanism" is never recorded as "graph QML is dead".

---

## 8. Glossary

- **Baseline** — a classical method the proposed method is compared against; the **baseline of
  record** is the strongest one that passes the adequacy bar.
- **Proposed method** — the quantum (or hybrid) method under test.
- **Cadence** — how often an answer is needed (per event, per query, daily, quarterly).
- **Classical competitor** — any item on the Rule 1 checklist; the **twin** is the strict one
  (same input, same access, same task).
- **Correctness** — the output matches a known right answer (exact, brute force or a trusted
  solver) within a stated tolerance and success probability.
- **Exclusion ledger** — the list of mechanisms that killed past programs, each scoped to the
  narrowest class it covers, with what it does not exclude and when it expires.
- **Lock** — the hashed record of a pre-registration's thresholds, splits and stop rules.
- **Gray zone** — the pre-written policy for a borderline or partial gate result.
- **Operating point** — the named setting (size, latency, memory, cost, cadence) where the claim
  must hold, with the value metrics that matter there.
- **Value metrics** — the business numbers a claim must move: time to solution (full pipeline
  latency), cost to solution ($ per task), energy to solution, solution quality (the accuracy bar),
  and value per run ($ impact on a business KPI).
- **Shots** — circuit repetitions to estimate an output: ≈1/ε² for precision ε, ≈1/ε with
  amplitude estimation.
- **Sign-free (stoquastic)** — a Hamiltonian whose off-diagonal entries are all non-positive in
  some simple basis; Monte Carlo methods become credible competitors (Rule 1).
- **Potential quantum advantage** — evidence consistent with an advantage type, not ruled out by
  Rule 1 or by overheads, and not yet shown in practice.
- **Claim ladder** — `speculative → plausible → observed → supported → strong → published`
  (↘ `refuted`). A single self-run experiment is capped at `observed`.
