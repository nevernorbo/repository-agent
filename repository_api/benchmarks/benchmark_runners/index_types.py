"""
Benchmark 6: Index Type Comparison (Dense vs Hybrid)

Uses the actual API to compare retrieval quality and latency between
regular (dense) and hybrid indices.
"""
import asyncio
import json
import time
from typing import Any, Dict, List, Set

from benchmarks.config import (
    K_VALUES,
    REPOSITORIES,
    RESULTS_DIR,
)
from benchmarks.queries.mean_flashcards import ALL_QUERIES as MF_QUERIES
from benchmarks.queries.fastapi_queries import ALL_QUERIES as FA_QUERIES
from benchmarks.queries.express import ALL_QUERIES as EX_QUERIES
from benchmarks.ground_truth.mean_flashcards import GROUND_TRUTH as MF_GT
from benchmarks.ground_truth.fastapi_gt import GROUND_TRUTH as FA_GT
from benchmarks.ground_truth.express import GROUND_TRUTH as EX_GT
from benchmarks.utils.api_client import BenchmarkAPIClient

REPO_QUERIES = {
    "nevernorbo/mean-flashcards": MF_QUERIES,
    "fastapi/fastapi": FA_QUERIES,
    "expressjs/express": EX_QUERIES,
}

REPO_GT = {
    "nevernorbo/mean-flashcards": MF_GT,
    "fastapi/fastapi": FA_GT,
    "expressjs/express": EX_GT,
}


async def run_index_type_benchmark(
    repos: List[Dict[str, Any]] | None = None,
) -> List[Dict[str, Any]]:
    """Compare dense and hybrid index types using the actual API."""
    if repos is None:
        repos = REPOSITORIES

    client = BenchmarkAPIClient()
    all_results = []

    for repo in repos:
        repo_name = repo["name"]
        queries = REPO_QUERIES.get(repo_name, [])
        gt = REPO_GT.get(repo_name, {})
        if not queries:
            continue

        print(f"\nIndex type comparison: {repo_name}")

        # ── Dense baseline ──────────────────────────────────────────
        dense_metrics = await _evaluate_api(client, repo_name, queries, gt, mode="dense")

        # ── Hybrid ──────────────────────────────────────────────────
        hybrid_metrics = await _evaluate_api(client, repo_name, queries, gt, mode="hybrid")

        repo_result = {
            "repo_name": repo_name,
            "index_types": {
                "dense": dense_metrics.get("aggregate", {}),
                "hybrid": hybrid_metrics.get("aggregate", {}),
            },
        }
        all_results.append(repo_result)

    out_path = RESULTS_DIR / "index_type_results.json"
    with open(out_path, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nResults written to {out_path}")
    return all_results


async def _evaluate_api(
    client: BenchmarkAPIClient, repo_name: str, queries, gt: dict, mode: str
) -> Dict[str, Any]:
    """Evaluate retrieval quality using the specified mode (dense or hybrid)."""
    per_query = []
    for q in queries:
        gt_subs = gt.get(q.id, set())
        if not gt_subs:
            continue

        try:
            if mode == "hybrid":
                resp = await client.search_hybrid(q.text, repo_name)
            else:
                resp = await client.search(q.text, repo_name)
            
            results = resp.get("result", [])
            latency_ms = resp.get("_latency_ms", 0)
        except Exception as e:
            print(f"  Error searching ({mode}) for query {q.id}: {e}")
            results = []
            latency_ms = 0

        paths = []
        for item in results:
            # Extract file path (handles NLU and Code result shapes)
            ctx = item.get("context", {})
            fp = ctx.get("file_path") or item.get("file", "")
            if fp:
                paths.append(fp)

        metrics = _compute_query_metrics(paths, gt_subs)
        metrics["latency_ms"] = round(latency_ms, 2)
        per_query.append({"query_id": q.id, **metrics})

    return {"per_query": per_query, "aggregate": _aggregate_metrics(per_query)}


def _compute_query_metrics(paths: List[str], gt_subs: Set[str]) -> dict:
    """Compute P@K, R@K, MRR for a single query."""
    metrics = {}
    for k in K_VALUES:
        top_k = paths[:k]
        hits = sum(1 for p in top_k if any(s in p for s in gt_subs))
        metrics[f"precision_at_{k}"] = round(hits / k, 4) if k > 0 else 0
        metrics[f"recall_at_{k}"] = round(hits / len(gt_subs), 4) if gt_subs else 0

    mrr = 0.0
    for rank, p in enumerate(paths, 1):
        if any(s in p for s in gt_subs):
            mrr = 1.0 / rank
            break
    metrics["mrr"] = round(mrr, 4)
    return metrics


def _aggregate_metrics(per_query: List[dict]) -> dict:
    """Compute mean of all numeric metrics across queries."""
    if not per_query:
        return {}
    agg = {}
    # Use keys from first query to find metric names
    metric_keys = [k for k in per_query[0].keys() if k != "query_id"]
    for key in metric_keys:
        vals = [q.get(key, 0) for q in per_query]
        agg[f"mean_{key}"] = round(sum(vals) / len(vals), 4) if vals else 0
    return agg


async def main():
    await run_index_type_benchmark()


if __name__ == "__main__":
    asyncio.run(main())
