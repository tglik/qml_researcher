---
thread: {thread}
checkpoint: {CP1 | CP2 | CP3 | CP4 | CP5 | ESCALATION:<type>}
mode: {HUMAN_APPROVE | HUMAN_SPOTCHECK | AGENT}
author: {agent:<role> | <person>}
eligible_signers: [{people who are not the author}]
date: {YYYY-MM-DD}
---

# Decision needed — {one line}

**Recommendation:** {what the agent recommends, in one sentence}

**Why:** {3–5 bullets, each with an artifact link}
-

**What it costs to continue:** {compute, time, human time}

**Options**
1. {…}
2. {…}

**The human's job here:** {e.g. CP2 — "is this the right question? is the operating point real?
are the thresholds defensible?" — not re-deriving the analysis}

**Reply with:**
```
/qml-lab sign {thread} {CP} --by <name> --outcome unchanged|minor|material --minutes <n> [--note "…"]
```
