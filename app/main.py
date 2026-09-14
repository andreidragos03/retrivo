from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.exception_handlers import register_exception_handlers
from app.routers.documents import router as documents_router


app = FastAPI()


register_exception_handlers(app)


app.include_router(documents_router)


@app.get("/")
async def root():
    return {"message": "Retrivo is running"}
