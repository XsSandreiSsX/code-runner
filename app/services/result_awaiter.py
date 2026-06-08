import asyncio
import logging

from shared.celery_app import app

from app.core.database import async_session_maker
from app.database import SubmissionDAO
from shared.models.enums import CeleryStatus, SubmissionStatus, SubmissionVerdict
from shared.schemas.runner import RunnerOutputSchema


logger = logging.getLogger(__name__)


class ResultAwaiter:
    """Background listener that synchronizes Celery results with submissions.

    Runs inside the FastAPI lifespan task and periodically checks unfinished
    submissions whose Celery tasks are still in progress. The listener reads
    task statuses and results from the Celery result backend, usually Redis,
    without blocking the FastAPI event loop.

    When a task is started, failed, or completed, the corresponding submission
    record is updated in the database with the actual status, verdict, error
    message, resource usage, and passed test count.
    """

    @classmethod
    async def _check_celery_status(cls, task_id: str):
        """Check Celery task status and result without blocking the event loop.

        Moves the synchronous Celery result backend call to a separate thread,
        because reading task metadata from Redis through Celery is blocking.

        Args:
            task_id: Celery task id to check.

        Returns:
            Tuple containing the Celery task status and task result.
        """

        def _sync_check():
            task = app.AsyncResult(id=task_id)
            return task.status, task.result

        return await asyncio.to_thread(_sync_check)

    @classmethod
    async def listen(cls):
        """Continuously listen for Celery results and update submissions.

        Runs as a background FastAPI lifespan task. Periodically loads
        submissions with IN_QUEUE or RUNNING status, checks their Celery task
        status from the Redis result backend, and writes the final judging
        result back to the database.

        The listener keeps running until it is cancelled by the application
        shutdown.
        """
        logger.info("ResultAwaiter started")

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
                        logger.debug(
                            "Found submissions to update: count=%s",
                            len(obj_lst),
                        )

                        for submission in obj_lst:
                            task_id = submission.celery_task_id

                            if not task_id:
                                logger.warning(
                                    "Submission has no celery_task_id: submission_id=%s",
                                    submission.id,
                                )
                                continue

                            try:
                                task_status, task_result = await cls._check_celery_status(
                                    task_id
                                )

                                logger.debug(
                                    "Checked Celery task: submission_id=%s task_id=%s status=%s",
                                    submission.id,
                                    task_id,
                                    task_status,
                                )

                                if task_status == CeleryStatus.STARTED.value:
                                    if submission.status != SubmissionStatus.RUNNING:
                                        submission.status = SubmissionStatus.RUNNING

                                        logger.info(
                                            "Submission changed status to RUNNING: submission_id=%s task_id=%s",
                                            submission.id,
                                            task_id,
                                        )

                                elif task_status == CeleryStatus.FAILURE.value:
                                    submission.status = SubmissionStatus.FINISHED
                                    submission.verdict = SubmissionVerdict.INTERNAL_ERROR
                                    submission.error_message = str(task_result)

                                    logger.error(
                                        "Submission failed in Celery: submission_id=%s task_id=%s error=%s",
                                        submission.id,
                                        task_id,
                                        task_result,
                                    )

                                elif task_status == CeleryStatus.SUCCESS.value:
                                    runner_output = RunnerOutputSchema.model_validate(
                                        task_result
                                    )

                                    submission.status = SubmissionStatus.FINISHED
                                    submission.verdict = runner_output.verdict
                                    submission.failed_test_index = (
                                        runner_output.failed_test_index
                                    )
                                    submission.error_message = runner_output.error_message
                                    submission.time_used = runner_output.time_used
                                    submission.memory_used = runner_output.memory_used
                                    submission.tests_passed = runner_output.tests_passed

                                    logger.info(
                                        "Submission successfully judged: submission_id=%s task_id=%s verdict=%s tests_passed=%s",
                                        submission.id,
                                        task_id,
                                        runner_output.verdict,
                                        runner_output.tests_passed,
                                    )

                            except Exception:
                                logger.exception(
                                    "Error processing submission: submission_id=%s task_id=%s",
                                    submission.id,
                                    task_id,
                                )

                        await session.commit()

            except asyncio.CancelledError:
                logger.info("ResultAwaiter stopped via CancelledError")
                raise

            except Exception:
                logger.exception("ResultAwaiter global error")

            await asyncio.sleep(1)