from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(min_length = 1)
    limit: int = Field(default = 5, ge = 1, le = 20)

class SearchResult(BaseModel):
    chunk_id: int
    document_id: int
    chunk_index: int
    content: str
    similarity: float

class SearchResponse(BaseModel):
    results: list[SearchResult]
