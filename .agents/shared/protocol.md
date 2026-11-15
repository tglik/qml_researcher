# Shared Protocol — qml-researcher Skills

Common infrastructure for all qml-researcher skills. **Read this once during Setup** in any
session that will spawn subagents, send progress updates, or export Word documents. Do not
re-read on every phase — load once into context and apply throughout.

---

## Hermes Artifact I/O Policy

When running under Hermes, prefer Hermes file tools (`read_file`, `write_file`, `patch`,
`search_files`) for all workspace artifact reads/writes. Do **not** use `execute_code` merely
to create directories, write markdown/json artifacts, merge phase files, or inspect local
workspace files — Slack/gateway `execute_code` approval is intentionally one-shot and will
re-prompt even after "Always Allow". Reserve `execute_code` for cases that genuinely need
Python control flow over many tool calls or nontrivial data processing.

---

## Agent Spawn Convention

All skills own their agents. Agent definitions live in `agents/` alongside each skill's
`SKILL.md` (lab roles: `lab/roles/<role>/`). Those files are the only source anyone edits.

**Claude Code** — spawn the registered agent. `scripts/gen_agents.py` renders every source into
`.claude/agents/<name>.md` with its `model`, `tools` and `maxTurns`, so routing and tool limits
take effect (a pasted definition runs on the session model with every tool). Pass only the task
and the context the agent cannot read itself:

```
Agent(
  subagent_type="<agent-name>",          # e.g. card-writer, experiment-designer, panel-methodologist
  description="<short description>",
  prompt="""
## QML Domain Criteria  ← inject when skill uses QML_DOMAIN
{QML_DOMAIN}

---

## Task for this invocation

{task-specific instructions}
"""
)
```

After editing any agent source, run `python scripts/gen_agents.py` (tests fail on stale output).

**Hermes, Codex, Gemini** — no registered agents: read the source and paste it first.

1. `Read .agents/skills/<skill>/agents/<agent-name>.md → AGENT_DEF`
2. Spawn with `{AGENT_DEF}`, a `---` separator, then the same prompt as above, through the
   runtime's mechanism: Codex `codex exec "<prompt>" -s read-only`; Hermes parallel task spawning;
   Gemini agent mode. Skill examples written as `subagent_type="<name>"` mean exactly this in
   those runtimes.

**Why this pattern:** agents stay self-contained within their skill (changing one cannot affect
another skill), and Claude Code still gets per-agent models and tools.

---

## Progress Update Format

After **every phase or revision cycle**, send a concise progress update before starting the next.

**Hermes/Slack:** send to the current conversation DM/thread (not the home channel unless the
skill was launched there). Emit the update as the next assistant message before the next
blocking tool call.

```text
Progress: <phase name> completed.
- <1–3 concrete facts: sources found, counts, verdict, artifact written>
Next: <next phase in one sentence>.
```

Progress messages are operational status, not research conclusions. Do not dump artifact body
in progress updates.

---

## Word Export

Convert the final Markdown report to `.docx` after writing it.

**Preferred:**
```
pandoc {WORKSPACE}/final.md -o {WORKSPACE}/final.docx --metadata title="<topic>"
```

**Fallback if pandoc is unavailable:** use a temporary venv with `python-docx`:
```
uv venv {WORKSPACE}/.docx-venv
{WORKSPACE}/.docx-venv/bin/python -m ensurepip --upgrade
{WORKSPACE}/.docx-venv/bin/python -m pip install python-docx
# then run a small converter script
```
Preserve headings, bullets, tables where feasible; citations as plain text.

Verify the `.docx` exists and is non-empty before marking Word export complete.

**On failure:** do not hide it. Attach/link the Markdown report instead and include the exact
blocker command/error on one line. Never mark `Word report generated: YES` when it failed.

---

## Session Memory Format

Write `{WORKSPACE}/session_memory.md` at skill Completion. Skills define their own field list;
use this common envelope:

```markdown
---
skill: <skill-name>
mode: <mode>
slug: <slug>
date: <YYYY-MM-DD>
topic: <parent question or paper title>
status: COMPLETE | DONE_WITH_CONCERNS | BLOCKED
pushed_to_permanent: false
---

## Summary
- <3 bullets from executive summary or verdict>

## Artifacts
| Artifact | Wiki link |
|----------|-----------|
| <name> | [[{WORKSPACE}/<file>]] |

## Connector Payload
[{date}] [SOURCE: <skill>] <one-line fact>. Output: [[{WORKSPACE}/<main output>]]
```

---

## Completion Message Format

Report to the user with this structure (Slack-safe, no raw artifact dumps):

```text
<SKILL> COMPLETE — <DONE | DONE_WITH_CONCERNS | BLOCKED>

Topic / Paper: <title>
Workspace: <WORKSPACE>

Executive summary:
- <decision-relevant bullets first>

What was done:
- <phase 1> completed: <key stat>
- <phase 2> completed: <key stat>
- ...
- Word report generated: <filename> | NO (reason)

Detailed report:
MEDIA:<WORKSPACE>/<final output>

STATUS: DONE | DONE_WITH_CONCERNS | BLOCKED
```
