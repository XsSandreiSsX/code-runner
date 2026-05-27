from app.core.http_exceptions import NotFoundError
from app.models.submission import Submission
from app.models.service import Service
from app.services.database import SubmissionDAO, TestSuiteDAO
from app.schemas.submission import SubmissionCreateSchema

from sqlalchemy.ext.asyncio import AsyncSession

class SubmissionService:
    @classmethod
    async def create_submission(cls, session: AsyncSession, data: SubmissionCreateSchema, issuer: Service) -> Submission:
        cur_testsuite = await TestSuiteDAO.get_or_none(session, id=data.testsuite_id, service_id=issuer.id)
        if not cur_testsuite:
            raise NotFoundError(f"Test suite with id: {data.testsuite_id} was not found.")

        payload = data.model_dump(exclude={"testsuite_id"})
        payload.update({"testsuite": cur_testsuite,
                        "service": issuer})

        new_obj = await SubmissionDAO.add(session, payload)
        return new_obj

    @classmethod
    async def get_submission(cls, session: AsyncSession, submission_id: int, issuer: Service) -> Submission:
        submission = await SubmissionDAO.get_or_none(session, id=submission_id, service_id=issuer.id)
        if not submission:
            raise NotFoundError(f"Submission with id: {submission_id} was not found.")
        return submission