from typing import AsyncGenerator

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_maker
from app.core.http_exceptions import InvalidTokenError, UnauthorizedError
from app.database import ServiceDAO
from app.models import Service

bearer_scheme = HTTPBearer()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a database session for FastAPI dependencies.

    Opens an async database session for an endpoint request, yields it to the
    endpoint handler, commits the transaction after successful execution, and
    rolls it back if an exception occurs.

    Yields:
        Active async database session.

    Raises:
        Exception: Re-raises any exception after rolling back the transaction.
    """
    async with async_session_maker() as session:
        try:
            yield session

            await session.commit()

        except Exception:
            await session.rollback()
            raise


async def get_current_issuer(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    session: AsyncSession = Depends(get_session),
) -> Service:
    """Authenticate the current service from a JWT bearer token.

    FastAPI dependency that extracts the bearer token, validates required JWT
    claims, finds the issuer service, verifies the token signature using the
    service JWT secret, and returns the authenticated service.

    Args:
        credentials: HTTP bearer credentials from the Authorization header.
        session: Active database session.

    Returns:
        Authenticated service that called the endpoint.

    Raises:
        UnauthorizedError: If the token cannot be decoded or the issuer service
            does not exist.
        InvalidTokenError: If the token is missing required claims, has an invalid
            signature, or is expired.
    """
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
