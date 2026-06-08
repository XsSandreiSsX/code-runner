import importlib.util
import json
from pathlib import Path
from types import ModuleType
from typing import Sequence

from app.core.app_exceptions import (
    SeedProblemDoesExistsError,
    ServiceDoesNotExistsError,
)
from app.core.config import BASE_DIR
from app.core.database import async_session_maker
from app.database import ServiceDAO
from app.models import TestSuite
from app.schemas.test_suite import TestSuiteCreateSchema
from app.services.test_suite import TestSuiteService

SEED_PROBLEMS_PATH = BASE_DIR / "seed_problems"


def load_py_file(path: Path) -> ModuleType:
    """
    Dynamically loads a Python file as a module.

    A unique module name is generated from the file name and its parent directory
    to avoid name conflicts when loading files with the same name from different
    problem folders.

    Args:
        path: Path to the Python file that should be loaded.

    Returns:
        The loaded Python module object.
    """
    module_name = path.stem + "_" + path.parent.name
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


def load_seed_problems(
    *,
    problem_name: str | None = None,
    fields: Sequence[str] | None = None,
):
    """
    Loads seed problems from the seed problems directory.

    If `problem_name` is provided, only the problem folder with the exact same
    name will be loaded. Otherwise, all available seed problems will be loaded.

    The `fields` argument can be used to load only specific parts of each problem.
    Available fields are: `meta`, `tests`, and `solutions`.

    Each seed problem can contain:
    - `meta.py` with problem metadata
    - `tests.json` with test cases
    - `solutions.py` with predefined sample solutions

    Args:
        problem_name: Optional exact name of the problem folder to load.
            If omitted, all seed problems will be loaded.
        fields: Optional list of fields to load. If omitted, all fields are loaded.
            Allowed values: `meta`, `tests`, `solutions`.

    Returns:
        A list of dictionaries containing the requested problem data.

    Raises:
        FileNotFoundError: If a required file for the requested field is missing.
        ValueError: If an unknown field is requested.
    """
    allowed_fields = {"slug", "meta", "tests", "solutions"}

    if fields is None:
        fields = list(allowed_fields)
    else:
        unknown_fields = set(fields) - allowed_fields

        if unknown_fields:
            raise ValueError(f"Unknown fields: {unknown_fields}")

    problems = []

    for problem_dir in SEED_PROBLEMS_PATH.iterdir():
        if not problem_dir.is_dir():
            continue

        if problem_name and problem_name != problem_dir.name:
            continue

        problem_data = {}

        meta_path = problem_dir / "meta.py"
        tests_path = problem_dir / "tests.json"
        solutions_path = problem_dir / "solutions.py"

        if "slug" in fields:
            problem_data["slug"] = problem_dir.name

        if "meta" in fields:
            if not meta_path.exists():
                raise FileNotFoundError(f"Missing meta.py in {problem_dir}")

            problem_data["meta"] = load_py_file(meta_path)

        if "tests" in fields:
            if not tests_path.exists():
                raise FileNotFoundError(f"Missing tests.json in {problem_dir}")

            with open(tests_path, "r", encoding="utf-8") as f:
                problem_data["tests"] = json.load(f)

        if "solutions" in fields:
            if not solutions_path.exists():
                raise FileNotFoundError(f"Missing solutions.py in {problem_dir}")

            problem_data["solutions"] = load_py_file(solutions_path)

        problems.append(problem_data)

    return problems


async def insert_seed_problem_into_service(name: str, to_service: str) -> TestSuite:
    """Insert a selected seed test suite into the specified service.

    Args:
        name: Slug of the seed problem to insert.
        to_service: Name of the service where the test suite should be created.

    Returns:
        Created test suite.

    Raises:
        SeedProblemDoesExistsError: If the seed problem does not exist.
        ServiceDoesNotExistsError: If the target service does not exist.
    """

    problems = [i["slug"] for i in load_seed_problems(fields=["slug"])]
    if name not in problems:
        raise SeedProblemDoesExistsError

    async with async_session_maker() as session:
        service = await ServiceDAO.get_one_or_none(session, name=to_service)
        if not service:
            raise ServiceDoesNotExistsError

        seed_problem = load_seed_problems(problem_name=name)[0]

        testsuite_data = TestSuiteCreateSchema(
            time_limit=seed_problem["meta"].TIME_LIMIT,
            memory_limit=seed_problem["meta"].MEMORY_LIMIT,
            test_cases=seed_problem["tests"],
        )
        testsuite = await TestSuiteService.create_testsuite(
            session, testsuite_data, issuer=service
        )

        await session.commit()

    return testsuite
