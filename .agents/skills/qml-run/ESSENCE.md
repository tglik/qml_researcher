# /qml-run — essence

**Job.** Execute one frozen phase faithfully: the classical side first, then the quantum side;
numbers anyone can trace to a file and a command; a gate table with no opinions in it; an honest
stop when something cannot be done. It measures; it never concludes.

## Judgment calls
- **Is this phase still decision-relevant?** If no locked gate depends on the work, it does not run.
- **Is the implementation trustworthy enough to scale?** Small known-answer cases first, a dry run at
  the smallest size, exact versus finite-shot convergence, then the full phase.
- **Is a surprising number a result or a bug?** Too good, too little variance, or independent of the
  input: logged as a possible bug first.
- **Blocked or not?** BLOCKED with the exact failing command is legitimate. Working around a
  constraint by changing the problem is the worst thing that can happen in this lab.

## Success
A gate table computed by a tool from locked thresholds, a phase report whose every number has a
provenance id, a clean guard check, and a gate decision that follows the pre-registered policy.

## Failure it guards against
Plausible wrong code that produces a clean-looking NO-GO, overclaiming, evaluation gaming, and
fabricating around blockers.
