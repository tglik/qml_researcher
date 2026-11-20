"""Tests for lab.tools.backlog through its CLI, against a throwaway vault."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CLAIM = "Rydberg graph kernels beat Weisfeiler-Lehman and GIN on attributed TU graphs at matched budget"


class BacklogTest(unittest.TestCase):
    def setUp(self):
        self.vault = Path(tempfile.mkdtemp())
        self.env = {**os.environ, "LAB_OUTPUT_ROOT": str(self.vault), "PYTHONPATH": str(REPO)}

    def tearDown(self):
        shutil.rmtree(self.vault)

    def bl(self, *args, ok=True):
        r = subprocess.run([sys.executable, "-m", "lab.tools.backlog", *args], cwd=REPO, env=self.env,
                           capture_output=True, text=True)
        if ok and r.returncode != 0:
            self.fail(f"{args} failed:\n{r.stdout}\n{r.stderr}")
        if not ok and r.returncode == 0:
            self.fail(f"{args} should have failed:\n{r.stdout}")
        return (r.stdout + r.stderr).strip()

    def direction(self):
        self.bl("direction", "add", "--id", "rydberg-graph-kernels", "--title", "Rydberg graph kernels",
                "--thesis", "Blockade kernels separate graph-native data from classical kernels",
                "--target-rung", "3", "--close-criteria",
                "Close if three candidates show geometric difference below 1.2 against WL at 16 nodes")

    def add(self, title="Detuning kernel vs WL", claim=CLAIM, *extra, ok=True):
        return self.bl("add", "--title", title, "--claim", claim, "--source", "A", "--base", "arXiv:2509.09421",
                       "--direction", "rydberg-graph-kernels", "--region", "quantum-native", *extra, ok=ok)

    def test_direction_needs_close_criteria_and_valid_rung(self):
        out = self.bl("direction", "add", "--id", "x", "--title", "x", "--thesis", "x", "--target-rung", "3",
                      "--close-criteria", "when bored", ok=False)
        self.assertIn("close criteria", out)
        out = self.bl("direction", "add", "--id", "x", "--title", "x", "--thesis", "x", "--target-rung", "9",
                      "--close-criteria", "close after three failed candidates at sixteen nodes", ok=False)
        self.assertIn("rung", out)

    def test_add_rejects_vague_claims_unknown_directions_and_duplicates(self):
        self.direction()
        self.assertIn("testable sentence", self.add("t", "quantum is better", ok=False))
        out = self.bl("add", "--title", "t", "--claim", CLAIM, "--source", "A", "--base", "b",
                      "--direction", "nope", ok=False)
        self.assertIn("no direction nope", out)
        cid = self.add()
        self.assertTrue(cid.startswith("c-"))
        out = self.add("Detuning kernel versus WL", CLAIM + " again", ok=False)
        self.assertIn(f"duplicate of {cid}", out)
        self.add("Detuning kernel versus WL", CLAIM + " again", "--force")

    def test_dedupe_against_past_programs(self):
        d = self.vault / "experiments" / "spectral_graph" / "09_candidate_retrieval_pauli"
        d.mkdir(parents=True)
        (d / "HYPOTHESIS.md").write_text(
            "# H\n\n**Claim, in one sentence:** polylog Pauli operator serves online candidate retrieval "
            "at matched byte budget against k-means\n", encoding="utf-8")
        out = self.bl("add", "--title", "Pauli retrieval", "--claim",
                      "polylog Pauli operator serves online candidate retrieval at matched byte budget against k-means",
                      "--source", "E", "--base", "exp 09", ok=False)
        self.assertIn("duplicate of spectral_graph/09_candidate_retrieval_pauli", out)

    def test_gate_queue_pick_link_outcome_report(self):
        self.direction()
        good = self.add()
        bad = self.add("Kernel for tabular fraud", "Rydberg kernel features improve tabular fraud AUC "
                       "over tuned LightGBM at one million rows")
        self.assertIn(good, self.bl("pending"))
        # a kill needs a reason; prior work needs evidence
        self.assertIn("needs --note", self.bl("score", bad, "--gate", "screen", "--verdict", "killed", ok=False))
        self.assertIn("needs --evidence", self.bl("score", good, "--gate", "novelty", "--score", "0.1",
                                                  "--prior-exists", ok=False))
        self.bl("score", bad, "--gate", "screen", "--verdict", "killed", "--gates", "G1",
                "--note", "per-row loading cost dominates")
        self.bl("score", bad, "--gate", "novelty", "--score", "0.6")
        self.bl("score", good, "--gate", "novelty", "--score", "0.8")
        out = self.bl("score", good, "--gate", "screen", "--verdict", "pass")
        self.assertIn("gate passed", out)
        self.bl("score", good, "--gate", "value", "--rung", "3", "--p", "0.3")
        q = self.bl("queue")
        self.assertIn(good, q.split("Explore sample")[0])
        self.assertNotIn(bad, q.split("Explore sample")[0])
        # a gate kill can be picked only if it is in the explore sample
        cs = [json.loads(l) for l in (self.vault / "indexes/backlog/candidates.jsonl").read_text().splitlines()]
        bad_row = next(c for c in cs if c["id"] == bad)
        out = self.bl("pick", bad, "--by", "adi", ok=bad_row["explore"])
        self.bl("pick", good, "--by", "adi")
        self.assertIn("--furthest must be", self.bl("outcome", good, "--furthest", "zzz", ok=False))
        self.assertIn("only gated", self.bl("pick", good, "--by", "meir", ok=False))
        self.bl("link", good, "--thread", "rydberg_graph/19_detuning_kernel")
        self.bl("outcome", good, "--furthest", "verdict", "--rung", "3")
        rep = self.bl("report")
        self.assertIn("A build-on-base", rep)
        self.assertIn("quantum-native", rep)
        self.assertIn("backlog OK", self.bl("validate"))

    def test_potential_profile_is_recorded_and_reported_but_never_gates(self):
        self.direction()
        cid = self.add()
        self.assertIn("potential", self.bl("pending"))
        self.assertIn("7 values", self.bl("score", cid, "--gate", "potential", "--answers", "2,1",
                                          "--evidence-class", "none", "--note", "x", ok=False))
        self.assertIn("evidence-class", self.bl("score", cid, "--gate", "potential", "--answers",
                                                "2,1,0,2,1,1,0", "--evidence-class", "proven", "--note", "x", ok=False))
        self.assertIn("needs --note", self.bl("score", cid, "--gate", "potential", "--answers",
                                              "2,1,0,2,1,1,0", "--evidence-class", "none", ok=False))
        # the profile alone does not finish the gate, and a low profile does not kill
        out = self.bl("score", cid, "--gate", "potential", "--answers", "0,0,0,1,0,1,0",
                      "--evidence-class", "none", "--note", "no named mechanism; weakest: work over input")
        self.assertIn("gate pending", out)
        self.bl("score", cid, "--gate", "novelty", "--score", "0.8")
        self.assertIn("gate passed", self.bl("score", cid, "--gate", "screen", "--verdict", "pass"))
        self.bl("score", cid, "--gate", "value", "--rung", "3", "--p", "0.3")
        q = self.bl("queue")
        self.assertIn("pot  2/14 none", q)
        rep = self.bl("report")
        self.assertIn("low 0-4 · rung 3-6", rep)
        self.assertIn("By evidence class", rep)
        self.assertIn("backlog OK", self.bl("validate"))
        rows = (self.vault / "indexes/backlog/candidates.jsonl").read_text().replace('"work": 0', '"work": 5')
        (self.vault / "indexes/backlog/candidates.jsonl").write_text(rows)
        self.assertIn("bad potential profile", self.bl("validate", ok=False))

    def explainer(self, cid, bet="mechanism-probe", qc="weak", status="draft", extra="", body_extra=""):
        h = self.bl("explain-hash", cid)
        heads = ["In plain words", "Background", "The real motivation", "Why quantum, honestly",
                 "Why it might fail", "What we learn either way", "Cost and feasibility", "Sources"]
        filler = " ".join(["plain words explain the idea for a reader outside the field"] * 8)
        body = "".join(f"## {h_}\n\n{filler}\n\n" for h_ in heads) + body_extra
        meta = (f"---\nid: {cid}\nkind: candidate\nbet: {bet}\nquantum_case: {qc}\n"
                f"tagline: Does the detuning kernel see graphs differently from WL?\nconfidence: speculative\n"
                f"claim_hash: {h}\nsources: [arXiv:2509.09421]\nwritten_by: explainer\nwritten_at: 2026-11-18\n"
                f"check_status: {status}\n{extra}---\n")
        d = self.vault / "indexes/backlog/explainers/candidates"
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{cid}.md").write_text(meta + body, encoding="utf-8")

    def test_explainer_lint_status_and_candor_caps(self):
        self.direction()
        cid = self.add()
        self.bl("score", cid, "--gate", "novelty", "--score", "0.8")
        self.bl("score", cid, "--gate", "screen", "--verdict", "pass")
        self.bl("score", cid, "--gate", "value", "--rung", "1", "--p", "0.3")
        self.assertIn(f"missing  candidate {cid}", self.bl("explain-status"))
        self.explainer(cid, bet="kill-test", qc="weak")
        self.assertIn("backlog OK", self.bl("validate", "--explainers"))
        self.assertIn(f"draft    candidate {cid}", self.bl("explain-status"))
        # a kill test may not claim a plausible quantum case, nor use advantage words
        self.explainer(cid, bet="kill-test", qc="plausible")
        self.assertIn("quantum_case plausible on a kill-test", self.bl("validate", "--explainers", ok=False))
        self.explainer(cid, bet="kill-test", qc="none", body_extra="It outperforms every kernel.\n")
        self.assertIn("advantage wording", self.bl("validate", "--explainers", ok=False))
        # the bet must follow the rung; strong needs mechanism=2 and window=2
        self.explainer(cid, bet="advantage-bet", qc="strong")
        out = self.bl("validate", "--explainers", ok=False)
        self.assertIn("value rung says kill-test", out)
        self.assertIn("quantum_case strong needs", out)
        # signing needs a separate checker; cited ids must be listed
        self.explainer(cid, bet="kill-test", qc="none", status="signed",
                       body_extra="See arXiv:2011.01938 for the measure.\n")
        out = self.bl("validate", "--explainers", ok=False)
        self.assertIn("signed without a separate checker", out)
        self.assertIn("2011.01938", out)
        self.explainer(cid, bet="kill-test", qc="none", status="signed",
                       extra="checked_by: explanation-checker\nchecked_at: 2026-11-18\n")
        self.assertIn("backlog OK", self.bl("validate", "--explainers"))
        self.assertNotIn(cid, self.bl("explain-status"))
        # changing the gate record makes the page stale
        self.bl("score", cid, "--gate", "value", "--rung", "1", "--p", "0.2", "--note", "re-scored")
        self.assertIn(f"stale    candidate {cid}", self.bl("explain-status"))

    def gated(self, title, claim, rung, p, direction="rydberg-graph-kernels"):
        cid = self.bl("add", "--title", title, "--claim", claim, "--source", "A", "--base", "arXiv:2509.09421",
                      "--direction", direction, "--force")
        self.bl("score", cid, "--gate", "novelty", "--score", "0.5")
        self.bl("score", cid, "--gate", "screen", "--verdict", "pass")
        self.bl("score", cid, "--gate", "value", "--rung", str(rung), "--p", str(p))
        return cid

    def test_direction_score_needs_reasons_and_ranks_by_expected_impact(self):
        self.direction()
        self.bl("direction", "add", "--id", "kikuchi", "--title", "Planted inference", "--thesis", "x",
                "--target-rung", "3", "--close-criteria", "Close if guiding-state enhancement vanishes on every non-Gaussian model")
        note = "the core candidate is a coin flip against a tuned classical twin"
        out = self.bl("direction", "score", "kikuchi", "--plausibility", "1.4", "--impact", "3", "--confidence", "low",
                      "--plausibility-note", note + " c-20261105-001", "--impact-note", note, ok=False)
        self.assertIn("plausibility must be in [0, 1]", out)
        out = self.bl("direction", "score", "kikuchi", "--plausibility", "0.3", "--impact", "4", "--confidence", "low",
                      "--plausibility-note", note, "--impact-note", note, ok=False)
        self.assertIn("must cite its evidence", out)
        self.bl("direction", "score", "kikuchi", "--plausibility", "0.3", "--impact", "4", "--confidence", "medium",
                "--plausibility-note", note + " (arXiv:2610.32595)", "--impact-note", note)
        self.bl("direction", "score", "rydberg-graph-kernels", "--plausibility", "0.7", "--impact", "1",
                "--confidence", "high", "--plausibility-note", note + " experiments/search/rydberg", "--impact-note", note)
        rank = self.bl("direction", "rank").splitlines()
        self.assertIn("kikuchi", rank[0])           # 1.2 beats 0.7: likely-but-minor ranks below
        self.assertIn("1.2", rank[0])
        self.assertIn("backlog OK", self.bl("validate"))

    def test_requires_sets_start_order_and_rejects_cycles(self):
        self.direction()
        twin = self.gated("Monte Carlo twin", "Glauber Monte Carlo matches blockade features within two points at sixteen nodes", 1, 0.3)
        app = self.gated("Protein variant", "Blockade features beat WL subtree features on PROTEINS residue contact graphs", 3, 0.6)
        other = self.gated("Shot cost", "One thousand shots keep blockade feature accuracy within three points at ten nodes", 3, 0.4)
        self.assertIn("--why", self.bl("require", app, "--on", twin, ok=False))
        self.bl("require", app, "--on", twin, "--why", "an applied variant is moot if the twin matches")
        order = self.bl("order", "--direction", "rydberg-graph-kernels").splitlines()[1:]
        ids = [next(w for w in line.split() if w.startswith("c-")) for line in order]
        # the twin has a dependent, so it goes first despite the lowest rank; the variant waits for it
        self.assertEqual(ids[0], twin)
        self.assertLess(ids.index(twin), ids.index(app))
        self.assertIn(other, ids)
        out = self.bl("require", twin, "--on", app, "--why", "a deliberately circular requirement for this test", ok=False)
        self.assertIn("cycle", out)
        self.bl("require", app, "--on", twin, "--drop")
        self.assertIn("backlog OK", self.bl("validate"))

    def test_cross_direction_requires_need_a_recorded_relation(self):
        self.direction()
        self.bl("direction", "add", "--id", "dequant", "--title", "Kills", "--thesis", "x", "--target-rung", "1",
                "--close-criteria", "Close after four kills in a row already refuted before we finished")
        rff = self.gated("RFF twin", "Random Fourier features match the detuning kernel within two points on MUTAG", 1, 0.5,
                         direction="dequant")
        noise = self.gated("Noise", "Detuning kernel accuracy drops under three points at one percent SPAM noise", 3, 0.4)
        self.bl("require", noise, "--on", rff, "--why", "if RFF matches the kernel the noisy version is moot")
        self.assertIn("cross_requires", self.bl("independence"))
        self.assertIn("no recorded relation", self.bl("validate", ok=False))
        out = self.bl("relate", "dequant", "rydberg-graph-kernels", "--kind", "dependent", "--proposal", "keep",
                      "--note", "the kill tests test the kernel this direction studies", ok=False)
        self.assertIn("not separate directions", out)
        self.bl("relate", "dequant", "rydberg-graph-kernels", "--kind", "dependent", "--proposal", "move",
                "--move", f"{rff}:rydberg-graph-kernels", "--evidence", rff,
                "--note", "the kill tests test the kernel this direction studies")
        self.assertIn("dependent, move (proposed)", self.bl("independence"))
        self.assertIn("backlog OK", self.bl("validate"))
        rs = json.loads((self.vault / "indexes/backlog/relations.json").read_text())
        self.assertEqual(rs[0]["moves"], [{"id": rff, "to": "rydberg-graph-kernels"}])

    def test_accepted_relation_is_applied_with_move_and_recorded(self):
        self.direction()
        self.bl("direction", "add", "--id", "dequant", "--title", "Kills", "--thesis", "x", "--target-rung", "1",
                "--close-criteria", "Close after four kills in a row already refuted before we finished")
        rff = self.gated("RFF twin", "Random Fourier features match the detuning kernel within two points on MUTAG", 1, 0.5,
                         direction="dequant")
        self.bl("relate", "dequant", "rydberg-graph-kernels", "--kind", "dependent", "--proposal", "merge",
                "--into", "rydberg-graph-kernels", "--note", "the kill tests test the kernel this direction studies")
        self.assertIn("accepted or rejected", self.bl("decide", "dequant", "rydberg-graph-kernels",
                                                      "--status", "maybe", "--by", "tsahi", ok=False))
        self.bl("decide", "dequant", "rydberg-graph-kernels", "--status", "accepted", "--by", "tsahi")
        self.bl("move", rff, "--to", "rydberg-graph-kernels", "--reason", "merge accepted by tsahi")
        self.bl("direction", "set", "dequant", "--status", "closed", "--reason", "merged into rydberg-graph-kernels")
        self.bl("direction", "edit", "rydberg-graph-kernels", "--title", "Rydberg kernels, kill first",
                "--reason", "merged with dequant")
        cs = [json.loads(l) for l in (self.vault / "indexes/backlog/candidates.jsonl").read_text().splitlines()]
        row = next(c for c in cs if c["id"] == rff)
        self.assertEqual(row["direction"], "rydberg-graph-kernels")
        self.assertEqual(row["history"][-1]["moved"], {"from": "dequant", "to": "rydberg-graph-kernels"})
        rs = json.loads((self.vault / "indexes/backlog/relations.json").read_text())
        self.assertEqual(rs[0]["status"], "accepted")
        self.assertIn("backlog OK", self.bl("validate"))

    def test_close_direction_records_history(self):
        self.direction()
        out = self.bl("direction", "set", "rydberg-graph-kernels", "--status", "closed",
                      "--reason", "close criteria fired")
        self.assertIn("exclusion-ledger", out)
        ds = json.loads((self.vault / "indexes/backlog/directions.json").read_text())
        self.assertEqual(ds[0]["history"][-1]["status"], "closed")


if __name__ == "__main__":
    unittest.main()
