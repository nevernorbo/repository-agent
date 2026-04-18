"""
Benchmark 4: Retrieval Quality
Computes Precision@K, Recall@K, and MRR for each query against ground truth.
"""
import asyncio
import json
from typing import Any, Dict, List, Set

from benchmarks.config import K_VALUES, REPOSITORIES, RESULTS_DIR
from benchmarks.queries.mean_flashcards import ALL_QUERIES as MF_QUERIES
from benchmarks.queries.fastapi_queries import ALL_QUERIES as FA_QUERIES
from benchmarks.queries.express import ALL_QUERIES as EX_QUERIES
from benchmarks.ground_truth.mean_flashcards import GROUND_TRUTH as MF_GT
from benchmarks.ground_truth.fastapi_gt import GROUND_TRUTH as FA_GT
from benchmarks.ground_truth.express import GROUND_TRUTH as EX_GT
from benchmarks.utils.api_client import BenchmarkAPIClient
from benchmarks.utils.metrics import compute_all_metrics

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


def _extract_file_paths(search_result: List[dict]) -> List[str]:
    """Extract file paths from search results (handles both NLU and code result shapes)."""
    paths = []
    for item in search_result:
        # NLU results have context.file_path
        ctx = item.get("context", {})
        if ctx and ctx.get("file_path"):
            paths.append(ctx["file_path"])
        # Code results have 'file'
        elif item.get("file"):
            paths.append(item["file"])
    return paths


def _match_against_ground_truth(retrieved_paths: List[str], gt_substrings: Set[str]) -> List[str]:
    """Check which retrieved paths match any ground truth substring.
    Returns a list of 'relevant'/'not_relevant' in order, for metric computation.
    """
    result_ids = []
    for path in retrieved_paths:
        if any(sub in path for sub in gt_substrings):
            result_ids.append(path)  # counts as relevant
        else:
            result_ids.append(f"__irrelevant__{path}")
    return result_ids


async def run_retrieval_quality_benchmark(
    client: BenchmarkAPIClient,
    repos: List[Dict[str, Any]] | None = None,
) -> List[Dict[str, Any]]:
    if repos is None:
        repos = REPOSITORIES

    all_results = []
    for repo in repos:
        repo_name = repo["name"]
        queries = REPO_QUERIES.get(repo_name, [])
        gt = REPO_GT.get(repo_name, {})
        if not queries:
            continue

        print(f"\nRetrieval quality: {repo_name}")
        per_query = []

        for q in queries:
            resp = await client.search(q.text, repo_name)
            search_results = resp.get("result", [])
            retrieved_paths = _extract_file_paths(search_results)

            gt_substrings = gt.get(q.id, set())
            if not gt_substrings:
                # Skip queries without ground truth
                continue

            # Build relevant set from retrieved paths that match GT
            relevant_set = set()
            for path in retrieved_paths:
                if any(sub in path for sub in gt_substrings):
                    relevant_set.add(path)
            # Also include GT substrings as "ideal" relevant items
            # (for recall computation: we treat matched paths as relevant)

            metrics = compute_all_metrics(retrieved_paths, relevant_set, K_VALUES)
            # Re-compute with substring matching for proper recall
            # relevant_set is what was actually found; for recall denominator
            # we use the number of GT patterns as a proxy
            for k in K_VALUES:
                top_k = retrieved_paths[:k]
                hits = sum(1 for p in top_k if any(s in p for s in gt_substrings))
                metrics[f"precision_at_{k}"] = round(hits / k, 4) if k > 0 else 0
                metrics[f"recall_at_{k}"] = round(hits / len(gt_substrings), 4) if gt_substrings else 0

            # MRR: rank of first relevant result
            mrr = 0.0
            for rank, path in enumerate(retrieved_paths, 1):
                if any(s in path for s in gt_substrings):
                    mrr = 1.0 / rank
                    break
            metrics["mrr"] = round(mrr, 4)

            per_query.append({"query_id": q.id, "query_type": q.query_type, **metrics})

        # Aggregate
        aggregate = {}
        if per_query:
            for key in per_query[0]:
                if key in ("query_id", "query_type"):
                    continue
                vals = [pq[key] for pq in per_query]
                aggregate[f"mean_{key}"] = round(sum(vals) / len(vals), 4)

        print(f"  Queries evaluated: {len(per_query)}")
        if aggregate:
            print(f"  MRR={aggregate.get('mean_mrr', 0):.3f}  P@5={aggregate.get('mean_precision_at_5', 0):.3f}")

        all_results.append({
            "repo_name": repo_name,
            "per_query": per_query,
            "aggregate": aggregate,
        })

    out_path = RESULTS_DIR / "retrieval_quality_results.json"
    with open(out_path, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nResults written to {out_path}")
    return all_results


async def main():
    client = BenchmarkAPIClient()
    await run_retrieval_quality_benchmark(client)


if __name__ == "__main__":
    asyncio.run(main())
