import logging

from shared.models.enums import SubmissionVerdict
from shared.schemas.runner import RunnerInputSchema, RunnerOutputSchema
from worker.core.runner import Runner
from worker.debugtools import log_metrology_report

logger = logging.getLogger(__name__)


class OutputCollector:
    """
    Temporary object used to collect test execution results.
    Used later for conversion into RunnerOutputSchema.
    """

    def __init__(self):
        self.verdict = None
        self.failed_test_index = None
        self.error_message = None
        self.time_used = 0
        self.memory_used = 1
        self.tests_passed = 0


class ProcessTestsUseCase:
    @classmethod
    def execute(
        cls,
        submission: RunnerInputSchema,
        time_limit_rate: float = 0.3,
        tle_tolerance_ms: float = 15.0,
        debug_mode: bool = False,
        task_id: str | None = None,
    ) -> RunnerOutputSchema:
        """Execute a submitted solution against all test cases.

        Runs the user solution in an isolated runner, checks its output,
        execution time, memory behavior, runtime errors, and produces the
        final judging verdict.

        Args:
            submission: Runner input with source code, test cases, and limits.
            time_limit_rate: Multiplier used to limit total execution time.
            tle_tolerance_ms: Allowed timing tolerance in milliseconds.
            debug_mode: Enables detailed runner metrology logging.
            submission_id: Optional submission id used only for logs.
            task_id: Optional Celery task id used only for logs.

        Returns:
            Final runner output with verdict and execution details.
        """
        runner = Runner(
            source_code=submission.source_code,
            time_limit=submission.time_limit,
            memory_limit=submission.memory_limit,
        )

        logger.info(
            "Judging started: task_id=%s tests_count=%s time_limit=%s memory_limit=%s",
            task_id,
            len(submission.test_cases),
            submission.time_limit,
            submission.memory_limit,
        )

        logger.debug(
            "Runner initialized: task_id=%s source_preview=%r",
            task_id,
            submission.source_code[:80],
        )

        output = OutputCollector()

        logger.debug(
            "Initializing workspace: task_id=%s",
            task_id,
        )
        runner.init_workspace()

        task_time_limit_ms = submission.time_limit * 1000
        max_total_allowed_time = (
            task_time_limit_ms * len(submission.test_cases) * time_limit_rate
        )

        logger.debug(
            "Calculated limits: task_id=%s task_time_limit_ms=%s max_total_allowed_time=%s",
            task_id,
            task_time_limit_ms,
            max_total_allowed_time,
        )

        all_time_used_ms = 0

        try:
            tests_passed = 0

            for i, test in enumerate(submission.test_cases):
                test_index = i + 1

                return_code, stdout, stderr, time_used_ms = runner.execute_code(
                    stdin=test.stdin
                )

                logger.debug(
                    "Test executed: task_id=%s test_index=%s return_code=%s time_used_ms=%s",
                    task_id,
                    test_index,
                    return_code,
                    time_used_ms,
                )

                logger.debug(
                    "Test output: task_id=%s test_index=%s expected=%r actual=%r stderr=%r",
                    task_id,
                    test_index,
                    test.stdout.strip(),
                    stdout.strip(),
                    stderr.strip(),
                )

                output.time_used = max(output.time_used, int(time_used_ms))
                all_time_used_ms += time_used_ms

                if time_used_ms >= (task_time_limit_ms - tle_tolerance_ms):
                    output.verdict = SubmissionVerdict.TIME_LIMIT_EXCEEDED
                    output.failed_test_index = test_index

                    logger.warning(
                        "Time limit exceeded: task_id=%s test_index=%s time_used_ms=%s limit_ms=%s",
                        task_id,
                        test_index,
                        time_used_ms,
                        task_time_limit_ms,
                    )
                    break

                if return_code != 0:
                    if stderr:
                        compilation_error = any(
                            error in stderr
                            for error in (
                                "SyntaxError",
                                "SyntaxWarning",
                                "ModuleNotFoundError",
                                "ImportError",
                                "IndentationError",
                            )
                        )

                        if compilation_error:
                            output.verdict = SubmissionVerdict.COMPILATION_ERROR

                            logger.warning(
                                "Compilation error: task_id=%s test_index=%s",
                                task_id,
                                test_index,
                            )

                        elif "MemoryError" in stderr:
                            output.verdict = SubmissionVerdict.MEMORY_LIMIT_EXCEEDED
                            output.failed_test_index = test_index

                            logger.warning(
                                "Memory limit exceeded: task_id=%s test_index=%s",
                                task_id,
                                test_index,
                            )

                        else:
                            output.verdict = SubmissionVerdict.RUNTIME_ERROR
                            output.failed_test_index = test_index

                            logger.warning(
                                "Runtime error: task_id=%s test_index=%s return_code=%s",
                                task_id,
                                test_index,
                                return_code,
                            )

                        output.error_message = stderr.strip()
                        break

                    else:
                        if time_used_ms >= (task_time_limit_ms - 15.0):
                            output.verdict = SubmissionVerdict.TIME_LIMIT_EXCEEDED
                        else:
                            output.verdict = SubmissionVerdict.MEMORY_LIMIT_EXCEEDED

                        output.failed_test_index = test_index

                        logger.warning(
                            "Process killed without stderr: task_id=%s test_index=%s verdict=%s time_used_ms=%s",
                            task_id,
                            test_index,
                            output.verdict,
                            time_used_ms,
                        )
                        break

                is_passed = test.stdout.strip() == stdout.strip()

                if not is_passed:
                    output.verdict = SubmissionVerdict.WRONG_ANSWER
                    output.failed_test_index = test_index

                    logger.warning(
                        "Wrong answer: task_id=%s test_index=%s",
                        task_id,
                        test_index,
                    )
                    break

                tests_passed += 1

                if all_time_used_ms > max_total_allowed_time:
                    output.verdict = SubmissionVerdict.TIME_LIMIT_EXCEEDED
                    output.failed_test_index = test_index
                    output.error_message = "Total time limit exceeded"

                    logger.warning(
                        "Total time limit exceeded: task_id=%s test_index=%s total_time_ms=%s max_total_allowed_time=%s",
                        task_id,
                        test_index,
                        all_time_used_ms,
                        max_total_allowed_time,
                    )
                    break

            output.tests_passed = tests_passed

            if len(submission.test_cases) == tests_passed:
                output.verdict = SubmissionVerdict.ACCEPTED

            if debug_mode:
                logger.debug(
                    "Debug mode enabled: task_id=%s",
                    task_id,
                )
                log_metrology_report(runner)

        except Exception:
            output.verdict = SubmissionVerdict.INTERNAL_ERROR
            output.error_message = "Internal worker error"

            logger.exception(
                "Internal error while judging: task_id=%s",
                task_id,
            )

        finally:
            runner.cleanup()

            result = RunnerOutputSchema.model_validate(output, from_attributes=True)

            logger.info(
                "Judging finished: task_id=%s verdict=%s failed_test_index=%s tests_passed=%s time_used=%s memory_used=%s",
                task_id,
                result.verdict,
                result.failed_test_index,
                result.tests_passed,
                result.time_used,
                result.memory_used,
            )

        return result