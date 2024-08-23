import traceback
from typing import Callable, Awaitable, TypeAlias

from fastapi import Request
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel
from starlette.middleware.base import BaseHTTPMiddleware, DispatchFunction
from starlette.responses import Response
from starlette.types import ASGIApp

from spakky_fastapi.error import InternalServerError, SpakkyFastAPIError

Next: TypeAlias = Callable[[Request], Awaitable[Response]]


class ErrorResponse(BaseModel):
    message: str
    args: list[str]
    traceback: str = ""


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    __debug: bool

    def __init__(
        self,
        app: ASGIApp,
        dispatch: DispatchFunction | None = None,
        debug: bool = False,
    ) -> None:
        super().__init__(app, dispatch)
        self.__debug = debug

    async def dispatch(self, request: Request, call_next: Next) -> Response:
        try:
            return await call_next(request)
        except SpakkyFastAPIError as e:
            return ORJSONResponse(
                content=ErrorResponse(
                    message=e.message,
                    args=[str(x) for x in e.args],
                ).model_dump(),
                status_code=e.status_code,
            )
        # pylint: disable=broad-exception-caught
        except Exception as e:
            if self.__debug:
                traceback.print_exc()  # pragma: no cover
            error = InternalServerError(e)
            return ORJSONResponse(
                content=ErrorResponse(
                    message=error.message,
                    args=[str(x) for x in error.args],
                    traceback=error.traceback if self.__debug else "",
                ).model_dump(),
                status_code=error.status_code,
            )
