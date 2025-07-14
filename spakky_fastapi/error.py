import traceback
from abc import ABC
from typing import ClassVar

from fastapi import status
from fastapi.responses import JSONResponse, ORJSONResponse
from spakky.core.error import AbstractSpakkyCoreError


class AbstractSpakkyFastAPIError(AbstractSpakkyCoreError, ABC):
    status_code: ClassVar[int]

    def __init__(self, *args: object) -> None:
        super().__init__(*args)

    def to_response(self, show_traceback: bool) -> JSONResponse:
        return ORJSONResponse(
            content={
                "message": self.message,
                "args": [str(x) for x in self.args],
                "traceback": traceback.format_exc() if show_traceback else None,
            },
            status_code=self.status_code,
        )


class BadRequest(AbstractSpakkyFastAPIError):
    message: ClassVar[str] = "Bad Request"
    status_code: ClassVar[int] = status.HTTP_400_BAD_REQUEST


class Unauthorized(AbstractSpakkyFastAPIError):
    message: ClassVar[str] = "Unauthorized"
    status_code: ClassVar[int] = status.HTTP_401_UNAUTHORIZED


class Forbidden(AbstractSpakkyFastAPIError):
    message: ClassVar[str] = "Forbidden"
    status_code: ClassVar[int] = status.HTTP_403_FORBIDDEN


class NotFound(AbstractSpakkyFastAPIError):
    message: ClassVar[str] = "Not Found"
    status_code: ClassVar[int] = status.HTTP_404_NOT_FOUND


class Conflict(AbstractSpakkyFastAPIError):
    message: ClassVar[str] = "Conflict"
    status_code: ClassVar[int] = status.HTTP_409_CONFLICT


class InternalServerError(AbstractSpakkyFastAPIError):
    message: ClassVar[str] = "Internal Server Error"
    status_code: ClassVar[int] = status.HTTP_500_INTERNAL_SERVER_ERROR
