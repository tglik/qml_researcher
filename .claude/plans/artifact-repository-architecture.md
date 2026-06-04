# Artifact Repository Architecture

**Date:** 2026-06-04  
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
| `skill-report` | Paper Card, Claim, Evidence, Author, Institute | `observed` (audit required to go higher) |
| `meeting-note` | Research Question, decision log entries, action items | `speculative` |
| `discussion` | Early claims, signals, research questions | `speculative` |
| `news-item` | Company cards, funding events, partnership signals | `speculative` |
| `document` | Research Question, Institute, strategic context | `plausible` |

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

```
cards/
  paper-cards/
    2405.12345.md           ← keyed by arXiv ID
  authors/
    farhi-edward.md         ← keyed by lastname-firstname slug
  institutes/
    mit-center-for-quantum.md
  claims/
    2405.12345-claim-01.md  ← keyed by paper_id + claim_slug
  evidence/
    2405.12345-claim-01-ev-01.md
  research-questions/
    neutral-atom-graph-kernels.md
```

### Layer 3 — Indexes

Aggregated views maintained by the extractor. Small files, loaded by skills at workflow start as context preamble.

```
indexes/
  claim-ledger.md     ← all claims + current status ladder position
  author-index.md     ← all known authors + their paper IDs
  topic-map.md        ← papers grouped by topic/direction
  paper-registry.md   ← all evaluated papers + verdict + date
```

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

Skills do **not** create cards inline. Each skill writes its primary source file only. A dedicated `/extract-artifacts` skill reads any source file (report, meeting note, news item, discussion) and creates/updates all cards.

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
                        → claim cards created at speculative status
                        → [[wikilinks]] added back to source file
```

This keeps the same pipeline regardless of whether input came from a skill or a human.

---

## Deduplication Decision: Canonical IDs per Card Type

Before creating any card, the extractor checks whether a file with the canonical ID already exists.

| Card type | Canonical ID | Key field |
|-----------|-------------|-----------|
| Paper Card | arXiv ID | `2405.12345` |
| Author Card | `lastname-firstname` slug | `farhi-edward` |
| Institute Card | normalized name slug | `mit-center-for-quantum` |
| Claim Card | `paper_id-claim-slug` | `2405.12345-claim-01` |
| Evidence Card | `paper_id-claim_id-ev-N` | `2405.12345-claim-01-ev-01` |
| Research Question | topic slug | `neutral-atom-graph-kernels` |

### Merge rules

| Situation | Action |
|-----------|--------|
| No existing card with this ID | Create new card |
| Existing card, additive fields (new paper citing same author) | Append to card, add [[wikilink]] |
| Existing card, factual field differs (different institution listed) | Log to `_conflicts.md`, do not overwrite |
| Existing card, claim status would be downgraded | Log to `_conflicts.md`, do not overwrite — claim status only moves forward via `/claim-promotion` |

Conflicts accumulate in `_conflicts.md` for human review. The extractor never auto-resolves a contradiction.

### Claim dedup (v0 policy)

Claims across different papers are **not auto-merged** in v0. Each claim card is scoped to its source paper (`paper_id-claim-slug`). When the same hypothesis appears in multiple papers, `[[wikilinks]]` connect the related claim cards. A human (or a future `/claim-merge` skill) creates a "Research Hypothesis" card to aggregate them once the pattern is clear.

This avoids false merges (two papers using similar wording for different claims) at the cost of some redundancy.

---

## Wikilinks Decision: Artifact Schemas Must Emit Links

The knowledge graph is only as good as the links between cards. Every artifact schema must include a wikilinks section.

**Minimum required links:**

| From | Must link to |
|------|-------------|
| Paper Card | Author cards, Institute card, Claim cards, Triage entry |
| Claim Card | Paper Card, Evidence cards, related Claim cards (cross-paper) |
| Evidence Card | Paper Card, Claim Card it supports/contradicts |
| Research Report | Paper Cards referenced, Research Question card, Claim Ledger entries |
| Triage entry | Paper Card (if PASS) or termination reason |

Example footer in a Paper Card:
```markdown
## Links
- Paper: [[2405.12345]]
- Authors: [[farhi-edward]], [[goldstone-jeffrey]]
- Institute: [[mit-center-for-quantum]]
- Claims: [[2405.12345-claim-01]], [[2405.12345-claim-02]]
- Triage: [[triage/2026-06-04_neutral-atom-graph]]
```

---

## Context Injection Decision: Index Files + Direct Card Reads

Skills query the knowledge base using three mechanisms, in order of scope:

### 1. Index files — broad context at workflow start

Skills load relevant indexes before beginning work:
```
claim-ledger.md  → know which claims are already supported/refuted
paper-registry.md → know which papers have been evaluated (avoid re-evaluation)
topic-map.md     → find prior work on the current topic
```

These are small curated files (tens to low hundreds of lines). The extractor keeps them current.

### 2. Direct card reads — specific entity lookup

When a skill encounters a known entity (arXiv ID, author name), it reads the card directly:
```
paper-cards/2405.12345.md exists? → load prior verdict, don't re-evaluate
authors/farhi-edward.md exists?   → load known context on this author
```

### 3. Glob + grep — topic queries

"Find all STRONG_INTEREST paper cards on graph ML" → grep frontmatter across `paper-cards/`.

Used by synthesis and portfolio-review skills to build a context snapshot before writing.

---

## Frontmatter Convention

Every card must have YAML frontmatter with the canonical ID and card type, so indexes can be built by scanning frontmatter without reading full file content.

```yaml
---
id: 2405.12345
type: paper-card
title: "Quantum Kernels for Graph ML with Neutral Atoms"
arxiv_id: 2405.12345
authors: [farhi-edward, goldstone-jeffrey]
institute: mit-center-for-quantum
topics: [graph-ml, neutral-atom, quantum-kernels]
verdict: STRONG_INTEREST
claim_status: plausible
evaluated: 2026-06-04
---
```

---

## Implementation Phases

### Phase 1 — Foundation (implement next)
- [ ] Create `qml-artifacts` git repo with folder structure (`sources/`, `cards/`, `indexes/`)
- [ ] Update `workspace.json` `output_root` to point at it
- [ ] Install Quartz on Mac Mini, configure to read `qml-artifacts/`
- [ ] Set up Cloudflare Tunnel, verify team can access the site
- [ ] Set up Mac Mini cron for hourly git commits + nightly push

### Phase 2 — Artifact schemas
- [ ] Update Paper Card schema with wikilinks section and frontmatter convention
- [ ] Define Claim Card schema
- [ ] Define Author Card schema
- [ ] Define Evidence Card schema
- [ ] Define index file formats (claim-ledger, paper-registry, topic-map)

### Phase 3 — Extractor skill
- [ ] Build `/extract-artifacts` skill — handles all source types via `source_type` frontmatter field
- [ ] Implement extraction rules per source type (skill-report → full card suite; meeting-note → research questions + decisions; news-item → company/funding context)
- [ ] Implement claim status ceiling enforcement per source type
- [ ] Implement canonical ID generation per card type
- [ ] Implement dedup check (read existing card by ID before writing)
- [ ] Implement conflict logging to `_conflicts.md`
- [ ] Implement index update (append to paper-registry, update claim-ledger)
- [ ] Wire as post-run hook after `/paper-review` and `/qml-triage`
- [ ] Document manual ingestion flow for meetings, discussions, news

### Phase 4 — Context injection in skills
- [ ] Update `/paper-review` to load `paper-registry.md` at start (skip already-evaluated papers)
- [ ] Update `/deep-research` to load `claim-ledger.md` + `topic-map.md` at start
- [ ] Update `/claim-promotion` to read from and write to claim cards directly

---

## Open Questions

- **`qml-artifacts` repo location:** local-only on Mac Mini with GitHub remote, or should Meir/Adi also have local clones? (Probably Mac Mini only — they access via Quartz site)
- **Conflict resolution workflow:** should `_conflicts.md` surface in the Quartz site as a "needs review" page? (Probably yes)
- **Nightly re-extraction:** run `/extract-artifacts` over all reports nightly to catch schema changes, or only on new/modified files? (Modified-only in v0, full scan weekly)
- **Claim merge policy:** when to graduate from per-paper claim cards to cross-paper Research Hypothesis cards — manual trigger or skill-prompted?
