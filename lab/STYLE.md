# Writing lab instructions

Rules for every `ESSENCE.md`, `PROTOCOL.md`, persona file and `criteria/lab_method.md`. If a person
finds a file confusing, the model will too. Drawn from Anthropic's skill-authoring best practices,
OpenAI's GPT-5.x prompting guidance and Google's Gemini prompt-design guidance, plus Adi's and
Meir's review (October 2026).

## Say each rule once
- The science lives in `criteria/lab_method.md`. A role file points to it ("apply Rule 6") and never
  restates or paraphrases it. Restated rules drift apart, and contradictions cost the model more
  than missing detail does.
- One term per concept, defined once in the lab method glossary ("arm", "ledger", "operating
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
