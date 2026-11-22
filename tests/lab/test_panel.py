"""Multi-model panel: blind prompts, answer validation, resume, aggregation, n_eff, champion cap,
minority picks, export format.

    python -m unittest tests.lab.test_panel -v      (from the repo root)
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from lab.tools import panel as P  # noqa: E402

RUBRIC = P.load_rubric("backlog_lanes")
CRIT = [k["id"] for k in RUBRIC["criteria"]]


def cand(i, **kw):
    c = {"id": f"c-{i:03d}", "title": f"Idea {i}", "claim": f"Claim {i} holds", "direction": "d1",
         "gate": {"value": {"rung": 1 + i % 6, "p": round(0.1 + 0.03 * i, 2), "note": "SECRET-GATE-NOTE"},
                  "novelty": {"score": 0.5}}}
    c.update(kw)
    return c


def scores(x, **kw):
    s = {"no_go": 0.1, "on_path": 0.8, "rung": 1 + x % 6, "plausibility": min(1, 0.05 * x), "upside": 1 + x % 5,
         "insight": 1, "fatal_test_days": 2, "champion": 0}
    s.update(kw)
    return s


def answer(s):
    return {"completed": True, "answer_text": json.dumps({"scores": s, "strongest_case": "c", "strongest_objection": "o"})}


class PromptTest(unittest.TestCase):
    def test_prompt_is_blind_to_gate_and_author(self):
        c = cand(3, by="claude", gate={"value": {"rung": 2, "p": 0.77, "note": "SECRET-GATE-NOTE"}})
        text = P.prompt_for(c, {"id": "d1", "title": "Dir", "thesis": "T"}, RUBRIC, "judge")
        self.assertNotIn("SECRET-GATE-NOTE", text)
        self.assertNotIn("0.77", text)
        self.assertNotIn("claude", text.lower().replace("claim", ""))
        for k in CRIT:
            self.assertIn(f"- {k} (", text)

    def test_roles_change_the_prompt_and_hash(self):
        c = cand(1)
        hs = {P.prompt_hash(P.prompt_for(c, None, RUBRIC, r)) for r in P.ROLES}
        self.assertEqual(len(hs), 3)


class ParseTest(unittest.TestCase):
    def test_rejects_out_of_range_and_missing(self):
        ok, err = P.parse_answer(answer(scores(3))["answer_text"], RUBRIC)
        self.assertIsNone(err)
        _, err = P.parse_answer(answer(scores(3, plausibility=1.4))["answer_text"], RUBRIC)
        self.assertIn("outside", err)
        s = scores(3); del s["upside"]
        _, err = P.parse_answer(answer(s)["answer_text"], RUBRIC)
        self.assertIn("upside", err)
        _, err = P.parse_answer(answer(scores(3, champion=0.5))["answer_text"], RUBRIC)
        self.assertIn("whole number", err)


class RunAndReportTest(unittest.TestCase):
    PANEL = {"name": "t", "seats": [
        {"id": "j1", "harness": "codex", "model": "m1", "family": "openai", "role": "judge"},
        {"id": "j2", "harness": "claude-code", "model": "m2", "family": "anthropic", "role": "judge"},
        {"id": "j3", "harness": "openai-compat", "model": "m3", "family": "google", "role": "judge"},
        {"id": "adv", "harness": "codex", "model": "m1", "family": "openai", "role": "advocate"}]}

    def setUp(self):
        self.cands = [cand(i) for i in range(1, 13)]

    def fake(self, agree=True):
        def caller(seat, prompt, schema):
            i = int(prompt.split("Candidate: Idea ")[1].split("\n")[0])
            x = i if agree or seat["id"] != "j3" else 13 - i        # j3 reverses the order
            champ = 1 if seat["id"] == "j1" and i >= 7 else 0     # j1 champions 6: over the cap
            return answer(scores(x, champion=champ))
        return caller

    def test_run_resumes_and_report_aggregates(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d)
            r = P.run(self.PANEL, RUBRIC, self.cands, {}, out, workers=2, caller=self.fake(), log=lambda *_: None)
            self.assertEqual(r["ok"], 12 * 4)
            r = P.run(self.PANEL, RUBRIC, self.cands, {}, out, workers=2, caller=self.fake(), log=lambda *_: None)
            self.assertEqual(r["ok"], 0)                                  # everything already done
            rep = P.report(RUBRIC, P.read_jsonl(out / "judgments.jsonl"), self.cands, {"c-012": "advantage-bet"})
            self.assertEqual(rep["judge_seats"], ["j1", "j2", "j3"])
            self.assertEqual(rep["agreement"]["plausibility"]["n_eff"], 1.0)   # identical judges = one vote
            e = rep["candidates"]["c-005"]
            self.assertEqual(e["n_judges"], 3)
            self.assertIn("advocate", e)                                       # bound, not in the median
            first = json.loads(P.export(rep, out, "r1").read_text().splitlines()[0])
            self.assertEqual(set(first["scores"]), {"j1", "j2", "j3"})            # advocate is a bound
            self.assertIn("adv", first["bounds"])
            self.assertEqual(json.loads((out / "run.json").read_text())["run"], "r1")
            # champion cap: j1 championed 6, at most 3 survive
            kept = [c for c, v in rep["candidates"].items() if v["by_seat"]["j1"]["champion"] == 1]
            self.assertEqual(len(kept), 3)
            self.assertEqual(len(rep["champions_capped"]), 3)
            self.assertIsNotNone(rep["vs_gate"])
            self.assertIn("advantage-bet", rep["bets"])

    def test_disagreement_lowers_n_eff_and_flags_contested_and_minority(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d)
            P.run(self.PANEL, RUBRIC, self.cands, {}, out, workers=2, caller=self.fake(agree=False), log=lambda *_: None)
            rep = P.report(RUBRIC, P.read_jsonl(out / "judgments.jsonl"), self.cands, {})
            self.assertGreater(rep["agreement"]["plausibility"]["n_eff"], 1.5)
            self.assertTrue(rep["contested"])
            self.assertTrue(any(m["seat"] == "j3" for m in rep["minority_picks"]))

    def test_failed_answers_are_recorded_and_retried(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d)
            bad = lambda s, p, sc: {"completed": False, "answer_text": None, "error": "boom"}
            r = P.run(self.PANEL, RUBRIC, self.cands[:2], {}, out, caller=bad, log=lambda *_: None)
            self.assertEqual(r["failed"], 8)
            r = P.run(self.PANEL, RUBRIC, self.cands[:2], {}, out, caller=self.fake(), log=lambda *_: None)
            self.assertEqual(r["ok"], 8)


class StatsTest(unittest.TestCase):
    def test_n_eff(self):
        self.assertEqual(P.n_eff(9, 0.0), 9.0)
        self.assertEqual(P.n_eff(9, 1.0), 1.0)
        self.assertAlmostEqual(P.n_eff(3, 0.56), 1.41, places=1)   # arXiv:2609.22512's frontier trio

    def test_log_spread(self):
        k = next(k for k in RUBRIC["criteria"] if k["id"] == "fatal_test_days")
        self.assertEqual(P.spread_of(k, [0.5, 60]), 1.0)

    def test_shipped_panels_load(self):
        for p in sorted(P.PANELS.glob("*.json")):
            P.load_panel(str(p))


if __name__ == "__main__":
    unittest.main()
