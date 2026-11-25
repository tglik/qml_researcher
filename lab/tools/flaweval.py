"""Planted-flaw eval for the screen (C10 eval 5, generated at scale).

Why: the screen and the ingest triage decide which ideas get compute, and nothing measured how
well they catch a known failure. Hand-written known answers do not scale (4 of 14 replay fixtures
exist). Following arXiv:2604.18936 (Woodward et al., MLST 2026), a model writes the test items and a
script checks them: every item carries a machine-readable spec of its quantum core, and a
deterministic checker proves from the spec whether the planted flaw is there. No model grades
whether a flaw exists; models only write prose and screen it.

Each item comes as a pair that differs only in the planted flaw:
- flawed: the spec has the flaw (the checker must say so), the claim text states its facts.
- twin:   one edit removes the flaw (the checker must say it is absent), same style and confidence.
Catching a flawed item is half the job; killing its twin as well means the screen reacts to the
topic, not the flaw. The headline number is discrimination = P(killed | flawed) - P(killed | twin); a narrowed twin
is not a kill (it goes on with a smaller claim).

Flaw types (the gate the lab method charges them to):
- clifford_only        G3  the whole circuit is Clifford: Gottesman-Knill simulates it classically.
                           Checked on the full unitary: every X_i and Z_i must conjugate to a Pauli.
- product_state_kernel G3  the feature map never entangles: the fidelity kernel is a product of
                           one-qubit kernels, O(n) classically. Checked by simulating the state on
                           random inputs and testing every one-qubit marginal for purity.
- full_readout         G1  the answer is a whole N-vector: reading it out costs at least the
                           tomography bound, which is not below the classical cost.
- data_loading         G1  arbitrary classical data are loaded into amplitudes: the load alone
                           costs N*d per load, not below the classical cost.
- dequantizable_lowrank G3 low-rank input with sample-and-query access and a sample as output:
                           the conditions of Tang 2019 / Chia et al. 2020 for a classical
                           polylog(N) sampler hold.

What it does not measure: whether the screen spots a real advantage. Planted flaws test known
failure types only; outcomes of closed experiments are still needed for the other half.

    python -m lab.tools.flaweval check   [--items F] [--prune]
        # re-run every checker, faithfulness and leak test; exit 1 on any failure (no model);
        # --prune drops the failing pairs (after a checker gets stricter)
    python -m lab.tools.flaweval generate --seat S [--panel P] [--flaws a,b] [--bases c-…,c-…]
                                         [--n N] [--items F]
        # a model writes N pairs per flaw from real backlog candidates; only pairs whose checker,
        # faithfulness and leak tests all pass are appended to --items, the rest are logged
    python -m lab.tools.flaweval prompt  <item-id> [--ledger PATH]
        # the exact screen prompt for one item
    python -m lab.tools.flaweval run     --seat S [--panel P] [--runs R] [--only ids] [--ledger PATH]
                                         [--workers W] [--items F] [--out DIR]
        # screen every item R times with one seat; resumable (item, seat, run, prompt) quadruples
    python -m lab.tools.flaweval report  [--items F] [--out DIR] [--json]

Default --items: tests/fixtures/lab/eval5/items.jsonl (committed, so items are reviewed in PRs).
Default --out: {OUTPUT_ROOT}/indexes/evals/planted_flaws/.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import hashlib
import json
import math
import random
import re
import sys
from pathlib import Path

import numpy as np

from . import panel as P
from .common import LabError, REPO, main_wrapper, now, output_root

ITEMS = REPO / "tests" / "fixtures" / "lab" / "eval5" / "items.jsonl"
PROMPT_VERSION = "flaweval-screen-v1"
GEN_VERSION = "flaweval-gen-v1"
MAX_QUBITS = 10
TOL = 1e-9
KILL = ("killed", "narrowed")
# Items must pass the gates their flaw does not decide. A classical cost under this is a few hours on
# cluster, and the screen rightly kills it at G2 (rule 4) whatever the flaw. The 2026-11-25 pilot killed
# every twin at 5e7-2e10 operations, and still most at 1e15 ("about 1 s on a petaflop node"). 1e20 is
# about a day on an exaflop machine.
MIN_CLASSICAL_OPS = 1e20
GENERIC_FORBID = ("planted", "flaw", "twin", "known answer", "this is a test")


class SpecError(LabError):
    pass


# --- gates and simulation --------------------------------------------------------------------------
_I2 = np.eye(2, dtype=complex)
_X = np.array([[0, 1], [1, 0]], dtype=complex)
_Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
_Z = np.array([[1, 0], [0, -1]], dtype=complex)
_H = np.array([[1, 1], [1, -1]], dtype=complex) / math.sqrt(2)
FIXED1 = {"h": _H, "x": _X, "y": _Y, "z": _Z, "id": _I2,
          "s": np.diag([1, 1j]), "sdg": np.diag([1, -1j]),
          "t": np.diag([1, np.exp(1j * math.pi / 4)]), "tdg": np.diag([1, np.exp(-1j * math.pi / 4)]),
          "sx": np.array([[1 + 1j, 1 - 1j], [1 - 1j, 1 + 1j]], dtype=complex) / 2}
ROT1 = {"rx": _X, "ry": _Y, "rz": _Z}
_CX = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]], dtype=complex)
FIXED2 = {"cx": _CX, "cnot": _CX, "cz": np.diag([1, 1, 1, -1]).astype(complex),
          "swap": np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 1]], dtype=complex)}
ROT2 = {"rzz": np.kron(_Z, _Z), "rxx": np.kron(_X, _X), "ryy": np.kron(_Y, _Y)}
GATE_NAMES = sorted({*FIXED1, *ROT1, *FIXED2, *ROT2})


def gate_matrix(g: dict, x: np.ndarray | None = None) -> tuple[np.ndarray, list[int]]:
    """A gate dict -> (matrix, qubits). Rotations take `angle`, or `feature` + `scale` (angle =
    scale * x[feature]); rotation convention exp(-i angle P / 2)."""
    name = str(g.get("name", "")).lower()
    qubits = g.get("qubits")
    if qubits is None and "qubit" in g:
        qubits = [g["qubit"]]
    if not isinstance(qubits, list) or not all(isinstance(q, int) for q in qubits):
        raise SpecError(f"gate {g}: qubits must be a list of integers")
    if name in FIXED1 or name in FIXED2:
        m = FIXED1.get(name, FIXED2.get(name))
    elif name in ROT1 or name in ROT2:
        if "angle" in g:
            theta = float(g["angle"])
        elif "feature" in g:
            if x is None:
                raise SpecError(f"gate {g} reads a feature but no input was given")
            theta = float(g.get("scale", 1.0)) * float(x[int(g["feature"])])
        else:
            raise SpecError(f"rotation {g} needs angle or feature")
        p = ROT1.get(name, ROT2.get(name))
        m = math.cos(theta / 2) * np.eye(p.shape[0]) - 1j * math.sin(theta / 2) * p
    else:
        raise SpecError(f"unknown gate {name!r}; known: {', '.join(GATE_NAMES)}")
    if m.shape[0] != 2 ** len(qubits) or len(set(qubits)) != len(qubits):
        raise SpecError(f"gate {g}: wrong number of qubits")
    return m, qubits


def apply(state: np.ndarray, m: np.ndarray, qubits: list[int], n: int) -> np.ndarray:
    """Apply m to `qubits` of a state (2**n,) or a matrix (2**n, k) whose columns are states.
    Qubit 0 is the most significant bit."""
    k = len(qubits)
    cols = state.shape[1:] if state.ndim > 1 else ()
    t = state.reshape((2,) * n + cols)
    t = np.moveaxis(t, qubits, list(range(k)))
    shp = t.shape
    t = (m @ t.reshape(2 ** k, -1)).reshape(shp)
    t = np.moveaxis(t, list(range(k)), qubits)
    return t.reshape(state.shape)


def _circuit(spec: dict) -> tuple[int, list[dict]]:
    n = spec.get("n_qubits")
    gates = spec.get("gates")
    if not isinstance(n, int) or not 1 <= n <= MAX_QUBITS:
        raise SpecError(f"n_qubits must be an integer 1..{MAX_QUBITS}")
    if not isinstance(gates, list) or not gates:
        raise SpecError("gates must be a non-empty list")
    for g in gates:
        q = g.get("qubits", [g.get("qubit")])
        if any(not isinstance(i, int) or not 0 <= i < n for i in q):
            raise SpecError(f"gate {g} acts outside 0..{n - 1}")
    return n, gates


def unitary(spec: dict, x: np.ndarray | None = None) -> np.ndarray:
    n, gates = _circuit(spec)
    u = np.eye(2 ** n, dtype=complex)
    for g in gates:
        m, q = gate_matrix(g, x)
        u = apply(u, m, q, n)
    return u


def statevector(spec: dict, x: np.ndarray | None = None) -> np.ndarray:
    n, gates = _circuit(spec)
    s = np.zeros(2 ** n, dtype=complex)
    s[0] = 1
    for g in gates:
        m, q = gate_matrix(g, x)
        s = apply(s, m, q, n)
    return s


# --- circuit families: a layer template instantiated at any width --------------------------------
# A claim is about a family at scale (e.g. 100 qubits); the checker instantiates the same template at
# small widths it can simulate exactly. Each layer is a local gate pattern, so whether the family is
# Clifford, or whether it entangles, is the same at every width >= 4 (checked at several widths).
ON = ("all", "chain", "ring", "even_pairs", "odd_pairs", "all_pairs", "first", "last")
PAIR_ON = ("chain", "ring", "even_pairs", "odd_pairs", "all_pairs")
CHECK_WIDTHS = (4, 6, 8)
MAX_CLAIM_QUBITS = 100000


def _targets(on: str, m: int) -> list[list[int]]:
    return {"all": [[q] for q in range(m)], "first": [[0]], "last": [[m - 1]],
            "chain": [[q, q + 1] for q in range(m - 1)],
            "ring": [[q, (q + 1) % m] for q in range(m)],
            "even_pairs": [[q, q + 1] for q in range(0, m - 1, 2)],
            "odd_pairs": [[q, q + 1] for q in range(1, m - 1, 2)],
            "all_pairs": [[a, b] for a in range(m) for b in range(a + 1, m)]}[on]


def family(spec: dict) -> tuple[int, list[dict]]:
    n = spec.get("n_qubits")
    layers = spec.get("layers")
    if isinstance(n, bool) or not isinstance(n, int) or not 4 <= n <= MAX_CLAIM_QUBITS:
        raise SpecError(f"n_qubits (the claimed width) must be an integer 4..{MAX_CLAIM_QUBITS}")
    if not isinstance(layers, list) or not layers:
        raise SpecError("layers must be a non-empty list")
    for lay in layers:
        name = str(lay.get("name", "")).lower()
        if name not in GATE_NAMES:
            raise SpecError(f"unknown gate {name!r}; known: {', '.join(GATE_NAMES)}")
        if lay.get("on") not in ON:
            raise SpecError(f"layer {lay}: on must be one of {', '.join(ON)}")
        two = name in FIXED2 or name in ROT2
        if two != (lay["on"] in PAIR_ON):
            raise SpecError(f"layer {lay}: a {'two' if two else 'one'}-qubit gate cannot act on {lay['on']}")
        if lay.get("feature") not in (None, "qubit"):
            raise SpecError(f"layer {lay}: feature must be 'qubit' (feature i drives qubit i)")
        if lay.get("feature") == "qubit" and two:
            raise SpecError(f"layer {lay}: feature-driven layers must be one-qubit rotations")
    return n, layers


def instantiate(spec: dict, m: int) -> dict:
    """The family at width m as a plain circuit {"n_qubits", "n_features", "gates"}."""
    _, layers = family(spec)
    gates = []
    for lay in layers:
        for qs in _targets(lay["on"], m):
            g = {"name": lay["name"], "qubits": qs}
            if lay.get("feature") == "qubit":
                g.update(feature=qs[0], scale=float(lay.get("scale", 1.0)))
            elif "angle" in lay:
                g["angle"] = lay["angle"]
            gates.append(g)
    return {"n_qubits": m, "n_features": m, "gates": gates}


def is_pauli(m: np.ndarray, tol: float = 1e-7) -> bool:
    """True if m = phase * X^a Z^b for bit strings a, b and |phase| = 1."""
    d = m.shape[0]
    cols = np.argmax(np.abs(m), axis=1)
    rows = np.arange(d)
    vals = m[rows, cols]
    if not np.allclose(np.abs(vals), 1, atol=tol):
        return False
    if np.abs(m).sum() - np.abs(vals).sum() > tol * d:
        return False
    a = int(cols[0])
    if not all(int(cols[j]) == (j ^ a) for j in range(d)):
        return False
    r = vals / vals[0]
    b = 0
    for k in range(int(math.log2(d))):
        j = 1 << k
        if abs(r[j] + 1) < 1e-6:
            b |= j
        elif abs(r[j] - 1) > 1e-6:
            return False
    sign = np.array([(-1) ** bin(b & j).count("1") for j in range(d)])
    return bool(np.allclose(r, sign, atol=1e-6))


def pauli_on(n: int, i: int, p: np.ndarray) -> np.ndarray:
    m = np.array([[1]], dtype=complex)
    for k in range(n):
        m = np.kron(m, p if k == i else _I2)
    return m


def single_qubit_purities(state: np.ndarray, n: int) -> list[float]:
    out = []
    t = state.reshape((2,) * n)
    for i in range(n):
        a = np.moveaxis(t, i, 0).reshape(2, -1)
        rho = a @ a.conj().T
        out.append(float(np.real(np.trace(rho @ rho))))
    return out


# --- checkers: spec -> (has_flaw, evidence) --------------------------------------------------------
def _num(spec: dict, key: str, lo: float = 0, integer: bool = False) -> float:
    v = spec.get(key)
    if isinstance(v, bool) or not isinstance(v, (int, float)) or not v > lo:
        raise SpecError(f"{key} must be a number > {lo}")
    if integer and v != int(v):
        raise SpecError(f"{key} must be an integer")
    return float(v)


def _choice(spec: dict, key: str, options: tuple[str, ...]) -> str:
    v = spec.get(key)
    if v not in options:
        raise SpecError(f"{key} must be one of {', '.join(options)}")
    return v


DIAGONAL = {"z", "s", "sdg", "t", "tdg", "rz", "cz", "rzz", "id"}


def _qs(g: dict) -> list[int]:
    return g["qubits"] if "qubits" in g else [g["qubit"]]


def effective_gates(gates: list[dict]) -> list[dict]:
    """Drop gates that cannot change the measured distribution: diagonal gates on qubits still in
    |0> (only a phase) and diagonal gates followed by nothing but diagonal gates on their qubits
    (they commute to the computational-basis measurement). Repeated to a fixed point."""
    gates = list(gates)
    while True:
        drop = set()
        fresh: set[int] = set(q for g in gates for q in _qs(g))      # qubits still in |0>
        for i, g in enumerate(gates):
            name = str(g.get("name", "")).lower()
            if name in DIAGONAL and all(q in fresh for q in _qs(g)):
                drop.add(i)
            elif name not in DIAGONAL:
                fresh -= set(_qs(g))
        for i, g in enumerate(gates):
            name = str(g.get("name", "")).lower()
            later = [h for h in gates[i + 1:] if set(_qs(h)) & set(_qs(g))]
            if name in DIAGONAL and all(str(h.get("name", "")).lower() in DIAGONAL for h in later):
                drop.add(i)
        if not drop:
            return gates
        gates = [g for i, g in enumerate(gates) if i not in drop]


def clifford_circuit(spec: dict) -> tuple[bool, str]:
    n, gates = _circuit(spec)
    if any("feature" in g for g in gates):
        raise SpecError("clifford_only circuits take fixed angles, not features")
    eff = effective_gates(gates)
    if not eff:
        return True, "trivial: no gate changes the measured distribution"
    u = unitary({"n_qubits": n, "gates": eff})
    for i in range(n):
        for name, p in (("X", _X), ("Z", _Z)):
            if not is_pauli(u @ pauli_on(n, i, p) @ u.conj().T):
                return False, (f"not Clifford: U {name}_{i} U^dagger is not a Pauli string "
                               f"({n} qubits, {len(eff)} of {len(gates)} gates affect the output)")
    return True, (f"Clifford: all {2 * n} generators X_i, Z_i conjugate to Pauli strings under the "
                  f"{len(eff)} gates that affect the output ({len(gates)} in all, {n} qubits), so "
                  "Gottesman-Knill simulates it in poly(n)")


def product_kernel_circuit(spec: dict, samples: int = 5, seed: int = 0) -> tuple[bool, str]:
    n, gates = _circuit(spec)
    d = spec.get("n_features")
    if not isinstance(d, int) or d < 1:
        raise SpecError("n_features must be a positive integer")
    used = {int(g["feature"]) for g in gates if "feature" in g}
    if not used:
        raise SpecError("a feature map must read at least one feature")
    if max(used) >= d:
        raise SpecError(f"a gate reads feature {max(used)} but n_features is {d}")
    # a fixed unitary after the last data-dependent gate cancels in |<psi(x)|psi(x')>|^2: drop it
    last = max(i for i, g in enumerate(gates) if "feature" in g)
    core = {"n_qubits": n, "gates": gates[:last + 1]}
    rng = np.random.default_rng(seed)
    worst = 1.0
    for _ in range(samples):
        x = rng.uniform(0, 2 * math.pi, d)
        worst = min(worst, *single_qubit_purities(statevector(core, x), n))
    if worst > 1 - 1e-9:
        return True, (f"product state: every one-qubit marginal is pure on {samples} random inputs "
                      f"(min purity {worst:.12f}), so k(x,x') factorizes into {n} one-qubit kernels, "
                      f"O(n) classically")
    return False, f"entangled: min one-qubit purity {worst:.6f} on {samples} random inputs"

def _over_widths(spec: dict, fn, what: str) -> tuple[bool, str]:
    n, _ = family(spec)
    results = [(m, *fn(instantiate(spec, m))) for m in CHECK_WIDTHS if m <= n]
    verdicts = {r[1] for r in results}
    if len(verdicts) != 1:
        raise SpecError(f"{what} differs across widths {[(m, v) for m, v, _ in results]}: not a uniform family")
    m, v, ev = results[-1]
    widths = ", ".join(str(r[0]) for r in results)
    return v, f"family claimed at {n} qubits, checked at widths {widths}; at {m}: {ev}"


def middle_cut_rank(state: np.ndarray, n: int) -> int:
    sv = np.linalg.svd(state.reshape(2 ** (n // 2), -1), compute_uv=False)
    return int((sv > 1e-9).sum())


def check_not_easy(spec: dict, samples: int = 3, seed: int = 1) -> tuple[bool, str]:
    """Twins must not be classically easy for another reason. Necessary, not sufficient: the
    middle-cut Schmidt rank must be the maximum 2^(m/2) at every check width, so no constant-bond
    MPS (1D shallow circuits, CX chains on |+>, a single CZ chain) simulates the family. Kernels are
    checked on the data-dependent part only, on random inputs."""
    n, layers = family(spec)
    rng = np.random.default_rng(seed)
    for m in CHECK_WIDTHS:
        if m > n:
            continue
        inst = instantiate(spec, m)
        gates = inst["gates"]
        if any("feature" in g for g in gates):
            last = max(i for i, g in enumerate(gates) if "feature" in g)
            inst = {**inst, "gates": gates[:last + 1]}
            states = [statevector(inst, rng.uniform(0, 2 * math.pi, m)) for _ in range(samples)]
        else:
            inst = {**inst, "gates": effective_gates(gates)}
            if not inst["gates"]:
                return False, "no gate changes the output"
            states = [statevector(inst)]
        r = min(middle_cut_rank(st, m) for st in states)
        if r < 2 ** (m // 2):
            return False, (f"easy: middle-cut Schmidt rank {r} < {2 ** (m // 2)} at width {m}, so a "
                           "low-bond MPS simulates it")
    return True, f"middle-cut Schmidt rank is maximal at widths {', '.join(map(str, CHECK_WIDTHS))}"


def check_clifford(spec: dict) -> tuple[bool, str]:
    if any(lay.get("feature") for lay in family(spec)[1]):
        raise SpecError("clifford_only circuits take fixed angles, not features")
    return _over_widths(spec, clifford_circuit, "Clifford-ness")


def check_product_kernel(spec: dict) -> tuple[bool, str]:
    return _over_widths(spec, product_kernel_circuit, "entanglement")



READOUTS = ("all_amplitudes", "all_probabilities", "scalar")


def readout_bound(spec: dict) -> float:
    n = _num(spec, "N", 1, integer=True)
    eps = _num(spec, "eps")
    if eps >= 1:
        raise SpecError("eps must be below 1")
    kind = _choice(spec, "readout", READOUTS)
    # pure-state tomography needs Theta(N / eps^2) copies (Haah et al. 2017, arXiv:1508.01797);
    # an N-outcome distribution to l_inf error eps needs O(log N / eps^2) samples; a scalar 1/eps^2.
    return {"all_amplitudes": n / eps ** 2, "all_probabilities": max(1.0, math.log2(n)) / eps ** 2,
            "scalar": 1 / eps ** 2}[kind]


def _classical(spec: dict) -> float:
    c = _num(spec, "classical_cost_ops")
    if c < MIN_CLASSICAL_OPS:
        raise SpecError(f"classical_cost_ops {c:.3g} is not a bottleneck (needs >= {MIN_CLASSICAL_OPS:.0e}); "
                        "the screen would kill both items at G2")
    return c


def check_readout(spec: dict) -> tuple[bool, str]:
    lower = readout_bound(spec)
    classical = _classical(spec)
    verdict = lower >= classical
    return verdict, (f"readout '{spec['readout']}' at N={int(spec['N'])}, eps={spec['eps']} needs at least "
                     f"{lower:.3g} repetitions vs classical {classical:.3g} ops: "
                     + ("readout alone is not below the classical cost" if verdict else "readout is cheaper"))


ACCESS = ("arbitrary_classical", "qram_assumed", "efficient_formula")


def check_loading(spec: dict) -> tuple[bool, str]:
    n = _num(spec, "N_rows", 0, integer=True)
    d = _num(spec, "d", 0, integer=True)
    loads = _num(spec, "loads", 0, integer=True)
    classical = _classical(spec)
    access = _choice(spec, "access", ACCESS)
    # an arbitrary state of N*d amplitudes needs Omega(N*d) gates (parameter counting); QRAM must be
    # built once at the same cost; a state given by an efficient formula costs polylog per load.
    lower = {"arbitrary_classical": n * d * loads, "qram_assumed": n * d,
             "efficient_formula": loads * math.log2(n * d + 1) ** 2}[access]
    verdict = lower >= classical
    return verdict, (f"loading '{access}' of {int(n)}x{int(d)} data, {int(loads)} loads, costs at least "
                     f"{lower:.3g} vs classical {classical:.3g} ops: "
                     + ("loading alone is not below the classical cost" if verdict else "loading is cheaper"))


DEQ_ACCESS = ("sample_query", "sparse_oracle", "circuit_block_encoding")
DEQ_OUTPUT = ("sample", "scalar", "full_vector")


def check_dequantizable(spec: dict) -> tuple[bool, str]:
    n = _num(spec, "N", 1, integer=True)
    k = _num(spec, "rank", 0, integer=True)
    kappa = _num(spec, "condition_number")
    eps = _num(spec, "eps")
    access = _choice(spec, "access", DEQ_ACCESS)
    output = _choice(spec, "output", DEQ_OUTPUT)
    if n < 1e9:
        raise SpecError("N must be at least 1e9, or a dense classical solve is cheap and both items die at G2")
    low_rank = k <= math.log2(n) ** 2
    conds = {"sample-and-query access": access == "sample_query",
             f"rank {int(k)} <= log2(N)^2 = {math.log2(n) ** 2:.0f}": low_rank,
             "output is a sample or a scalar": output in ("sample", "scalar")}
    if all(conds.values()):
        return True, ("dequantizable: " + "; ".join(conds) + f". A classical sampler runs in "
                      f"poly(k={int(k)}, kappa={kappa:g}, 1/eps={1 / eps:g}) * polylog(N) "
                      "(Tang 2019, arXiv:1807.04271; Chia et al. 2020, arXiv:1910.06151)")
    failed = [c for c, ok in conds.items() if not ok]
    return False, "dequantization theorem does not apply: fails " + "; ".join(failed)


FLAWS = {
    "clifford_only": {
        "gate": "G3", "check": check_clifford,
        "about": ("The proposed quantum circuit uses only Clifford gates (H, S, CNOT, CZ, Paulis, "
                  "rotations by multiples of pi/2) on a computational-basis input, so it is "
                  "classically simulable by Gottesman-Knill."),
        "twin": "Replace one gate layer with a non-Clifford one (T, or a rotation by an angle that is not a "
                "multiple of pi/2) so the circuit is no longer Clifford. Make both circuits entangle strongly "
                "(several entangling layers separated by non-commuting one-qubit layers, all_pairs where it "
                "fits): a CX chain on |+> does nothing, and one chain layer is a low-bond MPS.",
        "spec_help": ('{"n_qubits": 64, "layers": [{"name": "h", "on": "all"}, {"name": "cx", "on": "chain"}, '
                      '{"name": "rz", "on": "all", "angle": 1.5707963267948966}, {"name": "cz", "on": "odd_pairs"}]}  '
                      "(a circuit family: n_qubits is the width the claim is about, 4 or more; each layer applies "
                      f"one gate on: {', '.join(ON)}; gate names: {', '.join(GATE_NAMES)}; rotations "
                      "exp(-i angle P/2); input |0...0>, measured in the computational basis)"),
        "keywords": ("clifford", "stabilizer", "gottesman", "knill", "efficiently simulable", "classically simulable"),
        "forbid": ("clifford", "stabilizer", "gottesman", "knill", "simulable", "simulatable"),
    },
    "product_state_kernel": {
        "gate": "G3", "check": check_product_kernel,
        "about": ("The quantum kernel's feature map never creates entanglement, so the encoded state is "
                  "a product state and the fidelity kernel is a product of one-qubit kernels, "
                  "computable classically in O(n)."),
        "twin": "Add entangling layers between data-encoding layers (several, separated by non-commuting "
                "encoding layers; all_pairs where it fits) so the encoded state is strongly entangled; a single "
                "chain layer is a low-bond MPS and still easy.",
        "spec_help": ('{"n_qubits": 50, "layers": [{"name": "h", "on": "all"}, {"name": "ry", "on": "all", '
                      '"feature": "qubit", "scale": 1.0}, {"name": "cz", "on": "chain"}, {"name": "rz", "on": "all", '
                      '"feature": "qubit", "scale": 0.5}]}  '
                      "(a feature-map family on n_qubits >= 4 qubits with one feature per qubit; fidelity kernel "
                      "k(x,x') = |<psi(x)|psi(x')>|^2 of the state prepared from |0...0>; a layer with "
                      "feature 'qubit' rotates qubit i by scale * x_i; each layer applies one gate on: "
                      f"{', '.join(ON)}; gate names: {', '.join(GATE_NAMES)})"),
        "keywords": ("product state", "unentangled", "no entanglement", "separable", "factoriz", "factoris",
                     "classically computable", "closed form", "cosine kernel"),
        "forbid": ("product state", "unentangled", "separable", "factoriz", "factoris", "classically computable",
                   "closed form", "closed-form", "dequantiz", "simulable"),
    },
    "full_readout": {
        "gate": "G1", "check": check_readout,
        "about": ("The algorithm's answer is the full N-dimensional output vector, and the repetitions "
                  "needed to read it out (tomography) already cost at least as much as the classical "
                  "method."),
        "twin": "Make the answer a single scalar (an expectation value or overlap) at the same precision, "
                "with everything else unchanged.",
        "spec_help": ('{"N": 1125899906842624, "readout": "all_amplitudes", "eps": 0.01, '
                      '"classical_cost_ops": 5.0e20}  (readout: all_amplitudes | all_probabilities | '
                      "scalar; eps = target error; classical_cost_ops = the classical method's cost for "
                      "the same answer)"),
        "keywords": ("readout", "read out", "read-out", "tomography", "shots", "repetitions", "sampling cost"),
        "forbid": ("tomography", "readout bottleneck", "read-out bottleneck", "dequantiz"),
    },
    "data_loading": {
        "gate": "G1", "check": check_loading,
        "about": ("Arbitrary classical data are amplitude-encoded, and the loading cost (N*d gates per "
                  "load, or building QRAM once) already costs at least as much as the classical method."),
        "twin": "Make the input state given by an efficient formula or circuit (structured data or "
                "quantum-native input) instead of arbitrary classical data.",
        "spec_help": ('{"N_rows": 1000000000, "d": 100000, "access": "arbitrary_classical", "loads": 1000000, '
                      '"classical_cost_ops": 1.0e20}  (access: arbitrary_classical | qram_assumed | '
                      "efficient_formula; loads = how many times the state is prepared; "
                      "classical_cost_ops = classical cost of the whole task)"),
        "keywords": ("loading", "load the data", "state preparation", "encoding cost", "input model", "qram"),
        "forbid": ("loading bottleneck", "input bottleneck", "dequantiz", "data-loading problem"),
    },
    "dequantizable_lowrank": {
        "gate": "G3", "check": check_dequantizable,
        "about": ("The input is a low-rank matrix given with sample-and-query (QRAM-style) access and the "
                  "output is a sample or a scalar, so Tang-style quantum-inspired sampling matches it "
                  "classically in polylog(N)."),
        "twin": "Make the matrix full rank (rank comparable to N) and sparse, given by a sparse oracle "
                "rather than sample-and-query access.",
        "spec_help": ('{"N": 1000000000, "rank": 50, "condition_number": 10, "eps": 0.05, '
                      '"access": "sample_query", "output": "sample"}  (access: sample_query | '
                      "sparse_oracle | circuit_block_encoding; output: sample | scalar | full_vector)"),
        "keywords": ("dequantiz", "quantum-inspired", "tang", "chia et al", "sampling-based classical",
                     "low-rank sampling", "length-square"),
        "forbid": ("dequantiz", "quantum-inspired", "tang 2019", "tang-style", "ewin tang", "chia et al",
                   "length-square", "classical sampling"),
    },
}


def check_spec(flaw: str, spec: dict) -> tuple[bool, str]:
    if flaw not in FLAWS:
        raise SpecError(f"unknown flaw {flaw}")
    if not isinstance(spec, dict):
        raise SpecError("spec must be an object")
    return FLAWS[flaw]["check"](spec)


# --- items ---------------------------------------------------------------------------------------
def facts(flaw: str, spec: dict) -> list:
    """Tokens the claim text must contain verbatim (case-insensitive), so the text states the spec.
    A tuple is a set of alternatives."""
    if flaw in ("clifford_only", "product_state_kernel"):
        names = sorted({str(g.get("name", "")).upper() for g in spec.get("layers", [])})
        return [f"{spec.get('n_qubits')} qubits", *names]
    if flaw == "full_readout":
        return [_fmt(spec.get("N")), {"all_amplitudes": "amplitude", "all_probabilities": "probabilit",
                                      "scalar": ("expectation", "scalar", "overlap", "single number")
                                      }.get(spec.get("readout"), "?")]
    if flaw == "data_loading":
        return [_fmt(spec.get("N_rows")), {"arbitrary_classical": "amplitude", "qram_assumed": "QRAM",
                                           "efficient_formula": ("formula", "closed-form circuit", "efficient circuit",
                                                                 "generated by")}.get(spec.get("access"), "?")]
    if flaw == "dequantizable_lowrank":
        return [f"rank {spec.get('rank')}", {"sample_query": "sample", "sparse_oracle": "sparse",
                                             "circuit_block_encoding": "block-encod"}.get(spec.get("access"), "?")]
    return []


def _fmt(v) -> str:
    """How a size must appear in the text: an exact integer, digits only (10^9 is written 1000000000)."""
    return str(int(v)) if isinstance(v, (int, float)) and not isinstance(v, bool) else str(v)


def _norm(text: str) -> str:
    return re.sub(r"(?<=\d)[,_ ](?=\d{3})", "", text.lower())


def _has(text: str, token: str) -> bool:
    """token at a word start; short tokens (gate names like H, S, CX) must also end a word."""
    t, text = _norm(token), _norm(text)
    tail = r"(?![a-z0-9])" if len(t) <= 4 else ""
    return re.search(r"(?<![a-z0-9])" + re.escape(t) + tail, text) is not None


def text_problems(flaw: str, kind: str, item: dict) -> list[str]:
    text = _norm(f"{item.get('title', '')}\n{item.get('claim', '')}")
    out = [f"missing fact {t!r}" for t in facts(flaw, item.get("spec") or {})
           if not any(_has(text, x) for x in (t if isinstance(t, tuple) else (t,)))]
    out += [f"leaks {w!r}" for w in (*FLAWS[flaw]["forbid"], *GENERIC_FORBID) if _has(text, w)]
    words = len(item.get("claim", "").split())
    if not 25 <= words <= 160:
        out.append(f"claim is {words} words (25-160)")
    return out


def validate_pair(flawed: dict, twin: dict, flaw: str) -> list[str]:
    """Everything that makes a pair unusable; empty list = accepted."""
    problems = []
    if flawed.get("title", "").strip() != twin.get("title", "").strip():
        problems.append("twin title must equal the flawed title (a different title cues the screen)")
    wf, wt = len(flawed.get("claim", "").split()), len(twin.get("claim", "").split())
    if wf and wt and not 0.8 <= wt / wf <= 1.25:
        problems.append(f"claim lengths differ too much ({wf} vs {wt} words)")
    for kind, it, want in (("flawed", flawed, True), ("twin", twin, False)):
        try:
            has, ev = check_spec(flaw, it.get("spec"))
        except SpecError as e:
            problems.append(f"{kind}: bad spec: {e}")
            continue
        if has != want:
            problems.append(f"{kind}: checker says has_flaw={has} ({ev})")
        problems += [f"{kind}: {p}" for p in text_problems(flaw, kind, it)]
    return problems


def make_pair(flaw: str, flawed: dict, twin: dict, by: dict, base: str | None, note: str = "") -> list[dict]:
    pair = "p-" + hashlib.sha256(json.dumps([flaw, flawed["claim"], twin["claim"]]).encode()).hexdigest()[:10]
    out = []
    for kind, it in (("flawed", flawed), ("twin", twin)):
        has, ev = check_spec(flaw, it["spec"])
        easy = None
        if kind == "twin" and flaw in ("clifford_only", "product_state_kernel"):
            ok, why = check_not_easy(it["spec"])
            easy = None if ok else why
        out.append({"id": f"{pair}-{'f' if kind == 'flawed' else 't'}", "pair": pair, "kind": kind,
                    "flaw": flaw, "expected_gate": FLAWS[flaw]["gate"], "title": it["title"],
                    "claim": it["claim"], "spec": it["spec"],
                    "check": {"has_flaw": has, "evidence": ev, **({"twin_easy": easy} if easy else {})},
                    "base": base, "by": by, "note": note, "at": now()})
    return out


def read_items(path: Path) -> list[dict]:
    return P.read_jsonl(path)


def check_items(items: list[dict]) -> list[str]:
    problems, pairs = [], {}
    ids = [it["id"] for it in items]
    if len(ids) != len(set(ids)):
        problems.append("duplicate item ids")
    for it in items:
        pairs.setdefault(it["pair"], {})[it["kind"]] = it
    for pid, kinds in pairs.items():
        if set(kinds) != {"flawed", "twin"}:
            problems.append(f"{pid}: needs one flawed and one twin item")
            continue
        flaw = kinds["flawed"]["flaw"]
        if kinds["twin"]["flaw"] != flaw:
            problems.append(f"{pid}: flawed and twin name different flaws")
            continue
        problems += [f"{pid}: {p}" for p in validate_pair(kinds["flawed"], kinds["twin"], flaw)]
    return problems


# --- generation ----------------------------------------------------------------------------------
GEN_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["flawed_title", "flawed_claim", "flawed_spec_json", "twin_title", "twin_claim", "twin_spec_json"],
    "properties": {k: {"type": "string"} for k in
                   ("flawed_title", "flawed_claim", "flawed_spec_json", "twin_title", "twin_claim", "twin_spec_json")},
}


def gen_prompt(flaw: str, base: dict, feedback: str = "") -> str:
    f = FLAWS[flaw]
    return "\n".join([
        "You are writing test items for an evaluation of a research screen in a quantum machine learning lab.",
        "The screen reads one-paragraph research candidates and decides whether each deserves compute.",
        "Write TWO candidates in the style of the example below, as a confident researcher would pitch them.",
        "",
        f"Example candidate from the lab's backlog (use its application area and tone, not its method):",
        f"Title: {base['title']}",
        f"Claim: {base['claim']}",
        "",
        "Candidate A (the 'flawed' one) must have this property in its quantum core, stated through concrete "
        "facts and never named or hinted at:",
        f"  {f['about']}",
        "Candidate B (the 'twin') is Candidate A with the smallest edit that removes the property:",
        f"  {f['twin']}",
        "B must be a pitch a careful screen could PASS, so the only reason to reject A is the property above:",
        f"  - a real classical bottleneck: the best known classical method (not brute-force state-vector "
        f"simulation) costs at least {MIN_CLASSICAL_OPS:.0e} operations (a day on an exaflop machine), "
        "circuits on 50 or more qubits, matrices with N of 1000000000 or more;",
        "  - inputs given by a formula, a circuit or a physical system, not a stored classical table, unless "
        "loading stored data is the property itself;",
        "  - an output the application actually needs: if B returns one number, the task must need only that number;",
        "  - no other cost (shots, loading, readout) that is obviously above the classical cost.",
        "Both must claim an advantage with equal confidence and read like real pitches. Neither may say it "
        "is a test, and neither may judge itself. Use the SAME title for both and change as few words of the "
        "claim as possible: the edit must be the only difference a reader can find.",
        "The script ignores gates that cannot change the result: diagonal gates (Z, S, T, RZ, CZ, RZZ) that "
        "act only on qubits still in |0>, or that are followed only by diagonal gates before the "
        "computational-basis measurement, and any fixed gates after the last data-dependent gate of a "
        "kernel feature map. So the edit must sit where it changes the output.",
        "",
        "For each candidate also give its quantum core as JSON (a string field), in this format:",
        f"  {f['spec_help']}",
        "A script checks the JSON: A must have the property, B must not. The claim text must state the "
        "JSON's facts: name every gate in UPPER CASE as in the JSON (e.g. H, CX, RZ), write the qubit count "
        "as '<n> qubits', write sizes as plain integers (1000000, not 10^6 or 1M), and write 'rank <k>' "
        "where a rank is given. Name an output as 'amplitudes', 'probabilities' or 'expectation value'; "
        "a data input as 'amplitude encoding', 'QRAM' or 'formula'; a matrix input as 'sample' (for "
        "sample-and-query access), 'sparse' or 'block-encoding'.",
        f"Never use these words in a title or claim: {', '.join((*f['forbid'], *GENERIC_FORBID))}.",
        "Each claim 40-120 words.",
        *(["", "Your previous attempt was rejected: " + feedback] if feedback else []),
        "",
        "Answer with JSON only, matching the schema.",
    ])


def parse_gen(text: str | None) -> tuple[dict, dict]:
    if not text:
        raise SpecError("no answer")
    m = re.search(r"\{.*\}", text, re.S)
    a = json.loads(m.group(0) if m else text)
    out = []
    for k in ("flawed", "twin"):
        try:
            spec = json.loads(a[f"{k}_spec_json"])
        except (KeyError, json.JSONDecodeError) as e:
            raise SpecError(f"{k}_spec_json is not JSON: {e}") from None
        out.append({"title": a[f"{k}_title"].strip(), "claim": a[f"{k}_claim"].strip(), "spec": spec})
    return out[0], out[1]


def generate(seat: dict, flaws: list[str], bases: list[dict], n: int, items_path: Path,
             caller=P.call_seat, tries: int = 2, log=print, seed: int = 0) -> dict:
    rng = random.Random(seed)
    accepted, rejected = 0, []
    by = {"seat": seat["id"], "family": seat["family"], "model": seat["model"], "prompt": GEN_VERSION}
    with items_path.open("a", encoding="utf-8") as f:
        for flaw in flaws:
            for _ in range(n):
                base = rng.choice(bases)
                feedback = ""
                for attempt in range(tries):
                    res = caller(seat, gen_prompt(flaw, base, feedback), GEN_SCHEMA)
                    try:
                        if not res.get("completed"):
                            raise SpecError(res.get("error") or "not completed")
                        flawed, twin = parse_gen(res.get("answer_text"))
                        problems = validate_pair(flawed, twin, flaw)
                    except (SpecError, KeyError, json.JSONDecodeError, AttributeError) as e:
                        problems = [str(e)]
                    if not problems:
                        for row in make_pair(flaw, flawed, twin, by, base.get("id")):
                            f.write(json.dumps(row, ensure_ascii=False) + "\n")
                        f.flush()
                        accepted += 1
                        break
                    feedback = "; ".join(problems)[:1500]
                    rejected.append({"flaw": flaw, "base": base.get("id"), "attempt": attempt + 1,
                                     "problems": problems})
                    log(f"  rejected {flaw} from {base.get('id')} (try {attempt + 1}): {feedback[:200]}")
    log(f"accepted {accepted} pairs, {len(rejected)} rejected attempts -> {items_path}")
    return {"accepted": accepted, "rejected": rejected}


# --- screening -----------------------------------------------------------------------------------
SCREEN_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["G0", "G1", "G2", "G3", "verdict", "deciding_gates", "note"],
    "properties": {
        "G0": {"type": "string"},
        **{g: {"type": "string", "enum": ["green", "amber", "red"]} for g in ("G1", "G2", "G3")},
        "verdict": {"type": "string", "enum": ["pass", "narrowed", "killed"]},
        "deciding_gates": {"type": "array", "items": {"type": "string", "enum": ["G0", "G1", "G2", "G3"]}},
        "note": {"type": "string"},
    },
}


def _triage_section() -> str:
    text = (REPO / "lab" / "roles" / "screen-analyst" / "PROTOCOL.md").read_text(encoding="utf-8")
    m = re.search(r"## Triage mode.*?(?=\n## )", text, re.S)
    return m.group(0) if m else text


def screen_prompt(item: dict, ledger: str | None = None) -> str:
    """What the screen sees: the screen analyst's triage protocol, the lab's method and domain
    criteria, optionally the exclusion ledger, and the candidate's title and claim. Never its spec,
    its flaw type, its twin, or who wrote it."""
    parts = [P.LAB_CONTEXT, "",
             "You are the lab's screen analyst in triage mode. Screen ONE candidate. Your protocol:", "",
             _triage_section(), "",
             "Answer only steps 1-3 (G0, G1-G3, verdict) here; skip the potential profile, value and bet sheet.",
             "Give each of G1-G3 as green, amber or red; G0 as the matching ledger entry or 'none'. "
             "In note, give the mechanism and number or precedent behind every red, in at most 80 words.",
             "", "=== criteria/lab_method.md ===", (REPO / "criteria" / "lab_method.md").read_text(encoding="utf-8"),
             "", "=== criteria/qml_domain.md ===", (REPO / "criteria" / "qml_domain.md").read_text(encoding="utf-8")]
    if ledger:
        parts += ["", "=== exclusion ledger ===", ledger]
    parts += ["", "=== candidate ===", f"Title: {item['title']}", f"Claim: {item['claim']}", "",
              "Answer with JSON only, matching the schema."]
    return "\n".join(parts)


def parse_screen(text: str | None) -> tuple[dict | None, str | None]:
    if not text:
        return None, "no answer"
    m = re.search(r"\{.*\}", text, re.S)
    try:
        a = json.loads(m.group(0) if m else text)
    except json.JSONDecodeError as e:
        return None, f"not JSON: {e}"
    if a.get("verdict") not in ("pass", "narrowed", "killed"):
        return None, f"bad verdict {a.get('verdict')!r}"
    for g in ("G1", "G2", "G3"):
        if a.get(g) not in ("green", "amber", "red"):
            return None, f"bad {g} {a.get(g)!r}"
    return {k: a.get(k) for k in ("G0", "G1", "G2", "G3", "verdict", "deciding_gates", "note")}, None


def run(seat: dict, items: list[dict], out: Path, runs: int = 1, ledger: str | None = None,
        workers: int = 4, caller=P.call_seat, log=print) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    path = out / "screens.jsonl"
    done = {(r["item"], r["seat"], r["run"], r["prompt_hash"]) for r in P.read_jsonl(path) if r.get("ok")}
    gen_families = {(it.get("by") or {}).get("family") for it in items}
    if seat["family"] in gen_families:
        log(f"warning: seat family {seat['family']} also wrote some items; report splits by author family")
    tasks = []
    for it in items:
        text = screen_prompt(it, ledger)
        h = hashlib.sha256((PROMPT_VERSION + "\n" + text).encode()).hexdigest()[:12]
        for r in range(runs):
            if (it["id"], seat["id"], r, h) not in done:
                tasks.append((it, r, text, h))
    log(f"screen seat {seat['id']} · {len(items)} items × {runs} runs · {len(tasks)} calls to make")

    def one(t):
        it, r, text, h = t
        res = caller(seat, text, SCREEN_SCHEMA)
        ans, err = parse_screen(res.get("answer_text")) if res.get("completed") else (None, res.get("error"))
        return {"item": it["id"], "pair": it["pair"], "kind": it["kind"], "flaw": it["flaw"],
                "seat": seat["id"], "family": seat["family"], "model": seat["model"],
                "resolved_model": res.get("resolved_model"), "run": r, "prompt_hash": h,
                "ledger": bool(ledger), "at": now(), "ok": ans is not None, "error": err,
                "cost_usd": (res.get("usage") or {}).get("total_cost_usd"), **(ans or {})}

    ok = failed = 0
    cost = 0.0
    with cf.ThreadPoolExecutor(max_workers=max(1, workers)) as pool, path.open("a", encoding="utf-8") as f:
        for row in pool.map(one, tasks):
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
            f.flush()
            ok += row["ok"]
            failed += not row["ok"]
            cost += row.get("cost_usd") or 0.0
            if not row["ok"]:
                log(f"  failed {row['item']} run {row['run']}: {row['error']}")
    log(f"recorded {ok} screens, {failed} failures, reported cost ${cost:.2f} -> {path}")
    return {"ok": ok, "failed": failed, "cost_usd": round(cost, 4)}


# --- report --------------------------------------------------------------------------------------
def _rate(xs: list[bool]) -> float | None:
    return round(sum(xs) / len(xs), 3) if xs else None


def _boot(pairs: list[tuple[float, float]], b: int = 2000, seed: int = 0) -> tuple[float, float] | None:
    """95% bootstrap interval of mean(flawed_kill - twin_kill) over pairs."""
    if len(pairs) < 2:
        return None
    rng = random.Random(seed)
    stats = sorted(sum(f - t for f, t in (rng.choice(pairs) for _ in pairs)) / len(pairs) for _ in range(b))
    return round(stats[int(0.025 * b)], 3), round(stats[int(0.975 * b) - 1], 3)


def summarize(rows: list[dict], items: dict[str, dict]) -> dict:
    rows = [r for r in rows if r.get("ok") and r["item"] in items]
    per_item: dict[str, list[dict]] = {}
    for r in rows:
        per_item.setdefault(r["item"], []).append(r)
    caught = {i: [r["verdict"] in KILL for r in rs] for i, rs in per_item.items()}
    # discrimination and false kills count only `killed`: a narrowed twin still goes on with a smaller claim
    killed = {i: [r["verdict"] == "killed" for r in rs] for i, rs in per_item.items()}
    strict = {i: [r["verdict"] in KILL and r.get(items[i]["expected_gate"]) == "red" for r in rs]
              for i, rs in per_item.items()}
    mention = {i: [any(k in (r.get("note") or "").lower() for k in FLAWS[items[i]["flaw"]]["keywords"])
                   for r in rs] for i, rs in per_item.items()}
    mean = lambda xs: sum(xs) / len(xs)   # noqa: E731
    flawed = [i for i in per_item if items[i]["kind"] == "flawed"]
    # a twin the checker flags as easy for another reason (e.g. a low-bond MPS) is rightly killed, so it
    # does not count toward false kills or discrimination; its kills are still listed in the report
    twins = [i for i in per_item if items[i]["kind"] == "twin" and not items[i]["check"].get("twin_easy")]
    pairs = []
    for i in flawed:
        t = i[:-1] + "t"
        if t in twins:
            pairs.append((mean(killed[i]), mean(killed[t])))
    multi = [rs for rs in per_item.values() if len(rs) > 1]
    stable = [len({r["verdict"] in KILL for r in rs}) == 1 for rs in multi]
    out = {
        "screens": len(rows), "items": len(per_item), "pairs": len(pairs),
        "easy_twins_excluded": sum(1 for i in per_item if items[i]["check"].get("twin_easy")),
        "catch_rate": _rate([x for i in flawed for x in caught[i]]),
        "catch_rate_strict": _rate([x for i in flawed for x in strict[i]]),
        "mechanism_named": _rate([x for i in flawed for x in mention[i]]),
        "false_kill_rate": _rate([x for i in twins for x in killed[i]]),
        "discrimination": round(mean([f - t for f, t in pairs]), 3) if pairs else None,
        "discrimination_ci95": _boot(pairs),
        "run_agreement": _rate(stable),
        # the triage protocol allows `killed` only on a red gate; a kill with no red breaks it
        "kill_without_red": _rate([r["verdict"] == "killed" and "red" not in (r.get("G1"), r.get("G2"), r.get("G3"))
                                   for r in rows if r["verdict"] == "killed"]),
        "cost_usd": round(sum(r.get("cost_usd") or 0 for r in rows), 2),
    }
    return out


def report(rows: list[dict], items: list[dict]) -> dict:
    by_id = {it["id"]: it for it in items}
    rows = [r for r in rows if r["item"] in by_id]          # screens of pruned items are ignored
    seats = sorted({r["seat"] for r in rows})
    rep = {"items": len(items), "pairs": len({it["pair"] for it in items}), "seats": {}}
    for s in seats:
        rs = [r for r in rows if r["seat"] == s]
        fam = next((r["family"] for r in rs), None)
        entry = {"family": fam, "all": summarize(rs, by_id), "by_flaw": {}, "by_author_family": {}}
        for flaw in FLAWS:
            sub = {i: it for i, it in by_id.items() if it["flaw"] == flaw}
            if any(r["item"] in sub for r in rs):
                entry["by_flaw"][flaw] = summarize(rs, sub)
        for af in sorted({(it.get("by") or {}).get("family") or "?" for it in items}):
            sub = {i: it for i, it in by_id.items() if ((it.get("by") or {}).get("family") or "?") == af}
            if any(r["item"] in sub for r in rs):
                entry["by_author_family"][af + (" (same family as screen)" if af == fam else "")] = summarize(rs, sub)
        # every kill of a twin, for a person to read: a minimal edit can leave a twin incoherent, and
        # killing it for that is right, so the false-kill rate is an upper bound until these are read
        entry["twin_kills"] = [{"item": r["item"], "flaw": r["flaw"], "run": r["run"], "verdict": r["verdict"],
                                "easy": bool(by_id[r["item"]]["check"].get("twin_easy")),
                                "red": [g for g in ("G1", "G2", "G3") if r.get(g) == "red"], "note": r.get("note")}
                               for r in rs if r.get("ok") and r["kind"] == "twin" and r["verdict"] == "killed"]
        rep["seats"][s] = entry
    return rep


def print_report(rep: dict, notes: int = 20) -> None:
    print(f"{rep['items']} items in {rep['pairs']} pairs")
    cols = ("screens", "catch_rate", "catch_rate_strict", "false_kill_rate", "discrimination",
            "discrimination_ci95", "mechanism_named", "run_agreement", "kill_without_red")
    for s, e in rep["seats"].items():
        print(f"\nseat {s} ({e['family']}), cost ${e['all']['cost_usd']}")
        print("  " + " · ".join(f"{c} {e['all'][c]}" for c in cols))
        for label, group in (("flaw", e["by_flaw"]), ("author", e["by_author_family"])):
            for k, v in group.items():
                print(f"  {label} {k}: catch {v['catch_rate']} (strict {v['catch_rate_strict']}) · "
                      f"false kill {v['false_kill_rate']} · discrimination {v['discrimination']} · n pairs {v['pairs']}")
        if e["twin_kills"]:
            print(f"  twin kills to read ({len(e['twin_kills'])}; the false-kill rate is an upper bound until read):")
            for t in e["twin_kills"][:notes]:
                print(f"    {t['item']} run {t['run']} {t['flaw']}{' (easy twin)' if t['easy'] else ''} "
                      f"red {','.join(t['red']) or '-'}: {(t['note'] or '')[:160]}")


# --- CLI -----------------------------------------------------------------------------------------
def _seat(panel: str, seat_id: str) -> dict:
    p = P.load_panel(panel)
    s = next((s for s in p["seats"] if s["id"] == seat_id), None)
    if not s:
        raise LabError(f"no seat {seat_id} in panel {panel}; seats: {', '.join(x['id'] for x in p['seats'])}")
    why = P.seat_available(s)
    if why:
        raise LabError(f"seat {seat_id} cannot run here: {why}")
    return s


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(prog="lab.tools.flaweval")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("check", "generate", "prompt", "run", "report"):
        p = sub.add_parser(name)
        p.add_argument("--items", type=Path, default=ITEMS)
        if name in ("generate", "run"):
            p.add_argument("--seat", required=True)
            p.add_argument("--panel", default="default")
        if name in ("run", "report"):
            p.add_argument("--out", type=Path)
        if name in ("run", "prompt"):
            p.add_argument("--ledger", type=Path, help="exclusion ledger to show the screen (default: none)")
    sub.choices["check"].add_argument("--prune", action="store_true", help="drop every failing pair from --items")
    sub.choices["generate"].add_argument("--flaws", default=",".join(FLAWS))
    sub.choices["generate"].add_argument("--bases", default="", help="backlog candidate ids (default: all)")
    sub.choices["generate"].add_argument("--root", type=Path, help="backlog folder")
    sub.choices["generate"].add_argument("--n", type=int, default=1, help="pairs per flaw")
    sub.choices["generate"].add_argument("--seed", type=int, default=0)
    sub.choices["prompt"].add_argument("item")
    sub.choices["run"].add_argument("--runs", type=int, default=1)
    sub.choices["run"].add_argument("--only", default="")
    sub.choices["run"].add_argument("--workers", type=int, default=4)
    sub.choices["report"].add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    items = read_items(a.items) if a.items.exists() else []
    if a.cmd == "check":
        problems = check_items(items)
        for pr in problems:
            print("FAIL " + pr)
        if a.prune and problems:
            bad = {pr.split(":", 1)[0] for pr in problems}
            keep = [i for i in items if i["pair"] not in bad]
            a.items.write_text("".join(json.dumps(i, ensure_ascii=False) + "\n" for i in keep), encoding="utf-8")
            print(f"pruned {len(items) - len(keep)} items; {len(keep)} kept")
            return 0
        print(f"{len(items)} items, {len({i['pair'] for i in items})} pairs, {len(problems)} problems")
        return 1 if problems else 0
    if a.cmd == "generate":
        flaws = [f for f in a.flaws.split(",") if f]
        unknown = [f for f in flaws if f not in FLAWS]
        if unknown:
            raise LabError(f"unknown flaws: {unknown}")
        cands, _ = P.load_items(P.backlog_root(a.root))
        want = {x for x in a.bases.split(",") if x}
        bases = [c for c in cands if not want or c["id"] in want]
        if not bases:
            raise LabError("no base candidates")
        a.items.parent.mkdir(parents=True, exist_ok=True)
        generate(_seat(a.panel, a.seat), flaws, bases, a.n, a.items, seed=a.seed)
        return 0
    ledger = a.ledger.read_text(encoding="utf-8") if getattr(a, "ledger", None) else None
    if a.cmd == "prompt":
        it = next((i for i in items if i["id"] == a.item), None)
        if not it:
            raise LabError(f"unknown item {a.item}")
        print(screen_prompt(it, ledger))
        return 0
    out = a.out or output_root() / "indexes" / "evals" / "planted_flaws"
    if a.cmd == "run":
        problems = check_items(items)
        if problems:
            raise LabError(f"{len(problems)} item problems; run `check` first")
        only = {x for x in a.only.split(",") if x}
        todo = [i for i in items if not only or i["id"] in only or i["pair"] in only]
        res = run(_seat(a.panel, a.seat), todo, out, a.runs, ledger, a.workers)
        return 1 if res["failed"] else 0
    rows = [r for p in sorted(out.glob("screens*.jsonl")) for r in P.read_jsonl(p)]
    rep = report(rows, items)
    if a.json:
        print(json.dumps(rep, indent=1, ensure_ascii=False))
    else:
        print_report(rep)
    return 0


if __name__ == "__main__":
    main_wrapper(main)
