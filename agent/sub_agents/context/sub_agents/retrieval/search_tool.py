"""
API Search Tool: Connects to the Memvid2 knowledge base via REST API.

This tool makes HTTP requests to the search API endpoint to retrieve
relevant code context, documentation, and dependency information.
"""

import requests
from google.adk.tools.tool_context import ToolContext

SEARCH_API_URL = "http://localhost:8000/api/search"


def search_codebase_api(query: str, tool_context: ToolContext) -> dict:
    """
    Search the codebase knowledge base via REST API.

    Args:
        query: The search query about the codebase

    Returns:
        Dictionary containing search results.
    """
    try:
        repo_name = tool_context.state.get("repository")
        print("Invoking search tool on repo: ", repo_name)

        if not repo_name:
            return {
                "status": "error",
                "error": "No repository found in the current agent session state.",
                "results": [],
            }

        params = {"query": query, "repo_name": repo_name}

        response = requests.get(SEARCH_API_URL, params=params)
        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException as e:
        return {"status": "error", "error": str(e), "results": []}
