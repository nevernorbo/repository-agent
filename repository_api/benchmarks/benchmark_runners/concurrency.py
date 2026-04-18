"""
Benchmark 3: Concurrency Performance
Tests how the API handles multiple simultaneous search requests.
"""
import asyncio
import json
import statistics
import time
from typing import Any, Dict, List

from benchmarks.config import CONCURRENCY_LEVELS, REPOSITORIES, RESULTS_DIR
from benchmarks.queries.mean_flashcards import ALL_QUERIES as MF_QUERIES
from benchmarks.queries.fastapi_queries import ALL_QUERIES as FA_QUERIES
from benchmarks.queries.express import ALL_QUERIES as EX_QUERIES
from benchmarks.utils.api_client import BenchmarkAPIClient

REPO_QUERIES = {
    "nevernorbo/mean-flashcards": MF_QUERIES,
    "fastapi/fastapi": FA_QUERIES,
    "expressjs/express": EX_QUERIES,
}


async def _single_search(client: BenchmarkAPIClient, query_text: str, repo_name: str) -> Dict:
    """Execute a single search and return latency + success info."""
    try:
        resp = await client.search(query_text, repo_name)
        return {"latency_ms": resp.get("_latency_ms", 0), "error": False}
    except Exception as e:
        return {"latency_ms": 0, "error": True, "error_msg": str(e)}


async def run_concurrency_benchmark(
    client: BenchmarkAPIClient,
    repos: List[Dict[str, Any]] | None = None,
    levels: List[int] | None = None,
) -> List[Dict[str, Any]]:
    if repos is None:
        repos = REPOSITORIES
    if levels is None:
        levels = CONCURRENCY_LEVELS

    all_results = []
    for repo in repos:
        repo_name = repo["name"]
        queries = REPO_QUERIES.get(repo_name, [])
        if not queries:
            continue

        print(f"\nConcurrency test: {repo_name}")
        level_results = []

        for n in levels:
            # Pick first n queries (cycling if needed)
            batch = [queries[i % len(queries)] for i in range(n)]

            start = time.monotonic()
            tasks = [_single_search(client, q.text, repo_name) for q in batch]
            responses = await asyncio.gather(*tasks)
            wall_time = time.monotonic() - start

            latencies = [r["latency_ms"] for r in responses if not r["error"]]
            error_count = sum(1 for r in responses if r["error"])
            mean_lat = round(statistics.mean(latencies), 2) if latencies else 0
            throughput = round(len(latencies) / wall_time, 2) if wall_time > 0 else 0

            print(f"  n={n:>3}  mean_lat={mean_lat:>8.1f}ms  qps={throughput:>6.1f}  errors={error_count}")

            level_results.append({
                "concurrency": n,
                "mean_latency_ms": mean_lat,
                "throughput_qps": throughput,
                "error_count": error_count,
                "wall_time_s": round(wall_time, 3),
            })

        all_results.append({
            "repo_name": repo_name,
            "levels": level_results,
        })

    out_path = RESULTS_DIR / "concurrency_results.json"
    with open(out_path, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nResults written to {out_path}")
    return all_results


async def main():
    client = BenchmarkAPIClient()
    await run_concurrency_benchmark(client)


if __name__ == "__main__":
    asyncio.run(main())
