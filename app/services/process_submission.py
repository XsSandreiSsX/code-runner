import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.database import SubmissionDAO
from app.models import Submission
from app.schemas.test_suite import TestCaseSchema
from shared.celery_app import app
from shared.schemas.runner import RunnerInputSchema


logger = logging.getLogger(__name__)


class ProcessSubmissionUseCase:
    @classmethod
    async def execute(cls, session: AsyncSession, submission: Submission):
        """Send a submission to the judge worker through Celery.

        Builds a runner payload from the submission source code, test cases,
        and resource limits, sends it to the Celery queue, and stores the
        created Celery task id in the submission.

        Args:
            session: Active database session from the router.
            submission: Submission that should be sent for judging.
        """
        logger.info("Sending submission to Celery: submission_id=%s", submission.id)

        payload = RunnerInputSchema(
            source_code=submission.source_code,
            test_cases=[
                TestCaseSchema(
                    stdin=test.stdin,
                    stdout=test.stdout,
                )
                for test in submission.testsuite.test_cases
            ],
            time_limit=submission.testsuite.time_limit,
            memory_limit=submission.testsuite.memory_limit,
        ).model_dump(mode="json")

        logger.debug(
            "Prepared runner payload: submission_id=%s tests_count=%s time_limit=%s memory_limit=%s",
            submission.id,
            len(submission.testsuite.test_cases),
            submission.testsuite.time_limit,
            submission.testsuite.memory_limit,
        )

        task = app.send_task("submissions.run", args=[payload])

        logger.info(
            "Celery task created: submission_id=%s task_id=%s",
            submission.id,
            task.id,
        )

        await SubmissionDAO.update_obj(
            session,
            {"celery_task_id": task.id},
            obj=submission,
        )