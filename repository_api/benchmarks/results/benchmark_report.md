# Repository API — Benchmark Report

_Generated on 2026-04-19 08:23 UTC_

## 1. Indexing Performance

| Repository | Size Category | Files | LOC | Regular Indexing (s) | Hybrid Indexing (s) | Total Wall Clock (s) | Status |
|---|---|---|---|---|---|---|---|
| `nevernorbo/mean-flashcards` | small | 68 | 3627 | 13.13 | 11.99 | 31.25 | completed |
| `fastapi/fastapi` | large | 1123 | 107994 | 31.15 | 96.79 | 160.00 | completed |
| `expressjs/express` | medium | 141 | 21346 | 9.36 | 9.49 | 25.71 | completed |

## 2. Search Latency

| Repository | Queries | Mean (ms) | P50 (ms) | P90 (ms) | P99 (ms) |
|---|---|---|---|---|---|
| `nevernorbo/mean-flashcards` | 50 | 132.39 | 119.03 | 139.60 | 361.43 |
| `fastapi/fastapi` | 50 | 138.25 | 127.57 | 148.57 | 356.79 |
| `expressjs/express` | 50 | 125.19 | 123.89 | 143.12 | 152.00 |

## 3. Concurrency Performance

### `nevernorbo/mean-flashcards`

| Concurrency | Mean Latency (ms) | Throughput (qps) | Errors |
|---|---|---|---|
| 1 | 115.01 | 7.61 | 0 |
| 2 | 186.26 | 7.48 | 0 |
| 5 | 340.48 | 8.98 | 0 |
| 10 | 415.23 | 15.70 | 0 |
| 20 | 594.23 | 20.27 | 0 |

### `fastapi/fastapi`

| Concurrency | Mean Latency (ms) | Throughput (qps) | Errors |
|---|---|---|---|
| 1 | 297.31 | 3.03 | 0 |
| 2 | 244.69 | 6.09 | 0 |
| 5 | 235.98 | 13.67 | 0 |
| 10 | 319.15 | 21.69 | 0 |
| 20 | 587.04 | 19.19 | 0 |

### `expressjs/express`

| Concurrency | Mean Latency (ms) | Throughput (qps) | Errors |
|---|---|---|---|
| 1 | 136.15 | 6.61 | 0 |
| 2 | 129.67 | 11.87 | 0 |
| 5 | 221.77 | 15.93 | 0 |
| 10 | 336.28 | 20.41 | 0 |
| 20 | 544.90 | 22.84 | 0 |


## 4. Retrieval Quality (All Queries)

| Repository | P@1 | R@1 | P@3 | R@3 | P@5 | R@5 | P@10 | R@10 | MRR |
|---|---|---|---|---|---|---|---|---|---|
| `nevernorbo/mean-flashcards` | 0.40 | 0.22 | 0.37 | 0.58 | 0.35 | 0.90 | 0.17 | 0.90 | 0.45 |
| `fastapi/fastapi` | 0.28 | 0.21 | 0.25 | 0.58 | 0.22 | 0.84 | 0.11 | 0.84 | 0.40 |
| `expressjs/express` | 0.02 | 0.02 | 0.04 | 0.12 | 0.04 | 0.22 | 0.02 | 0.22 | 0.07 |

## 5. Natural Language vs Code Queries

| Repository | Type | P@5 | R@5 | MRR |
|---|---|---|---|---|
| `nevernorbo/mean-flashcards` | natural_language | 0.35 | 0.82 | 0.40 |
| `nevernorbo/mean-flashcards` | code | 0.34 | 0.98 | 0.50 |
| `fastapi/fastapi` | natural_language | 0.22 | 0.82 | 0.41 |
| `fastapi/fastapi` | code | 0.22 | 0.86 | 0.39 |
| `expressjs/express` | natural_language | 0.06 | 0.32 | 0.11 |
| `expressjs/express` | code | 0.02 | 0.12 | 0.04 |

## 6. Index Type Comparison (Dense vs Sparse vs Hybrid)

| Repository | Index Type | P@5 | R@5 | MRR | Mean Latency (ms) |
|---|---|---|---|---|---|
| `nevernorbo/mean-flashcards` | dense | 0.35 | 0.90 | 0.47 | 57.50 |
| `nevernorbo/mean-flashcards` | hybrid | 0.17 | 0.45 | 0.24 | 28.75 |
| `fastapi/fastapi` | dense | 0.22 | 0.84 | 0.41 | 73.96 |
| `fastapi/fastapi` | hybrid | 0.11 | 0.42 | 0.21 | 36.98 |
| `expressjs/express` | dense | 0.04 | 0.22 | 0.09 | 56.55 |
| `expressjs/express` | hybrid | 0.02 | 0.11 | 0.04 | 28.27 |
