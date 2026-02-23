import json
import uuid
from pathlib import Path

import numpy as np
import qdrant_client
from qdrant_client import models
from qdrant_client.http import models as rest
from tqdm import tqdm

from code_search.config import (
    DATA_DIR,
    QDRANT_API_KEY,
    QDRANT_CODE_COLLECTION_NAME,
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

    collection_name = QDRANT_CODE_COLLECTION_NAME
    input_file = Path(DATA_DIR) / "qdrant_snippets.jsonl"
    encoder = UniXcoderEmbeddingsProvider()

    input_file = Path(DATA_DIR) / input_file
    output_file = Path(DATA_DIR) / f"{collection_name}.npy"

    if not input_file.exists():
        raise RuntimeError(f"File {input_file} does not exist. Skipping")

    if output_file.exists():
        print(f"File {output_file} already exists. Skipping encoding.")
        embeddings = np.load(str(output_file)).tolist()
    else:
        print(f"Preparing the output for {output_file}")

        embeddings = []
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

                embedding = encoder.embed_code(body, docstring)
                embeddings.append(embedding)

        np.save(str(output_file), np.array(embeddings))

    payloads = []
    with open(input_file, "r") as fp:
        for line in tqdm(fp):
            line_dict = json.loads(line)
            payloads.append(line_dict)

    print(f"Embeddings shape: ({len(embeddings)}, {len(embeddings[0])})")

    # 1. Check if collection exists instead of recreating
    if not client.collection_exists(collection_name):
        print(f"Creating collection {collection_name}")
        client.create_collection(
            collection_name=collection_name,
            vectors_config=rest.VectorParams(
                size=len(embeddings[0]),  # Standardized to first index
                distance=rest.Distance.COSINE,
                on_disk=True,
            ),
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

    # 2. Use UUIDs for IDs to avoid overwriting existing points (0, 1, 2...)
    point_ids = [str(uuid.uuid4()) for _ in range(len(embeddings))]

    print(f"Storing data in the collection {collection_name}")
    client.upload_collection(
        collection_name=collection_name,
        ids=point_ids,
        vectors=embeddings,
        payload=payloads,
    )


if __name__ == "__main__":
    encode_and_upload()
