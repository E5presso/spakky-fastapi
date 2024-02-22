from http import HTTPStatus
from uuid import UUID, uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient


def test_get(app: FastAPI) -> None:
    with TestClient(app) as client:
        response = client.get(f"/dummy")
        assert response.status_code == HTTPStatus.OK
        assert response.text == "Hello World!"


def test_post(app: FastAPI) -> None:
    with TestClient(app) as client:
        response = client.post("/dummy", json={"name": "John", "age": 30})
        assert response.status_code == HTTPStatus.OK
        assert response.json() == {"name": "John", "age": 30}


def test_put(app: FastAPI) -> None:
    with TestClient(app) as client:
        response = client.put("/dummy", json={"name": "John", "age": 30})
        assert response.status_code == HTTPStatus.OK
        assert response.json() == {"name": "John", "age": 30}


def test_patch(app: FastAPI) -> None:
    with TestClient(app) as client:
        response = client.patch("/dummy", json={"name": "John", "age": 30})
        assert response.status_code == HTTPStatus.OK
        assert response.json() == {"name": "John", "age": 30}


def test_delete(app: FastAPI) -> None:
    with TestClient(app) as client:
        id: UUID = uuid4()
        response = client.delete(f"/dummy/{id}")
        assert response.status_code == HTTPStatus.OK
        assert response.text == f'"{id}"'


def test_head(app: FastAPI) -> None:
    with TestClient(app) as client:
        response = client.head("/dummy")
        assert response.status_code == HTTPStatus.OK


def test_options(app: FastAPI) -> None:
    with TestClient(app) as client:
        response = client.options("/dummy")
        assert response.status_code == HTTPStatus.OK
        assert response.text == "Hello Options!"


def test_file(app: FastAPI) -> None:
    with TestClient(app) as client:
        response = client.get("/dummy/file/dummy.txt")
        assert response.status_code == HTTPStatus.OK
        assert response.text == "Hello File!"


def test_file_without_response_class(app: FastAPI) -> None:
    with TestClient(app) as client:
        response = client.get("/dummy/file-without-response-class/dummy.txt")
        assert response.status_code == HTTPStatus.OK
        assert response.text == "Hello File!"
