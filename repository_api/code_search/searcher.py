from typing import List

from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer

from code_search.config import (
    ENCODER_NAME,
    QDRANT_API_KEY,
    QDRANT_CODE_COLLECTION_NAME,
    QDRANT_NLU_COLLECTION_NAME,
    QDRANT_URL,
)
from code_search.model.encoder import UniXcoderEmbeddingsProvider
from code_search.postprocessing import merge_search_results


class CodeSearcher:
    def __init__(self):
        self.collection_name = QDRANT_CODE_COLLECTION_NAME
        self.client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
        self.encoder = UniXcoderEmbeddingsProvider()

    def search(self, query, repo_filter, limit=5) -> List[dict]:
        vector = self.encoder.embed_code(docstring=query)
        result = self.client.search(
            collection_name=self.collection_name,
            query_vector=vector,
            limit=limit,
            query_filter=repo_filter,
            with_payload=["start_line", "end_line", "file"],
        )

        return [hit.payload for hit in result]


class NluSearcher:
    def __init__(self):
        self.collection_name = QDRANT_NLU_COLLECTION_NAME
        self.client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
        self.encoder = SentenceTransformer(ENCODER_NAME)

    def search(self, query, repo_filter, limit=5) -> List[dict]:
        vector = self.encoder.encode([query])[0].tolist()
        result = self.client.search(
            collection_name=self.collection_name,
            query_vector=vector,
            limit=limit,
            query_filter=repo_filter,
        )

        return [hit.payload for hit in result]


class CombinedSearcher:
    def __init__(self):
        self.nlu_searcher = NluSearcher()
        self.code_searcher = CodeSearcher()

    def create_repo_filter(self, repo_name):
        return models.Filter(
            must=[
                models.FieldCondition(
                    key="repo_name",
                    match=models.MatchValue(value=repo_name),
                )
            ]
        )

    def search(self, query, repo_name, limit=5, code_limit=20) -> List[dict]:
        print("Filtering on repo_name: ", repo_name)

        repo_filter = self.create_repo_filter(repo_name)
        nlu_res = self.nlu_searcher.search(query, repo_filter, limit=limit)
        code_res = self.code_searcher.search(query, repo_filter, limit=code_limit)

        merged_results = merge_search_results(code_res, nlu_res)

        return merged_results


from fastembed import SparseTextEmbedding
from code_search.config import QDRANT_CODE_COLLECTION_NAME_HYBRID, QDRANT_NLU_COLLECTION_NAME_HYBRID

class HybridCodeSearcher:
    def __init__(self):
        self.collection_name = QDRANT_CODE_COLLECTION_NAME_HYBRID
        self.client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
        self.dense_encoder = UniXcoderEmbeddingsProvider()
        self.sparse_encoder = SparseTextEmbedding("Qdrant/bm25", providers=["CUDAExecutionProvider", "CPUExecutionProvider"])

    def search(self, query, repo_filter, limit=5) -> List[dict]:
        dense_vector = self.dense_encoder.embed_code(docstring=query)
        sparse_emb_gen = list(self.sparse_encoder.embed([query]))[0]
        sparse_vector = models.SparseVector(
            indices=sparse_emb_gen.indices.tolist(),
            values=sparse_emb_gen.values.tolist()
        )

        result = self.client.query_points(
            collection_name=self.collection_name,
            prefetch=[
                models.Prefetch(query=dense_vector, using="dense", limit=limit*2),
                models.Prefetch(query=sparse_vector, using="sparse", limit=limit*2),
            ],
            query=models.FusionQuery(fusion=models.Fusion.RRF),
            limit=limit,
            query_filter=repo_filter,
            with_payload=["start_line", "end_line", "file"],
        )

        return [hit.payload for hit in result.points]


class HybridNluSearcher:
    def __init__(self):
        self.collection_name = QDRANT_NLU_COLLECTION_NAME_HYBRID
        self.client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
        self.dense_encoder = SentenceTransformer(ENCODER_NAME)
        self.sparse_encoder = SparseTextEmbedding("Qdrant/bm25", providers=["CUDAExecutionProvider", "CPUExecutionProvider"])

    def search(self, query, repo_filter, limit=5) -> List[dict]:
        dense_vector = self.dense_encoder.encode([query])[0].tolist()
        sparse_emb_gen = list(self.sparse_encoder.embed([query]))[0]
        sparse_vector = models.SparseVector(
            indices=sparse_emb_gen.indices.tolist(),
            values=sparse_emb_gen.values.tolist()
        )

        result = self.client.query_points(
            collection_name=self.collection_name,
            prefetch=[
                models.Prefetch(query=dense_vector, using="dense", limit=limit*2),
                models.Prefetch(query=sparse_vector, using="sparse", limit=limit*2),
            ],
            query=models.FusionQuery(fusion=models.Fusion.RRF),
            limit=limit,
            query_filter=repo_filter,
            with_payload=True,
        )

        return [hit.payload for hit in result.points]


class HybridCombinedSearcher:
    def __init__(self):
        self.nlu_searcher = HybridNluSearcher()
        self.code_searcher = HybridCodeSearcher()

    def create_repo_filter(self, repo_name):
        return models.Filter(
            must=[
                models.FieldCondition(
                    key="repo_name",
                    match=models.MatchValue(value=repo_name),
                )
            ]
        )

    def search(self, query, repo_name, limit=5, code_limit=20) -> List[dict]:
        print("Filtering on repo_name (Hybrid): ", repo_name)

        repo_filter = self.create_repo_filter(repo_name)
        nlu_res = self.nlu_searcher.search(query, repo_filter, limit=limit)
        code_res = self.code_searcher.search(query, repo_filter, limit=code_limit)

        merged_results = merge_search_results(code_res, nlu_res)

        return merged_results
