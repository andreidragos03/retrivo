from sqlalchemy.orm import Session

from app.repositories.types import ScoredChunk
from app.repositories.document_chunks import search_similar_chunks
from app.services.embeddings import create_embeddings


def retrieve_chunks(
    db: Session,
    query: str,
    limit: int = 5
) -> list[ScoredChunk]:
    if not query.strip():
        raise ValueError("Query cannot be empty")

    if limit <= 0:
        raise ValueError("Limit must be greater than zero")
    
    query_embedding = create_embeddings([query])[0]

    results = search_similar_chunks(
        db = db,
        query_embedding = query_embedding,
        limit = limit
    )

    return results
