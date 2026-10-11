# Astra critical review of the lab validation design

Date: 2026-10-11. Reviewer: `gpt-6-astra`, high reasoning, independent review context. Reviewed against repository HEAD `73017b7` and the user's revised, uncommitted `artifacts/lab_validation_design_2026-10-11.md`. Relevant gstack review methodology applied read-only. No evaluations executed and no design changes made.

**Verdict: revise before building the pilot.** The evaluation architecture is stronger, but it conflates proposed scientific policy with deployed skill behavior. The first slice cannot invoke its named skills with the listed packets. Some historical-case rules would bias the benchmark toward the over-exclusion it is intended to detect.

## 1. [P1] Separate target scientific policy from deployed instructions

Design lines 16, 35, 171 and 321.

The design scores six evidence classes and N1–N6 across mechanism, formal, commercial, and non-QML cases. Every actual role receives `criteria/lab_method.md`, which instead specifies N1–N5, GO/NO-GO/BLOCKED categories, a blanket real-data decision rule, and industrial operating-point requirements. Screening applies all five QML criteria; its protocols do not implement profile dispatch.

A component correctly following those instructions can fail the benchmark's different policy. Silently overriding them would test a modified component. This is a scientific-policy conflict, not merely a vocabulary mismatch.

**Fix:** freeze a policy/profile adapter. Score scientific adequacy under the target policy separately from compliance with deployed instructions. Translate verdicts using evidence and scope, not a one-to-one label mapping. Mark unsupported profiles explicitly, or version instruction overrides as a separate candidate. Attribute policy failures separately from reasoning failures.

Evidence: `lab/README.md:69`, `criteria/lab_method.md:39`, `criteria/lab_method.md:181`, `lab/roles/screen-analyst/PROTOCOL.md:24`.

## 2. [P1] The fixed packets do not satisfy native skill contracts

Design lines 295–297, 315 and 321.

The proposed verdict-only pack has a hypothesis, evidence packet, verdict key and mutations. `/qml-verdict` requires valid thread state, a verified lock and a nonblocked panel result; its writer consumes a proposal, phase reports/gates/provenance, and prewritten verdict sentences. `/qml-audit` verifies provenance and splits, recomputes metrics, and reruns stored code at specified sizes and against the classical baseline. Summary statistics from a paper cannot fulfill these obligations. The prereg example similarly omits approved CP1/state and native outputs.

Invoking full skills yields precondition failures or an appropriate INSUFFICIENT audit. Bypassing these requirements creates an interpretation exercise rather than full-skill validation.

**Fix:** define two explicit surfaces: bounded interpretation-role tests with named responsibility overrides, and full-skill fixtures with native state, prerequisites, locks, provenance/splits, raw data and runnable code. Label benchmark-created locks retrospective. Specify checkpoint behavior and legitimate early-stop routes; a paper kill must not fail for missing artifacts from deliberately skipped stages.

Evidence: `.agents/skills/qml-verdict/SKILL.md:28`, `lab/roles/verdict-writer/PROTOCOL.md:7`, `lab/roles/verdict-auditor/PROTOCOL.md:20`, `.agents/skills/qml-prereg/SKILL.md:31`, `.agents/skills/qml-screen/SKILL.md:57`.

## 3. [P1] Isolation is required in step 1

Design lines 120, 281 and 321–323.

Step 3 defers the access-controlled runtime, but steps 1–2 already invoke file/shell-capable skills while withholding answer keys, original results and production memory. Withholding paths from prompts does not enforce that boundary.

The existing test harness supplies a `config_override.json` and prompt override. Lab Python tools instead resolve output paths through `LAB_OUTPUT_ROOT` or actual workspace configuration, and checkpoint configuration through `LAB_CONFIG_DIR`. They do not consume that JSON override.

**Fix:** introduce an allowlisted process/workspace boundary at the first slice, hide evaluator files, and propagate `LAB_OUTPUT_ROOT` and `LAB_CONFIG_DIR` to disposable stores. Verify forbidden reads and production writes before grading. Defer only the bulk search service to step 3.

Evidence: `.agents/skills/test-skills/SKILL.md:153`, `lab/tools/common.py:14`, `lab/tools/common.py:41`.

## 4. [P1] Known-fate candidates require claim-level adjudication

Design lines 71–77.

The design requires papers whose central claim was refuted, then makes support for that claim a critical failure. Two candidate pairings are conditional limitations rather than established blanket refutations:

- [Thanasilp et al.](https://arxiv.org/abs/2208.11060) derive concentration under specified conditions involving expressivity, measurements, entanglement and noise. This does not itself refute every feature-map regime or Havlicek et al.'s demonstrated constructions.
- [Bermejo et al.](https://arxiv.org/html/2408.12739v1) address low-bodyness and locally easy datasets, with quantum acquisition of classical shadows still potentially needed. [Cong et al.](https://arxiv.org/abs/1810.03787) also make phase-recognition and error-correction claims, not only claims about classical hardness.
- [Tang](https://arxiv.org/abs/1807.04271) is a cleaner case for a claimed exponential recommendation speedup under comparable sampling access. It does not refute correctness of the quantum algorithm or all possible polynomial advantages.

The design acknowledges that candidates need verification, but its required expected behavior assumes they will become refuted-central-claim cases.

**Fix:** call them candidate claim-level challenge pairs until reviewed. Record the exact original proposition, later theorem/result, matched assumptions/access model, and surviving claims. Conditional limitation is a valid separate class. Only verified contradictions receive mandatory rejection labels.

## 5. [P1] Historical corpus membership does not prevent revision leakage

Design lines 87 and 118.

An arXiv ID submitted before the cutoff can acquire later abstracts, arguments, results and references. The bulk metadata filter plus on-demand fetch does not require historical versions for every document. Unversioned references resolve to the latest version; recording today's response makes leakage repeatable rather than historical. See [official arXiv reference documentation](https://github.com/arXiv/arxiv-docs/blob/develop/source/help/faq/references.md).

**Fix:** pin each source to the last version available before the cutoff, including searchable metadata, abstracts, full text and snippets. Record version IDs/hashes and reject unversioned fetches. Treat unavailable historical versions as coverage gaps. Add a case where a later revision contains forbidden information.

## 6. [P2] Historical risk labels must be justified by historical evidence

Design line 77.

Requiring the screen to name the eventual failure mode as amber rewards hindsight when no then-available evidence makes that particular risk foreseeable. A speculative list or memorized later result can outscore disciplined uncertainty.

**Fix:** require a pre-cutoff evidence locator or derivation from allowed assumptions for mandatory historical risks. Otherwise accept calibrated uncertainty and report anticipation separately as exploratory foresight. Freeze historical and current-assessment keys independently.

## 7. [P2] Split analyst quality from retrieval quality

Design lines 139, 151–153, 253 and 323.

The scorecard combines screen and literature scout, but `screen-analyst` may not search the web. It identifies gaps and returns `needs-research`; the enclosing skill calls `/qml-deep-research`, then reruns the analyst. A bare analyst cannot satisfy retrieval recall, while the full skill is a composed workflow. Giving BM25 directly to the analyst changes the tested component.

**Fix:** separately test the analyst on curated literature, the deployed research component on frozen-corpus retrieval, and the composite screen/research/screen workflow. Attribute recall to the retrieving component or composite, and log research requests, budgets and intermediate artifacts.

Evidence: `lab/roles/screen-analyst/PROTOCOL.md:33`, `.agents/skills/qml-screen/SKILL.md:47`.

## Clarifications, not additional firm findings

- The Opus 5.5 June 2026 cutoff was verified against the [official model documentation](https://platform.claude.com/docs/en/models/opus-5-5/overview). Do not flag that date as incorrect. The recognition probe still needs a specific matching rule: correct broad predictions can be inference, and an unsuccessful probe does not establish absence of memorization. Use suspected-contamination labels and preserve partition counts.
- The 20-example judge calibration target explicitly disclaims statistical assurance. The design's criterion-level disagreement tracking and inspection of passes are sensible. An executable calibration rubric is needed before ranking candidates; the number 20 is not itself a defect.

## Retain and next step

Retain curated-input versus pipeline comparisons, acceptance of scientifically equivalent designs, clean cases alongside planted defects, critical failures that cannot be averaged away, family-level independence, and limits on qualification from small holdouts.

**Recommended next step:** prove one runnable fixture and its policy/adapter contract before investing reviewer time in four paper packs. This is a review recommendation, not an implementation decision.
