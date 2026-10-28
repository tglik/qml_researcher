# Writing lab instructions

Rules for every `ESSENCE.md`, `PROTOCOL.md`, persona file and `criteria/lab_method.md`. If a person
finds a file confusing, the model will too. Drawn from Anthropic's skill-authoring best practices,
OpenAI's GPT-5.x prompting guidance and Google's Gemini prompt-design guidance, plus Adi's and
Meir's review (October 2026).

## Say each rule once
- The science lives in `criteria/lab_method.md`. A role file points to it ("apply Rule 6") and never
  restates or paraphrases it. Restated rules drift apart, and contradictions cost the model more
  than missing detail does.
- One term per concept, defined once in the lab method glossary ("baseline", "ledger", "operating
  point", "cadence"). If you need a new term, add it to the glossary first. Say *classical
  competitor* for any classical method that could beat the quantum one; say *twin* only for the
  strict same-input, same-access case.

## Write plain sentences
- One idea per bullet. No slogans, no "⇒", no stacked dashes.
- Skip what the model already knows (what Clifford circuits or MPS are). Add only what is specific
  to this lab: our thresholds, our order of checks, our past mistakes.
- Use absolutes (never, must) only for invariants: role separation, the lock, provenance,
  honesty. For judgment calls, give the decision rule.

## Keep role files self-contained
- No bare experiment ids ("exp 07", "Amendment A", "M01") in role or skill files. If an example is
  needed, write it so a reader who never saw the experiment understands it.
- Worked precedents belong in the lab method, next to the rule they support.

## Use one shape
Essence: **Job** (one sentence) · **Place in the lab** (who comes before and after, what you
produce) · **How you work** · **Never** · **Example** (one good, one bad).
Protocol: Invoked by · Inputs · Output · Steps · May not · Return.

## Show, don't describe
One concrete good example and one concrete bad example beat a paragraph of adjectives.

## Write artifacts for a reader outside the field
These rules apply to `HYPOTHESIS.md`, the plan (`PROPOSAL.md`) and the experiment docs. The
reader is an ML engineer who is not a quantum or domain expert: a teammate, a partner, or the
next agent. Good papers explain what the reader needs and cite the rest.
- **Message first.** Open with the point in a paragraph; details follow.
- **Define or cite every term** the first time, or put it in *Background*. Domain terms count too.
- **Say what the method does and why.** Describe the algorithm step by step, give a reason for
  every design choice, and for every hypothesis say why we expect it and why it is worth testing.
- **Use standard academic terms:** "baseline", "proposed method", "held-out set". Do not use lab
  shorthand in prose: no "arm", gate ids (G5), rule numbers or panel issue numbers. Lock ids appear
  only in an experiment's *Locked rules* section and in references to it.
- **Keep history out.** Revisions and panel responses go to `change_log.md`; the documents always
  read as the current design.
- **Short beats complete.** If a section needs more than a screen, move the detail to the
  experiment doc or `frozen_definitions.md` and link it.
