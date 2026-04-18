"""
Information Retrieval metrics for evaluating search quality.

All functions expect:
    retrieved  – ordered list of identifiers returned by the search system
    relevant   – set of identifiers that are considered relevant (ground truth)
"""

from typing import Dict, List, Set


def precision_at_k(retrieved: List[str], relevant: Set[str], k: int) -> float:
    """Fraction of the top-k results that are relevant.

    Args:
        retrieved: Ordered list of result identifiers.
        relevant: Set of relevant identifiers (ground truth).
        k: Cut-off rank.

    Returns:
        Precision value in [0, 1].
    """
    if k <= 0:
        return 0.0
    top_k = retrieved[:k]
    if not top_k:
        return 0.0
    hits = sum(1 for item in top_k if item in relevant)
    return hits / k


def recall_at_k(retrieved: List[str], relevant: Set[str], k: int) -> float:
    """Fraction of all relevant items that appear in the top-k results.

    Args:
        retrieved: Ordered list of result identifiers.
        relevant: Set of relevant identifiers (ground truth).
        k: Cut-off rank.

    Returns:
        Recall value in [0, 1].  Returns 0 if there are no relevant items.
    """
    if not relevant or k <= 0:
        return 0.0
    top_k = retrieved[:k]
    hits = sum(1 for item in top_k if item in relevant)
    return hits / len(relevant)


def reciprocal_rank(retrieved: List[str], relevant: Set[str]) -> float:
    """Reciprocal of the rank of the first relevant result.

    Args:
        retrieved: Ordered list of result identifiers.
        relevant: Set of relevant identifiers (ground truth).

    Returns:
        1/rank of first hit, or 0 if no relevant result is found.
    """
    for rank, item in enumerate(retrieved, start=1):
        if item in relevant:
            return 1.0 / rank
    return 0.0


def mean_reciprocal_rank(
    all_retrieved: List[List[str]], all_relevant: List[Set[str]]
) -> float:
    """Mean Reciprocal Rank across multiple queries.

    Args:
        all_retrieved: List of result lists, one per query.
        all_relevant: List of relevant-item sets, one per query.

    Returns:
        MRR value in [0, 1].
    """
    if not all_retrieved:
        return 0.0
    rrs = [
        reciprocal_rank(ret, rel) for ret, rel in zip(all_retrieved, all_relevant)
    ]
    return sum(rrs) / len(rrs)


def compute_all_metrics(
    retrieved: List[str], relevant: Set[str], k_values: List[int]
) -> Dict[str, float]:
    """Compute all IR metrics for a single query at multiple K values.

    Args:
        retrieved: Ordered list of result identifiers.
        relevant: Set of relevant identifiers (ground truth).
        k_values: List of cut-off values (e.g. [1, 3, 5, 10]).

    Returns:
        Dictionary with metric name → value mappings, e.g.::

            {
                "precision_at_1": 1.0,
                "precision_at_3": 0.67,
                "recall_at_1": 0.25,
                "recall_at_3": 0.50,
                "mrr": 1.0,
            }
    """
    metrics: Dict[str, float] = {}
    for k in k_values:
        metrics[f"precision_at_{k}"] = precision_at_k(retrieved, relevant, k)
        metrics[f"recall_at_{k}"] = recall_at_k(retrieved, relevant, k)
    metrics["mrr"] = reciprocal_rank(retrieved, relevant)
    return metrics
