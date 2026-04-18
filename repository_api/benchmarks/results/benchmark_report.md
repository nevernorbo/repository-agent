# Repository API — Benchmark Report

_Generated on 2026-04-18 17:16 UTC_

## 1. Indexing Performance

| Repository | Size Category | Files | LOC | Indexing Time (s) | Status |
|---|---|---|---|---|---|
| `nevernorbo/mean-flashcards` | small | 0 | 0 | 26.07 | completed |
| `fastapi/fastapi` | large | 0 | 0 | 89.13 | completed |
| `expressjs/express` | medium | 0 | 0 | 20.23 | completed |

## 2. Search Latency

| Repository | Queries | Mean (ms) | P50 (ms) | P90 (ms) | P99 (ms) |
|---|---|---|---|---|---|
| `nevernorbo/mean-flashcards` | 50 | 183.93 | 178.81 | 198.36 | 354.77 |
| `fastapi/fastapi` | 50 | 191.80 | 178.88 | 225.33 | 439.20 |
| `expressjs/express` | 50 | 168.54 | 167.41 | 192.80 | 225.46 |

## 3. Concurrency Performance

### `nevernorbo/mean-flashcards`

| Concurrency | Mean Latency (ms) | Throughput (qps) | Errors |
|---|---|---|---|
| 1 | 170.76 | 4.55 | 0 |
| 2 | 270.88 | 4.88 | 0 |
| 5 | 496.56 | 5.29 | 0 |
| 10 | 1034.08 | 5.40 | 0 |
| 20 | 1959.52 | 5.26 | 0 |

### `fastapi/fastapi`

| Concurrency | Mean Latency (ms) | Throughput (qps) | Errors |
|---|---|---|---|
| 1 | 381.32 | 2.24 | 0 |
| 2 | 600.79 | 3.17 | 0 |
| 5 | 881.20 | 4.19 | 0 |
| 10 | 1543.35 | 4.33 | 0 |
| 20 | 2997.53 | 4.43 | 0 |

### `expressjs/express`

| Concurrency | Mean Latency (ms) | Throughput (qps) | Errors |
|---|---|---|---|
| 1 | 138.97 | 6.57 | 0 |
| 2 | 282.37 | 4.93 | 0 |
| 5 | 473.74 | 5.76 | 0 |
| 10 | 1000.26 | 5.35 | 0 |
| 20 | 1789.19 | 5.78 | 0 |


## 4. Retrieval Quality (All Queries)

| Repository | P@1 | R@1 | P@3 | R@3 | P@5 | R@5 | P@10 | R@10 | MRR |
|---|---|---|---|---|---|---|---|---|---|
| `nevernorbo/mean-flashcards` | 0.40 | 0.22 | 0.37 | 0.58 | 0.35 | 0.90 | 0.17 | 0.90 | 0.45 |
| `fastapi/fastapi` | 0.28 | 0.21 | 0.25 | 0.58 | 0.22 | 0.82 | 0.11 | 0.82 | 0.40 |
| `expressjs/express` | 0.02 | 0.02 | 0.05 | 0.14 | 0.04 | 0.22 | 0.02 | 0.22 | 0.07 |

## 5. Natural Language vs Code Queries

| Repository | Type | P@5 | R@5 | MRR |
|---|---|---|---|---|
| `nevernorbo/mean-flashcards` | natural_language | 0.35 | 0.82 | 0.40 |
| `nevernorbo/mean-flashcards` | code | 0.34 | 0.98 | 0.50 |
| `fastapi/fastapi` | natural_language | 0.21 | 0.78 | 0.41 |
| `fastapi/fastapi` | code | 0.22 | 0.86 | 0.39 |
| `expressjs/express` | natural_language | 0.06 | 0.32 | 0.11 |
| `expressjs/express` | code | 0.02 | 0.12 | 0.04 |

## 6. Index Type Comparison (Dense vs Sparse vs Hybrid)

| Repository | Index Type | P@5 | R@5 | MRR | Mean Latency (ms) |
|---|---|---|---|---|---|
| `nevernorbo/mean-flashcards` | dense | 0.35 | 0.90 | 0.47 | 62.31 |
| `nevernorbo/mean-flashcards` | sparse | 0.00 | 0.00 | 0.00 | 0.00 |
| `nevernorbo/mean-flashcards` | hybrid | 0.17 | 0.45 | 0.24 | 31.15 |
| `fastapi/fastapi` | dense | 0.22 | 0.82 | 0.41 | 80.11 |
| `fastapi/fastapi` | sparse | 0.00 | 0.00 | 0.00 | 0.00 |
| `fastapi/fastapi` | hybrid | 0.11 | 0.41 | 0.21 | 40.05 |
| `expressjs/express` | dense | 0.04 | 0.22 | 0.09 | 59.05 |
| `expressjs/express` | sparse | 0.00 | 0.00 | 0.00 | 0.00 |
| `expressjs/express` | hybrid | 0.02 | 0.11 | 0.04 | 29.52 |
