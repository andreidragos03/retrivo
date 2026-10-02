import pytest
from types import SimpleNamespace

from app.services.embeddings import (
    EMBEDDING_MODEL,
    create_embeddings
)


class FakeEmbeddings:
    def __init__(self, embeddings=None):
        self.calls = []

        self.returned_embeddings = embeddings or [
            [0.1, 0.2, 0.3],
            [0.4, 0.5, 0.6],
        ]

    def create(self, *, model: str, input: list[str]):
        self.calls.append({
            "model": model,
            "input": input,
        })

        return SimpleNamespace(
            data=[
                SimpleNamespace(embedding = embedding)
                for embedding in self.returned_embeddings
            ]
        )


def test_empty_input_returns_no_embeddings():
    fake_embeddings = FakeEmbeddings()

    result = create_embeddings(
        [],
        embeddings_client = fake_embeddings
    )

    assert result == []
    assert fake_embeddings.calls == []


def test_create_embeddings_batches_texts_and_preserves_order():
    fake_embeddings = FakeEmbeddings()

    texts = [
        "PostgreSQL supports transactions.",
        "Retrivo performs semantic search."
    ]

    result = create_embeddings(
        texts,
        embeddings_client = fake_embeddings
    )

    assert result == [
        [0.1, 0.2, 0.3],
        [0.4, 0.5, 0.6]
    ]

    assert fake_embeddings.calls == [
        {
            "model": EMBEDDING_MODEL,
            "input": texts
        }
    ]


def test_create_embeddings_rejects_wrong_number_of_embeddings():
    fake_embeddings = FakeEmbeddings(
        embeddings=[
            [0.1, 0.2, 0.3],
        ]
    )

    with pytest.raises(
        RuntimeError,
        match = "Embedding provider returned an unexpected number of embeddings"
    ):
        create_embeddings(
            ["first", "second"],
            embeddings_client = fake_embeddings
        )
