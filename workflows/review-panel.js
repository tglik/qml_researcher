export const meta = {
  name: 'review-panel',
  description: 'QML Lab review panel as a workflow: six persona agents in parallel, verdict computed by the script, one merge agent that may not soften issues',
  phases: [
    { title: 'Six parallel reviews' },
    { title: 'Merge' },
  ],
}

// args: { thread: "<path to the program thread>", pass: 1 | 2, agentPrefix?: "qml-researcher:" }
// Invoke: /qml-researcher:review-panel with args {thread, pass}. Run setup checks first
// (see .agents/skills/qml-review-panel/SKILL.md, "Setup"); a workflow cannot ask mid-run.
//
// Why a workflow and not only the skill: the six reviews fan out from code, every persona returns
// its issues as schema-checked JSON, and the panel verdict and blocking count are computed here,
// so the merge agent cannot drop or soften a BLOCKING issue. The skill stays the fallback for
// Hermes/Codex and for runtimes without workflows.

if (!args || !args.thread || ![1, 2, '1', '2'].includes(args.pass)) {
  throw new Error('args must be {thread: "<thread path>", pass: 1 | 2}')
}
const thread = args.thread
const pass = Number(args.pass)
const prefix = args.agentPrefix === undefined ? 'qml-researcher:' : args.agentPrefix

const PERSONAS = [
  'methodologist', 'dequantization-theorist', 'hardware-realist',
  'baseline-champion', 'value-translator', 'mathematical-critic',
]

const ISSUES = {
  type: 'object',
  required: ['issues'],
  properties: {
    issues: {
      type: 'array',
      items: {
        type: 'object',
        required: ['severity', 'anchor', 'file', 'problem', 'fix'],
        properties: {
          severity: { type: 'string', enum: ['BLOCKING', 'NON-BLOCKING'] },
          anchor: { type: 'string', description: 'verbatim quote from the file' },
          file: { type: 'string' },
          problem: { type: 'string' },
          fix: { type: 'string' },
        },
      },
    },
    checklist_md: { type: 'string', description: 'methodologist only: the checklist (pass 1) or drift check (pass 2) as markdown' },
  },
}

phase('Six parallel reviews')
const reviews = await parallel(PERSONAS.map(p => () => agent(
  `Review ${thread}, pass ${pass}, as the ${p} persona. Inputs per your PROTOCOL for this pass.` +
  (p === 'hardware-realist' ? ' Also read criteria/hardware_roadmaps.md.' : '') +
  ` Write your issues to ${thread}/panel/${pass}/${p}.md (or "No issues in <lane>."). ` +
  `Do not read other personas' files. Return the same issues as data; an empty list means no issues.` +
  (p === 'methodologist' ? ' Return the checklist (pass 1) or drift check (pass 2) in checklist_md.' : ''),
  { agentType: `${prefix}panel-${p}`, schema: ISSUES, label: p, phase: 'Six parallel reviews' },
)))

const missing = PERSONAS.filter((p, i) => !reviews[i])
const rows = []
PERSONAS.forEach((p, i) => (reviews[i]?.issues || []).forEach(x => rows.push({ persona: p, ...x })))
rows.sort((a, b) => (a.severity === 'BLOCKING' ? 0 : 1) - (b.severity === 'BLOCKING' ? 0 : 1))
const blocking = rows.filter(r => r.severity === 'BLOCKING').length
// A persona that failed to report is not "no issues": the panel cannot approve without it.
const verdict = missing.length || blocking ? 'BLOCKED' : rows.length ? 'APPROVED-WITH-CHANGES' : 'APPROVED'
log(`panel pass ${pass}: ${verdict}, blocking ${blocking}, non-blocking ${rows.length - blocking}` +
    (missing.length ? `, missing ${missing.join(', ')}` : ''))

phase('Merge')
const methodologist = reviews[0]?.checklist_md || '(methodologist did not return a checklist)'
const merged = await agent(
  `Write ${thread}/PANEL_${pass}.md from artifacts/lab/templates/PANEL.md. Frontmatter: thread, pass ${pass}, ` +
  `today's date, verdict ${verdict}, blocking ${blocking}. The Issues table has exactly these ${rows.length} rows, ` +
  `in this order, numbered from 1, text copied verbatim (do not edit, merge, soften, re-grade or drop any):\n` +
  JSON.stringify(rows, null, 1) +
  `\nCopy this methodologist section in verbatim:\n${methodologist}\n` +
  (missing.length ? `Add a line under Issues: "Missing persona reports: ${missing.join(', ')} — panel BLOCKED until rerun."\n` : '') +
  `Then run: python -m lab.tools.validate artifact ${thread}/PANEL_${pass}.md and append one line to ` +
  `${thread}/decision_log.md: "panel pass ${pass}: ${verdict}, blocking ${blocking}". Return the validate output.`,
  { label: 'merge', phase: 'Merge', effort: 'low' },
)

return {
  thread, pass, verdict, blocking, non_blocking: rows.length - blocking, missing,
  by_persona: Object.fromEntries(PERSONAS.map((p, i) => [p, reviews[i] ? reviews[i].issues.length : null])),
  path: `${thread}/PANEL_${pass}.md`, validate: merged,
}
