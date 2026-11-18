# Scorer — <thread>

The frozen code that turns each phase's raw outputs into gate numbers. Signed at CP2 with the
spec, hashed into `PREREG.lock.json`, run by `python -m lab.tools.gates`. The implementer never
edits it and never reads `heldout/`.

| Gate (lock id) | Phase | Reads (raw file · columns) | Held-out file | Computes |
|---|---|---|---|---|
| P1.G4.threshold | P1 | `P1_toy/raw/classical_preds.csv` · `y_hat`; `P1_toy/raw/proposed_preds.csv` · `y_hat` | `heldout/test_labels.csv` · `y` | classical MAE minus proposed MAE |

**Raw format the implementer must produce:** one row per test instance, in the order of
`heldout/test_labels.csv` (row order is fixed by `splits.json`).

**Tested before CP2 on:** a synthetic pass case and a synthetic fail case per gate (describe them).
