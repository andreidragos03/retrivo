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
