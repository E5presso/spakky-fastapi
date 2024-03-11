from typing import Callable, Awaitable, TypeAlias

from fastapi import Request
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel
from spakky_fastapi.error import InternalServerError, SpakkyFastAPIError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

Next: TypeAlias = Callable[[Request], Awaitable[Response]]


class ErrorResponse(BaseModel):
    message: str
    args: list[str]


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
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
            error = InternalServerError(e)
            return ORJSONResponse(
                content=ErrorResponse(
                    message=error.message,
                    args=[str(x) for x in error.args],
                ).model_dump(),
                status_code=error.status_code,
            )
