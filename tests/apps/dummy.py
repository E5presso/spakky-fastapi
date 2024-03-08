from uuid import UUID
from datetime import timedelta

from fastapi import Depends, WebSocket
from fastapi.responses import FileResponse, PlainTextResponse
from pydantic import BaseModel
from spakky.bean.autowired import autowired
from spakky.cryptography.jwt import JWT
from spakky.cryptography.key import Key
from spakky.extensions.logging import AsyncLogging
from spakky.stereotype.controller import Controller
from spakky.stereotype.usecase import UseCase
from spakky_fastapi.jwt_auth import JWTAuth
from spakky_fastapi.routing import (
    delete,
    get,
    head,
    options,
    patch,
    post,
    put,
    websocket,
)


class Dummy(BaseModel):
    name: str
    age: int


@Controller("/dummy")
class DummyController:
    __key: Key

    @autowired
    def __init__(self, key: Key) -> None:
        self.__key = key

    async def just_function(self) -> str:
        return "Just Function!"

    @AsyncLogging()
    @get("", response_class=PlainTextResponse)
    async def get_dummy(self) -> str:
        return "Hello World!"

    @AsyncLogging()
    @get(
        "/file/{name}",
        response_class=FileResponse,
        description="Get file by given name",
    )
    async def get_file(self, name: str) -> str:
        return f"tests/apps/{name}"

    @AsyncLogging()
    @get(
        "/file-without-response-class/{name}",
        description="Get file by given name",
    )
    async def get_file_without_response_class(self, name: str) -> FileResponse:
        return FileResponse(f"tests/apps/{name}")

    @AsyncLogging()
    @post("")
    async def post_dummy(self, dummy: Dummy) -> Dummy:
        return dummy

    @AsyncLogging()
    @put("")
    async def put_dummy(self, dummy: Dummy) -> Dummy:
        return dummy

    @AsyncLogging()
    @patch("")
    async def patch_dummy(self, dummy: Dummy) -> Dummy:
        return dummy

    @AsyncLogging()
    @delete("/{id}")
    async def delete_dummy(self, id: UUID) -> UUID:
        return id

    @AsyncLogging()
    @head("", response_class=PlainTextResponse)
    async def head_dummy(self) -> None:
        ...

    @AsyncLogging()
    @options("", response_class=PlainTextResponse)
    async def options_dummy(self) -> str:
        return "Hello Options!"

    @AsyncLogging()
    @websocket("/ws")
    async def websocket_dummy(self, socket: WebSocket) -> None:
        await socket.accept()
        message: str = await socket.receive_text()
        await socket.send_text(message)
        await socket.close()

    @AsyncLogging()
    @get("/login")
    async def login(self, username: str) -> str:
        return (
            JWT()
            .set_expiration(timedelta(days=30))
            .set_payload(username=username)
            .sign(self.__key)
            .export()
        )

    @AsyncLogging()
    @JWTAuth("login")
    @get("/users/me", response_class=PlainTextResponse)
    async def get_user(self, token: JWT, request: Dummy = Depends()) -> str:
        print(request)
        return token.payload["username"]

    @AsyncLogging()
    @JWTAuth("login")
    @get("/users/profile", response_class=PlainTextResponse)
    async def get_profile(self, token: JWT) -> str:
        return token.payload["username"]


@UseCase()
class DummyUseCase:
    ...
