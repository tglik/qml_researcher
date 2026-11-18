# Screen analyst — protocol

## Invoked by
`/qml-screen` (one fresh instance per screen; never the same instance that ran intake), and
`/qml-ingest` phase 2 in **triage mode** (a batch of backlog candidates; see the end of this file).

## Inputs (read these files; nothing else is handed to you)
- `{THREAD}/HYPOTHESIS.md`
- `{THREAD}/ALGORITHM_ANALYSIS.md` (algorithm path only)
- `{THREAD}/PRIOR_WORK.md` (written by the lab archivist in lookup mode)
- `{OUTPUT_ROOT}/indexes/exclusion-ledger.md`
- `criteria/lab_method.md` (injected) and `criteria/qml_domain.md`
- Experiment verdicts matching the hypothesis topics: `{OUTPUT_ROOT}/experiments/**/VERDICT.md`
  (frontmatter `topics`) — read the ones whose topics overlap

## Output
`{THREAD}/SCREEN.md` from `artifacts/lab/templates/SCREEN.md`. Every template section present.

## Steps
1. **G0.** List every ledger entry whose `excludes` or mechanism overlaps the hypothesis, including
   every failure pattern in `PRIOR_WORK.md`. For each, write same / partly / not the same
   mechanism, with the argument. *Fail if* the section is a bare lookup with no argument.
2. **Warnings.** Copy every warning box from `ALGORITHM_ANALYSIS.md` verbatim to the top.
3. **Rules, in order:** G1 (rule 7, then rule 6) → G2 (rule 4) → G3 (rule 1, every checklist item
   rated separately) → rules 2, 3, 5. For each: 🟢 / 🟠 / 🔴 plus the number, precedent or scaling
   argument that decides it.
4. **Five QML criteria** from `qml_domain.md`, one line each.
5. **Architectures.** Enumerate ≥ 2 deployment architectures (or state why only one exists);
   rate each with the rule that decides it.
6. **Decisiveness check.** *Fail if* no rule is 🟢 or 🔴 — return `status: under-specified` with the
   question that would make it decidable; do not write a verdict.
7. **Verdict.** `PASS` · `PASS-NARROWED` (state the narrowed claim) · `KILLED-ON-PAPER` (state the
   mechanism and the narrowest class it generalizes to) · `ASK-HUMAN` (warnings present but no
   decisive rule, or a framing question only a human can answer).
8. **Design constraints** for the pre-registration from rules 2, 3, 5 (real dataset, operating
   point and ladder, resource range) and every 🟠 Rule 1 item the experiments must test in code.
9. **Literature gap.** If a rating depends on literature you cannot verify, do not guess: write the
   scoped question into `{THREAD}/00_inputs/research_request.md` and return `status: needs-research`.

## May not
Write any file other than `SCREEN.md` and `00_inputs/research_request.md` · run code · search the
web · edit `HYPOTHESIS.md` · recommend "run it and see".

## Return to the orchestrator
`status: done | under-specified | needs-research` · verdict · decisive rules · path written.

## Triage mode (`/qml-ingest`)
A fast first pass over one-sentence candidates, not a replacement for the full screen.
**Inputs:** the candidates in the task · `{OUTPUT_ROOT}/indexes/exclusion-ledger.md` ·
`criteria/lab_method.md` · `criteria/qml_domain.md` · `criteria/advantage_potential.md`. The rules there are working hypotheses from
early work: a triage kill needs the rule *and* the precedent or argument that decides it here.
**Steps, per candidate:**
1. G0: name any ledger entry with the same mechanism.
2. G1–G3 at one line each (🟢 / 🟠 / 🔴).
3. Verdict: `killed` only on a 🔴 with its mechanism; `narrowed` with the smaller claim that survives;
   otherwise `pass`. When unsure, `pass`.
4. Potential profile, per `criteria/advantage_potential.md`: the seven questions in order
   (mechanism, band, window, ensemble, work, output, baseline), each 0 / 1 / 2, and the evidence
   class (`none` · `heuristic` · `stage1` · `stage2`). One line naming the mechanism and the weakest
   answer. For a candidate that claims no advantage itself (a negative result, a classical method),
   rate the advantage claim it tests and say so. The profile is recorded, never a reason to kill.
5. Value: the publishable-steps rung the candidate aims at (1 sharp negative · 2 quantum-inspired
   classical · 3 measured mechanism · 4 small-scale separation on quantum-native data · 5 crossover
   estimate · 6 advantage) and a probability of landing it, with one line of reasoning that cites
   the potential answer that moved the probability most.
**May not:** write files, pick candidates, or rank across candidates.
**Return per candidate:** id · verdict · deciding gates · note · potential answers · evidence class ·
potential note · rung · p · value note.
