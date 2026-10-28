---
thread: {thread}
entry_path: {algorithm | use-case}
source: {path to the input: algorithm paper/notes in 00_inputs/, hypothesis card, transfer card, deep-research report, or "direct"}
source_hypothesis_card: {cards/hypotheses/<slug> | none}   # C12 I1 — promotion updates this card's status
format: 2
checklist: {n}/6
status: {draft | complete | not-a-hypothesis}
date: {YYYY-MM-DD}
---

# Hypothesis — {the question in plain words, e.g. "does a quantum fingerprint kernel beat classical ML on small datasets?"}

<!-- Write for a reader outside the field: an ML engineer who is not a quantum or domain expert.
Plain words, one idea per sentence, the message before the details. Define every term the first
time it appears, or put it in Background. Use common academic terms ("baseline", "proposed
method"), not lab shorthand (no gate ids, rule numbers or "arm"). See lab/STYLE.md. -->

## In one paragraph
{4–6 sentences: what the method does, why the proposer thinks it helps, what we test it on and
against, and the result that makes us drop it (in bold). If the claim is classical at every size we
can run, say so here.}

**Claim, in one sentence:** {the claim a number could contradict, with its margin, data and size —
the sentence read back to the proposer and frozen when the program runs.}

## Background the reader needs
- **{Term}.** {One or two sentences.} ({Reference.})
{Only the concepts the sections below use. Domain terms (chemistry, finance, …) belong here too.}

## The algorithm
{The proposed method as a pipeline or numbered steps: input → what the quantum part computes →
what it outputs → how that output is used. Name what each step produces. One sentence that says
what the quantum computer's job is, e.g. "the quantum computer is a feature extractor; everything
after it is a standard kernel model". Math only where words would be ambiguous.}

## Why this approach, and why built this way
**The proposer's reason:** {why the proposer expects it to work, in their terms.}

**Design choices and why:** {one bullet per choice: why this encoding / size / readout / place in
the pipeline, and what the alternative would cost. Mark the lab's own analysis as [analysis].}

**What we already know:** {prior results on this question, if any; omit the paragraph if none.}

**What must be true for the claim to hold.** Each link is tested by the hypothesis in brackets:
1. {link} ({Hk})
2. {link that cannot be tested here} (Not testable here: {reason}.)

## Hypotheses
{One block per link. Optional first block: **Precondition** (e.g. the baseline is adequate), with
*Why* and *If it fails*.}

**H1 — {short name}.** {Statement a number could contradict: quantity, margin, data, size.}
- *Why we expect it:* {the mechanism or evidence behind the prediction.}
- *Why test it:* {which link it tests and what we learn either way; where the margin comes from.}
- *Disproof:* {the result that makes it false, written before any data.}

## Classical baselines
{The strongest classical methods that get the same input and the same tuning budget (lab_method
Rule 1). Say which one decides each hypothesis. If the proposer named a weak baseline, say it is a
starting point, not the bar. End with the fairness rule: whatever physical input the quantum method
gets, the baselines get too.}

## Where the claim must hold
| | Tested here | Target |
|---|---|---|
| Problem size | | |
| Data | | |
| Metric | | |
| Cost / latency / cadence | | |
| Hardware | {modality, or "hardware-agnostic"} | |

## Known risks
- **{Risk in a few words.}** {Why it could sink the claim; which hypothesis it touches.}
{Risks raised before any data: classical shortcuts, labels that cannot reward the mechanism, small
data, results from earlier runs.}

## Open points
- [ASSUMPTION] / [UNVERIFIED] / [OPEN] {what the interview could not resolve, and who settles it}

## Sources
- {inputs read during intake, one line each}
