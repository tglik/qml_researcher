# What changed, and what we would like from you

## Why we did this
All three of us found the exp 18 documents hard to follow. Four things caused most of it:
- **Lab shorthand instead of plain words.** Gate ids (G5/N1), rule numbers, "arm", "twin", "Q-FEAT-core" and experiment codes were used without being defined.
- **No algorithm and no motivation.** The hypothesis never said what the quantum circuit computes, what it outputs, or why it should help with CO₂ binding. Adi's test failed: a PhD student could not explain the idea back from it.
- **The main point was buried.** The claim was one four-line sentence with eight qualifiers. The proposal was 1,662 lines and opened with four rounds of revision notes.
- **Design, history and review responses were mixed together.** Panel issue numbers and revision notes sat inside the rules an implementer has to follow.

## What we did
1. **Rewrote exp 18 as drafts.** The hypothesis, a short plan, and one document per experiment (E1–E5). The science, thresholds and data are unchanged. The frozen thread and its lock are untouched.
2. **Changed the lab**, so every new program comes out in this format (commit 7aff247):
   - new templates for the hypothesis, the plan and the experiment document;
   - an intake checklist that also requires the *why*;
   - "arm" replaced by "baseline" and "proposed method";
   - writing rules for readers outside the field.

| | Before | After |
|---|---|---|
| Hypothesis | 121 lines, no algorithm, no motivation | 226 lines: summary, background with references, the algorithm, why it is built this way, and a *why* for every hypothesis |
| Proposal | one 1,662-line file | a 170-line plan plus five experiment documents (105–183 lines each) |
| Decision ("what this changes") | in the hypothesis | in the plan |
| Revision history | at the top of the proposal | in the change log only |

## What to look at, in this order
1. **The hypothesis.** After reading it, could you explain the claim, the algorithm and why it is built this way to someone else?
2. **The plan.** Can you get the whole program in five minutes? **Meir:** the *Before spending* section has four questions that need your decision.
3. **E1** (running now) and **E3** (the core experiment). Are the decision rules clear and correct?
4. **E2, E4, E5.** Are they described correctly?
5. **The qml-06 hypothesis.** A second example, on a QML paper. **Adi:** does its *why* section explain the method the way you would want from a PhD student?
6. **The three templates.** This is what the lab will produce for every new program.

## How to review
For each item, pick a verdict and write a comment. Quote the line you mean, and suggest wording where you can. Every item except this one has a **Compare with the original** panel, so you can judge before and after side by side. Your reviews are saved for the whole team to see.
