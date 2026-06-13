---
name: test-skills
version: 1.0.0
description: |
  Quality evaluation harness for qml-researcher skills. Scores output artifacts
  on skill-specific axes (0–5 each), computes a combined weighted score, and
  reports regressions against committed baselines.

  Two primary modes:
    --eval {workspace}  Evaluate artifacts from a completed skill run (common daily use)
    --run               Spawn the skill with a test fixture, then evaluate (full regression CI)

  Use --eval after any skill run to grade output quality. Use --run to reproduce
  a known test case end-to-end and detect regressions.

triggers:
  - test skills
  - evaluate skill quality
  - grade this run
  - run skill tests
  - check skill regression
  - how good was that last run

input:
  - --eval {workspace_path}: path to a completed skill workspace to evaluate
  - --case {id}: which test case to apply (e.g. qml-paper-review/full-strong-paper)
  - --skill {name}: filter --run to one skill; or auto-detect from --eval workspace
  - --run: execute skill with test fixture, then evaluate (expensive)
  - --fast: with --run, skip full-mode cases (use fast/fact-check variants only)
  - --accept-baseline {test_id}: write current scores as new baseline (commit afterward)
  - --list: list available test cases and their current baseline scores

output:
  - Score card JSON per test case: tests/reports/{run-id}/{test-id}.scores.json
  - Regression report (Hermes-formatted text)
  - Updated baseline files (--accept-baseline only)

allowed-tools:
  - Agent
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - AskUserQuestion
---

# /test-skills

Skill output artifacts → quality scored on axis rubrics → regression delta vs committed baseline → report.

> **Infrastructure:** Read `.agents/shared/protocol.md` once during Setup for the Agent Spawn
> Convention and progress format. Apply throughout.

---

## Hermes Platform Notes

- Use `clarify` instead of `AskUserQuestion` for mode disambiguation.
- Progress updates go to the current DM/thread. Emit one update after each test case scores.
- Do NOT use `execute_code` for file reads/writes — use Hermes file tools.

---

## Iron Rules

```
❌ Do NOT reuse the evaluator agent instance across test cases — spawn fresh per case
❌ Do NOT let the evaluator read or be influenced by baseline scores during scoring
❌ Do NOT mark a regression unless combined_score delta ≥ thresholds defined in test case YAML
❌ Do NOT use --run on full-mode deep-research cases without explicit user confirmation (expensive)
❌ Do NOT fabricate scores — every axis score must cite a specific artifact line or file state
```

---

## Setup

```
Read: config/workspace.json → CONFIG
OUTPUT_ROOT    = resolve(CONFIG.output_root)
ANALYTICS_PATH = CONFIG.analytics_folder + "/events.jsonl"
TESTS_ROOT     = {repo_root}/tests
RUN_ID         = "ts-{YYYYMMDD-HHMMSS}"
REPORTS_DIR    = {TESTS_ROOT}/reports/{RUN_ID}/
```

**Analytics — write start event** (append to ANALYTICS_PATH):
```json
{"ts":"{ISO_NOW}","run_id":"{RUN_ID}","event":"skill_start","skill":"test-skills","version":"1.0.0","mode":"{mode}","input_summary":"{flags}"}
```

Read `.agents/shared/protocol.md` — load Agent Spawn Convention into context.

---

## Phase 0 — Mode Detection + Test Case Loading

### 0.1 Detect mode

| Flags present | Mode |
|---|---|
| `--list` | list → print cases, stop |
| `--eval {path}` | eval → go to Phase 2 |
| `--run` | run → Phase 1 then Phase 2 |
| `--accept-baseline {id}` | accept → Phase 4 only |
| None | interactive → ask once |

If mode is ambiguous, ask:
> What would you like to do?
> A) Evaluate a completed workspace (paste the workspace path)
> B) Run a skill against a test fixture end-to-end
> C) List available test cases

### 0.2 Load test cases

Scan `{TESTS_ROOT}/cases/**/*.yaml`. For each file:
- Read YAML frontmatter: `id`, `skill`, `mode`, `description`
- Build `TEST_CASES[]`

Apply filters:
- `--skill {name}` → keep cases where `skill == name`
- `--case {id}` → keep cases where `id == given`
- `--fast` (with `--run`) → keep cases where `mode != full` (fast, fact-check, lit-review only)

### 0.3 --list mode

Print:
```
Available test cases ({N} total):
  qml-paper-review/full-strong-paper  — full review of Danaci 2605.21346 [baseline: {combined}/5 or "no baseline"]
  qml-paper-review/fast-mode          — fast review of Liu biomedical [baseline: ...]
  ...
```
Stop.

---

## Phase 1 — Skill Execution (--run mode only)

**Confirm before running full-mode deep-research cases:**
> Test cases include full-mode deep-research ({N} cases). These are expensive (~20+ min, multiple agent spawns). Run them? A) Yes B) Skip full-mode (use fast/fact-check only)

For each selected test case in `TEST_CASES[]`:

### 1.1 Prepare isolated workspace

```
TEST_WORKSPACE = {REPORTS_DIR}/{test_id}/skill-output/
```

Write `{TEST_WORKSPACE}/config_override.json`:
```json
{
  "output_root": "{TEST_WORKSPACE}",
  "analytics_folder": "{TEST_WORKSPACE}/analytics"
}
```

### 1.2 Load skill definition

```
Read: .agents/skills/{test_case.skill}/SKILL.md → SKILL_DEF
```

If test_case has a `fixture` field and the fixture file exists:
```
Read: {TESTS_ROOT}/fixtures/{test_case.input.fixture} → FIXTURE_CONTENT
```

### 1.3 Spawn skill agent

```
Read: .agents/shared/protocol.md → PROTOCOL

Agent(
  subagent_type="claude",
  description="Run {skill} / {mode} test: {test_id}",
  prompt="""
{SKILL_DEF}

---

## Test Harness Override

This is a test execution. Apply these overrides:

OUTPUT_ROOT = {TEST_WORKSPACE}
config/workspace.json is overridden — do not read the real one. Use OUTPUT_ROOT = {TEST_WORKSPACE}.

{IF fixture exists:}
FIXTURE CONTENT (use this instead of fetching live content):
For input {test_case.input.value} — do NOT fetch from arXiv or web.
Instead, treat the following as the fetched paper content and write it to
{TEST_WORKSPACE}/00_paper_content.md before Phase 1:

{FIXTURE_CONTENT}
{END IF}

## Input

{test_case.input.prompt}

## Mode flags

{test_case.mode_flags if present}
"""
)
```

Emit progress: `Test {test_id}: skill running...`

When agent completes, record `skill_workspace = {TEST_WORKSPACE}`.

---

## Phase 2 — Artifact Evaluation

For each test case (in --eval mode: one case; in --run mode: all executed cases):

### 2.1 Locate workspace

- `--eval {path}`: `skill_workspace = resolve(path)`
- `--run`: `skill_workspace` from Phase 1
- If --eval and --case not given: try to auto-detect skill from `state.json` in the workspace:
  ```
  Read: {skill_workspace}/state.json → try skill field
  ```
  If found, locate the matching test case. If multiple match, ask user to confirm.

### 2.2 Verify expected artifacts exist

Read `test_case.axes` — collect all unique `artifacts` entries.
For each expected artifact:
- If file missing: note as `MISSING_ARTIFACT` and set score 0 for all axes that require it.

### 2.3 Spawn evaluator agent

```
Read: .agents/skills/test-skills/agents/skill-evaluator.md → EVAL_DEF

Agent(
  subagent_type="claude",
  description="Evaluate {test_id} quality axes",
  prompt="""
{EVAL_DEF}

---

## Evaluation context

test_id: {test_id}
skill: {test_case.skill}
mode: {test_case.mode}
workspace: {skill_workspace}

## Axes to score

{test_case.axes as YAML block}

## Artifact availability

{list of expected artifacts with exists: true/false}

## Instructions

Read each artifact listed under each axis. Score 0-5 per the rubric. Output a JSON score card.
Do NOT read or reference any baseline scores during evaluation.
"""
)
```

Collect `scores_json` from evaluator output.

### 2.4 Compute combined score

```
combined = sum(score * weight for each axis) / sum(weights)
```

Write `{REPORTS_DIR}/{test_id}.scores.json`:
```json
{
  "test_id": "{test_id}",
  "run_id": "{RUN_ID}",
  "skill": "{skill}",
  "mode": "{mode}",
  "skill_workspace": "{skill_workspace}",
  "scored_at": "{ISO_NOW}",
  "scores": { ... },
  "combined": {float},
  "missing_artifacts": [...]
}
```

Emit progress: `Test {test_id}: scored {combined:.1f}/5. [MISSING: {N} artifacts if any]`

---

## Phase 3 — Regression Check

### 3.1 Load baselines

For each scored test case, attempt:
```
Read: {TESTS_ROOT}/baselines/{test_id}.json → baseline
```

If file not found: `baseline_status = NO_BASELINE` — record as informational, not a failure.

### 3.2 Spawn regression-checker

```
Read: .agents/skills/test-skills/agents/regression-checker.md → RC_DEF

Agent(
  subagent_type="claude",
  description="Check regressions for {N} test cases",
  prompt="""
{RC_DEF}

---

## Score cards (current run)

{list of score card JSON content}

## Baselines

{list of baseline JSON content, or "NO_BASELINE" for missing ones}

## Regression thresholds (from test case YAMLs)

{per-test-case thresholds block}
"""
)
```

Collect `regression_report` from agent.

---

## Phase 4 — Report + Baseline Accept

### 4.1 Format and send report

```
TEST-SKILLS COMPLETE — {RUN_ID}

Test cases run: {N}
Regressions:    {N_reg}  ⚠
Improvements:   {N_imp}  ✓
No baseline:    {N_new}

Per-case results:
  {test_id}  combined={combined:.1f}/5  {PASS|REGRESSION|IMPROVEMENT|NO_BASELINE}
  ...

{regression details if any}

{improvement notes if any}

Reports: {REPORTS_DIR}
```

If no regressions:
```
All tested cases pass or improve vs baseline.
```

### 4.2 --accept-baseline mode

If `--accept-baseline {test_id}` was passed:
1. Load `{REPORTS_DIR}/{test_id}.scores.json`
2. Write `{TESTS_ROOT}/baselines/{test_id}.json` with current scores
3. Print: `Baseline updated for {test_id}. Commit tests/baselines/{test_id}.json to lock it in.`

---

## Completion

**Analytics — write end event:**
```json
{"ts":"{ISO_NOW}","run_id":"{RUN_ID}","event":"skill_end","skill":"test-skills","version":"1.0.0","outcome":"success","duration_s":{elapsed},"regressions":{N_reg}}
```

If any regressions found: `"outcome": "regression"`.

---

## Anti-Pattern Reference

| Anti-pattern | Why it fails | What to do instead |
|---|---|---|
| Evaluator reads baseline before scoring | Anchors scores to past performance | Load baseline ONLY in regression-checker, after scoring |
| Single evaluator for all test cases | Context contamination across cases | Fresh agent spawn per test case |
| Running full deep-research in --run without warning | ~20 min, expensive | Always confirm before running full-mode cases |
| Accepting baseline for a run with MISSING_ARTIFACTS | Locks in broken state | Require all expected artifacts to exist before --accept-baseline |
| Evaluating without specifying --case for --eval | Auto-detection may pick wrong rubric | Always specify --case with --eval or confirm the auto-detected match |
