from typing import Generic, Literal, Self, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ClientResponse(BaseModel, Generic[T]):
    status: Literal["success", "error"]
    data: T | None = None
    detail: str

    @classmethod
    def success(cls, detail: str, data: T | None = None) -> Self:
        response = cls(
            status="success",
            data=data,
            detail=detail,
        )
        return response

    @classmethod
    def error(cls, detail: str) -> Self:
        response = cls(
            status="error",
            detail=detail,
        )
        return response


class SwaggerError(BaseModel):
    status: Literal["error"]
    data: None = None
    detail: str
