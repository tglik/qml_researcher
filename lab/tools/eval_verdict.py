"""Tool-free verdict-role fixture. Does not invoke lab skills or touch the live vault.

python -m lab.tools.eval_verdict self-check
python -m lab.tools.eval_verdict prepare --case v03 --candidate role-adapted
python -m lab.tools.eval_verdict run --harness claude-code --case v03 --candidate direct --model MODEL
python -m lab.tools.eval_verdict suite --harness codex --model MODEL --trials 3
python -m lab.tools.eval_verdict grade --case v03 --response response.json

Harnesses: claude-code, codex (headless CLI, tools disabled or detected), openai-api (raw API).
"""
from __future__ import annotations

import argparse
import copy
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import urllib.error
import urllib.request
import uuid

from . import harness as agent_harness

REPO = Path(__file__).resolve().parents[2]
FIXTURE = REPO / "tests/fixtures/paper_replay/verdict_v1"
SOURCES = (
    "lab/roles/verdict-writer/ESSENCE.md",
    "lab/roles/verdict-writer/PROTOCOL.md",
    "criteria/lab_method.md",
    ".agents/skills/qml-verdict/SKILL.md",
)
API_URL = "https://api.openai.com/v1/responses"
CLASSES = {"SUPPORTED_SIGNAL", "EMPIRICAL_NEGATIVE", "INCONCLUSIVE", "INVALID_OR_BLOCKED"}
FIELDS = {"case_id", "evidence_class", "next_action", "scientific_exclusion_licensed",
          "binding_exclusion_allowed", "general_quantum_advantage_established", "scope_id",
          "reported_result", "evidence_refs", "rationale"}
BOOL_FIELDS = {"scientific_exclusion_licensed", "binding_exclusion_allowed",
               "general_quantum_advantage_established"}
NEXT_ACTIONS = ["FOLLOW_UP", "MORE_EVIDENCE", "REPAIR_VALIDITY", "STOP_BUDGET", "STOP_SCOPED_CLAIM"]
RESULT_FIELDS = ["estimate_pp", "lower_pp", "upper_pp", "minimum_useful_effect_pp"]
HARNESSES = ("claude-code", "codex", "openai-api")
ISOLATION = {
    "openai-api": "no_tools_no_files_no_history_api_request",
    "claude-code": "headless_cli_all_tools_removed_verified_from_init_event",
    "codex": "headless_cli_shell_present_readonly_sandbox_tool_use_detected_from_events",
}
# Strict schema: valid for both Claude Code --json-schema and Codex --output-schema.
ANSWER_SCHEMA = {
    "type": "object", "additionalProperties": False, "required": sorted(FIELDS),
    "properties": {
        "case_id": {"type": "string"},
        "evidence_class": {"type": "string", "enum": sorted(CLASSES)},
        "next_action": {"type": "string", "enum": NEXT_ACTIONS},
        **{key: {"type": "boolean"} for key in sorted(BOOL_FIELDS)},
        "scope_id": {"type": "string"},
        "reported_result": {"type": "object", "additionalProperties": False, "required": RESULT_FIELDS,
                            "properties": {key: {"type": "number"} for key in RESULT_FIELDS}},
        "evidence_refs": {"type": "array", "items": {"type": "string"}},
        "rationale": {"type": "string"},
    },
}


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def encoded(value) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False).encode("utf-8")


def read_json(path: Path):
    def invalid_constant(value):
        raise ValueError(f"non-finite JSON number: {value}")
    def unique_object(pairs):
        obj = {}
        for key, value in pairs:
            if key in obj:
                raise ValueError(f"duplicate JSON key: {key}")
            obj[key] = value
        return obj
    return json.loads(path.read_text(encoding="utf-8"), parse_constant=invalid_constant,
                      object_pairs_hook=unique_object)


def packet(case_id: str) -> dict:
    fixture = read_json(FIXTURE / "packets.json")
    matches = [c for c in fixture["cases"] if c["case_id"] == case_id]
    if len(matches) != 1:
        raise ValueError(f"case must identify exactly one packet: {case_id}")
    result = copy.deepcopy(fixture["common"])
    for key, value in matches[0].items():
        if key in ("checks", "limits"):
            result[key].update(value)
        else:
            result[key] = value
    result["fixture_version"] = fixture["fixture_version"]
    result["provenance"] = fixture["provenance"]
    numbers = list(result["result"].values()) + [result["protocol"]["minimum_useful_effect_pp"]]
    if any(type(v) not in (int, float) or not math.isfinite(v) for v in numbers):
        raise ValueError("packet has invalid numeric evidence")
    r = result["result"]
    if not r["lower_pp"] <= r["estimate_pp"] <= r["upper_pp"]:
        raise ValueError("inconsistent interval")
    return result


def build_request(case_id: str, candidate: str, model: str, max_tokens: int = 3000) -> dict:
    """Only allowlisted context crosses the model boundary; never read the gold key here."""
    if candidate not in ("direct", "role-adapted"):
        raise ValueError("unknown candidate")
    if not model.strip() or not 256 <= max_tokens <= 8000:
        raise ValueError("model and token cap (256..8000) are required")
    policy = (FIXTURE / "policy.md").read_text(encoding="utf-8")
    if candidate == "role-adapted":
        essence = (REPO / SOURCES[0]).read_text(encoding="utf-8")
        policy = essence + "\n\n---\nExplicit evaluation adapter (overrides essence):\n" + policy
    return {
        "model": model,
        "instructions": policy,
        "input": [{"role": "user", "content": "Interpret this evidence packet:\n" +
                   json.dumps(packet(case_id), ensure_ascii=False, sort_keys=True)}],
        "tools": [], "tool_choice": "none", "store": False,
        "max_output_tokens": max_tokens, "truncation": "disabled",
        "text": {"format": {"type": "json_object"}},
    }


def harness_prompt(request: dict) -> str:
    """The same instructions and packet as the API request, as one stdin prompt."""
    return request["instructions"] + "\n\n---\n" + request["input"][0]["content"]


def manifest(case_id: str, candidate: str, request: dict, harness: str = "openai-api") -> dict:
    paths = list(SOURCES) + ["lab/tools/eval_verdict.py", "lab/tools/harness.py"]
    return {
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "fixture_version": packet(case_id)["fixture_version"],
        "test_surface": "interpretation_role_only",
        "candidate": candidate, "case_id": case_id, "requested_model": request["model"],
        "harness": harness,
        "request_sha256": digest(encoded(request)),
        "answer_schema_sha256": digest(encoded(ANSWER_SCHEMA)),
        "packet_sha256": digest(encoded(packet(case_id))),
        "source_sha256": {p: digest((REPO / p).read_bytes()) for p in paths},
        "policy_sha256": digest((FIXTURE / "policy.md").read_bytes()),
        "isolation": ISOLATION[harness],
        "native_policy_compliance": "NOT_EVALUATED",
        "full_skill_validation": "NOT_EVALUATED",
        "human_review": "PENDING",
    }


def check_request(request: dict) -> None:
    allowed = {"model", "instructions", "input", "tools", "tool_choice", "store",
               "max_output_tokens", "truncation", "text"}
    if set(request) != allowed or request["tools"] != [] or request["tool_choice"] != "none":
        raise ValueError("request violates no-tool/no-history boundary")
    if request["store"] is not False or request["truncation"] != "disabled":
        raise ValueError("unexpected persistence/truncation policy")
    messages = request["input"]
    if (not isinstance(messages, list) or len(messages) != 1 or
        set(messages[0]) != {"role", "content"} or messages[0]["role"] != "user" or
        not isinstance(messages[0]["content"], str)):
        raise ValueError("only one inline text packet is allowed")


def call_model(request: dict) -> dict:
    check_request(request)
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise ValueError("OPENAI_API_KEY is not configured; no model request was made")
    req = urllib.request.Request(API_URL, data=encoded(request), method="POST", headers={
        "Content-Type": "application/json", "Authorization": "Bearer " + key})
    # No local subprocess, MCP, file attachments, tool loop, conversation, or automatic retry.
    try:
        with urllib.request.urlopen(req, timeout=55) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        raise ValueError(f"model API returned HTTP {exc.code}; no retry was attempted") from None
    except (urllib.error.URLError, TimeoutError) as exc:
        raise ValueError(f"model transport failed ({type(exc).__name__}); no retry was attempted") from None


def model_text(response: dict) -> str:
    if response.get("status") != "completed":
        raise ValueError("model response is incomplete or failed; no scientific score")
    texts = []
    for item in response.get("output", []):
        if item.get("type") == "reasoning":
            continue
        if item.get("type") != "message" or item.get("role") != "assistant":
            raise ValueError("unexpected tool or non-message output; no execution permitted")
        for content in item.get("content", []):
            if content.get("type") != "output_text":
                raise ValueError("model refusal or unexpected content; no scientific score")
            texts.append(content["text"])
    if len(texts) != 1:
        raise ValueError("expected exactly one JSON response")
    return texts[0]


def resolve_ref(data: dict, ref: str):
    current = data
    for key in ref.split("."):
        if not isinstance(current, dict) or key not in current:
            raise ValueError(f"unknown evidence ref: {ref}")
        current = current[key]
    return current


def grade(case_id: str, answer) -> dict:
    data = packet(case_id)
    gold_file = read_json(FIXTURE / "gold.json")
    if gold_file["fixture_version"] != data["fixture_version"]:
        raise ValueError("fixture/gold version mismatch")
    gold = gold_file["cases"][case_id]
    failures, citation_failures = [], []
    if not isinstance(answer, dict) or set(answer) != FIELDS:
        failures.append("response_schema")
    else:
        for key in BOOL_FIELDS:
            if type(answer[key]) is not bool:
                failures.append(f"boolean_type:{key}")
        if answer["case_id"] != case_id:
            failures.append("case_id")
        if answer["scope_id"] != data["scope_id"]:
            failures.append("scope_generalization")
        for key in ("evidence_class", "next_action", "scientific_exclusion_licensed"):
            if answer[key] != gold[key]:
                failures.append(key)
        if answer["binding_exclusion_allowed"] is not False:
            failures.append("unauthorized_binding_exclusion")
        if answer["general_quantum_advantage_established"] is not False:
            failures.append("unsupported_general_advantage")
        expected_numbers = {**data["result"], "minimum_useful_effect_pp":
                            data["protocol"]["minimum_useful_effect_pp"]}
        reported = answer["reported_result"]
        if not isinstance(reported, dict) or set(reported) != set(expected_numbers):
            failures.append("result_schema")
        else:
            for key, value in expected_numbers.items():
                actual = reported[key]
                if (type(actual) not in (int, float) or not math.isfinite(actual) or
                    not math.isclose(actual, value, rel_tol=0, abs_tol=1e-9)):
                    failures.append(f"number:{key}")
        refs = answer["evidence_refs"]
        if (not isinstance(refs, list) or not all(isinstance(r, str) for r in refs) or
            len(refs) != len(set(refs))):
            failures.append("evidence_refs_schema")
        else:
            # Citation completeness is reported separately: a correct verdict that omits one
            # decisive pointer must not be indistinguishable from a false exclusion.
            citation_failures += ["missing_decisive_ref:" + r for r in gold["decisive_refs"] if r not in refs]
            for ref in refs:
                try:
                    resolve_ref(data, ref)
                except ValueError:
                    failures.append(f"fabricated_ref:{ref}")
        if not isinstance(answer["rationale"], str) or not answer["rationale"].strip():
            failures.append("missing_rationale")
    return {
        "case_id": case_id, "structural_result": "FAIL" if failures else "PASS",
        "critical_failures": failures,
        "citation_result": "FAIL" if citation_failures else "PASS",
        "citation_failures": citation_failures,
        "gold_evidence_class": gold["evidence_class"],
        "answer_evidence_class": answer.get("evidence_class") if isinstance(answer, dict) else None,
        "human_semantic_review": "PENDING",
        "scientific_qualification": "NOT_ESTABLISHED",
        "native_policy_compliance": "NOT_EVALUATED", "full_skill_validation": "NOT_EVALUATED",
        "gold_sha256": digest((FIXTURE / "gold.json").read_bytes()),
        "gold_review_status": gold_file["review_status"],
    }


def control_answer(case_id: str) -> dict:
    """Evaluator-only authored control, NEVER a candidate model or baseline."""
    data = packet(case_id)
    gold = read_json(FIXTURE / "gold.json")["cases"][case_id]
    return {
        "case_id": case_id, "evidence_class": gold["evidence_class"],
        "next_action": gold["next_action"], "scope_id": data["scope_id"],
        "scientific_exclusion_licensed": gold["scientific_exclusion_licensed"],
        "binding_exclusion_allowed": False, "general_quantum_advantage_established": False,
        "reported_result": {**data["result"], "minimum_useful_effect_pp":
                            data["protocol"]["minimum_useful_effect_pp"]},
        "evidence_refs": gold["decisive_refs"],
        "rationale": "Authored structural grader control, not an independently generated scientific explanation.",
    }


def self_check() -> dict:
    rows = []
    for case_id in read_json(FIXTURE / "gold.json")["cases"]:
        good = control_answer(case_id)
        rows.append({"case": case_id, "probe": "authored_correct_structure",
                     "passed": grade(case_id, good)["structural_result"] == "PASS"})
        # Every alternative evidence class must fail; a constant-label grader cannot pass.
        for label in sorted(CLASSES - {good["evidence_class"]}):
            wrong = copy.deepcopy(good)
            wrong["evidence_class"] = label
            rows.append({"case": case_id, "probe": "wrong_class:" + label,
                         "passed": grade(case_id, wrong)["structural_result"] == "FAIL"})
        for field, value in (("binding_exclusion_allowed", True),
                             ("general_quantum_advantage_established", True),
                             ("scope_id", "all_quantum_methods"), ("evidence_refs", ["invented"])):
            wrong = copy.deepcopy(good)
            wrong[field] = value
            rows.append({"case": case_id, "probe": field,
                         "passed": grade(case_id, wrong)["structural_result"] == "FAIL"})
        # Omitting decisive pointers is a citation failure, not a wrong verdict.
        uncited = grade(case_id, {**good, "evidence_refs": []})
        rows.append({"case": case_id, "probe": "missing_refs_is_citation_only",
                     "passed": uncited["structural_result"] == "PASS" and uncited["citation_result"] == "FAIL"})
    return {"kind": "grader_self_check_not_model_baseline", "passed": all(r["passed"] for r in rows),
            "checks": rows, "model_calls": 0, "independent_paper_count": 0,
            "family_count": 1, "candidate_quality": "UNMEASURED"}


def new_report_dir() -> Path:
    root = (REPO / "output/paper-replay").resolve()
    if not root.is_relative_to(REPO.resolve()):
        raise ValueError("report root must remain inside this repository")
    path = root / (dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8])
    path.mkdir(parents=True, exist_ok=False)
    return path


def save(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def execute(folder: Path, case_id: str, candidate: str, harness: str, model: str,
              effort: str | None = None, timeout: int = 600) -> dict:
    """One candidate run into `folder`. Execution failures are recorded, never scored."""
    request = build_request(case_id, candidate, model)
    check_request(request)
    save(folder / "request.json", request)
    run_manifest = manifest(case_id, candidate, request, harness)
    run_manifest.update(execution_status="PREPARED_NOT_RUN", requested_effort=effort)
    save(folder / "manifest.json", run_manifest)
    try:
        violations = []
        if harness == "openai-api":
            response = call_model(request)
            save(folder / "provider-response.json", response)
            text = model_text(response)
            run_manifest.update(resolved_model=response.get("model"), usage=response.get("usage"),
                                response_id=response.get("id"))
        else:
            binary = agent_harness.find_binary(harness)
            run_manifest.update(harness_binary=str(binary), harness_version=agent_harness.version(binary))
            out = agent_harness.run(harness, harness_prompt(request), ANSWER_SCHEMA, model, effort, timeout)
            (folder / "harness-events.jsonl").write_text(out["stdout"], encoding="utf-8")
            (folder / "harness-stderr.txt").write_text(out["stderr"], encoding="utf-8")
            run_manifest.update(harness_argv=out["argv"], resolved_model=out["resolved_model"],
                                usage=out["usage"], harness_warnings=out["warnings"],
                                isolation_violations=out["violations"])
            if not out["completed"]:
                raise ValueError(f"{harness} run did not complete: {out['error']}")
            text, violations = out["answer_text"], out["violations"]
        (folder / "answer.json").write_text(text or "", encoding="utf-8")
        try:
            result = grade(case_id, read_json(folder / "answer.json"))
        except ValueError:
            # A completed answer that violates JSON is a candidate contract failure,
            # not a transport error that could disappear from accuracy denominators.
            result = grade(case_id, None)
            result["response_parse_status"] = "INVALID_JSON"
        if violations:
            # Tool use is a critical failure that stays in the denominator, not an excluded run.
            result["critical_failures"] += ["forbidden_tool_use:" + v for v in violations]
            result["structural_result"] = "FAIL"
        result.update(harness=harness, candidate=candidate)
        save(folder / "scores.json", result)
        run_manifest["execution_status"] = "COMPLETED"
        save(folder / "manifest.json", run_manifest)
        return {**result, "execution_status": "COMPLETED", "folder": str(folder)}
    except (ValueError, OSError) as exc:
        run_manifest.update(execution_status="ERROR_NO_SCIENTIFIC_SCORE", error=str(exc))
        save(folder / "manifest.json", run_manifest)
        return {"case_id": case_id, "candidate": candidate, "harness": harness, "folder": str(folder),
                "execution_status": "ERROR_NO_SCIENTIFIC_SCORE", "error": str(exc)}


def summarize(rows: list[dict]) -> dict:
    by_candidate = {}
    for row in rows:
        s = by_candidate.setdefault(row["candidate"], {
            "runs": 0, "completed": 0, "execution_errors": 0, "not_run": 0, "structural_pass": 0,
            "citation_pass": 0, "forbidden_tool_use": 0, "false_exclusions": 0, "confusion": {}})
        s["runs"] += 1
        if row["execution_status"] == "NOT_RUN":
            s["not_run"] += 1
            continue
        if row["execution_status"] != "COMPLETED":
            s["execution_errors"] += 1
            continue
        s["completed"] += 1
        s["structural_pass"] += row["structural_result"] == "PASS"
        s["citation_pass"] += row["citation_result"] == "PASS"
        s["forbidden_tool_use"] += any(f.startswith("forbidden_tool_use") for f in row["critical_failures"])
        s["false_exclusions"] += (row["answer_evidence_class"] == "EMPIRICAL_NEGATIVE" and
                                  row["gold_evidence_class"] != "EMPIRICAL_NEGATIVE")
        cell = s["confusion"].setdefault(row["gold_evidence_class"], {})
        predicted = str(row["answer_evidence_class"])
        cell[predicted] = cell.get(predicted, 0) + 1
    return by_candidate


def suite(harness: str, model: str, cases: list[str], candidates: list[str], trials: int,
          effort: str | None = None, timeout: int = 600) -> tuple[Path, dict]:
    """Every case x candidate x trial. Stops at the first execution error (e.g. a usage limit);
    remaining runs are recorded as NOT_RUN so the denominator stays visible."""
    folder = new_report_dir()
    rows, stopped = [], None
    for trial in range(1, trials + 1):
        for case_id in cases:
            for candidate in candidates:
                if stopped:
                    rows.append({"case_id": case_id, "candidate": candidate, "trial": trial,
                                 "execution_status": "NOT_RUN"})
                    continue
                run_folder = folder / f"{case_id}-{candidate}-t{trial}"
                run_folder.mkdir()
                row = {**execute(run_folder, case_id, candidate, harness, model, effort, timeout), "trial": trial}
                rows.append(row)
                if row["execution_status"] != "COMPLETED":
                    stopped = row["error"]
                print(f"{case_id} {candidate} t{trial}: {row['execution_status']} "
                      f"{row.get('structural_result', '')} {row.get('answer_evidence_class', '')}", flush=True)
    summary = {"kind": "role_only_interpretation_suite", "harness": harness, "requested_model": model,
               "requested_effort": effort, "trials": trials, "stopped_early": stopped,
               "by_candidate": summarize(rows), "runs": rows,
               "note": "Trials and cases share one synthetic family; not independent reliability evidence. "
                       "Human semantic review of rationales is pending for every completed run."}
    save(folder / "summary.json", summary)
    return folder, summary


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "run", "suite", "grade", "self-check"))
    parser.add_argument("--case", default="v03")
    parser.add_argument("--cases", default="all", help="suite: comma-separated case ids or 'all'")
    parser.add_argument("--candidate", choices=("direct", "role-adapted"), default="direct")
    parser.add_argument("--candidates", default="direct,role-adapted")
    parser.add_argument("--harness", choices=HARNESSES)
    parser.add_argument("--model")
    parser.add_argument("--effort", help="reasoning effort passed to the harness (e.g. low, medium, high)")
    parser.add_argument("--trials", type=int, default=3)
    parser.add_argument("--timeout", type=int, default=600, help="seconds per harness run")
    parser.add_argument("--response", type=Path)
    args = parser.parse_args(argv)
    if args.command in ("run", "suite"):
        if not args.harness or not args.model:
            parser.error(f"{args.command} requires --harness and --model; no request made")
        if args.harness == "openai-api" and not os.environ.get("OPENAI_API_KEY"):
            parser.error("openai-api requires OPENAI_API_KEY; no request made")
        if args.harness == "openai-api" and args.effort:
            parser.error("--effort is not supported for openai-api")
    if args.command == "grade" and args.response is None:
        parser.error("grade requires --response")
    if args.command == "suite":
        all_cases = list(read_json(FIXTURE / "gold.json")["cases"])
        cases = all_cases if args.cases == "all" else args.cases.split(",")
        candidates = args.candidates.split(",")
        if set(cases) - set(all_cases) or set(candidates) - {"direct", "role-adapted"} or args.trials < 1:
            parser.error("unknown case/candidate or trials < 1")
        folder, summary = suite(args.harness, args.model, cases, candidates, args.trials, args.effort, args.timeout)
        for candidate, s in summary["by_candidate"].items():
            print(f"{candidate}: {s['structural_pass']}/{s['completed']} structural PASS, "
                  f"{s['citation_pass']}/{s['completed']} citation PASS, false exclusions {s['false_exclusions']}, "
                  f"tool use {s['forbidden_tool_use']}, errors {s['execution_errors']}, not run {s['not_run']}")
        print(folder)
        return 2 if summary["stopped_early"] else 0
    if args.command == "self-check":
        result = self_check()
        folder = new_report_dir()
        save(folder / "self-check.json", result)
        print(f"{sum(r['passed'] for r in result['checks'])}/{len(result['checks'])} grader controls passed; model quality UNMEASURED\n{folder}")
        return 0 if result["passed"] else 1
    if args.command == "grade":
        result = grade(args.case, read_json(args.response))
        result["response_origin"] = "EXTERNAL_IMPORT_ACCESS_NOT_VERIFIED"
        result["response_sha256"] = digest(args.response.read_bytes())
        folder = new_report_dir()
        save(folder / "scores.json", result)
        print(f"Structural result: {result['structural_result']}; human review PENDING\n{folder}")
        return 0 if result["structural_result"] == "PASS" else 1
    if args.command == "prepare":
        request = build_request(args.case, args.candidate, args.model or "MODEL_REQUIRED_FOR_RUN")
        check_request(request)
        folder = new_report_dir()
        save(folder / "request.json", request)
        (folder / "harness-prompt.txt").write_text(harness_prompt(request), encoding="utf-8")
        save(folder / "answer-schema.json", ANSWER_SCHEMA)
        save(folder / "manifest.json", {**manifest(args.case, args.candidate, request),
                                        "execution_status": "PREPARED_NOT_RUN"})
        print(f"Prepared request only; no model call\n{folder}")
        return 0
    folder = new_report_dir()
    row = execute(folder, args.case, args.candidate, args.harness, args.model, args.effort, args.timeout)
    if row["execution_status"] != "COMPLETED":
        print(f"Run failed: {row['error']}\nsee {folder}/manifest.json", file=sys.stderr)
        return 2
    print(f"Structural result: {row['structural_result']}; citations {row['citation_result']}; "
          f"human review PENDING\n{folder}")
    return 0 if row["structural_result"] == "PASS" else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError, KeyError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(2)
