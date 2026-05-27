# QML Domain Criteria for Paper Triage and Evaluation

Version: 1.0 | Last updated: 2026-05-27
Maintainers: Tsahi, Meir, Adi — edit this file as the team's understanding evolves.

This document is the authoritative source for how the team evaluates QML papers.
It is loaded by the `/qml-triage` and `/qml-evaluate` skills as a cached context block.
**Edit criteria here; skills pick up changes automatically.**

---

## How to Apply These Criteria

Each criterion produces one of three verdicts:
- **FAIL** — clear, specific failure evidence found → whole paper gets SKIP (unless overridden by context)
- **WARN** — ambiguous; paper does not clearly pass but evidence is insufficient to SKIP → contributes to TRIAGE
- **PASS** — paper explicitly addresses this criterion or is clearly out of scope for it

A paper is **SKIP** if any criterion is FAIL.
A paper is **TRIAGE** if no criterion is FAIL but at least one is WARN.
A paper is **PASS** only if all criteria are PASS.

Severity of a FAIL:
- **CRITICAL** — alone sufficient to SKIP (e.g., dequantization-vulnerable, toy baseline only)
- **MAJOR** — SKIP unless the paper's novelty is exceptional on another dimension
- **MINOR** — WARN, not FAIL

---

## Criterion 1: Dequantization Risk

### Definition
A QML method is **dequantization-vulnerable** if a classical algorithm using randomized linear algebra — specifically Nystrom approximation, Random Fourier Features (RFF), sketching, or low-rank matrix methods — can reproduce the same computational result within polynomial overhead. If so, the quantum advantage disappears classically and the paper's main claim is likely invalid.

Key references: Ewin Tang's dequantization results (2018, 2019); Cotler et al. (2021) on classical shadow tomography reproducing quantum kernel estimates.

### What a Failing Paper Looks Like
- Claims speedup for a quantum kernel or quantum linear algebra routine without proving hardness of classical approximation
- Uses a quantum kernel of the form K(x,y) = |⟨φ(x)|φ(y)⟩|² where φ is a polynomial-depth circuit — these are known to be approximable by RFF
- Cites exponential advantage in a sampling or linear-algebra task without addressing Tang-style reductions
- Advantage holds only in the query complexity model (oracle access) without evidence it persists in the realistic model where classical algorithms can exploit data structure
- Paper benchmarks against a classical SVM or kernel method without testing whether an RFF approximation of the proposed quantum kernel achieves comparable accuracy

**Red flags in abstract/intro:** "quantum speedup for linear systems," "quantum advantage for kernel methods," "exponential speedup for recommendation," "quantum PCA advantage" — all require dequantization check.

### What a Passing Paper Looks Like
- Explicitly proves or cites a hardness result showing the task is not efficiently Nystrom/RFF-approximable
- Works in a regime (e.g., highly non-stationary kernel, specific data manifold) where classical low-rank approximation is provably insufficient
- Demonstrates empirically that an RFF approximation of their quantum kernel performs substantially worse (not just slightly) on the target task
- Addresses dequantization risk explicitly in a limitations or related work section

### Examples
**Failing:** "We propose a quantum kernel for molecular property prediction and show it outperforms an SVM on a 100-molecule benchmark." → No dequantization check. The quantum kernel is almost certainly RFF-approximable. SKIP.

**Passing:** "Our quantum kernel exploits Hamiltonian simulation on neutral-atom hardware; we show that the resulting feature map cannot be efficiently approximated by polynomial-degree classical kernels on this graph-structured data." → Explicit argument against classical approximation. Advance to full read.

---

## Criterion 2: Geometric Difference

### Definition
A quantum kernel K_Q(x,y) has **genuine geometric difference** from classical kernels (RBF, polynomial, Matérn) if it induces a fundamentally different geometry on the data manifold — one that cannot be reproduced by any classical kernel family even in principle, not just in practice. Without geometric difference, a quantum kernel is an expensive way to approximate something classical methods already do well.

Geometric difference was formalized by Huang et al. (Nature Communications, 2021): a quantum kernel provides learning advantage only if it has high geometric difference with the best classical kernel for the task.

### What a Failing Paper Looks Like
- Proposes a quantum kernel without checking whether its feature space geometry is distinct from standard kernel families
- Shows performance improvement over a generic SVM but does not test against the best-tuned classical kernel (e.g., ARD-RBF, Matérn 5/2 with automatic relevance determination)
- Claims the quantum kernel "captures quantum correlations" without specifying what classical correlations it cannot capture
- The circuit is a single-layer encoding (Z-feature map, ZZ-feature map) — these produce kernels equivalent to truncated Fourier series and have minimal geometric difference from cosine kernels

**Red flags:** Single-layer Pauli encoding circuits; ZZ-feature maps on low-dimensional data; "quantum-enhanced SVM" without kernel comparison.

### What a Passing Paper Looks Like
- Computes or bounds the geometric difference between the proposed quantum kernel and the best-performing classical kernel on the target dataset
- Demonstrates that the quantum kernel separates data that no polynomial-degree classical kernel separates well
- Uses hardware-native entanglement patterns (e.g., neutral-atom Rydberg interactions) that generate correlations structurally unavailable to classical kernel families
- Provides theory on why the specific data structure (graph topology, many-body physics, molecular geometry) requires the specific quantum geometry

---

## Criterion 3: Trainability / Simulability Trilemma

### Definition
Parameterized quantum circuits (PQCs) face a fundamental trilemma:
1. **Barren plateaus** — generic random circuits have exponentially vanishing gradients, making training impossible at scale
2. **Classical simulability** — circuits shallow enough to train are often classically simulable via tensor networks, stabilizer methods, or polynomial-time algorithms
3. **Expressibility trap** — maximally expressive circuits have barren plateaus; low-expressibility circuits offer no quantum advantage

A paper that does not address all three corners of this trilemma for its specific circuit architecture is incomplete.

Reference: McClean et al. (2018) on barren plateaus; Cerezo et al. (2021) on cost-function-dependent plateaus; Napp et al. (2022) on classical simulation of shallow circuits.

### What a Failing Paper Looks Like
- Uses a deep (>10-20 layer) random PQC without addressing barren plateau mitigation
- Claims trainability for a circuit that has been shown to be in the barren-plateau regime by prior work
- Uses a shallow, low-entanglement circuit on a task where classical simulation (e.g., MPS/DMRG) trivially applies
- Reports training success on toy problems (n ≤ 6 qubits) and extrapolates to large-n without noise or gradient analysis
- Does not report whether gradients vanish with system size
- Uses hardware-efficient ansatz (HEA) on a non-chemistry task without justification — HEA is known to suffer from barren plateaus on generic tasks

**Red flags:** n ≤ 10 qubit experiments only; no gradient norm vs. system size analysis; "hardware-efficient ansatz" with no barren plateau discussion; "random circuit" or "random initialization."

### What a Passing Paper Looks Like
- Uses a structured ansatz (QAOA-style, problem-specific, Hamiltonian simulation) with theoretical justification for gradient propagation
- Provides gradient norm scaling analysis showing polynomial rather than exponential decay
- Uses mid-circuit measurement or feedforward to escape the trainability-expressibility trap
- Demonstrates the circuit is not classically simulable via a hardness argument or by showing tensor network contraction cost is exponential for the specific structure
- Employs reservoir computing or Hamiltonian kernel approaches that sidestep the training problem entirely (fixed-parameter circuits)

---

## Criterion 4: Hardware Fit — NISQ / Neutral Atom

### Definition
The team's hardware context is **neutral-atom processors** (Pasqal, QuEra, Atom Computing), operating in the NISQ regime (50–500 qubits, no error correction, coherence-limited depth). Our partner is Q-Factor.

A paper is hardware-realistic if its approach maps to this regime without requiring: fault-tolerant error correction, QRAM of size O(N), depth O(polylog N), or connectivity beyond what neutral-atom hardware provides.

### What a Failing Paper Looks Like
- Requires fault-tolerant quantum computation (QFT, Shor, HHL, Grover) as a subroutine
- Assumes QRAM for data loading (exponential state preparation is intractable)
- Requires all-to-all connectivity but neutral-atom hardware is 2D grid or configurable geometry
- Circuit depth exceeds coherence limits (typically T2-limited to O(100-1000) two-qubit gates on current neutral-atom hardware)
- Claims hardware results on superconducting (IBM/Google) qubits and extrapolates to neutral atom without topology/noise analysis
- "Near-term" claim but requires >100 logical qubits

**Red flags:** "Assumes QRAM," "fault-tolerant gate set," circuit depth O(n log n) or worse for n > 50, superconducting-only experiments claimed as general.

### What a Passing Paper Looks Like
- Explicitly analyzes neutral-atom gate fidelities, coherence times, and qubit connectivity
- Circuit depth ≤ O(100) two-qubit gates for n ≤ 200 qubits
- Uses Rydberg-native gates (CZ, CCZ via blockade) rather than generic universal gates
- Demonstrates graph-structured entanglement that maps to neutral-atom reconfigurable arrays
- Identifies the specific neutral-atom primitive (analog Hamiltonian simulation, digital circuit, hybrid analog-digital) being exploited
- Quantum advantage claimed for n = 50-300 qubit regime accessible within 2-3 years

### Hardware Parameter Reference (update as hardware improves)
- Two-qubit gate fidelity: ~99.5% (best current neutral atom)
- Coherence time: T2 ~ 1-10 seconds (atom-clock transitions)
- Max qubits demonstrated: ~256 (QuEra Aquila), 100+ (Pasqal)
- Native gates: CZ (Rydberg blockade), local and global single-qubit rotations
- Connectivity: reconfigurable 2D arrays, limited all-to-all via atom transport

---

## Criterion 5: Strong Classical Baseline

### Definition
A QML paper demonstrates quantum advantage only relative to the **best available** classical method for the same task, trained and tuned appropriately. Using a weak, untuned, or obsolete classical baseline is the single most common failure mode in QML papers and renders the advantage claim invalid.

### Task-Specific Baseline Requirements

**Tabular / low-dimensional ML:**
- Required: TabPFN-2.5 (2026 version), XGBoost with Optuna/Bayesian hyperparameter tuning, LightGBM
- NOT acceptable: vanilla MLP, untuned SVM, logistic regression, decision tree
- Special case: if the paper claims few-shot or meta-learning advantage, compare to few-shot tabular methods (SAINT, TabPFN in few-shot mode)

**Graph-structured data / molecular properties:**
- Required: GNN (GIN, MPNN, or SchNet for molecules), SOAP kernel with Gaussian process regression, GAP (Gaussian Approximation Potential) for energy prediction
- NOT acceptable: generic SVM on flattened molecular fingerprints, MLP on hand-crafted features

**Time series / dynamical systems:**
- Required: LSTM, Transformer-based forecasters (Mamba, PatchTST), state-space models (S4, Mamba)
- NOT acceptable: ARIMA, vanilla RNN

**Image recognition:**
- Required: ResNet/ViT on same data volume; classical kernel methods (CKKS, RBF-SVM)
- NOT acceptable: MLP, LeNet on simple benchmarks

**Combinatorial optimization:**
- Required: state-of-the-art classical solvers (Gurobi, commercial MIP, simulated annealing with best-practice hyperparameters)
- NOT acceptable: greedy heuristics or brute force

### What a Failing Paper Looks Like
- Quantum model outperforms "MLP baseline" or "standard SVM" without testing TabPFN/XGBoost
- Classical baseline uses default hyperparameters while the quantum model is tuned
- Advantage demonstrated only on datasets with n ≤ 100 training examples without controlling for the regime where TabPFN is known to dominate (n < 1000)
- Classical baseline is run on CPU while quantum model timing is excluded or compared to GPU classical runs
- No ablation: removing the quantum component produces similar performance

**Red flags:** Comparison to "neural network baseline"; "we compare to SVM with RBF kernel"; datasets with fewer than 50 training examples; no hyperparameter search described for the classical model.

### What a Passing Paper Looks Like
- Explicitly names and cites the classical baselines used, with hyperparameter search protocol described
- Runs TabPFN-2.5 or XGBoost with Optuna tuning on all tabular benchmarks
- Shows quantum advantage persists across multiple random seeds and train/test splits
- Includes an ablation where the quantum component is replaced by a classical approximation to isolate the contribution
- Addresses the data efficiency regime explicitly: if advantage only appears at n < 100, this is noted as a limited claim

---

## Quick Reference: SKIP/TRIAGE/PASS Decision Table

| Criterion | SKIP (CRITICAL) | TRIAGE (WARN) | PASS |
|-----------|-----------------|---------------|------|
| Dequantization | Clear RFF/Nystrom vulnerability; no hardness argument | Partially addresses; regime unclear | Explicit hardness or empirical disproof |
| Geometric diff | Single-layer encoding; ZZ-feature map only | Uses structured encoding, no comparison | Geometric difference computed or argued |
| Trainability | Barren plateau regime; n ≤ 8 qubits only | Shallow circuit, no simulability check | Gradient analysis + simulability addressed |
| Hardware fit | QRAM assumed; fault-tolerant required | Superconducting-only; depth borderline | Neutral-atom analysis explicit |
| Classical baseline | Toy baseline (MLP/SVM default) only | Missing one required baseline | All required baselines, tuned |

**Any CRITICAL = SKIP immediately.** TRIAGE requires at least 2 criteria at WARN with none at CRITICAL.

---

## Venue Tier List (Source Priority)

When evaluating how much to trust a paper's claims, apply this priority order:

| Tier | Venues | Weight |
|------|--------|--------|
| T1 — Peer-reviewed top-venue | Nature, Science, PRL, PRX Quantum, NeurIPS, ICML, ICLR | Highest |
| T2 — Strong peer-reviewed | QST (IOP), npj Quantum Information, PRApplied, JMLR, CVPR, AAAI | High |
| T3 — Peer-reviewed workshop | NeurIPS/ICML workshops, QIP contributed talks | Medium |
| T4 — Preprint, high citations | arXiv with ≥20 citations within 1 year | Low-medium |
| T5 — Recent preprint | arXiv < 1 year, < 20 citations | Low — caveat all claims |

For triage: T4/T5 papers require stricter evidence before PASS. T1/T2 papers may get TRIAGE instead of SKIP on borderline criteria.

---

## Current Strong Directions (Update as Landscape Evolves)

Papers in these directions should be read unless they fail a criterion outright:
- Neutral-atom graph kernels and Rydberg-native ML
- Quantum reservoir computing on neutral-atom hardware
- Hamiltonian kernels (kernel defined by quantum evolution)
- Dynamic circuits with mid-circuit measurement and feedforward
- MBQC-style architectures for learning
- Geometric quantum machine learning (equivariant circuits on molecular symmetry groups)
- Quantum advantage for specific structured graph problems (graph isomorphism testing, graph property learning)

---

## Deprioritized Directions (Do Not Re-Suggest Without New Evidence)

Skip papers in these directions unless they present fundamentally new evidence:
- Generic low-data tabular VQC demos (n < 200 samples, standard UCI datasets)
- Single-encoding PQC claims (ZZ-feature map, Z-feature map) — equivalent to truncated Fourier
- Generic HHL linear-algebra speedups without dequantization refutation
- Quantum advantage on MNIST, iris, or breast cancer datasets
- "Quantum neural network" papers with hardware-efficient ansatz on non-quantum data
- Variational quantum eigensolver (VQE) for chemistry without noise analysis and classical baseline (CCSD(T), DMRG)

---

## Expanded Scope: QML-Adjacent Papers

Direct QML papers are the primary target, but the team also needs signal from adjacent quantum
computing areas where results have direct implications for QML methods, hardware, or approaches.

**A paper is in scope for triage if it falls into any adjacent category below.**
Apply the 5 core criteria with appropriate N/A markings, plus the QML Transfer Value gate.

---

### Adjacent Category A — Quantum Circuit Primitives for QML

Papers about state preparation, circuit optimization, gate design, barren plateau mitigation,
or entanglement structure that directly enable or constrain QML circuits.

**Examples:** shallow circuit encoding of MPS states, local vs global cost functions for VQC
training, entanglement-efficient circuit architectures, tensor-network-based circuit design.

**Why in scope:** QML methods are built on these primitives. An improvement in circuit encoding
depth or a solution to barren plateaus directly unlocks better QML training.

**What makes it PASS/TRIAGE (not SKIP):**
- Proposes a specific, novel technique (not just a survey)
- Claims are demonstrated experimentally or proved theoretically (sound evidence)
- The technique generalizes beyond a single narrow use case
- QML Transfer Value is HIGH: directly applicable to QML circuit design or training

**What keeps it SKIP:**
- General technique already covered by existing literature (e.g., standard VQE barren plateau papers)
- Hardware platform incompatible with neutral-atom regime with no adaptation path
- Technique only applies to toy circuit sizes (n ≤ 4 qubits)

---

### Adjacent Category B — Quantum Optimization with Graph/ML Connections

Papers about quantum algorithms for graph problems, combinatorial optimization, or quantum
sampling where results intersect with graph-structured QML or data-efficient learning.

**Examples:** quantum MaxCut variants, graph isomorphism, quantum sampling for structured data,
QAOA-style approaches on graph problems with ML-relevant structure.

**Why in scope:** Graph optimization methods inform quantum graph kernel design; quantum sampling
approaches may feed into data augmentation or Boltzmann machine-style generative models.

**What makes it PASS/TRIAGE (not SKIP):**
- Demonstrates genuine (non-trivially-simulable) quantum advantage on a graph problem
- Identifies a graph structure where quantum circuits outperform classical GNNs or spectral methods
- QML Transfer Value is HIGH or MEDIUM: the graph approach is adaptable to learning tasks

**What keeps it SKIP:**
- Explicitly classically simulable (circuit is tractable classically, paper acknowledges it)
- No quantum advantage claimed or demonstrated on the target graph problem
- Graph problem is not connected to any learning task or data representation the team cares about

---

### Adjacent Category C — Hardware Architecture / NISQ Constraints Relevant to QML

Papers about neutral-atom hardware capabilities, gate fidelity, error mitigation, fault-tolerant
design, or QEC overhead that affect what QML circuits are realistic to deploy.

**Examples:** full-stack neutral atom quantum processor design, LDPC code overhead analysis for
NISQ algorithms, Rydberg gate fidelity improvements, reconfigurable array topology for ML kernels.

**Why in scope:** Hardware constraints are the binding constraint on QML deployment; understanding
the 2–3 year hardware roadmap directly governs which QML approaches are viable.

**What makes it PASS/TRIAGE (not SKIP):**
- Directly analyzes neutral-atom / Rydberg hardware (not just generic quantum hardware)
- Reports gate fidelity, coherence times, or qubit counts relevant to QML circuit requirements
- Identifies specific constraints or opportunities for QML (e.g., "this topology enables these kernels")
- QML Transfer Value is HIGH or MEDIUM

**What keeps it SKIP:**
- Superconducting/trapped-ion only with no neutral-atom relevance
- Pure fault-tolerant quantum computing with no NISQ-regime bridge
- No connection to circuit depths or qubit counts accessible in 2–3 years

---

### QML Transfer Value Assessment (for Adjacent Papers)

For every adjacent paper, assess QML Transfer Value after applying the 5 criteria:

| Value | Meaning | Triage outcome |
|-------|---------|----------------|
| HIGH | Technique or result directly applicable to QML circuit design, training, or hardware deployment | TRIAGE or PASS (criteria permitting) |
| MEDIUM | Provides useful context, negative result, or design constraint for QML directions | TRIAGE with narrow checklist |
| LOW | Interesting quantum computing result but no clear QML application path | SKIP regardless of criteria scores |

**Additional gate:** An adjacent paper with QML Transfer Value = LOW is SKIP even if all 5 criteria
technically pass. The team's time is bounded; adjacent papers must earn their read.

---

### Applying the 5 Criteria to Adjacent Papers

Mark a criterion N/A when it genuinely does not apply to the paper type:

| Criterion | Mark N/A when... |
|-----------|-----------------|
| Dequantization Risk | Paper makes no quantum speedup claim (e.g., pure circuit design, hardware characterization) |
| Geometric Difference | Paper is not about a quantum kernel or feature map |
| Trainability | Paper is not about a parameterized/trained circuit |
| Hardware Fit | Paper is explicitly about hardware characterization (hardware fit IS the subject) |
| Classical Baseline | Paper is not about a learning task with classical ML comparators |

All N/A markings must include a one-sentence justification.
