import asyncio

import typer

from app.cli_commands.judge_test import JudgeTest
from app.cli_commands.problem import (
    insert_seed_problem_into_service,
    load_seed_problems,
)
from app.cli_commands.service import add_service, delete_service, refresh_jwt
from app.core.app_exceptions import (
    SeedProblemDoesExistsError,
    ServiceAlreadyExistsError,
    ServiceDoesNotExistsError,
)
from utils.jwt_generator import generate_internal_jwt

cli = typer.Typer(help="Service access and JWT secret management commands.")


@cli.command(
    name="add-service",
    short_help="Add a new service and generate a secret key.",
    help="Create a new service, generate its JWT secret, and optionally generate a short-lived test JWT token.",
)
def cli_add_service(name: str = typer.Argument(..., help="Unique name of the service")):
    try:
        service = asyncio.run(add_service(name))
    except ServiceAlreadyExistsError:
        typer.secho(
            f"\n[ERROR] Service '{name}' already exists.",
            fg=typer.colors.RED,
            bold=True,
        )
        return

    typer.secho(
        f"\n[SUCCESS] Service '{name}' added successfully.",
        fg=typer.colors.GREEN,
        bold=True,
    )
    typer.echo("Save this jwt_secret. It is shown only once:")
    typer.secho(f"-> {service.jwt_secret}\n", fg=typer.colors.BRIGHT_MAGENTA, bold=True)

    prompt = typer.style(
        "Generate a 15-minute test JWT token?", fg=typer.colors.GREEN, bold=True
    )

    if typer.confirm(prompt, default=False):
        token = generate_internal_jwt(
            iss=service.name, jwt_secret=service.jwt_secret, ttl=900
        )
        typer.secho("\n[INFO] Test JWT token:", fg=typer.colors.CYAN)
        typer.secho(f"{token}\n", fg=typer.colors.YELLOW)


@cli.command(
    name="refresh-jwt",
    short_help="Regenerate the JWT secret key for an existing service.",
    help="Generate a new JWT secret for an existing service. The previous secret becomes invalid immediately.",
)
def cli_refresh_jwt(name: str = typer.Argument(..., help="Name of the service")):
    prompt = typer.style(
        f"Are you sure you want to refresh the JWT secret for '{name}'?",
        fg=typer.colors.YELLOW,
    )
    if not typer.confirm(prompt, default=False):
        typer.secho("\n[CANCELLED] JWT refresh cancelled.", fg=typer.colors.YELLOW)
        return

    try:
        service = asyncio.run(refresh_jwt(name))
    except ServiceDoesNotExistsError:
        typer.secho(f"\n[ERROR] Service '{name}' not found.", fg=typer.colors.RED)
        return

    typer.secho(f"\n[SUCCESS] JWT secret updated for '{name}'.", fg=typer.colors.GREEN)
    typer.echo("Save the new secret. The old one is invalidated immediately:")
    typer.secho(f"-> {service.jwt_secret}\n", fg=typer.colors.BRIGHT_MAGENTA, bold=True)


@cli.command(
    name="delete-service",
    short_help="Permanently delete a service and revoke access.",
    help="Delete a service from the database. Related records may also be removed depending on database relationships.",
)
def cli_delete_service(name: str = typer.Argument(..., help="Name of the service")):
    prompt = typer.style(
        f"Are you sure you want to DELETE service '{name}'?",
        fg=typer.colors.RED,
        bold=True,
    )

    if not typer.confirm(prompt, default=False):
        typer.secho("\n[CANCELLED] Deletion cancelled.", fg=typer.colors.YELLOW)
        return

    try:
        service = asyncio.run(delete_service(name))
    except ServiceDoesNotExistsError:
        typer.secho(
            f"\n[ERROR] Service '{name}' not found.",
            fg=typer.colors.RED,
        )
        return

    typer.secho(
        f"\n[SUCCESS] Service '{service.name}' has been permanently deleted.",
        fg=typer.colors.GREEN,
    )


@cli.command(
    name="list-problems",
    short_help="List all seed problems.",
    help="Show all available seed problems loaded from the seed problems directory.",
)
def cli_list_problems():
    problems = [i["slug"] for i in load_seed_problems(fields=["slug"])]

    if not problems:
        typer.secho("[WARNING] No seed problems found.", fg=typer.colors.YELLOW)
    else:
        typer.secho(
            f"\nFOUND {len(problems)} SEED PROBLEMS:",
            fg=typer.colors.BRIGHT_CYAN,
            bold=True,
        )

        for slug in problems:
            typer.echo(f"  -> {typer.style(slug)}")
        typer.echo("")


@cli.command(
    name="check-problem",
    short_help="Show seed problem metadata.",
    help="Display statement, input format, output format, time limit, and memory limit for a seed problem.",
)
def cli_check_problem(name: str = typer.Argument(..., help="Name of the problem")):
    problems = [i["slug"] for i in load_seed_problems(fields=["slug"])]
    if name not in problems:
        typer.secho(f"[ERROR] Problem '{name}' not found.", fg=typer.colors.RED)
        return

    meta = load_seed_problems(problem_name=name, fields=["meta"])[0]["meta"]

    typer.echo("")
    typer.secho(
        f"PROBLEM: {meta.TITLE.upper()}", fg=typer.colors.BRIGHT_CYAN, bold=True
    )
    typer.echo(f"Time Limit:   {meta.TIME_LIMIT}s")
    typer.echo(f"Memory Limit: {meta.MEMORY_LIMIT}MB")
    typer.echo("")
    typer.secho("Statement:", fg=typer.colors.GREEN, bold=True)
    typer.echo(meta.STATEMENT.strip())
    typer.echo("")
    typer.secho("Input Format:", fg=typer.colors.BLUE, bold=True)
    typer.echo(meta.INPUT.strip())
    typer.echo("")
    typer.secho("Output Format:", fg=typer.colors.MAGENTA, bold=True)
    typer.echo(meta.OUTPUT.strip())
    typer.echo("")


@cli.command(
    name="insert-problem",
    short_help="Load and insert a seed problem into the database.",
    help="Create a test suite from a seed problem and attach it to the specified service.",
)
def cli_insert_problem(
    name: str = typer.Argument(..., help="Name of the problem"),
    to_service: str = typer.Option("admin", "--to-service", help="Name of the service"),
):
    try:
        testsuite = asyncio.run(
            insert_seed_problem_into_service(name=name, to_service=to_service)
        )
    except ServiceDoesNotExistsError:
        typer.secho(
            f"[ERROR] Service '{to_service}' not found. Create it before inserting a problem.",
            fg=typer.colors.RED,
        )
        return
    except SeedProblemDoesExistsError:
        typer.secho(f"[ERROR] Problem '{name}' not found.", fg=typer.colors.RED)
        return

    typer.secho(
        f"[SUCCESS] Test suite successfully added to service '{to_service}'.",
        fg=typer.colors.GREEN,
    )
    typer.secho(
        f"  -> Test suite id: {testsuite.id}",
        fg=typer.colors.MAGENTA,
        bold=True,
    )


@cli.command(
    name="judge-test",
    short_help="Run full integration test for a seed problem with verdict assertion.",
    help="Create temporary data, run all predefined solutions for a seed problem, compare actual verdicts with expected verdicts, and remove temporary data.",
)
def cli_judge_test(
    name: str = typer.Argument(..., help="Name of the problem for testing"),
):
    async def async_inner():
        tester = JudgeTest(name)
        try:
            await tester.setup()
            await tester.run()

        except SeedProblemDoesExistsError:
            typer.secho(f"[ERROR] Problem '{name}' not found.", fg=typer.colors.RED)
            return

        finally:
            await tester.teardown()

    asyncio.run(async_inner())


if __name__ == "__main__":
    cli()