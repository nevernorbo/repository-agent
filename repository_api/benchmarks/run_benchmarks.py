"""
Benchmark orchestrator — CLI entry point for running all or specific benchmarks.

Usage:
    # Run all benchmarks
    python -m benchmarks.run_benchmarks --all

    # Run specific benchmarks
    python -m benchmarks.run_benchmarks --indexing --search

    # Run for specific repos only
    python -m benchmarks.run_benchmarks --all --repos fastapi/fastapi

    # Generate report from existing results
    python -m benchmarks.run_benchmarks --report-only
"""

import argparse
import asyncio
import sys
from typing import List, Optional

from benchmarks.config import REPOSITORIES


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Repository API benchmark suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Benchmark selectors
    parser.add_argument("--all", action="store_true", help="Run all benchmarks")
    parser.add_argument("--indexing", action="store_true", help="Run indexing benchmark (1)")
    parser.add_argument("--search", action="store_true", help="Run search latency benchmark (2)")
    parser.add_argument("--concurrency", action="store_true", help="Run concurrency benchmark (3)")
    parser.add_argument("--quality", action="store_true", help="Run retrieval quality benchmark (4)")
    parser.add_argument("--nl-vs-code", action="store_true", help="Run NL vs code comparison (5)")
    parser.add_argument("--index-types", action="store_true", help="Run index type comparison (6)")
    parser.add_argument("--report-only", action="store_true", help="Generate report from existing results")

    # Filters
    parser.add_argument(
        "--repos",
        nargs="+",
        default=None,
        help="Only run benchmarks on these repos (e.g. fastapi/fastapi expressjs/express)",
    )

    # Options
    parser.add_argument(
        "--api-url",
        default=None,
        help="Override API base URL (default: from config / env)",
    )

    return parser.parse_args()


def _filter_repos(repo_names: Optional[List[str]]) -> list:
    """Filter REPOSITORIES by name if --repos was specified."""
    if repo_names is None:
        return REPOSITORIES
    filtered = [r for r in REPOSITORIES if r["name"] in repo_names]
    if not filtered:
        print(f"WARNING: No matching repos found for {repo_names}")
        print(f"Available: {[r['name'] for r in REPOSITORIES]}")
    return filtered


async def run(args: argparse.Namespace):
    repos = _filter_repos(args.repos)

    # Override API URL if specified
    if args.api_url:
        import benchmarks.config as cfg
        cfg.API_BASE_URL = args.api_url

    from benchmarks.utils.api_client import BenchmarkAPIClient

    client = BenchmarkAPIClient()

    run_all = args.all
    quality_results = None

    # ── 1. Indexing ──────────────────────────────────────────────
    if run_all or args.indexing:
        print("\n" + "=" * 70)
        print("  BENCHMARK 1: Indexing Performance")
        print("=" * 70)
        from benchmarks.benchmark_runners.indexing import run_indexing_benchmark
        await run_indexing_benchmark(client, repos)

    # ── 2. Search Latency ────────────────────────────────────────
    if run_all or args.search:
        print("\n" + "=" * 70)
        print("  BENCHMARK 2: Search Latency")
        print("=" * 70)
        from benchmarks.benchmark_runners.search import run_search_benchmark
        await run_search_benchmark(client, repos)

    # ── 3. Concurrency ───────────────────────────────────────────
    if run_all or args.concurrency:
        print("\n" + "=" * 70)
        print("  BENCHMARK 3: Concurrency Performance")
        print("=" * 70)
        from benchmarks.benchmark_runners.concurrency import run_concurrency_benchmark
        await run_concurrency_benchmark(client, repos)

    # ── 4. Retrieval Quality ─────────────────────────────────────
    if run_all or args.quality:
        print("\n" + "=" * 70)
        print("  BENCHMARK 4: Retrieval Quality (P@K, R@K, MRR)")
        print("=" * 70)
        from benchmarks.benchmark_runners.retrieval_quality import run_retrieval_quality_benchmark
        quality_results = await run_retrieval_quality_benchmark(client, repos)

    # ── 5. NL vs Code ────────────────────────────────────────────
    if run_all or args.nl_vs_code:
        print("\n" + "=" * 70)
        print("  BENCHMARK 5: Natural Language vs Code Queries")
        print("=" * 70)
        from benchmarks.benchmark_runners.nl_vs_code import run_nl_vs_code_comparison
        run_nl_vs_code_comparison(quality_results)

    # ── 6. Index Types ───────────────────────────────────────────
    if run_all or args.index_types:
        print("\n" + "=" * 70)
        print("  BENCHMARK 6: Index Type Comparison")
        print("=" * 70)
        from benchmarks.benchmark_runners.index_types import run_index_type_benchmark
        await run_index_type_benchmark(repos)

    # ── Report ───────────────────────────────────────────────────
    if run_all or args.report_only:
        print("\n" + "=" * 70)
        print("  Generating Benchmark Report")
        print("=" * 70)
        from benchmarks.utils.reporting import generate_report
        generate_report()


def main():
    args = parse_args()

    # Ensure at least one action is selected
    actions = [
        args.all, args.indexing, args.search, args.concurrency,
        args.quality, args.nl_vs_code, args.index_types, args.report_only,
    ]
    if not any(actions):
        print("No benchmark selected. Use --all or pick specific benchmarks.")
        print("Run with --help for usage info.")
        sys.exit(1)

    asyncio.run(run(args))


if __name__ == "__main__":
    main()
