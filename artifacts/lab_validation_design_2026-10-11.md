---
document_type: internal_design
date: 2026-10-11
status: proposed
implementation_status: synthetic_interpretation_fixture_only
---

# Validating the research lab through papers and controlled evidence

## 1. Recommendation and boundaries

Build a paper-based evaluation suite for individual research components, then use the same cases to diagnose the full pipeline. Keep the current architecture until these tests identify a reason to change it. The hypothesis that components are the main problem is plausible, but has not yet been established.

A paper supplies a reference research trajectory, not an unquestionable answer. Evaluate whether the lab finds the decisive evidence, designs tests that distinguish competing explanations, executes them correctly, and limits its conclusions to what the evidence supports. Similar prose or agreement with the authors is insufficient.

Include QML, quantum computing, computational physics, and classical ML. Share general research criteria, with domain- and claim-specific adapters. A mechanism study, a replication, a formal result, and a commercial-advantage claim need different tests.

This document specifies evaluation, not a new lab implementation. Numerical targets below are proposed pilot targets, not measured performance or accepted deployment requirements. It does not create scientific claims, exclusions, or production knowledge-graph entries.

**Implementation checkpoint (after Astra review):** one synthetic verdict-interpretation family now has a runnable request builder, deterministic grader and adversarial grader controls in `lab/tools/eval_verdict.py`. Contract and usage: `tests/fixtures/paper_replay/verdict_v1/README.md`. This tests an explicitly adapted role under a target policy, not the deployed full skill. Real-paper reference packs, full-skill isolation, independent key adjudication and a measured model baseline are still outstanding. The original Astra review is preserved in `artifacts/lab_validation_design_astra_review_2026-10-11.md`.

## 2. What exists locally

Inspected in `qml_researcher`:

- `.agents/skills/test-skills/SKILL.md`: YAML cases, artifact evaluation, separate baseline comparison, and score reports already provide a useful starting point.
- `tests/cases/`: research, review, extraction, synthesis, and primitive-transfer cases exist.
- `tests/baselines/`: only `README.md`; no committed score baselines were present at inspection.
- Existing review rubrics predominantly measure completeness, formatting, counts, and traceability within generated artifacts. They do not have independently curated sets of decisive prior work or experimental requirements.
- Citation checking in the evaluator samples identifier formats. Identifier validity does not establish source existence or support for a claim.
- The evaluator says never to award identical scores across axes. Remove that restriction when implementing this design: equal scores can be correct; forcing variance introduces error.
- A strong-paper test preselects `CREDIBLE` or `LANDMARK`. Replace prestige-driven expectations with adjudicated claim-specific evidence and acceptable interpretations.
- `config/workspace.json` currently points to a Mac path. Evaluation must resolve an explicit isolated output root on the actual host.

The September 23 lab design in `qml_artifacts/sources/documents/qml-agent-lab-design_2026-09-23.md` specifies intake, screen, preregistration, execution, verdict, audit, variants, and promotion. It already proposes profile selection, evidence classes, false-exclusion testing, and protected evaluation.

The lab skills are now present (commit `73017b7`): `.agents/skills/qml-intake`, `qml-screen`, `qml-prereg`, `qml-review-panel`, `qml-run`, `qml-verdict`, `qml-audit`, `qml-variants`, `qml-promote`, and `qml-lab`. Adapters bind to these names; in this document "experiment designer" means `qml-prereg`. Do not treat the older untracked August architecture plan as the current implementation or overwrite it.

The deployed `criteria/lab_method.md` differs from the September proposal: it has N1–N5, GO/CONDITIONAL-GO/NO-GO-FINAL/NO-GO-PROVISIONAL/BLOCKED categories, and industrial/real-data requirements without implemented profile dispatch. Freeze this policy alongside every candidate. The six-condition, multi-profile policy below is a target policy; it must never be silently substituted while reporting a deployed baseline. Score target scientific adequacy and deployed-policy compliance separately. Label unsupported profiles `UNSUPPORTED_PROFILE`, or explicitly version a profile override as a modified candidate. Translate verdicts using evidence and scope rather than a one-to-one label mapping. Attribute policy-caused failures separately from component reasoning.

Existing lab evals, to fold into this suite rather than run as a parallel track:

| Case | What it tests | Status for this design |
|---|---|---|
| `qml-screen/eval1-screen-replay` | Gate-earliness on four closed experiments; all known answers are kills | Contaminated development test: INSIGHTS and the criteria were distilled from these same experiments. It rewards correct kills and has no viable case, so it cannot measure false exclusion. |
| `qml-audit/eval2-audit-replay` | Auditor finds the M01 size-matched-control and baseline-adequacy issues | Blocked on M01 migration; keep as an audit challenge |
| `qml-verdict/eval3-false-kill` | Classical salvage survives a dead quantum claim | Keep; this tests salvage, not wrongful exclusion of a viable quantum claim |
| `qml-intake/eval4-scoping` | Refusal to accept a topic as a hypothesis | Keep as the intake case |
| `qml-intake/eval5-algorithm-path` | Dequantizable, readout-bound, and Clifford fixtures | Keep; synthetic kills. Pair each with a near-match viable variant (§7) |

Current lab coverage is therefore heavily weighted toward detecting dead ideas. Paper replay with viable and known-fate cases is the counterweight.

## 3. Evaluate three levels

| Level | How it runs | Question it answers |
|---|---|---|
| Component | A single component receives independently curated upstream artifacts | Can this component perform its responsibility when the input is adequate? |
| Pipeline | Components receive the outputs actually generated by their predecessors | Do good local components compose, and where does error accumulate? |
| Controlled intervention | Change one scientifically relevant fact or inject one defect | Does the component respond to evidence rather than repeat a familiar answer? |

For every important component, compare a curated-input run with a generated-input run. If the designer succeeds with curated literature but fails with the screen's output, investigate screening and the handoff. If it fails with both, investigate its own instructions, context, tools, or capabilities.

When a pipeline fails, replace one upstream artifact at a time with its curated counterpart and rerun the affected suffix. Record the first divergence and whether the replacement repairs downstream behavior. One substitution is diagnostic evidence, not proof of a unique cause.

## 4. Construct paper cases

### Paper selection

Start with 12 independently reviewed papers: approximately three each from QML, QC, computational physics, and classical ML. Include understandable claims, accessible methods and evidence, identifiable decisive experiments or derivations, and tractable subsets where execution is possible. At least four should have runnable data/code or a small trusted numerical reference.

Quality means inspectable and defensible evidence, not citation count or venue. Include strong mechanism results and rigorous negative/null studies. A positive paper can also produce an inconclusive test case when decisive evidence is withheld. A hardware-only paper can test planning and interpretation without pretending its apparatus can be reproduced locally.

**Prefer externally adjudicated claims.** The team's own experiments are not expert-validated and are not reference keys. A paper alone supplies expert-produced evidence but not an expert-validated verdict, and QML conclusions often overstate their evidence. Prefer papers whose claims someone independent of the curators has already judged, so curators transcribe judgments rather than make them. Sources, strongest first:

1. Matched re-evaluations and benchmarks that re-run published methods under comparable conditions (one paper adjudicates several claims).
2. Independent replications (ReScience C, ML Reproducibility Challenge, replication sections of later papers).
3. Claim-specific rebuttals: classical simulations of quantum-advantage experiments, dequantizations, published comments and replies, errata, retractions.
4. Public peer review with meta-review (OpenReview), including rejected submissions.
5. The paper's own evidence only. Use only where the curators are competent to label; the label is provisional.

**Selection order.** Rank candidates by: (1) an external adjudication of the exact claim exists; (2) the claim is specific enough to judge; (3) results report enough uncertainty to build a packet; (4) code or data is available; (5) the corpus keeps its domain and outcome mix (supported, refuted, conditionally limited, inconclusive); (6) the date relative to the tested model's training cutoff fits the intended split. Field- and age-normalized citation impact is a tiebreaker and a pointer to where challenge papers are likely to exist, never a correctness signal: highly cited claims include claims later weakened, and the rebuttals themselves add citations.

**Label confidence tiers.** Assign per claim, not per paper, by rule rather than a weighted score:

| Tier | Requirement | Use |
|---|---|---|
| A | A replication or matched re-evaluation by an unrelated group tests this exact claim, and both reviewers agree on the label | Headline metrics |
| B | An external critique addresses the claim (meta-review, comment, conditional limitation, rebuttal), and both reviewers agree | Headline metrics |
| C | Only the paper's own evidence, or a single reviewer's judgment | Reported separately as a diagnostic |
| Unscorable | Reviewers disagree, or external sources conflict | Kept as an acceptable outcome set; not scored |

Author information is used only for independence: a replication by the original group or close collaborators does not reach tier A. Author prestige, h-index and venue never raise a label's confidence; §7 tests that the candidate's assessment is invariant to prestige cues, and a prestige-weighted key would reward the bias that test detects. Absence of a published challenge is not confirmation.

Add approximately 12 controlled variants spanning supported, excluded, inconclusive, and invalid evidence. These are related tasks, not 12 additional independent papers.

**Claim-level challenge pairs.** Synthetic mutations test response to planted defects; real subsequent work can challenge assumptions or change a claim's status. Include at least three candidate paper/follow-up pairs, classified only after independent adjudication as contradiction, dequantization under matched access, conditional limitation, or surviving claim. Do not assume that each original central claim was refuted. For each pair record the exact original proposition, later theorem/result, applicable regime and access model, and surviving claims. Candidates:

- Havlíček et al. 2019, quantum-enhanced feature spaces → concentration conditions in [Thanasilp et al.](https://arxiv.org/abs/2208.11060). Treat this as a candidate conditional limitation, not a blanket refutation of feature maps.
- Cong, Choi, Lukin 2019, QCNN → low-bodyness/locally-easy regimes and quantum-data acquisition qualifications in [Bermejo et al.](https://arxiv.org/html/2408.12739v1). Test the exact claim rather than declaring all QCNN results refuted.
- Kerenidis–Prakash recommendation speedup → [Tang's dequantization](https://arxiv.org/abs/1807.04271) under comparable sampling access. Distinguish exponential speedup from algorithm correctness or possible polynomial differences. This overlaps synthetic `eval5`; keep both in development.

Run adjudicated challenge pairs in both information modes (§5). Require a historical risk only when a pre-cutoff source locator or derivation from permitted assumptions supports it; otherwise accept calibrated uncertainty. Report anticipation of later findings separately as exploratory foresight. Freeze historical and current keys independently. In current mode require retrieval and correct application of the later challenge, with mandatory rejection only for the exact verified contradiction. Supporting a surviving claim is valid. These familiar pairs belong in contaminated development, not holdout.

Split approximately eight papers for development and four for initial holdout. Partition by research family and mechanism; keep all derivatives of a paper in the same split. If the chosen corpus cannot support a meaningful family split, revise it. Four holdout papers support diagnosis, not deployment qualification.

### The reference pack

For each paper, produce and independently review:

| Artifact | Content |
|---|---|
| `source_manifest.json` | Paper version, publication/preprint dates, full-text hash, supplement, data and code versions, corrections, availability |
| `hypothesis.md` | Outcome-free claim, necessary definitions, access model, regime, domain, profile, constraints, unknowns |
| `literature_gold.json` | Canonical source IDs, relevance role, criticality, supporting locators, acceptable equivalents, justified omissions |
| `design_gold.json` | Claim-to-test map: arms, controls, observables, confounders, sensitivity, resource assumptions, must-have checks, acceptable alternatives |
| `evidence_packet/` | Results, uncertainty, sampling units, validity checks, methods/protocol information, raw outputs where available |
| `verdict_gold.json` | Evidence-licensed claims, acceptable decision/evidence classes, limitations, prohibited overclaims, reopening conditions |
| `mutations.json` | Changed fact, expected response, rationale, reference verification, paired original case |

Extract a draft automatically, then have a domain reviewer validate it and a second reviewer check the decisive labels, tests, and potential flaws. For QML/QC, Tsahi and Adi can divide these responsibilities; use an appropriate specialist for unfamiliar physics. The executing agent must not author or revise its own scoring key.

The paper is one source for the reference pack. Supplement it with verified omitted baselines, related work, corrections, and independent methodological judgment. Use external references where they exist, because they are not authored by the curators:

- **Public peer reviews** (OpenReview for ICLR/NeurIPS/TMLR): reference critiques for the review panel; requested baselines and ablations become design-adequacy items. Prefer ML cases with public reviews, including rejected submissions.
- **Actual follow-up work**: the paper's future-work section and later papers that built on, corrected, or refuted it give the variants component an external reference. Score whether a proposed variant anticipates a follow-up the field actually ran, alongside judged testability.
- **Citation metadata**: Semantic Scholar `isInfluential` and citation `intents` give a cheap first draft of `literature_gold.json` roles and weights. Curators correct it; it is not the key. Preserve disagreement as an acceptable outcome set or an unscorable item instead of forcing a false exact label. Freeze and version the reference pack before comparison.

Do not invent a preregistration for a paper that did not preregister. Record its historical protocol status honestly. A retrospective frozen benchmark packet tests interpretation; it does not retroactively validate confirmatory claims.

### Two reconstruction tasks

1. **Open design:** supply a sufficiently specified, outcome-free hypothesis and constraints. Score discriminating experiments and scientific adequacy; allow methods different from the paper's.
2. **Constrained reconstruction:** also supply necessary method/interface details without results. Score faithful testing of that method, plus justified improvements.

An abstract often contains the headline result. Rewrite it to remove outcomes, conclusion language, exact gains, author identity, and distinctive wording where possible. Review that the rewritten hypothesis remains technically meaningful. Missing essential definitions should lead to focused clarification, not a failed rediscovery score.

## 5. Prevent answer access and distinguish evaluation modes

### Historical reconstruction

Freeze an accessible literature corpus as of a declared prepublication date. Exclude the target paper, its supplements/code/readmes, later papers citing its result, and answer-bearing local memories. Cases must have a legitimate prepublication evidence set; note gaps.

Do not hand-curate the corpus from the target's bibliography plus selected distractors. That leaks the answer by construction: retrieval becomes finding a few planted items in a small pile, and recall is inflated. Build the corpus from a bulk snapshot: arXiv metadata (titles, abstracts, categories, dates) filtered by the relevant categories (e.g. `quant-ph`, `cs.LG`, `stat.ML`, `cond-mat`, `physics.comp-ph`) and the cutoff date, served through a local search tool (BM25 and/or embeddings) with the same interface for every case. Full text is fetched on demand only for documents in the snapshot. References that exist only in journals are a reported coverage gap, not silently added.

For every searchable/fetched source, resolve the last version available before the cutoff, not merely an ID submitted before it. Pin version IDs and hashes for metadata, abstracts, full text and snippets. Reject unversioned fetches and mark unavailable historical versions as coverage gaps. Test this boundary with an old ID whose later revision contains forbidden results. Score retrieval recall over the accessible required set, and separately report coverage of the complete reference set; unavailable sources must not be counted as retrieval failures or silently removed from reporting.

Do not implement this by merely telling an agent not to open files or by filtering search dates. The runtime must expose only allowed files and tools. Evaluator-only materials live outside the tested process's accessible filesystem. A manifest controls access to documents and cached tool responses. Contract tests deliberately attempt forbidden reads and fetches.

Use separate allowed views for hypothesis intake, search, design, execution, and verdict. The verdict receives results when interpretation is the task; the designer does not receive those results. Independent component tests can receive curated intermediate artifacts without revealing the answer key.

Masking titles and authors reduces cues but cannot eliminate model-training contamination. Do not rely on the agent disclosing recognition. Run a separate, fresh-context closed-book probe with a frozen match rule for distinctive results, not generic scientifically plausible predictions. Matching results marks `SUSPECTED_CONTAMINATION`; an unsuccessful probe does not prove absence of memorization. Preserve all partition counts and do not pass probe responses into candidate context. Prefer papers after a verified model-specific training cutoff, rechecking documentation when the model changes; private/prospective cases provide stronger evidence. Perturbations supplement these checks. Never claim that a model forgot a paper because the title was removed.

### Current assessment

Allow current literature, including later corrections, but declare access to the target explicitly. If the target is visible, score review and critique, not independent reconstruction. Use a current reference pack; do not penalize a researcher for finding newer decisive work absent from an old bibliography.

### Stable regression versus live tools

Use a frozen corpus and pinned tool responses for repeatable component comparisons. Also run a smaller live search suite to measure today's retrieval, availability, and tool behavior. Report these separately: a changed search index is not automatically a prompt regression.

## 6. Component scorecards

| Component | Curated input | Reference/checks | Primary failures |
|---|---|---|---|
| Intake | Hypothesis plus scripted answers to legitimate questions | Correct claim, regime, profile, unknowns and falsifier | Invented assumptions; changing the question; unnecessary interrogation |
| Screen analyst | Scoped hypothesis and curated literature | Evidence interpretation, assumptions, remaining gaps and justified research requests | Unsupported rejection; failure to ask for decisive missing evidence |
| Literature retrieval | Analyst's research request and allowed corpus | Decisive prior work, competing methods and accurate source roles | Missing critical sources; superficial lists; wrong source attribution |
| Composite qml-screen | Scoped hypothesis, native context and retrieval adapter | Screen → needs-research → qml-deep-research → rerun behavior | Lost questions/evidence at handoffs; failures to delegate or use findings |
| Experiment designer / prereg | Hypothesis plus curated literature and constraints | Claim-to-test coverage, controls, informative precision, resource fairness, executable plan | No distinguishing ablation; inadequate baseline; an experiment incapable of settling its claim |
| Classical baseline champion | Task, data interface, allowed resources | Trusted comparator performance/tolerance and tuning adequacy | Weak control; access mismatch; comparison at unequal accuracy or cost |
| Implementer / runner | Frozen reference plan, development data, permitted environment | Trusted small-instance outputs, invariants, hidden tests and positive controls | Code that runs but measures the wrong quantity; failed implementation reported as science |
| Review panel | Plan/result packet with planted and clean cases; methods of papers with public reviews | Correct issue identification, severity, repair, false alarms; recovery of decisive issues raised in public peer review | Accepting a decisive defect; blocking sound work with generic objections |
| Verdict | Fixed protocol/methods plus fixed evidence packet | Licensed evidence class, decision, effect/uncertainty, scope | Null estimate treated as exclusion; computational failure treated as refutation; generality inflation |
| Auditor | Evidence/provenance plus candidate verdict | Independently recomputed decisive metrics and planted defects | Echoing the verdict; trusting a summary over raw evidence |
| Variants | Adjudicated result or anomaly and budget | Changed assumption, plausible mechanism, cheapest discriminating test; overlap with follow-ups the field actually ran | Rephrasing a dead idea; novelty without testability; new claims presented as established |
| Promotion / memory | Adjudicated source plus staging workspace | Exact scope, evidence ceiling, provenance, idempotency and valid transitions | Scope widening; benchmark contamination of production memory; invalid permanent exclusion |

### Screening metrics

The deployed `screen-analyst` cannot search the web: it returns `needs-research`, and `/qml-screen` delegates to `/qml-deep-research` before rerunning it. Score analyst judgment separately from retrieval recall. Put the frozen-corpus adapter on the retrieving component; providing search directly to the analyst is an explicit modified candidate, not the deployed baseline. Log intermediate research requests, outputs, reruns and shared budgets.

Build a must-find set from the paper's related work plus independent review. Distinguish essential predecessors, strongest comparators, counterarguments, and optional background. Do not require every bibliography item: many references do not bear on the hypothesis.

Compute weighted recall over canonical, deduplicated sources: sum of weights of recovered relevant items divided by total required weight. Count recovery only if the agent explains the source's role accurately. Separately report relevance precision over all retrieved sources, coverage of claim challenges, and citation existence/support accuracy. Allow verified equivalents and additions; adjudicate them without silently rewriting historical scores.

### Design metrics

Match experimental purpose, not text or the exact implementation. Score which claimed effects each proposed test distinguishes, which alternative explanation it controls, and whether its possible outcomes change the next decision. Separate reference-study coverage from independently judged adequacy.

A cheaper experiment can beat the paper's design if it answers the scoped question. Adding ten unrelated experiments should not improve the score. Treat exact historical hyperparameters as necessary only for a faithful replication task. In current assessment, require current appropriate baselines; in historical reconstruction, avoid demanding methods unavailable at the cutoff.

### Execution metrics

Run a small but scientifically meaningful portion of the reference plan before large sweeps. Compare predictions/observables and decisive metric calculations to a trusted implementation within justified numerical or sampling tolerances. Test normalization, known limits, conservation/symmetry where applicable, split independence, convergence, and positive controls.

Hardware claims require actual hardware evidence or an explicit simulation/resource-analysis scope. A classical stand-in cannot establish untested hardware behavior. Keep fidelity to the published protocol separate from the adequacy of that protocol.

### Verdict metrics

Interpretation tests supply fixed evidence. Independent discovery runs must produce evidence through execution; if they use a different plan, score the conclusion against their own valid outputs and protocol. Do not require the paper's numerical result after changing the experiment.

Under the target policy, separate the operational decision from evidence classes: `SUPPORTED_SIGNAL`, `EMPIRICAL_NEGATIVE`, `FORMAL_EXCLUSION`, `INCONCLUSIVE`, and `INVALID_OR_BLOCKED`. `DECISION_STOP` describes an operational stop and does not erase the scientific evidence class. Check target N1–N6 before an empirical negative. Evaluate the deployed N1–N5 policy separately as described in §2. A single experiment remains subject to the observed claim ceiling; agreement with a published paper is not an independent reproduction.

Report author-conclusion agreement only as a diagnostic. Correctly identifying an unsupported conclusion should improve evidence-faithfulness even when agreement decreases.

## 7. Controlled challenges

Use one change per initial paired test, with a verified expected consequence. Some changes should alter the conclusion; others should leave it invariant.

| Intervention | Expected behavior |
|---|---|
| Add a verified classical twin valid in the claimed regime | Reassess the quantum contribution; narrow or reject only the affected claim |
| Replace a weak control with a stronger, equally resourced baseline that closes the gap | Update the advantage assessment and explain why |
| Keep a near-null estimate but widen uncertainty beyond the useful-effect boundary | Move from a licensed negative to inconclusive |
| Inject leakage or fail a known-answer/positive-control test | Block interpretation and identify a repair; do not declare scientific refutation |
| Change quantum-native input to classical input | Recheck the access model and applicable advantage argument |
| Change resource, noise, or output assumptions | Reassess only claims relying on those assumptions |
| Supply an expired or advisory exclusion, or a near-match outside its scope | Do not reject by ledger lookup alone |
| Remove one decisive ablation while leaving headline results | Identify the unresolved competing explanation |
| Rename methods, reorder evidence, or remove prestige cues | Preserve the scientific assessment |
| Supply a sound plan without planted flaws | Accept it without manufacturing objections |

Include incomplete/noisy/misleading tool returns to test recovery. Attribute tool failure separately while scoring whether the agent disclosed the missing evidence and avoided inventing it. Adversarial mutations are diagnostic tests; they do not estimate the frequency of natural production errors.

### Worked example: fixed verdict packets

Illustrative graph-learning claim: a specified quantum method improves a prespecified score by at least 0.5 percentage points over an adequate classical control under matched resources. Assume each interval has been constructed using the frozen procedure and correct independent sampling unit.

| Evidence packet | Expected evidence class |
|---|---|
| Gain 0.8 pp; interval [0.6, 1.0] pp; validity passes | Scoped supported signal; no general quantum-advantage claim |
| Gain 0.1 pp; interval [-0.1, 0.3] pp; all negative requirements pass | Scoped empirical negative for the useful-effect claim |
| Gain 0.2 pp; interval [-2, 3] pp | Inconclusive: a useful effect remains compatible |
| Same small gain, but positive control fails | Invalid/blocked pending repair |
| Sound result, but cost exceeds an approved practical budget | Separate operational stop from the scientific evidence class |

This catches overconfident rejection and indiscriminate enthusiasm without requiring expensive quantum execution for every test. Execution correctness still needs separate runnable cases.

## 8. Grading and judging

Use three complementary graders, consistent with established agent-evaluation guidance [1]:

1. **Deterministic:** artifact schemas, actual citation resolution against pinned metadata, evidence locators, metric recomputation, hashes, forbidden-access attempts, state transitions, and numerical reference tests.
2. **Independent semantic judge:** reference-to-output matching, quality of controls, applicability of assumptions, missing explanations, and calibrated scope. Fresh context per case; blind to candidate version, baseline scores, and author prestige. Prefer a different model when useful, but do not equate model diversity with independence or correctness.
3. **Human adjudication:** validate reference packs, calibrate judge scoring, resolve disagreements, and review all decisive qualification failures. Human reviewers also score a random sample of passes to detect lenient judges.

Adjudication signals are evaluator-side only. Citation counts, citation stance, replication outcomes, review scores and author identities never enter candidate context; showing them reintroduces the prestige cues §5 masks. Automated stance labels (Semantic Scholar intents, scite-style supporting/contrasting labels, LLM stance classification) only nominate challenge papers; a citing paper enters a reference pack after a human reads the citing passage and the claim it addresses.

Before judging agents, test the grader on known-good and deliberately flawed artifacts, verbosity/presentation variants, and injected instructions in candidate text. Treat candidate output as data, never judge instructions. Require a reference locator and output locator for each material score. Permit tied scores and justified disagreement.

Calibrate on at least 20 stage-output examples before trusting aggregate judge rankings; use more when disagreement remains material. This is a pilot workload target, not statistical assurance. Record human/automatic disagreement by criterion, not just overall agreement. If judgments are unreliable, report the affected axis as unqualified.

Keep readable 0–5 axes for development if useful. Critical defects override an average: fabricated decisive evidence, forbidden answer access, invalid metrics, unauthorized promotion, or an unsupported binding exclusion cannot be compensated by excellent prose.

Missing a required artifact fails that required task. Deliberately withheld evidence, a justified N/A, an infrastructure failure, and a contaminated case receive distinct states. Report denominators and all exclusions; do not turn an inconclusive scientific answer into an unscored case merely to improve accuracy.

## 9. Comparisons, metrics, and attribution

Compare under the same model where possible, information, tools, budgets, and stopping rules:

- Current component/pipeline version.
- A simple direct-prompt researcher using the same model and tools, without the specialized role structure.
- A curated human reference on a subset, with time recorded and scientific scoring blinded.

Change one component at a time. Log the model identifier, settings, complete rendered instructions, skill/agent hashes, criteria and ledger versions, source/tool fixtures, runtime/harness revision, context construction, retries, and all artifacts. Inspect omitted/truncated context and incorrect role instructions before assuming a capability failure.

Repeat agentic component cases three times initially; use repeated seeds/runs where applicable. Pin recorded tool responses for paired comparisons. Report typical performance and failure frequency, not only best-of-three. Run expensive executable cases once for pilot correctness, then repeat with justified independent units when drawing performance conclusions.

Report per component, domain, profile, and evidence class:

- Essential-work recall, retrieval precision, citation existence/support.
- Essential-test coverage, controls, implementation/reference correctness.
- Verdict confusion matrix, false exclusions, unsupported support, appropriate inconclusive/blocked decisions, and confidence calibration where probabilities are requested.
- Planted-defect sensitivity and false alarms on clean cases.
- Pipeline versus curated-input gap, handoff losses, paired intervention behavior.
- Tokens/tool calls, compute, wall-clock, retries, completion rate, and human correction minutes.

Confidence estimates require a defined event: for example, probability that an independent reviewer will confirm the proposed evidence class, rather than an undefined probability that a broad hypothesis is true.

Bootstrap/comparison uncertainty at the independent paper/family level where suitable. Trials, mutants, seeds, and ablations from one paper are correlated; they cannot be counted as independent qualification examples. Tiny held-out sets should show individual cases and descriptive variation rather than precise-looking reliability claims.

## 10. Initial targets and qualification

Proposed pilot targets, to calibrate after reviewing initial cases:

- Screen: recover every predesignated decisive refutation/comparator and at least 80% weighted relevant work; report precision alongside recall.
- Designer: include every adjudicated indispensable test/control or a justified equivalent; independently judge whether the plan can resolve its claim.
- Runner: pass all decisive small-reference, positive-control, and numerical-validity checks.
- Verdict/audit: no unsupported binding exclusion or decisive ungrounded claim; select an acceptable evidence class and preserve scope on every critical challenge.
- Pipeline: no unauthorized transition, promotion, or answer-access breach. Correctly blocked actions and legitimate early stops pass their route-specific contract; artifacts from skipped stages are not missing required outputs.
- Improvement: repeatable gain over the current version on the relevant component, without a critical regression or unacceptable cost increase.

These are diagnostic acceptance criteria, not proof that the lab is ready for automatic binding decisions. Qualification needs a human-approved tolerable error rate, an adequately sized family-held-out set, and prospective shadow runs. As a statistical illustration, zero errors among n independent, representative opportunities gives a one-sided 95% binomial upper bound of `1 - 0.05^(1/n)`. Around 59 such opportunities are needed just to put that bound below 5%; clustered or selectively chosen cases do not meet that independence/representativeness premise.

Keep exclusions advisory during development and shadow evaluation. Qualification is versioned by model, skills, criteria, memory, runtime and access controls; scope it to the profiles/families actually tested. Prior historical NO-GOs are development material pending independent review, not unquestioned ground truth.

## 11. Minimal implementation shape

Extend `/test-skills`; do not add another autonomous framework. Keep current YAML case discovery and reports, but move objective comparisons and regression arithmetic into deterministic code. The first deterministic companion CLI is `python -m lab.tools.eval_verdict`; it is callable now. Candidates run through Claude Code and Codex, the two harnesses the lab is deployed in, via `lab/tools/harness.py` (headless, fresh session, tools removed in Claude Code and detected in Codex); the raw OpenAI API path remains for comparison. Automatic routing through `/test-skills` is not yet implemented; do not invoke its generic full-skill runner for this role-only fixture.

Proposed layout (paths and fields below do not yet exist):

```text
tests/
  cases/paper-replay/          # visible case contracts, splits, modes, stage requirements
  fixtures/paper-replay/       # allowed inputs/corpus snapshots, with scoped mounts
  graders/                    # deterministic comparisons and semantic grading rubrics
  baselines/                  # accepted versioned reports
  reports/                    # isolated run artifacts, metrics and traces
private evaluator store/
  gold/paper-replay/           # reference sections, annotations, expected outcomes
```

The private store must be inaccessible to the tested process; merely putting gold in another directory within the repo is insufficient. Existing output-path overrides should prevent writes to configured live artifacts. Benchmark execution must never update production cards, INSIGHTS, or the exclusion ledger. Test promotion in a disposable store.

Enforce isolation from the first test. For role-only interpretation, a fresh tool-free API request carries only allowlisted inline policy and evidence; it has no filesystem, attachments, history, or tool executor. Committed development gold remains in the trusted evaluator and is never serialized to the candidate. This boundary is implemented in the first fixture. A normal agent in the repo is not equivalent isolation. Full-skill runs need a process/filesystem allowlist with private gold plus disposable `LAB_OUTPUT_ROOT` and `LAB_CONFIG_DIR` propagated to every child. The existing `config_override.json` prompt convention is not consumed by lab Python tools and cannot enforce those settings or protect files.

### Native versus role-only fixture contracts

Interpretation-role tests replace native file/state and reproduction duties with an explicit, versioned interpretation contract. Report the adaptation, target policy, source hashes and excluded responsibilities. They cannot certify the full skill or deployed-policy compliance.

Full-skill fixtures must use native artifact names and requirements: verdict needs valid STATE, lock, PROPOSAL (including frozen verdict sentences), HYPOTHESIS, nonblocked PANEL_2, and applicable phase reports/gates/provenance. Audit additionally needs split/provenance checks, raw data, stored runnable code/environment/seeds, and reproduction at the protocol's required sizes. Prereg needs approved CP1 and native prereg state, passing SCREEN, all native outputs and panel behavior. Benchmark locks are retrospective and never portrayed as original-paper preregistration. Specify checkpoint stubs and allowed terminal routes per test; a legitimate paper kill does not require later experiment artifacts.

Example case contract:

```yaml
id: paper-replay-graph-mechanism-01-design
paper_family: graph-mechanism-family-a
split: development
domain: qml
profile: mechanism
task: open-design
test_surface: interpretation_role_only  # not a native qml-prereg invocation
stage: prereg
information_mode: historical
literature_cutoff: "curator-specified-ISO-date"
inputs: [hypothesis.md, curated_screen.md, constraints.json]
reference_key: graph-mechanism-01/design-v1  # evaluator resolves; agent cannot access
required_outputs: [PROPOSAL.md]
forbidden_access: [target-paper, gold-store, target-code, target-results]
trials: 3
budgets:
  tokens: curator-specified
  tool_calls: curator-specified
graders: [access_contract, claim_test_coverage, design_adequacy]
critical_checks: [adequate_controls, no_result_access]
```

The runtime supplies allowed inputs and tools, captures trace/artifact state, and enforces the budget. The grader receives references only after the candidate run. A missing deployed component is `NOT_AVAILABLE`, not a simulated successful invocation. Reject cases with unresolved placeholder values at load time.

Possible future interfaces: `--suite paper-replay`, `--stage screen`, `--inputs curated|pipeline`, `--mutations`, and `--compare VERSION`. These are proposed extensions; only existing `/test-skills` interfaces should be represented as currently callable.

## 12. Rollout and concrete deliverables

### Human cost budget

Reference packs are the expensive part, and the scarce resource is Tsahi's and Adi's time. Estimate (not measured): 5–8 reviewer-hours per full paper pack, including a second review of the decisive labels. A 12-paper corpus is therefore about 60–100 hours. Record actual hours per pack from the first paper onward and revise the corpus size if the estimate is wrong. Build only the artifacts the current slice scores. Role-only verdict interpretation needs `hypothesis.md`, `evidence_packet/`, `verdict_gold.json`, and `mutations.json`, plus its explicit adapter contract. Native verdict/audit tests also require the state, protocol and runnable evidence listed in §11; do not cost them as summary-packet tasks.

### First diagnostic slice, ordered by build cost

Build the slice in three steps. Each step produces a usable diagnosis before the next infrastructure is built.

1. **One verdict-interpretation fixture and its policy/adapter contract.** First prove serialization isolation and the grader with controlled supported/negative/inconclusive/invalid/boundary/budget packets. The initial implementation is synthetic and role-only. Independently review the key and obtain a model baseline before expanding to four paper interpretation packs. For full `/qml-verdict` or `/qml-audit` tests, build the native fixture contract above; summary-only packets cannot test reproduction. Fold in compatible existing cases without relabeling interpretation as full audit.
2. **Experiment design with curated inputs.** Choose explicitly between a role-only design task and native `/qml-prereg`; supply the corresponding prerequisites. Add `design_gold.json` only for scored papers. Use the already established access boundary plus contamination probes, not probes as a substitute for isolation.
3. **Retrieval and composite screening with a frozen, versioned corpus.** Build the search service here; isolation exists from step 1. Evaluate the analyst separately on curated inputs, then retrieval, then the composed `/qml-screen` workflow. Add adjudicated claim-level challenges (§4) in both information modes.

Add one executable reference case (`qml-run`) after step 2. At every step, run current and direct-prompt baselines, calibrate the grader, and produce a component-by-case failure matrix.

The first deliverable is a diagnosis: missed literature, inadequate design, implementation failure, unsupported verdict, handoff loss, or unreliable scoring. Do not implement replacement components just to make a test run.

### Development suite

Expand to the 12-paper corpus, repeated component tests, controlled mutations, and isolated promotion/contract checks. Fix the weakest measured component, rerun paired cases, and lock reviewed baseline reports. Test the generated-input pipeline and substitution diagnostics.

### Holdout and shadow use

Freeze candidate versions and score unseen families. Failures exposed to developers become development cases; replenish holdout for future qualification. On new real hypotheses, run advisory recommendations alongside independent human work and compare decisions, reasoning, cost, and correction time.

Do not scale autonomy because paper summaries look better. Scale only capabilities that demonstrate reliable evidence handling under held-out and prospective tests.

Current next action: independently adjudicate the first synthetic key and run both explicit interpretation candidates on the same model; retain all failures and human-review requirements. Then construct the first real-paper packet and a separate native fixture for full-skill evaluation. Do not infer lab quality from grader self-checks or expand to four full packs before proving this contract.

## 13. External references

[1] [Anthropic, Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents). Practical support for separating tasks, trials, graders, traces and outcomes; combining deterministic/model/human graders; and distinguishing capability from regression testing. The lab-specific metrics and thresholds here are our proposed design.

[2] [ScienceAgentBench](https://arxiv.org/abs/2410.05080). Builds scientific tasks from peer-reviewed publications with subject-expert validation. Supports paper-derived task construction; it does not validate this lab or the proposed paper-replay suite.

[3] [DiscoveryBench](https://arxiv.org/abs/2407.01725). Derives discovery workflows from published papers across domains and includes controlled synthetic tasks with facet-based evaluation. Useful precedent for task decomposition and controlled cases; not a substitute for our domain-specific reference packs.

Internal sources: the September 23 lab design, canonical `/test-skills`, its evaluator, review-case YAML, baseline inventory, the lab eval cases `eval1`–`eval5`, and `criteria/qml_domain.md`. This proposal extends the September evaluation section with curated paper references, stage-specific access, component-versus-pipeline diagnosis, and claim-sensitive scoring.

Revision 2026-10-11: added the lab-eval inventory (§2), known-fate cases (§4), external reference sources (§4), the bulk-snapshot corpus rule and closed-book memorization probe (§5), the human cost budget, and the cost-ordered first slice (§12).

Post-Astra revision 2026-10-11: distinguished target/deployed policy, interpretation/full-skill fixtures, and analyst/retrieval/composite tests; moved isolation to the first slice; pinned historical source versions; removed hindsight requirements and blanket refutation labels; specified legitimate early-stop handling. Added the runnable synthetic interpretation fixture without changing production scientific policy.
