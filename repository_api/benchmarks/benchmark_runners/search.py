"""
Benchmark 2: Search Latency
Measures per-query latency with summary percentile statistics.
"""
import asyncio
import json
import statistics
from typing import Any, Dict, List

from benchmarks.config import REPOSITORIES, RESULTS_DIR
from benchmarks.queries.mean_flashcards import ALL_QUERIES as MF_QUERIES
from benchmarks.queries.fastapi_queries import ALL_QUERIES as FA_QUERIES
from benchmarks.queries.express import ALL_QUERIES as EX_QUERIES
from benchmarks.utils.api_client import BenchmarkAPIClient

REPO_QUERIES = {
    "nevernorbo/mean-flashcards": MF_QUERIES,
    "fastapi/fastapi": FA_QUERIES,
    "expressjs/express": EX_QUERIES,
}


def _percentile(data: List[float], p: float) -> float:
    """Simple percentile without numpy."""
    if not data:
        return 0.0
    sorted_data = sorted(data)
    k = (len(sorted_data) - 1) * (p / 100)
    f = int(k)
    c = f + 1 if f + 1 < len(sorted_data) else f
    d = k - f
    return sorted_data[f] + d * (sorted_data[c] - sorted_data[f])


async def run_search_benchmark(
    client: BenchmarkAPIClient,
    repos: List[Dict[str, Any]] | None = None,
) -> List[Dict[str, Any]]:
    if repos is None:
        repos = REPOSITORIES

    all_results = []
    for repo in repos:
        repo_name = repo["name"]
        queries = REPO_QUERIES.get(repo_name, [])
        if not queries:
            continue

        print(f"\nSearching in: {repo_name} ({len(queries)} queries)")
        query_results = []
        for q in queries:
            resp = await client.search(q.text, repo_name)
            latency = resp.get("_latency_ms", 0)
            result_items = resp.get("result", [])
            query_results.append({
                "query_id": q.id,
                "query": q.text,
                "query_type": q.query_type,
                "latency_ms": latency,
                "result_count": len(result_items),
            })

        latencies = [r["latency_ms"] for r in query_results]
        summary = {
            "mean_ms": round(statistics.mean(latencies), 2) if latencies else 0,
            "p50_ms": round(_percentile(latencies, 50), 2),
            "p90_ms": round(_percentile(latencies, 90), 2),
            "p99_ms": round(_percentile(latencies, 99), 2),
        }
        print(f"  mean={summary['mean_ms']}ms  p50={summary['p50_ms']}ms  p90={summary['p90_ms']}ms")

        all_results.append({
            "repo_name": repo_name,
            "queries": query_results,
            "summary": summary,
        })

    out_path = RESULTS_DIR / "search_results.json"
    with open(out_path, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nResults written to {out_path}")
    return all_results


async def main():
    client = BenchmarkAPIClient()
    await run_search_benchmark(client)


if __name__ == "__main__":
    asyncio.run(main())
