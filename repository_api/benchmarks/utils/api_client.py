"""
Async HTTP client for interacting with the repository_api service during benchmarks.
"""

import asyncio
import time
from typing import Any, Dict, List, Optional

import httpx

from benchmarks.config import API_BASE_URL, INDEX_POLL_INTERVAL_S, INDEX_TIMEOUT_S


class BenchmarkAPIClient:
    """Thin async wrapper around the repository_api HTTP endpoints."""

    def __init__(self, base_url: str = API_BASE_URL, timeout: float = 120.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    # ------------------------------------------------------------------
    # Indexing
    # ------------------------------------------------------------------

    async def index_repository(self, repo_name: str) -> Dict[str, Any]:
        """Trigger indexing via POST /api/index.

        Returns:
            Response JSON body.
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(
                f"{self.base_url}/api/index",
                json={"repo_name": repo_name},
            )
            resp.raise_for_status()
            return resp.json()

    async def get_index_status(self, repo_name: str) -> str:
        """Poll GET /api/index/status/{repo_name}.

        Returns:
            Status string: "not_started", "cloned", "indexing", "completed", or "failed: ...".
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(
                f"{self.base_url}/api/index/status/{repo_name}",
            )
            resp.raise_for_status()
            return resp.json().get("status", "unknown")

    async def wait_for_indexing(
        self,
        repo_name: str,
        timeout_s: int = INDEX_TIMEOUT_S,
        poll_interval_s: int = INDEX_POLL_INTERVAL_S,
    ) -> Dict[str, Any]:
        """Block until indexing finishes (or times out).

        Returns:
            Dict with ``status``, ``elapsed_s``, and ``repo_name``.

        Raises:
            TimeoutError: If indexing does not finish within *timeout_s*.
        """
        start = time.monotonic()
        while True:
            status = await self.get_index_status(repo_name)
            elapsed = time.monotonic() - start

            if status == "completed":
                return {
                    "repo_name": repo_name,
                    "status": "completed",
                    "elapsed_s": round(elapsed, 2),
                }
            if status.startswith("failed"):
                return {
                    "repo_name": repo_name,
                    "status": status,
                    "elapsed_s": round(elapsed, 2),
                }
            if elapsed > timeout_s:
                raise TimeoutError(
                    f"Indexing {repo_name} did not complete within {timeout_s}s "
                    f"(last status: {status})"
                )

            await asyncio.sleep(poll_interval_s)

    # ------------------------------------------------------------------
    # Searching
    # ------------------------------------------------------------------

    async def search(
        self, query: str, repo_name: str, limit: int = 5
    ) -> Dict[str, Any]:
        """Execute GET /api/search and return the JSON body.

        The response includes the list of results **and** the wall-clock
        latency as measured from the client side.
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            start = time.monotonic()
            resp = await client.get(
                f"{self.base_url}/api/search",
                params={"query": query, "repo_name": repo_name},
            )
            latency_ms = (time.monotonic() - start) * 1000
            resp.raise_for_status()
            body = resp.json()
            body["_latency_ms"] = round(latency_ms, 2)
            return body

    async def search_timed(
        self, query: str, repo_name: str
    ) -> Dict[str, Any]:
        """Convenience: search + return results with latency attached."""
        return await self.search(query, repo_name)

    # ------------------------------------------------------------------
    # Repository listing
    # ------------------------------------------------------------------

    async def get_repositories(self) -> List[str]:
        """GET /api/repositories — list all indexed repos."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(f"{self.base_url}/api/repositories")
            resp.raise_for_status()
            return resp.json()
