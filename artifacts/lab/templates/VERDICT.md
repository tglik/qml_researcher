---
id: {slug}
type: experiment
title: "{Short name — the question}"
program: {program slug}
experiment_number: "{NN}"
topics: [{topic}, …]
verdict: {GO | CONDITIONAL-GO | NO-GO-FINAL | NO-GO-PROVISIONAL | BLOCKED}
claim_status: observed
evaluated: {YYYY-MM-DD}
thread: {thread}
audit: {pending | CONFIRMED | OVERTURNED | INSUFFICIENT}
ledger: []
---

# Verdict — {short name}

## Outcome
**{VERDICT}** — {three to five plain-language sentences a non-specialist can act on.}
{GO / CONDITIONAL-GO only: advantage type (provable asymptotic / heuristic asymptotic /
practical), the resource where it shows, confidence (high/medium/low) with the reason,
and the conditions.}

## Gate by gate
| Gate (lock id) | Outcome | Evidence (file:line or provenance id) |
|---|---|---|

## Hypotheses — tested range vs absence
| Hypothesis | Result | "Not shown in tested range" or "shown absent" | Evidence |
|---|---|---|---|

## Mechanism
{Why it held or failed, structurally. The narrowest class this generalizes to.}

## What this licenses — and what it does not
- Licenses: …
- Does not license: …

## Negative Verdict Standard (NO-GO only)
| | Holds? | Note |
|---|---|---|
| N1 baseline adequacy | | |
| N2 gate integrity | | |
| N3 discriminating power | | |
| N4 mechanism named | | |
| N5 independent audit | pending | set by /qml-audit |

## What survives regardless
{Classical results, instruments, datasets and protocols that transfer even though the quantum
claim did not. Not a consolation section — write "none" only if genuinely none.}

## Reopening condition
{PROVISIONAL: the named experiment that would reopen it. Otherwise: next step.}

---

## Graph links
### Why it matters
### Caveats
### Related
- Program siblings: …
- Hypothesis tested: [[cards/hypotheses/…]]
- Related papers: …
