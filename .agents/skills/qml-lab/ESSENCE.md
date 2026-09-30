# /qml-lab — essence

## What this skill is for
The lab's front door and its conscience. People start programs, see what is waiting for them,
and sign decisions here; every other lab skill is reached through it. It exists so that a
program stays on its frozen question, happens in the right order, stays inside its budget, and
asks a human only for the decisions that need one.

## The judgment calls it makes
- **Is the next step allowed?** Order is a safety property: no pre-registration before the
  screen is signed, no run before the lock is frozen, no verdict before the panel has seen raw
  results, no promotion before the verdict is signed.
- **Is the next step worth doing?** The decision-relevance test: can this work change the outcome
  of any locked gate? If not, it is not run.
- **Does a human need to see this?** Only at the checkpoints in their current mode, and on the
  listed escalations. A pre-registered stop is the design working, not an escalation.
- **Has a checkpoint earned less supervision?** Only when the record says so: five consecutive
  sign-offs with no material change and a passing replay eval — and only Tsahi approves the step.

## What success looks like
A person asks the lab what is waiting, sees in one screen what is waiting for them and why, reads a
one-page brief, signs in a single command, and spends about an hour per milestone — on the
questions "is this the right question?" and "does this verdict mean what it says?".

## The failure it guards against
A system that runs an impeccably gated experiment on the wrong question, or quietly lets a
human checkpoint become a rubber stamp. Hence: briefs instead of transcripts, the minutes
field, and automatic restoration of supervision after any material miss.
