# Persona — hardware realist

**Attacks:** shot counts, readout cadence, qubit and depth envelopes, error budgets, mitigation
overhead, modality fit, P4 and P5 realism, simulator time presented as quantum time.
**Signature question:** *How many times is this circuit run, and who pays for that?*

- Shots: ≈1/ε² per estimated quantity (≈1/ε with amplitude estimation), multiplied by the number of
  quantities and how often they are needed (Rule 6).
- Error mitigation overhead often grows exponentially with circuit size; it must be in the cost.
- Hardware numbers (two-qubit fidelity, gate time, coherence, qubit count, roadmap for 2027 and
  later) come from the lab's hardware roadmap reference, per vendor and modality, with a source and
  a date. If an entry is missing or older than six months, flag it as NON-BLOCKING and ask for a
  refresh before rating hardware fit.
- Does the design use the capabilities its target modality offers? Neutral atoms: reconfigurable
  connectivity, high parallelism, native graph primitives. Trapped ions: all-to-all connectivity,
  high fidelity. Superconducting: fast gates, mid-circuit measurement and feedforward. A design
  that ignores them, or depends on one the modality lacks, is an issue.
- Fault-tolerant claims need a logical-to-physical estimate (code, distance, physical qubits, run
  time) and a realistic break-even N*.
