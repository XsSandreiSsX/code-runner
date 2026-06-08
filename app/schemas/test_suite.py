from typing import List

from pydantic import BaseModel, ConfigDict, Field, PositiveInt, model_validator


class TestCaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    stdin: str = Field()
    stdout: str = Field()


class TestSuiteCreateSchema(BaseModel):
    time_limit: PositiveInt = Field(default=1)
    memory_limit: PositiveInt = Field(default=1024)

    test_cases: List[TestCaseSchema] = Field(min_length=1, max_length=100)


class TestSuiteUpdateSchema(BaseModel):
    time_limit: PositiveInt | None = None
    memory_limit: PositiveInt | None = None

    test_cases: list[TestCaseSchema] | None = Field(default=None, min_length=1)

    @model_validator(mode="after")
    def validate_not_empty(self):
        if all(
            value is None
            for value in [self.time_limit, self.memory_limit, self.test_cases]
        ):
            raise ValueError("At least one field must be provided")

        return self


class TestSuiteCreatedDataSchema(BaseModel):
    id: int = Field(default=67)


class TestSuiteGetSchema(TestSuiteCreatedDataSchema, TestSuiteUpdateSchema):
    model_config = ConfigDict(from_attributes=True)
