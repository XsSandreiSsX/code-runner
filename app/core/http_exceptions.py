from fastapi import status

class HttpException(Exception):
    status_code: int = status.HTTP_400_BAD_REQUEST
    detail = "Bad Request"

    def __init__(self, detail: str | None = None) -> None:
        if detail is not None:
            self.detail = detail


class ConflictError(HttpException):
    status_code = status.HTTP_409_CONFLICT

