# Author Card Schema

Version: 1.0 | Written by: `/extract-artifacts`

One card per researcher. Keyed by `lastname-firstname` slug. Accumulates across all papers and sources that mention the author.

---

## File Location

```
{output_root}/cards/authors/{lastname-firstname}.md
```

Example: `cards/authors/farhi-edward.md`

---

## Frontmatter

```yaml
---
id: farhi-edward
type: author-card
name: "Edward Farhi"
institute: mit-center-for-quantum     # primary institute slug
papers: [2405.12345, 2301.67890]      # arXiv IDs of evaluated papers
first_seen: 2026-06-04
last_updated: 2026-06-04
---
```

---

## Full Schema

```markdown
# Author: {Full Name}

**Institute:** [[cards/institutes/{slug}]]
**Role:** {researcher | professor | industry | unknown}

---

## Papers evaluated

| arXiv ID | Title | Verdict | Date |
|----------|-------|---------|------|
| [[cards/paper-cards/{id}]] | {short title} | {verdict} | {date} |

## Known positions / affiliations

- {YYYY}–{YYYY}: {role} at {institution}

## Notes

{Anything relevant to judging future papers by this author — known biases, strong areas, conflicts of interest.}

---

## Links

- Institute: [[cards/institutes/{slug}]]
- Papers: [[cards/paper-cards/{id1}]], [[cards/paper-cards/{id2}]]
```

---

## Dedup rules

- **Key:** `lastname-firstname` slug, all lowercase, hyphens only
- On conflict (two sources give different institutes): log to `_conflicts.md`, keep first value
- On new paper by existing author: append row to Papers table, update `papers` frontmatter list and `last_updated`
- Name normalization: strip accents, Jr/Sr/II suffixes; "van der X" → `vander-x`
