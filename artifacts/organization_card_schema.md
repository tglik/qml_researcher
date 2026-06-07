# Organization Card Schema

Version: 1.0 | Written by: `/extract-artifacts`

One card per organization. Keyed by a slug derived from the org name. Covers universities, research labs, commercial companies, government agencies, and consortia. Created automatically when a person card lists a new affiliation.

---

## File Location

```
{output_root}/cards/organizations/{org-slug}.md
```

Example: `cards/organizations/mit-center-for-quantum.md`

---

## Frontmatter

```yaml
---
id: mit-center-for-quantum
type: organization-card
name: "MIT Center for Quantum Engineering"
org_type: university             # university | research-lab | company | government | consortium
parent_org: mit                  # parent org slug, or null
location: "Cambridge, MA, USA"
persons: [farhi-edward, goldstone-jeffrey]   # person-card slugs affiliated here
papers: [2405.12345, 2301.67890]             # arXiv IDs where this org appears
first_seen: 2026-06-04
last_updated: 2026-06-04
---
```

---

## Full Schema

```markdown
# Organization: {Full Name}

**Type:** university | research-lab | company | government | consortium
**Parent:** [[cards/organizations/{parent-slug}]] | N/A
**Location:** {city, country}
**Website:** {url | unknown}

---

## Affiliated persons

| Person | Role | Period |
|--------|------|--------|
| [[cards/persons/{slug}]] | {professor | researcher | engineer | ...} | {YYYY–YYYY or "current"} |

## Papers from this org

| arXiv ID | Title | Verdict | Date |
|----------|-------|---------|------|
| [[cards/paper-cards/{id}]] | {short title} | {verdict} | {date} |

## Notes

{Research focus areas, known strengths or weaknesses in QML, funding sources, industrial partnerships.}

---

## Links

- Persons: [[cards/persons/{slug1}]], [[cards/persons/{slug2}]]
- Papers: [[cards/paper-cards/{id1}]], [[cards/paper-cards/{id2}]]
- Parent org: [[cards/organizations/{parent-slug}]]
```

---

## Dedup rules

- **Key:** short stable slug — abbreviation for well-known orgs (e.g., `mit`, `google-quantum-ai`, `pasqal`); full slugified name otherwise
- On conflict (same org listed under two slightly different names): merge into canonical slug, log alias in `_aliases.md`
- On new person or paper: append row to relevant table, update `persons`/`papers` frontmatter lists and `last_updated`
- Slug normalization: lowercase, hyphens only, drop "the", "of", "for", "and"; max 5 tokens

## Org type definitions

| Type | Examples |
|------|---------|
| `university` | MIT, ETH Zurich, Caltech |
| `research-lab` | Google Quantum AI, IBM Research, QuEra |
| `company` | Pasqal, Atom Computing, IonQ |
| `government` | DARPA, DOE national labs, DLR |
| `consortium` | QED-C, Quantum Flagship, NSF Quantum Leap |
