# .agents/

This directory is the **canonical** home for all qml-researcher skills.

`.agents/skills/` is the CLI-neutral open standard discovery path (SKILL.md open standard, adopted Jan 2026). No single CLI owns this directory.

## Discovery by CLI

| CLI | Native discovery path | Setup needed |
|-----|-----------------------|-------------|
| Codex CLI | `.agents/skills/` | None — reads here natively |
| Hermes | `.agents/skills/` | None — reads here natively |
| Gemini CLI | `.agents/skills/` | None — reads here natively |
| Claude Code | `.claude/skills/` | None — committed symlinks point here |

## Symlink structure

`.claude/skills/<skill>` → `../../.agents/skills/<skill>`

The symlinks are committed to the repo. On macOS/Linux they materialize automatically on clone. On Windows, see README.md troubleshooting section.

## Adding a new skill

1. Create the skill under `.agents/skills/<skill-name>/SKILL.md`
2. Add a symlink in `.claude/skills/`: `ln -s ../../.agents/skills/<skill-name> .claude/skills/<skill-name>`
3. Commit both the skill directory and the symlink
4. Add an entry to `.agents/skills/<skill-name>/openai.yaml` (stub — schema unconfirmed)
