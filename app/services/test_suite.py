from app.core.http_exceptions import NotFoundError

from app.models import TestSuite, TestCase
from app.services.database import TestSuiteDAO
from app.schemas.test_suite import TestSuiteCreateSchema, TestSuiteUpdateSchema

from sqlalchemy.ext.asyncio import AsyncSession


class TestSuiteService:
    @classmethod
    async def create_testsuite(cls, session: AsyncSession, data: TestSuiteCreateSchema) -> TestSuite:
        tests = data.test_cases

        payload = data.model_dump(exclude={"test_cases"})
        payload.update({"test_cases": [TestCase(**test.model_dump()) for test in tests]})

        new_obj = await TestSuiteDAO.add(session, data=payload)
        return new_obj

    @classmethod
    async def get_testsuite(cls, session: AsyncSession, testsuite_id: int) -> TestSuite:
        obj = await TestSuiteDAO.get_or_none(session, id=testsuite_id)
        if not obj:
            raise NotFoundError(f"Test suite with id: {testsuite_id} was not found.")

        return obj

    @classmethod
    async def update_testsuite(cls, session: AsyncSession, data: TestSuiteUpdateSchema, testsuite_id: int) -> TestSuite:
        payload = data.model_dump(exclude={"test_cases"}, exclude_unset=True)
        if data.test_cases:
            tests = data.test_cases
            payload.update({"test_cases": [TestCase(**test.model_dump()) for test in tests]})

        obj = await TestSuiteDAO.get_or_none(session, id=testsuite_id)
        if not obj:
            raise NotFoundError(f"Test suite with id: {testsuite_id} was not found.")

        updated_obj = await TestSuiteDAO.update_obj(session, data=payload, obj=obj)
        return updated_obj

    @classmethod
    async def delete_testsuite(cls, session: AsyncSession, testsuite_id: int) -> None:
        obj = await TestSuiteDAO.get_or_none(session, id=testsuite_id)
        if not obj:
            raise NotFoundError(f"Test suite with id: {testsuite_id} was not found.")

        await TestSuiteDAO.delete_obj(session, obj=obj)

