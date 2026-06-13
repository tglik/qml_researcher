---
id: mis-neutral-atom-context
type: primitive_context
primitive: "Maximum Independent Set (MIS)"
hardware: "neutral-atom (Rydberg blockade)"
regime: ANALOG
source: "Tsahi deep-research session, 2026-06-13"
---

# MIS on Neutral-Atom Hardware — Research Context

Pre-seeded context for `/qml-primitive-transfer` test fixture.
Derived from the team's paper-review run on quantum optimization / MIS (2026-06-13).

---

## The Primitive

**Maximum Independent Set (MIS):** Given an undirected graph G = (V, E), find the largest
subset S ⊆ V such that no two vertices in S share an edge.

**Complexity:** NP-hard in general. Best classical approximation within O(n / log² n) vertices.
Exact solution requires exponential time in the worst case for dense graphs.

---

## Why Neutral Atoms Are a Natural Fit

Rydberg atom arrays encode the MIS problem natively via the **Rydberg blockade mechanism**:

1. Each atom = one graph vertex.
2. Two atoms within blockade radius r_b cannot both be in the Rydberg excited state
   simultaneously — this is the independent set constraint (no adjacent pair both selected).
3. The system Hamiltonian drives atoms toward states that maximize the number of excited atoms
   subject to the blockade, which corresponds to finding a maximum independent set.
4. Atom positions (and therefore graph connectivity) are programmable via spatial light
   modulators or holographic tweezers.

**Key property:** The MIS ground state is encoded in the *physical* configuration of the atom
array — not in a circuit depth that scales with problem size. This is what makes analog
Rydberg hardware qualitatively different from gate-based quantum computers for this problem.

**Experimental references:**
- Ebadi et al. (2022, Nature): 289 atoms, solved MIS on king graph instances up to n=289.
  Classical solvers could verify solutions but could not replicate the quantum sampling
  distribution efficiently for the hardest instances.
- Wurtz et al. (2022): MWIS (Maximum Weight Independent Set) on Rydberg arrays with
  non-uniform detuning profiles — directly relevant to weighted combinatorial optimization.
- Nguyen et al. (2023): near-optimal solutions on unit-disk graphs, matching and sometimes
  beating classical approximation algorithms for n up to ~200 atoms.

---

## Current Hardware Constraints

| Constraint | Current state | Implication |
|------------|--------------|-------------|
| Atom count | ~100–300 (lab), ~1000 roadmap | Graph size limited; most real ML problems need reduction to fit |
| Connectivity | Unit-disk graphs (2D plane embedding) | Graph must be planar-embeddable or needs MWIS embedding |
| Coherence time | ~μs to ms | Short enough that circuit-style gates are limited; analog evolution preferred |
| Repetition rate | ~kHz | Multiple shots feasible; sampling from the MIS distribution is the use model |
| Precision | Approximate solutions | Exact MIS not guaranteed; near-optimal solutions are the regime |

---

## Known Equivalent Problems (Ground Truth for Test Evaluation)

This section documents the known reduction relationships for use by the test evaluator.
The `problem-mapper` agent should find at least these:

| Problem | Direction | Type | Notes |
|---------|-----------|------|-------|
| Vertex Cover | ↔ | poly-time (complement) | S is MIS iff V\S is Vertex Cover |
| Maximum Clique | ↔ | poly-time (complement graph) | MIS in G = Max-Clique in Ḡ |
| Set Packing | ← | poly-time | MIS is a special case of Set Packing |
| Maximum Weight Independent Set (MWIS) | ← | special-case (generalization) | MIS = MWIS with uniform weights |
| QUBO / Ising | ↔ | poly-time | MIS encodes as QUBO with penalty λ per edge violated |
| 3-SAT | → | poly-time | Standard NP-completeness reduction (theoretical, not practical for quantum) |
| Graph Coloring | → | poly-time (chromatic number bound) | MIS size bounds chromatic number: χ(G) ≥ n / α(G) |
| Constraint Satisfaction (binary) | ← | special-case | MIS is binary CSP with pairwise edge constraints |

**Direction notation:**
- `←` = given a MIS solver, you can solve this problem (useful direction for the primitive)
- `→` = given this problem solved, you can solve MIS (not the useful direction for acceleration)
- `↔` = bidirectional equivalence

---

## Known ML Workloads (Ground Truth for Test Evaluation)

This section documents ML workloads that genuinely connect to the MIS primitive.
The `problem-mapper` agent should find at least 3 of these:

| ML Workload | Connects via | Classical bottleneck | NISQ-feasible |
|-------------|--------------|---------------------|---------------|
| Feature selection (high-dimensional tabular) | MWIS | Exponential search over feature subsets; approximate methods lose correlated-feature structure | PARTIAL (n~200 features) |
| Graph community detection (conflict-based) | MIS / Vertex Cover | NP-hard for max-modularity partitioning; spectral methods are approximate | PARTIAL |
| Ensemble pruning / model selection | Set Packing | Selecting diverse, non-redundant model subsets is Set Packing; greedy approximation suboptimal | YES (small ensembles) |
| Collision-free trajectory planning (multi-agent RL) | MIS | At each timestep, valid joint actions = independent set in conflict graph | PARTIAL |
| Fraud ring detection (graph anomaly) | MIS / Vertex Cover | Finding isolated fraud cliques = MIS on transaction conflict graphs | PARTIAL |
| Portfolio optimization (binary selection) | MWIS | Selecting assets with maximum return subject to pairwise constraints | PARTIAL |
| Hyper-parameter search (configuration spaces) | CSP / MIS | Compatible configuration search = CSP with pairwise incompatibility constraints | YES (small spaces) |

---

## Notes for Test Evaluators

- The `problem_coverage` axis should award full credit if `01_equivalent_problems.md` correctly
  identifies Vertex Cover, Max-Clique, QUBO/Ising, and Set Packing with the correct reduction
  directions from this ground truth table.
- The `ml_workload_traceability` axis should award full credit if `02_ml_workloads.md` includes
  at least 3 workloads from the table above with explicit "connects via" traces.
- The `business_rating_depth` axis should flag a failure if all workloads receive HIGH aggregate
  — feature selection and ensemble pruning are strong candidates, but trajectory planning and
  hyperparam search are closer to MED or PARTIAL-timeline at current NISQ scale.
