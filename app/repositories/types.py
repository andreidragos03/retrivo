from dataclasses import dataclass

from app.models.document_chunk import DocumentChunk


@dataclass
class ScoredChunk:
    chunk: DocumentChunk
    similarity: float
