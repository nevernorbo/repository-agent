"""
API Search Tool: Connects to the Qdrant knowledge base via REST API.

This tool makes HTTP requests to the search API endpoint to retrieve
relevant code context, documentation, and dependency information.
"""

import requests

SEARCH_API_URL = "http://localhost:8000/api/search"


def search_codebase_api(query: str) -> dict:
    """
    Search the codebase knowledge base via REST API.

    Args:
        query: The search query about the codebase

    Returns:
        Dictionary containing search results with:
        - 'status': 'success' or 'error'
        - 'results': List of matched code contexts
        - 'metadata': Information about the search
    """
    try:
        payload = {"query": query}

        response = requests.get(SEARCH_API_URL, params=payload)
        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException as e:
        return {"status": "error", "error": str(e), "results": []}
