# /qml-run — essence

## What this skill is for
Executing one frozen phase faithfully: numbers anyone can trace to a file and a command, a gate
table with no opinions in it, and an honest stop when something cannot be done. It measures; it
never concludes.

## The judgment calls it makes
- **Is this phase still decision-relevant?** Restate the frozen question and the gates this phase
  serves before any code. If no locked gate depends on the work, it is not work.
- **Is the implementation trustworthy enough to scale?** Small analytic cases first, a dry run at
  the smallest size, exact vs finite-shot convergence — only then the full phase.
- **Is a surprising number a result or a bug?** Too good, too little variance, independent of the
  input: logged as a possible bug first.
- **Blocked or not?** BLOCKED with the exact failing command is a legitimate outcome. Working
  around a constraint — downloading a checkpoint, patching a scorer, training on test, redefining
  a metric — is the worst thing that can happen in this lab.

## What success looks like
A gates table computed by a tool from locked thresholds, a phase report whose every number has
a provenance id, a clean guard check, and a gate-decision proposal that follows the
pre-registered policy.

## The failure it guards against
Plausible wrong code that produces a clean-looking NO-GO, and the documented agent pathologies:
overclaiming, evaluation gaming, and fabricating around blockers.
