# /qml-review-panel — essence

## What this skill is for
Group meeting on demand, without the social filter — five reviewers, each attacking one surface,
run twice: on the proposal before it is frozen, and on the raw results before anyone has written
what they mean.

## The judgment calls it makes
- **Is this blocking?** Only if the conclusion we want to draw cannot be licensed without the fix.
- **Is a clean pass honest?** Yes, when it is. A panel that always blocks is noise; one that never
  blocks is decoration. The block rate is tracked for exactly this reason.
- **When to look.** The second pass happens before verdict language exists, because once an
  interpretation is written, review turns into defense.

## What success looks like
Pass 1 catches the missing control, the untuned baseline, the single-point gate, the unreal
operating point — before they are frozen. Pass 2 catches drift, leakage and artifact
explanations while they are still just numbers.

## The failure it guards against
M01's H2 — a gate that "passed" until a random subset of the same size did the same, caught by a
human after the fact. The panel exists to catch that prospectively.
