---
schema: primitive_transfer_card
version: 1.0.0
description: |
  Output artifact for /qml-primitive-transfer. Documents a quantum primitive,
  its equivalent NP-hard problem reductions, the classical ML workloads those
  reductions touch, multi-dimensional business value ratings for each workload,
  and startup-oriented next steps.
---

# Primitive Transfer Card Schema

## Frontmatter (required in every card)

```yaml
---
schema: primitive_transfer_card
version: 1.0.0
primitive: <name>              # e.g., "Maximum Independent Set (MIS)"
hardware: <modality>           # e.g., "neutral-atom (Rydberg blockade)"
regime: NISQ | FT | ANALOG     # realistic execution horizon
date: YYYY-MM-DD
source_report: <path or null>  # path to the deep-research / paper-review that surfaced this primitive
slug: <kebab-case-slug>
---
```

---

## Section 1: Primitive Profile

```markdown
## Primitive Profile

**Name:** {primitive name}
**Native combinatorial structure:** {what graph/set/combinatorial object this primitive operates on}
**Hardware modality:** {neutral-atom | trapped-ion | superconducting | photonic | other}
**Regime:** {NISQ | ANALOG | FT}
**Advantage mechanism:** {what makes this primitive non-trivially hard classically — e.g., Rydberg blockade encodes MIS energy landscape natively}
**Key constraint:** {what limits the current primitive — qubit count, coherence time, connectivity, etc.}
**Source:** {paper, review report, or description}
```

---

## Section 2: Equivalent Problem Map

```markdown
## Equivalent Problem Map

For each equivalent problem: the reduction direction, polynomial complexity of the reduction,
and the canonical classical domain where this problem appears.

| Problem | Reduction from primitive | Reduction type | Example domain |
|---------|--------------------------|----------------|----------------|
| {name} | {how MIS/etc. reduces to this} | poly-time / quasi-poly | {domain} |
| ... | | | |

### Reduction notes
{Any non-trivial caveats about the reductions — e.g., which direction is tight, where overhead is significant}
```

---

## Section 3: ML Workload Map

```markdown
## ML Workload Map

For each ML workload: how it connects to the equivalent problem map, the current
classical bottleneck, and the QML fit rationale.

| ML Workload | Domain | Connects via | Classical bottleneck | QML fit rationale |
|-------------|--------|--------------|---------------------|-------------------|
| {name} | {domain} | {equivalent problem} | {bottleneck} | {why quantum primitive helps} |
| ... | | | | |

### Workload notes
{Any cross-workload patterns or groupings worth noting}
```

---

## Section 4: Business Value Ratings

Each workload is rated on four value dimensions, each scored 0–3:

| Score | Meaning |
|-------|---------|
| 3 | Strong positive: this dimension is a primary driver of value |
| 2 | Moderate: meaningful contribution, not the main driver |
| 1 | Weak: possible upside but uncertain or small |
| 0 | Not applicable or negligible |

**Dimensions:**

- **Speedup × Event Value** (`sv`): acceleration magnitude × business value of one solved instance (e.g., drug discovery = few events, massive value per hit)
- **Volume Leverage** (`vl`): low per-event speedup but high transaction frequency → aggregate value (e.g., ad placement optimization at scale)
- **Data Efficiency** (`de`): quantum approach reduces the labeled-data requirement → cheaper training or earlier deployment
- **Resource Efficiency** (`re`): energy or compute reduction meaningful at the deployment scale

```markdown
## Business Value Ratings

| ML Workload | sv | vl | de | re | Aggregate | Notes |
|-------------|----|----|----|----|-----------|-------|
| {name} | {0-3} | {0-3} | {0-3} | {0-3} | HIGH/MED/LOW | {one-line rationale} |
| ... | | | | | | |

**Aggregate rule:** HIGH = sv+vl ≥ 4 OR any dimension = 3 + one other ≥ 2. MED = at least two dimensions ≥ 2. LOW = otherwise.

### Rating notes
{Any cross-workload patterns, notable outliers, or dimension-specific caveats}
```

---

## Section 5: Top Opportunities (ranked)

```markdown
## Top Opportunities

Ranked by aggregate business potential. HIGH opportunities listed first.

### 1. {ML Workload Name} — {Aggregate}

**Why it matters:** {2–3 sentences. What problem it solves, who pays for it, why quantum is defensible here.}
**Quantum wedge:** {what specifically the primitive provides that classical cannot easily replicate}
**Nearest classical ceiling:** {what classical method currently dominates and where it breaks down}
**Startup positioning:** {how this maps to the team's current hardware partner angle, domain expertise, or IP}
**Risk:** {the single biggest risk — dequantization, hardware scale, market timing, etc.}

---

### 2. {ML Workload Name} — {Aggregate}
...
```

---

## Section 6: Startup Alignment & Next Steps

```markdown
## Startup Alignment

{2–4 sentences on which opportunities best fit the startup's current positioning:
hardware partner (Q-Factor / neutral-atom), team expertise (classical ML background),
and timeline (NISQ near-term vs FT long-term).}

## Suggested Next Steps

| Action | Type | Priority | Owner |
|--------|------|----------|-------|
| {action} | experiment / partnership / IP / literature | HIGH/MED/LOW | Tsahi/Adi/Meir |
| ... | | | |
```

---

## Links section (required at end of every card)

```markdown
## Workspace

| Artifact | Link |
|----------|------|
| Primitive profile | [[00_primitive.md]] |
| Equivalent problems | [[01_equivalent_problems.md]] |
| ML workload map | [[02_ml_workloads.md]] |
| Business ratings | [[03_business_ratings.md]] |
| Transfer card (Markdown) | [[04_transfer_card.md]] |
| Transfer card (Word) | [[04_transfer_card.docx]] |
```
