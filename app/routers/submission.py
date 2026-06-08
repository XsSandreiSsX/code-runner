from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.core.deps import get_current_issuer, get_session
from app.models.service import Service
from app.schemas.client_response import ClientResponse, SwaggerError
from app.schemas.submission import (
    SubmissionCreatedDataSchema,
    SubmissionCreateSchema,
    SubmissionGetDataSchema,
)
from app.services.process_submission import ProcessSubmissionUseCase
from app.services.submission import SubmissionService

router = APIRouter()


@router.post(
    "",
    summary="Create a new submission",
    description="Submit a user code for testing by test suite",
    response_model=ClientResponse[SubmissionCreatedDataSchema],
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Created new submission"},
        404: {"description": "Test suite not found", "model": SwaggerError},
    },
)
async def create_submission(
    data: SubmissionCreateSchema,
    session: AsyncSession = Depends(get_session),
    issuer: Service = Depends(get_current_issuer),
):
    submission = await SubmissionService.create_submission(session, data, issuer)

    await ProcessSubmissionUseCase.execute(session, submission)

    return ClientResponse.success(
        data=SubmissionCreatedDataSchema(
            submission_id=submission.id, submission_status=submission.status.value
        ),
        detail="Submission created successfully",
    )


@router.get(
    "/{submission_id}",
    summary="Check submission",
    description="Check the status of an existing submission",
    response_model=ClientResponse[SubmissionGetDataSchema],
    responses={
        404: {"description": "Submission not found", "model": SwaggerError},
    },
)
async def check_submission(
    submission_id: int,
    session: AsyncSession = Depends(get_session),
    issuer: Service = Depends(get_current_issuer),
):
    submission = await SubmissionService.get_submission(session, submission_id, issuer)

    return ClientResponse.success(
        data=SubmissionGetDataSchema.model_validate(submission),
        detail="Submission found successfully",
    )
