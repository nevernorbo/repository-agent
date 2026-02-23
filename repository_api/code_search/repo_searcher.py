from typing import Set

from qdrant_client import QdrantClient

from code_search.config import (
    QDRANT_API_KEY,
    QDRANT_CODE_COLLECTION_NAME,
    QDRANT_NLU_COLLECTION_NAME,
    QDRANT_URL,
)


class RepoSearcher:
    def __init__(self):
        self.client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
        self.collections = [QDRANT_CODE_COLLECTION_NAME, QDRANT_NLU_COLLECTION_NAME]

    def get_unique_repositories(self) -> Set[str]:
        unique_repos = set()

        for collection in self.collections:
            offset = None
            while True:
                # Scroll through the collection to find all repo_names
                points, next_offset = self.client.scroll(
                    collection_name=collection,
                    limit=100,  # Adjust batch size based on your DB size
                    with_payload=["repo_name"],
                    with_vectors=False,
                    scroll_filter=None,  # You could filter by user_id here if needed
                    offset=offset,
                )

                for point in points:
                    name = point.payload.get("repo_name")
                    if name:
                        unique_repos.add(name)

                offset = next_offset
                if offset is None:
                    break

        return unique_repos
