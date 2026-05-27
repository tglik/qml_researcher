---
name: qml-fetch-arxiv
version: 1.0.0
description: |
  Helper skill: fetch a paper from arXiv by ID, URL, or title search.
  Returns title, abstract, introduction text, arXiv ID, venue, venue_tier,
  and partial_fetch flag — ready for /qml-triage or /qml-evaluate to consume.
  Can be invoked standalone to retrieve paper content without running triage.
  Auto-invoked by /qml-triage when input is an arXiv ID, arXiv URL, or plain
  title string.
input:
  - arXiv ID: 2401.12345 or 2401.12345v2
  - arXiv URL: https://arxiv.org/abs/2401.12345 or https://ar5iv.org/abs/...
  - arxiv: prefix: arxiv:2401.12345
  - Plain title or keyword string → triggers arXiv search
output:
  - Structured paper content: title, abstract, intro_text, arxiv_id, venue, venue_tier, partial_fetch
  - Printed to stdout in a readable block; usable as input to /qml-triage Phase 1+
---

# /qml-fetch-arxiv

Fetch any arXiv paper by ID, URL, or title. Handles ar5iv redirects, arXiv API fallback,
and title search automatically.

---

## Phase 1: Parse Input and Determine Fetch Mode

### 1.1 Classify the input

| Input | Action |
|-------|--------|
| Matches `\d{4}\.\d{4,5}(v\d+)?` (bare ID or with `arxiv:` prefix) | Extract numeric ID, strip version suffix → go to Phase 2 |
| URL contains `arxiv.org/abs/` or `ar5iv` | Extract the ID segment after `/abs/` → go to Phase 2 |
| URL is `https://arxiv.org/pdf/{id}` | Extract ID from path → go to Phase 2 |
| Plain text (no URL scheme, no ID pattern) | → go to Phase 1.2 (title search) |

Strip any `v\d+` version suffix before storing the canonical ID.

### 1.2 Title Search (if input is plain text)

**Goal:** Find the most likely arXiv paper matching the title or keywords.

**Step 1:** Build a search URL:
```
https://arxiv.org/search/?searchtype=all&query={url-encoded title}&start=0&order=-relevance
```

`WebFetch` this URL with prompt:
> List the first 3 result entries: arXiv ID, title, authors, submission date. Format as a numbered list.

**Step 2:** If 1 clear match — proceed with that arXiv ID.

**Step 3:** If multiple plausible matches — print them and ask:
```
Multiple papers found. Which one did you mean?
  1. {id} — {title} ({year}) — {authors}
  2. {id} — {title} ({year}) — {authors}
  3. {id} — {title} ({year}) — {authors}
Enter the number, or provide the arXiv ID directly.
```
Wait for user selection before continuing.

**Step 4:** If no matches — try `WebSearch site:arxiv.org "{title}"` as a fallback.
If still no match:
```
Error: Could not find a paper matching "{input}" on arXiv.
Try providing the arXiv ID directly (e.g., 2401.12345).
```
Stop.

### Gate: Phase 1 → Phase 2
- Canonical arXiv ID extracted ✓

---

## Phase 2: Fetch Paper Content

### 2.1 Primary fetch — ar5iv

`WebFetch https://ar5iv.org/abs/{arxiv_id}` with prompt:
> Extract: (1) the full paper title, (2) the complete abstract, (3) the full text of the Introduction section (everything under the "Introduction" or "1. Introduction" heading until the next section heading). Also note: the venue or conference name if mentioned, any acknowledgment of submission to a conference or journal.

**Handle the ar5iv redirect:** ar5iv.org currently redirects to `ar5iv.labs.arxiv.org`. If a redirect is returned, immediately follow it:
`WebFetch https://ar5iv.labs.arxiv.org/abs/{arxiv_id}` with the same prompt.

If the page is found and content is non-empty → set `fetch_mode = "ar5iv"`, `partial_fetch = false`.

### 2.2 Fallback — arXiv API

If ar5iv returns 404, empty body, or content clearly lacks the paper text (paper too new to be indexed — typically < 48h from submission):

`WebFetch https://export.arxiv.org/abs/{arxiv_id}` with prompt:
> Extract: the paper title and abstract from the XML/HTML response. Look for <title> and <summary> tags or equivalent.

If successful → set `fetch_mode = "arxiv_api"`, `partial_fetch = true`.
Note: fallback gives abstract only, no introduction.

If both fail:
```
Error: Could not fetch {arxiv_id}.
  ar5iv: {status}
  arXiv API: {status}
Check the ID is correct. If the paper was submitted in the last 48 hours, try again tomorrow.
```
Stop.

### Gate: Phase 2 → Phase 3
- Title extracted ✓
- Abstract extracted ✓
- Introduction extracted (or `partial_fetch = true` if abstract-only) ✓

---

## Phase 3: Extract Venue and Tier

### 3.1 Detect venue

Look in the fetched text for venue signals:
- "Submitted to {venue}" or "Published in {venue}" or "Accepted at {venue}"
- Conference/journal name in the header or footnote
- arXiv subject class (e.g., `quant-ph`, `cs.LG`, `cs.AI`) — use as hint but not venue

If no venue found: `venue = "arXiv preprint"`.

### 3.2 Assign venue tier

Use the tier table from `criteria/qml_domain.md`:

| Tier | Venues |
|------|--------|
| T1 | Nature, Science, PRL, PRX Quantum, NeurIPS, ICML, ICLR |
| T2 | QST (IOP), npj Quantum Information, PRApplied, JMLR, CVPR, AAAI |
| T3 | NeurIPS/ICML workshops, QIP contributed talks |
| T4 | arXiv with ≥20 citations within 1 year |
| T5 | arXiv < 1 year, < 20 citations |
| unknown | Cannot determine |

Default: `T5` for unconfirmed preprints. If venue is known, assign accordingly.

### Gate: Phase 3 → Phase 4
- `venue` assigned ✓
- `venue_tier` assigned ✓

---

## Phase 4: Output

Print the extracted content in a structured block for use by the caller (`/qml-triage`, `/qml-evaluate`, or the user directly):

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ARXIV FETCH RESULT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
arXiv ID:      {arxiv_id}
Title:         {full title}
Venue:         {venue}
Venue tier:    {T1 | T2 | T3 | T4 | T5 | unknown}
Fetch mode:    {ar5iv | arxiv_api}
Partial fetch: {true | false}

Abstract:
{full abstract text}

Introduction (first section):
{introduction text, or "Not available — abstract-only fetch" if partial_fetch = true}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

If invoked standalone (not from within `/qml-triage`), end here.
If invoked as part of `/qml-triage` Phase 0-A, pass the above content directly into Phase 1.

---

## Failure Modes

| Failure | Symptom | Mitigation |
|---------|---------|-----------|
| ar5iv redirect not followed | Redirect returned as error, no content | Always retry with `ar5iv.labs.arxiv.org` on first redirect |
| Paper too new for ar5iv | 404 or empty body | Fall back to arXiv API immediately; mark `partial_fetch = true` |
| Title search returns wrong paper | ID fetched but content doesn't match | Print title from fetched page; confirm with user before proceeding |
| Venue not stated in preprint | Can't assign tier | Default to T5; note "venue not stated in fetched text" |
| arXiv search returns 0 results | Unusual title or typo | Try WebSearch as fallback; ask user for direct ID |
