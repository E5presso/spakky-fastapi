from typing import ClassVar

from fastapi import status
from fastapi.responses import ORJSONResponse
from spakky.core.error import SpakkyCoreError


class SpakkyFastAPIError(SpakkyCoreError):
    status_code: ClassVar[int]

    def __init__(self, error: SpakkyCoreError) -> None:
        self.message = error.message
        self.args = error.args

    def to_response(self) -> ORJSONResponse:
        return ORJSONResponse(
            content={
                "message": self.message,
                "args": [str(x) for x in self.args],
            },
            status_code=self.status_code,
        )


class SpakkyUnknownError(SpakkyCoreError):
    message = "알 수 없는 오류가 발생했습니다."


class BadRequest(SpakkyFastAPIError):
    status_code: ClassVar[int] = status.HTTP_400_BAD_REQUEST


class Unauthorized(SpakkyFastAPIError):
    status_code: ClassVar[int] = status.HTTP_401_UNAUTHORIZED


class Forbidden(SpakkyFastAPIError):
    status_code: ClassVar[int] = status.HTTP_403_FORBIDDEN


class NotFound(SpakkyFastAPIError):
    status_code: ClassVar[int] = status.HTTP_404_NOT_FOUND


class Conflict(SpakkyFastAPIError):
    status_code: ClassVar[int] = status.HTTP_409_CONFLICT


class InternalServerError(SpakkyFastAPIError):
    status_code: ClassVar[int] = status.HTTP_500_INTERNAL_SERVER_ERROR
    stacktrace: str | None

    def __init__(self, error: Exception, stacktrace: str | None) -> None:
        super().__init__(SpakkyUnknownError(error.args))
        self.stacktrace = stacktrace

    def to_response(self) -> ORJSONResponse:
        return ORJSONResponse(
            content={
                "message": self.message,
                "args": [str(x) for x in self.args],
                "stacktrace": self.stacktrace,
            },
            status_code=self.status_code,
        )
