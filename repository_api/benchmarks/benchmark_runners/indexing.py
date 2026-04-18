"""
Benchmark 1: Indexing Performance
Measures end-to-end time to index each repository via the API.
"""
import asyncio
import json
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List

from benchmarks.config import REPOSITORIES, RESULTS_DIR
from benchmarks.utils.api_client import BenchmarkAPIClient


def _count_repo_stats(repo_path: str) -> Dict[str, int]:
    """Count files and lines of code in a cloned repo (best-effort)."""
    p = Path(repo_path)
    if not p.exists():
        return {"file_count": 0, "loc": 0}
    file_count = 0
    loc = 0
    for f in p.rglob("*"):
        if f.is_file() and f.suffix in {".py", ".js", ".jsx", ".ts", ".tsx", ".cs"}:
            file_count += 1
            try:
                loc += sum(1 for _ in f.open("r", encoding="utf-8", errors="ignore"))
            except Exception:
                pass
    return {"file_count": file_count, "loc": loc}


async def run_indexing_benchmark(
    client: BenchmarkAPIClient,
    repos: List[Dict[str, Any]] | None = None,
) -> List[Dict[str, Any]]:
    """Index each repository and measure wall-clock time.

    Returns a list of result dicts, one per repo.
    """
    if repos is None:
        repos = REPOSITORIES

    results = []
    for repo in repos:
        repo_name = repo["name"]
        print(f"\n{'='*60}")
        print(f"Indexing: {repo_name}")
        print(f"{'='*60}")

        start = time.monotonic()
        try:
            await client.index_repository(repo_name)
            outcome = await client.wait_for_indexing(repo_name)
            elapsed = time.monotonic() - start
            status = outcome["status"]
        except Exception as e:
            elapsed = time.monotonic() - start
            status = f"error: {e}"

        result = {
            "repo_name": repo_name,
            "size_category": repo.get("size_category", "unknown"),
            "total_indexing_time_s": round(elapsed, 2),
            "status": status,
            # file_count / loc will be 0 unless we clone locally too
            "file_count": 0,
            "loc": 0,
        }
        print(f"  Status: {status} | Time: {elapsed:.1f}s")
        results.append(result)

    # Persist
    out_path = RESULTS_DIR / "indexing_results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults written to {out_path}")
    return results


async def main():
    client = BenchmarkAPIClient()
    await run_indexing_benchmark(client)


if __name__ == "__main__":
    asyncio.run(main())
