# Hardware roadmaps

Reference for the hardware realist, the algorithm analyst (break-even N*) and P5 hardware plans.
Every number needs a source and a date. An entry older than six months is stale: refresh it
(`/qml-deep-research`, scoped to that vendor) before using it to rate hardware fit.

**Status: skeleton — not yet filled.** Do not rate hardware fit from memory; until a row is filled
and sourced, mark hardware numbers [UNVERIFIED].

## Current devices and roadmap (2027 onward)
| Vendor | Modality | Qubits (physical / logical) | 2-qubit fidelity | Gate time | Coherence | Roadmap milestones 2027+ | Source · date |
|---|---|---|---|---|---|---|---|
| IBM | superconducting | | | | | | |
| Google Quantum AI | superconducting | | | | | | |
| Rigetti | superconducting | | | | | | |
| Quantinuum | trapped ion | | | | | | |
| IonQ | trapped ion | | | | | | |
| Quantum Art | trapped ion | | | | | | |
| QuEra | neutral atom | | | | | | |
| Pasqal | neutral atom | | | | | | |
| Atom Computing | neutral atom | | | | | | |
| Infleqtion | neutral atom | | | | | | |
| Q-Factor | neutral atom | | | | | | |
| PsiQuantum | photonic | | | | | | |
| Xanadu | photonic | | | | | | |

## Capabilities an algorithm can exploit
| Modality | Native capabilities | Typical constraints |
|---|---|---|
| Neutral atom | Reconfigurable connectivity (atom shuttling), high parallelism, native Rydberg blockade for graph problems (MIS), large arrays | Slower gate and shuttle times, atom loss, mid-circuit measurement maturity varies by vendor |
| Trapped ion | All-to-all connectivity, high gate fidelity, long coherence | Slow gates, limited qubit counts per trap |
| Superconducting | Fast gates, mid-circuit measurement and feedforward, mature tooling | Nearest-neighbor connectivity, shorter coherence |
| Photonic | Room-temperature operation, natural fit for measurement-based architectures | Probabilistic gates, photon loss |

Vendor-specific capabilities (and whether they are available now or on the roadmap) go in the
first table's milestones column.
