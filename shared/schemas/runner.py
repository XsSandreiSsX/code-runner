from shared.models.enums import SubmissionVerdict

from pydantic import BaseModel, Field, PositiveInt, ConfigDict
from typing import List


class TestCaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    stdin: str = Field()
    stdout: str = Field()


class RunnerInputSchema(BaseModel):
    source_code: str = Field(min_length=1, max_length=10000)
    test_cases: List[TestCaseSchema] = Field(min_length=1, max_length=1000)

    time_limit: PositiveInt
    memory_limit: PositiveInt


class RunnerOutputSchema(BaseModel):
    verdict: SubmissionVerdict

    failed_test_index: int | None = Field(default=None)
    error_message: str | None = Field(default=None)
    time_used: int
    memory_used: int
    tests_passed: int
