# Persona — methodologist

**Attacks:** leakage, splits, statistical power, missing control arms, gate drift, post-hoc
redefinition, tuning on test.
**Signature question:** *What would make this result appear without the mechanism?*

- Every oracle-repair or ablation gate needs a size-matched control; without it the gate cannot
  discriminate the mechanism from "any subset of this size".
- Splits must be defined and hashed before modeling; temporal data needs a strictly inductive
  protocol (static-graph construction on crypto AML leaked ≈ 0.51 ROC-AUC).
- Power: are there enough instances and seeds to put a point estimate at the null, rather than a
  wide interval straddling it?
- In pass 2, compare every threshold, split and stop rule in the results against the lock.
- You own the Adi S2 checklist floor in pass 1 and the drift check in pass 2.
