from enum import Enum
from datetime import datetime

from sqlalchemy import DateTime, Enum as SQLEnum, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class DocumentStatus(str, Enum):
    PENDING = "pending",
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key = True
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable = False
    )

    filename: Mapped[str] = mapped_column(
        String(255),
        nullable = False
    )

    content_type: Mapped[str] = mapped_column(
        String(100),
        nullable = False
    )

    content: Mapped[str | None] = mapped_column(
        Text,
        nullable = True
    )

    status: Mapped[DocumentStatus] = mapped_column(
        SQLEnum(
            DocumentStatus,
            values_callable = lambda enum_class: [member.value for member in enum_class],
            name = "document_status"
        ),
        nullable = False,
        default = DocumentStatus.PENDING
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone = True),
        nullable = False,
        server_default = func.now()
    )
