"""SessionStart/SubagentStart hook that makes the plugin work outside a clone (hooks/qml_env.py).

    python -m unittest tests.lab.test_plugin_env -v      (from the repo root)
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
HOOK = REPO / "hooks" / "qml_env.py"


def run(event: str, project: Path, env_file: Path | None = None, out: str = "") -> dict | None:
    env = {k: v for k, v in os.environ.items() if not k.startswith(("CLAUDE_", "PYTHONPATH"))}
    env.update({"CLAUDE_PLUGIN_ROOT": str(REPO), "CLAUDE_PROJECT_DIR": str(project)})
    if env_file:
        env["CLAUDE_ENV_FILE"] = str(env_file)
    if out:
        env["CLAUDE_PLUGIN_OPTION_OUTPUT_ROOT"] = out
    r = subprocess.run([sys.executable, str(HOOK)], input=json.dumps({"hook_event_name": event}),
                       capture_output=True, text=True, env=env)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout) if r.stdout.strip() else None


class PluginEnvHookTest(unittest.TestCase):
    def test_inside_a_clone_it_does_nothing(self):
        self.assertIsNone(run("SessionStart", REPO))

    def test_outside_a_clone_lab_tools_import_and_output_root_is_set(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            env_file = d / "env"
            env_file.touch()
            res = run("SessionStart", d, env_file, out=str(d / "arts"))
            ctx = res["hookSpecificOutput"]["additionalContext"]
            self.assertIn(f"{REPO}/criteria/lab_method.md", ctx)
            self.assertIn("qml_domain.md", ctx)
            self.assertIn(str(d / "arts"), ctx)
            # a Bash command in an unrelated project, after the env file, imports lab.tools
            cmd = (f"source {env_file}; python3 -c 'from lab.tools.common import output_root; "
                   f"print(output_root())'")
            env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
            r = subprocess.run(["bash", "-c", cmd], cwd=d, capture_output=True, text=True, env=env)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual(r.stdout.strip(), str(d / "arts"))

    def test_without_output_root_the_model_is_told_to_ask(self):
        with tempfile.TemporaryDirectory() as d:
            res = run("SubagentStart", Path(d))
            self.assertEqual(res["hookSpecificOutput"]["hookEventName"], "SubagentStart")
            self.assertIn("not configured", res["hookSpecificOutput"]["additionalContext"])


if __name__ == "__main__":
    unittest.main()
