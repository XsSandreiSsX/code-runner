from app.models import Submission
from app.database import SubmissionDAO
from app.schemas.test_suite import TestCaseSchema
from shared.schemas.runner import RunnerInputSchema

from shared.celery_app import app
from sqlalchemy.ext.asyncio import AsyncSession



class ProcessSubmissionUseCase:
    @classmethod
    async def execute(cls, session: AsyncSession, submission: Submission):
        payload = RunnerInputSchema(
            source_code=submission.source_code,
            test_cases=[TestCaseSchema(
                stdin=test.stdin,
                stdout=test.stdout,
            ) for test in submission.testsuite.test_cases
                ],
            time_limit=submission.testsuite.time_limit,
            memory_limit=submission.testsuite.memory_limit,
        ).model_dump(mode="json")
        task = app.send_task("submissions.run", args=[payload])
        await SubmissionDAO.update_obj(session, {"celery_task_id": task.id}, obj=submission)


