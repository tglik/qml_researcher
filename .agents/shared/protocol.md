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
`SKILL.md`. **Never** use named `subagent_type` values — always `subagent_type="claude"` and
inject the agent definition into the prompt.

Before every Agent call:

1. Read the agent file: `Read .agents/skills/<skill>/agents/<agent-name>.md → AGENT_DEF`
2. Spawn with the definition injected first, then a `---` separator, then the task:

```
Agent(
  subagent_type="claude",
  description="<short description>",
  prompt="""
{AGENT_DEF}

---

## QML Domain Criteria  ← inject when skill uses QML_DOMAIN
{QML_DOMAIN}

---

## Task for this invocation

{task-specific instructions}
"""
)
```

**Why this pattern:** agents are self-contained within their skill; changing an agent here
cannot affect any other skill.

When running in **Claude Code**: use the `Agent` tool with `subagent_type="claude"`.  
When running in **Codex CLI**: `codex exec "<prompt>" -s read-only`.  
When running in **Hermes**: use Hermes parallel task spawning.  
When running in **Gemini CLI**: use Gemini's agent mode.  
Task prompts are agent-agnostic — inject them into whichever spawn mechanism your runtime supports.

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
