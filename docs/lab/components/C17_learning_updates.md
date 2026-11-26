# C17: Study learnings into the backlog

**Date:** 2026-11-26 · **Status:** built (`lab/tools/backlog.py`: `line`, `learn`, `review`,
lines-aware `order` and `direction rank`; `lab/tools/workspace.py`: `agenda`) · **Builds on:** C13
start order, C14 lanes, C16 study workspace.

## Why
After Lab 1 studies 1 to 3 (2026-11-25) the portfolio analyst recommended, by hand, that the lab
pause the Rydberg coupling-learning sub-line except for one fatal test (c-20261125-007), and run that
test before c-20261111-008. Tsahi asked whether changes to the direction score could make these
decisions. They cannot, and should not:

- **Order inside a direction is not set by the direction score.** The order comes from candidate
  fields (prerequisites, cheapest fatal test, bands), and the lab agenda in `lab.json` was typed by
  hand and ignored even that.
- **A score threshold for pausing would fire on noise.** Direction scores are one agent's
  plausibility × impact, with a ±30% bar at medium confidence. The move from 0.525 to 0.42 stayed
  inside the overlap with the 0.60 directions, so it moved nothing. A threshold low enough to matter
  would trip when an analyst types a slightly different number.
- **It hits the wrong unit.** Both refutations were about one mechanism: quantum resources make
  Rydberg coupling learning cheaper. The direction's main target, a learner on Rydberg data, had
  not been tested. A penalty on the whole direction drags down ideas that were never tested.
- **Fixed penalties on siblings are wrong both ways.** c-20261125-007 was written to avoid the
  exact failure (identifiability, which a Fisher test cannot see). A blanket discount would punish
  it, and ignoring the result would leave c-20261125-003 (a detuning choice, which s-003's global
  control already covered) at its old p.

So kill and pause decisions follow explicit rules, the order is derived from the backlog, and
scores change only through a recorded review.

## Rules
1. **The tested candidate closes with the verdict.** `backlog learn SID` reads a released study's
   state (`from`, `outcome`), records the evidence on the candidate and closes it.
2. **Lines and two strikes.** A line is a group of candidates in one direction that share one
   mechanism, stated as the assumption a refutation would hit (`line add --mechanism`). A refuted
   study is a strike on its candidate's line. After `STRIKES_TO_PAUSE` (2) strikes the line pauses
   on its own. Its candidates leave the start order, except one named **last test**
   (`line last-test --kill`) with its kill number written down beforehand. If the last test is
   supported, the line reopens. If it is refuted or inconclusive, the line stays paused, and only a
   person reopens it (`line set --status open --by`). The strikes stay on record, so the next
   refutation pauses it again.
3. **Review, not a multiplier.** `learn` marks every open sibling in the line "review due", along
   with the direction's assessment if it is older than the release. Siblings added or value-scored
   after the release are not marked, because they already saw the result. Each sibling records
   `review --effect kills|weakens|strengthens|none --why`. `weakens` and `strengthens` are refused
   until the value score (p) has been redone after the study. `none` must say why the claim
   survives the result. A candidate with a review due waits in the start order. The direction
   clears its review by being rescored (`direction score`, whose note may now cite a study id).
4. **The agenda is derived.** `workspace agenda` takes the lab direction's start order, leaves out
   studied candidates, and holds back blocked candidates, unscored candidates, and anything that
   waits on a held one. It prints how this differs from `lab.json`. A person applies it with
   `agenda --apply --by WHO --reason TEXT`. The previous change is kept in `agenda_history`.
5. **Directions are never paused by a score.** `direction rank` shows paused lines and reviews that
   are due. Pausing or closing a direction stays a person's call (`direction set`), made against the
   direction's own close criteria.
6. **Tested bets stop counting.** A closed candidate is no longer an open bet. Before this change,
   `direction rank` still counted the refuted c-20261105-026 (with its 2-day fatal test), and that
   count decided quantum-native's place in its tie.

## Worked example (qml_artifacts, 2026-11-26)
- Line `rydberg-coupling-learning` covers c-026, c-001, c-002, c-003, c-004, c-005, c-006, c-007
  and c-008.
- `learn` was run on s-001 (refuted), s-002 (supported) and s-003 (refuted). That makes 2 strikes,
  so the line paused. c-20261125-007 was named the last test, with the kill threshold from its bet
  sheet: shot ratio under 1.3x.
- The prerequisite was flipped: c-005 now requires c-007, instead of c-007 requiring c-005. With
  idealised rotations, c-007 is the upper bound on what global control can buy. If that bound is
  below 1.3x, realisable pulses (c-005) cannot matter. Cheapest fatal test first.
- The two reviews on c-003 came out as `none` for s-002 and `weakens` for s-003. Detuning is one of
  the global-control knobs that s-003 found worth at most 1.2x, so p was rescored from 0.25 to 0.1.
- The derived agenda puts c-20261125-007 first and c-20261111-008 second.
- The direction score is unchanged at 0.42. It was already rescored after s-003, and the
  top-direction order does not change either way.

## Not done (on purpose)
- No automatic p update for siblings or directions. The quantity that would justify one, how much a
  refutation of mechanism M should lower P(claim), is exactly the per-sibling judgment that the
  review records.
- No score threshold for pausing a direction.
- Lines are tagged by the portfolio step. They are not inferred from text similarity, because
  text overlap is not shared mechanism.
