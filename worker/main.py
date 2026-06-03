from worker.core.process_tests import ProcessTestsUseCase
from shared.celery_app import app
from shared.schemas.runner import RunnerInputSchema


@app.task(name="submissions.run")
def run_submission(payload: dict):
    submission = RunnerInputSchema.model_validate(payload)

    result = ProcessTestsUseCase.execute(submission)
    return result.model_dump(mode="json")

