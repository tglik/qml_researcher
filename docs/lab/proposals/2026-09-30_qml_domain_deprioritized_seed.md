# Proposal — seed `qml_domain.md` *Deprioritized Directions* from the exclusion ledger

**Status:** proposed, not applied (criteria changes are human commits — C12 I6).
**Source:** the 10 `final` entries seeded into `qml_artifacts/indexes/exclusion-ledger.md` on 2026-09-30.
**Reviewer:** Adi or Meir. Accept, trim, or reject line by line; then paste the accepted lines into
`criteria/qml_domain.md` → *Deprioritized Directions (Do Not Re-Suggest Without New Evidence)*.

Proposed lines (each links its ledger entry, so paper review can cite the evidence):

- Polylog-Pauli synthetic graph Hamiltonian as a recommendation ranking/re-ranking component — wrong classical target (linear term dominates) (`polylog-pauli-recsys-ranking-wrong-target`)
- Polylog-Pauli operator or its block partition as the candidate-retrieval stage at matched bytes (`polylog-pauli-candidate-retrieval`)
- Estimating a real graph's spectral gap from an operator fit to low-order spectral moments (`polylog-pauli-moment-fit-global-spectral-properties`)
- Fitted polylog-Pauli parameters as graph-classification descriptors (`polylog-pauli-graph-encoder-fingerprints`)
- Szegedy-walk acceleration of MCMC on fast-mixing QUBO landscapes (`szegedy-walk-qubo-mcmc-mixing`)
- Quantum optimization of the per-node split step in gradient-boosted trees (`quantum-split-optimization-gradient-boosting`)
- Exact (quantum) QBoost weak-learner subset selection for accuracy at matched size (`qboost-weak-learner-subset-selection`)
- Non-stoquastic / magnetic graph operators on stored transaction graphs as a quantum fraud route (`nonstoquastic-graph-operators-fraud-detection`)
- QAE for rare-event tail probabilities benchmarked only against crude Monte Carlo (`qae-rare-event-probability-aml-validation`)
- Quantum methods in per-event fraud scoring layers under millisecond caps (`quantum-fraud-scoring-per-event-layers`)

Not proposed (provisional entries — they block quantum spend but should not stop the literature
skills from surfacing counter-evidence): `polylog-pauli-recsys-serving-classical-twin`,
`polylog-pauli-offline-index-seeding`.
