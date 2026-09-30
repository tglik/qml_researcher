# QML Lab — office hours: what are we building?

**Date:** 2026-09-30 · **Participants:** Tsahi (with Claude) · **Inputs:** three proposals ·
**Status:** decisions settled; high-level plan in [`01_high_level_plan.md`](01_high_level_plan.md),
component designs in [`components/`](components/)

---

## 1. The three proposals

| | Tsahi — *QML Lab* design doc | Adi — *Quantum Algorithm Evaluation Protocol* | Meir — *Roles & Skills* (ChatGPT) |
|---|---|---|---|
| Source | `qml_artifacts/sources/documents/qml-agent-lab-design_2026-09-23.md` | Artifact, 8 markdown docs (overview + S0–S6) | ChatGPT share, 2 turns |
| Unit of work | A scoped **use-case hypothesis** ("QML for X at operating point Y beats classical") | A **proposed quantum algorithm** | A **research program / quest** |
| Core bet | Kill on paper first; the trustworthy NO-GO is the product | Check correctness, then climb a size ladder toward industrial relevance | An org model: roles ≠ skills ≠ tools, with explicit permissions |
| Pipeline | intake → screen (G0–G9) → prereg + lock → panel → run → panel → verdict → audit → variants → promote | S0 understand → S1 design → S2 review → S3 run (P1–P5) → S4 go/no-go → S5 verify → S6 pivot | objective → program design → literature → hypotheses → critique → spec → baseline → implement → resources → KPI → decide → memory |
| Execution ladder | Gates ordered by cost × fatality (G0 ledger … G9 hardware envelope) | Phases by scale: P1 toy 6–16q, P2 18–26q, P3 real data + industrial extrapolation, P4 noise, P5 hardware plan | Not specified (deterministic execution layer) |
| Humans | 2 blocking gates (freeze, promotion); ≈1 h per milestone | Stop and ask at every failed gate | Escalation inbox routed to human experts; 1 human over 50+ programs |
| Runtime | Skills inside existing repos | Protocol docs for any agent | Platform: workflow engine, tools, permission matrix |
| Distinct contributions | Exclusion ledger · `PREREG.lock.json` · Negative Verdict Standard (N1–N5) · 5-persona panel run twice · variant mining · replay evals on 15 closed experiments · over-killing as the inverted pathology | Cost in the same variable (N vs q), end-to-end (loading, readout, shots) · scaling-class warning table · simulation cost ≠ quantum cost · simulation-limits table · noise + hardware phases · Adi's S5 reproduction subset · paper / patent / quantum-inspired pivots | Roles ≠ skills ≠ tools · O/E/R/A/S permission vocabulary · human role table · escalation-ownership table · decision brief, not transcript · "adding an AI researcher is cheap, adding a human raises supervised capacity" |

**Where they already agree.** Generator ≠ verifier. Criteria fixed before results. The
classical baseline is an adversary with its own role and an equal-or-larger tuning budget.
Negative results are first-class and persisted. Every claim points to evidence.

**Where they actually fork.** (1) what enters the system, (2) how big V1 is, (3) which ladder is the
spine, (4) where humans sit. Everything else composes.

---

## 2. Decisions

| # | Question | Decision | Why |
|---|---|---|---|
| **D1** | What enters? | **Algorithm *or* use-case hypothesis, normalized.** `/qml-intake` has two entry paths — *algorithm path* (Adi's S0 question set → `ALGORITHM_ANALYSIS.md`) and *use-case path* (falsifiability interrogation). Both converge on `HYPOTHESIS.md` with numbered hypotheses H1..Hn, each with a predicted value or scaling. A *program* = one thread folder. | Adi's team brings algorithms; the closed experiments started from use cases. Refusing either loses half the pipeline. Converging on one artifact keeps everything downstream single-path. |
| **D2** | Runtime? | **Skills + files only.** Skills in `qml_researcher/.agents/skills/`, agents per `.agents/shared/protocol.md`, state in files. No workflow engine, no permission service. Meir's roles/skills/tools split is kept as a *documentation and folder convention*. | Smallest thing that can prove the lab works. A platform before the screen and audit are proven is building the executor before the ladder says it's worth it. |
| **D3** | Which ladder is the spine? | **Screen, then phases.** Paper screen (G0–G3, fused with Adi's S0 analysis + warning table) runs first. Survivors get a prereg whose milestones are Adi's **P1–P5**, ordered cheapest-fatal-first. G4–G9 attach to phases (table in `01`). | Tsahi's ladder answers *should we spend compute*; Adi's answers *how to spend it*. The historical kill rate is highest at G1–G3, so they stay in front. |
| **D4** | Where do humans sit? | **Autonomy ladder that starts supervised.** Every checkpoint has a mode: `HUMAN_APPROVE → HUMAN_SPOTCHECK → AGENT`. V1: human approval at screen, design/freeze, each phase-gate report, verdict/analysis, and promotion. Target: Tsahi's 2 blocking gates (freeze, promotion) + Meir's escalation table. | We need to gain confidence that the system stays on goal and converges before we remove supervision. |
| **D5** | What retires a human gate? | **Measured agreement.** Each human decision is logged as `unchanged / minor-edit / material-change`. A checkpoint steps down one mode after **5 consecutive runs with 0 material changes** *and* a pass of that checkpoint's replay eval. Any later material miss restores the previous mode. | Retirement decided by data, not mood; restoring is automatic so stepping down is cheap to try. |
| **D6** | Who are the humans? | **Any of the 3 may sign any gate in V1; signer ≠ author.** Standing roles: **Meir** — junior researcher (drives skills, drafts artifacts); **Adi** — lab director (supervises, approves, prioritizes); **Tsahi** — part-time user + system engineer (evals, skill changes, autonomy promotions). Every role slot has `filled_by: agent \| human`. | Keeps sign-off simple while preserving the generator ≠ verifier rule for people too. Meir operating the system hands-on is the fastest way to find where it's wrong. |
| **D7** | How far does V1 execute? | **Local simulation for P1–P3; P4 = small density-matrix / trajectory noise sweeps; P5 = compilation + resource estimation (modeling only).** No QPU, no cloud spend before G4/G5 pass. | Matches the materials program's "no cloud spend before the gates fire" and Adi's "hardware needs human approval". |
| **D8** | Three people, shared repos — how? | **Branch per program.** One thread folder in `qml_artifacts/experiments/` + one git branch per program; `STATE.json` names an owner. Shared ledger, registry and criteria change only in the `/qml-promote` PR, merged by a human. | Ledger writes serialize through review; programs never step on each other. |
| **D9** | First pilot? | **Replay evals first** (screen replay, M01 audit replay, false-kill, scoping), **then one live program: an Adi-sourced algorithm**, driven by Meir, through the algorithm path. | The replay set is almost all use-case hypotheses; the algorithm path is the new, untested one. |
| **D10** | Verdict vocabulary? | **`GO · CONDITIONAL-GO · NO-GO-FINAL · NO-GO-PROVISIONAL · BLOCKED`.** FINAL requires N1–N5. Adi's *"not shown in tested range ≠ shown absent"* is a mandatory field. Advantage *type* (provable / heuristic / practical) and confidence are mandatory for GO / CONDITIONAL-GO. | Merges Adi's S4 categories with Tsahi's provisional-by-default negative standard. |
| **D11** | What happens after a NO-GO? | **Variants + pivot, merged.** ≤5 mined variants (mechanism inversion, one-axis relaxation, salvage classification) + Adi's S6 questions (algorithm tweak, task tweak, sweet spot, paper, patent) with the not-legal-advice + disclosure-order warning. | Tsahi's generators give search directions; Adi's questions capture publication and IP value the lab was leaving on the table. |
| **D12** | Where do things live? *(added in follow-up, same day)* | **Two repos, not three.** `qml_researcher` = system code (skills, agents, criteria, schemas, tools, evals). `qml_artifacts` = all research artifacts, **including every experiment's docs, code, results and small data** under `experiments/<thread>/`. `qml_experiments` is retired (plain copy at a pinned sha, then archived). The experiment folder is the graph entity — `VERDICT.md` frontmatter replaces Experiment Cards and the mirrored source reports. Data > 5 MB is gitignored and re-created by `fetch.py` from a sha256 manifest. Detail: [C11](components/C11_repo_consolidation.md). | The split between an evidence repo and a knowledge repo was the main source of friction: bridge cards, mirrors, cross-repo config, two places to keep in sync. |
| **D13** | Where does the lab live, and how does it fit the researcher? *(follow-up)* | **Inside `qml_researcher`, as a bounded layer.** One user-facing entry point (`/qml-lab`, plus `/qml-intake`); stage skills behind it. System tools stdlib-only in `qml_researcher/lab/`; scientific tools in the experiments venv. Hermes gets an allowlist (status/sign/briefs in Slack; execution local). Seven feedback edges close the loop with the literature skills — verdicts update hypothesis status, the scout and synthesis respect the exclusion ledger, final exclusions propose `qml_domain.md` deprioritizations, transfer cards and actionable hypotheses feed intake. Detail: [C12](components/C12_researcher_integration.md). | Repo already packages "lab practices" and the kill-bad-ideas persona; a separate repo would recreate the friction D12 removed. Risks (skill sprawl, heavy deps, Slack exposure, release pace) are handled by the boundary rules. |

---

## 3. Mapping the proposals onto the settled design

### Adi's stages → components

| Adi | Lands in | Notes |
|---|---|---|
| Overview global rules 1–10, simulation-limits table, glossary | C02 `criteria/lab_method.md` | Loaded by every skill |
| S0 Algorithm understanding + Gate 0 | C04 `/qml-intake` (algorithm path) + `/qml-screen` | Warning table → screen warning boxes; Gate 0 PROCEED/ASK/STOP → screen verdict |
| S1 Experiment design (P1–P5) | C05 `/qml-prereg` | Phases become milestones; hypotheses map + 1.7 gate rules → lock |
| S2 Design review + Gate 2 | C05 `/qml-review-panel` (pass 1) | Adi's checklist is the panel's mandatory floor |
| S3 Execution + Gates 3.1–3.5 | C06 `/qml-run` | Phase report template kept; gate = CP3 |
| S4 Summary go/no-go | C07 `/qml-verdict` | D10 vocabulary |
| S5 Verification | C07 `/qml-audit` | Reproduction subset rule adopted verbatim |
| S6 No-go pivot | C08 `/qml-variants` | D11 |
| `env.md`, `decision_log.md`, `change_log.md` | C01 thread layout | Kept as-is |

### Meir's roles → roles in C03

| Meir (AI) | QML Lab role(s) | V1 |
|---|---|---|
| Senior QML Researcher | `lab-director` + `experiment-designer` | ✓ |
| Junior QML Researcher | `implementer` + drafting for `screen-analyst` (often **Meir himself**) | ✓ |
| Literature & Provenance | Out of lab — routed to existing `/qml-deep-research`, `/qml-paper-review` | reuse |
| QML Experimenter | `implementer` | ✓ |
| Classical ML Adversary | `classical-twin-champion` + panel `baseline-champion` | ✓ |
| Quantum Systems Specialist | panel `hardware-realist` + P4/P5 owner | ✓ (modeling) |
| Peer Reviewer / Math Critic | `review-panel` (5 personas) + `verdict-auditor` | ✓ |
| Memory & Proximity Curator | `lab-archivist` + G0 ledger engagement | ✓ |

| Meir (human) | V1 person |
|---|---|
| Human QML Researcher / Program Owner | Meir (and Tsahi when he runs a program) |
| Principal / Senior Researcher | Adi |
| Lab / Portfolio Manager | Adi (priorities), Tsahi (compute budget) |
| Classical ML / Domain Expert | Tsahi |
| Quantum Hardware Expert | Adi |

### Deferred from Meir's proposal (not rejected)
Platform workflow engine, permission enforcement in code, escalation dashboard UI, portfolio
diversity monitoring, 50+ concurrent programs. Each becomes relevant once W4 (autonomy
step-down) shows the file-based lab converging. The role/permission tables in C03 are written
so a platform can lift them unchanged.

---

## 4. Open questions carried forward

1. **Materials program artifacts are not in the local `qml_experiments` checkout.** The
   pre-registration pattern (`materials_configuration_space/…`) and M01 (eval 2) depend on them.
   Locate before the C11 migration so they land in `qml_artifacts/experiments/` with the rest.
2. **Auditor independence**: different model for `verdict-auditor` where available (the Sept 23
   doc's recommendation) — confirm which second model is available under Hermes.
3. **Adi's pilot algorithm**: which one, and does it arrive as a paper, notes, or code?
4. **Resource-estimation tooling for P5**: Qiskit transpiler + Azure QRE, or a hand model first?
5. ~~Exp 13 missing from the README table~~ — wrong: it is there (earlier view was truncated).
   Migrated with the rest (C11).
6. **Per-thread Python environments** after consolidation: shared
   `experiments/requirements.txt` baseline plus optional per-thread overrides (C11 default).
