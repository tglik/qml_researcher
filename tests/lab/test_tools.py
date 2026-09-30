"""End-to-end tests for lab/tools through their CLIs (the same interface the skills use).

    python -m unittest discover -s tests/lab -v        (from the repo root)

Each test builds a throwaway program thread in a temp git repo and a temp config, so nothing
touches the real vault or config/lab_autonomy.json.
"""
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

PROPOSAL = """---
thread: toy
---
# Pre-registration — toy

```lock
id: baseline.adequacy
kind: baseline
text: Classical arm within 1.1x of published SOTA MAE 0.10 on the test split.
```

```lock
id: splits.definition
kind: split
text: 80/20 random split, seed 0, created before modeling.
```

```lock
id: P1.G4.threshold
kind: threshold
text: Headroom (classical error minus oracle error) must be at least 0.02.
op: ">="
value: 0.02
```

```lock
id: P1.stop_rule
kind: stop_rule
text: If P1.G4 fails, stop the program.
```
"""


class LabToolsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.vault = self.tmp / "vault"
        self.thread = self.vault / "experiments" / "toy_thread" / "01_toy"
        self.thread.mkdir(parents=True)
        (self.vault / "indexes").mkdir()
        self.cfg = self.tmp / "config"
        self.cfg.mkdir()
        shutil.copy(REPO / "config" / "lab_autonomy.json", self.cfg / "lab_autonomy.json")
        subprocess.run(["git", "init", "-q", str(self.vault)], check=True)
        subprocess.run(["git", "-C", str(self.vault), "-c", "user.email=t@t", "-c", "user.name=t",
                        "commit", "-q", "--allow-empty", "-m", "init"], check=True)
        self.env = {**os.environ, "LAB_OUTPUT_ROOT": str(self.vault), "LAB_CONFIG_DIR": str(self.cfg),
                    "PYTHONPATH": str(REPO)}

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def run_tool(self, *args, ok=True):
        r = subprocess.run([sys.executable, "-m", *args], cwd=REPO, env=self.env, capture_output=True, text=True)
        if ok and r.returncode != 0:
            self.fail(f"{' '.join(args)} failed:\n{r.stdout}\n{r.stderr}")
        if not ok and r.returncode == 0:
            self.fail(f"{' '.join(args)} should have failed:\n{r.stdout}")
        return r.stdout + r.stderr

    def new_program(self):
        self.run_tool("lab.tools.state", "new", str(self.thread), "--owner", "meir", "--path", "use-case")

    # --- state -----------------------------------------------------------------------------
    def test_state_new_validate_and_preconditions(self):
        self.new_program()
        self.run_tool("lab.tools.state", "validate", str(self.thread))
        out = self.run_tool("lab.tools.state", "check", str(self.thread), "--need", "lock", ok=False)
        self.assertIn("not frozen", out)
        out = self.run_tool("lab.tools.state", "check", str(self.thread), "--need", "cp:CP1", ok=False)
        self.assertIn("CP1 not approved", out)

    # --- lock ------------------------------------------------------------------------------
    def test_lock_freeze_verify_detects_drift_and_amend_timing(self):
        self.new_program()
        (self.thread / "PROPOSAL.md").write_text(PROPOSAL)
        self.run_tool("lab.tools.lock", "freeze", str(self.thread), "--by", "adi")
        self.run_tool("lab.tools.lock", "verify", str(self.thread))
        self.run_tool("lab.tools.lock", "freeze", str(self.thread), "--by", "adi", ok=False)  # once only
        # silent threshold move is caught
        (self.thread / "PROPOSAL.md").write_text(PROPOSAL.replace("value: 0.02", "value: 0.01"))
        out = self.run_tool("lab.tools.lock", "verify", str(self.thread), ok=False)
        self.assertIn("CHANGED  P1.G4.threshold", out)
        # amendment before data access is accepted
        self.run_tool("lab.tools.lock", "amend", str(self.thread), "--touches", "P1.G4.threshold",
                      "--reason", "panel issue 3", "--phase", "P1", "--by", "tsahi")
        self.run_tool("lab.tools.lock", "verify", str(self.thread))
        # once data exists for P1, a further amendment is refused
        (self.thread / "P1_toy" / "raw").mkdir(parents=True)
        (self.thread / "P1_toy" / "raw" / "m.csv").write_text("gap\n0.03\n")
        self.run_tool("lab.tools.provenance", "record", str(self.thread), "P1", "--id", "P1.gap", "--value", "0.03",
                      "--file", "P1_toy/raw/m.csv", "--command", "python run.py")
        (self.thread / "PROPOSAL.md").write_text(PROPOSAL.replace("value: 0.02", "value: 0.005"))
        out = self.run_tool("lab.tools.lock", "amend", str(self.thread), "--touches", "P1.G4.threshold",
                            "--reason", "late", "--phase", "P1", "--by", "tsahi", ok=False)
        self.assertIn("already has data", out)

    def test_freeze_requires_core_kinds(self):
        self.new_program()
        (self.thread / "PROPOSAL.md").write_text("```lock\nid: x\nkind: metric\ntext: m\n```\n")
        out = self.run_tool("lab.tools.lock", "freeze", str(self.thread), "--by", "adi", ok=False)
        self.assertIn("no lock block of kind", out)

    # --- gates -----------------------------------------------------------------------------
    def test_gates_computed_from_lock_and_refuse_invented_gates(self):
        self.new_program()
        (self.thread / "PROPOSAL.md").write_text(PROPOSAL)
        self.run_tool("lab.tools.lock", "freeze", str(self.thread), "--by", "adi")
        res = self.thread / "P1_toy" / "results"
        res.mkdir(parents=True)
        (res / "measured.json").write_text(json.dumps({"P1.G4.threshold": {"value": 0.031, "provenance_id": "P1.gap"}}))
        out = self.run_tool("lab.tools.gates", str(self.thread), "P1")
        self.assertIn("| P1.G4.threshold | 0.031 | >= 0.02 | PASS | P1.gap |", out)
        (res / "measured.json").write_text(json.dumps({"P1.G9.new": {"value": 1}}))
        out = self.run_tool("lab.tools.gates", str(self.thread), "P1", ok=False)
        self.assertIn("cannot be invented after freeze", out)

    # --- autonomy --------------------------------------------------------------------------
    def test_sign_rejects_author_and_logs_rows(self):
        self.new_program()
        self.run_tool("lab.tools.state", "open-cp", str(self.thread), "CP1", "--author", "person:meir")
        out = self.run_tool("lab.tools.autonomy", "sign", str(self.thread), "CP1", "--by", "meir", "--decision",
                            "approve", "--outcome", "unchanged", "--minutes", "10", ok=False)
        self.assertIn("signer = author", out)
        self.run_tool("lab.tools.autonomy", "sign", str(self.thread), "CP1", "--by", "adi", "--decision",
                      "approve", "--outcome", "minor", "--minutes", "12")
        self.run_tool("lab.tools.state", "check", str(self.thread), "--need", "cp:CP1")
        log = (self.vault / "indexes" / "autonomy-log.md").read_text()
        self.assertIn("| CP1 | HUMAN_APPROVE | person:meir | adi | approve | minor | 12 |", log)

    def test_step_down_needs_streak_evals_and_approver(self):
        self.new_program()
        for i in range(5):
            self.run_tool("lab.tools.state", "open-cp", str(self.thread), "CP1", "--author", "agent:screen-analyst")
            self.run_tool("lab.tools.autonomy", "sign", str(self.thread), "CP1", "--by", "adi", "--decision",
                          "approve", "--outcome", "unchanged", "--minutes", "8")
        out = self.run_tool("lab.tools.autonomy", "step-down", "CP1", "--by", "tsahi", ok=False)
        self.assertIn("evals missing", out)
        for e in ("eval1-screen-replay", "eval4-scoping", "eval5-algorithm-path"):
            self.run_tool("lab.tools.autonomy", "eval", e, "pass")
        self.run_tool("lab.tools.autonomy", "step-down", "CP1", "--by", "adi", ok=False)   # not an approver
        out = self.run_tool("lab.tools.autonomy", "step-down", "CP1", "--by", "tsahi")
        self.assertIn("HUMAN_SPOTCHECK", out)
        # a material finding restores the previous mode automatically
        self.run_tool("lab.tools.state", "open-cp", str(self.thread), "CP1", "--author", "agent:screen-analyst")
        self.run_tool("lab.tools.autonomy", "sign", str(self.thread), "CP1", "--by", "adi", "--decision",
                      "reject", "--outcome", "material", "--minutes", "30")
        cfg = json.loads((self.cfg / "lab_autonomy.json").read_text())
        self.assertEqual(cfg["checkpoints"]["CP1"]["mode"], "HUMAN_APPROVE")

    def test_auto_only_below_human_approve_and_spotcheck_restores(self):
        self.new_program()
        self.run_tool("lab.tools.state", "open-cp", str(self.thread), "CP1", "--author", "agent:screen-analyst")
        out = self.run_tool("lab.tools.autonomy", "auto", str(self.thread), "CP1", "--decision", "approve", ok=False)
        self.assertIn("HUMAN_APPROVE", out)
        cfg = json.loads((self.cfg / "lab_autonomy.json").read_text())
        cfg["checkpoints"]["CP1"]["mode"] = "HUMAN_SPOTCHECK"
        cfg["spotcheck"]["sample_rate"] = 1.0
        (self.cfg / "lab_autonomy.json").write_text(json.dumps(cfg))
        self.run_tool("lab.tools.autonomy", "sign", str(self.thread), "CP1", "--by", "adi", "--decision",
                      "approve", "--outcome", "unchanged", "--minutes", "5")   # close the HUMAN_APPROVE one
        self.run_tool("lab.tools.state", "open-cp", str(self.thread), "CP1", "--author", "agent:screen-analyst")
        out = self.run_tool("lab.tools.autonomy", "auto", str(self.thread), "CP1", "--decision", "approve")
        self.assertIn("spot-check pending", out)
        self.run_tool("lab.tools.autonomy", "spotcheck", str(self.thread), "CP1", "--by", "meir",
                      "--outcome", "material", "--minutes", "15")
        cfg = json.loads((self.cfg / "lab_autonomy.json").read_text())
        self.assertEqual(cfg["checkpoints"]["CP1"]["mode"], "HUMAN_APPROVE")

    # --- guard ----------------------------------------------------------------------------
    def test_guard_catches_protected_edit_during_phase(self):
        self.new_program()
        (self.thread / "PROPOSAL.md").write_text(PROPOSAL)
        self.run_tool("lab.tools.lock", "freeze", str(self.thread), "--by", "adi")
        git = ["git", "-C", str(self.vault), "-c", "user.email=t@t", "-c", "user.name=t"]
        subprocess.run(git + ["add", "-A"], check=True)
        subprocess.run(git + ["commit", "-q", "-m", "freeze"], check=True)
        self.run_tool("lab.tools.state", "set", str(self.thread), "--by", "/qml-run", "--stage", "run", "--phase", "P1")
        subprocess.run(git + ["commit", "-qam", "phase start"], check=True)
        (self.thread / "P1_toy").mkdir()
        (self.thread / "P1_toy" / "run.py").write_text("print(1)\n")
        self.run_tool("lab.tools.guard", str(self.thread))                      # allowed files only
        (self.thread / "VERDICT.md").write_text("# premature verdict\n")
        out = self.run_tool("lab.tools.guard", str(self.thread), ok=False)
        self.assertIn("protected file changed during P1: VERDICT.md", out)

    # --- splits / provenance ---------------------------------------------------------------
    def test_splits_are_immutable(self):
        self.new_program()
        (self.thread / "test_ids.csv").write_text("1\n2\n")
        self.run_tool("lab.tools.splits", "hash", str(self.thread), "--name", "test", "--file", "test_ids.csv")
        (self.thread / "test_ids.csv").write_text("1\n3\n")
        self.run_tool("lab.tools.splits", "hash", str(self.thread), "--name", "test", "--file", "test_ids.csv", ok=False)
        self.run_tool("lab.tools.splits", "verify", str(self.thread), ok=False)

    def test_provenance_detects_changed_file(self):
        self.new_program()
        (self.thread / "P1_toy" / "raw").mkdir(parents=True)
        f = self.thread / "P1_toy" / "raw" / "m.csv"
        f.write_text("x\n1\n")
        self.run_tool("lab.tools.provenance", "record", str(self.thread), "P1", "--id", "n1", "--value", "1",
                      "--file", "P1_toy/raw/m.csv", "--command", "python a.py")
        self.run_tool("lab.tools.provenance", "check", str(self.thread))
        f.write_text("x\n2\n")
        self.run_tool("lab.tools.provenance", "check", str(self.thread), ok=False)

    # --- ledger ----------------------------------------------------------------------------
    def test_ledger_validation_rules(self):
        led = self.vault / "indexes" / "exclusion-ledger.md"
        led.write_text("""# Exclusion ledger

## good-entry
```yaml
id: good-entry
status: provisional
created: 2026-07-29
verdict_ref: experiments/x/VERDICT.md
mechanism: >
  something structural
excludes: >
  The polylog construction as a ranking component of a recommendation stage at any scale.
does_not_exclude: >
  Other constructions.
evidence: [exp-04]
audit: legacy-human
review_by: 2027-09-30
topics: [graph-ml]
reopening_condition: >
  rerun with an adequate baseline
```

## bad-entry
```yaml
id: bad-entry
status: final
created: 2026-08-01
verdict_ref: experiments/y/VERDICT.md
mechanism: x
excludes: graph QML
does_not_exclude: >
  n/a
evidence: [exp-05]
audit: INSUFFICIENT
review_by: 2027-09-30
topics: [graph-ml]
```
""")
        out = self.run_tool("lab.tools.ledger", "validate", ok=False)
        self.assertIn("bad-entry: a final entry needs audit CONFIRMED", out)
        self.assertIn("bad-entry: 'excludes' is too short", out)
        self.assertNotIn("good-entry", out)
        sliced = self.tmp / "sliced.md"
        self.run_tool("lab.tools.ledger", "slice", "--before", "2026-07-30", "--out", str(sliced))
        self.assertIn("good-entry", sliced.read_text())
        self.assertNotIn("bad-entry", sliced.read_text())

    # --- validate --------------------------------------------------------------------------
    def test_artifact_sections_checked_against_template(self):
        self.new_program()
        (self.thread / "SCREEN.md").write_text("---\nverdict: PASS\n---\n# Screen\n\n## Verdict\nPASS\n")
        out = self.run_tool("lab.tools.validate", "artifact", str(self.thread / "SCREEN.md"), ok=False)
        self.assertIn("missing section '## G0", out)


if __name__ == "__main__":
    unittest.main()
