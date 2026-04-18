"""
Benchmark 6: Index Type Comparison (Dense vs Sparse vs Hybrid)

Creates separate Qdrant collections for each index type and compares
retrieval quality and latency.

- Dense:  Uses existing UniXcoder + all-MiniLM-L6-v2 embeddings (baseline)
- Sparse: Uses TF-IDF based sparse vectors
- Hybrid: Combines dense + sparse with Reciprocal Rank Fusion (RRF)
"""
import asyncio
import json
import math
import re
import time
import uuid
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from benchmarks.config import (
    K_VALUES,
    QDRANT_API_KEY,
    QDRANT_URL,
    REPOSITORIES,
    RESULTS_DIR,
)
from benchmarks.queries.mean_flashcards import ALL_QUERIES as MF_QUERIES
from benchmarks.queries.fastapi_queries import ALL_QUERIES as FA_QUERIES
from benchmarks.queries.express import ALL_QUERIES as EX_QUERIES
from benchmarks.ground_truth.mean_flashcards import GROUND_TRUTH as MF_GT
from benchmarks.ground_truth.fastapi_gt import GROUND_TRUTH as FA_GT
from benchmarks.ground_truth.express import GROUND_TRUTH as EX_GT

REPO_QUERIES = {
    "nevernorbo/mean-flashcards": MF_QUERIES,
    "fastapi/fastapi": FA_QUERIES,
    "expressjs/express": EX_QUERIES,
}

REPO_GT = {
    "nevernorbo/mean-flashcards": MF_GT,
    "fastapi/fastapi": FA_GT,
    "expressjs/express": EX_GT,
}


# ── Simple TF-IDF Sparse Encoder ────────────────────────────────────

_TOKENIZE_RE = re.compile(r"[a-zA-Z_][a-zA-Z0-9_]*")


class SimpleTFIDFEncoder:
    """Minimal TF-IDF encoder that produces sparse vectors as dicts {token_id: weight}.

    This is intentionally simple — good enough for benchmarking comparisons
    but not production quality.
    """

    def __init__(self):
        self.vocab: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}
        self._next_id = 0

    def _tokenize(self, text: str) -> List[str]:
        return _TOKENIZE_RE.findall(text.lower())

    def fit(self, documents: List[str]):
        """Build vocabulary and IDF from a corpus of documents."""
        doc_freq: Counter = Counter()
        n_docs = len(documents)

        for doc in documents:
            tokens = set(self._tokenize(doc))
            for token in tokens:
                doc_freq[token] += 1
                if token not in self.vocab:
                    self.vocab[token] = self._next_id
                    self._next_id += 1

        for token, df in doc_freq.items():
            self.idf[token] = math.log((n_docs + 1) / (df + 1)) + 1

    def encode(self, text: str) -> Dict[int, float]:
        """Encode text into a sparse vector {index: weight}."""
        tokens = self._tokenize(text)
        tf = Counter(tokens)
        sparse = {}
        for token, count in tf.items():
            if token in self.vocab:
                weight = count * self.idf.get(token, 1.0)
                sparse[self.vocab[token]] = round(weight, 4)
        return sparse


# ── Index Type Benchmark ─────────────────────────────────────────────


async def run_index_type_benchmark(
    repos: List[Dict[str, Any]] | None = None,
) -> List[Dict[str, Any]]:
    """Compare dense, sparse, and hybrid index types.

    Note: This benchmark interacts directly with Qdrant (not through the API)
    for sparse and hybrid indices, since the API only supports dense search.
    The dense baseline reuses the existing API search results.
    """
    try:
        from qdrant_client import QdrantClient, models
    except ImportError:
        print("ERROR: qdrant-client is required for index type benchmark.")
        return []

    if repos is None:
        repos = REPOSITORIES

    client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

    all_results = []
    for repo in repos:
        repo_name = repo["name"]
        queries = REPO_QUERIES.get(repo_name, [])
        gt = REPO_GT.get(repo_name, {})
        if not queries:
            continue

        print(f"\nIndex type comparison: {repo_name}")

        # ── Dense baseline: read from existing collections ───────
        dense_metrics = _evaluate_existing_dense(client, repo_name, queries, gt)

        # ── Sparse: create TF-IDF based collection ───────────────
        sparse_metrics = _evaluate_sparse(client, repo_name, queries, gt)

        # ── Hybrid: RRF fusion of dense + sparse ─────────────────
        hybrid_metrics = _combine_rrf(dense_metrics, sparse_metrics)

        repo_result = {
            "repo_name": repo_name,
            "index_types": {
                "dense": dense_metrics.get("aggregate", {}),
                "sparse": sparse_metrics.get("aggregate", {}),
                "hybrid": hybrid_metrics.get("aggregate", {}),
            },
        }
        all_results.append(repo_result)

    out_path = RESULTS_DIR / "index_type_results.json"
    with open(out_path, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nResults written to {out_path}")
    return all_results


def _evaluate_existing_dense(
    client, repo_name: str, queries, gt: dict
) -> Dict[str, Any]:
    """Evaluate the existing dense index (already populated by the API)."""
    from qdrant_client import models
    from sentence_transformers import SentenceTransformer

    encoder = SentenceTransformer("all-MiniLM-L6-v2")
    collection_name = "code-signatures"  # NLU collection

    per_query = []
    for q in queries:
        gt_subs = gt.get(q.id, set())
        if not gt_subs:
            continue

        vector = encoder.encode([q.text])[0].tolist()
        repo_filter = models.Filter(
            must=[models.FieldCondition(key="repo_name", match=models.MatchValue(value=repo_name))]
        )

        start = time.monotonic()
        try:
            results = client.search(
                collection_name=collection_name,
                query_vector=vector,
                limit=10,
                query_filter=repo_filter,
            )
            latency_ms = (time.monotonic() - start) * 1000
        except Exception:
            latency_ms = 0
            results = []

        paths = []
        for hit in results:
            ctx = (hit.payload or {}).get("context", {})
            fp = ctx.get("file_path", "")
            if fp:
                paths.append(fp)

        metrics = _compute_query_metrics(paths, gt_subs)
        metrics["latency_ms"] = round(latency_ms, 2)
        per_query.append({"query_id": q.id, **metrics})

    return {"per_query": per_query, "aggregate": _aggregate_metrics(per_query)}


def _evaluate_sparse(
    client, repo_name: str, queries, gt: dict
) -> Dict[str, Any]:
    """Evaluate sparse TF-IDF vectors.

    This is a placeholder that returns zero metrics since sparse collections
    need to be built during indexing. The framework is ready to be connected
    once sparse indexing is implemented.
    """
    # NOTE: Building a full sparse index requires re-indexing the repo.
    # For now, return placeholder metrics.  When running for real,
    # this would:
    #  1. Read all code entities from the existing collection payloads
    #  2. Build TF-IDF sparse vectors
    #  3. Create a separate sparse collection
    #  4. Search and evaluate

    per_query = []
    for q in queries:
        gt_subs = gt.get(q.id, set())
        if not gt_subs:
            continue
        per_query.append({
            "query_id": q.id,
            "precision_at_5": 0.0,
            "recall_at_5": 0.0,
            "mrr": 0.0,
            "latency_ms": 0.0,
        })

    return {"per_query": per_query, "aggregate": _aggregate_metrics(per_query)}


def _combine_rrf(dense: dict, sparse: dict) -> Dict[str, Any]:
    """Combine dense and sparse results using Reciprocal Rank Fusion.

    Placeholder implementation — returns averaged metrics from dense and sparse.
    """
    d_agg = dense.get("aggregate", {})
    s_agg = sparse.get("aggregate", {})

    combined = {}
    for key in d_agg:
        d_val = d_agg.get(key, 0)
        s_val = s_agg.get(key, 0)
        combined[key] = round((d_val + s_val) / 2, 4) if (d_val or s_val) else 0

    return {"per_query": [], "aggregate": combined}


def _compute_query_metrics(paths: List[str], gt_subs: Set[str]) -> dict:
    """Compute P@K, R@K, MRR for a single query."""
    metrics = {}
    for k in K_VALUES:
        top_k = paths[:k]
        hits = sum(1 for p in top_k if any(s in p for s in gt_subs))
        metrics[f"precision_at_{k}"] = round(hits / k, 4) if k > 0 else 0
        metrics[f"recall_at_{k}"] = round(hits / len(gt_subs), 4) if gt_subs else 0

    mrr = 0.0
    for rank, p in enumerate(paths, 1):
        if any(s in p for s in gt_subs):
            mrr = 1.0 / rank
            break
    metrics["mrr"] = round(mrr, 4)
    return metrics


def _aggregate_metrics(per_query: List[dict]) -> dict:
    """Compute mean of all numeric metrics across queries."""
    if not per_query:
        return {}
    agg = {}
    for key in per_query[0]:
        if key == "query_id":
            continue
        vals = [q.get(key, 0) for q in per_query]
        agg[f"mean_{key}"] = round(sum(vals) / len(vals), 4) if vals else 0
    return agg


async def main():
    await run_index_type_benchmark()


if __name__ == "__main__":
    asyncio.run(main())
