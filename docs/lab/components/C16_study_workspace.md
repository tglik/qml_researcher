# C16 — Study workspace and the one-lab pilot

**Status:** built 2026-11-25, pilot not yet run. **Skill:** `/qml-study`. **Tool:** `lab.tools.workspace`.
**Why:** Tsahi asked (2026-11-22) to replicate what made the Agent alphaXiv cohort productive
("A Society of AI Scientists", Ahmad et al., Nov 2026; analysis doc
https://claude.ai/artifact/JtxHUoejgC7kcjepqTj769). On 2026-11-25 he narrowed it: one lab first,
labs added one at a time after a debrief, and the agenda taken from the backlog, not from people.

## What it copies, and from where

| Mechanism | Evidence in the source | Here |
| --- | --- | --- |
| Small study unit, many sequential authors | 98% of agents wrote one study; Stage 1 was one lab of 62 sequential agents | One `/qml-study` run = one author, one claim, hours |
| Announce, peer critique before running | 55/62 announced first; critique changed controls before GPU runs | `lock` needs announce + critique by another agent + author response with `--changed` |
| Public self-correction | 32 corrections by 20 of 62 agents, all before upload | `post correction`; plan changes after lock only via correction + `amend` |
| Numbers bound to files | 1.92M ledger entries; audits reproduced 55/55 and 20/20 | `ledger` with sha256; `release` re-checks every file |
| Objections run as code | 49% of major objections flipped a conclusion when run; text review could not tell fixed from broken | `objection` needs a script under `objections/` and a flips yes/no |
| Code read against title | 3 of 3 inspected papers had an answer-key or target leak | `AUDIT.md` with `verdict: PASS` by an agent who is not the author |
| Null results count in full | 35% null/refuted, cited at parity | `--outcome refuted|null` releases normally |

Deliberately **not** copied: visible scores during design (88% herding vs 30% hidden) — `new`
copies only title, claim, base and the bet's fatal test; output quotas (19 of 34 labs stopped at
exactly 15) — the lab has no study target; post/message minimums.

## Layout
`{output_root}/workspace/`: `lab.json` (agenda + budget), `log/` (one file per post, append-only,
so parallel sessions never conflict), `studies/<sid>/` (STUDY.md, code/, outputs/, objections/,
AUDIT.md, plus tool-only state.json, ledger.jsonl, objections.jsonl, bundle.lock.json).
The lab guard hook denies hand edits to the tool-only files and the log, STUDY.md after lock
(unless a correction was posted and no number is in the ledger), and anything in a released study.

## The pilot
- **One lab.** Agenda = backlog candidates in a person-approved order in `lab.json`. First agenda:
  the open direction tied first that has cheap bet fatal tests (quantum-native data learning).
- **Debrief after the first 3 released studies or 1 week**, whichever comes first: `workspace
  report` plus a person's read of whether each study moved the direction toward an algorithm we
  would own. Apply the learnings to this skill, then decide on lab 2 (a second direction).
- **Cost:** `budget.max_usd` / `max_hours` per study in `lab.json`; `release --cost-usd` records
  spend where the runtime reports it.

## Known limits
- Agent names are self-reported. The tool checks that author, critic and auditor names differ; it
  cannot prove different contexts or model families. Use a non-Claude critic/auditor where
  available (C15).
- "Never read scores" is a skill instruction, not a hook rule: a hook cannot tell a designing
  author from any other reader of the backlog.
- With one lab, peer critique comes from a fresh subagent, not from another lab with its own
  stake. The source found critique worked best across labs (Stage 2); we will only see that at lab 2.
- The source community did not produce novelty: agents lost to humans on novelty and significance,
  and its quality edge came from one lab. Expect rigor from this; whether it produces steps toward
  our own algorithm is what the debrief must judge.
