from fastapi import APIRouter, Depends, HTTPException, Response, status, File, Form, UploadFile

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.exceptions import DocumentNotFoundError
from app.dependencies import get_db, pagination_params
from app.schemas.documents import (
    DocumentCreate,
    DocumentResponse,
    DocumentUpdate,
)
from app.repositories.documents import(
    get_document_by_id,
    update_document as update_document_in_db,
    delete_document as delete_document_in_db,
    list_documents as list_documents_from_db
)
from app.extractors.exceptions import DocumentExtractionError
from app.extractors.pdf import extract_text_from_pdf
from app.services.ingestion import create_pending_document, process_pdf_document


router = APIRouter(
    prefix="/documents",
    tags=["documents"],
)


@router.post(
    "/upload",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    title: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=415,
            detail="Unsupported file type. Only PDF files are supported.",
        )

    if not file.filename:
        raise HTTPException(
            status_code=422,
            detail="The uploaded file must have a filename.",
        )

    file_bytes = await file.read()

    document = create_pending_document(
        db=db,
        title=title,
        filename=file.filename,
        content_type=file.content_type,
    )

    try:
        document = process_pdf_document(
            db=db,
            document=document,
            file_bytes=file_bytes,
        )
    except DocumentExtractionError:
        raise HTTPException(
            status_code=422,
            detail="The uploaded PDF could not be processed.",
        )

    return document


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
