from uuid import UUID

from fastapi import WebSocket
from fastapi.responses import FileResponse, PlainTextResponse
from pydantic import BaseModel
from spakky.stereotype.controller import Controller
from spakky.stereotype.usecase import UseCase
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
    async def just_function(self) -> str:
        return "Just Function!"

    @get("", response_class=PlainTextResponse)
    async def get_dummy(self) -> str:
        return "Hello World!"

    @get(
        "/file/{name}",
        response_class=FileResponse,
        description="Get file by given name",
    )
    async def get_file(self, name: str) -> str:
        return f"tests/apps/{name}"

    @get(
        "/file-without-response-class/{name}",
        description="Get file by given name",
    )
    async def get_file_without_response_class(self, name: str) -> FileResponse:
        return FileResponse(f"tests/apps/{name}")

    @post("")
    async def post_dummy(self, dummy: Dummy) -> Dummy:
        return dummy

    @put("")
    async def put_dummy(self, dummy: Dummy) -> Dummy:
        return dummy

    @patch("")
    async def patch_dummy(self, dummy: Dummy) -> Dummy:
        return dummy

    @delete("/{id}")
    async def delete_dummy(self, id: UUID) -> UUID:
        return id

    @head("", response_class=PlainTextResponse)
    async def head_dummy(self) -> None:
        ...

    @options("", response_class=PlainTextResponse)
    async def options_dummy(self) -> str:
        return "Hello Options!"

    @websocket("/ws")
    async def websocket_dummy(self, socket: WebSocket) -> None:
        await socket.accept()
        message: str = await socket.receive_text()
        await socket.send_text(message)
        await socket.close()


@UseCase()
class DummyUseCase:
    ...
