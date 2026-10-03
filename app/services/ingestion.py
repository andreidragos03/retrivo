from sqlalchemy.orm import Session

from app.chunking.text import chunk_text
from app.extractors.pdf import extract_text_from_pdf
from app.models.document import Document, DocumentStatus
from app.services.embeddings import create_embeddings
from app.repositories.document_chunks import create_document_chunks, set_chunk_embeddings
from app.repositories.documents import (
    create_document,
    set_document_content,
    update_document_status,
)


def create_pending_document(
    db: Session,
    title: str,
    filename: str,
    content_type: str
) -> Document:
    document = create_document(
        db = db,
        title = title,
        filename = filename,
        content_type = content_type
    )

    db.commit()
    db.refresh(document)

    return document

def process_pdf_document(
    db: Session,
    document: Document,
    file_bytes: bytes,
) -> Document:
    update_document_status(
        db = db,
        document = document,
        status = DocumentStatus.PROCESSING
    )
    db.commit()

    try:
        extracted_text = extract_text_from_pdf(file_bytes)

        set_document_content(
            db = db,
            document = document,
            content = extracted_text
        )

        chunk_texts = chunk_text(extracted_text)

        document_chunks = create_document_chunks(
            db = db,
            document = document,
            chunks = chunk_texts
        )

        embeddings = create_embeddings(chunk_texts)

        set_chunk_embeddings(
            db = db,
            chunks = document_chunks,
            embeddings = embeddings
        )

        update_document_status(
            db = db,
            document = document,
            status = DocumentStatus.READY
        )

        db.commit()
        db.refresh(document)
 
        return document
    except Exception:
        db.rollback()

        update_document_status(
            db = db,
            document = document,
            status = DocumentStatus.FAILED
        )

        db.commit()
        raise
