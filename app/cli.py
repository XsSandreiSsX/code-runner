from app.core.deps import get_session
from app.database import ServiceDAO
from utils.jwt_test import generate_internal_jwt

from contextlib import asynccontextmanager
import secrets
import asyncio
import typer

get_session_context = asynccontextmanager(get_session)
cli = typer.Typer()

async def _add_service(name: str):
    async with get_session_context() as session:
        service = await ServiceDAO.add(session, {"name": name, "jwt_secret": secrets.token_hex(32)})
        typer.echo(f"A new service has been added. Save this jwt_secret - it is shown only once: {service.jwt_secret}")

        if typer.confirm("Generate a 15-minute test JWT token?"):
            typer.echo(
                f"Test token: {generate_internal_jwt(iss=service.name, jwt_secret=service.jwt_secret, ttl=900)}"
            )


async def _delete_service(name: str):
    async with get_session_context() as session:
        service = await ServiceDAO.get_one_or_none(session, name=name)
        if not service:
            typer.echo(f"Service with name {name} not found")
            return

        if typer.confirm("Are you sure you want to delete this service?"):
            await ServiceDAO.delete_obj(session, obj=service)
            typer.echo(f"Service {name} deleted")


async def _refresh_jwt(name: str):
    async with get_session_context() as session:
        service = await ServiceDAO.get_one_or_none(session, name=name)
        if not service:
            typer.echo(f"Service with name {name} not found")
            return

        if typer.confirm("Are you sure you want to refresh this jwt?"):
            jwt = secrets.token_hex(32)
            await ServiceDAO.update_obj(session, {"jwt_secret": jwt}, obj=service)
            typer.echo(f"Save this new jwt_secret - it is shown only once: {jwt}")


@cli.command(short_help="Add a new service")
def add_service(name: str):
    asyncio.run(_add_service(name))


@cli.command(short_help="Refresh service jwt")
def refresh_jwt(name: str):
    asyncio.run(_refresh_jwt(name))


@cli.command()
def delete_service(name: str):
    asyncio.run(_delete_service(name))


if __name__ == "__main__":
    cli()