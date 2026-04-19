"""
Reporter: Renders benchmark results to the terminal and exports to JSON + CSV.

Uses `rich` for styled console output with graceful fallback to plain text
if rich is not installed.
"""

import csv
import json
import os
from datetime import datetime, timezone

from benchmarks.config import CATEGORIES, RESULTS_DIR
from benchmarks.evaluator import ModelMetrics
from benchmarks.runner import RunResult

# ── Rich import with fallback ─────────────────────────────────────────────────
try:
    from rich.console import Console
    from rich.table import Table
    from rich import box
    _RICH = True
    console = Console()
except ImportError:
    _RICH = False
    console = None  # type: ignore[assignment]


# ── Terminal output ───────────────────────────────────────────────────────────

def _print(msg: str) -> None:
    if _RICH:
        console.print(msg)
    else:
        print(msg)


def print_model_summary(metrics: ModelMetrics) -> None:
    """Print a one-line accuracy summary for a model."""
    pct = f"{metrics.accuracy * 100:.1f}%"
    strict_pct = f"{metrics.strict_accuracy * 100:.1f}%"
    _print(
        f"[bold cyan]{metrics.model}[/bold cyan]  "
        f"Overall: [bold]{pct}[/bold] ({metrics.correct}/{metrics.total})  "
        f"Strict (non-ambiguous): [bold]{strict_pct}[/bold]  "
        f"Avg latency: {metrics.avg_latency:.2f}s  "
        f"Errors: {metrics.error_count}  "
        f"Hallucinations: {len(metrics.hallucination_flags)}"
        if _RICH else
        f"{metrics.model}  Overall: {pct} ({metrics.correct}/{metrics.total})  "
        f"Strict: {strict_pct}  Avg latency: {metrics.avg_latency:.2f}s  "
        f"Errors: {metrics.error_count}  Hallucinations: {len(metrics.hallucination_flags)}"
    )


def print_accuracy_table(all_metrics: dict[str, ModelMetrics]) -> None:
    """Print a comparative accuracy table across all models."""
    if _RICH:
        table = Table(title="Routing Accuracy by Model & Category", box=box.ROUNDED)
        table.add_column("Model", style="cyan", no_wrap=True)
        table.add_column("Overall", justify="right")
        table.add_column("Strict", justify="right")
        for cat in CATEGORIES:
            table.add_column(cat.capitalize(), justify="right")
        table.add_column("Hallucinations", justify="right")
        table.add_column("Avg Latency", justify="right")

        for model, m in all_metrics.items():
            row = [
                model,
                f"{m.accuracy * 100:.1f}%",
                f"{m.strict_accuracy * 100:.1f}%",
                *[f"{m.category_metrics[c].accuracy * 100:.1f}%" for c in CATEGORIES],
                str(len(m.hallucination_flags)),
                f"{m.avg_latency:.2f}s",
            ]
            table.add_row(*row)

        console.print(table)
    else:
        header = ["Model", "Overall", "Strict"] + [c.capitalize() for c in CATEGORIES] + ["Halluc", "Latency"]
        print("  ".join(f"{h:<30}" if i == 0 else f"{h:>10}" for i, h in enumerate(header)))
        for model, m in all_metrics.items():
            row = (
                [model, f"{m.accuracy * 100:.1f}%", f"{m.strict_accuracy * 100:.1f}%"]
                + [f"{m.category_metrics[c].accuracy * 100:.1f}%" for c in CATEGORIES]
                + [str(len(m.hallucination_flags)), f"{m.avg_latency:.2f}s"]
            )
            print("  ".join(f"{v:<30}" if i == 0 else f"{v:>10}" for i, v in enumerate(row)))


def print_confusion_matrix(metrics: ModelMetrics) -> None:
    """Print the confusion matrix for one model."""
    if _RICH:
        table = Table(title=f"Confusion Matrix — {metrics.model}", box=box.SIMPLE)
        table.add_column("Expected \\ Routed", style="bold")
        for cat in CATEGORIES:
            table.add_column(cat.capitalize(), justify="right")
        table.add_column("unknown", justify="right")

        for expected in CATEGORIES:
            row_data = [expected]
            for routed in CATEGORIES + ["unknown"]:
                count = metrics.confusion_matrix.get(expected, {}).get(routed, 0)
                cell = str(count)
                # Highlight diagonal (correct)
                if routed == expected and count > 0:
                    cell = f"[green]{count}[/green]"
                elif count > 0:
                    cell = f"[red]{count}[/red]"
                row_data.append(cell)
            table.add_row(*row_data)

        console.print(table)
    else:
        headers = ["Expected"] + [c[:10] for c in CATEGORIES] + ["unknown"]
        print("  ".join(f"{h:>12}" for h in headers))
        for expected in CATEGORIES:
            row = [expected] + [
                str(metrics.confusion_matrix.get(expected, {}).get(routed, 0))
                for routed in CATEGORIES + ["unknown"]
            ]
            print("  ".join(f"{v:>12}" for v in row))


def print_hallucinations(metrics: ModelMetrics) -> None:
    """Print prompts where the classifier's reasoning contradicted its routing."""
    if not metrics.hallucination_flags:
        _print(f"[green]No hallucinated reasoning detected for {metrics.model}.[/green]"
               if _RICH else f"No hallucinations for {metrics.model}.")
        return

    _print(f"\n[bold yellow]Hallucinated Reasoning — {metrics.model}[/bold yellow]"
           if _RICH else f"\nHallucinations — {metrics.model}")
    for r in metrics.hallucination_flags:
        _print(f"  Prompt   : {r.prompt[:80]}" + ("..." if len(r.prompt) > 80 else ""))
        _print(f"  Expected : {r.expected_category}  →  Routed: {r.routed_category or 'unknown'}")
        _print(f"  Reasoning: {r.classifier_reasoning[:200]}" + ("..." if len(r.classifier_reasoning) > 200 else ""))
        _print("")


def print_misclassifications(metrics: ModelMetrics) -> None:
    """Print individual prompts that were routed incorrectly."""
    wrong = [r for r in metrics.results if not r.correct]
    if not wrong:
        _print(f"[green]All prompts correctly routed for {metrics.model}![/green]"
               if _RICH else f"All correct for {metrics.model}!")
        return

    _print(f"\n[bold red]Misclassifications — {metrics.model} ({len(wrong)} / {metrics.total})[/bold red]"
           if _RICH else f"\nMisclassifications — {metrics.model} ({len(wrong)} / {metrics.total})")
    for r in wrong:
        ambig = " [ambiguous]" if r.is_ambiguous else ""
        _print(
            f"  [{r.expected_category}→{r.routed_category or 'unknown'}]{ambig}  {r.prompt[:80]}"
            + ("..." if len(r.prompt) > 80 else "")
        )


# ── File export ───────────────────────────────────────────────────────────────

def _ensure_results_dir() -> str:
    os.makedirs(RESULTS_DIR, exist_ok=True)
    return RESULTS_DIR


def _timestamp() -> str:
    return datetime.now(tz=timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def export_json(
    all_metrics: dict[str, ModelMetrics],
    model_results: dict[str, list[RunResult]],
) -> str:
    """Export full results to JSON. Returns the file path."""
    ts = _timestamp()
    path = os.path.join(_ensure_results_dir(), f"{ts}_results.json")

    payload: dict = {"timestamp": ts, "models": {}}

    for model, metrics in all_metrics.items():
        payload["models"][model] = {
            "summary": {
                "accuracy": round(metrics.accuracy, 4),
                "strict_accuracy": round(metrics.strict_accuracy, 4),
                "correct": metrics.correct,
                "total": metrics.total,
                "error_count": metrics.error_count,
                "avg_latency_seconds": round(metrics.avg_latency, 4),
                "hallucination_count": len(metrics.hallucination_flags),
            },
            "category_accuracy": {
                cat: {
                    "accuracy": round(cm.accuracy, 4),
                    "strict_accuracy": round(cm.strict_accuracy, 4),
                    "correct": cm.correct,
                    "total": cm.total,
                }
                for cat, cm in metrics.category_metrics.items()
            },
            "confusion_matrix": metrics.confusion_matrix,
            "results": [
                {
                    "prompt": r.prompt,
                    "expected_category": r.expected_category,
                    "is_ambiguous": r.is_ambiguous,
                    "routed_agent": r.routed_agent,
                    "routed_category": r.routed_category,
                    "correct": r.correct,
                    "latency_seconds": round(r.latency_seconds, 4),
                    "classifier_reasoning": r.classifier_reasoning,
                    "error": r.error,
                }
                for r in model_results[model]
            ],
        }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    return path


def export_csv(
    all_metrics: dict[str, ModelMetrics],
    model_results: dict[str, list[RunResult]],
) -> str:
    """Export per-prompt results to CSV. Returns the file path."""
    ts = _timestamp()
    path = os.path.join(_ensure_results_dir(), f"{ts}_results.csv")

    fieldnames = [
        "model",
        "prompt",
        "expected_category",
        "routed_category",
        "correct",
        "is_ambiguous",
        "latency_seconds",
        "hallucination",
        "error",
    ]

    hallucination_prompts = {
        model: {r.prompt for r in metrics.hallucination_flags}
        for model, metrics in all_metrics.items()
    }

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for model, results in model_results.items():
            for r in results:
                writer.writerow({
                    "model": model,
                    "prompt": r.prompt,
                    "expected_category": r.expected_category,
                    "routed_category": r.routed_category or "unknown",
                    "correct": r.correct,
                    "is_ambiguous": r.is_ambiguous,
                    "latency_seconds": round(r.latency_seconds, 4),
                    "hallucination": r.prompt in hallucination_prompts.get(model, set()),
                    "error": r.error or "",
                })

    return path


def print_full_report(
    all_metrics: dict[str, ModelMetrics],
    model_results: dict[str, list[RunResult]],
) -> tuple[str, str]:
    """
    Print the full benchmark report and export files.
    Returns (json_path, csv_path).
    """
    _print("\n" + "=" * 70)
    _print("[bold]CLASSIFIER ROUTING BENCHMARK RESULTS[/bold]" if _RICH else "CLASSIFIER ROUTING BENCHMARK RESULTS")
    _print("=" * 70 + "\n")

    print_accuracy_table(all_metrics)

    for model, metrics in all_metrics.items():
        _print(f"\n{'─' * 60}")
        print_confusion_matrix(metrics)
        print_misclassifications(metrics)
        print_hallucinations(metrics)

    json_path = export_json(all_metrics, model_results)
    csv_path = export_csv(all_metrics, model_results)

    _print(f"\n[bold green]Results saved:[/bold green]" if _RICH else "\nResults saved:")
    _print(f"  JSON: {json_path}")
    _print(f"  CSV:  {csv_path}")

    return json_path, csv_path
