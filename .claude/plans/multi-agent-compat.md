# Plan: Multi-Agent CLI Compatibility for qml-researcher Skills

**Date:** 2026-05-31
**Branch:** main
**Status:** DRAFT — pending /autoplan review

---

## Problem

The `qml-researcher` skills (`/qml-deep-research`, `/qml-paper-review`, `/fetch-arxiv`) are installed under `.claude/skills/` — a Claude Code-specific path. Codex CLI, Hermes Agent, Gemini CLI, and GitHub Copilot read from `.agents/skills/` as the universal fallback. Skills are also unusable in those CLIs because:
1. **Wrong discovery path**: `.claude/skills/` is invisible to every non-Anthropic agent
2. **Missing AGENTS.md**: Codex CLI requires an `AGENTS.md` file for project-level instructions (equivalent to CLAUDE.md)
3. **Claude Code-specific syntax in skill bodies**: `Agent(subagent_type="claude", ...)` calls, `AskUserQuestion` tool, and some frontmatter fields (`allowed-tools`, `hooks`) are CC-only
4. **Hardcoded absolute paths**: `c:\Users\tmgli\Documents\Source\qml_researcher\criteria\qml_domain.md` in skill bodies fails cross-machine and cross-OS
5. **No agent configuration files**: Codex expects `agents/openai.yaml` per skill for UI metadata and invocation policy

---

## Goals

1. Skills work in Claude Code (no regression)
2. Skills are discoverable and usable in Codex CLI, Hermes Agent, and Gemini CLI
3. QML domain criteria and agent definitions remain portable
4. No duplication — single source of truth for each skill

---

## Approach: `.agents/skills/` as Canonical (Agent-Neutral) + Per-CLI Symlinks

Move canonical skill files to `.agents/skills/` — the CLI-neutral open standard path. Each agent CLI that has its own discovery directory gets symlinks pointing back to `.agents/skills/`. No CLI owns the source of truth.

```
.agents/skills/              ← CANONICAL (agent-neutral, open standard)
  fetch-arxiv/
  qml-deep-research/ + agents/
  qml-paper-review/ + agents/

.claude/skills/              ← CC discovery (symlinks → .agents/skills/)
  fetch-arxiv    → ../../.agents/skills/fetch-arxiv
  qml-deep-research → ../../.agents/skills/qml-deep-research
  qml-paper-review  → ../../.agents/skills/qml-paper-review

# Codex, Hermes, Gemini read .agents/skills/ natively — no extra symlinks needed.
# If a future CLI adds its own per-project discovery dir, add symlinks then.
```

**Why `.agents/skills/` as canonical:** It is the CLI-neutral open standard (confirmed Jan 2026). Making any CLI's native path canonical (`.claude/skills/`, `.codex/skills/`) privileges one vendor. `.agents/` is the right owner.

**Why only `.claude/skills/` symlinks for now:** Codex, Hermes, and Gemini already read `.agents/skills/` natively. Only Claude Code needs a bridging symlink to its own discovery path. Adding `.codex/skills/` and `.hermes/skills/` symlink dirs is fine if you want explicit presence, but it adds no functional value today.

**Windows note:** Requires `git config core.symlinks true` + Developer Mode (Win 10+) or WSL. Add to README.

**Rejected: keep `.claude/skills/` canonical:** Privileges one CLI. When new CLIs are added, `.claude/skills/` is a confusing source of truth.

**Rejected copy approach:** Duplication; two copies diverge.

---

## Changes Required

### 1. Move skills to `.agents/skills/` (canonical) + add `.claude/skills/` symlinks (HIGH)

Move skill files from `.claude/skills/` to `.agents/skills/`. Then create symlinks in `.claude/skills/` so Claude Code continues to discover them.

```bash
# Step 1: move canonical files
mkdir -p .agents/skills
mv .claude/skills/fetch-arxiv         .agents/skills/fetch-arxiv
mv .claude/skills/qml-deep-research   .agents/skills/qml-deep-research
mv .claude/skills/qml-paper-review    .agents/skills/qml-paper-review

# Step 2: create CC symlinks
ln -s ../../.agents/skills/fetch-arxiv        .claude/skills/fetch-arxiv
ln -s ../../.agents/skills/qml-deep-research  .claude/skills/qml-deep-research
ln -s ../../.agents/skills/qml-paper-review   .claude/skills/qml-paper-review

# Step 3: verify
test -L .claude/skills/fetch-arxiv && cat .claude/skills/fetch-arxiv/SKILL.md
```

Result:
```
.agents/skills/              ← CANONICAL
  fetch-arxiv/SKILL.md
  qml-deep-research/SKILL.md + agents/
  qml-paper-review/SKILL.md + agents/

.claude/skills/              ← CC symlinks only
  fetch-arxiv    → ../../.agents/skills/fetch-arxiv
  qml-deep-research → ../../.agents/skills/qml-deep-research
  qml-paper-review  → ../../.agents/skills/qml-paper-review
```

Commit both the moved files and the new symlinks. Windows: see README troubleshooting.

### 2. Add AGENTS.md (HIGH — Codex CLI project instructions)

Create `AGENTS.md` at repo root alongside `CLAUDE.md`. Content mirrors the QML domain constraints and skill routing section from CLAUDE.md, translated to the AGENTS.md format Codex reads.

AGENTS.md = **thin wrapper only** (not a mirror of CLAUDE.md — that would drift).

Content in AGENTS.md:
- One-paragraph project description
- Explicit pointer: "Full QML domain constraints are in CLAUDE.md — read it if available"
- Skill discovery note: skills are in `.agents/skills/`
- Output path pointer: `config/workspace.json` controls `output_root`
- Codex-specific: note that `Agent(subagent_type="claude", ...)` maps to `codex exec` in Codex

### 3. Fix hardcoded absolute paths in skill bodies (HIGH — correctness on all machines/OS)

Current in `qml-deep-research/SKILL.md` and `qml-paper-review/SKILL.md`:
```
Read: c:\Users\tmgli\Documents\Source\qml_researcher\criteria\qml_domain.md → QML_DOMAIN
```

Fix: replace with relative repo path only:
```
Read: criteria/qml_domain.md → QML_DOMAIN
```
The fallback comment already exists ("fall back to: `criteria/qml_domain.md` from the repo root"), so the absolute path is just dead weight that breaks non-Windows machines.

### 4. Add `openai.yaml` stub per skill (MEDIUM — Codex metadata, schema unconfirmed)

Codex CLI reads optional metadata from the skill directory. Schema is not yet confirmed from official docs — treat these as speculative stubs. Place at skill root (not inside `agents/`):

```yaml
# openai.yaml — Codex CLI skill metadata stub (SCHEMA UNCONFIRMED)
# Schema based on public documentation as of 2026-06-01; verify before relying on.
display_name: "QML Deep Research"
description: "Multi-phase literature research for QML topics"
invocation_policy: explicit
```

If Codex silently ignores unknown/malformed YAML, these are harmless. If not, remove.

### 5. Abstract `AskUserQuestion` in skill bodies (MEDIUM — interactive prompts in non-CC agents)

`AskUserQuestion` is a Claude Code-specific tool. Codex, Hermes, and Gemini do not support it — they fall through to prose output instead. The practical impact:
- **Phase 0A** of `/qml-deep-research` uses AskUserQuestion for 5 forcing questions
- **`/qml-paper-review`** has no AskUserQuestion calls (already CLI-agnostic for core phases)

Fix: add a **visible prose fallback block** before each AskUserQuestion call site (not an HTML comment — agents may strip or ignore comments):
```markdown
> **If running outside Claude Code (Codex, Hermes, Gemini):** AskUserQuestion is not
> available. Ask the following question in prose, wait for the user's typed reply,
> then continue. Do not batch multiple questions in one message.
```
This is a non-breaking addition. CC ignores prose before its own AskUserQuestion call.
The Q1-Q5 interactive loop in Phase 0A degrades gracefully: questions become sequential
prose prompts. The one-at-a-time requirement is preserved in prose instructions.

### 6. Generalize agent-spawn syntax (LOW — documentation + best-effort compat)

Current skills use:
```
Agent(
  subagent_type="claude",
  description="...",
  prompt="..."
)
```

This is Claude Code SDK syntax. Other CLIs handle sub-agent spawning differently:
- Codex: `codex exec "<prompt>" -s read-only`
- Hermes: parallel task spawning via Hermes's native orchestration
- Gemini CLI: Gemini's agent mode

The skill bodies are markdown instructions, not code. The Agent(...) blocks are pseudo-code that each CLI's orchestrator interprets. We cannot make these identical across CLIs.

Fix: add a minimal agent compatibility header per skill that explains the spawn pattern for non-CC agents:

```markdown
## Agent Spawn Compatibility
When running in Claude Code: use the Agent tool with subagent_type="claude".
When running in Codex CLI: use `codex exec "<prompt>" -s read-only`.
When running in Hermes: use Hermes parallel task spawning.
The task prompts below are agent-agnostic — inject them into whichever spawn mechanism your CLI supports.
```

### 7. Update README installation section (HIGH — DX gate: promotes to HIGH)

Rewrite the installation section. The install model is: clone THIS repo, run the symlink setup, invoke from repo root. Do NOT describe "clone into .agents/skills/" — that model breaks relative paths.

**New README install section structure:**
```markdown
## Installation

### macOS / Linux (Claude Code + Codex + Hermes + Gemini)

1. Clone into your project or a shared location:
   git clone https://github.com/tglik/qml_researcher /path/to/qml_researcher
   cd /path/to/qml_researcher

2. The `.agents/skills/` directory (canonical) and `.claude/skills/` symlinks are committed
   to the repo — no setup step needed after clone on macOS/Linux.

   Verify the symlinks resolved correctly:
   ls -la .claude/skills/  # should show 3 symlinks pointing to ../../.agents/skills/
   cat .claude/skills/fetch-arxiv/SKILL.md  # should show actual SKILL.md content

   Codex, Hermes, Gemini read .agents/skills/ directly — no setup needed.
   Claude Code reads .claude/skills/ via the committed symlinks — no setup needed.

4. Configure output path (first time only):
   # Default output_root is output/ (repo-local, gitignored).
   # Already set in config/workspace.json — no action needed for default.
   # To sync to cloud storage, edit config/workspace.json.

5. Run your first skill:
   # Claude Code: /fetch-arxiv 2401.12345
   # Codex:       codex "/fetch-arxiv 2401.12345"
   # Hermes:      hermes "/fetch-arxiv 2401.12345"

### Windows

Symlinks require Developer Mode or WSL:
1. Enable Developer Mode (Settings → System → For developers → Developer mode)
2. git config --global core.symlinks true
3. Re-clone the repo (existing clone has text files instead of symlinks)
   (The .claude/skills/ symlinks are committed — they materialize on clone when core.symlinks=true)
4. Verify in WSL/Git Bash: test -L .claude/skills/fetch-arxiv && echo OK

### Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `codex skills list` shows empty | wrong cwd, or `.agents/skills/` symlinks not materialized | Verify `cwd = repo root`; check `ls -la .agents/skills/` shows actual directories |
| `Claude Code` can't find skills | `.claude/skills/` symlinks broken | Run `test -L .claude/skills/fetch-arxiv && echo OK`; if text file, see Windows steps |
| Windows: `.claude/skills/fetch-arxiv` is a text file | Symlinks checked out as text (Developer Mode off or `core.symlinks false`) | Enable Developer Mode, set `git config core.symlinks true`, delete and re-clone |
| `AskUserQuestion` prompt not showing (Codex/Hermes) | AskUserQuestion is CC-only; skill falls back to prose | Normal — answer in chat when the skill asks a question in prose |
| `File not found: criteria/qml_domain.md` | CLI invoked from wrong directory | Always invoke from repo root, not from inside .agents/skills/ |
```

Also update the skill catalog table to use actual skill names (`/qml-deep-research`, not `/deep-research`).

### 8. ~~Add `.gitignore` entry for output~~ (REMOVED — already done)

`output/` is already gitignored. No change needed.

---

## What Stays Claude Code-Specific (Not Portable)

These features work only in Claude Code and are intentionally kept as CC-only:
- `allowed-tools` frontmatter — safely ignored by other agents
- gstack integration (`/browse`, `~/.claude/skills/gstack/`) — CC-only
- `hooks` frontmatter — CC-only
- AskUserQuestion native tool — CC has richer version; others fall back to prose

---

## Files Touched

| File | Change |
|------|--------|
| `.agents/skills/` | Create (move files from `.claude/skills/`) — becomes canonical |
| `.claude/skills/*` | Convert to symlinks → `../../.agents/skills/<skill>` |
| `AGENTS.md` | Create new (thin wrapper + inline 5 QML criteria) |
| `.agents/skills/qml-deep-research/SKILL.md` | Fix absolute path (line 106); add AskUserQuestion prose fallback; add cwd note |
| `.agents/skills/qml-paper-review/SKILL.md` | Add Agent Spawn Compatibility header |
| `.agents/skills/qml-deep-research/openai.yaml` | Create new (stub, at skill root) |
| `.agents/skills/qml-paper-review/openai.yaml` | Create new (stub, at skill root) |
| `.agents/skills/fetch-arxiv/openai.yaml` | Create new (stub, at skill root) |
| `README.md` | Update installation section; add Windows symlink setup steps |
| `.agents/README.md` | Create: "canonical skills live here; .claude/skills/ has symlinks pointing here" |

---

<!-- AUTONOMOUS DECISION LOG -->
## Decision Audit Trail

| # | Phase | Decision | Classification | Principle | Rationale | Rejected |
|---|-------|----------|----------------|-----------|-----------|---------|
| 1 | CEO | Full multi-agent goal confirmed | User-confirmed | — | User stated Codex + Hermes + Gemini targets | Cross-machine CC only |
| 2 | CEO | Portability parallel with skill catalog | User-confirmed | — | Independent work streams, 2-3hr effort | Defer until catalog complete |
| 3 | CEO | Remove .gitignore item from scope | Mechanical | P3 | Already done | — |
| 4 | CEO | Keep .claude/skills/ canonical; symlinks in .agents/ | Mechanical | P5 | Lower change radius; CC path unchanged | Move canonical to .agents/ |
| 5 | CEO | AGENTS.md = thin wrapper, not mirror of CLAUDE.md | Mechanical | P5 | Eliminates drift; one authority for QML domain | Mirror CLAUDE.md content |
| 6 | CEO | openai.yaml as speculative stubs with schema note | Taste → T1 | P1 | Complete > nothing, but schema unconfirmed | Skip openai.yaml entirely |
| 7 | Eng | Fix Files Touched table (had inverted symlink direction) | Mechanical | P3 | Table contradicted architecture prose; fix prevents wrong implementation | — |
| 8 | Eng | Fix symlink target path typo (../ → ../../) in prose | Mechanical | P3 | Correct relative path from .agents/skills/<skill> to .claude/skills/<skill> | — |
| 9 | Eng | Move openai.yaml from agents/ subdir to skill root | Mechanical | P5 | agents/ is for agent definitions; skill root is cleaner | Inside agents/ subdir |
| 10 | Eng | AGENTS.md includes 5 QML criteria inline + pointer to criteria/qml_domain.md | Mechanical | P1 | Codex needs criteria to enforce safety rules; can't rely on it reading CLAUDE.md | Thin pointer only |
| 11 | Eng | AskUserQuestion fallback = visible prose block (not HTML comment) | Mechanical | P5 | Agents may strip HTML comments; prose is always visible | HTML comment |
| 12 | Eng | Add cwd requirement + symlink verification to success criteria | Mechanical | P5 | Eliminates silent breakage from wrong invocation path | — |
| 13 | Eng | gstack /browse not a real portability blocker (skills use WebSearch natively) | Taste → T2 | P3 | Skill frontmatter lists WebSearch/WebFetch; gstack is CC session guidance only | Flag as blocker |
| 14 | DX | Promote README rewrite to HIGH priority | Mechanical | P1 | DX gate: no hello-world path for any CLI = unusable docs | Keep as LOW |
| 15 | DX | Add troubleshooting section to README (3 scenarios) | Mechanical | P1 | Silent failures need documented recovery paths | Skip |
| 16 | DX | Fix install model in README: clone repo, run ln -s; not "clone into .agents/" | Mechanical | P5 | "Clone into .agents/" breaks relative paths and criteria/ resolution | Keep broken model |
| 17 | DX | AGENTS.md includes "Available skills" list with correct names | Mechanical | P1 | Codex user needs skills list without opening README | Skip |
| 18 | DX | Fix README skill catalog to use actual names (qml-deep-research not deep-research) | Mechanical | P3 | Naming mismatch between README and real skill dirs confuses first-time users | Skip |
| 19 | DX | Document config/workspace.json first-time setup (default = output/) | Mechanical | P1 | Skill silently fails if Read: config/workspace.json fails | Skip |
| 20 | Post-review | .agents/skills/ = canonical; .claude/skills/ = symlinks (not the reverse) | User-feedback | — | No CLI should own the canonical path; .agents/ is CLI-neutral open standard | .claude/skills/ canonical |

---

## Success Criteria

**Automated (run before merge):**
- [ ] `test -d .agents/skills/fetch-arxiv` — real directory (canonical)
- [ ] `test -f .agents/skills/fetch-arxiv/SKILL.md` — actual file, not symlink
- [ ] `test -L .claude/skills/fetch-arxiv` — CC path is a symlink
- [ ] `test -L .claude/skills/qml-deep-research` — CC path is a symlink
- [ ] `test -L .claude/skills/qml-paper-review` — CC path is a symlink
- [ ] `cat .claude/skills/fetch-arxiv/SKILL.md` — resolves through symlink to actual content
- [ ] `grep -r "c:\\\\Users" .agents/skills/` returns empty — Windows path removed
- [ ] `readlink .claude/skills/fetch-arxiv` = `../../.agents/skills/fetch-arxiv`

**Manual (Claude Code regression):**
- [ ] `/fetch-arxiv 2401.12345` in CC completes without error
- [ ] `/qml-deep-research --scope-only test` in CC triggers Phase 0A

**Manual (Codex):**
- [ ] `codex skills list` shows all 3 skills
- [ ] `codex "/fetch-arxiv 2401.12345"` completes

**Manual (Hermes — when available):**
- [ ] `hermes skills` shows all 3 skills

**Note:** All CLIs must be invoked from repo root (`cwd = qml_researcher/`). Skills use repo-root-relative paths (`AGENTS_DIR = .claude/skills/<skill>/agents/`, `criteria/qml_domain.md`).

Test plan artifact: `~/.gstack/projects/tglik-qml_researcher/main-test-plan-*.md`
