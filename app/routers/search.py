from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.search import SearchRequest, SearchResponse, SearchResult
from app.services.retrieval import retrieve_chunks


router = APIRouter(
    prefix = "/search",
    tags = ["search"]
)


@router.post("", response_model = SearchResponse)
def search(
    request: SearchRequest,
    db: Session = Depends(get_db)
) -> SearchResponse:
    scored_chunks = retrieve_chunks(
        db = db,
        query = request.query,
        limit = request.limit
    )
    
    results = []

    for scored_chunk in scored_chunks:
        chunk = scored_chunk.chunk

        result = SearchResult(
            chunk_id = chunk.id,
            document_id = chunk.document_id,
            chunk_index = chunk.chunk_index,
            content = chunk.content,
            similarity = scored_chunk.similarity
        )

        results.append(result)

    return SearchResponse(results = results)
