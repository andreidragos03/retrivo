from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.exceptions import DocumentNotFoundError


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(DocumentNotFoundError)
    async def document_not_found_handler(
        request: Request,
        exc: DocumentNotFoundError,
    ):
        return JSONResponse(
            status_code=404,
            content={
                "detail": f"Document {exc.document_id} not found"
            },
        )
