"""Frozen scorer (lab.tools.scorer + lock + gates), the CP3 verifier lane, and the PreToolUse guard hook.

    python -m unittest tests.lab.test_scorer_and_hook -v      (from the repo root)
"""
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from test_tools import PROPOSAL, REPO, LabFixture

SCORE_PY = '''import argparse, csv, json
from pathlib import Path
ap = argparse.ArgumentParser(); ap.add_argument("--phase"); ap.add_argument("--thread"); ap.add_argument("--out")
a = ap.parse_args()
t = Path(a.thread)
labels = [float(r["y"]) for r in csv.DictReader(open(t / "scorer/heldout/labels.csv"))]
preds = [float(r["y"]) for r in csv.DictReader(open(t / "P1_toy/raw/preds.csv"))]
mae = sum(abs(p - y) for p, y in zip(preds, labels)) / len(labels)
json.dump({"P1.G4.threshold": {"value": round(0.1 - mae, 6)}}, open(a.out, "w"))
'''


class ScorerTest(LabFixture):
    def frozen_with_scorer(self):
        self.new_program()
        (self.thread / "PROPOSAL.md").write_text(PROPOSAL, encoding="utf-8")
        sc = self.thread / "scorer"
        (sc / "heldout").mkdir(parents=True)
        (sc / "score.py").write_text(SCORE_PY, encoding="utf-8")
        (sc / "heldout" / "labels.csv").write_text("y\n1.0\n2.0\n", encoding="utf-8")
        out = self.run_tool("lab.tools.lock", "freeze", str(self.thread), "--by", "adi")
        self.assertIn("scorer frozen: 2 files", out)
        self.run_tool("lab.tools.state", "set", str(self.thread), "--by", "/qml-lab", "--stage", "run", "--phase", "P1")
        raw = self.thread / "P1_toy" / "raw"
        raw.mkdir(parents=True)
        (raw / "preds.csv").write_text("y\n1.0\n2.05\n", encoding="utf-8")

    def test_gates_run_the_frozen_scorer_and_ignore_hand_written_numbers(self):
        self.frozen_with_scorer()
        res = self.thread / "P1_toy" / "results"
        res.mkdir(parents=True)
        # a hand-written measured.json is overwritten by the scorer's numbers
        (res / "measured.json").write_text(json.dumps({"P1.G4.threshold": {"value": 9.9}}), encoding="utf-8")
        out = self.run_tool("lab.tools.gates", str(self.thread), "P1")
        self.assertIn("| P1.G4.threshold | 0.075 | >= 0.02 | PASS | scorer:P1.G4.threshold |", out)
        measured = json.loads((res / "measured.json").read_text(encoding="utf-8"))
        self.assertEqual(measured["_scorer"]["by"], "lab.tools.scorer")
        self.run_tool("lab.tools.provenance", "check", str(self.thread))
        # a rerun with the same raw outputs reuses the same provenance id and stays consistent
        self.run_tool("lab.tools.gates", str(self.thread), "P1")
        self.run_tool("lab.tools.provenance", "check", str(self.thread))

    def test_scorer_change_after_freeze_is_a_lock_mismatch(self):
        self.frozen_with_scorer()
        score = self.thread / "scorer" / "score.py"
        score.write_text(SCORE_PY.replace("0.1 - mae", "0.1"), encoding="utf-8")
        out = self.run_tool("lab.tools.lock", "verify", str(self.thread), ok=False)
        self.assertIn("SCORER  changed scorer/score.py", out)
        out = self.run_tool("lab.tools.gates", str(self.thread), "P1", ok=False)
        self.assertIn("lock mismatch", out)
        # an approved amendment before data access re-freezes it
        self.run_tool("lab.tools.lock", "amend", str(self.thread), "--touches", "scorer",
                      "--reason", "metric bug", "--phase", "P1", "--by", "tsahi")
        self.run_tool("lab.tools.lock", "verify", str(self.thread))
        # swapping held-out labels is caught too
        (self.thread / "scorer" / "heldout" / "labels.csv").write_text("y\n1.0\n2.05\n", encoding="utf-8")
        out = self.run_tool("lab.tools.lock", "verify", str(self.thread), ok=False)
        self.assertIn("SCORER  changed scorer/heldout/labels.csv", out)

    def test_scorer_cannot_report_gates_outside_the_lock(self):
        self.frozen_with_scorer()
        bad = SCORE_PY.replace('{"P1.G4.threshold"', '{"P1.G9.invented": {"value": 1}, "P1.G4.threshold"')
        (self.thread / "scorer" / "score.py").write_text(bad, encoding="utf-8")
        self.run_tool("lab.tools.lock", "amend", str(self.thread), "--touches", "scorer",
                      "--reason", "test", "--phase", "P1", "--by", "tsahi")
        out = self.run_tool("lab.tools.gates", str(self.thread), "P1", ok=False)
        self.assertIn("not in the lock", out)

    def test_cp3_passes_on_the_verifier_only_with_a_scorer(self):
        self.frozen_with_scorer()
        self.run_tool("lab.tools.gates", str(self.thread), "P1")
        out = self.run_tool("lab.tools.autonomy", "cp3-check", str(self.thread))
        self.assertIn("CP3 can pass on the verifier", out)
        (self.thread / "briefs").mkdir(exist_ok=True)
        (self.thread / "briefs" / "DECISION_BRIEF_CP3_1.md").write_text("brief", encoding="utf-8")
        self.run_tool("lab.tools.state", "open-cp", str(self.thread), "CP3", "--author", "agent:implementer",
                      "--brief", "briefs/DECISION_BRIEF_CP3_1.md")
        out = self.run_tool("lab.tools.autonomy", "auto", str(self.thread), "CP3", "--decision", "approve")
        self.assertIn("CP3 auto-approve (AGENT)", out)

    def test_cp3_needs_a_person_without_a_scorer(self):
        self.new_program()
        (self.thread / "PROPOSAL.md").write_text(PROPOSAL, encoding="utf-8")
        out = self.run_tool("lab.tools.lock", "freeze", str(self.thread), "--by", "adi")
        self.assertIn("WARNING: no scorer/", out)
        self.run_tool("lab.tools.state", "set", str(self.thread), "--by", "/qml-lab", "--stage", "run", "--phase", "P1")
        res = self.thread / "P1_toy" / "results"
        res.mkdir(parents=True)
        (res / "measured.json").write_text(json.dumps({"P1.G4.threshold": {"value": 0.03}}), encoding="utf-8")
        self.run_tool("lab.tools.gates", str(self.thread), "P1")
        out = self.run_tool("lab.tools.autonomy", "cp3-check", str(self.thread))
        self.assertIn("no frozen scorer", out)
        # CP3 is AGENT in config, but this instance falls back to a person
        (self.thread / "briefs").mkdir(exist_ok=True)
        (self.thread / "briefs" / "DECISION_BRIEF_CP3_1.md").write_text("brief", encoding="utf-8")
        self.run_tool("lab.tools.state", "open-cp", str(self.thread), "CP3", "--author", "agent:implementer",
                      "--brief", "briefs/DECISION_BRIEF_CP3_1.md")
        out = self.run_tool("lab.tools.autonomy", "auto", str(self.thread), "CP3", "--decision", "approve", ok=False)
        self.assertIn("now waits for a person", out)
        st = json.loads((self.thread / "STATE.json").read_text(encoding="utf-8"))
        self.assertEqual(st["checkpoints"]["CP3:P1"]["mode"], "HUMAN_APPROVE")


class GuardHookTest(LabFixture):
    def hook(self, tool, **tool_input):
        event = {"tool_name": tool, "tool_input": tool_input, "cwd": str(self.thread)}
        r = subprocess.run([sys.executable, str(REPO / "hooks" / "lab_guard.py")], input=json.dumps(event),
                           capture_output=True, text=True, env={k: v for k, v in self.env.items() if k != "LAB_GUARD_OFF"})
        self.assertEqual(r.returncode, 0, r.stderr)
        if not r.stdout.strip():
            return None
        return json.loads(r.stdout)["hookSpecificOutput"]["permissionDecision"]

    def setUp(self):
        super().setUp()
        self.new_program()
        (self.thread / "PROPOSAL.md").write_text(PROPOSAL, encoding="utf-8")
        (self.thread / "scorer" / "heldout").mkdir(parents=True)
        (self.thread / "scorer" / "score.py").write_text(SCORE_PY, encoding="utf-8")
        (self.thread / "scorer" / "heldout" / "labels.csv").write_text("y\n1\n", encoding="utf-8")

    def set_stage(self, stage):
        st = json.loads((self.thread / "STATE.json").read_text(encoding="utf-8"))
        st["stage"] = stage
        (self.thread / "STATE.json").write_text(json.dumps(st), encoding="utf-8")

    def test_before_freeze_the_designer_may_write_the_scorer_and_proposal(self):
        self.assertIsNone(self.hook("Write", file_path=str(self.thread / "scorer" / "score.py"), content="x"))
        self.assertIsNone(self.hook("Edit", file_path=str(self.thread / "PROPOSAL.md")))
        self.assertEqual(self.hook("Write", file_path=str(self.thread / "STATE.json")), "deny")

    def test_after_freeze_scorer_is_denied_and_proposal_asks(self):
        self.run_tool("lab.tools.lock", "freeze", str(self.thread), "--by", "adi")
        self.set_stage("run")
        self.assertEqual(self.hook("Edit", file_path=str(self.thread / "scorer" / "score.py")), "deny")
        self.assertEqual(self.hook("Edit", file_path=str(self.thread / "PROPOSAL.md")), "ask")
        self.assertEqual(self.hook("Write", file_path=str(self.thread / "PREREG.lock.json")), "deny")
        self.assertEqual(self.hook("Write", file_path=str(self.thread / "P1_toy/results/measured.json")), "deny")
        self.assertEqual(self.hook("Write", file_path=str(self.thread / "VERDICT.md")), "deny")
        self.assertIsNone(self.hook("Write", file_path=str(self.thread / "P1_toy/raw/preds.csv")))

    def test_heldout_reads_and_shell_tampering_are_denied_during_run(self):
        self.run_tool("lab.tools.lock", "freeze", str(self.thread), "--by", "adi")
        self.set_stage("run")
        self.assertEqual(self.hook("Read", file_path=str(self.thread / "scorer/heldout/labels.csv")), "deny")
        self.assertEqual(self.hook("Bash", command="cat scorer/heldout/labels.csv"), "deny")
        self.assertEqual(self.hook("Bash", command="sed -i 's/0.1/0.2/' scorer/score.py"), "deny")
        self.assertEqual(self.hook("Bash", command="echo '{}' > P1_toy/results/measured.json"), "deny")
        self.assertIsNone(self.hook("Bash", command="cat scorer/score.py"))
        self.assertIsNone(self.hook("Bash", command="python -m lab.tools.gates " + str(self.thread) + " P1"))
        self.assertEqual(self.hook("Bash", command="python -m lab.tools.gates x P1 && rm scorer/score.py"), "deny")

    def test_paths_outside_a_thread_are_ignored(self):
        self.assertIsNone(self.hook("Write", file_path=str(self.tmp / "notes.md")))


if __name__ == "__main__":
    unittest.main()
