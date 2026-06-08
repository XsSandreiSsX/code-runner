import secrets

from app.core.app_exceptions import ServiceAlreadyExistsError, ServiceDoesNotExistsError
from app.core.database import async_session_maker
from app.database import ServiceDAO
from app.models.service import Service


async def add_service(name: str) -> Service:
    """Create a service for CLI usage.

    Generates a JWT secret, creates a new service record, and returns the
    created service.

    Args:
        name: Unique service name.

    Returns:
        Created service.

    Raises:
        ServiceAlreadyExistsError: If a service with the given name already
            exists.
    """
    async with async_session_maker() as session:
        existing = await ServiceDAO.get_one_or_none(session, name=name)
        if existing:
            raise ServiceAlreadyExistsError()

        secret = secrets.token_hex(32)
        service = await ServiceDAO.add(session, {"name": name, "jwt_secret": secret})
        await session.commit()

    return service


async def delete_service(name: str) -> Service:
    """Delete a service for CLI usage.

    Finds a service by name, deletes it from the database, and returns the
    deleted service object.

    Args:
        name: Name of the service to delete.

    Returns:
        Deleted service.

    Raises:
        ServiceDoesNotExistsError: If the service with the given name does not
            exist.
    """
    async with async_session_maker() as session:
        service = await ServiceDAO.get_one_or_none(session, name=name)
        if not service:
            raise ServiceDoesNotExistsError()

        await ServiceDAO.delete_obj(session, obj=service)
        await session.commit()

    return service


async def refresh_jwt(name: str) -> Service:
    """Refresh a service JWT secret for CLI usage.

    Finds a service by name, generates a new JWT secret, updates the service,
    and returns the updated service.

    Args:
        name: Name of the service whose JWT secret should be refreshed.

    Returns:
        Updated service.

    Raises:
        ServiceDoesNotExistsError: If the service with the given name does not
            exist.
    """
    async with async_session_maker() as session:
        service = await ServiceDAO.get_one_or_none(session, name=name)
        if not service:
            raise ServiceDoesNotExistsError()

        new_jwt = secrets.token_hex(32)
        await ServiceDAO.update_obj(session, {"jwt_secret": new_jwt}, obj=service)
        await session.commit()

    return service