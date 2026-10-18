---
thread: {thread}
date: {YYYY-MM-DD}
source_verdict: {NO-GO-FINAL | NO-GO-PROVISIONAL | CONDITIONAL-GO | KILLED-ON-PAPER | GO | BLOCKED}
recommendation: {close | publish | ip-first | new-cycle:<variant #>}
---

# Variants and pivot — {short name}

## Mechanism
**Primary cause:** {incorrect algorithm · exponential quantum resource · input-loading cost ·
readout cost · shot count · classical competitor / dequantization · classically simulable ·
trainability · noise sensitivity · classical not a real bottleneck · polynomial speedup too small
for overheads · advantage only on instances that do not matter}
**Stated as a precondition:** "{The failure happens because …}"
{For GO or BLOCKED: write "Variants not generated — <reason>" and fill only Salvage.}
{For NO-GO-PROVISIONAL: variants do not replace the reopening condition and do not unlock quantum spend.}

## Variants (≤ 10, best first)
| # | Idea (one sentence) | What changed | Why it escapes the failure | Target advantage · operating point | End-to-end cost before → after | G0–G3 quick check | New risks | Cheapest kill test |
|---|---|---|---|---|---|---|---|---|
| 1 | | | | | | | | |

{Or: "No viable variant — <reason>."}

**Potential, in brief** (one or two lines per variant, in rank order):
- 1: …

**Covered cases** (same gate, same mechanism — not variants; they go into the ledger entry):
- …

## Salvage
- **(a) Classical results worth keeping** (including a useful classical competitor — noted here, not ranked): …
- **(b) Instruments and protocols that transfer:** …
- **(c) Quantum variants** (only these re-enter the quantum program): → table above

## Pivot questions
| Question | Candidates | Argument | Rating |
|---|---|---|---|
| Q1 Algorithm changed slightly? | | | |
| Q2 Task changed slightly — still useful in practice? | | | |
| Q3 Sweet spot (size, instances, accuracy, noise)? | | | |

## Publication and IP
- **Paper?** What is new (negative result, benchmark, dequantization, quantum-inspired method, resource analysis) · venues · closest work · title / abstract / figures sketch.
- **Patent?** Novel technical elements · obvious prior art.
> ⚠️ Not legal advice — get a patent professional. **Any public disclosure (paper, preprint,
> talk) before filing may destroy novelty; decide the order before publishing anything.**

## Recommendation
{close · publish · IP-first · new cycle at intake with variant #n (and a draft HYPOTHESIS claim)}
