from typing import Awaitable, Callable, TypeAlias

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, DispatchFunction
from starlette.responses import Response
from starlette.types import ASGIApp

from spakky_fastapi.error import AbstractSpakkyFastAPIError, InternalServerError

Next: TypeAlias = Callable[[Request], Awaitable[Response]]


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
        except AbstractSpakkyFastAPIError as e:
            return e.to_response()
        except Exception:
            return InternalServerError().to_response(self.__debug)
