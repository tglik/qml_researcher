# QML Lab — high-level plan

**Date:** 2026-09-30 · **Decisions:** [`00_office_hours.md`](00_office_hours.md) (D1–D13) ·
**Component designs:** [`components/`](components/) · **Supersedes:** §2–§4 and §14 of
`qml_artifacts/sources/documents/qml-agent-lab-design_2026-09-23.md` (the rest of that doc —
rules, Negative Verdict Standard, failure modes, junior-researcher comparison — still stands and
is referenced, not repeated)

---

## 1. What we are building, in one paragraph

A file-based lab of skills and agent roles that takes **either a proposed quantum algorithm or a
use-case hypothesis**, kills it on paper if it can, and otherwise runs a pre-registered,
phase-by-phase experiment (toy → medium → real data → noise → hardware plan) against an
adversarially strong classical baseline, ending in an **audited verdict** that is promoted into
the knowledge graph as either a scoped, expiring exclusion or a qualified go. Humans — Meir as
junior researcher, Adi as lab director, Tsahi as user and system engineer — start by approving
every major checkpoint; each checkpoint **earns its way to less supervision** by measured
agreement between the agent's draft and the human's decision, until only design freeze and
promotion remain human.

---

## 1b. Where it lives and how it fits (D13)

The lab is built **inside `qml_researcher`** as a bounded layer, not a separate repo: it reuses
the spawn protocol, claim ladder, criteria, config, eval harness and Hermes installer, and a
separate repo would recreate the cross-repo friction D12 just removed. It completes the
researcher's loop — the literature half proposes candidate directions; the lab measures them;
verdicts flow back as hypothesis status, exclusions the scout respects, and deprioritized
directions in `qml_domain.md`. Boundary rules (one entry point, two tool tiers, Hermes
allowlist, separate lab versioning) and the seven feedback edges are in
[C12](components/C12_researcher_integration.md).

---

## 2. Architecture — five layers, all files

Meir's `Role → Skill → Tool → Evidence → Memory` split, realized without a platform (D2), in
**two repos** (D12): `qml_researcher` holds the system (roles, skills, tools); `qml_artifacts`
holds everything the system produces (evidence and memory). `qml_experiments` is retired.

| Layer | What it is | Where it lives | Component |
|---|---|---|---|
| **Roles** | Who may do what: agent definitions + human slots + permission matrix | `lab/roles/<role>/{ESSENCE,PROTOCOL}.md` (+ `docs/lab/components/C03`) | C03 |
| **Skills** | Numbered-phase procedures with a pass/fail gate per phase | `.agents/skills/qml-{intake,screen,prereg,review-panel,run,verdict,audit,variants,promote,lab}/` | C04–C09 |
| **Tools** | Deterministic Python — hashing, provenance, fits, budgets, resource estimates. The LLM never judges a number these can compute | `qml_researcher/lab/tools/*.py` | C06 |
| **Evidence** | Code, results, small data, phase reports, verdicts — one thread per program, one branch per program. `VERDICT.md` frontmatter *is* the experiment's graph entity (no separate card) | `qml_artifacts/experiments/<thread>/` | C01, C11 |
| **Memory** | Criteria, exclusion ledger, registry, literature cards, autonomy log | `qml_researcher/criteria/lab_method.md`; `qml_artifacts/{indexes,cards,sources}` | C02 |

Control state — which checkpoint each program is at, who owns it, what mode each checkpoint is
in — lives in two files: per-program `STATE.json` (C01) and lab-wide
`qml_researcher/config/lab_autonomy.json` (C09).

---

## 3. Lifecycle

```
            ┌───────────── algorithm path (Adi S0) ─────────────┐
 input ─────┤                                                   ├──► HYPOTHESIS.md (H1..Hn, predicted values)
            └──────────── use-case path (falsifiability) ───────┘         (+ ALGORITHM_ANALYSIS.md)
                                   /qml-intake
                                        │
 /qml-screen  G0 ledger · G1 readout · G2 resource cap (both arms) · G3 twin · 5 QML criteria · warning boxes
                                        │                        └─► KILLED-ON-PAPER ─► variants ─► promote
                               ◆ CP1 screen ◆
                                        │
 /qml-prereg  H→experiment map · metrics · baselines+twin · P1..P5 milestones · gray-zone policy · both verdict sentences
              → PREREG.lock.json (lab.tools.lock)
 /qml-review-panel #1  (5 personas + Adi's S2 checklist floor)
                               ◆ CP2 freeze ◆
                                        │
   ┌──── per phase Pk ─────────────────────────────────────────────────────────┐
   │ /qml-run  re-anchor · unit tests 2–4q · dry run · full run · gates.md · provenance │
   │           phase report (expected vs observed per H)                       │
   │                          ◆ CP3 phase gate ◆ ── pass ─► next phase          │
   └──────────────────────────────── fail/partial ─► stop (pre-registered) or escalate
                                        │
 /qml-review-panel #2  drift check — before any verdict language exists
 /qml-verdict  GO · CONDITIONAL-GO · NO-GO-FINAL · NO-GO-PROVISIONAL · BLOCKED
 /qml-audit    fresh context · lock diff · recompute ≥2 · rerun subset · N1–N5
                               ◆ CP4 verdict ◆
                                        │
 /qml-variants  ≤5 variants + Adi S6 pivot questions (NO-GO only; salvage always)
 /qml-promote   VERDICT frontmatter finalized · ledger entry · registry · proposals → PR
                               ◆ CP5 promotion ◆

 escalations (any step): unplanned failure · 2× budget · cloud/QPU request · apparent advantage ·
                         BLOCKED twice · panel blocks twice · signer = author conflict
                         → DECISION_BRIEF.md to the named person (C03 table)
```

`/qml-lab` (C09) is the loop around all of it: reads `STATE.json` first, writes it last, refuses
out-of-order calls, opens and closes checkpoints.

### Gate ladder attached to phases (D3)

| Gate | Attached to | What must be true | Precedent |
|---|---|---|---|
| G0 exclusion ledger | screen | Engages each brushed exclusion by mechanism | new |
| G1 readout shape/cadence | screen | Output size × frequency survives rule 6 | fraud/AML table; exp 09 |
| G2 resource cap, both arms | screen | Mandatory preprocessing charged to quantum arm | Amendment A / Q-FEAT-screen |
| G3 classical twin | screen (paper) → P1 (code, if needed) | No same-access classical twin matches | exp 04 (424×), exp 12 (4.5 s), exp 13 |
| G4 target headroom | P1 (toy) and P3 (real) | Error exists *where* the quantum step acts | exp 03; M01 |
| G5 baseline adequacy | P1 → P3 | Classical arm within pre-registered factor of SOTA — license gate | M01 H0 |
| G6 real-data transfer | P3 | Synthetic win reproduces on named real data | exp 05 → 06 |
| G7 Pareto front | P2 + P3 | Win holds across the resource axis, not one point | exp 11 |
| G8 modeled-quantum vs measured-classical at operating point | P3 | End-to-end, same variable (Adi rule 3) | exp 04, 08 |
| G9 hardware envelope / crossover band | P4 + P5 | Noise threshold + compiled resources + break-even N* | Adi P4/P5 |

---

## 4. Components

| # | Component | Skills / files | Wave |
|---|---|---|---|
| [C01](components/C01_artifacts_state_layout.md) | Artifacts, state & thread layout | templates, JSON schemas | W0 |
| [C02](components/C02_knowledge_layer.md) | Knowledge layer | `criteria/lab_method.md`, exclusion ledger, autonomy log | W0 |
| [C03](components/C03_roles_people_permissions.md) | Roles, people & permissions | `docs/lab/roles.md`, agent defs, escalation table | W0 |
| [C04](components/C04_intake_and_screen.md) | Intake & screen | `/qml-intake`, `/qml-screen` | W1 |
| [C05](components/C05_prereg_and_review.md) | Pre-registration & review panel | `/qml-prereg`, `/qml-review-panel` | W2 |
| [C06](components/C06_execution_harness_and_run.md) | Execution harness & run | `/qml-run`, `lab/tools/*.py` | W3 (lock.py in W2) |
| [C07](components/C07_verdict_and_audit.md) | Verdict & audit | `/qml-verdict`, `/qml-audit` | W2 |
| [C08](components/C08_variants_pivot_promotion.md) | Variants, pivot & promotion | `/qml-variants`, `/qml-promote` | W1 (promote), W3 (variants) |
| [C09](components/C09_orchestrator_autonomy.md) | Orchestrator & autonomy controller | `/qml-lab`, `config/lab_autonomy.json` | W1 (manual), W3 (full) |
| [C10](components/C10_evaluation_improvement.md) | Evaluation & self-improvement | evals 1–5 in `/test-skills`, retro loop | W1 onward |
| [C12](components/C12_researcher_integration.md) | Researcher integration | boundary rules (one entry point, two tool tiers, Hermes allowlist) + 7 feedback edges into the literature skills | W1–W3 |
| [C11](components/C11_repo_consolidation.md) | Repository consolidation | move experiments into `qml_artifacts/experiments/`, data policy, retire `qml_experiments` | W0 (first) |

---

## 5. Autonomy roadmap (D4, D5)

| Checkpoint | What is decided | V1 mode | Target mode | Retire evidence (in addition to 5 consecutive 0-material runs) |
|---|---|---|---|---|
| **CP1** screen | PASS / PASS-NARROWED / KILLED-ON-PAPER | HUMAN_APPROVE | AGENT (+ ledger engagement shown in brief) | Eval 1 screen replay + eval 4 scoping + eval 5 algorithm path |
| **CP2** freeze | Prereg + lock + panel #1 | HUMAN_APPROVE | **HUMAN_APPROVE (permanent)** | — framing errors only a human catches |
| **CP3** phase gate | Proceed to next phase / stop / escalate | HUMAN_APPROVE | AGENT for pre-registered pass/stop; escalation for anything unplanned | Lock-diff clean on all runs; 0 BLOCKED-fabrication findings in audits |
| **CP4** verdict | Verdict + audit pair | HUMAN_APPROVE | HUMAN_SPOTCHECK (1 in 3, plus every GO/CONDITIONAL-GO) | Eval 2 M01 audit replay + eval 3 false-kill |
| **CP5** promotion | Ledger/card/criteria changes | HUMAN_APPROVE (PR merge) | **HUMAN_APPROVE (permanent)** | — ledger writes prune everyone's search space |

Modes: `HUMAN_APPROVE` — blocks until a human signs. `HUMAN_SPOTCHECK` — proceeds; a human
reviews a sampled subset within 48 h and a material finding restores `HUMAN_APPROVE`.
`AGENT` — proceeds; decision logged; escalations still fire.

Every human decision writes one row to `qml_artifacts/indexes/autonomy-log.md`:
`date · program · checkpoint · author · signer · outcome (unchanged|minor|material) · minutes · note`.
The counter and the step-down proposal are computed by `/qml-lab` (C09); **Tsahi approves each
step-down**, and it takes effect by editing `config/lab_autonomy.json` in a PR.

---

## 6. Build waves

Order follows the ladder applied to the system itself: prove the cheapest, most fatal parts —
screen and audit — before building an executor.

| Wave | Scope | Exit criterion | Est. |
|---|---|---|---|
| **W0 — foundations** | **C11 migration first** (experiments → `qml_artifacts/experiments/`, cards → VERDICT frontmatter, data manifests, Quartz ignores, archive `qml_experiments`) · C01 templates + schemas · C02 `lab_method.md` + ledger seeded with 13 closed verdicts (+ materials M00/M01 once located) + autonomy log · C03 `roles.md` + agent defs · `config/lab_autonomy.json` all `HUMAN_APPROVE` | Quartz builds with 0 broken links and no code pages; 2 migrated experiments rerun and reproduce; ledger has one entry per closed experiment with `excludes` + `does_not_exclude`; Adi reviews 3 entries unchanged | 5–7 days |
| **W1 — screen & memory** | `/qml-intake` (both paths + transfer/hypothesis-card input) · `/qml-screen` · `/qml-promote` · `/qml-lab` minimal (state + checkpoints, no run) · evals 1, 4 · **C12 boundary rules + scout reads ledger (I2) + deprioritization proposals (I6)** | Eval 1 ≥60% of NO-GOs killed at G0–G3 incl. 3 known-answer checks; eval 4 refuses 3/3 | 1 week |
| **W2 — discipline & audit** | `/qml-prereg` + `lock.py` · `/qml-review-panel` · `/qml-verdict` · `/qml-audit` · evals 2, 3 | M01 replay: auditor flags H2 size-matched artifact and H0 → provisional; eval 3 keeps all 4 classical salvage results | 2 weeks |
| **W3 — executor & pilot** | `/qml-run` + `lab/tools/*` · `/qml-lab` full loop · `/qml-variants` · eval 5 · **pilot: Adi's algorithm, Meir driving** | Pilot reaches an audited verdict through P1–P3 with every CP logged; supervision ≤ 1.5 h per milestone | 2–3 weeks |
| **W4 — step-down** | Apply D5 using autonomy-log data; Tsahi's improvement loop (C10) running per program | First checkpoint (expected CP1 or CP3) moves to its next mode with the retire evidence attached | ongoing |

---

## 7. How we know it works

| KPI | Target | Measured from |
|---|---|---|
| Human minutes per milestone | ≤ 60 by end of W4 (≤ 90 during pilot) | autonomy-log `minutes` |
| Agreement rate per checkpoint | trending to ≥ 90% unchanged-or-minor | autonomy-log `outcome` |
| Gate-earliness on replay | ≥ 60% of NO-GOs killed at G0–G3 | eval 1 |
| False-kill count | 0 | eval 3 + audit OVERTURNED count |
| Panel block rate | between 10% and 60% (outside = decoration or noise) | `PANEL_n.md` |
| Lock integrity | 0 unexplained diffs | `lock.py verify` at every CP3/CP4 |
| Time to screen verdict | < 1 working day from intake | `STATE.json` timestamps |

---

## 8. Decision trace

| Decision | Realized in |
|---|---|
| D1 input normalized | C04 (two intake paths → `HYPOTHESIS.md`), C01 templates |
| D2 skills + files | §2 layers; C03 (matrix as convention), C06 (tools, not services) |
| D3 screen then phases | §3 gate-to-phase table; C04, C05 |
| D4 autonomy ladder | §5; C09 modes + controller |
| D5 measured-agreement retirement | §5; C09 step-down math; C10 eval gates |
| D6 people, signer ≠ author | C03 people + matrix; C09 `sign` |
| D7 local sim, P4–P5 modeling | C06 phase notes; C05 budget phase |
| D8 branch per program | C01 thread layout + `STATE.owner`; C08 promote PRs; C09 `new` |
| D9 replay first, Adi pilot | §6 W1–W3 exits; C10 evals 1–5 |
| D10 verdict vocabulary | C07; C08 card-enum mapping; C02 ledger `status` |
| D11 variants + pivot | C08 |
| D13 lab inside qml_researcher as a bounded layer | C12; C06 tool tiers; C09 entry point |
| D12 two repos, experiments in the vault | C11; C01 layout; C02 registry; C06 data fetch; C08 promote without cards |

## 8b. Implementation status (2026-09-30)

Branch `lab/implementation` (qml_researcher) and `lab/w0-knowledge` (qml_artifacts). Review guide:
[`lab/README.md`](../../lab/README.md) — every role and skill is split into **ESSENCE** (how it
thinks, for Adi/Meir) and **PROTOCOL/SKILL** (how it runs); a test enforces the split.

| Area | Built | Where |
|---|---|---|
| Method criteria | ✅ six rules with precedents, gate ladder, Adi's global rules + warning and simulation tables, N1–N5 | `criteria/lab_method.md` |
| Roles | ✅ 12 roles (ESSENCE + PROTOCOL) + 5 panel personas | `lab/roles/` |
| Skills | ✅ 10 lab skills (ESSENCE + SKILL), linked into `.claude/skills` | `.agents/skills/qml-*` |
| Templates & schemas | ✅ 11 templates, 3 JSON schemas, experiment-entity schema | `artifacts/lab/` |
| Deterministic tools | ✅ state · lock · validate · autonomy · provenance · splits · gates · guard · ledger · check_sizes (stdlib) | `lab/tools/` |
| Tests | ✅ 17 passing (tools end-to-end via CLI; structure incl. "no mechanics in essence files") | `tests/lab/` |
| Autonomy config | ✅ all checkpoints HUMAN_APPROVE; step-down math + auto/spot-check | `config/lab_autonomy.json` |
| Knowledge seed | ✅ exclusion ledger — 12 entries (10 final, 2 provisional) covering all 13 closed experiments; verdicts linked; autonomy log | vault `indexes/` |
| Researcher integration (C12) | ✅ scout reads ledger (I2) · synthesis engages ledger (I3) · deep research as lab service (I4) · intake pre-fill from cards (I5) · qml_domain cross-ref + seed proposal (I6, proposal only) · paper review/deep research load our verdicts (I7) · Hermes allowlist · SOUL "The lab" · README/AGENTS | various |
| Evals (C10) | ✅ eval 4 and 5 fully specified · 🟡 eval 1: 4 known-answer fixtures, 10 framings to write · 🟡 eval 3 specified · ⛔ eval 2 blocked (materials program missing) | `tests/cases/qml-*`, `tests/fixtures/lab/` |

**Not built yet:** scientific tools in the experiments venv (`sim_budget`, `fit_scaling`,
`resource_est` — needed for P1+ runs); `registry.py` (registry is maintained by hand until
`/qml-promote` runs for real); the 10 remaining eval-1 framings; the pilot. **Not yet exercised:**
no skill has run end to end on a live program — the first real run (a replay, then Adi's
algorithm) is the next step.

---

## 9. Non-goals for V1
Platform/workflow engine, permission enforcement in code, dashboard UI (D2). QPU or cloud
execution (D7). Literature search inside the lab — routed to `/qml-deep-research` and
`/qml-paper-review`. Many concurrent programs — V1 assumes ≤ 3 (one per person).
