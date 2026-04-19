"""
Central configuration for all benchmark runs.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BENCHMARKS_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BENCHMARKS_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# Target repositories
# ---------------------------------------------------------------------------
REPOSITORIES = [
    {
        "name": "nevernorbo/mean-flashcards",
        "url": "https://github.com/nevernorbo/mean-flashcards",
        "size_category": "small",
        "primary_language": "javascript",
    },
    {
        "name": "fastapi/fastapi",
        "url": "https://github.com/fastapi/fastapi",
        "size_category": "large",
        "primary_language": "python",
    },
    {
        "name": "expressjs/express",
        "url": "https://github.com/expressjs/express",
        "size_category": "medium",
        "primary_language": "javascript",
    },
]

# ---------------------------------------------------------------------------
# API settings
# ---------------------------------------------------------------------------
API_BASE_URL = os.environ.get("BENCHMARK_API_URL", "http://localhost:8000")

# ---------------------------------------------------------------------------
# Qdrant settings (used directly for index-type benchmarks)
# ---------------------------------------------------------------------------
QDRANT_URL = os.environ.get("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.environ.get("QDRANT_API_KEY")

# ---------------------------------------------------------------------------
# Benchmark parameters
# ---------------------------------------------------------------------------

# K values for Precision@K, Recall@K evaluation
K_VALUES = [1, 3, 5, 10]

# Concurrency levels for the concurrency benchmark
CONCURRENCY_LEVELS = [1, 2, 5, 10, 20]

# Qdrant index types to compare
INDEX_TYPES = ["dense", "sparse", "hybrid"]

# How long to wait for indexing to finish (seconds)
INDEX_TIMEOUT_S = 1200

# Number of search results to request per query
SEARCH_LIMIT = 10

# Pause between polling status during indexing (seconds)
INDEX_POLL_INTERVAL_S = 5
