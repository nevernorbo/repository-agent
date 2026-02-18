from typing import List

from code_search.config import (
    ENCODER_NAME,
    QDRANT_API_KEY,
    QDRANT_CODE_COLLECTION_NAME,
    QDRANT_NLU_COLLECTION_NAME,
    QDRANT_URL,
)
from code_search.model.encoder import UniXcoderEmbeddingsProvider
from code_search.postprocessing import merge_search_results
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer


class CodeSearcher:
    def __init__(self):
        self.collection_name = QDRANT_CODE_COLLECTION_NAME
        self.client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
        self.encoder = UniXcoderEmbeddingsProvider("cpu")

    def search(self, query, limit=5) -> List[dict]:
        vector = self.encoder.embed_code(docstring=query)
        result = self.client.search(
            collection_name=self.collection_name,
            query_vector=vector,
            limit=limit,
            with_payload=["start_line", "end_line", "file"],
        )

        return [hit.payload for hit in result]


class NluSearcher:
    def __init__(self):
        self.collection_name = QDRANT_NLU_COLLECTION_NAME
        self.client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
        self.encoder = SentenceTransformer(ENCODER_NAME)

    def search(self, query, limit=5) -> List[dict]:
        vector = self.encoder.encode([query])[0].tolist()
        result = self.client.search(
            collection_name=self.collection_name,
            query_vector=vector,
            limit=limit,
        )

        return [hit.payload for hit in result]


class CombinedSearcher:
    def __init__(self):
        self.nlu_searcher = NluSearcher()
        self.code_searcher = CodeSearcher()

    def search(self, query, limit=5, code_limit=20) -> List[dict]:
        nlu_res = self.nlu_searcher.search(query, limit=limit)
        code_res = self.code_searcher.search(query, limit=code_limit)

        merged_results = merge_search_results(code_res, nlu_res)

        return merged_results
