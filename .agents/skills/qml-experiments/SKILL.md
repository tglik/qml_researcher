---
name: qml-experiments
version: 2.0.0
description: |
  Direct context and bounded actions on the team's self-run experiments, which live in the
  qml_artifacts vault under `experiments/<thread>/<NN_name>/` (moved there from the retired
  qml_experiments repo on 2026-09-30). Gives research skills and the researcher direct
  context on what has actually been run: questions, verdicts, reproduce commands, and
  whether results are fresh relative to the code that produced them. Also supports three
  bounded actions: check run status, rerun an experiment's own reproduce command (after
  re-creating any large data with data/fetch.py), and make a scoped code change inside one
  experiment's folder. Read-heavy by default — the write/execute actions always show what
  they're about to do and confirm before touching anything. Never writes a verdict: each
  VERDICT.md (and its frontmatter, the experiment's graph entity) is human-authored.
triggers:
  - qml-experiments
  - what closed experiments have we run
  - what have we already measured for <topic>
  - rerun a closed experiment
  - has this closed experiment been rerun since the code changed
  - make a code change in a closed experiment
# Narrowed (docs/lab C12): live lab programs are driven through /qml-lab (status, next, sign);
# this skill is the helper for closed/legacy experiments and supplies /qml-run's rerun mechanics.

input:
  - subcommand: status (default, no slug) | show <slug> | run-status <slug> | rerun <slug> [--yes] | edit <slug> "<change description>"
  - slug: an experiment identifier — program slug (e.g. `recsys-classical-twin`), folder
    name (`04_recsys_classical_twin`), `thread/NN_name` (`spectral_graph/04_recsys_classical_twin`),
    or a plain number if unambiguous across threads. See Slug Resolution.

output:
  - status: one table across every experiment — question, verdict, results freshness,
    uncommitted-changes flag, and whether VERDICT.md has entity frontmatter
  - show: the experiment's README.md + VERDICT.md content (frontmatter included) and its git log
  - run-status: a freshness/staleness diagnosis for one experiment — no execution
  - rerun: the reproduce command that was run, a saved log, and a before/after diff of
    results/ — never a verdict, never a commit
  - edit: a git diff of a scoped code change inside one experiment's folder — never a commit

allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
  - Edit
  - Write
  - AskUserQuestion
---

# /qml-experiments

Direct, read-first context into the team's experiments (`{output_root}/experiments/`), plus
three bounded actions: check whether a run is stale, rerun it, or make a scoped code edit.
This skill never writes a `VERDICT.md` or any file outside the one experiment folder it was
asked about.

---

## Why this exists

`{output_root}/experiments/` is where the team's own falsifiable experiments live — code,
results, figures, small data, and a hand-written `VERDICT.md` per experiment whose
frontmatter is the experiment's entity in the knowledge graph (see
`artifacts/lab/experiment_entity_schema.md`). This skill reads what is actually there right
now and takes small, confirmed actions in it without pretending to replace the human
verdict-writing step.

---

## Setup

Read `config/workspace.json` → CONFIG.

```
ARTIFACTS_ROOT   = resolve(CONFIG.output_root)
EXPERIMENTS_ROOT = ARTIFACTS_ROOT / "experiments"
```

If `EXPERIMENTS_ROOT` does not exist on disk, stop:
```
Error: {EXPERIMENTS_ROOT} does not exist. Experiments live in the qml_artifacts vault under
experiments/ — check output_root in config/workspace.json (a per-machine path).
```

Git commands run in `ARTIFACTS_ROOT` (the vault is the git repo). If it isn't a git repo,
warn but proceed — git-derived fields (freshness, uncommitted changes) are reported as "unknown".

---

## Folder shape (recap — inline so this skill doesn't depend on experiments/README.md staying in this exact form)

```
{EXPERIMENTS_ROOT}/                  = {output_root}/experiments/
├── README.md                        index: table of every experiment, question, verdict
├── requirements.txt / .venv/        shared Python env (.venv gitignored)
└── <thread>/                        e.g. boosting_trees/, spectral_graph/, fraud_aml/
    ├── EXPERIMENT_INDEX.md          narrative walkthrough of the thread (thread-level, not per-experiment)
    ├── INSIGHTS.md                  cross-experiment takeaways (thread-level)
    └── NN_short_name/               one experiment
        ├── README.md                question, design, key result, Reproduce section
        ├── VERDICT.md               frontmatter (graph entity) + full write-up (human-authored)
        ├── src/                     code
        ├── data/                    manifest.json + fetch.py; files > 5 MB gitignored
        ├── results/                 tables / raw metric dumps
        └── figures/
```

The **`README.md`** at `{EXPERIMENTS_ROOT}` already contains a per-thread table (# | folder | question | verdict)
that is the cheapest, most authoritative status source — read it first in every mode below
rather than re-deriving verdicts from each experiment's files.

---

## Slug Resolution

Given a user-supplied slug, find exactly one experiment folder:

1. Glob `{EXPERIMENTS_ROOT}/*/*/README.md` → candidate folders (thread/NN_name).
2. Normalize the input and each candidate's `NN_name` the same way: lowercase, strip a
   leading numeric prefix + underscore, replace `_` with `-` (e.g. `04_recsys_classical_twin`
   → `recsys-classical-twin`).
3. Match, in order, against: exact `thread/NN_name` path → exact normalized slug → normalized
   slug substring → bare number (`04`, `4`) against `NN_name`'s prefix.
4. Zero matches → stop and print the full candidate list (thread + folder + question, one
   line each) so the user can pick a real one.
5. More than one match → use `AskUserQuestion` listing the matches (thread, folder, question)
   — never guess silently across threads.

---

## Mode: `status` (default — no slug given)

1. Read `{EXPERIMENTS_ROOT}/README.md`. Extract the per-thread tables (# | folder | question | verdict).
2. For each row, resolve the folder and compute, cheaply:
   - **Results freshness**: compare the newest mtime under `results/` (if it exists) to the
     newest mtime under `src/`. Label: `fresh` (results newer than src) | `stale — src changed
     after results` | `no results/ yet`.
   - **Uncommitted changes**: `git status --porcelain -- {folder}` in `ARTIFACTS_ROOT` →
     `clean` | `dirty (N files)`.
   - **Entity state**: does `{folder}/VERDICT.md` start with frontmatter containing `id` and
     `verdict`? → `entity` | `no frontmatter` | `no VERDICT.md`.
3. Print one table, columns: `#  Thread  Question (truncated)  Verdict  Freshness  Git  Entity`.
4. Below the table, call out anything that needs attention:
   ```
   ⚠ Stale results (code changed since last run): {list}
   ⚠ Uncommitted changes: {list}
   ⚠ VERDICT.md without entity frontmatter: {list} — add it per
     artifacts/lab/experiment_entity_schema.md so the registry and topic map can link it
   ```
   Omit any section with nothing to report.

---

## Mode: `show <slug>`

1. Resolve `slug` → `{thread}/{folder}`.
2. Print, in order:
   - Path, thread table row (question + verdict from experiments/README.md)
   - Full contents of `{folder}/README.md`
   - Full contents of `{folder}/VERDICT.md` if it exists, else note it's missing — flag
     explicitly if its frontmatter `verdict` disagrees with the README table's verdict text
   - `git log --oneline -5 -- {folder}` (last 5 commits touching this experiment)

---

## Mode: `run-status <slug>`

Diagnostic only — never executes anything.

1. Resolve `slug` → folder.
2. Report:
   - `git log -1 --format='%h %ad %s' --date=short -- {folder}/src` (last src change)
   - `git log -1 --format='%h %ad %s' --date=short -- {folder}/results` (last results change,
     if `results/` is tracked — many are gitignored, so also report `results/` mtime directly)
   - Freshness verdict (same rule as `status` mode, but list the specific newer files, not
     just the label)
   - `git status --porcelain -- {folder}` (uncommitted changes, listed)
   - Whether `VERDICT.md`'s mtime predates the newest file under `results/` — if so, flag:
     "results/ has changed since VERDICT.md was last edited; the written verdict may not
     reflect the current numbers."
3. End with a one-line recommendation: `rerun recommended` | `up to date` | `verdict may be stale — human review needed` (never both "rerun" and "verdict is fine" — staleness in results and staleness in the verdict text are reported separately, since only a human can judge whether new numbers change the verdict).

---

## Mode: `rerun <slug> [--yes]`

1. Resolve `slug` → folder.
2. Read `{folder}/README.md`, find the `## Reproduce` section (fall back to `## Setup` if
   no `Reproduce` heading exists). Extract the exact shell command(s).
3. If no reproduce/setup command is found in the README, stop:
   ```
   No Reproduce section found in {folder}/README.md — nothing to run automatically.
   Read the file and run the pipeline manually, or add a Reproduce section first.
   ```
4. Print, before doing anything:
   ```
   About to run in {EXPERIMENTS_ROOT}/{thread}/{folder}:
     {command(s), verbatim}
   Current git status: {clean | dirty (N files) — results will reflect these uncommitted changes}
   ```
5. **Confirm before executing.** Unless `--yes` was explicitly passed, ask via
   `AskUserQuestion` (prose confirmation if AskUserQuestion isn't available in this CLI) —
   this can be a long-running job (see the multi-hour sweep logs already in
   `boosting_trees/01_boosting_split_headroom/`) and it will overwrite `results/`.
6. On confirmation: activate the shared venv (`source {EXPERIMENTS_ROOT}/.venv/bin/activate`,
   falling back to an experiment-local `.venv` if the folder has its own). If
   `{folder}/data/fetch.py` exists, run `python data/fetch.py --verify` first — it re-creates
   gitignored large files and checks their sha256 against `data/manifest.json`; stop on a
   mismatch. Then `cd` into the experiment folder, run the command(s), teeing output to
   `{folder}/rerun_{YYYYMMDD-HHMMSS}.log` (same naming pattern as the existing `*_sweep.log`
   files in `01_boosting_split_headroom` — gitignored, so this matches repo convention).
7. Report: exit code, tail of the log, and `git status --porcelain -- {folder}/results`
   (what actually changed on disk).
8. Always close with:
   ```
   This did not update VERDICT.md (or its frontmatter) or the experiments/README.md table —
   those are human-authored. If these numbers materially change the verdict, update
   VERDICT.md by hand.
   ```
9. Never commit or push in the vault from this skill. Its git history is the user's to
   manage, same as this repo's own commit policy.

---

## Mode: `edit <slug> "<change description>"`

1. Resolve `slug` → folder.
2. List `{folder}/src/` and read the file(s) relevant to the change description.
3. **Scope guard** — only files under `{folder}/` may be touched (its own `src/`, and its
   `README.md` if the change is documentation-only). If the request implies a change to a
   thread-level file (`EXPERIMENT_INDEX.md`, `INSIGHTS.md`, `spectral_graph/README.md`) or
   to another experiment, stop and say so explicitly:
   ```
   "{description}" implies a change outside {folder}/ ({thread-level file or other
   experiment}). That affects the thread's shared narrative — needs a human decision, not
   a single-experiment edit. Scoping this edit to {folder}/ only; make the rest by hand.
   ```
4. Make the edit with `Edit`/`Write`, scoped as above.
5. Show `git diff -- {folder}`.
6. Do not commit. Do not automatically rerun — tell the user: `Run /qml-experiments rerun
   {slug} to see the effect of this change.`

---

## Failure Modes to Avoid

```
❌ Committing a data file > 5 MB — list it in data/manifest.json as untracked and make
   data/fetch.py re-create it instead
❌ Auto-committing or auto-pushing in the vault — human decides when
❌ Rerunning without printing the exact command and getting confirmation first — these can
   be long, real compute jobs that overwrite results/
❌ Treating a rerun's fresh numbers as an updated verdict — VERDICT.md and claim_status are
   human-authored; a rerun produces new numbers, not a new verdict
❌ Writing or editing VERDICT.md or its frontmatter from this skill — human-authored
❌ Editing thread-level files (EXPERIMENT_INDEX.md, INSIGHTS.md, thread README.md) under an
   edit request scoped to one experiment
❌ Guessing the vault path instead of reading output_root from config/workspace.json
❌ Silently picking one match when a slug is ambiguous across threads — ask
```
