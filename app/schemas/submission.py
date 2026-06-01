from shared.models.enums import SubmissionStatus, SubmissionVerdict
from pydantic import BaseModel, Field, ConfigDict


class SubmissionCreateSchema(BaseModel):
    testsuite_id: int = Field(default=1)
    source_code: str = Field(min_length=1, max_length=10000)


class SubmissionCreatedDataSchema(BaseModel):
    submission_id: int = Field(default=1)
    submission_status: str = Field(default="IN_QUEUE")


class SubmissionGetDataSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(default=1)
    testsuite_id: int = Field(default=1)

    status: SubmissionStatus = Field(default=SubmissionStatus.IN_QUEUE)
    verdict: SubmissionVerdict | None = Field(default=None)

    failed_test_index: int | None = Field(default=None)
    error_message: str | None = Field(default=None)
    time_used: int | None = Field(default=None)
    memory_used: int | None = Field(default=None)
    tests_passed: int | None = Field(default=None)


