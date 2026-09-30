# C03 — Roles, people & permissions

## Purpose
Decide who may generate, who may check, and who may approve — for agents *and* people — so
that generator ≠ verifier holds by construction. Realizes Meir's Role × Skill × Permission
model as a documentation-plus-convention layer (D2), written so a later platform can lift it.

## Owner role(s) and human touchpoints
Owned by Tsahi (system engineer). Adi approves the permission matrix before W1. Changes to
this file are CP5-class (human PR).

## Inputs / outputs
Output: `qml_researcher/docs/lab/roles.md` (the tables below, canonical) and agent definition
files under each owning skill (`.agents/skills/<skill>/agents/<role>.md`, per `protocol.md`
— skills own their agents; a role used by two skills gets one canonical file in the owning
skill and is referenced by path from the other).

## Artifact schemas

### Role slots (agents)
| Role | Mandate | Owning skill | May not | Meir name | Adi stage |
|---|---|---|---|---|---|
| `lab-director` | Frozen question, budget, decision-relevance test, stop rule | `qml-lab` | change gates; write results | Senior researcher | — |
| `scoping-interviewer` | Falsifiability interrogation (use-case path) | `qml-intake` | start literature or code | Senior (formulation) | — |
| `algorithm-analyst` | Adi S0 analysis (algorithm path) | `qml-intake` | recommend a design | Senior + Systems | S0 Analyst |
| `screen-analyst` | G0–G3 + 5 criteria, kill cheap | `qml-screen` | recommend "run it and see" | Junior + Peer reviewer | Gate 0 |
| `experiment-designer` | Prereg, gates, P1–P5, both verdict sentences | `qml-prereg` | run what it designed; audit | Senior | S1 Designer |
| `classical-twin-champion` | Strongest honest classical arm + twin | `qml-prereg` (spec) / `qml-run` (build) | touch quantum arm | Classical adversary | S0 C-14 |
| `implementer` | One phase at a time, provenance | `qml-run` | edit lock/gates/verdict | Junior + Experimenter | S3 Experimenter |
| `review-panel` ×5 | methodologist · dequantization-theorist · hardware-realist · baseline-champion · value-translator | `qml-review-panel` | rewrite what it reviews | Peer reviewer / critic | S2 Reviewer |
| `verdict-writer` | Verdict vs frozen gates | `qml-verdict` | strengthen wording past status | Senior (synthesis) | S4 Summarizer |
| `verdict-auditor` | Fresh-context audit, artifacts only | `qml-audit` | have run or designed anything | Peer reviewer | S5 Verifier |
| `variant-generator` | Variants + pivot questions | `qml-variants` | emit unscreened ideas | Senior (pivot) | S6 Explorer |
| `lab-archivist` | Source report, ledger entry, registry | `qml-promote` | interpret or widen scope | Memory curator | — |

Every slot has `filled_by: agent | human`. A human filling a slot (typically **Meir** as
`implementer`, `screen-analyst` drafter, or `scoping-interviewer`) inherits the slot's
*may-not* column.

### People (V1)
| Person | Standing role | Typical slots | Signs |
|---|---|---|---|
| **Meir** | Junior researcher / program owner | `implementer`, `screen-analyst` (draft), `scoping-interviewer` | any CP where he is not the author |
| **Adi** | Lab director / principal | — (supervisor) | any CP; default signer for CP2 and CP4; priorities; physics-bearing thresholds |
| **Tsahi** | User + system engineer | any slot when running his own program | any CP where not author; **autonomy step-downs**; skill/template changes |

**Signer ≠ author** is the one hard people-rule: a checkpoint's `author` (agent role *or* the
human who drafted/edited it) cannot be its `signer`. `/qml-lab` rejects a sign-off that
violates it.

### Permission matrix (checkpoint and file level)
Vocabulary from Meir: **O** own · **E** execute · **R** review · **A** approve · **S** escalate.

| | intake | screen | prereg/lock | panel | run | verdict | audit | variants | promote/ledger | autonomy config |
|---|---|---|---|---|---|---|---|---|---|---|
| lab-director | R | R | R | R | S | R | — | R | R | — |
| scoping-interviewer / algorithm-analyst | O/E | — | — | — | — | — | — | — | — | — |
| screen-analyst | R | O/E | — | — | — | — | — | R | — | — |
| experiment-designer | R | R | O/E | — | — | — | — | — | — | — |
| classical-twin-champion | — | R | E | — | E (baseline arm only) | — | — | — | — | — |
| implementer | — | — | — | — | O/E | — | — | — | — | — |
| review-panel | — | — | R | O/E | — | — | — | — | — | — |
| verdict-writer | — | — | — | — | — | O/E | — | — | — | — |
| verdict-auditor | — | — | — | — | — | R | O/E | — | — | — |
| variant-generator | — | — | — | — | — | R | R | O/E | — | — |
| lab-archivist | — | — | — | — | — | — | — | — | O/E | — |
| Meir / Adi / Tsahi | A (CP-less, advisory) | **A (CP1)** | **A (CP2)** | R | **A (CP3)** | **A (CP4)** | R | R | **A (CP5)** | Tsahi A |

File-write enforcement in V1 is by convention + checks: `/qml-run` computes a git diff at phase
end and fails if the implementer touched `PREREG.lock.json`, `PROPOSAL.md`, `frozen_definitions.md`,
or `VERDICT.md`.

### Escalation table (Meir §7 mapped to V1 people)
| Trigger | First owner | Human target | Brief must include |
|---|---|---|---|
| Unplanned phase failure (not a pre-registered stop) | implementer → lab-director | Adi | likely cause: bug / hyperparams / real limit / noise; options + cost |
| Phase cost > 2× budget | lab-director | Adi (priority), Tsahi (compute) | spent vs planned, remaining gates, option to stop |
| Cloud / GPU spend or QPU request | lab-director | Adi + Tsahi | G4/G5 status (must be passed) |
| Apparent advantage (any GO or CONDITIONAL-GO draft) | verdict-auditor + classical-twin-champion | Adi + Tsahi | twin attempts, baseline adequacy, lock diff |
| BLOCKED twice on same phase | implementer | Meir (owner) → Adi | exact failing command, attempts |
| Panel BLOCKED twice | review-panel | Adi | the blocking issues, designer's responses |
| Mathematical inconsistency / trainability failure | review-panel | Adi | derivation or gradient evidence |
| Literature contradicts hypothesis / novelty unclear | screen-analyst | Tsahi → routes to `/qml-deep-research` | citations |
| Two programs converging on the same mechanism | lab-archivist | Adi | the two threads + shared ledger entry |
| Signer = author conflict | `/qml-lab` | the other two people | — |

## Procedure
1. W0: write `roles.md` with the four tables; write agent defs (one file per role) with
   mandate, *may-not*, required inputs (artifact paths only), output template, and the
   role's guideline sentence from the Sept 23 doc §3.1. *Pass:* each def ≤ 150 lines,
   references templates by path.
2. Adi reviews the matrix. *Pass:* signed in `decision_log` of the lab repo.

## Checkpoints and autonomy
No checkpoint of its own; defines who can sign each one. The step-down authority (Tsahi) is a
people-rule, not a mode.

## Separation / permission rules
- `implementer` ∉ {verdict-writer, verdict-auditor}. `experiment-designer` ∉ verdict-auditor.
- `verdict-auditor` receives artifacts only, fresh context, different model where available.
- `classical-twin-champion` is scored on baseline strength (C10), never on the verdict.
- Signer ≠ author, for people.

## Failure modes and controls
| Failure | Control |
|---|---|
| Same model plays implementer and auditor (prompt-level separation only) | Different model for auditor where available; mechanical audit components (lock diff, recomputation) |
| Meir (as implementer) also signs CP3 on his own phase | signer ≠ author check in `/qml-lab` |
| Escalation spam | Only listed triggers page; pre-registered stops never page |

## Evals that cover it
C10 structural check: each CP row in the autonomy log has author ≠ signer; eval 2 run with
the auditor on a fresh context.

## Build tasks
- [ ] `docs/lab/roles.md` (S, ½ day)
- [ ] 12 agent defs + 5 panel persona defs (M, 2 days)
- [ ] `scripts/lab/guard.py` — git-diff write guard used by `/qml-run` (S, C06)

## Acceptance criteria
Every skill in C04–C09 spawns only roles listed as O/E for it; Adi signs the matrix; the
guard rejects a seeded implementer edit to `PREREG.lock.json`.

## Open questions
- Second model for the auditor under Hermes (see `00` open question 2).
