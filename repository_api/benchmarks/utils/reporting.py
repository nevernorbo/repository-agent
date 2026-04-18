"""
Report generator — converts raw benchmark JSON results into a Markdown report.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from benchmarks.config import K_VALUES, RESULTS_DIR


def _load_json(filename: str) -> Optional[Dict[str, Any]]:
    """Load a JSON file from the results directory, returning None on failure."""
    path = RESULTS_DIR / filename
    if not path.exists():
        return None
    with open(path, "r") as f:
        return json.load(f)


def _fmt(value: float, decimals: int = 2) -> str:
    """Format a float for table display."""
    if value is None:
        return "—"
    return f"{value:.{decimals}f}"


# ======================================================================
# Section renderers
# ======================================================================


def _render_indexing(data: List[Dict]) -> str:
    """Render the indexing performance table."""
    lines = [
        "## 1. Indexing Performance\n",
        "| Repository | Size Category | Files | LOC | Indexing Time (s) | Status |",
        "|---|---|---|---|---|---|",
    ]
    for entry in data:
        lines.append(
            f"| `{entry['repo_name']}` "
            f"| {entry.get('size_category', '—')} "
            f"| {entry.get('file_count', '—')} "
            f"| {entry.get('loc', '—')} "
            f"| {_fmt(entry.get('total_indexing_time_s', 0))} "
            f"| {entry.get('status', '—')} |"
        )
    return "\n".join(lines) + "\n"


def _render_search_latency(data: List[Dict]) -> str:
    """Render the search latency summary table."""
    lines = [
        "## 2. Search Latency\n",
        "| Repository | Queries | Mean (ms) | P50 (ms) | P90 (ms) | P99 (ms) |",
        "|---|---|---|---|---|---|",
    ]
    for entry in data:
        s = entry.get("summary", {})
        lines.append(
            f"| `{entry['repo_name']}` "
            f"| {len(entry.get('queries', []))} "
            f"| {_fmt(s.get('mean_ms', 0))} "
            f"| {_fmt(s.get('p50_ms', 0))} "
            f"| {_fmt(s.get('p90_ms', 0))} "
            f"| {_fmt(s.get('p99_ms', 0))} |"
        )
    return "\n".join(lines) + "\n"


def _render_concurrency(data: List[Dict]) -> str:
    """Render the concurrency test table."""
    lines = [
        "## 3. Concurrency Performance\n",
    ]
    for entry in data:
        lines.append(f"### `{entry['repo_name']}`\n")
        lines.append(
            "| Concurrency | Mean Latency (ms) | Throughput (qps) | Errors |"
        )
        lines.append("|---|---|---|---|")
        for level in entry.get("levels", []):
            lines.append(
                f"| {level['concurrency']} "
                f"| {_fmt(level.get('mean_latency_ms', 0))} "
                f"| {_fmt(level.get('throughput_qps', 0))} "
                f"| {level.get('error_count', 0)} |"
            )
        lines.append("")
    return "\n".join(lines) + "\n"


def _render_retrieval_quality(data: List[Dict]) -> str:
    """Render the retrieval quality metrics table."""
    lines = [
        "## 4. Retrieval Quality (All Queries)\n",
    ]

    # Build header dynamically from K_VALUES
    header_cols = ["Repository"]
    for k in K_VALUES:
        header_cols.extend([f"P@{k}", f"R@{k}"])
    header_cols.append("MRR")
    lines.append("| " + " | ".join(header_cols) + " |")
    lines.append("|" + "---|" * len(header_cols))

    for entry in data:
        agg = entry.get("aggregate", {})
        row = [f"`{entry['repo_name']}`"]
        for k in K_VALUES:
            row.append(_fmt(agg.get(f"mean_precision_at_{k}", 0)))
            row.append(_fmt(agg.get(f"mean_recall_at_{k}", 0)))
        row.append(_fmt(agg.get("mean_mrr", 0)))
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines) + "\n"


def _render_nl_vs_code(data: List[Dict]) -> str:
    """Render the NL vs Code comparison table."""
    lines = [
        "## 5. Natural Language vs Code Queries\n",
        "| Repository | Type | P@5 | R@5 | MRR |",
        "|---|---|---|---|---|",
    ]
    for entry in data:
        for qtype in ("natural_language", "code"):
            m = entry.get(qtype, {})
            lines.append(
                f"| `{entry['repo_name']}` "
                f"| {qtype} "
                f"| {_fmt(m.get('mean_precision_at_5', 0))} "
                f"| {_fmt(m.get('mean_recall_at_5', 0))} "
                f"| {_fmt(m.get('mean_mrr', 0))} |"
            )
    return "\n".join(lines) + "\n"


def _render_index_types(data: List[Dict]) -> str:
    """Render the index type comparison table."""
    lines = [
        "## 6. Index Type Comparison (Dense vs Sparse vs Hybrid)\n",
        "| Repository | Index Type | P@5 | R@5 | MRR | Mean Latency (ms) |",
        "|---|---|---|---|---|---|",
    ]
    for entry in data:
        for idx_type in entry.get("index_types", {}):
            m = entry["index_types"][idx_type]
            lines.append(
                f"| `{entry['repo_name']}` "
                f"| {idx_type} "
                f"| {_fmt(m.get('mean_precision_at_5', 0))} "
                f"| {_fmt(m.get('mean_recall_at_5', 0))} "
                f"| {_fmt(m.get('mean_mrr', 0))} "
                f"| {_fmt(m.get('mean_latency_ms', 0))} |"
            )
    return "\n".join(lines) + "\n"


# ======================================================================
# Public API
# ======================================================================


def generate_report(output_path: Optional[Path] = None) -> str:
    """Aggregate all result JSON files and produce a Markdown report.

    Args:
        output_path: Where to write the report.  Defaults to
            ``RESULTS_DIR / "benchmark_report.md"``.

    Returns:
        The full Markdown report as a string.
    """
    if output_path is None:
        output_path = RESULTS_DIR / "benchmark_report.md"

    sections = [
        f"# Repository API — Benchmark Report\n",
        f"_Generated on {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}_\n",
    ]

    # 1. Indexing
    indexing = _load_json("indexing_results.json")
    if indexing:
        sections.append(_render_indexing(indexing))

    # 2. Search latency
    search = _load_json("search_results.json")
    if search:
        sections.append(_render_search_latency(search))

    # 3. Concurrency
    concurrency = _load_json("concurrency_results.json")
    if concurrency:
        sections.append(_render_concurrency(concurrency))

    # 4. Retrieval quality
    quality = _load_json("retrieval_quality_results.json")
    if quality:
        sections.append(_render_retrieval_quality(quality))

    # 5. NL vs Code
    nl_code = _load_json("nl_vs_code_results.json")
    if nl_code:
        sections.append(_render_nl_vs_code(nl_code))

    # 6. Index types
    idx_types = _load_json("index_type_results.json")
    if idx_types:
        sections.append(_render_index_types(idx_types))

    report = "\n".join(sections)

    with open(output_path, "w") as f:
        f.write(report)

    print(f"Report written to {output_path}")
    return report
