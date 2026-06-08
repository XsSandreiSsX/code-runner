import asyncio
import time
import uuid
from dataclasses import dataclass
from typing import Any

from celery.states import FAILURE, SUCCESS

from app.cli_commands.problem import (
    insert_seed_problem_into_service,
    load_seed_problems,
)
from app.cli_commands.service import add_service, delete_service
from app.cli_ui import run_checks_ui
from app.core.database import async_session_maker
from app.models import Service
from app.schemas.submission import SubmissionCreateSchema
from app.services.process_submission import ProcessSubmissionUseCase
from app.services.submission import SubmissionService
from shared.celery_app import app
from shared.models.enums import SubmissionStatus
from shared.schemas.runner import RunnerOutputSchema, SubmissionVerdict


@dataclass
class CheckResult:
    name: str
    expected: str
    actual: str | None
    passed: bool


async def wait_celery_result(
    task_id: str,
    timeout: float | None = None,
    interval: float = 0.25,
) -> Any:
    """Wait for a Celery task result without blocking the event loop.

    Args:
        task_id: Celery task id.
        timeout: Maximum wait time in seconds. If None, waits forever.
        interval: Delay between backend status checks.

    Returns:
        Celery task result.

    Raises:
        RuntimeError: If the Celery task failed.
        TimeoutError: If the task did not finish before timeout.
    """
    started_at = time.monotonic()

    while True:
        meta = await asyncio.to_thread(app.backend.get_task_meta, task_id)

        status = meta.get("status")

        if status == SUCCESS:
            return meta.get("result")

        if status == FAILURE:
            raise RuntimeError(meta.get("result"))

        if timeout is not None and time.monotonic() - started_at >= timeout:
            raise TimeoutError(f"Celery task {task_id} timed out.")

        await asyncio.sleep(interval)


class JudgeTest:
    """Checks the judge pipeline using a temporary seed problem setup.

    This class verifies that the queue, message broker, Redis backend, and
    solution judging logic work correctly together.

    It creates a temporary service, inserts a seed test suite into it, submits
    all predefined solutions for the seed problem, compares their actual
    verdicts with the expected verdicts, and removes all temporary data after
    the check is finished.
    """

    def __init__(self, seed_problem_slug: str):
        """Initialize judge test for a seed problem.

        Args:
            seed_problem_slug: Slug of the seed problem to check.
        """
        self.seed_problem_slug = seed_problem_slug

        self.service_id: int | None = None
        self.service_name: str | None = None
        self.testsuite_id: int | None = None

    async def setup(self):
        """Create a temporary service and test suite, then store their IDs."""
        service_name = uuid.uuid4().hex[:8]

        service = await add_service(service_name)

        testsuite = await insert_seed_problem_into_service(
            self.seed_problem_slug,
            service_name,
        )

        self.service_id = service.id
        self.service_name = service.name
        self.testsuite_id = testsuite.id

    async def run(self) -> list[CheckResult]:
        """Run checks for all predefined solutions of the seed problem."""
        if self.service_id is None:
            raise RuntimeError("Service is not initialized. Call setup() first.")

        if self.testsuite_id is None:
            raise RuntimeError("TestSuite is not initialized. Call setup() first.")

        solutions_module = load_seed_problems(
            problem_name=self.seed_problem_slug,
            fields=["solutions"],
        )[0]["solutions"]

        checks = []

        for expected_verdict in SubmissionVerdict:
            solution = getattr(solutions_module, expected_verdict.value, None)

            if solution is None:
                continue

            check_name = f"solution expected {expected_verdict.value}"

            checks.append(
                (
                    check_name,
                    self.check_solution(
                        expected_verdict=expected_verdict,
                        solution=solution,
                    ),
                )
            )

        if not checks:
            raise RuntimeError(
                f"No solutions found for seed problem: {self.seed_problem_slug}"
            )

        return await run_checks_ui(checks)

    async def check_solution(
        self,
        expected_verdict: SubmissionVerdict,
        solution: str,
    ) -> CheckResult:
        """Submit one predefined solution and validate its actual verdict.

        Args:
            expected_verdict: Verdict that the solution is expected to receive.
            solution: Source code of the predefined solution.

        Returns:
            Check result containing the expected verdict, actual verdict, and
            whether they match.
        """
        if self.service_id is None:
            raise RuntimeError("Service is not initialized.")

        if self.testsuite_id is None:
            raise RuntimeError("TestSuite is not initialized.")

        name = f"solution expected {expected_verdict.value}"

        async with async_session_maker() as session:
            service = await session.get(Service, self.service_id)

            if service is None:
                raise RuntimeError(f"Service {self.service_id} not found.")

            data = SubmissionCreateSchema(
                testsuite_id=self.testsuite_id,
                source_code=solution,
            )

            submission = await SubmissionService.create_submission(
                session,
                data,
                service,
            )

            await ProcessSubmissionUseCase.execute(session, submission)

            await session.commit()

            raw_result = await wait_celery_result(submission.celery_task_id)
            result = RunnerOutputSchema(**raw_result)

            submission.status = SubmissionStatus.FINISHED
            submission.verdict = result.verdict
            submission.failed_test_index = result.failed_test_index
            submission.error_message = result.error_message
            submission.time_used = result.time_used
            submission.memory_used = result.memory_used
            submission.tests_passed = result.tests_passed

            await session.commit()

            actual_verdict = result.verdict

            return CheckResult(
                name=name,
                expected=expected_verdict.value,
                actual=actual_verdict.value if actual_verdict else None,
                passed=actual_verdict == expected_verdict,
            )

    async def teardown(self):
        """Delete the temporary service and related database records."""
        if self.service_name:
            await delete_service(self.service_name)
