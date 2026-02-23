import json
import uuid
from pathlib import Path

import tqdm
from qdrant_client import QdrantClient, models
from qdrant_client.models import Distance, VectorParams
from sentence_transformers import SentenceTransformer

from code_search.config import (
    DATA_DIR,
    ENCODER_NAME,
    ENCODER_SIZE,
    QDRANT_API_KEY,
    QDRANT_NLU_COLLECTION_NAME,
    QDRANT_URL,
)
from code_search.index.textifier import textify

file_name = Path(DATA_DIR) / "structures.json"


def iter_batch(iterable, batch_size=64):
    batch = []
    for item in iterable:
        batch.append(item)
        if len(batch) == batch_size:
            yield batch
            batch = []
    if batch:
        yield batch


def load_records():
    with open(file_name, "r") as fp:
        for line in fp:
            row = json.loads(line)
            yield row


def encode(sentence_transformer_name=ENCODER_NAME):
    model = SentenceTransformer(sentence_transformer_name)
    for batch in iter_batch(load_records()):
        texts = [textify(row) for row in batch]
        embeddings = model.encode(texts).tolist()
        yield from embeddings


def upload():
    collection_name = QDRANT_NLU_COLLECTION_NAME

    client = QdrantClient(
        QDRANT_URL,
        api_key=QDRANT_API_KEY,
        prefer_grpc=True,
    )

    if not client.collection_exists(collection_name):
        print(f"Collection {collection_name} not found. Creating...")
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=ENCODER_SIZE,
                distance=Distance.COSINE,
                on_disk=True,
            ),
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

    vectors = list(encode())
    payloads = list(tqdm.tqdm(load_records()))
    point_ids = [str(uuid.uuid4()) for _ in range(len(vectors))]

    client.upload_collection(
        collection_name=collection_name,
        ids=point_ids,
        vectors=vectors,
        payload=payloads,
    )


if __name__ == "__main__":
    upload()
