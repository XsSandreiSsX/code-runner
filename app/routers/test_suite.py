from app.core.deps import get_session

from app.schemas.test_suite import TestSuiteCreateSchema, TestSuiteUpdateSchema, TestSuiteCreatedDataSchema, TestSuiteGetSchema
from app.schemas.client_response import ClientResponse, SwaggerError

from app.services.test_suite import TestSuiteService

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

router = APIRouter()

@router.post("",
             summary="Create a test suite",
             description="Create a new test suite",
             response_model=ClientResponse[TestSuiteCreatedDataSchema],
             status_code=status.HTTP_201_CREATED,
             responses={201: {"description": "Successfully created new test suite"}},)
async def create_testsuite(data: TestSuiteCreateSchema, session: AsyncSession = Depends(get_session)):
    testsuite = await TestSuiteService.create_testsuite(session, data)

    return ClientResponse[TestSuiteCreatedDataSchema].success(
        data=TestSuiteCreatedDataSchema(id=testsuite.id),
        detail="Successfully created new test suite",
    )


@router.get("/{testsuite_id}",
            summary="Get a test suite",
            description="Get a test suite",
            response_model=ClientResponse[TestSuiteGetSchema],
            responses={404: {"description": "Not found test suite",
                             "model": SwaggerError}})
async def get_testsuite(testsuite_id: int, session: AsyncSession = Depends(get_session)):
    testsuite = await TestSuiteService.get_testsuite(session, testsuite_id)

    return ClientResponse[TestSuiteGetSchema].success(
        data=TestSuiteGetSchema.model_validate(testsuite),
        detail="Successfully retrieved test suite",
    )


@router.delete("/{testsuite_id}",
               summary="Delete a test suite",
               description="Delete a test suite",
               response_model=ClientResponse[None],
               responses={200: {"description": "Successfully deleted test suite"},
                          404: {"description": "Not found test suite",
                                "model": SwaggerError}},)
async def delete_testsuite(testsuite_id: int, session: AsyncSession = Depends(get_session)):
    await TestSuiteService.delete_testsuite(session, testsuite_id)
    return ClientResponse[None].success(
        detail="Successfully deleted test suite",
    )


@router.patch("/{testsuite_id}",
              summary="Update a test suite",
              description="Update a test suite",
              response_model=ClientResponse[None],
              responses={200: {"description": "Successfully updated test suite"},
                         404: {"description": "Not found test suite",
                               "model": SwaggerError}},)
async def update_testsuite(testsuite_id: int, data: TestSuiteUpdateSchema, session: AsyncSession = Depends(get_session)):
    await TestSuiteService.update_testsuite(session, data, testsuite_id)

    return ClientResponse[None].success(
        detail="Successfully updated test suite",
    )
