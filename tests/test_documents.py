from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.document import Document


def create_test_document(
    title: str = "Example document",
    content: str | None = "Example content",
) -> Document:
    return Document(
        title=title,
        filename="test.pdf",
        content_type="application/pdf",
        content=content,
    )


def test_get_existing_document(
    client: TestClient,
    db: Session
):
    document = create_test_document(
        title="Example document",
        content="Example content",
    )

    db.add(document)
    db.commit()
    db.refresh(document)
    
    response = client.get(f"/documents/{document.id}")

    data = response.json()

    assert data["id"] == document.id
    assert data["title"] == "Example document"
    assert data["filename"] == "test.pdf"
    assert data["content_type"] == "application/pdf"
    assert data["content"] == "Example content"
    assert data["status"] == "pending"
    assert data["created_at"] is not None

def test_get_missing_document(
    client: TestClient
):
    response = client.get("/documents/999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Document 999 not found"
    }

def test_patch_document(
    client: TestClient,
    db: Session
):
    document = create_test_document(
        title="Example document",
        content="Example content",
    )

    db.add(document)
    db.commit()
    db.refresh(document)
    
    response = client.patch(
        f"/documents/{document.id}",
        json = {
            "title": "Updated title"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == document.id
    assert data["title"] == "Updated title"
    assert data["filename"] == "test.pdf"
    assert data["content_type"] == "application/pdf"
    assert data["content"] == "Example content"
    assert data["status"] == "pending"
    assert data["created_at"] is not None

    db.refresh(document)

    assert document.title == "Updated title"
    assert document.content == "Example content"

def test_delete_document(
    client: TestClient,
    db: Session
):
    document = create_test_document(
        title="Example document",
        content="Example content",
    )

    db.add(document)
    db.commit()
    db.refresh(document)
    
    response = client.delete(f"/documents/{document.id}")

    assert response.status_code == 204
    assert response.content == b""

    db.expire_all()

    deleted_document = db.get(Document, document.id)

    assert deleted_document is None

def test_list_documents_with_pagination(
    client: TestClient,
    db: Session
):
    documents = [
        create_test_document(title="Document 1", content="Content 1"),
        create_test_document(title="Document 2", content="Content 2"),
        create_test_document(title="Document 3", content="Content 3"),
        create_test_document(title="Document 4", content="Content 4"),
    ]

    db.add_all(documents)
    db.commit()

    response = client.get(
        "/documents",
        params = {
            "limit": 2,
            "offset": 1
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["title"] == "Document 2"
    assert data[1]["title"] == "Document 3"

def test_invalid_pagination_limit(
    client: TestClient
):
    response = client.get(
        "/documents",
        params = {
            "limit": 0,
            "offset": 0
        }
    )

    assert response.status_code == 422

def test_patch_document_rejects_null_title(
    client: TestClient,
    db: Session
):
    document = create_test_document(
        title="Example document",
        content="Example content",
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    response = client.patch(
        f"/documents/{document.id}",
        json = {"title": None}
    )

    assert response.status_code == 422
