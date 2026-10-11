# Paper-replay candidates (verified 2026-10-11)

Evaluator-only: contains proposed outcomes. Outcomes and tiers are curator hypotheses until a
human reads the citing passages in `candidates_verified.json`. Citation impact is a selection
tiebreaker only, never a correctness signal (design doc §4).

| ID | Domain | Original | Pub. | Cites | FWCI | Pctl | Adjudicators (cites original? / author overlap) | Proposed outcome | Tier guess | Issues |
|---|---|---|---|---|---|---|---|---|---|---|
| qml-01 | qml | Supervised learning with quantum enhanced feature spaces | 2018-04-30 | 2529 | 81 | 100.0 | 2208.11060 (yes); 2111.05451 (yes) | conditional_limitation | B | — |
| qml-02 | qml | Quantum Convolutional Neural Networks | 2018-10-09 | 1482 | 45 | 99.9 | 2408.12739 (yes) | conditional_limitation | B | — |
| qml-03 | qml | Quantum Recommendation Systems | 2016-03-29 | 85 | — | — | 1807.04271 (yes) | refuted_exponential_separation | A | — |
| qml-04 | qml | Quantum principal component analysis | 2013-07-01 | 1373 | 32 | 99.8 | 1811.00414 (yes) | conditional_limitation | B | — |
| qml-05 | qml | Data re-uploading for a universal quantum classifier | 2019-07-03 | 650 | 18 | 99.5 | 2403.07059 (yes) | mixed | A | — |
| qml-06 | qml | Power of data in quantum machine learning | 2020-11-03 | 760 | 32 | 99.8 | 2403.07059 (yes) | supported_scoped | B | — |
| qml-07 | qml | A rigorous and robust quantum speed-up in supervised machine learning | 2020-10-05 | 553 | 27 | 99.8 | — | supported_scoped | C | no_adjudicator |
| qml-08 | qml | Barren plateaus in quantum neural network training landscapes | 2018-03-29 | 2275 | 49 | 99.9 | 2001.00550 (yes); 2405.00781 (yes, overlap) | supported | A | author_overlap:2405.00781:j.mcclean |
| qc-01 | qc | Quantum supremacy using a programmable superconducting processor | 2019-10-23 | 7742 | 405 | 100.0 | 2111.03011 (yes) | refuted_cost_estimate | A | — |
| qc-02 | qc | Evidence for the utility of quantum computing before fault tolerance | 2023-06-14 | 1035 | 92 | 100.0 | 2306.14887 (yes); 2306.16372 (not found) | conditional_limitation | A | citation_not_found:2306.16372 |
| qc-03 | qc | Quantum computational advantage using photons | 2020-12-03 | 2269 | 122 | 100.0 | 2109.11525 (yes, overlap) | conditional_limitation | B | author_overlap:2109.11525:l.li |
| qc-04 | qc | Beyond-classical computation in quantum simulation | 2024-03-01 | 134 | 55 | 100.0 | 2503.05693 (yes); 2503.08247 (not found) | contested | Unscorable | citation_not_found:2503.08247 |
| qc-05 | qc | What is the Computational Value of Finite Range Tunneling? | 2015-12-07 | 267 | 31 | 99.7 | 1604.01746 (yes) | conditional_limitation | B | — |
| qc-06 | qc | Quantum algorithm for solving linear systems of equations | 2008-11-19 | 3307 | 23 | 99.6 | 10.1038/nphys3272 (yes) | conditional_limitation | B | — |
| phys-01 | physics | Quantized Majorana conductance | 2017-10-29 | 520 | 52 | 100.0 | 10.1038/s41586-021-03373-x (not found, overlap); 2004.08583 (not found, overlap) | refuted | A | citation_not_found:10.1038/s41586-021-03373-x, author_overlap:10.1038/s41586-021-03373-x:b.shojaei,c.liu,d.car,d.pennachio,d.xu,e.bakkers,g.wang,h.zhang,j.bommer,j.lee,j.logan,l.kouwenhoven,m.moor,m.pendharkar,m.verheijen,n.loo,p.veldhoven,r.veld,s.gazibegovic,s.koelling,s.sarma, citation_not_found:2004.08583, author_overlap:2004.08583:e.bakkers |
| phys-02 | physics | The First Room-Temperature Ambient-Pressure Superconductor | 2023-07-22 | 52 | — | — | — | refuted | A | no_adjudicator |
| phys-03 | physics | Solving the Quantum Many-Body Problem with Artificial Neural Networks | 2016-06-07 | 2216 | 88 | 100.0 | 2302.04919 (yes, overlap) | supported_scoped | B | author_overlap:2302.04919:g.carleo |
| ml-01 | ml | Neural Collaborative Filtering | 2017-08-16 | 221 | — | — | 2005.09683 (yes); 1907.06902 (yes) | refuted | A | — |
| ml-02 | ml | TabNet: Attentive Interpretable Tabular Learning | 2019-08-20 | 124 | 12 | 99.0 | 2106.03253 (yes); 2207.08815 (yes) | refuted | A | — |
| ml-03 | ml | Batch Normalization: Accelerating Deep Network Training by Reducing Internal Covariate Shift | 2015-02-11 | 23776 | — | — | 1805.11604 (yes) | mixed | A | — |
| ml-04 | ml | How Powerful are Graph Neural Networks? | 2018-10-01 | 371 | — | — | 1912.09893 (yes) | mixed | A | — |
| ml-05 | ml | Multi-Similarity Loss with General Pair Weighting for Deep Metric Learning | 2019-04-14 | 104 | — | — | 2003.08505 (yes) | conditional_limitation | A | — |
| ml-06 | ml | Improved Training of Wasserstein GANs | 2017-03-31 | 1470 | — | — | 1711.10337 (yes) | conditional_limitation | B | — |
| ml-07 | ml | Neural Architecture Search with Reinforcement Learning | 2016-11-05 | 4325 | — | — | 1707.05589 (yes) | refuted | A | — |
| ml-08 | ml | Deep Residual Learning for Image Recognition | 2015-12-10 | 4644 | — | — | 1812.01187 (yes) | supported | A | — |
| qml-09 | qml | Predicting Many Properties of a Quantum System from Very Few Measurements | 2020-02-18 | 1170 | 40 | 99.9 | 2008.05234 (yes) | supported | A | — |
| qml-10 | qml | Quantum advantage in learning from experiments | 2021-12-01 | 512 | 35 | 99.9 | — | supported_scoped | C | no_adjudicator |
| qc-07 | qc | Experimental loophole-free violation of a Bell inequality using entangled electron spins separated by 1.3 km | 2015-08-24 | 2835 | 130 | 100.0 | 1511.03190 (yes, overlap); 1511.03189 (yes, overlap) | supported | A | author_overlap:1511.03190:c.abellan,m.mitchell,v.pruneri,w.amaya, author_overlap:1511.03189:c.abellan,m.mitchell,v.pruneri,w.amaya |
| qc-08 | qc | Quantum error correction below the surface code threshold | 2024-08-24 | 748 | 113 | 100.0 | — | supported_scoped | C | no_adjudicator |
| qc-09 | qc | Logical quantum processor based on reconfigurable atom arrays | 2023-12-07 | 1099 | 98 | 100.0 | — | supported_scoped | C | no_adjudicator |
| phys-04 | physics | Probing many-body dynamics on a 51-atom quantum simulator | 2017-07-13 | 2471 | 100 | 100.0 | 1711.03528 (yes) | supported | B | — |
| phys-05 | physics | Observation of Gravitational Waves from a Binary Black Hole Merger | 2016-02-11 | 14192 | 840 | 100.0 | 1811.01921 (yes) | supported | A | — |
| ml-09 | ml | Highly accurate protein structure prediction with AlphaFold | 2021-07-15 | 43933 | 1778 | 100.0 | 10.1002/prot.26171 (not found) | supported | A | citation_not_found:10.1002/prot.26171 |
| ml-10 | ml | Attention Is All You Need | 2017-06-12 | 26920 | — | — | 1806.00187 (yes) | supported | A | — |
| ml-11 | ml | BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding | 2018-10-11 | 45096 | — | — | 1907.11692 (yes) | supported_scoped | A | — |
| ml-12 | ml | Scaling Laws for Neural Language Models | 2020-01-23 | 1500 | — | — | 2203.15556 (yes) | mixed | A | — |

**Mix.** ml: 12; physics: 5; qc: 9; qml: 10 | outcomes conditional_limitation 9, contested 1, mixed 4, refuted 5, refuted_cost_estimate 1, refuted_exponential_separation 1, supported 8, supported_scoped 7 | tier guesses A 21, B 10, C 4, Unscorable 1

## Curation notes

- **qml-01**: Hardware demo on a synthetic dataset; the advantage claim is conjectural in the paper itself. Test whether the verdict separates the demonstration from the advantage claim.
- **qml-02**: Simulability holds for the locally easy, low-bodyness regimes studied; quantum data acquisition may still be needed. Score the exact claim.
- **qml-03**: Algorithm correctness survives; the exponential separation does not under comparable sampling access. Overlaps synthetic eval5.
- **qml-04**: Speedup on classical data is dequantized; the quantum-data-input setting is a different access model. Good scope test.
- **qml-05**: Universality is formal and survives; competitiveness against tuned classical baselines is the adjudicated part. Confirm the benchmark includes this model.
- **qml-06**: Positive case within an engineered-data scope. Confirm what the benchmark says about projected kernels before assigning a tier.
- **qml-07**: Formal positive control. No external adjudication identified yet; tier C until one is found. Mining found discussion (e.g. 2406.07072 on trainability vs dequantization) but no claim-level adjudication. Formal positive control; tier C unless an independent proof check is found.
- **qml-08**: Cerezo et al. is independent of the original authors; the 2024 review includes McClean and does not count toward independence.
- **qc-01**: The classical-cost estimate is refuted; the hardware fidelity results stand. Claim-level split. arXiv 1910.11333 is the supplementary information, not the paper; use the Nature DOI.
- **qc-02**: Error-mitigation accuracy survives; beyond-classical framing does not in the reported regime. Begusic & Chan citation not found in Semantic Scholar or OpenAlex reference lists; the paper's subject is this experiment, so treat as an index gap and confirm in the PDF.
- **qc-03**: Rebuttal spoofs the benchmark tests used; exact sampling hardness is not refuted. Claim-level. Author-overlap flag 'L. Li' is a name collision (Google vs USTC), not shared authorship.
- **qc-04**: Live dispute with replies; good test that the verdict stays INCONCLUSIVE rather than picking a side. Mauron & Carleo citation not found in either index; confirm in the PDF.
- **qc-05**: Speedup holds against simulated annealing; not against the strongest classical solvers. Weak-baseline lesson, directly relevant to criterion 5.
- **qc-06**: Algorithm stands; end-to-end advantage depends on input/output caveats. Matches the deprioritized-HHL rule in CLAUDE.md.
- **phys-01**: Retracted after data-selection issues. Verify the retraction notice DOI. The retraction note is by the original authors (self-retraction): authoritative for the claim's evidential status but not an independent replication. Yu et al. shares Bakkers (device growth). Confirm whether independent critics (e.g. published data-selection concerns) triggered the retraction before assigning tier A.
- **phys-02**: Multiple independent replications attributed effects to Cu2S impurities. Adjudicator IDs to be found by citation mining. Citation mining found no challenger: Semantic Scholar has few citation passages for this preprint. Find replication papers manually (independent synthesis attributing the transition to Cu2S).
- **phys-03**: Positive physics case. Benchmark compares many variational methods; check what it says about NQS accuracy in the original models. Variational benchmarks paper includes Carleo as co-author: not independent, so tier B at most unless an unrelated benchmark is found.
- **ml-01**: Weak-baseline case: a properly tuned dot product beats the MLP. Relevant to the lab's recsys experiments.
- **ml-02**: Tabular baseline case aligned with criterion 5 (XGBoost/TabPFN).
- **ml-03**: Performance claim supported; mechanism claim contradicted. Tests claim-level scoring.
- **ml-04**: Expressivity theorem survives; empirical margins shrink under fair evaluation with structure-agnostic baselines. Graph domain matches lab directions.
- **ml-05**: Gains largely vanish under fair comparison. Confirm the reality check includes this loss.
- **ml-06**: With enough tuning budget, objectives reach similar scores. Tuning-budget confound.
- **ml-07**: A well-tuned LSTM outperforms the searched cell. Hyperparameter-budget asymmetry.
- **ml-08**: Positive control. Bag of tricks (Amazon) is an independent re-implementation; confirm it re-tests the residual-vs-plain claim rather than only building on ResNet.
- **qml-09**: Quantum-learning positive with an independent experiment. Check author overlap and whether the experiment tests the scaling claim or one instance.
- **qml-10**: Positive quantum-advantage claim (sample complexity, not runtime). No independent replication identified; tier C. Theory companions share authors.
- **qc-07**: Three independent groups, different platforms. Positive quantum claim, foundations rather than advantage. Verified overlap: Abellan, Mitchell, Pruneri, Amaya (ICFO) co-author all three tests as suppliers of the random-number generators. Core experimental groups are independent, but the setting-choice component is shared; record it as a common-mode dependency when assigning the tier.
- **qc-08**: Positive QEC claim, no independent replication identified on another platform for the same claim. Tier C until one is found.
- **qc-09**: Neutral-atom positive, relevant to the Q-Factor track. No independent replication identified; tier C.
- **phys-04**: Observation reported as an anomaly, explained later by independent theory. Calibration case: the original evidence supports the observation, not a mechanism. Neutral-atom relevant.
- **phys-05**: Independent reanalysis of open data by a group outside the collaboration. Check author overlap (some may be LVC members).
- **ml-09**: Blind assessment by independent CASP assessors. Strongly memorized: use mainly as a perturbation parent. CASP14 assessment citation not found in either index (journal reference-list gap); confirm in the PDF.
- **ml-10**: Independent re-implementation that reproduces and improves the results. Strongly memorized: perturbation parent.
- **ml-11**: Replication confirms the gains and finds BERT undertrained; the next-sentence-prediction component is not supported. Claim-level split.
- **ml-12**: Power-law form supported; the compute-optimal allocation revised (parameters and tokens scale about equally).

## Nominated challengers from citation mining

Regex hits on citing passages. Leads only; most are false positives until read.

### qml-01: Supervised learning with quantum enhanced feature spaces

- Quantum Encoding Strategies for Drug Response Prediction: An Exhaustive Benchmark on a 20-Qubit Superconducting QPU (2026, 10.64898/2026.07.08.737310): "Previous benchmarks comparing encoding strategies have relied either on classical simulators [6–8] or on demonstrations limited to two to four qubits [5, 13]."
- Generative Quantum Data Embeddings for Supervised Learning (2026, 2605.30866): "These choices face limitations in near-term QML: amplitude encoding can incur nontrivial state-preparation overhead as the data dimension grows, while simple angle encoding may yield product states and therefore admit ef"
- Quantum Kernels for SVM Entanglement Detection (2026, 10.1109/CAI68641.2026.11536374): "Feature maps based on entangled Pauli-string interactions, such as Pauli feature maps, generate kernels for which no efficient classical simulation is known [7], [8]."
- Benchmarking Quantum Kernel Support Vector Machines Against Classical Baselines on Tabular Data: A Rigorous Empirical Study with Hardware Validation (2026, 2604.18837): "For n qubits, the feature space dimension grows exponentially, which may provide representational power beyond efficient classical simulation [Havl´ıˇcek et al., 2019]."
- Hybrid Quantum-Classical Machine Learning for Cybersecurity Threat Detection and Intrusion Prediction: a Systematic Review (2026, 10.1109/AIMLA67915.2026.11522502): "B. Quantum Kernels and Parameter-Shift Gradients et al. [13] show that a quantum feature map Φ : which a quantum circuit estimates and passes to a classical SVM. Liu et al. [14] prove that when this kernel resists effici"
- Circuit Harmonic Matrices: A Spectral Framework for Quantum Machine Learning (2026, 2604.04292): "However, after rerunning these with double precision and further masking out vanishing variances, the actual physical correlation structure is exposed leading the results seen in Subfigure (c) in Figures 4–6."
- Karana: A Post-Quantum Secure AI Surveillance System for Autonomous Multimodal Threat Detection (2025, 10.1109/IETACS68750.2025.11385607): "In line with prior work on variational quantum classifiers [18], [19], our experiments showed a modest recall improvement of 2–3% in spoofed RF detection compared to a classical SVM baseline, suggesting potential robustn"
- Quantum feature-map learning with reduced resource overhead (2025, 2510.03389): "The fixed-ansatz second-order Pauli-Z (or ZZ ) feature-map [4] is an established choice due to its difficulty to classically simulate [4]."

### qml-02: Quantum Convolutional Neural Networks

- Q-Capsule: A Localized Capsule-Based Quantum Neural Architecture for Barren Plateau Mitigation (2026, 2610.11261): "…the circuit itself: quantum convolutional networks achieve at worst polynomially vanishing gradients through hierarchical convolution and pooling [10, 36], tensor-network-inspired circuits obtain favorable gradient scal"
- Quantum Convolutional Neural Networks for Groundwater Heat Plume Prediction: A Surrogate Modeling Approach (2026, 2606.23411): "The over-all quantum circuit depth is kept relatively shallow and scales approximately logarithmically with the number of qubits, O (log n ), which helps mitigate issues such as vanishing gradients and decoherence on cur"
- Mitigating measurement-induced training instability in hybrid quantum neural networks for protein classification (2026, 2606.22551): "Whereas modifying architectures such as QCNNs [23, 24], tensor network inspired designs [25, 26], problem dependent ansätze [27], and quantum kernel based methods [28, 29] aim to maintain non vanishing gradients by contr"
- Adversarial Robustness of Partitioned Quantum Classifiers (2025, 2502.20403): "However, recent arguments suggest that circuit architectures such as tree tensor networks and quantum convolutional neural networks (QCNNs) (Cong et al., 2019) that are free of barren plateaus (Pesah et al., 2021; Miao a"
- Subspace preserving quantum convolutional neural network architectures (2024, 2409.18918): "…work [21] on classical simulation of one specific type of quantum CNNs (QCNN) has shown, using the LOWESA algorithm [22, 23], that the Cong et al [16] proposal of QCNN is effectively classically simulate-friendly by con"
- Computing exact moments of local random quantum circuits via tensor networks (2024, 2403.01706): "As we can see from both panels in Fig.8, all the correlations are initially stored in the causal cone of O , to then quickly get washed out and become localized to the ﬁrst few sites (QCNN) or completely vanish (HEA)."
- Dynamical transition in controllable quantum neural networks with large depth (2023, 2311.18144): "Inthe late time limit, omitting the t dependence in our notation, we can expand the shifts δθ ℓ around the extremum θ * to second order as where the ﬁ rst-order term vanishes due to convergence and the Hessian matrix M ("
- Tensor ring optimized quantum-enhanced tensor neural networks (2023, 2310.01515): "…and its quantum counterparts, namely, Variational Quantum Tensor Networks classifier (VQTN) [50], Quantum Convolutional Neural Networks (QCNN) [60], Tensor Ring parametrized Variational Quantum Circuit (TR-VQC) [56], an"

### qml-03: Quantum Recommendation Systems

- A Quantum-Inspired Dequantization Method for Diagonally Weighted Matrix Functions: Application to Learning with Optimized Random Features (2026, 2609.10729): "Beginning with Tang’s dequantiza-tion [13] of the quantum recommendation system [22], several quantum linear-algebra and QML algorithms have been shown to admit efficient classical simulations under suitable input-model "
- From Quantum Algorithm Primitives to Design Patterns: A Unified Framework for NISQ and Fault‐Tolerant Regimes (2026, 10.1002/qute.70310): "Kerenidis and Prakash [ 65 ] developed quantum recommendation systems via qsvt , though Tang’s dequantiza-tion [ 126 ] showed that classical algorithms can achieve similar polynomial speedups for this problem, significan"
- Grover Quantum Algorithm: Applications and Limits (2026, 10.3390/encyclopedia6040089): "Ewin Tang proposed a “dequantized” version of a quantum algorithm for recommendation systems [18], and the initial quantum version was a well-cited work originally proposed by Kerenidis and Prakash [19]."
- A Primer on Quantum Machine Learning (2025, 2511.15969): "…coexist with no-go theorems for worst-or average-case performance [59–61], separations between classical and quantum learners are known for contrived tasks [62–65], yet other purported advantages for practical problems "
- Dequantization and Hardness of Spectral Sum Estimation (2025, 2509.20183): "The story of dequantization results typically begins with Tang [Tan19] who discovered a classical polynomial-time algorithm for recommendation systems, which was believed to offer an exponential quantum advantage by the "
- Dequantizability from inputs (2024, 2405.13273): "Meanwhile, with respect to quantum access that was justified by the data structure of [1, 2], poly-nomially slower classical counterparts of QML algorithms were provided by sample-query access corresponding to the data s"
- Robust Dequantization of the Quantum Singular Value Transformation and Quantum Machine Learning Algorithms (2023, 2304.04932): "In particular, quantum algorithms [28] and their dequantization [36, 20] consider and solve the following version."
- Quantum Algorithms for Escaping from Saddle Points (2020, 2007.10253): "However, the algorithm has a few drawbacks: 1) The cost is expensive when r = Θ(n); 2) It relies on a quantum data structure [47] which can actually be dequantized to classical algorithms with comparable cost [17, 60, 61"

### qml-04: Quantum principal component analysis

- Entanglement Induced Barren Plateaus (2020, 2010.15968): "The QML ﬁeld has enjoyed increased attention for quantum algorithms for principal component analysis [1], support vector machines [2], kernel meth-ods [3, 4], and quantum neural networks (QNN) [3, 5–8] but experiences se"
- Sampling-based sublinear low-rank matrix arithmetic framework for dequantizing Quantum machine learning (2019, 1910.06151): "Our framework improves on Tang’s dequantization [44] of the quantum principal component analysis (qPCA) algorithm [33]."
- Quantum Principal Component Analysis Only Achieves an Exponential Speedup Because of Its State Preparation Assumptions. (2018, 1811.00414): "We now dequantize Lloyd, Mohseni, and Rebentrost’s quantum principal component analysis (QPCA) algorithm [12], an inﬂuential early example of QML [20, 21]."
- Quantum-inspired classical algorithms for principal component analysis and supervised clustering (2018, no id): "matched with ℓ2-norm sampling assumptions in the classical ML model. In this note, we follow this guideline to dequantize two quantum machine learning algorithms, quantum principal component analysis [6] and quantum supe"

### qml-05: Data re-uploading for a universal quantum classifier

- Quantum Encoding Strategies for Drug Response Prediction: An Exhaustive Benchmark on a 20-Qubit Superconducting QPU (2026, 10.64898/2026.07.08.737310): "Previous benchmarks comparing encoding strategies have relied either on classical simulators [6–8] or on demonstrations limited to two to four qubits [5, 13]."
- Practicality of training a quantum-classical machine in the noisy intermediate-scale quantum era (2025, 10.1016/j.isci.2025.113058): "27 Previous work validated QNN using this algorithm, 23 although optimal machine learnable parameters (MLP) were derived from training on a classical simulator due to the cost and accuracy limitations of training on NISQ"
- A hybrid quantum–classical neural network for learning transferable visual representation (2023, 10.1088/2058-9565/acf1c7): "Experimental results (see appendix C) show that these two methods achieve negligible accuracy improvement in an QCLIP model, which contradicts previous conclusions from QML models [82, 83] implemented purely by QuNNs."

### qml-06: Power of data in quantum machine learning

- Mitigating measurement-induced training instability in hybrid quantum neural networks for protein classification (2026, 2606.22551): "Whereas modifying architectures such as QCNNs [23, 24], tensor network inspired designs [25, 26], problem dependent ansätze [27], and quantum kernel based methods [28, 29] aim to maintain non vanishing gradients by contr"
- How Quantum Circuits Actually Learn: A Causal Identification of Genuine Quantum Contributions (2026, 2603.16321): "…classically simulable [10, 11], we cannot determine whether this reflects fundamental limitations of quantum computing or merely under-utilization of available quantum resources a distinction with profound implications "
- Markov chain decision-making with quantum-assisted entropy kernels (2026, 10.1007/s44464-026-00010-2): "Theory quantifies the trade-offs and shows that highly expressive circuits may yield exponentially vanishing kernel variance [26, 55], echoing barren-plateau phenomena [11, 36]."
- Machine Failure Detection Based on Projected Quantum Models (2026, 2601.15641): "By appropriately choosing the quantum circuit for U ( θ ) , computing projected quantum features can be neither classically simulatable nor learnable by classical machine learning models [11]."
- Prospects for quantum advantage in machine learning from the representability of functions (2025, 2512.15661): "Recent literature on classical surrogates delineates the boundaries of dequantization for these models [8, 10, 11, 14, 29, 30]."
- Credit Default Prediction with Projected Quantum Feature Models and Ensembles (2025, 2510.01129): "A quantum machine learning (QML) model implemented with a Heisenberg feature map tailored to the underlying structure of the task [41] generally exhibits computational complexity that precludes efficient classical simula"
- Quantum phase transition detection via quantum support vector machine (2024, 10.1088/2058-9565/ad985f): "…efficiency compared to the existing QSVM algorithms; concurrently, our approach promises a quantum computational edge in scenarios where the quantum feature map circuit defies classical simulation [36, 37], thereby deli"
- Quantum Sensing Technologies and Smart Cities: Opportunities and Challenges (2024, 10.1109/ISC260477.2024.11004264): "Even if the method of mapping the system in terms of the evolution of a state of qubits is not perfect, then quantum simulation may still be valuable by providing a better approximation to a classical simulation – potent"

### qml-07: A rigorous and robust quantum speed-up in supervised machine learning

- Optimal algorithmic complexity of inference in quantum kernel methods (2026, 2604.15214): "Our results are therefore most relevant for kernel functions whose values do not vanish asymptotically [LAT21, HBK + 25], which are precisely the settings where quantum kernel methods are expected to be useful."
- Hybrid Quantum-Classical Machine Learning for Cybersecurity Threat Detection and Intrusion Prediction: a Systematic Review (2026, 10.1109/AIMLA67915.2026.11522502): "B. Quantum Kernels and Parameter-Shift Gradients et al. [13] show that a quantum feature map Φ : which a quantum circuit estimates and passes to a classical SVM. Liu et al. [14] prove that when this kernel resists effici"
- A Primer on Quantum Machine Learning (2025, 2511.15969): "…coexist with no-go theorems for worst-or average-case performance [59–61], separations between classical and quantum learners are known for contrived tasks [62–65], yet other purported advantages for practical problems "
- On the relation between trainability and dequantization of variational quantum learning models (2024, 2406.07072): "[41] one sees that the DLP kernel is not affected by the vanishing similarity and has no BPs under the uniform distribution."
- Hype or Heuristic? Quantum Reinforcement Learning for Join Order Optimisation (2024, 2405.07770): "This finding appears to contradict claims for quantum advantage in QML literature [37], [38], [40]."
- Neural auto-designer for enhanced quantum kernels (2024, 2401.11098): "For the global measurements-induced vanishing similarity, one can employ problem-specific quantum kernel to remit it (Liu et al., 2021)."
- Quantum agents in the Gym: a variational quantum algorithm for deep Q-learning (2021, 2103.15084): "This is contrary to the widely believed conjecture that no efficient classical algorithm can solve the DLP, and [61] proves that no classical learner can do better than random guessing."
- Empirical Evidence of Quantum Kernel Concentration in Few-Shot Keyword Spotting (2026, 10.1109/ACCESS.2026.3698241): "Contrary to the theoretical prediction that larger training sets should improve quantum kernel performance [9], the QSVM accuracy at SPC = 30 (19.3"

### qml-08: Barren plateaus in quantum neural network training landscapes

- What a Reporting Convention Hides: A Matched-Budget Audit of Quantum Natural Gradient with an Exactly Computed Metric (2026, 2610.09425): "The global-cost family is prone to barren plateaus, in which the gradient variance vanishes exponentially with the number of qubits (McClean et al., 2018; Cerezo et al., 2021)."
- Reduced Cost Quantum Kernel Training (2026, 2610.04190): "However, this approach does not eliminate the computational cost associated with kernel evaluation and can introduce barren plateaus, a phenomenon in which gradients vanish exponentially as the size of the system increas"
- Evolving Hybrid Quantum-Classical Architectures for Image Classification (2026, 2610.03220): "Poor circuit design can also produce barren plateaus, where gradients vanish exponentially with qubit count McClean et al. (2018); Cerezo et al. (2021), stalling training and rendering even expressive circuits effectivel"
- Zero- Versus Infinite-Temperature Damping in Variational Quantum Circuits: Feature Scale, Sampling Cost, and Frame Gauge (2026, 2610.01466): "Gra-dients of deep random circuits, and of global cost functions even in shallow ones, vanish exponentially with the number of qubits [4–6]."
- Quantum single-image super resolution (2026, 10.1007/s11128-026-05357-0): "Variational Quantum Circuits (VQCs) can suffer from the Barren Plateau phenomenon, where gradients vanish as the circuit depth, Qubit count, or randomness of the ansatz increases [43]."
- Scaling law of variational quantum algorithms (2026, 2609.39949): "…unitary 2-designs, resulting in concentration of measure and exponentially vanishing gradient vari-ances—a phenomenon known as a barren plateau [5, 6], as a consequence of concentration of measure over an exponentially "
- A Width-Matched Comparison of Hybrid Quantum-Classical Self-Supervised Learning for Fingerprint Recognition (2026, 2609.39172): "QNet has high expressibility and therefore can be plateau-prone, as explained in [19,12]; however, QCNN architectures may avoid the exponential vanishing-gradient problem [22]; therefore, QuFex is structurally restricted"
- Adaptive Rotation for iSOMA: Geometry, Benchmarking, and Noise Robustness in Variational Quantum Objectives (2026, 2609.37193): "VQA landscapes can exhibit vanishing-gradient regions, and gradient-free optimization does not in general evade the associated loss of resolvable cost differences [23, 24]."

### qc-01: Quantum supremacy using a programmable superconducting processor

- CT-bMPS: Approximate Tensor Network Contraction with Boundary MPS on Contraction Trees (2026, 2610.06574): "This approach is one of the leading methods for classically simulating random circuit sampling [15, 19] and is widely used to establish classical baselines for quantum computational advantage experiments [20, 21]."
- Experimentally Testable Quantum Advantage in Shallow Circuits (2026, 2609.38775): "Random-circuit sampling and photonic sampling experiments compare a quantum processor with the strongest available classical simulation methods [1–4]; their complexity-theoretic foundations and verification issues are re"
- On Certifying Source Sampling Hardness in Quantum Generative Modeling (2026, 2609.28802): "Prominent examples arise from quantum circuit families related to random circuit sampling [8–14], instantaneous quantum polynomial-time (IQP) circuits [15–19], and other sampling problems for which efficient classical si"
- Distinguishability Transitions from Global Quantum Snapshots (2026, 2609.09296): "The XEB is also notably used in the context of RCS benchmarking and fidelity estimation [14, 15, 37, 38]; however, its use in benchmarking has come under scrutiny in recent years due to its vulnerability to classical spo"
- How Far Can You Do Nothing On a Quantum Computer? (2026, 2608.21904): "Notable milestones include the first claims of quantum supremacy via random-circuit sampling [1] and the demonstration of quantum utility beyond brute-force classical simulation using error-mitigated superconducting circ"
- Realified tensor networks: quantum circuit simulation on real-valued matrix accelerators (2026, 2608.03987): "Tensor-network contraction simulates quantum circuits at scale, from single-amplitude evaluation [1, 2] to the verification [2, 3] and spoofing [4] of random-circuit-sampling experiments [5]."
- Stochastic Pauli-path simulator for large-scale quantum optimization (2026, 2607.17804): "Over the years, continued progress in classical simulation has not only provided practical platforms [5–10] for the design and development of quantum algorithms in the absence of large-scale quantum machines, but also im"
- Variance-Reduced Trajectory Unravelings for GPU Noisy Quantum-Circuit Simulation: Characterization and a Qiskit-Aer Integration Gap (2026, 2607.17678): "It serves, second, as a control experiment for quantum-advantage claims : classical simulation is the yardstick against which hardware results are judged, and several “advan-tage” claims have been narrowed or overturned "

### qc-02: Evidence for the utility of quantum computing before fault tolerance

- CT-bMPS: Approximate Tensor Network Contraction with Boundary MPS on Contraction Trees (2026, 2610.06574): "The original study used MPS and isometric tensor network states (isoTNS) for classical simulations [35]."
- How Far Can You Do Nothing On a Quantum Computer? (2026, 2608.21904): "Notable milestones include the first claims of quantum supremacy via random-circuit sampling [1] and the demonstration of quantum utility beyond brute-force classical simulation using error-mitigated superconducting circ"
- Quantum Error Management in Practice: A Cross-Stack Benchmark (2026, 2608.05202): "Mitigation techniques of this kind were essential to IBM’s demonstration that a 127-qubit processor can compute accurate expectation values beyond brute-force classical simulation [19], and they are reviewed comprehensiv"
- Image Classification on IBM Quantum Computers (2026, 2607.17705): "…real-device executions on architectures like the 127-qubit IBM Eagle processor have provided concrete evidence for quantum utility by outperforming brute-force classical simulation methods in tracking the time dynamics "
- Tuning Quantum MPS (2026, 2606.23262): "Classical simulation remains a fundamental tool for quantum computing, as current quantum hardware is still constrained by noise and limited scalability [1]."
- Computing noise-canceling observables via Pauli propagation (2026, 2606.20441): "On the quantum side, advances in hardware and error mitigation have enabled accurate observable estimation at scales beyond brute-force classical simulation [7]."
- Basis-Adaptive Sparse-State Simulation of Quantum Circuits (2026, 2605.27285): "The classical simulation boundary—where existing meth-ods stop matching circuit outputs—is central to reading quantum-advantage experiments [8, 10, 50]."
- EFaaS: A Quantum-Classical Serverless Entangled Scheduler for Hybrid Variational Algorithms (2026, 2605.27540): "Q UANTUM computing has crossed the threshold into the “Utility Era,” a phase where quantum hardware can execute complex circuits beyond the reach of brute-force classical simulation [1], [2]."

### qc-03: Quantum computational advantage using photons

- When Does Interference Help Learning? Kernel Geometry as a Pre-Experimental Test for Photonic Reservoir Computing (2026, 2610.11360): "For large-scale systems ( N ≥ 50 ) [47, 48], the cannot be evaluated classically; it guides the decision up to the classically simulable frontier, and beyond this limit, predicting utility relies on extrapolating alignme"
- Local Anticoncentration for Gaussian Boson Sampling via Conditional Wishart Geometry (2026, 2610.00112): "The optical setting is motivated by photonic implementations [12–14], while classical simulation and realistic error models remain separate benchmarks [15, 16]."
- Quantum Computing Applications in Engineering: Current Status and Future Prospects (2026, 10.1007/s11831-026-10569-9): "For Gaussian Boson sampling [ 4] reported a 10 14 × fold speedup (76–113 qubits, photonic Jiuzhang) com - pared to classical simulation (0.6 billion years)."
- Gaussian boson sampling with 1,024 squeezed states in 8,176 modes (2026, 10.1038/s41586-026-10523-6): "Previous GBS experiments detected 76, 113, 219 and 255 photon events 7–10 , with outcomes validated against contemporary classical spoofing algorithms 20–24 ."
- Wigner Distribution Sets Universal Lower Bound for Quantum Advantage in Gaussian Boson Sampling (2026, 10.3390/e28020188): "Variation in squeezing across modes reveals some interesting effects, such as the Jensen effect described in Section 3.5, but does not significantly affect complexity and accuracy of the Wigner lower bound (7), as is see"
- FastMPS: Revisit Data Parallel in Large-scale Matrix Product State Sampling (2025, 2512.20064): "In the design of quantum-computing hardware, MPS sampling underpins classical simulation of photonic quantum computing experiments, including Gaussian Boson Sampling (GBS) [5, 16, 17, 30, 31]."
- Sufficient conditions for hardness of lossy Gaussian boson sampling (2025, 2511.07853): "In particular, establishing hardness result under photon loss is especially crucial, since it is a leading cause of error in current GBS experiments [6–10], and also a key ingredient enabling eﬃcient classical simulation"
- Complexity and hardness of random peaked circuits (2025, 2510.00132): "…including random circuit sampling with superconducting and trapped-ion processors and Gaussian boson sampling with photonic devices [AAB + 19,ZWD + 20,MLA + 22,DQW + 23,LSN + 25], while concurrent advances in classical "

### qc-04: Beyond-classical computation in quantum simulation

- Q‐LEAP: Millisecond Hyperdimensional Optimization for Full‐Spectrum Optical Metamaterials (2026, 10.1002/advs.78032): "King et al. [ 25 ] showed that a quantum annealer can outperform classical simulations of quantum spin glasses, matching its accuracy on the largest problems would take classical matrix product state methods millions of "
- Towards Datalog on Quantum Annealers: Compiling Recursive Logic Programs with Bottom-up Semantics to 2-local Ising Models (2026, 2608.04645): "Whole-chip topologies are the substrate of D-Wave’s beyond-classical simulations [30], and a topology is itself a graph, so it hosts a natural program: reach of Table 3, single-source reachability over the chip’s own gra"
- Quantum-to-Classical Computability Transition via Negative Markov Chains (2026, 2604.19889): "This question is directly relevant to experimental claims of quantum advantage [7–15], many of which have subsequently been challenged by increasingly powerful classical simulation methods [16–28]."
- Molecular Design beyond Training Data with Novel Extended Objective Functionals of Generative AI Models Driven by Quantum Annealing Computer (2026, 2602.15451): "Recent experiments have demonstrated that quantum annealing achieves a scaling advantage in approaching low-energy configurations [15, 16], while the resulting sampling distributions cannot be efficiently reproduced by a"
- Classically Sampling Noisy Quantum Circuits in Quasi-Polynomial Time under Approximate Markovianity (2025, 2510.06324): "Several experimental works have attempted to demonstrate quantum advantage on near-term hardware [5–13]; however, subsequent studies have challenged these claims by developing classical simulation algorithms that can eff"
- Quenched Quantum Feature Maps (2025, 2508.20975): "Here, we bridge the developments in quantum ML and quantum supremacy by transforming the result of a beyond-classical simulation on D-Wave quantum annealing processors [8, 17, 18] into an empirical quantum advantage for "
- Roadblocks and Opportunities in Quantum Algorithms -- Insights from the National Quantum Initiative Joint Algorithms Workshop, May 20--22, 2024 (2025, 2508.13973): "The continuous-time dynamics of two-dimensional Ising models was recently simulated using a quantum annealer [153, 154], and similarly challenged by classical simulation [155–158]."
- Solving excited states for long-range interacting trapped ions with neural networks (2025, 2506.08594): "Combined with a transverse field − P ix which can be realized by a global laser or microwave, the eigenstates and dynamics of the system are challenging for classical simulation [10, 13]."

### qc-05: What is the Computational Value of Finite Range Tunneling?

- Quantum annealing with chaotic driver Hamiltonians (2024, 2409.20538): "The intuition for the enhanced performance is that quantum fluctuations allow for tunneling events through particularly spiky peaks of the energy landscape [12], which in contrast are not possible when using classical si"
- On the emerging potential of quantum annealing hardware for combinatorial optimization (2022, 2210.04291): "Acknowledging these anticipated hardware improvements, as well as the empirical findings of this study, revisiting the topic of demonstrating a QA scaling advantage (as in [19, 2]) is a natural next step to establish a s"
- A Quantum Annealing Approach to Reduce Covid-19 Spread on College Campuses (2021, 2112.01220): "This research has shown proven quantum speedups for a specific graph optimization problem [25], as well as evidence of a scaling advantage of QA over classical simulated annealing for specific classes of more general pro"
- Simulated versus reduced noise quantum annealing in maximum independent set solution to wireless network scheduling (2018, 10.1007/s11128-018-2117-1): "Interestingly, in late 2015, Google announced a result [14] claiming a 108 speedup on D-Wave 2X compared to classical simulated annealing and simulated quantum annealing based on carefully crafted “artificial problems."
- Inhomogeneous driving in quantum annealers can result in orders-of-magnitude improvements in performance (2018, 1806.11091): "This problem class is interesting because it was designed to benefit from a computational strength of quantum annealing (multi-spin cotunneling [7, 29]), while simultaneously being difficult for classical simulated annea"
- High Performance Computing for Geospatial Applications (2020, 10.1007/978-3-030-47998-5): "the quantum mechanical phenomenon where a particle tunnels through an energy barrier that it classically could not surmount), quantum annealing can explore rugged energy landscape more efficiently than classical methods,"
- Quantum Monte Carlo for Quantum-dot Cellular Automata (2016, no id): "Further, QMC generally exhibits better scaling with problem size and finds lower energy states than classical simulated annealing [1][2]."

### qc-06: Quantum algorithm for solving linear systems of equations

- Accelerating Inference for Multilayer Neural Networks with Quantum Computers (2025, 2510.07195): "However, these algorithms face trainability issues in the form of poor local minima (Bittel & Kliesch, 2021; Anschuetz & Kiani, 2022) and vanishing gradients, or barren plateaus (McClean et al., 2018; Larocca et al., 202"
- Sublinear-Time Algorithms for Diagonally Dominant Systems and Applications to the Friedkin-Johnsen Model (2025, 2509.13112): "Their algorithms are inspired by the HHL quantum algorithm [17] for solving linear systems and the breakthrough by Tang [33] of dequantizing the quantum algorithm for recommendation systems."
- Building intuition for quantum algorithms using the Aharonov–Bohm effect (2025, 2509.11893): "To do so we consider how hard it is classically to simulate the quantum system that makes up the quantum computer: if it was easy to classically simulate the quantum system that makes up the quantum computer, it would no"

### phys-01: Quantized Majorana conductance

- Hunting for Majoranas (2023, 2306.12473): "One report of its observation ( 83 ) was subsequently retracted ( 84 , 85 ); a second study exhibited scaling of the peak conductance that was interpreted as consis-tentwithquantization( 86 )."
- Variational Quantum Circuits for Machine Learning. An Application for the Detection of Weak Signals (2021, 10.3390/APP11146427): "While a study partly funded by Microsoft claimed to have detected Majorana fermions [20], its authors themselves retracted the claim."

### phys-03: Solving the Quantum Many-Body Problem with Artificial Neural Networks

- Vast world of quantum advantage (2026, 10.1103/tn89-g1xz): "Sophisticated tensor network algorithms [65], machine learning approaches [78], and quantum-inspired classical methods [79] continue to push the boundaries of classical simulation."
- When can classical neural networks represent quantum states? (2024, 2410.23152): "Recent works have shown that similar architectures can also be employed to classically simulate the properties of many-body quantum systems [17, 22, 34, 50, 51, 58], or learn a classical representation of a quantum state"
- Measuring Renyi Entropy in Neural Network Quantum States (2023, 2308.05513): "According to the structure of RBM, we can write down the expression of NQS with the neural network parameters W = { a, b, w } [4], The dynamics we considered is an evolution from an initial ground state with strong trans"

### ml-01: Neural Collaborative Filtering

- Learning Recommendation under an Identical-Pool Protocol: Top-K Ranking on Skill Graphs with Fair, Reproducible Evaluation (2025, 10.1109/BigData66926.2025.11401663): "Across collaborative, sequential, graph, self-supervised, and content paradigms [3], [5]–[9], [11], [14], [20], [21], [24], [25], prior research offers strong baselines and methodologies."
- Vetta: Adaptive Job-Talent Matching (2025, 10.1109/AIxSET65682.2025.00010): "Vetta is benchmarked on over 40,000 candidate profiles and 7,500 gigs with real hiring outcomes, and compared against strong baselines including LinkSAGE [12], NCF [14], and Adapted-APJFNN [3]."

### ml-02: TabNet: Attentive Interpretable Tabular Learning

- Multi-Class, Multi-Tier Network Intrusion Detection: A Comprehensive and Reproducible Benchmark (2026, 2609.36039): "Gradient-boosted trees are strong baselines for heterogeneous numerical tables [10], while neural tabular models such as TabNet [8] offer learned feature selection but can be sensitive to imbalance and limited class supp"
- Gaussian Mixture Model Target Labeling for Student Interest-Talent Alignment Classification (2026, 10.1109/IES71033.2026.11702699): "Given the tabular nature of ABM scores and the moderate dataset size, ensemble ML methods are commonly strong baselines, while deep tabular architectures may achieve competitive results but often require careful regulari"
- SEAF-FL-MLP: Audited Federated Edge-AI Anomaly Detection with Client Heterogeneity and Shortcut-Sensitivity Analysis (2026, 10.59628/jast.v4i7.3475): "TabNet introduced attentive interpretable tabular learning [18], and broader tabular deep-learning benchmarking shows that simple baselines and gradient-boosted models can remain highly competitive on tabular tasks [19]."
- A Two-Stage Ensemble Framework for Repurchase Prediction Integrating Sequence Modeling and Multi-Granularity Features (2026, 10.1109/ISoIRS70157.2026.11545311): "To comprehensively evaluate the competitiveness of the proposed framework, we benchmarked it against AutoGluon [18] (representing automated hyperparameter tuning), TabNet [15] (state-of-the-art deep tabular learning), an"
- Tri-Objective Self-Supervised Representation Learning for High-Dimensional Tabular Data (2025, 10.1109/PuneCon67554.2025.11379090): "…datasets (Adult, Breast Cancer, Covertype) and compare against strong baselines, including tree-based ensembles (XGBoost[1], CatBoost[2]), supervised MLPs, and recent SSL approaches (VIME[3], SCARF[4], SubTab, SAINT[6],"

### ml-03: Batch Normalization: Accelerating Deep Network Training by Reducing Internal Covariate Shift

- Machine-Learning-Based Regional Nowcasting Method for HF Maximum Usable Frequency Driven by Ionospheric Total Electron Content: A Case Study of North China (2026, 10.1109/TAP.2026.3717336): "Each Conv1D layer has a kernel size of 3 × 1 and a stride of 1, followed by batch normalization to stabilize training and mitigate exploding or vanishing gradients [46]."
- A Hybrid CNN–BiLSTM Framework for Intelligent Animal Detection with Simulated IoT Alert Generation (2026, 10.1109/ICESC70182.2026.11687205): "This normalization stops gradient vanishing caused by heterogeneous sensor scales and expedites convergence [4]."
- Physics-Informed Neural Networks for the High-Resolution Reconstruction of Flow Measurement Indicators in Fluid Dynamics (2026, 2607.11576): "In order to address the problem of vanishing and exploding gradients during training, we use batch-normalization before each layer [48, 49]."
- AutoNorm: Understanding Adaptive Normalization in Transformers through Differentiable Gating (2026, 2607.10593): "Normalization is fundamental to training deep neural networks, mitigating vanishing and exploding gradients and internal covariate shift [1], [2], [13], [14]."
- ViDeCerviNet: a hybrid vision transformer–DenseNet framework for superior accuracy in cervical cancer diagnosis and categorisation (2026, 10.1007/s11042-026-21737-1): "…with its residual learning framework to resolve the vanishing gradient problem; VGG [51 ] noted for its simple yet deep architecture; Inception [52] and InceptionResNet [ 53] that capture multi-scale features via parall"
- On the Benefits of Water Consumption and Reactive Power for Eventless NILM (2026, 10.1145/3765611.3815510): "The latter finding contradicts the claims of the publication introducing batch normalization [12], which argues that dropout negatively impacts model performance when employing batch normalization."
- PPIGAN: Prediction of Protein–Protein Interactions Using Generative Adversarial Networks (2026, 10.1177/15578666261453608): "Encoding block: 10 layers of convolution are used for down-sampling, and a batch normalization layer (Ioffe and Szegedy, 2015) is introduced in order to alleviate the gradient vanishing and accelerate the network converg"
- SparseOpt: Addressing Normalization-induced Gradient Skew in Sparse Training (2026, 2605.27541): "…architecture allows DNNs to learn complex and expressive features, it simultaneously introduces optimization challenges such as vanishing or exploding gradients, which make training deep networks difficult as network de"

### ml-04: How Powerful are Graph Neural Networks?

- Conformer-covariance diagnostics for aqueous solubility (2026, 10.1007/s10822-026-00943-x): "Message passing neural networks (MPNNs) [19] and directed variants [11] are strong baselines, but standard neighborhood aggregation is limited by the 1-dimensional Weisfeiler–Leman (1-WL) test [20, 21 ]."
- StARS: Socially Appropriate Robot Actions via a Recommender System-Driven Approach (2026, 2607.21802): "…[26], which performs neighborhood aggregation with graph-convolutional smoothing and provides a strong baseline for relational scene encoding; GIN [56], which uses sum aggregation and MLP updates and is known for strong"
- A Topological Characterization of Graph Neural Networks via Stochastic Block Model Embeddings on the n-Sphere (2026, 2606.07598): "The expressive power of MPNNs is bounded above by the Weisfeiler–Lehman colour-refinement hierarchy (Xu et al., 2019a; Maron et al., 2019), a fact we will revisit when we discuss limitations of the spherical fingerprint "

### ml-05: Multi-Similarity Loss with General Pair Weighting for Deep Metric Learning

- Are All Tokens Necessary for Visual Place Recognition? An Empirical Study of Token Reduction for Efficient Inference (2026, 2607.15563): "We train these models on the merged dataset proposed by SelaVPR++ [10] with the multi-similarity loss [68], obtaining strong baselines representative of modern advanced transformer-based VPR systems."
- Deep Metric Learning With Adaptively Composite Dynamic Constraints (2023, 10.1109/TPAMI.2023.3234536): "To better evaluate the effectiveness of the proposed approach, we conduct experiments under both the conventional deep metric learning setting [69], [84], [104] and the recent Metric Learning Reality Check (MLRC) setting"
- Informative Sample-Aware Proxy for Deep Metric Learning (2022, 2211.10382): "In this section, we first revisit the GPW framework [36] to provide a unified view of DML loss functions, and qualitatively discuss the impact and problems of hard samples on the learning of the proxies."
- Ranked List Loss for Deep Metric Learning (2021, 10.1109/TPAMI.2021.3068449): "Therefore, following the concurrent work Multi-Simi [68], and the following work SoftTriple [42] and Reality Check [38], we freeze the BatchNorm layers during training to fairly compare with their reported results on CUB"
- Pretraining Neural Architecture Search Controllers with Locality-based Self-Supervised Learning (2021, 2103.08157): "As Le pulls all the positive samples closely, decoder gets confused, hence influencing Lr.
Comparison between metric learning methods We compare MarginLoss [48], AngularLoss [43], NPairsLoss [36], MultiSimilarityLoss [44"
- Metric learning: cross-entropy vs. pairwise losses (2020, no id): "…from that, we use the common random sampling among all samples (as in most classiﬁcation training schemes) and set the mini-batch size to 128 in all experiments (contrary to [33] in which the authors use a mini-batch si"
- A Unifying Mutual Information View of Metric Learning: Cross-Entropy vs. Pairwise Losses (2020, 2003.08983): "Deviating from that, we use the common random sampling among all samples (as in most classification training schemes) and set the mini-batch size to 128 in all experiments (contrary to [40] in which the authors use a min"
- Ranked List Loss for Deep Metric Learning (2019, 1903.03238): "Therefore, following the concurrent work Multi-Simi [67], and the following work SoftTriple [41] and Reality Check [37], we freeze the BatchNorm layers during training to fairly compare with their reported results on CUB"

### ml-06: Improved Training of Wasserstein GANs

- Research on the application of deep learning in bridge health monitoring data analysis and anomaly diagnosis (2026, 10.1007/s44163-026-02173-4): "Mao et al. [45] proposed LSGAN to alleviate gradient vanishing, and Arjovsky et al. [46] proposed WGAN using Wasserstein distance to stabilize training."
- Deep Learning-Based Molecular Generation for Lung Cancer Therapeutics (2026, 10.3390/ddc5030048): "The conventional GAN loss (cross-entropy) results in gradient vanishing when the discriminator exhibits excessive confidence, but the Wasserstein loss provides significant gradients even when samples deviate from real da"
- Data Augmentation Method Based on Improved GAN for Underwater Acoustic Signals (2026, 10.1109/CCSB71176.2026.11716359): "…network architectures: WGAN-GP employs Wasserstein distance and gradient penalty to mitigate gradient vanishing and enhance training stability [11]; Conditional GAN (CGAN) integrates label information to enable controll"
- Generative Radio Map-Assisted Channel Estimation in Low-Altitude Economy (2026, 10.1109/TMC.2026.3665545): "Toavoid gradient vanishing in classical GANs, Wasserstein GAN (WGAN) [45] with gradient penalty (WGAN-GP) [46] is adopted in the proposed CVCGAN."
- A Systematic Review on Synthetic Medical Images Generation—Recent Trends and Future Opportunities (2026, 10.3390/diagnostics16142166): "In order to prevent vanishing gradient, researchers have designed various methods, including loss function, gradient penalty, and normalization techniques [47,103,104]."
- Generative Modeling of Bach-Style Symbolic Music: A Comparative Study of Autoregressive, Latent-Variable, and Adversarial Approaches (2026, 2606.13626): "We tried using the default GAN minimax loss, which had a tendency to train the discriminator faster than the generator as well as vanishing gradients, so we instead ended up using the Wasserstein GAN Arjovsky et al. [201"
- Theoretical Foundations and Effective Algorithms for Policy-Aware Simulator Learning (2026, 2605.29032): "Furthermore, standard divergences like KL or TV often suffer from vanishing gradients when the support of the learned model ̂ P and true dynamics P are disjoint [Arjovsky et al., 2017]."
- Imbalanced fault diagnosis with diffusion-based augmentation and dual-stage quality gating (2026, 10.1088/1361-6501/ae6f3e): "The deep convolutional GAN (DCGAN) uses convolutional architectures to preserve local structural consistency in spectrograms [17–19], while the Wasserstein GAN with gradient penalty (WGAN-GP) employs the Wasserstein dist"

### ml-07: Neural Architecture Search with Reinforcement Learning

- A Novel Parameter Initialization Mechanism Based on Model Structure Graph Conditional Diffusion (2026, 10.1109/ICCET70051.2026.11659021): "…initialization decoupled from structure often causes early-stage gradient oscillation[9], slow convergence[10],or even vanishing exploding gradients[11], especially in scenarios with unknown or dynamic model structures "

### ml-08: Deep Residual Learning for Image Recognition

- Panorama: Unveiling Latent Dependencies for Microservice Autoscaling via Meta-learning (2026, 10.1145/3832783.3837485): "To mitigate vanishing gradients and enhance training stability, residual connections [18] are integrated with layer normalization around both sub-layers."
- A Benchmark for Cultural-Heritage Deterioration Segmentation: Semi-Supervised Baselines, Auto-Discovery, and Calibration-Aware Evaluation (2026, 10.1145/3850157): "Convolutional models remain strong baselines, while Transformer encoders offer broader context for heterogeneous damage patterns [8, 20, 40, 53, 61]."
- ANALISIS KOMPARATIF KINERJA RESNET-50, EFFICIENTNET-B0, DAN MOBILENETV3-LARGE DALAM KLASIFIKASI KERUSAKAN DINDING BANGUNAN BERBASIS CITRA DIGITAL (2026, 10.36040/jati.v10i5.19247): "Jalur ini mengalirkan gradien langsung ke lapisan awal saat backpropagation , secara efektif mengatasi masalah vanishing gradient pada jaringan dalam [9]"
- PERBANDINGAN PERFORMA RESNET-18, EFFICIENTNET-B0, DAN ENSEMBLE LEARNING DENGAN VISUALISASI GRAD-CAM PADA DETEKSI KATARAK (2026, 10.36040/jati.v10i5.19300): "Pada jaringan konvensional, penambahan lapisan yang lebih dalam seringkali tidak meningkatkan akurasi, bahkan dapat menurunkan performa akibat terjadinya masalah vanishing gradient dan overfitting [13]."
- FlexVNE: A LLM-Powered Flexible Framework for Virtual Network Embedding in Cloud-Network Convergence (2026, 10.1109/TMC.2026.3700558): "…connection to preserve the original topological information: The residual connection, a well-established technique in deep feature learning [35], [36], [37], alleviates gradient vanishing during training while preservin"
- A Novel Neural Architecture With Multilevel Feature Extraction Coordinated by Dendritic Classifier (2026, 10.1109/TSMC.2026.3703975): "ResNet [5] addresses the issues of vanishing and exploding gradients caused by increasing model depth."
- An Improved Wafer-View GDBN Method Using MetaFormer Variant (2026, 10.1109/TCAD.2026.3656320): "Residual connection [30] and group normalization [31] were applied before the last two modules, addressing the vanishing gradient problem and enhancing the model’s convergence stability, respectively."
- Development of a risk assessment tool for early detection of glaucoma based on machine learning methods (2026, 10.11591/eei.v15i5.11682): "Residual neural network architectures have been widely adopted in medical image analysis because their skip connections enable stable optimization of deep models and alleviate vanishing-gradient problems [6]."
