import pymupdf
import pytest

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.extractors.pdf import extract_text_from_pdf
from app.models.document import Document, DocumentStatus
from app.models.document_chunk import DocumentChunk


def create_test_pdf(text: str) -> bytes:
    document = pymupdf.open()

    page = document.new_page()
    page.insert_text(
        (72, 72),
        text
    )

    pdf_bytes = document.tobytes()
    document.close()

    return pdf_bytes

def create_test_pdf_with_lines(lines: list[str]) -> bytes:
    document = pymupdf.open()

    page = document.new_page()

    y = 72

    for line in lines:
        page.insert_text(
            (72, y),
            line,
        )
        y += 15

    pdf_bytes = document.tobytes()
    document.close()

    return pdf_bytes

def fail_to_create_chunks(*args, **kwargs):
    raise RuntimeError("Simulated chunk persistence failure")


def test_upload_pdf_creates_ready_document_and_chunks(
    client: TestClient,
    db: Session
):
    pdf_bytes = create_test_pdf(
        "Retrivo can extract and chunk PDF documents."
    )

    response = client.post(
        "/documents/upload",
        data = {
            "title": "Retrivo Test Document"
        },
        files = {
            "file": (
                "retrivo-test.pdf",
                pdf_bytes,
                "application/pdf"
            )
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["title"] == "Retrivo Test Document"
    assert data["filename"] == "retrivo-test.pdf"
    assert data["content_type"] == "application/pdf"
    assert data["status"] == "ready"
    assert data["content"] is not None
    assert "Retrivo can extract and chunk PDF documents." in data["content"]
    assert data["created_at"] is not None

    document_id = data["id"]

    chunks = db.scalars(
        select(DocumentChunk)
        .where(DocumentChunk.document_id == document_id)
        .order_by(DocumentChunk.chunk_index)
    ).all()

    assert len(chunks) == 1

    assert chunks[0].document_id == document_id
    assert chunks[0].chunk_index == 0
    assert "Retrivo can extract and chunk PDF documents." in chunks[0].content

def test_invalid_pdf_marks_document_failed_without_chunks(
    client: TestClient,
    db: Session
):
    response = client.post(
        "/documents/upload",
        data = {
            "title": "Broken PDF"
        },
        files = {
            "file": (
                "broken.pdf",
                b"This is not actually a PDF.",
                "application/pdf"
            )
        }
    )

    assert response.status_code == 422

    document = db.scalar(
        select(Document)
        .where(Document.title == "Broken PDF")
    )

    assert document is not None
    assert document.status == DocumentStatus.FAILED
    assert document.content is None

    chunks = db.scalars(
        select(DocumentChunk)
        .where(DocumentChunk.document_id == document.id)
    ).all()

    assert chunks == []

def test_processing_failure_rolls_back_content_and_marks_document_failed(
    client: TestClient,
    db: Session,
    monkeypatch
):
    monkeypatch.setattr(
        "app.services.ingestion.create_document_chunks",
        fail_to_create_chunks,
    )

    pdf_bytes = create_test_pdf(
        "This text should be extracted successfully before chunk persistence fails."
    )

    with pytest.raises(
        RuntimeError,
        match = "Simulated chunk persistence failure"
    ):
        client.post(
            "/documents/upload",
            data = {
                "title": "Chunk Failure Document"
            },
            files = {
                "file": (
                    "chunk-failure.pdf",
                    pdf_bytes,
                    "application/pdf"
                )
            }
        )

    document = db.scalar(
        select(Document)
        .where(Document.title == "Chunk Failure Document")
    )

    assert document is not None
    assert document.status == DocumentStatus.FAILED
    assert document.content is None

    chunks = db.scalars(
        select(DocumentChunk)
        .where(DocumentChunk.document_id == document.id)
    ).all()

    assert chunks == []

def test_upload_long_pdf_creates_multiple_ordered_chunks(
    client: TestClient,
    db: Session,
):
    lines = [
        f"This is Retrivo test sentence number {index}."
        for index in range(40)
    ]

    pdf_bytes = create_test_pdf_with_lines(lines)

    response = client.post(
        "/documents/upload",
        data={
            "title": "Long Retrivo Document",
        },
        files={
            "file": (
                "long-document.pdf",
                pdf_bytes,
                "application/pdf",
            )
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["status"] == "ready"

    document_id = data["id"]

    chunks = db.scalars(
        select(DocumentChunk)
        .where(DocumentChunk.document_id == document_id)
        .order_by(DocumentChunk.chunk_index)
    ).all()

    assert len(chunks) > 1

    assert [chunk.chunk_index for chunk in chunks] == list(
        range(len(chunks))
    )

    assert all(
        len(chunk.content) <= 1000
        for chunk in chunks
    )
