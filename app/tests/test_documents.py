from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_get_existing_document():
    response = client.get("/documents/1")

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "title": "Example document",
        "content": "Example content",
    }

def test_get_missing_document():
    response = client.get("/documents/999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Document 999 not found"
    }

def test_create_document():
    response = client.post(
        "/documents",
        json = {
            "title": "My document",
            "content": "Hello Retrivo"
        }
    )

    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        "title": "My document",
        "content": "Hello Retrivo"
    }

def test_create_document_with_empty_title():
    response = client.post(
        "/documents",
        json = {
            "title": "",
            "content": "Hello"
        }
    )

    assert response.status_code == 422

def test_patch_document():
    response = client.patch(
        "/documents/1",
        json = {
            "title": "Updated title"
        }
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "title": "Updated title",
        "content": "Example content"
    }

def test_delete_document():
    response = client.delete("/documents/1")

    assert response.status_code == 204
    assert response.content == b""

def test_list_documents_with_pagination():
    response = client.get(
        "/documents",
        params = {
            "limit": 5,
            "offset": 10
        }
    )

    assert response.status_code == 200
    assert response.json() == {
        "limit": 5,
        "offset": 10,
        "documents": []
    }

def test_invalid_pagination_limit():
    response = client.get(
        "/documents",
        params = {
            "limit": 500,
        }
    )

    assert response.status_code == 422
