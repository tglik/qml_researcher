"""Evidence-limited analysis of the replay, including every planned paper.

Does not call models or change saved answers/grades. Run from the repository root.
"""
from __future__ import annotations

import collections
import hashlib
import json
from pathlib import Path
import statistics
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_replay as rr

NOTES = {
    'ml-01': ('Baseline tuning and evaluation leakage', 'Pair a correctly tuned neighborhood/matrix-factorization comparator with a deliberately weak one; score whether the recommendation changes.'),
    'ml-02': ('General superiority versus dataset-specific support', 'Require separate labels for the original three datasets and the broader benchmark; blanket refutation must fail.'),
    'ml-03': ('Empirical effectiveness versus a disputed mechanism', 'Preserve optimization benefits while removing the internal-covariate-shift explanation; score each claim independently.'),
    'ml-04': ('Expressivity theorem versus predictive superiority', 'Change graph families beyond the stated expressivity scope; require the reviewer to preserve the theorem and narrow the benchmark inference.'),
    'ml-05': ('Metric-learning protocol and tuning fairness', 'Match architecture, embedding dimension, augmentation and tuning budget; score whether the loss retains a measurable gain.'),
    'ml-06': ('Stability versus broad generative-model superiority', 'Separate gradient-penalty stability from sample-quality ranking and charge tuning and compute equally.'),
    'ml-07': ('Architecture search versus search-budget advantage', 'Supply random-search and weight-sharing controls at matched budgets; require costs of search as well as final training.'),
    'ml-08': ('Residual architecture versus improved training recipe', 'Add an actual plain-versus-residual factorial control: a better recipe alone cannot causally adjudicate the skip connection.'),
    'ml-11': ('Pretraining contribution versus compute/data confounding', 'Match data, steps and compute, and separate task transfer from claims about the specific pretraining objective.'),
    'phys-01': ('Signal interpretation and independent criticism', 'Use staged evidence about conductance without supplying the retraction label; require an alternative explanation rather than a remembered scandal.'),
    'phys-02': ('Extraordinary claim versus impurity explanation', 'Compare transport and magnetism with impurity and phase-pure controls; remove the LK-99 name to test evidence-based adjudication.'),
    'phys-03': ('Variational representation versus computational advantage', 'Match accuracy and total optimization cost against strong physics solvers; preserve useful representation results without asserting advantage.'),
    'phys-04': ('Nonthermal dynamics versus generic hardware utility', 'Keep the observation/foundations profile; test whether the reviewer asks for discriminating dynamical controls without demanding commercial advantage.'),
    'qc-01': ('Time-dependent sampling advantage', 'Specify classical algorithm, hardware, fidelity and date; pair historical and current comparisons without letting newer work rewrite what was known then.'),
    'qc-02': ('Hardware demonstration versus classical intractability', 'Vary observable and classical simulation budget; preserve the hardware result while testing the utility/intractability extrapolation.'),
    'qc-03': ('Sampling hardness versus verification and approximation', 'Vary loss, distinguishability and approximate classical sampler; score exactly which sampling claim survives.'),
    'qc-04': ('Quantum dynamics versus useful speedup', 'Separate evidence of quantum dynamics from superiority over matched classical simulation/optimization.'),
    'qc-05': ('Tunneling mechanism versus optimization advantage', 'Keep the tunneling observation fixed and alter the classical optimization baseline; the advantage label should change independently.'),
    'qc-06': ('Conditional linear-system speedup and access/output costs', 'Vary condition number, loading and requested output; test whether the theorem remains valid while the application claim fails.'),
    'qc-07': ('Positive foundations control', 'Test the relevant loopholes and statistical assumptions; reject blanket quantum-advantage hardware and business gates for a Bell-test claim.'),
    'qc-08': ('Scaling evidence for error suppression', 'Vary code distance and logical error confidence intervals; preserve the milestone without extrapolating to a useful fault-tolerant machine.'),
    'qc-09': ('Logical operation milestone versus scalable computation', 'Vary postselection and logical-versus-physical accounting; require explicit scope and resource definitions.'),
    'qml-01': ('Engineered data and tiny hardware demonstration', 'Keep classifier accuracy fixed and replace map-native labels with independent data and tuned classical kernels; score the advantage inference separately.'),
    'qml-02': ('Structured QCNN task versus generic learning advantage', 'Vary task structure and classical simulability; require preservation of scoped phase-recognition success.'),
    'qml-03': ('Matched sample-and-query access', 'Anonymize the recommendation paper and Tang follow-up; vary access symmetry. This is a strong conceptual case but an extremely familiar memory test.'),
    'qml-04': ('Quantum state input and restricted PCA output', 'Vary state preparation and whether a classical eigenvector is required; test practical claims separately from conditional complexity.'),
    'qml-05': ('Expressivity versus useful trainable learning', 'Keep universality fixed while changing finite-depth, finite-shot optimization and tuned Fourier comparators.'),
    'qml-06': ('Data-dependent separation versus blanket advantage', 'Vary data access and learning setting; require geometric comparison and retain the stated conditions.'),
    'qml-07': ('Rigorous separation under explicit assumptions', 'Use as a false-exclusion control: preserve the theorem while separately assessing cryptographic assumptions and implementation feasibility.'),
    'qml-08': ('Barren-plateau theorem scope', 'Vary initialization, locality and ansatz depth; blanket claims that all variational circuits fail must be penalized.'),
    'qml-09': ('Measurement efficiency for specified observables', 'Vary observable class, shadow norm and measurement access; preserve supported sample-efficiency results without inferring universal ML advantage.'),
    'qml-10': ('Quantum experimental access versus classical-data learning', 'Switch coherent/quantum access to classical measurement records; require exact access assumptions before accepting or rejecting the separation.'),
}


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8')) if path.exists() else None


def main():
    cards = rr.load_cards()
    rows = []
    for card, comp, arm in rr.matrix(cards):
        d = rr.run_dir(card['id'], comp, arm)
        run = read_json(d / 'run.json') or {}
        answer = read_json(d / 'answer.json')
        grade = read_json(d / 'grade/answer.json')
        parent = read_json(rr.run_dir(card['id'], 'verdict_current', 'lab') / 'answer.json')
        nondelivery = bool(answer and rr.is_nondelivered(answer))
        invalid_parent = bool(comp == 'audit' and (not parent or rr.is_nondelivered(parent)))
        rows.append(dict(card=card['id'], component=comp, arm=arm, answer=answer, grade=grade,
                         error=run.get('error'), nondelivery=nondelivery, invalid_parent=invalid_parent))
    manifest = read_json(rr.OUT / 'manifest.json')
    changed = [f for f,h in manifest['source_sha256'].items()
               if hashlib.sha256((rr.REPO / f).read_bytes()).hexdigest() != h]
    delivered = [r for r in rows if r['answer'] and not r['nondelivery']]
    eligible = [r for r in delivered if r['grade'] and not r['invalid_parent'] and r['component'] != 'probe']
    counts = dict(planned=len(rows), answer_files=sum(bool(r['answer']) for r in rows),
                  delivered=len(delivered), grade_files=sum(bool(r['grade']) for r in rows),
                  research_grades_eligible=len(eligible), changed_sources=changed)
    (rr.OUT / 'analysis_coverage.json').write_text(json.dumps(counts, indent=2), encoding='utf-8')
    lab = ['# Research system analysis — incomplete run, 2026-10-18',
           '\nThe full benchmark is blocked by the configured Claude session quota (reset reported as 21:00 Asia/Hebron on October 18). '
           'This report distinguishes observations from hypotheses. It is not a completed 32-paper performance result.',
           '\n## Coverage and provenance\n', '```json\n'+json.dumps(counts,indent=2)+'\n```',
           'The saved manifest matches current role/method/card hashes. This includes the latest feedback in those files. '
           'It does not prove the prompts execute all changed skills: the runner loads role ESSENCE files and lab_method, not the full stage skills, hardware roadmap or production orchestration.',
           '\n## What the available results support\n',
           'All available component grades belong to qml-03 (Quantum recommendation). This is one familiar dequantization case, not an estimate of performance across papers or domains. '
           'The closed-book probe recalls Tang and the outcome; historical performance therefore cannot establish prospective discovery.',
           'Observed strengths on this case: matched sample-and-query access, sampling rather than full reconstruction, separating correctness of the quantum algorithm from a refuted exponential separation, and retaining a possible polynomial gap.',
           'Observed weaknesses in the grader rationales: unverified recalled exponents; invented operating-point numbers; extra serving/hardware objections; long process framing; incomplete explicit assumptions. These are grader findings requiring human adjudication, not verified factual-error counts.',
           'The current lab verdict is a non-delivery notice. Its zero score and its dependent audit score must be excluded from research-quality aggregates and retained as delivery/recovery failures.',
           '\n| Component | Lab | Direct | Interpretation |\n|---|---:|---:|---|',
           '| Screen | 4 | 5 | One paired case; direct did better |',
           '| Historical verdict | 5 | 5 | Tie, with known later-literature recall |',
           '| Current verdict | delivery failure | 4 | No valid quality comparison |',
           '| Champion / designer / intake / panel / variants | 5 / 4 / 4 / 4 / 4 | untested | No evidence of role benefit over direct prompting |',
           '\n## Priority improvements to the research system\n',
           '1. Enforce claim decomposition: theorem, observed effect, comparative advantage and practical utility need independent labels and scopes.\n'
           '2. Require provenance for decisive numerical claims; mark proposed operating points as proposals and recalled exponents as unverified.\n'
           '3. Apply hardware/business criteria through the claim profile. A formal or foundations result should not fail an irrelevant advantage gate.\n'
           '4. Recover failed outputs before downstream audits, with explicit dependency invalidation.\n'
           '5. Evaluate concise decision usefulness as well as criterion coverage; extra objections can make an otherwise correct result harder to act on.',
           '\n## What cannot yet be concluded\n',
           'No credible all-paper accuracy, false-exclusion rate, domain ranking, component ranking, or benefit from the latest feedback can be calculated. '
           'A feedback-effect claim requires a paired run of the prior policy on the same inputs and model, not merely a current snapshot. '
           'This replay does not validate actual retrieval, experiment execution, reproducibility, checkpoint handling, promotion or full multi-role workflow quality.',
           '\n## Available graded evidence\n']
    for r in eligible:
        lab.append(f"- {r['card']} / {r['component']} / {r['arm']}: {r['grade']['score_0_5']}/5. {r['grade']['rationale']}")
    (rr.OUT / 'system_analysis.md').write_text('\n\n'.join(lab),encoding='utf-8')
    val = ['# Validation system analysis — all 32 case designs',
           '\nThis is a static audit of all 32 cards and the runner, plus observations from the partial run. '
           'Per-paper usefulness below is a design assessment, not an empirical discrimination score. Sources are the local cards and saved run artifacts; their external scientific accuracy was not independently reverified in this audit.',
           '\n## Overall assessment\n',
           'Useful as a development diagnostic for scientific judgment; not yet a reliable certification of the deployed lab. '
           'Its best feature is distinguishing scoped support from overclaim. Its major confounds are hindsight, answer cues, incomplete coverage and uncalibrated model grading.',
           '\n## What works\n',
           '- Claim/adjudicator pairs test whether a reviewer preserves a valid mechanism while rejecting an inflated advantage claim.\n'
           '- Positive formal, foundations and hardware cases can expose indiscriminate rejection.\n'
           '- Direct prompt controls isolate some incremental prompt value.\n'
           '- Historical/current evidence arms and closed-book probes make contamination visible.\n'
           '- Grading records attainable criteria, false alarms, extra useful points and problematic answer keys.\n'
           '- Saved prompts, hashes and dependency artifacts support inspection.',
           '\n## Failures and repairs\n',
           '1. **Hindsight:** historical prompts explicitly allow outside knowledge and name famous papers. A date in a card is not a knowledge boundary. Separate evidence-only scoring from open-knowledge review; add anonymized paired inputs and post-cutoff holdouts.\n'
           '2. **Answer cues:** designer receives curated screen findings; champion receives curated design; variants receives the adjudicated verdict and verdict rubric. These can test applying supplied findings, not discovering them. Report discovery and conditional reasoning separately and add cue-removed ablations.\n'
           '3. **Incomplete baseline controls:** only screen and verdict have direct arms. Designer, champion, panel, intake, audit and variants need matched controls before attributing gains to roles. The lab arm also receives profile guidance absent from direct, confounding role effects with task clarification.\n'
           '4. **Historical grading mismatch:** historical and current verdict use the same reference section. Attainability annotations help, but the overall 0–5 grade is not mechanically adjusted. Use separate frozen keys and explicitly prohibit hindsight penalties.\n'
           '5. **Grader calibration:** a different model within the same family is not independent scientific adjudication. Validate decisive quotes, criterion count/IDs, score boundaries and labels; blind arm identities; measure disagreement with humans and a second judge. No reliability estimate exists here.\n'
           '6. **Delivery versus quality:** interrupted output was scored zero; its downstream audit was scored against an absent verdict. Mark infrastructure failure and dependency-blocked as separate states. Fail fast on quota/auth errors rather than producing hundreds of redundant failures.\n'
           '7. **Reporting denominators:** per-paper summary currently omits papers with no lab grades. Always list all 32, including completed/ungraded, failed and unattempted cells. Report per-component denominators, macro paper averages, uncertainty and worst-case outcomes.\n'
           '8. **Resume validity:** answer-file existence alone triggers skipping; manifest is overwritten on each stage. Reject changed source/prompt/model fingerprints on resume and create a new run for changed policy. Preserve every attempt and its cost.\n'
           '9. **Auditor sensitivity:** auditing only the actual model verdict does not show whether an auditor catches errors. Add blinded correct and deliberately corrupted verdict pairs, measuring detection and false alarms.\n'
           '10. **Coverage:** this is role-only interpretation, with six components for general papers and nine for quantum papers. The seven lab-method rules, production tooling and experiment execution are not all tested. Build an explicit requirement-to-case coverage map.',
           '\n## Next validation experiments, in priority order\n',
           'First repair status accounting and resume guards, then finish candidate → audit → grade stages after quota reset. '
           'Second adjudicate keys and a stratified sample of grades, including all apparent critical failures. '
           'Third run cue-removal, anonymization, matched direct controls and correct/corrupted pairs on a small balanced subset. '
           'Fourth compare old/new feedback versions with identical model/settings, multiple independent replicates and paired uncertainty. '
           'Finally add an unseen holdout and actual execution/retrieval tests. Keep development and qualification results separate.',
           '\n## Paper-by-paper usefulness and coverage\n',
           'All cases are currently unproven as empirical discriminators. qml-03 has pilot grading; every other case lacks completed grading. '
           'The proposed perturbations below are recommendations, not executed tests.']
    for c in cards:
        rs=[r for r in rows if r['card']==c['id']]
        focus, repair=NOTES[c['id']]
        val.extend([f"### {c['id']} — {c['title']}",
                    f"Profile: {c['profile']}. Outputs {sum(bool(r['answer']) for r in rs)}/{len(rs)}; grades {sum(bool(r['grade']) for r in rs)}/{len(rs)}.",
                    f"**Informative target:** {focus}.",
                    '**Card expectation (reference claim, not independently revalidated here):** '+c['expected_verdict'],
                    '**Case-specific evaluation targets from the card:**\n'+c['screen']+'\n\n'+c['audit'],
                    '**Best improvement:** '+repair,
                    '**Interpretation limit:** '+('Pilot shows correct access-model reasoning, but memory recall and input cues prevent a discovery claim; non-delivery invalidates the current-verdict pair.' if c['id']=='qml-03' else 'No graded result yet: usefulness is inferred from the case design. Named historical literature permits memory shortcuts; test the perturbation before calling this case discriminating.')])
    (rr.OUT / 'validation_analysis.md').write_text('\n\n'.join(val),encoding='utf-8')
    print(json.dumps(counts))


if __name__ == '__main__':
    main()
