"""Reference reproduction for card qml-06 (Huang et al., Power of data in QML, arXiv:2011.01938).

Small-scale rerun of the paper's numerical study (Appendix L) at n <= 12 qubits. Its numbers are the
numeric answer key for card v2 qml-06 and the source of the mocked gate table and raw-results file.
The lab is graded against these numbers, not the paper's figures.

    python -I scripts/paper_replay/reference/qml06_power_of_data.py [--sizes 2 4 6 8 10 12] [--seeds 3]

Writes output/paper-replay/reference/qml-06/{runs.jsonl, results.json}. Resumable per run.

Deviations from the paper, all deliberate:
- Hyperparameters are chosen by 3-fold CV on the training split (lab rule). The paper reports the
  best hyperparameter on the reported split; that number is also recorded as `test_best`.
- Kernel regression uses KernelRidge (alpha = 1/(2C)) only, not best-of SVR/KernelRidge.
- E2 uses pairs j < j' in U_Z and exp(+i ...); the paper's double-sum and phase convention are
  ambiguous in the text.
- Engineered labels are thresholded at the median (Appendix G) before the 10% random flips (L15).
- PCA is fitted on all dress and shirt training images, for every task.
"""
from __future__ import annotations

import argparse
import gzip
import json
import os
from pathlib import Path
import sys
import urllib.request

for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np  # noqa: E402

REPO = Path(__file__).resolve().parents[3]
DATA = REPO / "output/paper-replay/data/fashion-mnist"
OUT = REPO / "output/paper-replay/reference/qml-06"
FMNIST_URL = "https://raw.githubusercontent.com/zalandoresearch/fashion-mnist/master/data/fashion/"
FILES = ("train-images-idx3-ubyte.gz", "train-labels-idx1-ubyte.gz")

N_TOTAL, N_TRAIN = 800, 600
C_GRID = [0.006, 0.015, 0.03, 0.0625, 0.125, 0.25, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0, 32.0, 64.0,
          128.0, 256, 512, 1024]                                    # L17, L25
GAMMA_MODEL = [0.25, 0.5, 1.0, 2.0, 3.0, 4.0, 5.0, 20.0]            # L19, L28 (÷ n·Var)
GAMMA_G = [0.25, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0, 32.0, 64.0]         # L11 (÷ n·Var)
LAMBDA_G = [1e-5, 1e-4, 1e-3, 0.01, 0.025, 0.05, 0.1]               # L10
G_TRA_MAX = 0.045                                                   # L9
DEPTHS, TREES = [2, 3, 4, 5], [25, 50, 100, 200, 500]               # L20–L24
HIDDEN = [10, 25, 50, 75, 100, 125, 150, 200]                       # L16


# ---------------------------------------------------------------- data

def load_fmnist() -> tuple[np.ndarray, np.ndarray]:
    DATA.mkdir(parents=True, exist_ok=True)
    for f in FILES:
        if not (DATA / f).exists():
            urllib.request.urlretrieve(FMNIST_URL + f, DATA / f)
    with gzip.open(DATA / FILES[0], "rb") as fh:
        img = np.frombuffer(fh.read(), np.uint8, offset=16).reshape(-1, 784).astype(float) / 255
    with gzip.open(DATA / FILES[1], "rb") as fh:
        lab = np.frombuffer(fh.read(), np.uint8, offset=8)
    keep = (lab == 3) | (lab == 6)                                   # dress = 3, shirt = 6
    return img[keep], np.where(lab[keep] == 3, 1, -1)


def pca_features(img: np.ndarray, n: int) -> np.ndarray:
    from sklearn.decomposition import PCA
    x = PCA(n_components=n, random_state=0).fit_transform(img)
    return (x - x.mean(0)) / x.std(0)


# ---------------------------------------------------------------- statevector simulator (batched)

def apply_1q(psi: np.ndarray, q: int, u: np.ndarray) -> np.ndarray:
    """psi: (B, 2, ..., 2); u: (2, 2) or (B, 2, 2)."""
    psi = np.moveaxis(psi, q + 1, -1)
    psi = np.einsum("b...j,bij->b...i", psi, u) if u.ndim == 3 else psi @ u.T
    return np.moveaxis(psi, -1, q + 1)


def apply_heisenberg(psi: np.ndarray, q: int, theta: np.ndarray) -> np.ndarray:
    """exp(-i θ (XX+YY+ZZ)) on qubits q, q+1, per batch item: e^{iθ}(cos2θ·I − i sin2θ·SWAP)."""
    shape = (-1,) + (1,) * (psi.ndim - 1)
    swapped = np.swapaxes(psi, q + 1, q + 2)
    return np.exp(1j * theta).reshape(shape) * (np.cos(2 * theta).reshape(shape) * psi
                                                - 1j * np.sin(2 * theta).reshape(shape) * swapped)


def zero_state(b: int, nq: int) -> np.ndarray:
    psi = np.zeros((b,) + (2,) * nq, complex)
    psi[(slice(None),) + (0,) * nq] = 1
    return psi


def embed(x: np.ndarray, kind: str, rng_state: np.random.Generator) -> np.ndarray:
    b, n = x.shape
    if kind == "E1":                                                 # L1: Π_j exp(-i X_j x_j)|0>
        psi = zero_state(b, n)
        for j in range(n):
            c, s = np.cos(x[:, j]), np.sin(x[:, j])
            u = np.stack([np.stack([c, -1j * s], -1), np.stack([-1j * s, c], -1)], -2)
            psi = apply_1q(psi, j, u)
        return psi
    if kind == "E2":                                                 # L2–L3: U_Z H U_Z H |0>
        z = 1 - 2 * ((np.arange(2 ** n)[:, None] >> (n - 1 - np.arange(n))) & 1)   # (2^n, n)
        phase = x @ z.T                                              # Σ_j x_j z_j
        for j in range(n):
            for k in range(j + 1, n):
                phase += np.outer(x[:, j] * x[:, k], z[:, j] * z[:, k])
        diag = np.exp(1j * phase)
        plus = np.full(2 ** n, 2 ** (-n / 2), complex)
        h = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
        psi = (diag * plus).reshape((b,) + (2,) * n)
        for j in range(n):
            psi = apply_1q(psi, j, h)
        return (psi.reshape(b, -1) * diag).reshape((b,) + (2,) * n)
    if kind == "E3":                                                 # L4: Trotterized Heisenberg on n+1 qubits
        nq, steps, t = n + 1, 20, n / 3
        haar = [haar_state(rng_state) for _ in range(nq)]
        full = haar[0]
        for v in haar[1:]:
            full = np.kron(full, v)
        psi = np.tile(full, (b, 1)).reshape((b,) + (2,) * nq)
        for _ in range(steps):
            for j in range(n):
                psi = apply_heisenberg(psi, j, (t / steps) * x[:, j])
        return psi
    raise ValueError(kind)


def haar_state(rng: np.random.Generator) -> np.ndarray:
    v = rng.normal(size=2) + 1j * rng.normal(size=2)
    return v / np.linalg.norm(v)


def qnn_label(psi: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """L12–L13: Trotterized Heisenberg with Gaussian couplings, T = t = 10, then <Z_1>."""
    nq = psi.ndim - 1
    J = rng.normal(size=nq - 1)
    for _ in range(10):
        for j in range(nq - 1):
            psi = apply_heisenberg(psi, j, np.full(psi.shape[0], J[j]))
    p = np.abs(psi) ** 2
    return p[:, 0].reshape(psi.shape[0], -1).sum(1) - p[:, 1].reshape(psi.shape[0], -1).sum(1)


def pauli_features(psi: np.ndarray) -> np.ndarray:
    """<X_k>, <Y_k>, <Z_k> for every qubit: the 1-RDM features of the projected kernel (L6)."""
    b, nq = psi.shape[0], psi.ndim - 1
    feats = []
    for k in range(nq):
        a = np.moveaxis(psi, k + 1, -1).reshape(b, -1, 2)
        rho01 = np.einsum("bi,bi->b", a[:, :, 0], a[:, :, 1].conj())
        feats += [2 * rho01.real, -2 * rho01.imag,
                  (np.abs(a[:, :, 0]) ** 2).sum(1) - (np.abs(a[:, :, 1]) ** 2).sum(1)]
    return np.stack(feats, 1)


# ---------------------------------------------------------------- kernel diagnostics

def sqd(a: np.ndarray, b: np.ndarray | None = None) -> np.ndarray:
    b = a if b is None else b
    return np.maximum((a * a).sum(1)[:, None] + (b * b).sum(1)[None] - 2 * a @ b.T, 0)


def psd_sqrt(k: np.ndarray) -> np.ndarray:
    e, u = np.linalg.eigh((k + k.T) / 2)
    return (u * np.sqrt(np.clip(e, 0, None))) @ u.T


def eff_dim(k: np.ndarray) -> float:
    """F12: d = Σ_k (Σ_{l>=k} t_l) / (N - k + 1), with Tr(K) = N."""
    t = np.sort(np.clip(np.linalg.eigvalsh(k * len(k) / np.trace(k)), 0, None))[::-1]
    tail = np.cumsum(t[::-1])[::-1]
    return float((tail / (len(t) - np.arange(len(t)))).sum())


def classical_kernels(x: np.ndarray) -> list[tuple[str, np.ndarray]]:
    n, var = x.shape[1], x.var()
    lin = x @ x.T
    out = [("linear", lin * len(x) / np.trace(lin))]
    d2 = sqd(x)
    out += [(f"rbf{g}", np.exp(-(g / (n * var)) * d2)) for g in GAMMA_G]
    return out


def geometric_difference(kq: np.ndarray, kcs: list[tuple[str, np.ndarray]]) -> dict:
    """L8–L9: min over classical kernels and λ of g_gen, subject to g_tra < 0.045."""
    sq = psd_sqrt(kq * len(kq) / np.trace(kq))
    best = None
    for name, kc in kcs:
        e, u = np.linalg.eigh((kc + kc.T) / 2)
        e = np.clip(e, 0, None)
        a = sq @ u
        for lam in LAMBDA_G:
            m_gen = (a * (e / (e + lam) ** 2)) @ a.T
            m_tra = (a * (1 / (e + lam) ** 2)) @ a.T
            g_tra = lam * np.sqrt(np.linalg.eigvalsh(m_tra)[-1])
            w, v = np.linalg.eigh(m_gen)
            g = float(np.sqrt(max(w[-1], 0)))
            ok = bool(g_tra < G_TRA_MAX)
            # Among configs meeting the training-error condition, the smallest g. If none meets it,
            # the config that fits training data best (smallest g_tra), flagged ok = False.
            rank = (ok, -g if ok else -g_tra)
            if best is None or rank > best["rank"]:
                best = {"g": g, "kernel": name, "lambda": lam, "g_tra": float(g_tra), "ok": ok,
                        "rank": rank, "v": v[:, -1]}
    best.pop("rank")
    best["y"] = sq @ best.pop("v")
    return best


# ---------------------------------------------------------------- models

def kfold_idx(n: int, k: int = 3) -> list[tuple[np.ndarray, np.ndarray]]:
    idx = np.arange(n)
    return [(np.setdiff1d(idx, f), f) for f in np.array_split(idx, k)]


def score(task: str, y, p) -> float:
    return float(np.mean(np.sign(p) != y)) if task == "cls" else float(np.mean(np.abs(p - y)))


def run_family(task, make, configs, Xtr, ytr, Xte, yte, precomputed=False) -> dict:
    """CV-selected test error (lab protocol) and best-on-test error (paper protocol)."""
    folds = kfold_idx(len(ytr))
    res = []
    for cfg in configs:
        cv = []
        for tr, va in folds:
            m = make(cfg)
            if precomputed:
                m.fit(Xtr[np.ix_(tr, tr)], ytr[tr]); p = m.predict(Xtr[np.ix_(va, tr)])
            else:
                m.fit(Xtr[tr], ytr[tr]); p = m.predict(Xtr[va])
            cv.append(score(task, ytr[va], p))
        m = make(cfg)
        m.fit(Xtr, ytr)
        res.append((float(np.mean(cv)), score(task, yte, m.predict(Xte)), cfg))
    pick = min(res, key=lambda r: r[0])
    return {"test_cv": pick[1], "cfg": str(pick[2]), "test_best": min(r[1] for r in res)}


def classical_suite(task, xtr, ytr, xte, yte) -> dict:
    from sklearn.svm import SVC
    from sklearn.kernel_ridge import KernelRidge
    from sklearn.ensemble import (RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier,
                                  GradientBoostingRegressor, AdaBoostClassifier, AdaBoostRegressor)
    from sklearn.neural_network import MLPClassifier, MLPRegressor
    n, var = xtr.shape[1], xtr.var()
    cls = task == "cls"
    trees = [(d, t) for d in DEPTHS for t in TREES]
    fams = {
        "gaussian": (lambda c: SVC(C=c[0], gamma=c[1] / (n * var)) if cls else
                     KernelRidge(alpha=1 / (2 * c[0]), kernel="rbf", gamma=c[1] / (n * var)),
                     [(c, g) for c in C_GRID for g in GAMMA_MODEL]),
        "linear": (lambda c: SVC(C=c, kernel="linear") if cls else KernelRidge(alpha=1 / (2 * c)), C_GRID),
        "random_forest": (lambda c: (RandomForestClassifier if cls else RandomForestRegressor)(
            max_depth=c[0], n_estimators=c[1], random_state=0), trees),
        "gradient_boosting": (lambda c: (GradientBoostingClassifier if cls else GradientBoostingRegressor)(
            max_depth=c[0], n_estimators=c[1], random_state=0), trees),
        "adaboost": (lambda c: (AdaBoostClassifier if cls else AdaBoostRegressor)(
            n_estimators=c, random_state=0), TREES),
        "neural_network": (lambda h: (MLPClassifier if cls else MLPRegressor)(
            hidden_layer_sizes=(h, h), max_iter=2000, random_state=0), HIDDEN),
    }
    out = {k: run_family(task, mk, cf, xtr, ytr, xte, yte) for k, (mk, cf) in fams.items()}
    best = min(out, key=lambda k: out[k]["test_cv"])
    out["best_classical"] = {"model": best, **out[best]}
    return out


def kernel_model(task, k_full, tr, te, ytr, yte) -> dict:
    from sklearn.svm import SVC
    from sklearn.kernel_ridge import KernelRidge
    make = (lambda c: SVC(C=c, kernel="precomputed")) if task == "cls" else \
        (lambda c: KernelRidge(alpha=1 / (2 * c), kernel="precomputed"))
    return run_family(task, make, C_GRID, k_full[np.ix_(tr, tr)], ytr, k_full[np.ix_(te, tr)], yte,
                      precomputed=True)


def pq_model(task, feats, tr, te, ytr, yte) -> dict:
    var, n = feats.var(), feats.shape[1] / 3
    d2 = sqd(feats)
    best = None
    for g in GAMMA_MODEL:
        r = kernel_model(task, np.exp(-(g / (n * var)) * d2), tr, te, ytr, yte)
        r["cfg"] = f"gamma={g},{r['cfg']}"
        if best is None or r["test_cv"] < best["test_cv"]:
            best = {**r, "test_best": min(r["test_best"], best["test_best"]) if best else r["test_best"]}
        else:
            best["test_best"] = min(best["test_best"], r["test_best"])
    return best


# ---------------------------------------------------------------- one run

def one_run(emb: str, n: int, seed: int, n_train: int = N_TRAIN) -> dict:
    img, lab = load_fmnist()
    x_pool = pca_features(img, n)
    rng = np.random.default_rng(1000 * seed + n)
    pick = rng.choice(len(x_pool), N_TOTAL, replace=False)
    x, y_c = x_pool[pick], lab[pick]
    perm = rng.permutation(N_TOTAL)
    tr, te = perm[:n_train], perm[N_TRAIN:]                          # test split fixed at 200
    psi = embed(x, emb, np.random.default_rng(seed))
    feats = pauli_features(psi)
    if emb == "E1":                                                  # product state: closed form
        assert np.allclose(feats[:, 2::3], np.cos(2 * x), atol=1e-8)
        assert np.allclose(feats[:, 1::3], -np.sin(2 * x), atol=1e-8)
    flat = psi.reshape(N_TOTAL, -1)
    k_q = np.abs(flat.conj() @ flat.T) ** 2
    k_pq = np.exp(-(1.0 / (feats.shape[1] / 3 * feats.var())) * sqd(feats))
    kcs = classical_kernels(x)
    g_q, g_pq = geometric_difference(k_q, kcs), geometric_difference(k_pq, kcs)
    y_q = qnn_label(psi, np.random.default_rng(10_000 + seed))
    y_e = np.sign(g_pq["y"] - np.median(g_pq["y"]))
    flip = rng.random(N_TOTAL) < 0.1
    y_e[flip] = rng.choice([-1, 1], flip.sum())

    rec = {"emb": emb, "n": n, "seed": seed, "n_train": n_train, "qubits": psi.ndim - 1,
           "d_Q": eff_dim(k_q), "d_PQ": eff_dim(k_pq),
           "g_CQ": g_q["g"], "g_CPQ": g_pq["g"],
           "g_CQ_cfg": {k: g_q[k] for k in ("kernel", "lambda", "g_tra", "ok")},
           "g_CPQ_cfg": {k: g_pq[k] for k in ("kernel", "lambda", "g_tra", "ok")},
           "kq_offdiag_mean": float((k_q.sum() - N_TOTAL) / (N_TOTAL * (N_TOTAL - 1))),
           "y_q_std": float(y_q.std()), "tasks": {}}
    for task_name, task, yy in (("C", "cls", y_c), ("Q", "reg", y_q), ("engineered", "cls", y_e)):
        r = {"Q": kernel_model(task, k_q, tr, te, yy[tr], yy[te]),
             "PQ": pq_model(task, feats, tr, te, yy[tr], yy[te])}
        r.update(classical_suite(task, x[tr], yy[tr], x[te], yy[te]))
        rec["tasks"][task_name] = r
    return rec


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sizes", type=int, nargs="+", default=[2, 4, 6, 8, 10, 12])
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--n-sweep", type=int, nargs="+", default=[100, 200, 400, 600])
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    load_fmnist()
    runs = OUT / "runs.jsonl"
    done = set()
    if runs.exists():
        for line in runs.read_text(encoding="utf-8").splitlines():
            r = json.loads(line)
            done.add((r["emb"], r["n"], r["seed"], r["n_train"]))
    jobs = [(e, n, s, N_TRAIN) for e in ("E1", "E2", "E3") for n in args.sizes for s in range(args.seeds)]
    jobs += [(e, 10, s, m) for e in ("E2", "E3") for s in range(args.seeds) for m in args.n_sweep
             if m != N_TRAIN]
    jobs = [j for j in jobs if j not in done]
    print(f"{len(jobs)} runs to do", flush=True)
    import concurrent.futures as cf
    with cf.ProcessPoolExecutor(args.workers) as ex, runs.open("a", encoding="utf-8") as fh:
        futs = {ex.submit(one_run, *j): j for j in jobs}
        for f in cf.as_completed(futs):
            try:
                rec = f.result()
            except Exception as e:  # noqa: BLE001
                print("FAILED", futs[f], repr(e), flush=True)
                continue
            fh.write(json.dumps(rec) + "\n"); fh.flush()
            t = rec["tasks"]
            print(rec["emb"], rec["n"], rec["seed"], rec["n_train"],
                  f"g_CPQ={rec['g_CPQ']:.2f} eng: PQ={1 - t['engineered']['PQ']['test_cv']:.3f} "
                  f"best_cl={1 - t['engineered']['best_classical']['test_cv']:.3f}", flush=True)
    summarize(runs)


def summarize(runs: Path) -> None:
    recs = [json.loads(l) for l in runs.read_text(encoding="utf-8").splitlines()]
    agg: dict = {}
    for r in recs:
        key = f"{r['emb']}|n={r['n']}|N={r['n_train']}"
        a = agg.setdefault(key, {"emb": r["emb"], "n": r["n"], "n_train": r["n_train"], "seeds": 0, "vals": {}})
        a["seeds"] += 1
        vals = {"d_Q": r["d_Q"], "d_PQ": r["d_PQ"], "g_CQ": r["g_CQ"], "g_CPQ": r["g_CPQ"],
                "kq_offdiag_mean": r["kq_offdiag_mean"],
                "g_CQ_ok": float(r["g_CQ_cfg"]["ok"]), "g_CPQ_ok": float(r["g_CPQ_cfg"]["ok"])}
        for task, t in r["tasks"].items():
            for arm in ("Q", "PQ", "best_classical"):
                vals[f"{task}.{arm}.cv"] = t[arm]["test_cv"]
                vals[f"{task}.{arm}.best"] = t[arm]["test_best"]
        for k, v in vals.items():
            a["vals"].setdefault(k, []).append(v)
    for a in agg.values():
        a["mean"] = {k: float(np.mean(v)) for k, v in a["vals"].items()}
        a["sd"] = {k: float(np.std(v)) for k, v in a["vals"].items()}
        del a["vals"]
    (OUT / "results.json").write_text(json.dumps(dict(sorted(agg.items())), indent=1), encoding="utf-8")
    print("wrote", OUT / "results.json")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "summarize":
        summarize(OUT / "runs.jsonl")
    else:
        main()
