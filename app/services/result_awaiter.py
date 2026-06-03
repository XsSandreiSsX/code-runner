from app.core.database import async_session_maker
from app.database import SubmissionDAO

from shared.models.enums import SubmissionStatus, CeleryStatus, SubmissionVerdict
from shared.schemas.runner import RunnerOutputSchema
from celery.result import AsyncResult
import asyncio

class ResultAwaiter:
    @classmethod
    async def listen(cls):
        while True:
            try:
                async with async_session_maker() as session:
                    obj_lst = await SubmissionDAO.get_many_or_none(
                        session,
                        status=[
                            SubmissionStatus.IN_QUEUE,
                            SubmissionStatus.RUNNING,
                        ],
                    )

                    if obj_lst:
                        for submission in obj_lst:
                            task_id = submission.celery_task_id
                            print("CELERY_TASK_ID: ", task_id)
                            if not task_id:
                                continue
                            task = AsyncResult(id=task_id)

                            if task.status == CeleryStatus.STARTED.value:
                                submission.status = SubmissionStatus.RUNNING

                            elif task.status == CeleryStatus.FAILURE.value:
                                submission.status = SubmissionStatus.FINISHED
                                submission.verdict = SubmissionVerdict.INTERNAL_ERROR
                                submission.error_message = str(task.result)

                            elif task.status == CeleryStatus.SUCCESS.value:
                                runner_output = RunnerOutputSchema.model_validate(task.result)

                                submission.status = SubmissionStatus.FINISHED
                                submission.verdict = runner_output.verdict
                                submission.failed_test_index = runner_output.failed_test_index
                                submission.error_message = runner_output.error_message
                                submission.time_used = runner_output.time_used
                                submission.memory_used = runner_output.memory_used
                                submission.tests_passed = runner_output.tests_passed

                        await session.commit()

            except asyncio.CancelledError:
                print("ResultAwaiter stopped")
                raise

            except Exception as e:
                print(f"ResultAwaiter error: {e}")

            await asyncio.sleep(1)




