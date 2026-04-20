"""
Benchmark configuration: models, categories, and runtime settings.
"""

from typing import Final

# ── Models to benchmark ──────────────────────────────────────────────────────
BENCHMARK_MODELS: Final[list[str]] = [
    "gemini-2.5-flash",
    "gemma-4-31b-it",
    "ollama/qwen3:0.6b",
]

# ── Routing categories ────────────────────────────────────────────────────────
CATEGORIES: Final[list[str]] = ["chat", "coding", "refactoring", "documenting"]

# Maps the ADK sub-agent name → category label
AGENT_TO_CATEGORY: Final[dict[str, str]] = {
    "chat_agent": "chat",
    "coding_agent": "coding",
    "refactoring_agent": "refactoring",
    "documenting_agent": "documenting",
}

CATEGORY_TO_AGENT: Final[dict[str, str]] = {v: k for k, v in AGENT_TO_CATEGORY.items()}

# ── Runtime settings ──────────────────────────────────────────────────────────

# Seconds to wait between API calls (avoid rate-limit bursts on preview models)
REQUEST_DELAY_SECONDS: float = 1.5

# Directory where result files are written (relative to project root)
RESULTS_DIR: str = "benchmarks/results"

# Synthetic context injected into session state so the classifier always has
# values for the keys it reads (retrieved_context, refined_context).
SYNTHETIC_RETRIEVED_CONTEXT: str = (
    "[Benchmark] No real retrieval performed. "
    "Evaluate routing based solely on the user prompt."
)
SYNTHETIC_REFINED_CONTEXT: str = (
    "[Benchmark] No refinement performed. "
    "Route the following prompt to the most appropriate specialist agent."
)
