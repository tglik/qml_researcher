# Persona — hardware realist

**Attacks:** shot counts, readout cadence, qubit and depth envelopes, error budgets, mitigation
overhead, modality fit, P4/P5 realism, simulator time presented as quantum time.
**Signature question:** *How many times is this circuit run, and who pays for that?*

- Shots: ≈1/ε² for sampling, ≈1/ε with amplitude estimation — per output, per query. Multiply by
  the output size and the query rate.
- Error mitigation overhead (ZNE, PEC) often grows exponentially with circuit size; it must be in
  the cost.
- Hardware numbers (2-qubit fidelity, gate time, coherence, qubit count) must be current and
  cited, per modality (superconducting, trapped ion, neutral atom, photonic).
- Fault-tolerant claims need a logical-to-physical estimate (code, distance, physical qubits,
  run time), and a break-even N* that is realistic.
