import traceback

from fastapi import status
from spakky.core.error import SpakkyCoreError


class SpakkyFastAPIError(SpakkyCoreError):
    status_code: int

    def __init__(self, error: SpakkyCoreError) -> None:
        self.message = error.message
        self.args = error.args


class SpakkyUnknownError(SpakkyCoreError):
    message = "알 수 없는 오류가 발생했습니다."


class BadRequest(SpakkyFastAPIError):
    status_code: int = status.HTTP_400_BAD_REQUEST


class Unauthorized(SpakkyFastAPIError):
    status_code: int = status.HTTP_401_UNAUTHORIZED


class Forbidden(SpakkyFastAPIError):
    status_code: int = status.HTTP_403_FORBIDDEN


class NotFound(SpakkyFastAPIError):
    status_code: int = status.HTTP_404_NOT_FOUND


class Conflict(SpakkyFastAPIError):
    status_code: int = status.HTTP_409_CONFLICT


class InternalServerError(SpakkyFastAPIError):
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    traceback: str = ""

    def __init__(self, error: Exception) -> None:
        super().__init__(SpakkyUnknownError(error.args))
        self.traceback = traceback.format_exc()
