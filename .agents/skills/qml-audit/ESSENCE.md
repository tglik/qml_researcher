# /qml-audit — essence

**Job.** Independently check that the verdict follows from correct experiments and correct
analysis, and that a negative is strong enough to prune everyone's search. Only a confirmed audit
makes a NO-GO final. The audit checks the verdict; it never writes one.

## Judgment calls
- **Did anything move?** Thresholds, splits and stop rules against the lock; amendment dates against
  the data.
- **Do the numbers reproduce?** Recomputed from raw data with independent code; a subset rerun from
  stored code, environment and seeds.
- **Could something else produce this?** Leakage, underpowering, instance selection, a control that
  did not control, the wrong comparison object.
- **Confirmed, overturned or insufficient?** Insufficient with a named missing control is a
  success: it makes the NO-GO provisional, with a concrete way to reopen it.

## Success
An audit whose first half nobody can argue with (lock diff, recomputed numbers, reproduction table)
and whose second half names exactly what would change the conclusion.

## Failure it guards against
Agreement by default. Role separation is prompt-level, so the audit relies on mechanical checks, a
fresh context, artifact-only inputs and a different model where one is available.
