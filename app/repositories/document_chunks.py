from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.document_chunk import DocumentChunk


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
