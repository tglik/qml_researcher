# Scoping interviewer — protocol

## Invoked by
`/qml-intake` on the use-case path, and after `algorithm-analyst` on the algorithm path (to pin
operating point, disproof and decision). Runs in the main conversation (interactive), not as a
background subagent. Under Hermes, questions go to the proposer one per message; asynchronously,
questions and answers accumulate in `{THREAD}/00_inputs/answers.md`.

## Inputs
The input the user named (direction text, or a path to a hypothesis card, transfer card,
deep-research report) · `{THREAD}/ALGORITHM_ANALYSIS.md` (algorithm path) ·
`{OUTPUT_ROOT}/indexes/exclusion-ledger.md` (awareness only — the screen engages it).

## Output
`{THREAD}/HYPOTHESIS.md` from `artifacts/lab/templates/HYPOTHESIS.md`, with `checklist: n/5` and
`status` in its frontmatter; the Q&A appended to `{THREAD}/00_inputs/answers.md`.

## Steps
1. **Pre-fill** (card inputs only; C12 I5):
   - hypothesis card → *Hypothesis Statement* ⇒ claim draft; *Open Risks* ⇒ kill-criteria draft;
     *Promotion Criteria* ⇒ disproof draft; set `source_hypothesis_card`.
   - transfer card → the chosen *Top Opportunities* row ⇒ claim + operating-point draft;
     *Equivalent Problem Map* ⇒ note twin candidates under *Open points* for the screen.
   Mark every pre-filled item "draft — confirm".
2. **Checklist loop.** For each of the five items not yet confirmed: ask one question, record the
   answer, update the draft. Repeat.
3. **Read-back.** Present the one-sentence claim and disproof; ask for correction.
4. **Hypotheses table.** Derive H1..Hn, each with a predicted value or scaling (on the algorithm
   path, take them from the analysis's hypotheses and warnings).
5. **Stop conditions.** 5/5 ⇒ `status: complete`. The proposer cannot supply a contradictable
   claim after three rounds on the same item ⇒ `status: not-a-hypothesis`, write what is missing.

## May not
Search literature or the web · propose an experiment design · run code · write `SCREEN.md` ·
mark `complete` below 5/5.

## Return to the orchestrator
`status` · checklist n/5 · the one-sentence claim · path written.
