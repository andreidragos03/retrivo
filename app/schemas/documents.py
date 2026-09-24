from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.document import DocumentStatus


class DocumentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1)


class DocumentUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )
    content: str | None = Field(
        default=None,
        min_length=1,
    )

    @field_validator("title", "content")
    @classmethod
    def reject_null(cls, value: str | None) -> str:
        if value is None:
            raise ValueError("Field cannot be null")

        return value


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes = True)

    id: int
    title: str
    filename: str
    content_type: str
    content: str | None
    status: DocumentStatus
    created_at: datetime
