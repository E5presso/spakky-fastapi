from http import HTTPStatus
from uuid import UUID, uuid4
from datetime import timedelta

from fastapi import FastAPI
from fastapi.testclient import TestClient
from spakky.cryptography.jwt import JWT
from spakky.cryptography.key import Key


def test_get(app: FastAPI) -> None:
    with TestClient(app) as client:
        response = client.get("/dummy")
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


def test_websocket(app: FastAPI) -> None:
    client = TestClient(app)
    with client.websocket_connect("/dummy/ws") as socket:
        socket.send_text("Hello World!")
        received: str = socket.receive_text()
        assert received == "Hello World!"


def test_token_authentification(app: FastAPI) -> None:
    with TestClient(app) as client:
        response = client.get("/dummy/login?username=John")
        assert response.status_code == HTTPStatus.OK
        response = client.get(
            url="/dummy/users/me?name=John&age=30",
            headers={"Authorization": f"Bearer {response.json()}"},
        )
        assert response.status_code == HTTPStatus.OK
        assert response.text == "John"


def test_token_authentification_with_wrong_token(app: FastAPI) -> None:
    with TestClient(app) as client:
        response = client.get(
            url="/dummy/users/me?name=John&age=30",
            headers={"Authorization": "Bearer undefined"},
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_token_authentification_without_extra_parameters(app: FastAPI) -> None:
    with TestClient(app) as client:
        response = client.get("/dummy/login?username=John")
        assert response.status_code == HTTPStatus.OK
        response = client.get(
            url="/dummy/users/profile",
            headers={"Authorization": f"Bearer {response.json()}"},
        )
        assert response.status_code == HTTPStatus.OK
        assert response.text == "John"


def test_token_authentification_without_token(app: FastAPI) -> None:
    with TestClient(app) as client:
        response = client.get(url="/dummy/users/profile")
        assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_token_authentification_with_expired_token(app: FastAPI, key: Key) -> None:
    token = (
        JWT()
        .set_expiration(timedelta(days=-30))
        .set_payload(username="John")
        .sign(key)
        .export()
    )
    with TestClient(app) as client:
        response = client.get(
            url="/dummy/users/profile",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_token_authentification_with_invalid_signature(app: FastAPI) -> None:
    token = (
        JWT()
        .set_expiration(timedelta(days=30))
        .set_payload(username="John")
        .sign(Key(size=32))
        .export()
    )
    with TestClient(app) as client:
        response = client.get(
            url="/dummy/users/profile",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_async_token_authentification_with_wrong_token(app: FastAPI) -> None:
    with TestClient(app) as client:
        response = client.get(
            url="/dummy/users/profile",
            headers={"Authorization": "Bearer undefined"},
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_async_token_authentification_without_extra_parameters(app: FastAPI) -> None:
    with TestClient(app) as client:
        response = client.get("/dummy/login?username=John")
        assert response.status_code == HTTPStatus.OK
        response = client.get(
            url="/dummy/users/profile/async",
            headers={"Authorization": f"Bearer {response.json()}"},
        )
        assert response.status_code == HTTPStatus.OK
        assert response.text == "John"


def test_async_token_authentification_without_token(app: FastAPI) -> None:
    with TestClient(app) as client:
        response = client.get(url="/dummy/users/profile/async")
        assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_async_token_authentification_with_expired_token(app: FastAPI, key: Key) -> None:
    token = (
        JWT()
        .set_expiration(timedelta(days=-30))
        .set_payload(username="John")
        .sign(key)
        .export()
    )
    with TestClient(app) as client:
        response = client.get(
            url="/dummy/users/profile/async",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_async_token_authentification_with_invalid_signature(app: FastAPI) -> None:
    token = (
        JWT()
        .set_expiration(timedelta(days=30))
        .set_payload(username="John")
        .sign(Key(size=32))
        .export()
    )
    with TestClient(app) as client:
        response = client.get(
            url="/dummy/users/profile/async",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_when_unexpected_error_ocurred(app: FastAPI) -> None:
    with TestClient(app) as client:
        response = client.get(url="/dummy/error")
        assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert response.json()["message"] == "알 수 없는 오류가 발생했습니다."
