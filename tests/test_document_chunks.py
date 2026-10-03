import pytest

from sqlalchemy.orm import Session

from app.models.document_chunk import DocumentChunk
from app.repositories.document_chunks import create_document_chunks, search_similar_chunks, set_chunk_embeddings
from tests.test_documents import create_test_document


def test_set_chunk_embeddings(
    db: Session
):
    document = create_test_document(
        title = "Embedding test",
        content = "First chunk Second chunk"
    )
    
    db.add(document)
    db.flush()

    chunks = create_document_chunks(
        db = db,
        document = document,
        chunks = [
            "First chunk",
            "Second chunk"
        ]
    )

    embedding_1 = [0.1] * 1536
    embedding_2 = [0.2] * 1536

    set_chunk_embeddings(
        db = db,
        chunks = chunks,
        embeddings = [embedding_1, embedding_2]
    )

    assert chunks[0].embedding is not None
    assert chunks[1].embedding is not None


def test_set_chunk_embeddings_reject_mismatched_counts(
    db: Session
):
    document = create_test_document(
        title = "Embedding mismatch test",
        content = "First chunk Second chunk",
    )

    db.add(document)
    db.flush()

    chunks = create_document_chunks(
        db = db,
        document = document,
        chunks = [
            "First chunk",
            "Second chunk",
        ],
    )

    with pytest.raises(
        ValueError,
        match = "Number of chunks must match number of embeddings"
    ):
        set_chunk_embeddings(
            db = db,
            chunks = chunks,
            embeddings=[
                [0.1] * 1536
            ]
        )

def test_search_similar_chunks_returns_chunks_by_cosine_distance(
    db: Session
):
    document = create_test_document(
        title = "Semantic search test",
        content = "Test content"
    )

    db.add(document)
    db.flush()

    chunks = create_document_chunks(
        db = db,
        document = document,
        chunks = [
            "Very similar",
            "Less similar",
            "Opposite"
        ]
    )

    set_chunk_embeddings(
        db = db,
        chunks = chunks,
        embeddings = [
            [1.0, 0.1] + [0.0] * 1534,
            [1.0, 1.0] + [0.0] * 1534,
            [-1.0, 0.0] + [0.0] * 1534
        ]
    )

    query_embedding = [1.0, 0.0] + [0.0] * 1534

    results = search_similar_chunks(
        db = db,
        query_embedding = query_embedding,
        limit = 3
    )

    assert [result.chunk.content for result in results] == [
        "Very similar",
        "Less similar",
        "Opposite"
    ]

    assert results[0].similarity > results[1].similarity
    assert results[0].similarity > results[2].similarity
    assert results[2].similarity == pytest.approx(-1.0)

def test_search_similar_chunks_respects_limit(
    db: Session
):
    document = create_test_document(
        title = "Semantic search limit test",
        content = "Test content"
    )

    db.add(document)
    db.flush()

    chunks = create_document_chunks(
        db = db,
        document = document,
        chunks = [
            "Closest",
            "Second",
            "Third"
        ]
    )

    set_chunk_embeddings(
        db = db,
        chunks = chunks,
        embeddings = [
            [1.0, 0.0] + [0.0] * 1534,
            [1.0, 0.5] + [0.0] * 1534,
            [0.0, 1.0] + [0.0] * 1534 
        ]
    )

    results = search_similar_chunks(
        db = db,
        query_embedding = [1.0, 0.0] + [0.0] * 1534,
        limit = 2
    )

    assert len(results) == 2

    assert [result.chunk.content for result in results] == [
        "Closest",
        "Second"
    ]
