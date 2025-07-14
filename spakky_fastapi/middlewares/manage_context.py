from typing import Awaitable, Callable, TypeAlias

from fastapi import Request
from spakky.pod.interfaces.application_context import IApplicationContext
from starlette.middleware.base import BaseHTTPMiddleware, DispatchFunction
from starlette.responses import Response
from starlette.types import ASGIApp

Next: TypeAlias = Callable[[Request], Awaitable[Response]]


class ManageContextMiddleware(BaseHTTPMiddleware):
    __application_context: IApplicationContext

    def __init__(
        self,
        app: ASGIApp,
        application_context: IApplicationContext,
        dispatch: DispatchFunction | None = None,
    ) -> None:
        super().__init__(app, dispatch)
        self.__application_context = application_context

    async def dispatch(self, request: Request, call_next: Next) -> Response:
        self.__application_context.clear_context()
        return await call_next(request)
