import os
from typing import Any

from openai import OpenAI


EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSIONS = 1536


def create_embeddings(
    texts: list[str],
    embeddings_client: Any | None = None
) -> list[list[float]]:
    if not texts:
        return []

    if embeddings_client is None:
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set")

        client = OpenAI(api_key = api_key)
        embeddings_client = client.embeddings

    response = embeddings_client.create(
        model = EMBEDDING_MODEL,
        input = texts
    )

    embeddings = [
        item.embedding
        for item in response.data
    ]

    if len(embeddings) != len(texts):
        raise RuntimeError("Embedding provider returned an unexpected number of embeddings")

    return embeddings
