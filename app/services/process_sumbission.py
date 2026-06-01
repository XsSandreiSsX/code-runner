from app.core.deps import get_session
from shared.models.enums import SubmissionStatus
from database import SubmissionDAO
from contextlib import asynccontextmanager


get_session_context = asynccontextmanager(get_session)


class ProcessSubmissionUseCase:
    @classmethod
    async def execute(cls, submission_id: int):
        print(f"process submission: {submission_id}")

        async with get_session_context() as session:
            submission = await SubmissionDAO.get_or_none(session, id=submission_id)
            await SubmissionDAO.update_obj(session, data={"status": SubmissionStatus.RUNNING}, obj=submission)

            await SubmissionDAO.update_obj(session, data={"status": SubmissionStatus.FINISHED}, obj=submission)
            print("running finished")
