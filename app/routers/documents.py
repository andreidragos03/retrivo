from fastapi import APIRouter, Depends, HTTPException, Response, status

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.exceptions import DocumentNotFoundError
from app.dependencies import get_db, pagination_params
from app.models.document import Document
from app.schemas.documents import (
    DocumentCreate,
    DocumentResponse,
    DocumentUpdate,
)
from app.repositories.documents import(
    create_document as create_document_in_db,
    get_document_by_id,
    update_document as update_document_in_db,
    delete_document as delete_document_in_db,
    list_documents as list_documents_from_db
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
    db_document = create_document_in_db(
        db = db,
        title = document.title,
        content = document.content
    )

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
    db_document = get_document_by_id(db, document_id)

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
    db_document = get_document_by_id(db, document_id)
    
    if db_document is None:
        raise DocumentNotFoundError(document_id)
    

    update_data = update.model_dump(exclude_unset = True)

    db_document = update_document_in_db(db, db_document, update_data)

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
    db_document = get_document_by_id(db, document_id)
    
    if db_document is None:
        raise DocumentNotFoundError(document_id)

    delete_document_in_db(db, db_document)
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
    documents = list_documents_from_db(
        db,
        pagination["offset"],
        pagination["limit"]
    )

    return documents
