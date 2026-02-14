"""
API Search Tool: Connects to the Memvid2 knowledge base via REST API.

This tool makes HTTP requests to the search API endpoint to retrieve
relevant code context, documentation, and dependency information.
"""

import requests

# URL for the new memvid_api_server
# SEARCH_API_URL = "http://localhost:8001/repository/msc-thesis-project/query"
SEARCH_API_URL = "http://localhost:8001/repository/query"


def search_codebase_api(query: str) -> dict:
    """
    Search the codebase knowledge base via REST API.

    Args:
        query: The search query about the codebase

    Returns:
        Dictionary containing search results.
    """
    try:
        # The new endpoint takes the query as a 'q' parameter
        params = {"q": query}

        response = requests.get(SEARCH_API_URL, params=params)
        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException as e:
        return {"status": "error", "error": str(e), "results": []}
