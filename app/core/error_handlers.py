from app.core.http_exceptions import HttpException
from app.schemas.client_response import ClientResponse

from fastapi.responses import JSONResponse
from fastapi import Request


async def http_exception_handler(request: Request, exc: HttpException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=ClientResponse.error(
            detail=exc.detail,
        ).model_dump()
    )