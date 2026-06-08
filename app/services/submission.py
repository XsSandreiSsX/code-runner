from sqlalchemy.ext.asyncio import AsyncSession

from app.core.http_exceptions import NotFoundError
from app.database import SubmissionDAO, TestSuiteDAO
from app.models import Service, Submission
from app.schemas.submission import SubmissionCreateSchema


class SubmissionService:
    """Provides submission-related business operations."""

    @classmethod
    async def create_submission(
        cls, session: AsyncSession, data: SubmissionCreateSchema, issuer: Service
    ) -> Submission:
        """Create a submission for the authenticated service."""
        cur_testsuite = await TestSuiteDAO.get_one_or_none(
            session, id=data.testsuite_id, service_id=issuer.id
        )
        if not cur_testsuite:
            raise NotFoundError(
                f"Test suite with id: {data.testsuite_id} was not found."
            )

        payload = data.model_dump(exclude={"testsuite_id"})
        payload.update({"testsuite": cur_testsuite, "service": issuer})

        new_obj = await SubmissionDAO.add(session, payload)
        return new_obj

    @classmethod
    async def get_submission(
        cls, session: AsyncSession, submission_id: int, issuer: Service
    ) -> Submission:
        """Get a submission owned by the authenticated service."""
        submission = await SubmissionDAO.get_one_or_none(
            session, id=submission_id, service_id=issuer.id
        )
        if not submission:
            raise NotFoundError(f"Submission with id: {submission_id} was not found.")
        return submission