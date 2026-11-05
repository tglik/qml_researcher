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

    def test_close_direction_records_history(self):
        self.direction()
        out = self.bl("direction", "set", "rydberg-graph-kernels", "--status", "closed",
                      "--reason", "close criteria fired")
        self.assertIn("exclusion-ledger", out)
        ds = json.loads((self.vault / "indexes/backlog/directions.json").read_text())
        self.assertEqual(ds[0]["history"][-1]["status"], "closed")


if __name__ == "__main__":
    unittest.main()
