from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


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

    content: Mapped[str] = mapped_column(
        Text,
        nullable = False
    )
