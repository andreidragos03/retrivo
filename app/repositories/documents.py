from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import Document


def create_document(
    db: Session,
    title: str,
    content: str
) -> Document:
    document = Document(
        title = title,
        content = content
    )

    db.add(document)
    db.flush()

    return document

def get_document_by_id(
    db: Session,
    document_id: int,
) -> Document | None:
    statement = select(Document).where(Document.id == document_id)

    return db.scalar(statement)

def update_document(
    db: Session,
    document: Document,
    update_data: dict
) -> Document:
    for field, value in update_data.items():
        setattr(document, field, value)

    db.flush()

    return document

def delete_document(
    db: Session,
    document: Document
) -> None:
    db.delete(document)
    db.flush()

def list_documents(
    db: Session,
    offset: int,
    limit: int
) -> list[Document]:
    statement = (
        select(Document)
        .order_by(Document.id)
        .offset(offset)
        .limit(limit)
    )

    return list(db.scalars(statement).all())
