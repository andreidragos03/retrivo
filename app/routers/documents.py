from fastapi import APIRouter, Depends, HTTPException, Response, status

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dependencies import get_db, pagination_params
from app.models.document import Document
from app.exceptions import DocumentNotFoundError
from app.schemas.documents import (
    DocumentCreate,
    DocumentResponse,
    DocumentUpdate,
)


router = APIRouter(
    prefix="/documents",
    tags=["documents"],
)


@router.post(
    "",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_document(
    document: DocumentCreate,
    db: Session = Depends(get_db)
):
    db_document = Document(
        title = document.title,
        content = document.content
    )

    db.add(db_document)
    db.commit()
    db.refresh(db_document)

    return db_document


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
)
def get_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    statement = select(Document).where(Document.id == document_id)

    db_document = db.scalar(statement)

    if db_document is None:
        raise DocumentNotFoundError(document_id)

    return db_document


@router.patch(
    "/{document_id}",
    response_model=DocumentResponse,
)
def update_document(
    document_id: int,
    update: DocumentUpdate,
    db: Session = Depends(get_db)
):
    statement = select(Document).where(Document.id == document_id)
    db_document = db.scalar(statement)
    
    if db_document is None:
        raise DocumentNotFoundError(document_id)

    update_data = update.model_dump(exclude_unset = True)

    for field, value in update_data.items():
        setattr(db_document, field, value)

    db.commit()
    db.refresh(db_document)

    return db_document


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    statement = select(Document).where(Document.id == document_id)
    db_document = db.scalar(statement)
    
    if db_document is None:
        raise DocumentNotFoundError(document_id)

    db.delete(db_document)
    db.commit()

    return Response(status_code = status.HTTP_204_NO_CONTENT)


@router.get(
        "",
        response_model = list[DocumentResponse]
)
def list_documents(
    pagination: dict = Depends(pagination_params),
    db: Session = Depends(get_db)
):
    statement = (
        select(Document)
        .order_by(Document.id)
        .offset(pagination["offset"])
        .limit(pagination["limit"])
    )

    documents = db.scalars(statement).all()

    return documents
