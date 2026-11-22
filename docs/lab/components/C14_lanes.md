# C14 — Lanes: steps and bets

**Date:** 2026-11-22 · **Status:** built (`lab/tools/backlog.py`: `lane`, `bet`, `panel`, lane-aware
`queue`, `order` and `direction rank`) · **Design doc:** "Idea scoring: lanes, not one number"
(Claude Doc, https://claude.ai/artifact/RezExA3WRC8iJeiNx9N3bU) · **Replaces:** the single rank of C13
for picking candidates; the C13 gate is unchanged.

## Why
One score, rung × p × (0.5 + novelty), with a capped linear payoff, favours cheap likely
measurements: on 2026-11-22 the top 8 of 67 were tools and measurements, and the 4 rung-4 bets sat at
9, 19, 26 and 29. The p values were one agent's single guess. Documented practice does not rank bets
this way: strategic buckets before ranking (Cooper et al. portfolio studies), the Heilmeier
Catechism for whether a bet is clear and checkable, X's "monkey first" for the order of work, real
options for buying cheap information on large upside, and lotteries only for real ties (SNSF).

## Rules
| | Steps lane | Bets lane |
|---|---|---|
| Belongs | a publishable step on our path | if it works, our method beats a strong classical baseline (upside 4–5) |
| Lane source (first that applies) | a person's `lane` | then the panel: upside median ≥ 4, or one judge ≥ 4 with a split panel or a champion; then an agent's sheet; then rungs 4 and 6 |
| Effort share | `LANE_SHARE["step"]` 0.5 | `LANE_SHARE["bet"]` 0.5 (Tsahi, 2026-11-22) |
| Order | band A (EV ≥ 1.2) · B (≥ 0.6) · C, fixed lottery inside a band | sheet · contested · upside · cheapest fatal test |
| p | inside EV | only the floor `BET_P_FLOOR` 0.05 |

- **Bet sheet** (`backlog bet CID --sheet FILE.json`): the eight Heilmeier answers (`HEILMEIER`),
  upside, insight, fatal test, its cost in days, and a no-go check. Upside below 4 moves the candidate
  to steps. Sheets are stored in `{OUTPUT_ROOT}/indexes/backlog/bet_sheets/` and are drafts until a
  person or the panel reviews them.
- **Monkey first:** inside a direction, after prerequisites and what others wait on, a sheeted bet
  whose fatal test costs ≤ `QUICK_FATAL_DAYS` (5) starts first.
- **Ties:** a direction score carries a relative error bar from its confidence (high 15%, medium
  30%, low 50%). Directions overlapping the group leader's bar are tied; inside a tie the cheapest
  fatal test among sheeted bets goes first, and a direction with none loses the tie.
- **Multi-model inputs:** `backlog panel scores.jsonl` imports the panel of
  `lab.tools.panel` (rubric `lab/rubrics/backlog_lanes.json`: gates `no_go`, `on_path`; scores
  `rung`, `plausibility`, `upside`, `insight`, `fatal_test_days`, `champion`). Medians replace the
  gate agent's numbers. A champion from any judge, or a contested upside or plausibility, marks a bet
  contested (the wildcard rule of Villum Fonden and Volkswagen Stiftung) and moves it up its lane.
  A panel `no_go` median ≥ 0.5 removes a bet.

## First panel run (2026-11-22)
Two model families (Claude Opus, GPT) scored all 77 candidates (qml_artifacts PR #13, n_eff about
1.2 of 2 on upside and plausibility). Imported into a copy of the backlog: no candidate on an open
direction reaches the bets lane. The three sheeted bets get upside medians of 2.5–3; the panel
scored the original claims, not the narrowed sheets. With a 50% bet share, that half of the effort
has nothing to fund until sources produce bets or the panel rescores the narrowed claims.

## What would prove this wrong
Record, per lane, how far closed candidates got (`outcome --rung`). After 10 closed bets: if sheeted
bets with a cheap fatal test do not kill or confirm faster than steps, drop monkey-first; if no bet
ever reaches rung 4, the bets lane is measuring our sources, not our scoring, and the fix belongs in
the sources (one direct bet per open direction's target algorithm).
