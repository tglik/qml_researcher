# Explainer — protocol

## Invoked by
`/qml-ingest` phase 4 (Explain): one fresh instance per batch of at most 6 candidates of one
direction, or at most 3 directions.

## Inputs (read these; nothing else is handed to you)
- The entity: its line in `{OUTPUT_ROOT}/indexes/backlog/candidates.jsonl` (title, claim, base,
  gate record: novelty, screen, value, potential) or its entry in `directions.json`.
- For a candidate, its direction's entry; for a direction, the titles and claims of its candidates.
- The base papers named in `base` and in the gate evidence: abstract and introduction, through
  `/fetch-arxiv` or WebFetch on `arxiv.org/abs/<id>`. Open at least the first base paper.
- `criteria/advantage_potential.md` (the seven questions) and `criteria/lab_method.md`.
- The previous explainer file, if one exists (rewrite it; keep what is still correct).

## Output
One file per entity, exactly this shape:
- candidate: `{OUTPUT_ROOT}/indexes/backlog/explainers/candidates/<cid>.md`
- direction: `{OUTPUT_ROOT}/indexes/backlog/explainers/directions/<id>.md`

Front matter is flat `key: value` lines (no nesting); lists are `[a, b]`:
```
---
id: <cid or direction id>
kind: candidate | direction
bet: kill-test | quantum-inspired | mechanism-probe | advantage-bet | resource-estimate | unscreened | mixed
quantum_case: none | weak | plausible | strong
tagline: <one sentence, at most 140 characters, no hype>
confidence: speculative | plausible | observed
claim_hash: <output of `python -m lab.tools.backlog explain-hash <id>`>
sources: [arXiv:XXXX.XXXXX, ...]
written_by: explainer
written_at: <YYYY-MM-DD>
check_status: draft
---
```

**Bet** follows the value rung: 1 kill-test, 2 quantum-inspired, 3 mechanism-probe, 4 and 6
advantage-bet, 5 resource-estimate, no value record `unscreened`. A direction is `mixed` unless all
its candidates share one bet. If the claim itself contradicts its rung, keep the rung's bet and say
so in "The real motivation".

**Quantum case** is a verdict, capped by the bet and the potential profile:
- kill-test, quantum-inspired → `none` or `weak` only.
- `strong` only for an advantage-bet or resource-estimate whose potential answers are
  mechanism = 2 and window = 2. `plausible` needs mechanism ≥ 1. No potential record → at most `weak`
  for a candidate, unless the gate notes name a mechanism and a hard regime.
- When unsure, choose the weaker verdict.

**Confidence** is `speculative` for every backlog item unless a lab verdict exists for it.

Body sections, in this order, with exactly these headings.

Candidate (450 to 1,100 words):
1. `## In plain words` — the claim restated for a non-specialist, 2 to 4 sentences.
2. `## Background` — the concepts the claim depends on, taught from scratch.
3. `## The real motivation` — what we actually get if it works, in one paragraph. Name the
   kind of result (publishable negative, measured mechanism, resource estimate, method, separation)
   and who would care. A publishable kill is a fine motivation; say so plainly.
4. `## Why quantum, honestly` — the first sentence states the verdict in words ("The quantum case
   here is weak."). Then the reason, tied to the mechanism, the structure and the hard regime. For a
   kill test, explain why we expect a classical method to match.
5. `## Why it might fail` — the strongest classical competitor and the main risks, from the
   screen notes.
6. `## What we learn either way` — the outcome if it works and if it fails.
7. `## Cost and feasibility` — sizes, simulator or hardware, rough effort, from the gate record.
8. `## Sources` — a bullet per source actually opened: `- arXiv:XXXX.XXXXX — title`.

Direction (800 to 1,700 words): `## In plain words`, `## Background`, `## The real motivation`,
`## Why quantum, honestly`, `## The case against`, `## If it works`, `## Why now`,
`## What closes it`, `## Sources`.

## Style
- Plain prose; bullets only for parallel items. Sentences under 25 words where possible.
- Define jargon in place: "geometric difference (a measure of how differently two kernels see
  the same data)". One analogy per page is plenty.
- No notation beyond simple inline symbols; no LaTeX.
- Banned unless quantum_case is plausible or strong: "outperforms", "beats classical",
  "quantum advantage" used as a fact, "exponential speedup", "superior", "revolutionary". Words
  like "breakthrough", "unprecedented", "game-changing" are banned everywhere.
- Attribute results: "the authors report", "the gate found".

## Steps
1. Read the inputs. Open the base papers. Note what each source says that you will use.
2. Compute the claim hash with `python -m lab.tools.backlog explain-hash <id>`.
3. Decide bet and quantum case from the rules above before writing a word of prose.
4. Write the file.
5. Run `python -m lab.tools.backlog validate --explainers` and fix every error on your files.

## May not
- Write `check_status: signed` or any `checked_*` field.
- Cite a source you did not open.
- Add sections, drop sections or rename headings.
