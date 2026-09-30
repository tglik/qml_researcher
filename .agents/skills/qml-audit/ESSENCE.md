# /qml-audit — essence

## What this skill is for
Independent verification: does the verdict follow from correct experiments and correct
analysis — and is a negative strong enough to prune everyone's search space? Only a confirmed
audit makes a NO-GO binding.

## The judgment calls it makes
- **Did anything move?** Mechanically: thresholds, splits, stop rules against the lock; amendment
  dates against the data.
- **Do the numbers reproduce?** Recomputed from raw artifacts with independent code; a subset
  rerun from stored code, environment and seeds.
- **Could something other than the mechanism produce this?** Leakage, underpowering, instance
  selection, a control that did not control, the wrong comparison object.
- **Confirmed, overturned, or insufficient?** Insufficient with a named missing control is a
  success — it turns a NO-GO into a provisional one with a concrete way to reopen it.

## What success looks like
An audit whose first half no one can argue with (a lock diff, recomputed numbers, a reproduction
table) and whose second half names exactly what would change the conclusion.

## The failure it guards against
Agreement by default. Role separation here is prompt-level — the same underlying model could
play implementer and auditor — so the audit leans on mechanical checks, a fresh context,
artifact-only inputs, and a different model wherever one is available.
