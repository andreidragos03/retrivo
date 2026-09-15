from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.document import Document


def test_get_existing_document(
    client: TestClient,
    db: Session
):
    document = Document(
        title = "Example document",
        content = "Example content"
    )

    db.add(document)
    db.commit()
    db.refresh(document)
    
    response = client.get(f"/documents/{document.id}")

    assert response.status_code == 200
    assert response.json() == {
        "id": document.id,
        "title": "Example document",
        "content": "Example content",
    }

def test_get_missing_document(
    client: TestClient
):
    response = client.get("/documents/999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Document 999 not found"
    }

def test_create_document(
    client: TestClient,
    db: Session
):
    response = client.post(
        "/documents",
        json = {
            "title": "My document",
            "content": "Hello Retrivo"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["title"] == "My document"
    assert data["content"] == "Hello Retrivo"

    db_document = db.get(Document, data["id"])

    assert db_document is not None
    assert db_document.title == "My document"
    assert db_document.content == "Hello Retrivo"

def test_create_document_with_empty_title(
    client: TestClient
):
    response = client.post(
        "/documents",
        json = {
            "title": "",
            "content": "Hello Retrivo"
        }
    )

    assert response.status_code == 422

def test_patch_document(
    client: TestClient,
    db: Session
):
    document = Document(
        title = "Original title",
        content = "Original content"
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
    assert response.json() == {
        "id": document.id,
        "title": "Updated title",
        "content": "Original content"
    }

    db.refresh(document)

    assert document.title == "Updated title"
    assert document.content == "Original content"

def test_delete_document(
    client: TestClient,
    db: Session
):
    document = Document(
        title = "Document to delete",
        content = "This document will be deleted"
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
        Document(title="Document 1", content="Content 1"),
        Document(title="Document 2", content="Content 2"),
        Document(title="Document 3", content="Content 3"),
        Document(title="Document 4", content="Content 4"),
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
