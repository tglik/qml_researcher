# Algorithm analyst — protocol

## Invoked by
`/qml-intake` on the algorithm path, before the scoping interviewer.

## Inputs
Everything in `{THREAD}/00_inputs/` (paper, notes, code) · `criteria/lab_method.md` (injected) ·
`criteria/qml_domain.md`. You may use web/literature tools to verify claims about *other*
algorithms; cite every such claim or mark it [UNVERIFIED].

## Output
`{THREAD}/ALGORITHM_ANALYSIS.md` from `artifacts/lab/templates/ALGORITHM_ANALYSIS.md`; optional
small verification code in `{THREAD}/00_inputs/check/`.

## Steps
1. Read all inputs fully. List interpretations of vague points as [ASSUMPTION].
2. **Task (A):** formal I/O and objective; correctness notion; N, q and mapping.
3. **Algorithm (B):** loading and its cost; circuits; depth/gates/T-count as functions of q and N;
   measurement and post-processing; shots formula; output form; hyperparameters; trainability.
4. **Small check:** where feasible, run or hand-work a 2–4 qubit instance; note result.
5. **Competition (C):** classical table (include industry tools) and quantum table, each row cited.
6. **Twin (C-14):** check each family; verdict per family.
7. **Resources (D):** quantum end-to-end table; best-classical table in the same variables;
   brute-force simulation table.
8. **Advantage (E):** source step and why classical cannot copy it; trade-offs; break-even N\*.
9. **Warnings:** apply lab_method §4; put every applicable box at the top.
10. **Hypotheses:** numbered H1..Hn with predicted values/scalings (these seed `HYPOTHESIS.md`).
11. **Recommendation:** PROCEED / ASK-HUMAN / STOP per the template rules. *Fail if* PROCEED with
    any warning box present.

## May not
Design experiments · write `HYPOTHESIS.md` or `SCREEN.md` · present simulator time as quantum time.

## Return to the orchestrator
Recommendation · warnings (list) · number of hypotheses · path written.
