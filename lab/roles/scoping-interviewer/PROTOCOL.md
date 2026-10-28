# Scoping interviewer — protocol

## Invoked by
`/qml-intake` on the use-case path, and after `algorithm-analyst` on the algorithm path (to pin
the why, operating point, disproof and decision). Runs in the main conversation (interactive), not as a
background subagent. Under Hermes, questions go to the proposer one per message; asynchronously,
questions and answers accumulate in `{THREAD}/00_inputs/answers.md`.

## Inputs
The input the user named (direction text, or a path to a hypothesis card, transfer card,
deep-research report) · `{THREAD}/ALGORITHM_ANALYSIS.md` (algorithm path) ·
`{OUTPUT_ROOT}/indexes/exclusion-ledger.md` (awareness only — the screen engages it).

## Output
`{THREAD}/HYPOTHESIS.md` from `artifacts/lab/templates/HYPOTHESIS.md` (`format: 2`), with
`checklist: n/6` and `status` in its frontmatter; the Q&A appended to
`{THREAD}/00_inputs/answers.md`, including the decision the answer changes (the designer copies it
into the plan; it is not written in `HYPOTHESIS.md`).

## Steps
1. **Pre-fill** (card inputs only; C12 I5):
   - hypothesis card → *Hypothesis Statement* ⇒ claim draft; *Open Risks* ⇒ kill-criteria draft;
     *Promotion Criteria* ⇒ disproof draft; set `source_hypothesis_card`.
   - transfer card → the chosen *Top Opportunities* row ⇒ claim + operating-point draft;
     *Equivalent Problem Map* ⇒ note twin candidates under *Open points* for the screen.
   Mark every pre-filled item "draft — confirm".
2. **Checklist loop.** For each of the six items not yet confirmed: ask one question, record the
   answer, update the draft. Repeat. For the why, ask why the proposer expects the method to work
   and why each design choice (encoding, size, readout, where it sits in the pipeline) was made.
3. **Read-back.** Present the one-sentence claim and disproof; ask for correction.
4. **Chain and hypotheses.** Write what must be true for the claim to hold as a numbered chain of
   links. Derive one hypothesis per testable link (on the algorithm path, from the analysis's
   hypotheses and warnings), each with a predicted value, *why we expect it*, *why test it* and its
   *disproof*. Name links that cannot be tested at the sizes the lab can run.
5. **Write for the reader.** Fill *In one paragraph*, *Background the reader needs* (terms and
   references from the inputs only), *The algorithm* and *Why this approach* from the inputs, the
   analysis and the answers. Mark the lab's own reasoning [analysis]. Check against `lab/STYLE.md`.
6. **Stop conditions.** 6/6 ⇒ `status: complete`. The proposer cannot supply a contradictable
   claim or a reason after three rounds on the same item ⇒ `status: not-a-hypothesis`, write what
   is missing.

## May not
Search literature or the web · propose an experiment design · run code · write `SCREEN.md` ·
mark `complete` below 6/6.

## Return to the orchestrator
`status` · checklist n/6 · the one-sentence claim · path written.
