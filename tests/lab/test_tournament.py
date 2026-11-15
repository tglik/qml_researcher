"""Pairwise tournament: Bradley-Terry fit, position-bias folding, Swiss pairing, replay metrics.

    python -m unittest tests.lab.test_tournament -v      (from the repo root)
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from lab.tools import tournament as t  # noqa: E402


def j(a, b, winner, order="ab"):
    return {"a": a, "b": b, "winner": winner, "judge": "test", "order": order, "reason": ""}


class TournamentTest(unittest.TestCase):
    IDS = ["c1", "c2", "c3", "c4"]

    def test_consistent_judge_recovers_the_true_order(self):
        # c1 > c2 > c3 > c4, every pair judged in both orders, judge always right
        js = []
        for x in range(4):
            for y in range(x + 1, 4):
                a, b = self.IDS[x], self.IDS[y]
                js += [j(a, b, "a", "ab"), j(b, a, "b", "ba")]
        order = [i for i, _ in t.ranking(self.IDS, js)]
        self.assertEqual(order, self.IDS)

    def test_position_biased_judge_counts_as_a_tie(self):
        # the judge always picks whoever is shown first: no information
        js = [j("c1", "c2", "a", "ab"), j("c2", "c1", "a", "ba")]
        st = t.fit(["c1", "c2"], js)
        self.assertEqual(st["c1"]["rating"], st["c2"]["rating"])
        self.assertEqual(st["c1"]["t"], 2)

    def test_prior_keeps_an_unbeaten_idea_finite(self):
        st = t.fit(["c1", "c2"], [j("c1", "c2", "a")])
        self.assertTrue(1500 < st["c1"]["rating"] < 1800, st)

    def test_swiss_pairs_are_deterministic_and_never_repeat(self):
        p1 = t.next_pairs(self.IDS, [], max_pairs=10)
        self.assertEqual(p1, t.next_pairs(self.IDS, [], max_pairs=10))
        self.assertEqual(len(p1), 4)                      # two pairs, both orders
        done = [j(p["a"], p["b"], "a", p["order"]) for p in p1]
        p2 = t.next_pairs(self.IDS, done, max_pairs=10)
        self.assertTrue(p2)
        self.assertFalse({(p["a"], p["b"]) for p in p2} & {(d["a"], d["b"]) for d in done})

    def test_replay_scores_agreement_with_known_outcomes(self):
        js = [j("c1", "c2", "a"), j("c2", "c3", "a"), j("c3", "c4", "a"), j("c1", "c4", "a")]
        r = t.replay(self.IDS, js, {"c1": 1, "c2": 1, "c3": 0, "c4": 0}, k=2)
        self.assertEqual(r["precision_at_k"], 1.0)
        self.assertGreater(r["kendall_tau_b"], 0.5)
        r = t.replay(self.IDS, js, {"c1": 0, "c2": 0, "c3": 1, "c4": 1}, k=2)
        self.assertEqual(r["precision_at_k"], 0.0)
        self.assertLess(r["kendall_tau_b"], -0.5)

    def test_cli_record_and_rank(self):
        with tempfile.TemporaryDirectory() as d:
            c, jp = Path(d) / "c.jsonl", Path(d) / "j.jsonl"
            c.write_text("\n".join(json.dumps({"id": i, "title": i}) for i in self.IDS) + "\n", encoding="utf-8")
            t.main(["record", str(jp), "--a", "c3", "--b", "c1", "--winner", "a", "--judge", "x", "--order", "ab"])
            ids, js = t.load(c, jp)
            self.assertEqual(t.ranking(ids, js)[0][0], "c3")
            with self.assertRaises(t.LabError):
                jp.write_text(json.dumps(j("c1", "zz", "a")) + "\n", encoding="utf-8")
                t.load(c, jp)

    def test_cli_ingest_appends_rows_from_a_file(self):
        with tempfile.TemporaryDirectory() as d:
            c, jp, rows = Path(d) / "c.jsonl", Path(d) / "j.jsonl", Path(d) / "r.json"
            c.write_text("\n".join(json.dumps({"id": i}) for i in self.IDS) + "\n", encoding="utf-8")
            rows.write_text(json.dumps([{"a": "c4", "b": "c2", "winner": "a", "order": "ab", "reason": "x `$(rm -rf /)`"}]),
                            encoding="utf-8")
            t.main(["ingest", str(jp), str(rows), "--judge", "wf"])
            ids, js = t.load(c, jp)
            self.assertEqual(js[0]["judge"], "wf")
            self.assertEqual(t.ranking(ids, js)[0][0], "c4")


if __name__ == "__main__":
    unittest.main()
