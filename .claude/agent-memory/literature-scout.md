# Literature Scout Memory

## Session Log

### 2026-05-31 — QCNN vs CNN parameter efficiency fact-check

**Research question:** Does QCNN show accuracy comparable to classical CNN with significantly fewer parameters?
**Output:** `output/research/qcnn-vs-cnn-parameter-efficiency_2026-05-31/01_literature_merged.md`
**Depth target met:** Yes (9 papers screened/included, 3+ directly addressing the claim)

**Summary:** Found strong evidence that the claim is context-dependent and potentially misleading. The primary supporting paper (Hur et al. 2022, arXiv 2108.00661, Quantum Machine Intelligence T2) artificially constrains the classical baseline to the same parameter budget and uses PCA-compressed inputs. The strongest counter-evidence is Bermejo et al. 2024 (arXiv 2408.12739, PRX Quantum T1), which proves QCNNs are classically simulable using Pauli shadow methods on all tested benchmarks up to 1024 qubits.

---

## Discovered Papers (verified identifiers)

| arXiv ID | Title | Authors | Year | Venue | Notes |
|---|---|---|---|---|---|
| 1810.03787 | Quantum Convolutional Neural Networks | Cong, Choi, Lukin | 2019 | Nature Physics | Foundational; quantum data (phases of matter); NOT image classification baseline |
| 2108.00661 | Quantum convolutional neural network for classical data classification | Hur, Kim, Park | 2022 | Quantum Machine Intelligence | Key paper for claim; MNIST/Fashion-MNIST; CNN baseline constrained to same param budget |
| 2011.02966 | Absence of Barren Plateaus in Quantum Convolutional Neural Networks | Pesah, Cerezo et al. | 2021 | Physical Review X | Proves polynomial gradient decay; partially superseded by 2408.12739 |
| 2408.12739 | Quantum Convolutional Neural Networks are Effectively Classically Simulable | Bermejo, Braccia, Rudolph, Holmes, Cincio, Cerezo | 2024/2026 | PRX Quantum | CRITICAL: shadow-based classical surrogates match QCNNs up to 1024 qubits |
| 2501.17041 | Benchmarking QCNNs for Signal Classification in Simulated Gamma-Ray Burst Detection | Farsian et al. | 2025 | PDP 2025/IEEE | Astrophysics domain; not image classification |
| 2411.13468 | Benchmarking QCNNs for Classification and Data Compression Tasks | Khoo et al. | 2024 | arXiv | Quantum phases benchmark; no classical CNN comparison |
| 2505.05957 | Efficient Quantum Convolutional Neural Networks for Image Classification | Röseler et al. | 2025 | arXiv | 96% vs 71% classical on MNIST — classical baseline likely constrained |
| 2603.11131 | Beyond Barren Plateaus: A Scalable QCNN for High-Fidelity Image Classification | Delhibabu | 2026 | arXiv | MNIST; O(log N) param claim; no strong classical baseline |
| s41467-025-63099-6 | Does provable absence of barren plateaus imply classical simulability? | — | 2025 | Nature Communications | Nuanced: BP-free regions can exist outside known simulable regimes |

---

## Useful Queries

- `"quantum convolutional neural network" accuracy benchmark classical CNN parameter efficiency` — returns relevant papers
- `QCNN barren plateau trainability classical simulability limitations` — returns Bermejo 2024 and Pesah 2021
- arXiv HTML reader at `ar5iv.labs.arxiv.org/html/<id>` — useful for extracting numerical results from PDFs that don't convert well

## Source Classes Tried

- Web search (Google) — worked well
- ar5iv HTML rendering — worked for numerical extraction from 2108.00661
- WebFetch on Nature/Springer pages — paywalled, redirects
- WebFetch on PDF URLs — binary format, not readable

## Unresolved Bibliographic Gaps

- Citation count for 2408.12739 not confirmed (estimated ~50+ from search result snippets)
- Citation count for s41467-025-63099-6 (Nature Comms 2025) not confirmed
- Exact authors for s41467-025-63099-6 not extracted (paywall)

## Known Non-Productive Source Classes

- Springer/Nature direct fetch — authentication redirect
- arXiv PDF fetch — binary, unreadable
