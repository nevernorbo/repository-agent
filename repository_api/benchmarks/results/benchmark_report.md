# Repository API — Benchmark Report

_Generated on 2026-04-20 08:04 UTC_

## 1. Indexing Performance

| Repository | Size Category | Files | LOC | Regular Indexing (s) | Hybrid Indexing (s) | Total Wall Clock (s) | Status |
|---|---|---|---|---|---|---|---|
| `nevernorbo/mean-flashcards` | small | 68 | 3627 | 11.12 | 10.93 | 26.14 | completed |
| `fastapi/fastapi` | large | 1123 | 107994 | 29.22 | 92.23 | 147.74 | completed |
| `expressjs/express` | medium | 141 | 21346 | 9.00 | 9.38 | 26.56 | completed |

## 2. Search Latency

| Repository | Queries | Mean (ms) | P50 (ms) | P90 (ms) | P99 (ms) |
|---|---|---|---|---|---|
| `nevernorbo/mean-flashcards` | 50 | 132.77 | 123.38 | 146.43 | 306.19 |
| `fastapi/fastapi` | 50 | 130.99 | 126.59 | 145.14 | 231.73 |
| `expressjs/express` | 50 | 124.17 | 124.08 | 136.46 | 155.46 |

## 3. Concurrency Performance

### `nevernorbo/mean-flashcards`

| Concurrency | Mean Latency (ms) | Throughput (qps) | Errors |
|---|---|---|---|
| 1 | 118.72 | 7.63 | 0 |
| 2 | 210.62 | 6.50 | 0 |
| 5 | 326.72 | 9.14 | 0 |
| 10 | 374.77 | 16.02 | 0 |
| 20 | 532.52 | 21.80 | 0 |

### `fastapi/fastapi`

| Concurrency | Mean Latency (ms) | Throughput (qps) | Errors |
|---|---|---|---|
| 1 | 321.92 | 2.95 | 0 |
| 2 | 174.36 | 8.54 | 0 |
| 5 | 225.46 | 16.60 | 0 |
| 10 | 377.29 | 18.23 | 0 |
| 20 | 628.30 | 22.69 | 0 |

### `expressjs/express`

| Concurrency | Mean Latency (ms) | Throughput (qps) | Errors |
|---|---|---|---|
| 1 | 167.65 | 5.56 | 0 |
| 2 | 145.77 | 9.61 | 0 |
| 5 | 216.64 | 16.04 | 0 |
| 10 | 317.23 | 22.27 | 0 |
| 20 | 615.01 | 23.16 | 0 |


## 4. Retrieval Quality (All Queries)

| Repository | P@1 | R@1 | P@3 | R@3 | P@5 | R@5 | P@10 | R@10 | MRR |
|---|---|---|---|---|---|---|---|---|---|
| `nevernorbo/mean-flashcards` | 0.40 | 0.22 | 0.37 | 0.58 | 0.35 | 0.90 | 0.17 | 0.90 | 0.45 |
| `fastapi/fastapi` | 0.28 | 0.21 | 0.25 | 0.60 | 0.22 | 0.84 | 0.11 | 0.84 | 0.40 |
| `expressjs/express` | 0.02 | 0.02 | 0.05 | 0.14 | 0.04 | 0.22 | 0.02 | 0.22 | 0.07 |

## 5. Natural Language vs Code Queries

| Repository | Type | P@5 | R@5 | MRR |
|---|---|---|---|---|
| `nevernorbo/mean-flashcards` | natural_language | 0.35 | 0.82 | 0.40 |
| `nevernorbo/mean-flashcards` | code | 0.34 | 0.98 | 0.50 |
| `fastapi/fastapi` | natural_language | 0.22 | 0.82 | 0.42 |
| `fastapi/fastapi` | code | 0.22 | 0.86 | 0.39 |
| `expressjs/express` | natural_language | 0.06 | 0.32 | 0.11 |
| `expressjs/express` | code | 0.02 | 0.12 | 0.04 |

## 6. Index Type Comparison (Dense vs Sparse vs Hybrid)

| Repository | Index Type | P@5 | R@5 | MRR | Mean Latency (ms) |
|---|---|---|---|---|---|
| `nevernorbo/mean-flashcards` | dense | 0.35 | 0.90 | 0.45 | 133.29 |
| `nevernorbo/mean-flashcards` | hybrid | 0.32 | 0.82 | 0.41 | 140.39 |
| `fastapi/fastapi` | dense | 0.22 | 0.84 | 0.40 | 136.07 |
| `fastapi/fastapi` | hybrid | 0.22 | 0.88 | 0.38 | 148.46 |
| `expressjs/express` | dense | 0.04 | 0.22 | 0.07 | 136.31 |
| `expressjs/express` | hybrid | 0.06 | 0.26 | 0.14 | 133.05 |
