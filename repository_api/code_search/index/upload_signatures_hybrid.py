import json
import uuid
from pathlib import Path

import tqdm
from fastembed import SparseTextEmbedding
from qdrant_client import QdrantClient, models
from qdrant_client.models import Distance, VectorParams
from sentence_transformers import SentenceTransformer

from code_search.config import (
    DATA_DIR,
    ENCODER_NAME,
    ENCODER_SIZE,
    QDRANT_API_KEY,
    QDRANT_NLU_COLLECTION_NAME_HYBRID,
    QDRANT_URL,
)
from code_search.index.textifier import textify

file_name = Path(DATA_DIR) / "structures.json"


def load_records():
    with open(file_name, "r") as fp:
        for line in fp:
            row = json.loads(line)
            yield row


def upload():
    collection_name = QDRANT_NLU_COLLECTION_NAME_HYBRID

    client = QdrantClient(
        QDRANT_URL,
        api_key=QDRANT_API_KEY,
        prefer_grpc=True,
    )
    
    dense_encoder = SentenceTransformer(ENCODER_NAME)
    sparse_encoder = SparseTextEmbedding("Qdrant/bm25", providers=["CUDAExecutionProvider", "CPUExecutionProvider"])

    records = list(load_records())
    texts = [textify(row) for row in records]
    
    print("Encoding dense vectors...")
    dense_embeddings = dense_encoder.encode(texts).tolist()
    
    print("Encoding sparse vectors...")
    sparse_embeddings = []
    # Batch the sparse embedding generation
    for sparse_emb_gen in sparse_encoder.embed(texts):
        sparse_embeddings.append(
            models.SparseVector(
                indices=sparse_emb_gen.indices.tolist(),
                values=sparse_emb_gen.values.tolist()
            )
        )

    if not client.collection_exists(collection_name):
        print(f"Collection {collection_name} not found. Creating...")
        client.create_collection(
            collection_name=collection_name,
            vectors_config={
                "dense": VectorParams(
                    size=ENCODER_SIZE,
                    distance=Distance.COSINE,
                    on_disk=True,
                )
            },
            sparse_vectors_config={
                "sparse": models.SparseVectorParams(
                    modifier=models.Modifier.IDF
                )
            },
            quantization_config=models.ScalarQuantization(
                scalar=models.ScalarQuantizationConfig(
                    type=models.ScalarType.INT8,
                    always_ram=True,
                    quantile=0.99,
                )
            ),
        )

        print("Creating index on 'repo_name' field")
        client.create_payload_index(
            collection_name=collection_name,
            field_name="repo_name",
            field_schema=models.PayloadSchemaType.KEYWORD,
        )
    else:
        print(f"Collection {collection_name} exists. Appending new records.")

    point_ids = [str(uuid.uuid4()) for _ in range(len(dense_embeddings))]

    combined_vectors = [
        {"dense": dense_embeddings[i], "sparse": sparse_embeddings[i]}
        for i in range(len(dense_embeddings))
    ]

    print("Uploading to Qdrant...")
    client.upload_collection(
        collection_name=collection_name,
        ids=point_ids,
        vectors=combined_vectors,
        payload=records,
    )


if __name__ == "__main__":
    upload()
