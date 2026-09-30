# C12 — Researcher integration: one research loop, two halves

## Purpose
Decide how the lab lives inside `qml_researcher` (D13) and close the loop between the
literature half (exists) and the lab half (new). Without this component the lab is a
separate pipeline bolted on: the scout keeps surfacing directions the lab already killed,
hypothesis cards never learn what was measured, and 10 new skills compete with 9 existing
ones for the same triggers.

```
literature half (exists)                      lab half (new)
qml-daily-scout ──► triage
qml-paper-review ─► paper cards  ─┐
qml-deep-research ─► reports     ─┼─► candidate ──► /qml-intake ─► screen ─► … ─► verdict ─► audit
qml-primitive-transfer ─► cards  ─┤   direction                                              │
synthesize-hypotheses ─► hyp cards┘                                                          ▼
        ▲                                                                              /qml-promote
        └── exclusion ledger · hypothesis status · criteria deprioritizations · variant cards ◄┘
```

## Owner role(s) and human touchpoints
Tsahi (system engineer) owns the boundary rules and the edits to existing literature skills.
Humans see the integration mostly as: fewer dead directions in the daily scout, hypothesis
cards that show experimental status, and lab decision briefs arriving in Slack (Hermes).

## Inputs / outputs
Changes to existing files in `qml_researcher` (literature skills, SOUL, installer, criteria)
and to `qml_artifacts` indexes (hypothesis ledger). No new artifacts beyond C01's.

## Artifact schemas

### Boundary rules (D13) — how the lab sits inside the repo
| Rule | Detail |
|---|---|
| **One user-facing entry point** | `/qml-lab` (`new · next · status · sign · escalate · amend · stats`) and `/qml-intake` (interactive) are the only lab skills with broad triggers. Stage skills (`qml-screen`, `qml-prereg`, `qml-review-panel`, `qml-run`, `qml-verdict`, `qml-audit`, `qml-variants`, `qml-promote`) get narrow, explicit triggers and are normally reached through `/qml-lab next`; each still works standalone for debugging. |
| **`/qml-experiments` becomes a lab helper** | Kept for status / rerun / edit of legacy experiments; `/qml-run` calls its rerun mechanics. Its triggers are narrowed to "legacy / closed experiments" so it doesn't compete with `/qml-lab status`. |
| **Two tool tiers** | *System tools* — `lock`, `validate`, `guard`, `provenance`, `splits`, `gates`, `autonomy`, `registry`, `check_sizes` — live in `qml_researcher/lab/` (a small Python package), **stdlib only**, so the skills plugin stays light and installable anywhere. *Scientific tools* — `fit_scaling` (numpy/scipy), `sim_budget`, `resource_est` (qiskit) — live in `qml_artifacts/experiments/_lab_tools/` and run in `experiments/.venv`, next to the code they measure. |
| **Hermes allowlist** | `scripts/install_hermes_skills.py` gets an explicit allowlist instead of installing everything. Slack gets `/qml-lab` (`status`, `sign`, decision briefs, escalations) and `/qml-intake` (async interrogation). `run`, `prereg`, `audit`, `verdict` stay local (Claude Code) — they need compute, a git checkout and long sessions. |
| **Lab versioning** | Lab skills share one `lab_version` (in `config/lab_autonomy.json`). Lab evals (C10) gate lab changes; existing literature evals gate literature changes; neither suite blocks the other. |
| **One scientist, many hats** | `SOUL.md` gains a short "The lab" section: the lab roles are hats worn by the same scientist and share its values; independence between hats comes from fresh contexts, artifact-only handoffs and mechanical checks, not from different personas. Role agent defs (C03) still inject the role's mandate and *may-not* list. |

### Integration points (the feedback edges)
| # | Edge | From → to | Change |
|---|---|---|---|
| **I1** | Hypothesis status from verdicts | `/qml-promote` → `cards/hypotheses/*` + `indexes/hypothesis-ledger.md` | When a program's `HYPOTHESIS.md` names a hypothesis card as its source, promotion updates that card's `status` on the claim ladder (verdict GO/CONDITIONAL-GO → `observed`; NO-GO-FINAL → `refuted`; NO-GO-PROVISIONAL → unchanged + note) and appends a Status History row `{date, from, to, "experiment: [[experiments/…/VERDICT]]"}`. Ceiling stays `observed` for a single experiment (existing schema rule). |
| **I2** | Ledger read by the scout | `indexes/exclusion-ledger.md` → `qml-daily-scout` "Skeptical QML filter" | A paper whose direction falls inside an active `final` exclusion is down-ranked and tagged `⛔ excluded: <ledger id>` with the one-line mechanism; `provisional` → tagged `⚠ provisional exclusion`, not down-ranked. A paper that argues against the exclusion's mechanism is **up-ranked** and flagged — it is exactly the "evidence of type X" that reopens an entry. |
| **I3** | Ledger engaged by hypothesis synthesis | ledger → `synthesize-hypotheses` Phase 2 (pattern detection) | Candidate hypotheses are checked against the ledger by mechanism (same G0 rule: "different words" is not different). A candidate that falls inside a `final` exclusion is not written; inside a `provisional` one it is written with `strategic_value: incremental` and a link to the entry. |
| **I4** | Deep research as a lab service | `/qml-screen` → `/qml-deep-research` | On "literature contradicts hypothesis" or "novelty unclear", the screen writes a scoped question to `00_inputs/research_request.md` and invokes deep-research with `--return-to <thread>`; the report path is recorded in `SCREEN.md` and the screen resumes. Replaces the C03 escalation-to-Tsahi for this trigger. |
| **I5** | Transfer cards and actionable hypotheses as intake input | `sources/reports/{transfer-analysis,primitives-analysis}/*/04_transfer_card.md`, `cards/hypotheses/*` (`strategic_value: actionable`) → `/qml-intake` | Intake accepts either by path. Field mapping: transfer card *Top Opportunities* row → claim + operating point draft; *Equivalent Problem Map* → classical-twin candidates for the screen; hypothesis card *Hypothesis Statement* → claim, *Open Risks* → kill-criteria draft, *Promotion Criteria* → disproof sentence draft. Interrogation still runs — the mapping pre-fills, it never skips the 5/5 checklist. `/qml-lab status` lists actionable hypotheses with no program as the backlog. |
| **I6** | One criteria stack | `/qml-promote` → `criteria/qml_domain.md` "Deprioritized Directions" | Every new `final` ledger entry proposes (in the promote PR description) a matching one-line entry in `qml_domain.md`'s *Deprioritized Directions (Do Not Re-Suggest Without New Evidence)* section, linking the ledger id — so paper-review and deep-research, which load `qml_domain.md`, inherit the exclusion without reading the ledger. `lab_method.md` and `qml_domain.md` cross-reference each other in their headers. |
| **I7** | Verdicts visible to literature skills | `experiments/**/VERDICT.md` frontmatter → `qml-paper-review`, `qml-deep-research` context loaders | These skills already load cards by topic; add experiment entities (by `topics`) to the same load, so a paper on a direction we measured is reviewed with our own number beside it. |

## Procedure
Build order (cheapest, highest-value first):
1. **W1 (with intake/screen):** boundary rules in the README "Lab" section; Hermes allowlist;
   narrowed `/qml-experiments` triggers; `lab/` package skeleton (stdlib). *Pass:* Hermes
   profile lists only allowlisted skills; `python -c "import lab"` works with no third-party packages.
2. **W1:** I2 (scout reads ledger) and I6 (deprioritization proposals) — both valuable the
   day the seeded ledger exists, before any executor. *Pass:* a scout run over a fixture
   containing one paper per seeded exclusion tags all of them; one "counter-mechanism"
   fixture paper is up-ranked.
3. **W1:** I5 (intake accepts transfer/hypothesis cards). *Pass:* intake on one existing
   actionable hypothesis card pre-fills ≥3 of 5 checklist items and still asks for the rest.
4. **W2:** I1 (hypothesis status from verdicts), I3 (synthesis engages ledger), I7 (literature
   skills load verdicts). *Pass:* promote on a replayed program updates its hypothesis card
   and ledger row; synthesize-hypotheses rerun on existing paper cards writes no hypothesis
   inside a `final` exclusion.
5. **W3:** I4 (deep research as a lab service), SOUL "The lab" section.

## Checkpoints and autonomy
No new checkpoints. I1 and I6 ride on **CP5** (promotion PR, permanent human approval) — a
verdict never silently rewrites a hypothesis card or the domain criteria.

## Separation / permission rules
- Literature skills **read** the ledger and verdict entities; they never write them.
- Only `/qml-promote` writes hypothesis status changes caused by experiments.
- `qml_domain.md` changes stay human commits; the lab only proposes.

## Failure modes and controls
| Failure | Control |
|---|---|
| Scout over-prunes a direction because an exclusion is topic-scoped | Exclusions are mechanism-scoped (C02); scout tags rather than drops; counter-mechanism papers are up-ranked |
| Trigger collisions misroute a request | One broad entry point; narrow stage triggers; C10 structural check that no two lab skills share a trigger phrase |
| Heavy deps leak into the skills plugin | Two tool tiers; `lab/` import test in CI with no third-party packages |
| Slack user starts a multi-hour run | Hermes allowlist excludes `run`/`prereg`/`audit`/`verdict` |
| A NO-GO silently kills a hypothesis card | Status change only via promote PR (CP5); PROVISIONAL leaves status unchanged |

## Evals that cover it
- **I2 scout fixture** (above) — added to `/test-skills` cases for `qml-daily-scout`.
- **I3 synthesis replay** — rerun on current paper cards; count hypotheses written inside `final` exclusions (must be 0).
- **I5 intake pre-fill** — part of C10 eval 4 fixtures.
- Structural: trigger-uniqueness check across all skills.

## Build tasks
- [ ] README "Lab" section + boundary rules (S)
- [ ] `install_hermes_skills.py` allowlist (S)
- [ ] `lab/` package skeleton + import test (S)
- [ ] `qml-daily-scout` ledger step (S, ½ day) — I2
- [ ] `/qml-promote` deprioritization proposal + hypothesis status update (in C08 tasks) — I1, I6
- [ ] `synthesize-hypotheses` Phase 2 ledger engagement (S) — I3
- [ ] `/qml-intake` card mapping (in C04 tasks) — I5
- [ ] paper-review / deep-research load verdict entities by topic (S) — I7
- [ ] deep-research `--return-to` hook (S) — I4
- [ ] `SOUL.md` "The lab" section (S)

## Acceptance criteria
All seven edges have a passing check; Hermes exposes only the allowlist; the literature eval
suite shows no regression after I2/I3/I7 edits.

## Open questions
- Should `strategic_value: actionable` hypotheses auto-open a program (`/qml-lab new`) or only
  appear in the backlog? Default: backlog only — opening a program is a human decision.
- Does the ledger eventually replace `qml_domain.md`'s Deprioritized Directions section? Default:
  no — the section stays the human-curated summary; the ledger is the evidence-backed detail.
