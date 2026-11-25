"""Study workspace (C16): lab.tools.workspace rules and the lab guard's workspace rules.

    python -m unittest tests.lab.test_workspace -v      (from the repo root)
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
HOOK = REPO / "hooks" / "lab_guard.py"
CID = "c-20990101-001"


class WorkspaceTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        bl = self.root / "indexes" / "backlog"
        (bl / "bet_sheets").mkdir(parents=True)
        (bl / "candidates.jsonl").write_text(json.dumps({
            "id": CID, "title": "Toy bet", "claim": "A toy quantum method beats a toy baseline",
            "base": "none", "direction": "toy-direction",
            "gate": {"novelty": {"score": 0.9}, "value": {"rung": 3, "p": 0.4}}}) + "\n")
        (bl / "bet_sheets" / f"{CID}.json").write_text(json.dumps(
            {"fatal_test": "Compute the toy bound; kill below 2x", "fatal_test_days": 2}))
        (self.root / "workspace").mkdir()
        (self.root / "workspace" / "lab.json").write_text(json.dumps(
            {"agenda": [CID], "budget": {"max_hours": 6, "max_usd": 20}}))
        self.env = {**os.environ, "LAB_OUTPUT_ROOT": str(self.root)}

    def tearDown(self):
        self.tmp.cleanup()

    def ws(self, *args, ok=True):
        r = subprocess.run([sys.executable, "-m", "lab.tools.workspace", *args], cwd=REPO, env=self.env,
                           capture_output=True, text=True)
        if ok:
            self.assertEqual(r.returncode, 0, r.stderr)
        else:
            self.assertNotEqual(r.returncode, 0, r.stdout)
        return r.stdout.strip() + r.stderr.strip()

    def hook(self, tool, tin):
        r = subprocess.run([sys.executable, str(HOOK)], input=json.dumps(
            {"tool_name": tool, "tool_input": tin, "cwd": str(self.root)}), capture_output=True, text=True,
            env={k: v for k, v in os.environ.items() if k != "LAB_GUARD_OFF"})
        return json.loads(r.stdout)["hookSpecificOutput"]["permissionDecision"] if r.stdout.strip() else None

    def fill(self, d: Path):
        t = (d / "STUDY.md").read_text()
        for h, body in (("## Prediction", "Ratio 3.0 at 4 atoms."), ("## Disproof", "Ratio below 2."),
                        ("## Plan", "Compute both bounds; baseline tuned on 50 trials.")):
            head, rest = t.split(h, 1)
            rest = rest.split("\n## ", 1)
            t = head + h + "\n" + body + "\n" + ("\n## " + rest[1] if len(rest) > 1 else "")
        (d / "STUDY.md").write_text(t)

    def start(self) -> tuple[str, Path]:
        self.assertEqual(self.ws("next"), CID)
        sid = self.ws("new", "--from", CID, "--by", "author-a")
        d = self.root / "workspace" / "studies" / sid
        self.assertIn("cheapest fatal test", (d / "STUDY.md").read_text())
        self.assertNotIn("rung", (d / "STUDY.md").read_text())          # no scores copied in
        return sid, d

    def lock(self, sid, d):
        self.fill(d)
        self.ws("post", "announce", "--study", sid, "--by", "author-a", "--body", "Plan: compute bounds.")
        self.ws("post", "critique", "--study", sid, "--by", "critic-b", "--body", "Tune the baseline harder.")
        self.ws("post", "response", "--study", sid, "--by", "author-a", "--changed", "yes", "--body", "Done.")
        self.ws("lock", sid, "--by", "author-a")

    def test_full_lifecycle_and_report(self):
        sid, d = self.start()
        self.lock(sid, d)
        (d / "outputs" / "m.json").write_text('{"ratio": 1.4}')
        self.ws("ledger", sid, "--id", "ratio", "--value", "1.4", "--file", "outputs/m.json", "--command", "python code/x.py")
        (d / "objections" / "o1.py").write_text("print('rerun with 3 seeds')\n")
        self.ws("objection", sid, "--script", "objections/o1.py", "--by", "objector-c", "--flips", "no", "--note", "seeds")
        self.ws("release", sid, "--by", "author-a", ok=False)                 # no audit yet
        (d / "AUDIT.md").write_text("---\nstudy: x\nauditor: auditor-d\nverdict: PASS\n---\nok\n")
        self.ws("release", sid, "--by", "author-a", "--outcome", "refuted", "--cost-usd", "3.5")
        rep = json.loads(self.ws("report"))
        self.assertEqual(rep["summary"]["released"], 1)
        self.assertEqual(rep["summary"]["design_changed_by_critique"], 1)
        self.assertEqual(rep["summary"]["outcomes"]["refuted"], 1)
        self.assertEqual(self.ws("next"), "agenda done: every candidate on lab.json has a study")
        self.assertEqual(self.hook("Write", {"file_path": str(d / "outputs" / "m.json"), "content": "x"}), "deny")

    def test_lock_needs_announce_peer_critique_and_response(self):
        sid, d = self.start()
        self.fill(d)
        self.ws("lock", sid, "--by", "author-a", ok=False)
        self.ws("post", "critique", "--study", sid, "--by", "critic-b", "--body", "x", ok=False)   # not announced
        self.ws("post", "announce", "--study", sid, "--by", "author-a", "--body", "plan")
        self.ws("post", "critique", "--study", sid, "--by", "author-a", "--body", "self", ok=False)  # self-critique
        self.ws("post", "critique", "--study", sid, "--by", "critic-b", "--body", "flaw")
        self.ws("lock", sid, "--by", "author-a", ok=False)                    # no response yet
        self.ws("post", "response", "--study", sid, "--by", "author-a", "--body", "ok", ok=False)  # needs --changed
        self.ws("post", "response", "--study", sid, "--by", "author-a", "--changed", "no", "--body", "ok")
        self.ws("lock", sid, "--by", "author-a")

    def test_template_sections_block_lock(self):
        sid, d = self.start()
        self.ws("post", "announce", "--study", sid, "--by", "author-a", "--body", "plan")
        self.ws("post", "critique", "--study", sid, "--by", "critic-b", "--body", "flaw")
        self.ws("post", "response", "--study", sid, "--by", "author-a", "--changed", "no", "--body", "ok")
        self.assertIn("template", self.ws("lock", sid, "--by", "author-a", ok=False))

    def test_plan_frozen_after_lock_unless_corrected_and_amended(self):
        sid, d = self.start()
        self.lock(sid, d)
        study = str(d / "STUDY.md")
        self.assertEqual(self.hook("Edit", {"file_path": study}), "deny")
        (d / "STUDY.md").write_text((d / "STUDY.md").read_text() + "\nsneaky\n")   # bypassing the hook
        (d / "outputs" / "m.json").write_text("{}")
        self.ws("release", sid, "--by", "author-a", ok=False)                 # tool also catches it
        self.ws("amend", sid, "--by", "author-a", "--reason", "x", ok=False)  # no correction posted
        self.ws("post", "correction", "--study", sid, "--by", "author-a", "--body", "baseline was wrong")
        self.assertIsNone(self.hook("Edit", {"file_path": study}))
        self.ws("amend", sid, "--by", "author-a", "--reason", "fix baseline")
        self.assertEqual(self.hook("Edit", {"file_path": study}), "deny")     # amended: frozen again

    def test_objection_must_be_code_and_audit_must_be_independent(self):
        sid, d = self.start()
        self.lock(sid, d)
        self.ws("objection", sid, "--script", "objections/none.py", "--by", "objector-c", "--flips", "no",
                "--note", "x", ok=False)
        (d / "objections" / "o.py").write_text("pass\n")
        self.ws("objection", sid, "--script", "objections/o.py", "--by", "author-a", "--flips", "no",
                "--note", "x", ok=False)
        (d / "outputs" / "m.json").write_text("{}")
        self.ws("ledger", sid, "--id", "r", "--value", "1", "--file", "outputs/m.json", "--command", "c")
        (d / "AUDIT.md").write_text("---\nauditor: author-a\nverdict: PASS\n---\n")
        self.ws("release", sid, "--by", "author-a", ok=False)
        (d / "AUDIT.md").write_text("---\nauditor: auditor-d\nverdict: FAIL\n---\n")
        self.ws("release", sid, "--by", "author-a", ok=False)
        (d / "outputs" / "m.json").write_text('{"changed": true}')
        (d / "AUDIT.md").write_text("---\nauditor: auditor-d\nverdict: PASS\n---\n")
        self.assertIn("changed", self.ws("release", sid, "--by", "author-a", ok=False))

    def test_hook_protects_tool_files_and_log(self):
        sid, d = self.start()
        for name in ("state.json", "ledger.jsonl", "bundle.lock.json"):
            self.assertEqual(self.hook("Write", {"file_path": str(d / name), "content": "{}"}), "deny", name)
        log = self.root / "workspace" / "log" / "x.md"
        self.assertEqual(self.hook("Write", {"file_path": str(log), "content": "fake"}), "deny")
        self.assertEqual(self.hook("Bash", {"command": f"echo hi > {log}"}), "deny")
        self.assertIsNone(self.hook("Write", {"file_path": str(d / "code" / "run.py"), "content": "x"}))
        self.assertIsNone(self.hook("Read", {"file_path": str(d / "state.json")}))

    def test_agenda_is_set_by_a_person(self):
        self.ws("new", "--from", "c-20990101-999", "--by", "author-a", ok=False)


if __name__ == "__main__":
    unittest.main()
