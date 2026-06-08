import asyncio
import time
from typing import Any, Awaitable

from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.text import Text

console = Console()

DOTS = [".", "..", "..."]


async def run_checks_ui(checks: list[tuple[str, Awaitable[Any]]]) -> list[Any]:
    """Run async checks and display their progress in a live Rich table.

    Creates an asyncio task for each check, updates the terminal UI while
    checks are running, shows success or failure for every finished check,
    and returns all check results after completion.

    Args:
        checks: List of check names and awaitable objects to run.

    Returns:
        List of results returned by completed checks.

    Raises:
        Exception: Re-raises the first exception raised by any check.
    """
    items = []

    for name, coro in checks:
        items.append(
            {
                "name": name,
                "task": asyncio.create_task(coro),
                "start": time.perf_counter(),
                "end": None,
                "done": False,
                "result": None,
                "error": None,
            }
        )

    tick = 0

    with Live(
        _render_table(items, tick),
        console=console,
        refresh_per_second=10,
        transient=False,
    ) as live:
        while True:
            all_done = True

            for item in items:
                task = item["task"]

                if not item["done"] and task.done():
                    item["done"] = True
                    item["end"] = time.perf_counter()

                    try:
                        item["result"] = task.result()
                    except Exception as exc:
                        item["error"] = exc

                if not item["done"]:
                    all_done = False

            live.update(_render_table(items, tick), refresh=True)

            if all_done:
                break

            tick += 1
            await asyncio.sleep(0.25)

    errors = [item["error"] for item in items if item["error"] is not None]

    if errors:
        raise errors[0]

    return [item["result"] for item in items]


def _render_table(items: list[dict], tick: int) -> Table:
    """Render the current check state as a Rich table.

    Builds a table with check status icons, messages, animated dots for
    running checks, and elapsed time for each item.

    Args:
        items: Runtime state of all checks.
        tick: Current UI tick used to animate loading dots.

    Returns:
        Rich table with the current checks progress.
    """
    table = Table(show_header=False, box=None, padding=(0, 1))

    table.add_column("icon", width=2)
    table.add_column("message")
    table.add_column("dots", width=3)
    table.add_column("elapsed", justify="right")

    dots = DOTS[tick % len(DOTS)]

    for item in items:
        end = item["end"] or time.perf_counter()
        elapsed = end - item["start"]

        name = item["name"]
        result = item["result"]
        error = item["error"]

        if error is not None:
            table.add_row(
                "[red]✗[/]",
                f"[red]ERROR[/] {name}: {error}",
                "",
                f"{elapsed:.1f}s",
            )

        elif item["done"]:
            if result.passed:
                table.add_row(
                    "[green]✓[/]",
                    f"[green]SUCCESS[/] {result.name}",
                    "",
                    f"{elapsed:.1f}s",
                )
            else:
                table.add_row(
                    "[red]✗[/]",
                    (
                        f"[red]FAILED[/] {result.name} "
                        f"expected [bold]{result.expected}[/], "
                        f"got [bold]{result.actual}[/]"
                    ),
                    "",
                    f"{elapsed:.1f}s",
                )

        else:
            table.add_row(
                "[cyan]~[/]",
                f"Checking {name}",
                Text(dots, style="cyan"),
                f"{elapsed:.1f}s",
            )

    return table