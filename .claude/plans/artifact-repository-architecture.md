# Artifact Repository Architecture

**Date:** 2026-06-04 | **Revised:** 2026-06-11  
**Status:** Decided — ready for implementation  
**Scope:** How QML research artifacts are stored, linked, exposed to the team, and queried by skills

---

## Problem

The team generates and receives knowledge from many sources — skill-generated research reports, weekly meeting notes, team WhatsApp discussions, public news like company announcements and funding rounds, and raw papers. All of this currently lands in disconnected places (local folders, `recent.md`, WhatsApp) with no extraction, no links, and no memory across sessions.

Goal: accumulate artifact cards into a growing knowledge base that gives skills better and better context over time, and gives the whole team a readable, navigable research wiki.

---

## Architecture Decision: Three Layers

```
Layer 1 — Sources      (any raw input, regardless of origin)
Layer 2 — Cards        (structured entities, one file per entity)
Layer 3 — Indexes      (aggregated views, what skills read for context)
```

### Layer 1 — Sources

Any raw input the team generates or receives. Not normalized. The extractor reads from all source types and extracts cards from each.

```
sources/
  reports/             ← skill-generated (paper reviews, deep research, triage)
    paper-reviews/
      2405.12345-review-2026-06-04.md
    deep-research/
      neutral-atom-kernels-2026-06-03/
    triage/
      2026-06-04_neutral-atom-graph.md
  meetings/            ← Spinach.ai exports, manual notes
    2026-06-04-weekly-sync.md
  discussions/         ← WhatsApp/team chat summaries
    2026-06-04-adi-qcnn-thread.md
  news/                ← company announcements, press, LinkedIn posts
    2026-06-04-ibm-10b-quantum-investment.md
  documents/           ← external docs: investor decks, partner whitepapers
    2026-05-23-pitch-v1-notes.md
```

Sources are the ground truth. Cards are derived from them. If the extractor schema evolves, sources can be re-processed without re-running research.

#### Source types and what the extractor targets

| Source type | Likely card extractions | Claim status ceiling |
|-------------|------------------------|----------------------|
| `skill-report` | Paper Card, Author, Institute | `observed` (audit required to go higher) |
| `meeting-note` | Research Question, decision log entries, action items | `speculative` |
| `discussion` | Early signals, research questions | `speculative` |
| `news-item` | Company cards, funding events, partnership signals | `speculative` |
| `document` | Research Question, Institute, strategic context | `plausible` |

**Note:** `/extract-artifacts` no longer creates Claim or Evidence cards. Claims and evidence are embedded inline in paper cards. Cross-paper synthesis is handled by `/synthesize-hypotheses`.

**Claim status ceiling by source:** a claim extracted from a WhatsApp discussion starts at `speculative` regardless of how confident the team sounds. Only a skill-audited report can produce a claim at `observed` or above. This enforces the claim ladder from the bottom up.

#### Source frontmatter convention

Every source file must declare its type so the extractor knows how to process it:

```yaml
---
source_type: meeting-note          # skill-report | meeting-note | discussion | news-item | document
source_date: 2026-06-04
source: spinach-ai                 # spinach-ai | whatsapp | manual | skill | gmail | web
participants: [tsahi, meir, adi]   # for meetings/discussions
extracted: false                   # flipped to true by extractor after processing
---
```

Sources are the source of truth. Cards are derived from them. If a report is re-run, cards can be re-extracted without losing anything.

### Layer 2 — Cards

One file per entity. Extracted from reports by the `/extract-artifacts` skill. Never written directly by research skills.

**Two-tier claim architecture:**

- **Tier 1 (paper-scoped):** Claims and evidence live as **inline sections inside paper cards** — not as separate files. They are part of the paper card's body (the existing `## Main Claim` and `## Evidence` sections).
- **Tier 2 (cross-paper):** `Research Hypothesis` cards are the only promoted cross-paper claim artifact. They are **never extracted** — they are only created by `/synthesize-hypotheses` after sufficient paper cards accumulate on a topic.

```
cards/
  paper-cards/
    2405.12345.md           ← keyed by arXiv ID; claims/evidence inline
  persons/
    farhi-edward.md         ← keyed by lastname-firstname slug
  organizations/
    mit-center-for-quantum.md
  hypotheses/
    rydberg-quantum-reservoir-computing.md  ← cross-paper, synthesized only
  research-questions/
    neutral-atom-graph-kernels.md
```

**Retired card types (v1):**
- `cards/claims/` — retired. Per-paper claim files were too granular and not useful for synthesis.
- `cards/evidence/` — retired. Evidence is embedded in paper cards.

### Layer 3 — Indexes

Aggregated views maintained by the extractor and synthesis skill. Small files, loaded by skills at workflow start as context preamble.

```
indexes/
  hypothesis-ledger.md   ← all Research Hypotheses + status + support_count + strategic_value
  author-index.md        ← all known authors + their paper IDs
  topic-map.md           ← papers grouped by topic/direction
  paper-registry.md      ← all evaluated papers + verdict + date
```

**`claim-ledger.md` is retired.** It was a flat list of per-paper claims that provided no synthesis value. Replaced by `hypothesis-ledger.md` which holds only cross-paper, synthesized, strategically-filtered hypotheses.

---

## Claim Status Ladder

Skills must move claims through this ladder with explicit evidence gates — writing agents may not strengthen wording beyond the current status. The ladder applies to both paper-card inline claims and Research Hypothesis cards.

```
speculative → plausible → observed → supported → strong → published
                                                         ↘ refuted
```

---

## Research Hypothesis: The Pareto Archive

The core design principle: **per-paper claims are footnotes; cross-paper hypotheses are first-class**.

A Research Hypothesis is created by `/synthesize-hypotheses` only when:

1. `support_count ≥ 2` — at least two independent papers or deep-research runs support the direction
2. Passes ≥1 of the 5 QML domain criteria (dequantization_risk, geometric_difference, trainability_simulability, hardware_fit, classical_baseline)
3. `strategic_value ∈ [directional, actionable]` — not `incremental` or `foundational` (foundational = already-known fact, incremental = minor refinement)
4. **Novelty check:** the synthesis agent explicitly scores "would this surprise a QML expert?" — kills trivially known claims

The `hypothesis-ledger.md` index is the pareto view: a small number of high-signal, cross-paper supported directions with strategic scores.

---

## Storage Decision: Git Repository

The artifact store is a **dedicated git repository** (`qml-artifacts`), separate from `qml_researcher`.

**Why git, not Google Drive:**
- Commit history = claim provenance. You can see which paper promoted a claim from `plausible` to `supported` and on what date.
- `git diff` on a card shows exactly what changed between extractions.
- GitHub provides offsite backup, search, and blame with zero extra tooling.
- No sync conflicts, no proprietary format, no storage costs.

**Periodic commits:** a Mac Mini cron job runs `git add . && git commit -m "auto: $(date)" && git push` on a schedule (e.g., hourly commits, nightly push).

**`workspace.json` config:**
```json
{
  "output_root": "/absolute/path/to/qml-artifacts"
}
```

---

## Team Access Decision: Quartz + Cloudflare Tunnel

### Why not raw Google Drive or GitHub web UI

Google Drive treats `.md` files as blobs (no rendering). GitHub renders markdown but has no graph view and requires a GitHub account. Neither is suitable for Meir (non-technical) as a daily research wiki.

### Quartz

[Quartz](https://quartz.jzhao.xyz/) is an open-source Node.js static site generator that reads a folder of markdown files and produces a website with:
- Rendered markdown
- Interactive graph view (D3-based, shows wikilink connections between cards)
- Backlinks panel, full-text search, frontmatter display
- `[[wikilink]]` navigation

**Obsidian is not required anywhere.** Quartz reads plain markdown files with `[[wikilinks]]`. No Obsidian install on Mac Mini or team machines.

Quartz runs on Mac Mini, watches the `qml-artifacts/` folder, and rebuilds the site when files change.

### Cloudflare Tunnel

Free Cloudflare daemon (`cloudflared`) installed on Mac Mini. Provides a stable public URL (e.g., `research.qmlteam.com`) with zero port forwarding or router config. Cloudflare Access (also free) adds a login gate.

**End-to-end flow:**
```
Skill writes artifact → qml-artifacts/ updated
Quartz watches folder → rebuilds site (seconds)
Meir opens https://research.qmlteam.com → sees rendered graph + artifacts
```

Meir and Adi open a URL in their browser. No installs. No accounts beyond the Cloudflare Access login.

---

## Card Extraction Decision: Background Extractor, Not Inline

### Decision

Skills do **not** create cards inline. Each skill writes its primary source file only. A dedicated `/extract-artifacts` skill reads any source file (report, meeting note, news item, discussion) and creates/updates paper cards, person cards, and organization cards.

`/extract-artifacts` does **not** create Claim or Evidence cards. Those artifact types are retired.

**Why not inline:**
- Skills would need to track dedup state ("has this author card been created yet?") — not their responsibility
- Adding a new card type would require updating every research skill
- The extractor can be re-run retroactively over any source if schemas evolve
- A meeting note or WhatsApp summary has no skill that "owns" it — the extractor is the single entry point for all source types

### Trigger options (not mutually exclusive)

| Trigger | When to use |
|---------|-------------|
| Post-run hook after each skill | Skill writes report → extractor runs immediately |
| Manual `/extract-artifacts <path>` | Drop a meeting note or news item, run extractor on it |
| Watch mode on `sources/` folder | Any new file dropped triggers extraction automatically |
| Nightly cron over full sources folder | Catch anything missed, re-extract after schema changes |

### Ingestion flow for non-skill sources

Non-skill sources (meetings, news, discussions) are ingested manually or via a future `/ingest` skill:

```
Team WhatsApp discussion → paste into sources/discussions/2026-06-04-adi-qcnn.md
                        → set frontmatter (source_type, date, participants)
                        → run /extract-artifacts on it
                        → research-question cards created at speculative status
                        → [[wikilinks]] added back to source file
```

---

## Deduplication Decision: Canonical IDs per Card Type

Before creating any card, the extractor checks whether a file with the canonical ID already exists.

| Card type | Canonical ID | Key field |
|-----------|-------------|-----------|
| Paper Card | arXiv ID | `2405.12345` |
| Person Card | `lastname-firstname` slug | `farhi-edward` |
| Organization Card | normalized name slug | `mit-center-for-quantum` |
| Research Hypothesis | topic slug | `rydberg-quantum-reservoir-computing` |
| Research Question | topic slug | `neutral-atom-graph-kernels` |

### Merge rules

| Situation | Action |
|-----------|--------|
| No existing card with this ID | Create new card |
| Existing card, additive fields (new paper citing same author) | Append to card, add [[wikilink]] |
| Existing card, factual field differs (different institution listed) | Log to `_conflicts.md`, do not overwrite |
| Existing hypothesis card, new paper provides additional support | Update `support_count`, append to `supporting_papers`, update `status` if warranted |

Conflicts accumulate in `_conflicts.md` for human review. The extractor never auto-resolves a contradiction.

---

## Wikilinks Decision: Artifact Schemas Must Emit Links

The knowledge graph is only as good as the links between cards. Every artifact schema must include a wikilinks section.

**Minimum required links:**

| From | Must link to |
|------|-------------|
| Paper Card | Person cards, Organization card, Research Hypothesis cards (if topic matches), Triage entry |
| Research Hypothesis | Paper Cards supporting/contradicting, related Hypotheses |
| Research Report | Paper Cards referenced, Research Question card, Hypothesis Ledger entries |
| Triage entry | Paper Card (if PASS) or termination reason |

Example footer in a Paper Card:
```markdown
## Links
- Paper: [[2405.12345]]
- Persons: [[cards/persons/farhi-edward]], [[cards/persons/goldstone-jeffrey]]
- Organizations: [[cards/organizations/mit-center-for-quantum]]
- Related hypotheses: [[cards/hypotheses/rydberg-quantum-reservoir-computing]]
- Triage: [[triage/2026-06-04_neutral-atom-graph]]
```

---

## Context Injection Decision: Index Files + Direct Card Reads

Skills query the knowledge base using three mechanisms, in order of scope:

### 1. Index files — broad context at workflow start

Skills load relevant indexes before beginning work:
```
hypothesis-ledger.md  → know which directions are already supported/refuted
paper-registry.md     → know which papers have been evaluated (avoid re-evaluation)
topic-map.md          → find prior work on the current topic
```

These are small curated files (tens to low hundreds of lines). The extractor keeps them current.

### 2. Direct card reads — specific entity lookup

When a skill encounters a known entity (arXiv ID, author name), it reads the card directly:
```
paper-cards/2405.12345.md exists? → load prior verdict, don't re-evaluate
persons/farhi-edward.md exists?   → load known context on this author
hypotheses/rydberg-qrc.md exists? → load prior hypothesis status before synthesis
```

### 3. Glob + grep — topic queries

"Find all STRONG_INTEREST paper cards on graph ML" → grep frontmatter across `paper-cards/`.

Used by synthesis and portfolio-review skills to build a context snapshot before writing.

---

## Frontmatter Convention

Every card must have YAML frontmatter with the canonical ID and card type, so indexes can be built by scanning frontmatter without reading full file content.

**Paper Card:**
```yaml
---
id: 2405.12345
type: paper-card
title: "Quantum Kernels for Graph ML with Neutral Atoms"
arxiv_id: 2405.12345
persons: [farhi-edward, goldstone-jeffrey]
organizations: [mit-center-for-quantum]
topics: [graph-ml, neutral-atom, quantum-kernels]
verdict: STRONG_INTEREST
claim_status: plausible
evaluated: 2026-06-04
source: sources/reports/paper-reviews/2405.12345-review-2026-06-04.md
extracted: true
---
```

**Research Hypothesis:**
```yaml
---
id: rydberg-quantum-reservoir-computing
type: research-hypothesis
title: "Rydberg Quantum Reservoir Computing for Temporal/Dynamical Learning"
strategic_value: directional          # foundational | directional | actionable | incremental
support_count: 3
status: plausible
qml_criteria_passed: [hardware_fit, geometric_difference]
supporting_papers: [2111.10956, 2602.00610, 2405.04799]
contradicting_papers: []
open_risks: [dequantization_risk, classical_baseline]
last_synthesized: 2026-06-11
synthesized_by: synthesize-hypotheses
---
```

---

## Implementation Phases

### Phase 1 — Foundation ✓
- [x] Create `qml-artifacts` git repo with folder structure (`sources/`, `cards/`, `indexes/`)
- [x] Update `workspace.json` `output_root` to point at it
- [ ] Install Quartz on Mac Mini, configure to read `qml-artifacts/`
- [ ] Set up Cloudflare Tunnel, verify team can access the site
- [ ] Set up Mac Mini cron for hourly git commits + nightly push

### Phase 2 — Artifact schemas ✓
- [x] Update Paper Card schema — remove claims/evidence from frontmatter
- [x] Define Research Hypothesis schema (replaces Claim Card + Evidence Card)
- [x] Retire Claim Card schema
- [x] Retire Evidence Card schema
- [x] Update index file formats (hypothesis-ledger replaces claim-ledger)

### Phase 3 — Extractor skill ✓
- [x] Update `/extract-artifacts` — remove claim/evidence card generation
- [x] Keep paper card, person, organization extraction unchanged
- [x] Update index-updater to write hypothesis-ledger instead of claim-ledger

### Phase 4 — Synthesize Hypotheses skill ✓
- [x] Build `/synthesize-hypotheses` skill
- [x] Implement: read paper cards grouped by topic, group claims by semantic similarity
- [x] Implement: filters (support_count ≥ 2, QML criteria, strategic_value, novelty check)
- [x] Implement: create/update Research Hypothesis cards
- [x] Implement: update hypothesis-ledger.md

### Phase 5 — qml-artifacts cleanup ✓
- [x] Delete `cards/claims/` files — retired
- [x] Delete `cards/evidence/` files — retired
- [x] Create `cards/hypotheses/` directory
- [x] Replace `claim-ledger.md` with `hypothesis-ledger.md`
- [x] Run first `/synthesize-hypotheses` pass on existing corpus

### Phase 6 — Context injection in skills
- [ ] Update `/qml-paper-review` to load `hypothesis-ledger.md` at start
- [ ] Update `/qml-deep-research` to load `hypothesis-ledger.md` + `topic-map.md` at start
- [ ] Update `/claim-promotion` to read from and write to Research Hypothesis cards directly

---

## Open Questions

- **`qml-artifacts` repo location:** local-only on Mac Mini with GitHub remote, or should Meir/Adi also have local clones? (Probably Mac Mini only — they access via Quartz site)
- **Conflict resolution workflow:** should `_conflicts.md` surface in the Quartz site as a "needs review" page? (Probably yes)
- **Nightly re-synthesis:** run `/synthesize-hypotheses` nightly to catch new paper cards — modified-only or full scan?
- **Hypothesis merge policy:** when does a Research Hypothesis graduate from `plausible` to `supported`? Proposal: when support_count ≥ 3 AND at least one paper has verdict STRONG_INTEREST AND all open_risks have been addressed.
