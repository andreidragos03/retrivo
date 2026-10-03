from unittest.mock import Mock

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.repositories.types import ScoredChunk


def test_search_returns_scored_chunks(
    client: TestClient,
    db: Session,
    monkeypatch
):
    first_chunk = Mock()
    first_chunk.id = 101
    first_chunk.document_id = 10
    first_chunk.chunk_index = 2
    first_chunk.content = "Dragos built LLM-powered internal tools."

    second_chunk = Mock()
    second_chunk.id = 102
    second_chunk.document_id = 10
    second_chunk.chunk_index = 4
    second_chunk.content = "Dragos worked with Azure and Databricks."

    fake_results = [
        ScoredChunk(
            chunk = first_chunk,
            similarity = 0.91
        ),
        ScoredChunk(
            chunk = second_chunk,
            similarity = 0.82
        )
    ]

    mock_retrieve_chunks = Mock(
        return_value = fake_results
    )

    monkeypatch.setattr(
        "app.routers.search.retrieve_chunks",
        mock_retrieve_chunks
    )

    response = client.post(
        "/search",
        json = {
            "query": "What AI experience does Dragos have?",
            "limit": 2
        }
    )

    assert response.status_code == 200

    mock_retrieve_chunks.assert_called_once_with(
        db = db,
        query = "What AI experience does Dragos have?",
        limit = 2
    )

    data = response.json()

    assert data == {
        "results": [
            {
                "chunk_id": 101,
                "document_id": 10,
                "chunk_index": 2,
                "content": "Dragos built LLM-powered internal tools.",
                "similarity": 0.91
            },
            {
                "chunk_id": 102,
                "document_id": 10,
                "chunk_index": 4,
                "content": "Dragos worked with Azure and Databricks.",
                "similarity": 0.82
            }
        ]
    }

def test_serahc_rejects_invalid_limit(
    client: TestClient
):
    response = client.post(
        "/search",
        json = {
            "query": "What AI experience does Dragos have?",
            "limit": 0
        }
    )

    assert response.status_code == 422
