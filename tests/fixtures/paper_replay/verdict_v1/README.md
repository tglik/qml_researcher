# First verdict interpretation fixture

This is one synthetic family with six packets, not six papers. It proves the input/output and
grading contract before costly paper curation. It does not validate `/qml-verdict`, `/qml-audit`,
their native state transitions, scientific reproduction, or deployed-policy compliance.

## What is runnable

From the repository root with Python 3.10+ (stdlib only):

```powershell
python -m lab.tools.eval_verdict self-check
python -m unittest discover -s tests/lab -p test_eval_verdict.py -v
python -m lab.tools.eval_verdict prepare --case v03 --candidate role-adapted
python -m lab.tools.eval_verdict grade --case v03 --response path/to/answer.json
```

`prepare` writes the exact request and a hash manifest under `output/paper-replay/`; it makes
no model call. `grade` labels imports `EXTERNAL_IMPORT_ACCESS_NOT_VERIFIED`; it cannot establish
how an imported answer was generated. `self-check` grades authored positive/negative controls;
its result is never a model baseline. Scores always leave semantic human review pending.

## Running through Claude Code or Codex

The lab runs inside Claude Code and Codex, so candidates are run through those harnesses headless.
Use full model IDs: aliases such as `haiku` resolve differently depending on which settings load.

```powershell
python -m lab.tools.eval_verdict run --harness claude-code --model claude-opus-5-5 --case v03 --candidate direct
python -m lab.tools.eval_verdict run --harness codex --model gpt-6.1-sol --effort high --case v03
# full pilot: 6 cases x 2 candidates x 3 trials = 36 runs, one summary.json
python -m lab.tools.eval_verdict suite --harness claude-code --model claude-opus-5-5 --trials 3
```

The binaries are found through `$CLAUDE_BIN` / `$CODEX_BIN`, then PATH, then the VS Code extension
(`~/.vscode/extensions/anthropic.claude-code-*/resources/native-binary/claude.exe`) and Codex app
(`~/.codex/.sandbox-bin/codex.exe`) locations. Auth is the harness's own login.

Each run is a fresh session in an empty temporary directory, prompt on stdin, nothing persisted.
The prompt is the same policy and packet the API request carries (`harness-prompt.txt` from
`prepare`); answers are constrained by the strict `ANSWER_SCHEMA`.

| Harness | Flags | Isolation |
|---|---|---|
| `claude-code` | `-p --tools "" --strict-mcp-config --setting-sources "" --no-session-persistence --json-schema` | Enforced: no built-in tools, MCP servers, user/project settings, hooks or CLAUDE.md. The init event must list only the internal `StructuredOutput` tool. |
| `codex` | `exec --ignore-user-config --ignore-rules --ephemeral -s read-only --output-schema --json` | Detected, not enforced: Codex has no switch to remove its shell, and the read-only sandbox still permits reads. Any command, file, MCP or search item fails the run. |

Isolation violations are critical failures that stay in the denominator. Each run folder keeps the
raw event stream (`harness-events.jsonl`), the harness version, resolved model, usage and cost.
`suite` stops at the first execution error (e.g. a usage limit) and records the remaining runs as
`NOT_RUN`. Codex parsing was tested against recorded event shapes only; the first live Codex run
was blocked by a ChatGPT usage limit.

The harness runs use each harness's default system prompt, not the lab skill's native context: this
is still a role-only interpretation test.

## Running through the raw OpenAI API

Set `OPENAI_API_KEY` and choose a model:

```powershell
python -m lab.tools.eval_verdict run --harness openai-api --case v03 --candidate direct --model YOUR_MODEL_ID
```

Each command makes at most one paid request, capped at 3,000 output/reasoning tokens and a
55-second client timeout, with no retry. A timeout does not guarantee provider-side cancellation.
An incomplete result is retained as an execution failure, not quietly retried or omitted.

## Candidate and policy contract

| Candidate | Operative instructions | What a result measures |
|---|---|---|
| `direct` | `policy.md` plus one inline packet | Direct interpretation under target policy v1 |
| `role-adapted` | Current verdict-writer ESSENCE, then explicit `policy.md` overrides | Adapted role interpretation under the same target policy |
| Deployed full skill | Not supported by this runner | Must use future native-state fixture; do not infer its quality here |

`policy.md` explicitly overrides native N1-N5, verdict vocabulary, profile requirements, panel
prerequisites, file writing and structural-mechanism requirements. Source hashes preserve which
deployed role/policy was inspected, but the full native PROTOCOL and lab_method are not sent as
operative instructions. No source files or production policies are changed by running this test.

## Isolation contract

The live candidate is a fresh API model request, not a local shell-capable agent. The trusted
runner sends only policy/selected essence and the chosen inline packet. The request has no tools,
files, conversation, or previous-response ID; tool choice is `none`, truncation is disabled, and
response storage is disabled. There is no tool dispatcher or subprocess execution path. The
candidate cannot read the runner's filesystem, gold file, credentials, or production vault through
this interface. The runner itself is trusted and reads gold only for grading after generation.

Gold is committed for development reproducibility; filesystem placement is not claimed as a
security boundary. The boundary is the tool-free API. Never run the candidate in this repository
with ordinary agent tools and call it isolated. File/shell-capable full-skill tests still require
an OS-enforced allowlist, a private gold store and propagated disposable `LAB_OUTPUT_ROOT` and
`LAB_CONFIG_DIR`; environment overrides alone are not sandboxing.

Transport semantics follow the official [Responses API](https://developers.openai.com/api/reference/resources/responses/methods/create).

## Packets and scoring

- `v01`: supported scoped signal.
- `v02`: precise negative for the minimum-useful-effect claim.
- `v03`: uncertainty includes a useful benefit.
- `v04`: same apparent negative as v02, but measurement validity fails.
- `v05`: interval endpoint equals the useful-effect boundary; no exclusion.
- `v06`: same supported evidence as v01, but spending stops for budget reasons.

`packets.json` supplies evidence, `gold.json` holds the evaluator-only answer key, and `policy.md`
defines the public task. Gold is an author-created provisional key pending independent human
adjudication. Synthetic checks and intervals are stipulations, not measured results or audited
experiments. No formal exclusion task is implemented in v1.

Deterministic checks reject wrong evidence/action classes, false exclusion permission, generalized
advantage, widened scope, altered numbers, fabricated evidence pointers, and schema errors.
Omitted decisive pointers are reported separately as `citation_result`, so a correct verdict with
an incomplete citation list is not counted the same as a wrong verdict.
They cannot judge whether free prose contradicts otherwise correct fields. A structural PASS
therefore remains `human_semantic_review: PENDING` and `scientific_qualification: NOT_ESTABLISHED`.
Do not average critical failures into a passing score or auto-accept any output as a baseline.

Reports include exact requests, source/packet/policy hashes, response bytes, provider model/usage
when available, execution status and grading results. Trials/mutations share one family and do
not constitute independent reliability observations. Runs write only fresh directories beneath
the repository's ignored `output/paper-replay/`, without loading live workspace configuration.

## Human review before accepting a candidate result

Check that the rationale uses the supplied evidence, respects scope and percentage-point units,
does not claim independent execution/audit, does not invent a mechanism, and distinguishes
scientific evidence from spending/promotion decisions. Mark each item pass/fail/unclear with an
output quote. Resolve all decisive failures/unclear items before any baseline acceptance.

Next: independently review this key and one recorded model response, then author a real paper
interpretation packet. Build a separate native fixture before claiming full-skill coverage.
