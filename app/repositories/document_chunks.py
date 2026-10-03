from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.repositories.types import ScoredChunk


def create_document_chunks(
    db: Session,
    document: Document,
    chunks: list[str]   
) -> list[DocumentChunk]:
    document_chunks = []

    for chunk_index, content in enumerate(chunks):
        document_chunk = DocumentChunk(
            document = document,
            chunk_index = chunk_index,
            content = content
        )

        document_chunks.append(document_chunk)

    db.add_all(document_chunks)
    db.flush()

    return document_chunks


def set_chunk_embeddings(
    db: Session,
    chunks: list[DocumentChunk],
    embeddings: list[list[float]]
) -> None:
    if len(chunks) != len(embeddings):
        raise ValueError(
            "Number of chunks must match number of embeddings"
        )

    for chunk, embedding in zip(chunks, embeddings):
        chunk.embedding = embedding

    db.flush()

def search_similar_chunks(
    db: Session,
    query_embedding: list[float],
    limit: int = 5
) -> list[ScoredChunk]:
    distance = DocumentChunk.embedding.cosine_distance(query_embedding)

    statement = (
        select(
            DocumentChunk,
            distance.label("distance")
        )
        .where(DocumentChunk.embedding.is_not(None))
        .order_by(distance)
        .limit(limit)
    )
    
    rows = db.execute(statement).all()

    scored_chunks = []

    for chunk, distance_value in rows:
        scored_chunk = ScoredChunk(
            chunk = chunk,
            similarity = 1 - float(distance_value)
        )

        scored_chunks.append(scored_chunk)

    return scored_chunks
