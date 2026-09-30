# QML Lab — implementation

The lab half of `qml_researcher`: skills and agent roles that take a proposed quantum
algorithm or a use-case hypothesis, kill it on paper if it can, and otherwise run a
pre-registered, phase-by-phase experiment against an adversarially strong classical baseline,
ending in an audited verdict. Design: [`docs/lab/`](../docs/lab/) (start with
`01_high_level_plan.md`).

---

## How to review this (read this first)

Every skill and every agent role is split into two files, on purpose:

| File | What it holds | Who should review it | Question to ask while reading |
|---|---|---|---|
| **`ESSENCE.md`** | The way of thinking: what this role/skill is for, how it reasons, what it refuses, what a good result looks like, the precedents it learns from | **Adi, Meir** (science) | *Would a good QML researcher think this way? Is anything here wrong, naive, or missing?* |
| **`PROTOCOL.md`** / **`SKILL.md`** | The mechanics: inputs, outputs, numbered phases, pass/fail gates, file paths, tool calls | **Tsahi** (system) | *Does it run? Does every step have a gate? Are the files right?* |

An ESSENCE file never contains file paths or step numbers; a PROTOCOL file never argues about
science. If you find science in a protocol or mechanics in an essence, that is a bug — flag it.

**Suggested review order for Adi and Meir** (≈2 hours total):
1. [`criteria/lab_method.md`](../criteria/lab_method.md) — the shared rules every role loads.
2. The four roles that carry the most judgment:
   [`screen-analyst`](roles/screen-analyst/ESSENCE.md),
   [`classical-twin-champion`](roles/classical-twin-champion/ESSENCE.md),
   [`experiment-designer`](roles/experiment-designer/ESSENCE.md),
   [`verdict-auditor`](roles/verdict-auditor/ESSENCE.md).
3. [`algorithm-analyst`](roles/algorithm-analyst/ESSENCE.md) (Adi's S0) and the
   [review panel personas](roles/review-panel/).
4. The skill essences in `.agents/skills/qml-*/ESSENCE.md`.

Leave comments inline (`> **Adi:** …`) or as a PR review. A changed ESSENCE file is a
change to how the lab thinks; it goes through the eval suite like any other change (C10).

---

## Layout

```
lab/
  README.md                        this file
  roles/<role>/ESSENCE.md          how the role thinks          (science review)
  roles/<role>/PROTOCOL.md         what the role does, exactly  (system review)
  roles/review-panel/personas/*.md five panel personas (essence only; they share one PROTOCOL)
  tools/                           deterministic tools, stdlib-only Python
.agents/skills/qml-<skill>/
  ESSENCE.md                       what the skill is for and its judgment calls
  SKILL.md                         the protocol: phases, gates, files, spawns
criteria/lab_method.md             six rules, gate ladder, Adi's global rules, warning tables
artifacts/lab/templates/           the artifact templates (HYPOTHESIS, SCREEN, VERDICT, …)
artifacts/lab/schemas/             JSON schemas (STATE, lock, provenance)
config/lab_autonomy.json           checkpoint modes (the autonomy ladder)
```

Evidence (experiment folders) lives in the `qml_artifacts` vault under `experiments/`.

---

## Conventions

**Spawning a role.** Lab roles are shared across skills, so they live here rather than in each
skill's `agents/` folder (a deliberate extension of `.agents/shared/protocol.md`). To spawn:

```
Read: lab/roles/<role>/ESSENCE.md  → ESSENCE
Read: lab/roles/<role>/PROTOCOL.md → PROTOCOL
Read: criteria/lab_method.md       → LAB_METHOD   (every lab role gets it)

Agent(
  subagent_type="claude",
  description="<role>: <short task>",
  prompt="""
{ESSENCE}

---

{PROTOCOL}

---

## Lab method (shared rules)
{LAB_METHOD}

---

## Task for this invocation
thread: {THREAD_DIR}
{task-specific instructions — artifact paths only, never a transcript}
"""
)
```

Essence comes first on purpose: the role reads *who it is* before *what to do*.

**Handoffs are artifacts, never transcripts.** A role receives file paths and reads them. It
never receives another agent's reasoning. This is what makes the auditor independent and
retries clean.

**State.** Every lab skill validates and reads the thread's `STATE.json` first and writes it last
(`python -m lab.tools.state …`). `/qml-lab` is the only skill that changes `stage` or opens and
closes checkpoints.

**Tools.** Anything a tool can compute, a model never judges: hashes, lock diffs, gate tables,
streaks. Tools live in `lab/tools/`, use only the Python standard library, and are run from the
repo root as `python -m lab.tools.<tool>`. Numeric/scientific helpers that need numpy/scipy/qiskit
live with the experiments (`qml_artifacts/experiments/_lab_tools/`) and run in the experiments venv.

**Human checkpoints.** CP1 screen · CP2 freeze · CP3 phase gate · CP4 verdict · CP5 promotion.
Their current mode (`HUMAN_APPROVE` / `HUMAN_SPOTCHECK` / `AGENT`) is in
`config/lab_autonomy.json`. Signer ≠ author, always.
