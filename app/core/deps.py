from app.core.database import async_session_maker
from app.core.http_exceptions import UnauthorizedError, InvalidTokenError
from app.models import Service

from app.database import ServiceDAO

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi import Depends
from typing import AsyncGenerator

import jwt


bearer_scheme = HTTPBearer()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session

            await session.commit()

        except Exception:
            await session.rollback()
            raise


async def get_current_issuer(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
                       session: AsyncSession = Depends(get_session)) -> Service:
    token = credentials.credentials

    try:
        payload = jwt.decode(token, options={"verify_signature": False})
    except jwt.exceptions.DecodeError:
        raise UnauthorizedError(detail="Unauthorized token")
    issuer = payload.get("iss")

    required = ("iss", "iat", "exp")
    for field in required:
        if field not in payload:
            raise InvalidTokenError(detail=f"Missing `{field}` in token")

    service = await ServiceDAO.get_one_or_none(session, name=issuer)
    if not service:
        raise UnauthorizedError(detail="Unauthorized service")

    try:
        jwt.decode(token, service.jwt_secret, algorithms=["HS256"])
    except (jwt.InvalidSignatureError, jwt.DecodeError):
        raise InvalidTokenError(detail="Invalid Authorization token")
    except jwt.ExpiredSignatureError:
        raise InvalidTokenError(detail="Expired Authorization token")

    return service