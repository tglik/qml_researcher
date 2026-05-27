# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## What this repo is

**qml-researcher** — a Claude Code skills plugin for the QML startup team (Tsahi, Meir, Adi). It packages all QML research workflows, domain reviewers, and lab practices as installable `SKILL.md` files. See [README.md](README.md) for the full picture.

Project memory (vault) lives at:
`C:\Users\tmgli\Documents\Source\ai-os\01_Projects\QML_Startup\`

Companion files: `agent_handoff.md`, `tasks.md`, `artifacts/`, `research/`, `recent.md`

---

## Repo structure (target)

```
.claude/
  agents/          # Agent role definitions (.md files)
  skills/          # SKILL.md workflow files (one per skill)
  tools/           # Shared tool definitions
artifacts/         # Schema templates for lab artifacts
docs/              # Architecture decisions, design notes
```

Skills are discovered by Claude Code by scanning `.claude/skills/` for `SKILL.md` files.

---

## Authoring a skill

Every skill is a directory under `.claude/skills/<skill-name>/SKILL.md` with this structure:

```yaml
---
name: skill-name
description: |
  One-line summary of what this skill does.
  Trigger conditions: when should Claude invoke this automatically.
input:
  - what the user provides or what's in context
output:
  - artifact type and filename pattern
---
```

Followed by a markdown body with:
- **Numbered phases** — each phase has a clear goal, steps, and output
- **Pass/fail gate** at the end of each phase — explicit criteria; workflow stops if gate fails
- **Output artifact definition** — schema reference from `artifacts/`, path, and commit instruction
- **Failure modes to check** — QML-specific pitfalls relevant to this skill

Keep phases short. Each phase should be completable in one agent turn. Long phases get split.

---

## Authoring an agent

Agent definitions live in `.claude/agents/<agent-name>.md`:

```yaml
---
name: agent-name
description: One sentence on the agent's role and when it's invoked.
model: claude-opus-4-7        # or claude-sonnet-4-6
tools: [WebSearch, Read, ...]
---
```

Body: role definition, responsibilities, output contract, what this agent may and may not do.

**Key constraint:** the agent that generates a claim must not be the agent that verifies it. Generation and verification roles must be separate agent files.

---

## QML domain constraints (baked into every research skill)

All skills that evaluate a QML direction or claim must screen against these 5 criteria:

1. **Dequantization risk** — does a classical Nystrom/RFF approximation match performance?
2. **Geometric difference** — is the quantum kernel genuinely different from RBF/polynomial?
3. **Trainability/simulability trilemma** — barren plateau risk? classically simulable PQC?
4. **Hardware fit** — NISQ-realistic on neutral-atom hardware (Q-Factor modality)?
5. **Strong classical baseline** — TabPFN-2.5/XGBoost for tabular; GNN/SOAP/GAP for graphs — not toy baselines

Current strong directions: neutral-atom graph/reservoir/Hamiltonian kernels, dynamic circuits, mid-circuit measurement/feedforward, MBQC-style architectures.

Deprioritized (do not re-suggest without new evidence): generic low-data tabular VQC demos, single-encoding PQC claims (= truncated Fourier), generic HHL linear-algebra speedups (dequantization-vulnerable).

---

## Artifact output conventions

- Artifacts → `C:\Users\tmgli\Documents\Source\ai-os\01_Projects\QML_Startup\artifacts\<topic>_<YYYY-MM-DD>.md`
- Research runs → `C:\Users\tmgli\Documents\Source\ai-os\01_Projects\QML_Startup\research\<topic>_<date>\`
- After every workflow run, prepend one line to `recent.md`: `[YYYY-MM-DD] [SOURCE: session] <fact>`
- All artifact writes go to git

Artifact schemas (Research Question Card, Project Charter, Paper Card, Evidence Record, Experiment Passport, Claim Ledger, Review Panel Report) are defined in `artifacts/` in this repo.

---

## Claim status ladder

Skills must move claims through this ladder with explicit evidence gates — writing agents may not strengthen wording beyond the current status:

```
speculative → plausible → observed → supported → strong → published
                                                         ↘ refuted
```

---

## gstack

Use the `/browse` skill from gstack for all web browsing. Never use `mcp__claude-in-chrome__*` tools.

### Skill routing

- Product ideas / brainstorming → `/office-hours`
- Architecture decisions → `/plan-eng-review`
- Strategy / startup scope → `/plan-ceo-review`
- Bugs / broken behavior → `/investigate`
- Code review → `/review`
- Ship / PR → `/ship`
- Save progress → `/context-save`
- Resume → `/context-restore`
