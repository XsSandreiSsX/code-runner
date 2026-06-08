from shared.celery_app import app
from shared.schemas.runner import RunnerInputSchema
from shared.logger import setup_logging
from worker.core.process_tests import ProcessTestsUseCase


setup_logging()


@app.task(name="submissions.run", bind=True)
def run_submission(self, payload: dict):
    submission = RunnerInputSchema.model_validate(payload)

    result = ProcessTestsUseCase.execute(submission,
                                         task_id=self.request.id)
    return result.model_dump(mode="json")
