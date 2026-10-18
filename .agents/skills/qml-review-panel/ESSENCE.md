# /qml-review-panel — essence

**Job.** Group meeting on demand, without the social filter: six reviewers, each attacking one
surface, run on the proposal before freeze and on the raw results before anyone writes what they
mean.

## Judgment calls
- **Is this blocking?** Only if the intended conclusion cannot be licensed without the fix.
- **Is a clean pass honest?** Yes, when it is. The block rate is tracked because both always
  blocking and never blocking are failures.
- **When to look.** Pass 2 happens before any verdict language exists, because once an
  interpretation is written, review turns into defense.

## Success
Pass 1 catches the missing control, the untuned baseline, the single-point gate and the unreal
operating point before they are frozen. Pass 2 catches drift, leakage and artifacts while they are
still just numbers.

## Failure it guards against
A gate that "passes" until a random subset of the same size does the same, caught only by a person
after the fact.
