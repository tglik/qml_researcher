# Person Card Schema

Version: 2.0 | Written by: `/extract-artifacts`

One card per researcher or individual. Keyed by `lastname-firstname` slug. Accumulates across all papers and sources that mention the person. Covers academic researchers, industry practitioners, and anyone cited in a QML context.

---

## File Location

```
{output_root}/cards/persons/{lastname-firstname}.md
```

Example: `cards/persons/farhi-edward.md`

---

## Frontmatter

```yaml
---
id: farhi-edward
type: person-card
name: "Edward Farhi"
organizations: [mit-center-for-quantum]  # org-card slugs (all known affiliations)
papers: [2405.12345, 2301.67890]         # arXiv IDs of evaluated papers
first_seen: 2026-06-04
last_updated: 2026-06-04
---
```

---

## Full Schema

```markdown
# Person: {Full Name}

**Primary affiliation:** [[cards/organizations/{slug}]]
**Role:** {researcher | professor | industry | student | unknown}

---

## Papers evaluated

| arXiv ID | Title | Verdict | Date |
|----------|-------|---------|------|
| [[cards/paper-cards/{id}]] | {short title} | {verdict} | {date} |

## Known positions / affiliations

- {YYYY}–{YYYY}: {role} at [[cards/organizations/{org-slug}]]

## Notes

{Anything relevant to judging future papers by this person — known biases, strong areas, conflicts of interest.}

---

## Links

- Organizations: [[cards/organizations/{slug1}]], [[cards/organizations/{slug2}]]
- Papers: [[cards/paper-cards/{id1}]], [[cards/paper-cards/{id2}]]
```

---

## Dedup rules

- **Key:** `lastname-firstname` slug, all lowercase, hyphens only
- On conflict (two sources give different affiliations): log to `_conflicts.md`, keep first value; add secondary to `organizations` list
- On new paper by existing person: append row to Papers table, update `papers` and `last_updated`
- Name normalization: strip accents, Jr/Sr/II suffixes; "van der X" → `vander-x`
