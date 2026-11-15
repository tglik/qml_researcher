export const meta = {
  name: 'rank-ideas',
  description: 'Rank backlog candidates by a pairwise tournament: Swiss rounds of two-order LLM judgments, Bradley-Terry fit by lab.tools.tournament',
  whenToUse: 'Choosing which candidates to run next; replaying the ranker on closed experiments',
  phases: [
    { title: 'Pair', model: 'haiku' },
    { title: 'Judge' },
    { title: 'Record', model: 'haiku' },
    { title: 'Rank', model: 'haiku' },
  ],
}

// args: { candidates: "<candidates.jsonl>", judgments: "<judgments.jsonl>", rounds?: 3,
//         perRound?: 12, question?: "<what 'better' means>", truth?: "<truth.json for replay>" }
// The candidates file holds {"id","title","summary",...} per line. Judgments are appended, so a
// second run continues the same tournament. No randomness: pairing is Swiss on the current fit.

if (!args || !args.candidates || !args.judgments) {
  throw new Error('args must include candidates and judgments paths')
}
const rounds = args.rounds || 3
const perRound = args.perRound || 12
const QUESTION = args.question ||
  'Which of these two candidates should the lab run first? Prefer the one more likely to give a ' +
  'publishable, honest result (positive or a clean negative) within a few agent-hours: a crisp ' +
  'falsifiable claim, a strong classical baseline that can actually be beaten or ruled out, low ' +
  'dequantization risk, hardware fit, and novelty against prior work. Do not prefer a candidate ' +
  'because it is cheaper unless the two are otherwise equal.'
const T = 'python -m lab.tools.tournament'

const PAIRS = { type: 'object', required: ['pairs'], properties: { pairs: { type: 'array', items: {
  type: 'object', required: ['a', 'b', 'order'],
  properties: { a: { type: 'string' }, b: { type: 'string' }, order: { type: 'string', enum: ['ab', 'ba'] } } } } } }
const CANDS = { type: 'object', required: ['candidates'], properties: { candidates: { type: 'array', items: {
  type: 'object', required: ['id', 'text'], properties: { id: { type: 'string' }, text: { type: 'string' } } } } } }
const VERDICT = { type: 'object', required: ['winner', 'reason'], properties: {
  winner: { type: 'string', enum: ['A', 'B', 'tie'] }, reason: { type: 'string' } } }

phase('Pair')
const loaded = await agent(
  `Read ${args.candidates} (JSONL). Return every candidate as {id, text}, where text is the line's ` +
  `title, summary and any other fields rendered as plain "key: value" lines, copied verbatim.`,
  { schema: CANDS, label: 'load candidates', phase: 'Pair', model: 'haiku', effort: 'low' })
const text = Object.fromEntries(loaded.candidates.map(c => [c.id, c.text]))

let judged = 0
for (let r = 1; r <= rounds; r++) {
  phase('Pair')
  const next = await agent(
    `Run exactly: ${T} pairs ${args.candidates} ${args.judgments} --max ${perRound}\nReturn its JSON output as pairs.`,
    { schema: PAIRS, label: `pairs round ${r}`, phase: 'Pair', model: 'haiku', effort: 'low' })
  if (!next || !next.pairs.length) { log(`round ${r}: no new pairs, stopping`); break }

  phase('Judge')
  // Each judge sees only the two texts, labelled A and B in the order the pairing asked for.
  const verdicts = await parallel(next.pairs.map(p => () => agent(
    `${QUESTION}\n\nCandidate A:\n${text[p.a]}\n\nCandidate B:\n${text[p.b]}\n\n` +
    `Answer with winner A, B or tie, and a two-sentence reason naming the deciding factor. ` +
    `Use only these texts; do not search or read files.`,
    { schema: VERDICT, label: `${p.a} vs ${p.b}`, phase: 'Judge' })))

  phase('Record')
  const rows = next.pairs.map((p, i) => verdicts[i] && {
    ...p, winner: verdicts[i].winner === 'A' ? 'a' : verdicts[i].winner === 'B' ? 'b' : 'tie',
    reason: verdicts[i].reason })
    .filter(Boolean)
  const file = `${args.judgments}.round${r}.json`
  await agent(
    `Write this JSON array, exactly as given, to ${file} with the Write tool:\n${JSON.stringify(rows)}\n` +
    `Then run: ${T} ingest ${args.judgments} ${file} --judge workflow:rank-ideas\nReport its output.`,
    { label: `record round ${r}`, phase: 'Record', model: 'haiku', effort: 'low' })
  judged += rows.length
  log(`round ${r}: ${rows.length} judgments recorded`)
}

phase('Rank')
const table = await agent(
  `Run: ${T} rank ${args.candidates} ${args.judgments}` +
  (args.truth ? `\nThen run: ${T} replay ${args.candidates} ${args.judgments} ${args.truth}` : '') +
  `\nReturn the outputs verbatim.`,
  { label: 'rank', phase: 'Rank', model: 'haiku', effort: 'low' })

return { judged, table }
