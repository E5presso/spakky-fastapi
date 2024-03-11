from typing import Callable, Awaitable, TypeAlias
from dataclasses import InitVar

from fastapi import Request
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel, Field
from spakky_fastapi.error import SpakkyFastAPIError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

Next: TypeAlias = Callable[[Request], Awaitable[Response]]


class ErrorResponse(BaseModel):
    error: InitVar[SpakkyFastAPIError]
    message: str = Field(init=False)
    args: list[str] = Field(init=False)

    def __post_init__(self, error: SpakkyFastAPIError) -> None:
        self.message = error.message
        self.args = [str(x) for x in error.args]


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Next) -> Response:
        try:
            return await super().dispatch(request, call_next)
        except SpakkyFastAPIError as e:
            return ORJSONResponse(
                content=ErrorResponse(error=e).model_dump(),
                status_code=e.status_code,
            )
