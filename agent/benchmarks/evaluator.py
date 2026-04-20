"""
Evaluator: Computes routing accuracy metrics from RunResult lists.

Produces per-model and per-category breakdowns, a confusion matrix,
and flags hallucinated reasoning (classifier reasoning contradicts routing).
"""

from collections import defaultdict
from dataclasses import dataclass, field

from benchmarks.config import CATEGORIES
from benchmarks.runner import RunResult


@dataclass
class CategoryMetrics:
    category: str
    total: int = 0
    correct: int = 0
    ambiguous_total: int = 0
    ambiguous_correct: int = 0

    @property
    def accuracy(self) -> float:
        return self.correct / self.total if self.total else 0.0

    @property
    def strict_total(self) -> int:
        """Non-ambiguous prompts only."""
        return self.total - self.ambiguous_total

    @property
    def strict_accuracy(self) -> float:
        strict_correct = self.correct - self.ambiguous_correct
        return strict_correct / self.strict_total if self.strict_total else 0.0


@dataclass
class ModelMetrics:
    model: str
    results: list[RunResult]
    category_metrics: dict[str, CategoryMetrics] = field(default_factory=dict)
    # confusion_matrix[expected][routed] = count
    confusion_matrix: dict[str, dict[str, int]] = field(default_factory=dict)
    hallucination_flags: list[RunResult] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def correct(self) -> int:
        return sum(1 for r in self.results if r.correct)

    @property
    def accuracy(self) -> float:
        return self.correct / self.total if self.total else 0.0

    @property
    def error_count(self) -> int:
        return sum(1 for r in self.results if r.error)

    @property
    def avg_latency(self) -> float:
        valid = [r.latency_seconds for r in self.results if not r.error]
        return sum(valid) / len(valid) if valid else 0.0

    @property
    def strict_accuracy(self) -> float:
        """Accuracy on non-ambiguous prompts only."""
        strict = [r for r in self.results if not r.is_ambiguous]
        if not strict:
            return 0.0
        return sum(1 for r in strict if r.correct) / len(strict)


def _detect_hallucination(result: RunResult) -> bool:
    """
    Flag if the classifier's written reasoning mentions a different agent than
    the one actually invoked.  A lightweight heuristic check.
    """
    if not result.classifier_reasoning or not result.routed_agent:
        return False
    reasoning_lower = result.classifier_reasoning.lower()
    # Determine what agent the reasoning *claims* to route to
    mentioned_agents = [
        agent for agent in ["chat_agent", "coding_agent", "refactoring_agent", "documenting_agent"]
        if agent.replace("_agent", "") in reasoning_lower or agent in reasoning_lower
    ]
    if not mentioned_agents:
        return False
    # If the top-mentioned agent differs from what was actually called → flag
    claimed = mentioned_agents[0]
    return claimed != result.routed_agent


def evaluate(model: str, results: list[RunResult]) -> ModelMetrics:
    """Compute all metrics for one model's results."""
    metrics = ModelMetrics(model=model, results=results)

    # Initialise confusion matrix and category metrics
    for cat in CATEGORIES:
        metrics.confusion_matrix[cat] = {c: 0 for c in CATEGORIES + ["unknown"]}
        metrics.category_metrics[cat] = CategoryMetrics(category=cat)

    for result in results:
        expected = result.expected_category
        routed = result.routed_category or "unknown"

        # Category metrics
        cm = metrics.category_metrics[expected]
        cm.total += 1
        if result.correct:
            cm.correct += 1
        if result.is_ambiguous:
            cm.ambiguous_total += 1
            if result.correct:
                cm.ambiguous_correct += 1

        # Confusion matrix
        if expected in metrics.confusion_matrix:
            metrics.confusion_matrix[expected][routed] = (
                metrics.confusion_matrix[expected].get(routed, 0) + 1
            )

        # Hallucination check
        if _detect_hallucination(result):
            metrics.hallucination_flags.append(result)

    return metrics


def evaluate_all(model_results: dict[str, list[RunResult]]) -> dict[str, ModelMetrics]:
    """Evaluate results for all models. Returns model → ModelMetrics mapping."""
    return {model: evaluate(model, results) for model, results in model_results.items()}
