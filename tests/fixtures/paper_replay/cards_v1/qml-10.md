id: qml-10
title: Learning from experiments
paper: Huang et al., Quantum advantage in learning from experiments (arXiv Dec 2021; Science 376, 1182, 2022)
link: https://arxiv.org/abs/2112.00778
type: Mechanism
cutoff: 2021-12-01
domain: qml
profile: formal

## expected_verdict
Supported (scoped), tier C. Information-theoretic theorems prove exponential separations in the number of experiments (copies), not runtime. A 40-qubit Sycamore experiment beats the proven conventional lower bound on specific tasks. No independent replication found; theory companions share authors.

## I0
Can quantum memory reduce experiment counts for a specified learning task?

## evidence
- Theorem 1 (observables): conventional experiments need Ω(2^n) to predict |⟨O⟩| for an observable from a set; quantum-enhanced need O(1).
- Theorem 2 (quantum PCA): conventional need Ω(2^(n/2)) to learn a property of the principal component; quantum-enhanced need O(1). Authors address Tang-style classical qPCA: those assume entry access to exponential precision, which itself costs exponentially many experiments.
- Theorem 3 (processes): learning approximate models of physical dynamics; e.g. distinguishing time-reversal-symmetric from general unitaries.
- Protocol: store two copies in quantum memory and do a Bell measurement across them; conventional = measure each copy (classical shadows as the best known strategy).
- Experiment: Google Sycamore, up to 40 qubits (20 system + 20 memory), ~1,300 gates; state ρ = 2^(−n)(I + 0.95·P); GRU classifier trained on noiseless simulation for n < 8, tested on hardware for n = 8–20; metric = experiments to reach 70% accuracy (Fig. 2c); hardware beats the conventional lower bound; 1,000 total copies per arm in the process task.

## intake
- Scope: sample complexity (number of experiments) for learning properties of states and processes, with vs without coherent quantum memory.
- Regime: specific constructed tasks (Pauli magnitude, principal-component property, symmetry of dynamics); n up to 20 system qubits on noisy hardware.
- Assumptions: the physical system can be transduced into a stable quantum memory; conventional strategies are single-copy measurements with classical processing; the lower bound covers all such strategies.
- Falsifier: a single-copy strategy beating the Ω(2^n) bound (proof error); or hardware results falling below the conventional lower bound once noise grows.

## screen
- Must flag: advantage is in experiment count, not runtime; tasks are constructed; transduction into quantum memory is assumed; hardware shows the tasks, not general utility.
- Must request: independent replication; overhead of the GRU training on simulated data.

## retrieval
- Pre-cutoff must-finds: Chen, Cotler, Huang & Li 2021, exponential separations with and without quantum memory; Bubeck, Chen & Li 2020, entanglement is necessary for optimal property testing; Lloyd et al. qPCA; Tang 2021 and Chia et al. 2020 dequantization; classical shadows (Huang, Kueng & Preskill 2020).
- Current mode: none independent in the inventory; companion theory papers share authors.

## designer
- For each task: copies needed to reach a fixed accuracy for (a) best single-copy strategy, (b) two-copy Bell protocol; across n; on hardware and noiseless simulation. Report runtime separately.

## champion
- Classical shadows / randomized single-copy measurement with optimal classical post-processing, plus the proven lower bound curve.

## panel
- Accept the theorems; require that any "advantage" wording names sample complexity; request a replication plan on another platform.

## run
- Simulate the two-copy Bell protocol for n ≤ 10 on ρ = 2^(−n)(I + 0.95P) and compare to a shadows baseline; hardware data not reproducible locally.

## verdict
- Label: Supported (scoped), tier C.
- Must say: sample-complexity separation, information-theoretic, holds even for unentangled states; independent replication absent.
- Must not say: a computational (runtime) speedup; or that the result is replicated.

## audit
- Check: 40 qubits / 1,300 gates; 2^n and 2^(n/2) bounds; 70% accuracy threshold; n = 8–20 on hardware; author overlap with theory companions.

## variants
- Independent replication on trapped-ion or neutral-atom hardware with matched information access; or a task with natural (not constructed) states.
