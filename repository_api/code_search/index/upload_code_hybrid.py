import json
import uuid
from pathlib import Path

import numpy as np
import qdrant_client
from fastembed import SparseTextEmbedding
from qdrant_client import models
from qdrant_client.http import models as rest
from tqdm import tqdm

from code_search.config import (
    DATA_DIR,
    QDRANT_API_KEY,
    QDRANT_CODE_COLLECTION_NAME_HYBRID,
    QDRANT_URL,
)
from code_search.model.encoder import UniXcoderEmbeddingsProvider

code_keys = [
    "code_snippet",
    "body",
    "signature",
    "name",
]

def encode_and_upload():
    client = qdrant_client.QdrantClient(
        QDRANT_URL,
        api_key=QDRANT_API_KEY,
        prefer_grpc=True,
    )

    collection_name = QDRANT_CODE_COLLECTION_NAME_HYBRID
    input_file = Path(DATA_DIR) / "qdrant_snippets.jsonl"
    
    dense_encoder = UniXcoderEmbeddingsProvider()
    sparse_encoder = SparseTextEmbedding("Qdrant/bm25", providers=["CUDAExecutionProvider", "CPUExecutionProvider"])

    if not input_file.exists():
        raise RuntimeError(f"File {input_file} does not exist. Skipping")

    print(f"Preparing the output for {collection_name}")

    dense_embeddings = []
    sparse_embeddings = []
    payloads = []
    
    with open(input_file, "r") as fp:
        for line in tqdm(fp):
            line_dict = json.loads(line)

            body = None
            for code_key in code_keys:
                body = line_dict.get(code_key)
                if body is not None:
                    break
            docstring = line_dict.get("docstring")

            if body is None or len(body) == 0:
                continue

            dense_emb = dense_encoder.embed_code(body, docstring)
            
            # Use body + docstring for sparse BM25
            sparse_text = body
            if docstring:
                sparse_text += "\n" + docstring
                
            # fastembed returns an iterator, we just take the first element
            sparse_emb_gen = list(sparse_encoder.embed([sparse_text]))[0]
            
            dense_embeddings.append(dense_emb)
            sparse_embeddings.append(
                models.SparseVector(
                    indices=sparse_emb_gen.indices.tolist(),
                    values=sparse_emb_gen.values.tolist()
                )
            )
            payloads.append(line_dict)

    print(f"Embeddings shape: dense=({len(dense_embeddings)}, {len(dense_embeddings[0])}), sparse={len(sparse_embeddings)}")

    if not client.collection_exists(collection_name):
        print(f"Creating hybrid collection {collection_name}")
        client.create_collection(
            collection_name=collection_name,
            vectors_config={
                "dense": rest.VectorParams(
                    size=len(dense_embeddings[0]),
                    distance=rest.Distance.COSINE,
                    on_disk=True,
                )
            },
            sparse_vectors_config={
                "sparse": rest.SparseVectorParams()
            },
            quantization_config=rest.ScalarQuantization(
                scalar=rest.ScalarQuantizationConfig(
                    type=rest.ScalarType.INT8,
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
        print(f"Collection {collection_name} already exists. Appending data.")

    point_ids = [str(uuid.uuid4()) for _ in range(len(dense_embeddings))]
    
    combined_vectors = [
        {"dense": dense_embeddings[i], "sparse": sparse_embeddings[i]}
        for i in range(len(dense_embeddings))
    ]

    print(f"Storing data in the collection {collection_name}")
    client.upload_collection(
        collection_name=collection_name,
        ids=point_ids,
        vectors=combined_vectors,
        payload=payloads,
    )

if __name__ == "__main__":
    encode_and_upload()
