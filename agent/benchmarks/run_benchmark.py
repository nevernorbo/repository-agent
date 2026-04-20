"""
Benchmark CLI entrypoint.

Usage:
    # Run all models, all prompts
    python -m benchmarks.run_benchmark

    # Run a specific model only
    python -m benchmarks.run_benchmark --model gemma-4-31b-it

    # Quick smoke test (first N prompts per model)
    python -m benchmarks.run_benchmark --max-prompts 4

    # Skip ambiguous prompts
    python -m benchmarks.run_benchmark --skip-ambiguous

    # Override inter-request delay (seconds)
    python -m benchmarks.run_benchmark --delay 2.0

    # Combine flags
    python -m benchmarks.run_benchmark --model gemini-3.1-flash-lite-preview --max-prompts 10 --skip-ambiguous
"""

import argparse
import asyncio
import os
import sys
from pathlib import Path

# ── Load .env from project root before any ADK/Google SDK imports ─────────────
# This ensures GOOGLE_API_KEY (and other vars) are in os.environ in time.
_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
try:
    from dotenv import load_dotenv
    if _ENV_PATH.exists():
        load_dotenv(dotenv_path=_ENV_PATH, override=False)
        print(f"[env] Loaded {_ENV_PATH}")
    else:
        print(f"[env] Warning: .env not found at {_ENV_PATH}", file=sys.stderr)
except ImportError:
    # Fallback: manual parse (no python-dotenv)
    if _ENV_PATH.exists():
        with open(_ENV_PATH) as _f:
            for _line in _f:
                _line = _line.strip()
                if _line and not _line.startswith("#") and "=" in _line:
                    _k, _, _v = _line.partition("=")
                    os.environ.setdefault(_k.strip(), _v.strip())
        print(f"[env] Loaded {_ENV_PATH} (manual fallback)")

if not os.environ.get("GOOGLE_API_KEY") and not os.environ.get("GOOGLE_CLOUD_PROJECT"):
    print(
        "[env] ERROR: GOOGLE_API_KEY is not set and no Vertex AI project found.\n"
        "      Add GOOGLE_API_KEY to your .env file or export it manually.",
        file=sys.stderr,
    )
    sys.exit(1)

from benchmarks.config import BENCHMARK_MODELS, REQUEST_DELAY_SECONDS
from benchmarks.dataset import DATASET, BenchmarkPrompt
from benchmarks.evaluator import evaluate_all
from benchmarks.reporter import print_full_report
from benchmarks.runner import RunResult, run_model_benchmark


# ── Progress callback ─────────────────────────────────────────────────────────

def _progress(model: str, idx: int, total: int, result: RunResult) -> None:
    status = "✓" if result.correct else "✗"
    err = f" [ERROR: {result.error[:60]}]" if result.error else ""
    routed = result.routed_category or "unknown"
    print(
        f"  [{idx:>3}/{total}] {status} "
        f"expected={result.expected_category:<14} "
        f"routed={routed:<14} "
        f"latency={result.latency_seconds:.2f}s"
        f"{err}"
    )


# ── Main ──────────────────────────────────────────────────────────────────────

async def _main(args: argparse.Namespace) -> None:
    # 1. Select models
    models = [args.model] if args.model else BENCHMARK_MODELS
    if args.model and args.model not in BENCHMARK_MODELS:
        print(
            f"Warning: '{args.model}' is not in the standard model list. "
            "Proceeding anyway.",
            file=sys.stderr,
        )

    # 2. Filter dataset
    prompts: list[BenchmarkPrompt] = list(DATASET)
    if args.skip_ambiguous:
        prompts = [p for p in prompts if not p.is_ambiguous]
    if args.max_prompts:
        prompts = prompts[: args.max_prompts]

    print(
        f"\nBenchmark configuration:\n"
        f"  Models  : {', '.join(models)}\n"
        f"  Prompts : {len(prompts)} "
        f"({'skip-ambiguous' if args.skip_ambiguous else 'include-ambiguous'})\n"
        f"  Delay   : {args.delay}s between requests\n"
    )

    # 3. Run each model
    all_model_results: dict[str, list[RunResult]] = {}

    for model in models:
        print(f"\n{'═' * 60}")
        print(f"  Running: {model}")
        print(f"{'═' * 60}")

        results = await run_model_benchmark(
            model=model,
            prompts=prompts,
            delay=args.delay,
            progress_callback=_progress,
        )
        all_model_results[model] = results

        # Quick per-model summary right after completion
        from benchmarks.evaluator import evaluate  # noqa: PLC0415
        m = evaluate(model, results)
        print(
            f"\n  → {model}: {m.correct}/{m.total} correct "
            f"({m.accuracy * 100:.1f}%)  "
            f"Hallucinations: {len(m.hallucination_flags)}"
        )

    # 4. Full evaluation + report
    all_metrics = evaluate_all(all_model_results)
    json_path, csv_path = print_full_report(all_metrics, all_model_results)

    print(f"\nDone. JSON → {json_path}\n      CSV  → {csv_path}\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Benchmark the classifier_agent routing accuracy across LLM models.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--model",
        metavar="MODEL_ID",
        default=None,
        help="Run a single model instead of all. E.g. --model gemma-4-31b-it",
    )
    parser.add_argument(
        "--max-prompts",
        metavar="N",
        type=int,
        default=None,
        help="Limit to the first N prompts per model (useful for smoke tests).",
    )
    parser.add_argument(
        "--skip-ambiguous",
        action="store_true",
        default=False,
        help="Exclude prompts marked as ambiguous from the benchmark.",
    )
    parser.add_argument(
        "--delay",
        metavar="SECONDS",
        type=float,
        default=REQUEST_DELAY_SECONDS,
        help=f"Seconds to wait between API calls (default: {REQUEST_DELAY_SECONDS}).",
    )

    args = parser.parse_args()
    asyncio.run(_main(args))


if __name__ == "__main__":
    main()
