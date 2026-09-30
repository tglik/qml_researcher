# C11 — Repository consolidation: experiments move into `qml_artifacts`

## Purpose
End the split between `qml_experiments` (code/data/verdicts) and `qml_artifacts` (knowledge
graph). The split forced a bridge layer — mirrored source reports, Experiment Cards,
`experiments_root` config, the `/qml-experiments` cross-repo skill — and every program had to
be kept in sync across two repos. After this change (D12):

| Repo | Holds |
|---|---|
| `qml_researcher` | **System code** — skills, agents, criteria, schemas, `lab/tools/` tools, evals, docs |
| `qml_artifacts` | **All research artifacts** — literature cards and sources (as today) **plus** every experiment: docs, code, results, figures, small data |
| `qml_experiments` | **Retired** — archived read-only with a pointer README; no skill reads or writes it |

The experiment folder becomes the graph entity: its `VERDICT.md` frontmatter replaces the
Experiment Card, and there is no mirrored source report.

## Owner role(s) and human touchpoints
Tsahi executes the migration (W0). Adi spot-checks 3 migrated experiments (rendering + one
rerun). Meir and Adi pull the new layout before the pilot.

## Inputs / outputs
Input: `qml_experiments` at a pinned commit sha; 13 cards in `qml_artifacts/cards/experiments/`;
13 mirrors in `qml_artifacts/sources/reports/experiments/`.
Output:
```
qml_artifacts/
  experiments/
    README.md                         index (replaces qml_experiments/README.md tables)
    requirements.txt                  shared baseline env; per-thread overrides allowed
    boosting_trees/01_boosting_split_headroom/ …
    spectral_graph/{03..11}_*/ + INSIGHTS.md, README.md, EXPERIMENT_INDEX.md, figures/
    fraud_aml/{12,13}_*/ + README.md
    <new lab threads>/                C01 layout
  indexes/experiment-registry.md      rebuilt from VERDICT frontmatter
  indexes/exclusion-ledger.md         (C02)
```

## Artifact schemas

### `VERDICT.md` frontmatter — the experiment entity (replaces `experiment_card_schema.md`)
```yaml
---
id: recsys-classical-twin                  # kept identical to the old card slug
type: experiment
aliases: [cards/experiments/recsys-classical-twin]   # keeps all 133 old wiki-links resolving in Quartz
title: "Recsys Classical Twin — does a classical machine reproduce the QSVT pipeline's cost?"
thread: spectral_graph
experiment_number: "04"
program: idea1-synthetic-prior-spectral-filtering-recsys
topics: [graph-ml, recommendation, dequantization]
verdict: NO-GO-PROVISIONAL                 # D10 vocabulary; legacy values mapped below
claim_status: observed
evaluated: 2026-07-29
audit: legacy-human                        # CONFIRMED | OVERTURNED | INSUFFICIENT | legacy-human
ledger: [polylog-pauli-graph-hamiltonian-recsys-ranking]
related: [[experiments/spectral_graph/06_node_correspondence_realdata/VERDICT]]
---
```
The card's body sections that are not already in the verdict (key numbers table, "links into
the graph") move into a `## Graph links` section at the end of `VERDICT.md`.

Legacy verdict mapping: `CLOSED_NO` → `NO-GO-FINAL` only if N1–N5 hold on re-read, otherwise
`NO-GO-PROVISIONAL`; `PROVISIONAL` → `NO-GO-PROVISIONAL`; `GO`/`CLOSED_YES` → `GO`. The
re-read is done during ledger seeding (C02), not guessed during the copy.

### Data policy (per experiment)
```
<experiment>/data/
  manifest.json      [{"path": "yelp2018/train.txt", "sha256": "…", "bytes": 6905856,
                       "source": "https://…", "fetch": "fetch.py#yelp2018", "tracked": false}]
  fetch.py           re-creates every untracked file and verifies sha256
  <small files>      committed when ≤ 5 MB each
```
- Committed: code, `results/` tables, `figures/`, markdown, data files ≤ 5 MB.
- Gitignored: data > 5 MB, caches (`openml_cache/`, `*.pkl` checkpoints), `.venv/`, logs.
- `provenance.json` (C01) records the same sha256, so an audit rerun (C07) calls `fetch.py`
  and fails loudly on a hash mismatch.

### Quartz publishing
Add to `qml-quartz/quartz.config.yaml` `ignorePatterns`:
`experiments/**/src/**`, `experiments/**/data/**`, `experiments/**/raw/**`,
`experiments/**/.venv/**`, `experiments/**/*.log`. Markdown (README, HYPOTHESIS, SCREEN,
PROPOSAL, PHASE_REPORT, PANEL, VERDICT, AUDIT, VARIANTS) and `figures/` are published.

## Procedure — migration (plain copy, one reviewed PR)
| Step | Work | Pass/fail |
|---|---|---|
| 1 Pin | Record `qml_experiments` HEAD sha; confirm clean tree; locate `materials_configuration_space` and include it if found | sha recorded |
| 2 Copy | Copy tracked files (`git ls-files`) into `qml_artifacts/experiments/`, **normalizing the layout**: the stray top-level `experiments/0N_*` folders are merged into their thread folders (`boosting_trees/`, `spectral_graph/`) | Every tracked file accounted for (script diff) |
| 3 Data split | For each file > 5 MB: move to gitignore, write manifest entry + fetch function, verify fetch reproduces sha | `fetch.py --verify` green for all 13 |
| 4 Entity frontmatter | Convert each card's frontmatter into `VERDICT.md` frontmatter (script), add `aliases`, append card-only body content as `## Graph links` | 13/13 converted |
| 5 Remove bridges | Delete `cards/experiments/*.md` and `sources/reports/experiments/*.md` | Quartz build has 0 broken links |
| 6 Indexes | Rebuild `experiment-registry.md` and topic-map experiment rows from VERDICT frontmatter (`lab/tools/registry.py`) | Registry lists 13 (+ materials) |
| 7 Quartz | Add ignorePatterns; build | Verdict pages render with figures; no `.py` / data pages |
| 8 Rerun check | Rerun 2 experiments' reproduce commands from the new location (one with fetched data) | Results match committed `results/` |
| 9 Archive | Commit a pointer `README.md` in `qml_experiments` ("moved to qml_artifacts/experiments at <sha>"), archive the GitHub repo read-only | Archived |

Commit message of the copy names the source sha — that is the history link (D12: plain copy).

### `qml_researcher` changes (same PR window)
| File | Change |
|---|---|
| `config/workspace.json` | Remove `experiments_root`; experiments resolve as `{output_root}/experiments` |
| `.agents/skills/qml-experiments/` | Repoint to `{output_root}/experiments`; drop card-extraction-state reporting; keep status / show / run-status / rerun / edit (reused by `/qml-run`, C06) |
| `artifacts/experiment_card_schema.md` | Retire → replaced by `artifacts/lab/experiment_entity_schema.md` (the frontmatter above) |
| `.agents/skills/extract-artifacts/agents/{source-classifier,entity-extractor}.md` | Remove the `experiment-report` source type and experiment-card path |
| `AGENTS.md`, `README.md`, `SOUL.md` | Replace the two-repo description with the single-vault one |
| `qml_artifacts/README.md`, `index.md` | Same |

## Checkpoints and autonomy
One-time human review: the migration PR is merged by a human (CP5-class change).

## Separation / permission rules
Migration scripts are deterministic and live in `qml_researcher/scripts/lab/migrate/`; the
agent does not hand-edit 13 verdicts. After migration, skills write inside
`experiments/<thread>/` only on that program's branch (D8); ledger / registry / criteria files
change only at promotion.

## Failure modes and controls
| Failure | Control |
|---|---|
| Broken wiki-links after deleting cards | `aliases` in VERDICT frontmatter; Quartz build link check |
| Vault bloat / Quartz publishes code or data | 5 MB rule + ignorePatterns + a pre-commit size check (`lab/tools/check_sizes.py`) |
| Lost reproducibility for large data | `manifest.json` + `fetch.py --verify`; rerun check in step 8 |
| History lost (plain copy) | Source sha in the copy commit; archived repo stays readable |
| Obsidian/Quartz slowed by many code files | ignorePatterns; `.obsidian` excluded folders list updated |

## Evals that cover it
C10 eval fixtures now read legacy experiments from `qml_artifacts/experiments/` (time-sliced by
`evaluated` date in frontmatter). Structural check: every `VERDICT.md` has valid entity
frontmatter.

## Build tasks
- [ ] `scripts/lab/migrate/copy_experiments.py` (layout normalization + accounting diff) (S)
- [ ] `scripts/lab/migrate/split_data.py` (manifest + fetch stubs) + per-experiment fetch functions (M, 1 day)
- [ ] `scripts/lab/migrate/cards_to_frontmatter.py` (S)
- [ ] `lab/tools/registry.py` (S)
- [ ] `lab/tools/check_sizes.py` pre-commit (S)
- [ ] Quartz ignorePatterns + build check (S)
- [ ] `qml_researcher` reference updates (table above) (S)
- [ ] Archive `qml_experiments` (S)
Total ≈ 2–3 days, in W0 before ledger seeding (the ledger's `verdict_ref` paths use the new
location).

## Acceptance criteria
Quartz builds with 0 broken links; 13 verdict pages render with figures and no code pages;
`fetch.py --verify` green for all; 2 reruns reproduce committed results; no file in
`qml_researcher` references `qml_experiments` except this doc and the office-hours record.

## Execution log (2026-09-30)

Run on branches `migrate/experiments-into-vault` (qml_artifacts), `lab/c11-consolidation`
(qml_researcher), `archive/moved-to-qml-artifacts` (qml_experiments) — **nothing committed yet**.

| Step | Result |
|---|---|
| 1 Pin | `qml_experiments` @ `8158aa0`, clean. Materials program **not found** anywhere locally or in history — not migrated. |
| 2 Copy | 389 tracked → 387 copied, 2 left behind (`.gitignore`; `scripts/make_docx.py` → moved to `qml_researcher/scripts/`). 14 relocated: 12 stray top-level data files into `spectral_graph/{03,07}_*/data/`, plus root README/requirements into `experiments/`. |
| 3 Data split | 4 files > 5 MB gitignored (amazon-book `train.txt` + `cache.npz`, yelp2018 `train.txt`, `com-youtube.ungraph.txt.gz`). Manifests written for all 6 data dirs. `fetch.py` for exps 03 and 07; verified by deleting the 4 files and re-fetching: all sha256 match; rebuilt `cache.npz` array-identical. Local `data/.gitignore` in 03/07 (which ignored all data — those files were only tracked because they sat in the stray folder) reduced to a pointer at the central 5 MB rule. |
| 4–5 Entity + bridges | 13 cards folded into `VERDICT.md` frontmatter with `aliases`; card-only sections kept under `## Graph links`; 13 cards + 13 mirrors deleted; links rewritten in registry and topic map (table cells escape `\|`). `scripts/templates/experiment-report.md` retired. |
| 6 Indexes | Registry/topic-map links rewritten in place; `registry.py` generator **deferred** to W1 (`/qml-promote`) — the current registry has hand-written program narrative a generator would clobber. |
| 7 Quartz | ignorePatterns added (src, data, raw, .venv, logs, `*.py`, `*.sh`, `_metadoc_tmp`, `*.npz`, `*.parquet`). Build OK; 13 `cards/experiments/<slug>` URLs redirect to the verdicts; registry 13/13, topic map 14/14 links resolve. **Known gap:** relative markdown links inside experiment READMEs (`[x](VERDICT.md)`, `(../03_…)`) don't resolve under `markdownLinkResolution: shortest` — same pre-existing behavior as other relative links in the vault. |
| 8 Reruns | Shared venv at `experiments/.venv` from `requirements.txt`. **Exp 13**: byte-identical `rare_event.json`. **Exp 07** on re-fetched `com-youtube`: λ₂ agrees to 1e-14, all fit values match; committed row was run with `--maxiter 8000` (script default 6000) — undocumented in the README. **Exp 04** (gowalla, seeded, same numpy/scipy): within 0.3% but not bit-exact (NDCG 0.8925 → 0.8922, Jaccard 0.527 → 0.529); cause not determined. Committed results restored after each rerun. |
| qml_researcher | `experiments_root` removed; `/qml-experiments` v2.0 points at `{output_root}/experiments` and runs `fetch.py --verify` before reruns; `/extract-artifacts` rejects `experiment-report` sources; `experiment_card_schema.md` → `artifacts/lab/experiment_entity_schema.md`; AGENTS / SOUL / README describe the two-repo layout. |
| 9 Archive | Retirement banner added to `qml_experiments/README.md` (uncommitted). GitHub archive **not done** — needs the owner. |

Deferred: `registry.py`, `check_sizes.py` pre-commit hook, Quartz relative-link fix, D10 mapping of
legacy verdict values (happens in ledger seeding).

## Open questions
- Materials program — include in the copy if located, else it lands later directly in the new layout.
- Per-thread venvs vs one shared `experiments/requirements.txt`? Default: shared baseline +
  optional per-thread `requirements.txt`.
