"""Offline tests for the Claude Code / Codex harness adapters. No CLI is launched and no model is called."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from lab.tools import eval_verdict as ev
from lab.tools import harness as h


def claude_events(tools=("StructuredOutput",), tool_uses=("StructuredOutput",), answer=None, ok=True):
    events = [{"type": "system", "subtype": "init", "tools": list(tools), "mcp_servers": [],
               "model": "claude-test-model"}]
    events += [{"type": "assistant", "message": {"content": [{"type": "tool_use", "name": n, "input": {}}]}}
               for n in tool_uses]
    events.append({"type": "result", "subtype": "success" if ok else "error_during_execution",
                   "is_error": not ok, "structured_output": answer, "result": "",
                   "usage": {"output_tokens": 10}, "total_cost_usd": 0.01, "num_turns": 2})
    return events


def codex_events(items=("reasoning", "agent_message"), failed=None):
    events = [{"type": "thread.started", "thread_id": "t"}, {"type": "turn.started"},
              {"type": "item.completed", "item": {"type": "error", "message": "code mode host missing"}}]
    events += [{"type": "item.completed", "item": {"type": t, "text": "{}"}} for t in items]
    events.append({"type": "turn.failed", "error": {"message": failed}} if failed else
                  {"type": "turn.completed", "usage": {"input_tokens": 5, "output_tokens": 7}})
    return events


def jsonl(events):
    return "\n".join(json.dumps(e) for e in events)


class ParserTest(unittest.TestCase):
    def test_claude_clean_run_returns_structured_output(self):
        parsed = h.parse_claude(claude_events(answer={"x": 1}))
        self.assertTrue(parsed["completed"])
        self.assertEqual(json.loads(parsed["answer_text"]), {"x": 1})
        self.assertEqual(parsed["violations"], [])
        self.assertEqual(parsed["resolved_model"], "claude-test-model")

    def test_claude_exposed_or_used_tools_are_violations(self):
        parsed = h.parse_claude(claude_events(tools=("StructuredOutput", "Read"), tool_uses=("Read",), answer={}))
        self.assertIn("tools_exposed:StructuredOutput,Read", parsed["violations"])
        self.assertIn("tool_use:Read", parsed["violations"])
        events = claude_events(answer={})
        events[0]["mcp_servers"] = [{"name": "gmail"}]
        self.assertIn("mcp_servers_exposed", h.parse_claude(events)["violations"])
        self.assertIn("no_init_event", h.parse_claude(events[1:])["violations"])

    def test_claude_error_result_does_not_complete(self):
        parsed = h.parse_claude(claude_events(answer={"x": 1}, ok=False))
        self.assertFalse(parsed["completed"])
        self.assertIsNone(parsed["answer_text"])

    def test_codex_clean_run_prefers_last_message_file(self):
        parsed = h.parse_codex(codex_events(), '{"a": 1}')
        self.assertTrue(parsed["completed"])
        self.assertEqual(parsed["answer_text"], '{"a": 1}')
        self.assertEqual(parsed["violations"], [])
        self.assertEqual(parsed["warnings"], ["code mode host missing"])
        self.assertEqual(parsed["usage"]["usage"]["output_tokens"], 7)

    def test_codex_shell_file_mcp_and_search_items_are_violations(self):
        items = ("command_execution", "file_change", "mcp_tool_call", "web_search", "agent_message")
        parsed = h.parse_codex(codex_events(items=items), "{}")
        self.assertEqual(parsed["violations"], ["tool_use:command_execution", "tool_use:file_change",
                                                "tool_use:mcp_tool_call", "tool_use:web_search"])

    def test_codex_usage_limit_is_an_execution_failure(self):
        parsed = h.parse_codex(codex_events(failed="You've hit your usage limit."), None)
        self.assertFalse(parsed["completed"])
        self.assertIn("usage limit", parsed["error"])


class InvocationTest(unittest.TestCase):
    def setUp(self):
        self.binary = Path(tempfile.mkdtemp()) / "fake.exe"
        self.binary.write_text("")

    def invoke(self, harness, stdout):
        captured = {}
        def fake_run(argv, **kwargs):
            captured.update(argv=argv, cwd=kwargs["cwd"], input=kwargs["input"])
            return subprocess.CompletedProcess(argv, 0, stdout, "")
        env = {"CLAUDE_BIN": str(self.binary), "CODEX_BIN": str(self.binary)}
        with patch.dict(os.environ, env), patch("subprocess.run", fake_run):
            out = h.run(harness, "PROMPT", ev.ANSWER_SCHEMA, "model-x", "high")
        return out, captured

    def test_claude_argv_removes_tools_settings_mcp_and_persistence(self):
        out, call = self.invoke("claude-code", jsonl(claude_events(answer={"x": 1})))
        argv = call["argv"]
        self.assertEqual(argv[argv.index("--tools") + 1], "")
        self.assertEqual(argv[argv.index("--setting-sources") + 1], "")
        for flag in ("-p", "--strict-mcp-config", "--no-session-persistence", "--json-schema"):
            self.assertIn(flag, argv)
        self.assertEqual(argv[argv.index("--effort") + 1], "high")
        self.assertEqual(call["input"], "PROMPT")
        self.assertNotIn(str(ev.REPO), str(call["cwd"]))
        self.assertIn("<answer-schema>", out["argv"])
        self.assertTrue(out["completed"])

    def test_codex_argv_ignores_user_config_and_uses_readonly_sandbox(self):
        out, call = self.invoke("codex", jsonl(codex_events()))
        argv = call["argv"]
        for flag in ("exec", "--ignore-user-config", "--ignore-rules", "--ephemeral", "--json",
                     "--output-schema", "--skip-git-repo-check"):
            self.assertIn(flag, argv)
        self.assertEqual(argv[argv.index("-s") + 1], "read-only")
        self.assertEqual(argv[argv.index("-C") + 1], str(call["cwd"]))
        self.assertIn('model_reasoning_effort="high"', argv)
        self.assertEqual(argv[-1], "-")
        self.assertTrue(out["completed"])

    def test_missing_binary_is_reported(self):
        with patch.dict(os.environ, {"CLAUDE_BIN": str(self.binary) + ".missing"}):
            with self.assertRaises(h.HarnessError):
                h.find_binary("claude-code")


class SchemaTest(unittest.TestCase):
    def test_answer_schema_is_strict_and_matches_grader_fields(self):
        schema = ev.ANSWER_SCHEMA
        self.assertEqual(set(schema["required"]), ev.FIELDS)
        self.assertEqual(set(schema["properties"]), ev.FIELDS)
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(set(schema["properties"]["evidence_class"]["enum"]), ev.CLASSES)
        nested = schema["properties"]["reported_result"]
        self.assertEqual(set(nested["required"]), set(nested["properties"]))
        self.assertFalse(nested["additionalProperties"])


class ExecuteTest(unittest.TestCase):
    def fake(self, answer=None, violations=(), completed=True, error=None):
        return {"completed": completed, "answer_text": json.dumps(answer) if answer else None,
                "violations": list(violations), "resolved_model": "m", "usage": {}, "warnings": [],
                "error": error, "stdout": "", "stderr": "", "argv": []}

    def execute(self, fake, case="v02"):
        folder = Path(tempfile.mkdtemp())
        with patch.object(h, "find_binary", return_value=Path("fake")), \
             patch.object(h, "version", return_value="1.0"), \
             patch.object(h, "run", return_value=fake):
            return ev.execute(folder, case, "direct", "claude-code", "m"), folder

    def test_correct_answer_passes_and_records_harness(self):
        row, folder = self.execute(self.fake(ev.control_answer("v02")))
        self.assertEqual(row["structural_result"], "PASS")
        manifest = ev.read_json(folder / "manifest.json")
        self.assertEqual(manifest["harness"], "claude-code")
        self.assertEqual(manifest["execution_status"], "COMPLETED")

    def test_tool_use_fails_even_with_correct_answer(self):
        row, _ = self.execute(self.fake(ev.control_answer("v02"), violations=["tool_use:command_execution"]))
        self.assertEqual(row["structural_result"], "FAIL")
        self.assertIn("forbidden_tool_use:tool_use:command_execution", row["critical_failures"])

    def test_incomplete_run_is_not_scored(self):
        row, folder = self.execute(self.fake(completed=False, error="usage limit"))
        self.assertEqual(row["execution_status"], "ERROR_NO_SCIENTIFIC_SCORE")
        self.assertFalse((folder / "scores.json").exists())

    def test_suite_stops_at_first_error_and_keeps_denominator(self):
        outcomes = [self.fake(ev.control_answer("v01")), self.fake(completed=False, error="usage limit")]
        root = Path(tempfile.mkdtemp())
        with patch.object(ev, "new_report_dir", return_value=root), \
             patch.object(h, "find_binary", return_value=Path("fake")), \
             patch.object(h, "version", return_value="1.0"), \
             patch.object(h, "run", side_effect=outcomes), patch("builtins.print"):
            _, summary = ev.suite("claude-code", "m", ["v01", "v02"], ["direct"], 2)
        stats = summary["by_candidate"]["direct"]
        self.assertEqual((stats["runs"], stats["completed"], stats["execution_errors"], stats["not_run"]), (4, 1, 1, 2))
        self.assertEqual(stats["confusion"], {"SUPPORTED_SIGNAL": {"SUPPORTED_SIGNAL": 1}})
        self.assertIn("usage limit", summary["stopped_early"])

    def test_false_exclusion_is_counted(self):
        wrong = {**ev.control_answer("v03"), "evidence_class": "EMPIRICAL_NEGATIVE"}
        row, _ = self.execute(self.fake(wrong), case="v03")
        self.assertEqual(ev.summarize([row])["direct"]["false_exclusions"], 1)


if __name__ == "__main__":
    unittest.main()
