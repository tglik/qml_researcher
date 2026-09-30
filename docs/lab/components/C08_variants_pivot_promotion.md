# C08 — Variants, pivot & promotion (`/qml-variants`, `/qml-promote`)

## Purpose
Turn every closed program into (a) the next best directions, mined from the named failure
mechanism, and (b) durable memory — a scoped, expiring exclusion, a finalized verdict
entity, and any transferable rule — without over-pruning. Merges Tsahi's variant generators with Adi's S6
pivot questions (D11).

## Owner role(s) and human touchpoints
`variant-generator`, `lab-archivist`. Human: **CP5 promotion** — permanent `HUMAN_APPROVE`,
realized as merging the promote PR in `qml_artifacts` (and in `qml_researcher` when criteria
change). Variants themselves need no sign-off; they enter the backlog as `speculative`.

## Inputs / outputs
| Skill | Input | Output |
|---|---|---|
| `/qml-variants` | `VERDICT.md`, `AUDIT.md` (or `SCREEN.md` for KILLED-ON-PAPER), ledger | `VARIANTS.md`; ≤ 5 hypothesis cards (`research_hypothesis_schema.md`) at status `speculative` |
| `/qml-promote` | audited verdict (or CP1-approved kill), `VARIANTS.md` | finalized `VERDICT.md` entity frontmatter; ledger entry; rebuilt registry + topic-map rows; proposed criteria / INSIGHTS amendments; the program branch's PR into `qml_artifacts` master |

## Artifact schemas
C01 `VARIANTS.md`; C02 ledger entry; C11 `VERDICT.md` entity frontmatter (replaces
`experiment_card_schema.md`); existing `research_hypothesis_schema.md`.

No card and no mirrored source report (D12): the experiment folder is the graph entity, and
`VERDICT.md` frontmatter carries the D10 verdict value directly, so no enum mapping is needed.

## Procedure

### `/qml-variants` (runs at verdict time, never at kill-less time — needs the mechanism)
| Phase | Work | Pass/fail |
|---|---|---|
| 0 Mechanism | Restate mechanism as a precondition; pick cause from Adi S6 §1 list (loading / readout / shots / twin / simulable / trainability / noise / small poly speedup / irrelevant instances) | One primary cause |
| 1 Inversion | What would have to be true for the mechanism not to apply? (twin exists because diffusion has no sign cancellation → magnetic Laplacians → exp 12) | ≥ 1 candidate or "none" |
| 2 Axis relaxation | Relax exactly one axis: data regime, output shape, cadence, resource cap, accuracy tolerance, deployment stage — is there a real use case there? | One axis per candidate |
| 3 Adi S6 Q1–Q3 | Algorithm tweak; task tweak (check still useful in practice); sweet spot from P1–P4 curve crossings | Rated high/med/low with argument |
| 4 Salvage | (a) classical results worth keeping, (b) instruments/protocols that transfer, (c) genuine quantum variants — only (c) re-enters the quantum program | Every (a)/(b) listed explicitly |
| 5 Screen pre-apply | Each surviving variant gets the six-rule screen pre-applied; names **newly-passed gate** and **newly-faced gate** + predicted kill gate. Same gate, same mechanism → not a variant, goes to ledger `covered_cases` | ≤ 5 ranked |
| 6 Paper & patent (Adi S6 Q4–Q5) | What's new (negative result, benchmark, dequantization, quantum-inspired method, resource analysis); venues, closest work, title/abstract/figures. Patent: novel technical elements, obvious prior art. ⚠️ Not legal advice; **disclosure before filing may destroy novelty — decide order first** | Flags + recommendation |
| 7 Recommend | close / publish / IP-first / new cycle at intake (name which variant) | One |

### `/qml-promote`
| Phase | Work | Pass/fail |
|---|---|---|
| 0 Branch | Work on the program's existing branch `lab/<thread>` in `qml_artifacts` | Branch up to date with master |
| 1 Entity frontmatter | Finalize `VERDICT.md` frontmatter (C11 schema): verdict, audit result, topics, `ledger` ids, `related` links | Validates vs `experiment_entity_schema.md` |
| 2 Ledger | Entry per C02 schema, **narrowest mechanism-scoped class**, `does_not_exclude` mandatory, `review_by` set; FINAL only if audit CONFIRMED | Validates |
| 3 Registry / topic map | `scripts/lab/registry.py` rebuilds `indexes/experiment-registry.md` and topic-map experiment rows from all VERDICT frontmatter | Diff limited to this program's rows |
| 4 Graph links | Add `## Graph links` to `VERDICT.md` (claims, papers, hypotheses it bears on) | Links resolve in Quartz build |
| 5 Proposals | Optional `criteria/qml_domain.md` deprioritization; optional INSIGHTS / `lab_method.md` amendment **only** if a genuinely new transferable rule emerged — both as *proposed diffs* in the PR description, not applied (they live in `qml_researcher`) | Marked "proposal" |
| 6 Hypothesis cards | Write variant cards in `cards/hypotheses/` linked to the ledger entry they descend from | — |
| 7 PR + CP5 | Open PR with brief as description; `/qml-lab` logs CP5 on merge | Human merge |

Iron rule: scope discipline — "this construction fails as a recsys ranker for this mechanism"
may never be recorded as "graph QML is dead".

## Checkpoints and autonomy
| CP | V1 | Target |
|---|---|---|
| CP5 promotion | HUMAN_APPROVE (PR merge) | **HUMAN_APPROVE (permanent)** |

## Separation / permission rules
Archivist never interprets or widens. Variant-generator cannot emit unscreened ideas. Paper /
patent output is advisory; any external disclosure is a human decision outside the lab.

## Failure modes and controls
| Failure | Control |
|---|---|
| Idea spam | ≤ 5; newly-passed / newly-faced gate required; same-mechanism → covered case |
| Salvage dropped along with the quantum claim | Explicit (a)/(b) section; eval 3 |
| Topic-scoped exclusion | Narrowest class; human merge; quarterly review |
| Premature disclosure | Patent warning in VARIANTS; recommendation "IP-first" when flagged |

## Evals that cover it
Eval 3 (false-kill: exp 09 compressed index at 80–87% of full retriever, exp 10 D2 streaming
moments, exp 12 phase-cancellation features + leakage warning must survive). Replay check:
variants from exp 11-style mechanisms should reproduce exp 12's inversion.

## Build tasks
- [ ] `/qml-promote` SKILL.md + `lab-archivist` def (M, 1.5 days — W1)
- [ ] `/qml-variants` SKILL.md + `variant-generator` def (M, 1.5 days — W3)
- [ ] `scripts/lab/registry.py` (shared with C11) (S)

## Acceptance criteria
Promote on one legacy thread (e.g. exp 13, after C11) produces valid entity frontmatter, a
ledger entry and registry rows in a PR with 0 material edits by the reviewer; Quartz build
has 0 broken links; eval 3 green.

## Open questions
- Should a program branch merge to master before promotion (e.g. to share work-in-progress
  phase reports)? Default: yes for the thread folder only; ledger/registry only at promotion.
