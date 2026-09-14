from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.dependencies import pagination_params
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


@router.get("")
async def list_documents(
    pagination: dict = Depends(pagination_params),
):
    return {
        "limit": pagination["limit"],
        "offset": pagination["offset"],
        "documents": [],
    }


@router.post(
    "",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_document(document: DocumentCreate):
    return DocumentResponse(
        id=1,
        title=document.title,
        content=document.content,
    )


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
)
async def get_document(document_id: int):
    if document_id != 1:
        raise DocumentNotFoundError(document_id)

    return DocumentResponse(
        id=document_id,
        title="Example document",
        content="Example content",
    )


@router.patch(
    "/{document_id}",
    response_model=DocumentResponse,
)
async def update_document(
    document_id: int,
    update: DocumentUpdate,
):
    if document_id != 1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    existing_document = {
        "id": document_id,
        "title": "Example document",
        "content": "Example content",
    }

    update_data = update.model_dump(exclude_unset=True)
    existing_document.update(update_data)

    return DocumentResponse(**existing_document)


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_document(document_id: int):
    if document_id != 1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
