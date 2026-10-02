import pytest

from sqlalchemy.orm import Session

from app.models.document_chunk import DocumentChunk
from app.repositories.document_chunks import create_document_chunks, set_chunk_embeddings
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
