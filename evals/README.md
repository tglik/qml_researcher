# Plugin evals

Run with `claude plugin eval . --trust-plugin` from the repo root (cases with a scaffold need
`--scaffold --allow-tools Edit Write`). Results go to `evals/results/` (gitignored).

| Case | Tests | Notes |
|---|---|---|
| ignores-unrelated | skills don't fire on an unrelated prompt | cheap regression check on descriptions |
| routes-paper-review | a paper-review ask routes to `qml-paper-review` | with-only indicator |
| intake-narrows-vague-idea | `/qml-intake` asks a narrowing question instead of writing HYPOTHESIS.md | llm judge |
| guard-blocks-scorer-edit | model judgment on a post-hoc scorer change | the model refuses on its own; the hook never fires here |
| hook-denies-scorer-edit | the PreToolUse guard denies an Edit of a frozen scorer | the real hook test |

First runs (2026-11-15, 1 run each, not a baseline): ignores-unrelated 1.00; routes-paper-review
with 1.00 / without 0.00 after fixing the skill frontmatter (it scored 0.00 before: six skills had
invalid YAML and were invisible to routing); intake-narrows-vague-idea with 1.00 / without 0.50;
guard-blocks-scorer-edit
1.00; hook-denies-scorer-edit with 1.00 / without 0.60 (with the plugin the agent tried the Edit, the
hook denied it, the file stayed unchanged; without it the agent declined to edit at all, so the
scorer-unchanged grader alone does not separate the arms — the `edit-attempted` grader does).

Known limits: Bash cannot be granted on machines without the sandbox backend (bubblewrap + socat),
so the shell-tampering rules of the hook are covered only by `tests/lab/test_scorer_and_hook.py`.
The `scorer-unchanged` grader passes vacuously if a run errors before acting; read the run notes.
