"""
Benchmark 5: Natural Language vs Code Query Comparison
Splits retrieval quality results by query type and compares.
"""
import json
from pathlib import Path
from typing import Any, Dict, List

from benchmarks.config import K_VALUES, RESULTS_DIR


def run_nl_vs_code_comparison(
    quality_results: List[Dict[str, Any]] | None = None,
) -> List[Dict[str, Any]]:
    """Split the retrieval quality results by query_type and compare.

    If *quality_results* is None, reads from the saved JSON file.
    """
    if quality_results is None:
        path = RESULTS_DIR / "retrieval_quality_results.json"
        if not path.exists():
            print("ERROR: retrieval_quality_results.json not found. Run benchmark 4 first.")
            return []
        with open(path, "r") as f:
            quality_results = json.load(f)

    all_results = []
    for repo_data in quality_results:
        repo_name = repo_data["repo_name"]
        per_query = repo_data.get("per_query", [])

        nl_queries = [q for q in per_query if q.get("query_type") == "natural_language"]
        code_queries = [q for q in per_query if q.get("query_type") == "code"]

        def _aggregate(queries):
            if not queries:
                return {}
            agg = {}
            metric_keys = [k for k in queries[0] if k not in ("query_id", "query_type")]
            for key in metric_keys:
                vals = [q[key] for q in queries]
                agg[f"mean_{key}"] = round(sum(vals) / len(vals), 4)
            return agg

        nl_agg = _aggregate(nl_queries)
        code_agg = _aggregate(code_queries)

        # Compute deltas (code - NL)
        delta = {}
        for key in nl_agg:
            if key in code_agg:
                delta[key] = round(code_agg[key] - nl_agg[key], 4)

        print(f"\n{repo_name}")
        print(f"  NL   ({len(nl_queries):>2} queries): P@5={nl_agg.get('mean_precision_at_5', 0):.3f}  MRR={nl_agg.get('mean_mrr', 0):.3f}")
        print(f"  Code ({len(code_queries):>2} queries): P@5={code_agg.get('mean_precision_at_5', 0):.3f}  MRR={code_agg.get('mean_mrr', 0):.3f}")

        all_results.append({
            "repo_name": repo_name,
            "natural_language": nl_agg,
            "code": code_agg,
            "delta": delta,
            "nl_query_count": len(nl_queries),
            "code_query_count": len(code_queries),
        })

    out_path = RESULTS_DIR / "nl_vs_code_results.json"
    with open(out_path, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nResults written to {out_path}")
    return all_results


def main():
    run_nl_vs_code_comparison()


if __name__ == "__main__":
    main()
