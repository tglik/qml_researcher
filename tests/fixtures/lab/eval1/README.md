# Eval 1 — screen replay fixtures

Each fixture is the **pre-experiment framing** of a closed experiment: what the team believed
and proposed *before* running it — no results, no verdict language. The screen is run with the
exclusion ledger **time-sliced** to entries created before that experiment
(`python -m lab.tools.ledger slice --before <date> --out <tmp>`), so it cannot see its own answer.

**Written so far** (known-answer cases — the ones the design names explicitly):

| Fixture | Replays | Ledger slice before | Known answer |
|---|---|---|---|
| `fraud_authorization.md` | fraud/AML screen | 2026-09-15 | Empty *with the anti-correlation reason*: capped layers are per-event (G1), infrequent layers are uncapped (G2) |
| `exp07_spectral_gap.md` | exp 07 | 2026-07-29 | Rule 1 flags the wrong comparison object: the restricted Pauli family has a near-free exact classical spectrum |
| `exp09_retrieval_readout.md` | exp 09 | 2026-07-29 | Readout routes die at G1 on paper (~√(candidates) vs ~log(catalog)) |
| `exp04_twin.md` | exp 04 | 2026-07-29 | G3 red on paper: small classical description + diffusion, no sign cancellation ⇒ twin |

**Still to write (needs Adi or Tsahi — hindsight-free framing is a human job):** exps 01, 02,
03, 05, 06, 08, 10, 11, 12, 13, and the materials program (Q-FEAT-screen must die at G2 —
blocked until `materials_configuration_space` is located). Source for each: the experiment
README's question + the git history before its first results commit.

Target (docs/lab C10): ≥ 60% of the NO-GOs killed at G0–G3, and all four known answers above.
