import pytest

from unittest.mock import Mock
from app.services.retrieval import retrieve_chunks
from app.repositories.types import ScoredChunk


def test_retrieve_chunks_embeds_query_and_searches_similar_chunks(
    monkeypatch
):
    fake_embedding = [0.1] * 1536

    fake_results = [
        ScoredChunk(
            chunk=Mock(),
            similarity=0.91,
        ),
        ScoredChunk(
            chunk=Mock(),
            similarity=0.78,
        ),
    ]

    mock_create_embeddings = Mock(
        return_value = [fake_embedding]
    )

    mock_search_similar_chunks = Mock(
        return_value = fake_results
    )

    monkeypatch.setattr(
        "app.services.retrieval.create_embeddings",
        mock_create_embeddings
    )

    monkeypatch.setattr(
        "app.services.retrieval.search_similar_chunks",
        mock_search_similar_chunks
    )

    fake_db = Mock()

    results = retrieve_chunks(
        db = fake_db,
        query = "What AI systems has Dragos built?",
        limit = 3
    )

    mock_create_embeddings.assert_called_once_with(
        ["What AI systems has Dragos built?"]
    )

    mock_search_similar_chunks.assert_called_once_with(
        db = fake_db,
        query_embedding = fake_embedding,
        limit = 3,
    )

    assert results == fake_results

def test_retrieve_chunks_rejects_empty_query():
    with pytest.raises(
        ValueError,
        match = "Query cannot be empty"
    ):
        retrieve_chunks(
            db = Mock(),
            query = "    "
        )

def test_retrieve_chunks_rejects_non_positive_limit():
    with pytest.raises(
        ValueError,
        match = "Limit must be greater than zero"
    ):
        retrieve_chunks(
            db = Mock(),
            query = "Valid query",
            limit = 0
        )
