from worker.core.runner import Runner
from shared.models.enums import SubmissionVerdict
from shared.schemas.runner import RunnerInputSchema, RunnerOutputSchema
from worker.debugtools import log_metrology_report

import logging

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
    ) -> RunnerOutputSchema:
        """
        Executes a user solution against all test cases and
        produces the final verification verdict.

        Args:
            submission: Required data for solution verification.
            time_limit_rate: Multiplier used to calculate the
                total execution time limit.
            tle_tolerance_ms: Allowed timing deviation used when
            checking the execution time limit.
            debug_mode: Enables logging of the runner metrology report.


        Returns:
            Solution verdict ready to be returned to the FastAPI backend.
        """

        runner = Runner(
            source_code=submission.source_code,
            time_limit=submission.time_limit,
            memory_limit=submission.memory_limit,
        )
        logger.debug(f"Executing {runner.source_code[:30]}")
        logger.debug(f"Time Limit: {runner.time_limit}")
        logger.debug(f"Memory Limit: {runner.memory_limit}")

        output = OutputCollector()

        # Prepare the workspace and required files
        # before executing the user's solution.
        logger.debug("Initialization of the workspace")
        runner.init_workspace()

        task_time_limit_ms = submission.time_limit * 1000

        # Limit the total execution time across all test cases.
        #
        # This mechanism prevents abuse where a solution stays
        # within the limit for each individual test case but
        # consumes an excessive amount of time overall.
        max_total_allowed_time = (
            task_time_limit_ms
            * len(submission.test_cases)
            * time_limit_rate
        )
        logger.debug(f"Maximum time for all tests: {max_total_allowed_time}")

        all_time_used_ms = 0

        try:
            tests_passed = 0

            for i, test in enumerate(submission.test_cases):
                logger.info(f"Running test: {i + 1}/{len(submission.test_cases)}")
                return_code, stdout, stderr, time_used_ms = (
                    runner.execute_code(stdin=test.stdin)
                )
                logger.debug(f"Expected output: {test.stdout.strip()}")
                logger.debug(f"Real output: {stdout.strip()}")
                logger.debug(f"Return code: {return_code}")
                logger.debug(f"Stderr: {stderr.strip()}")
                logger.debug(f"Time used (ms): {time_used_ms}")


                output.time_used = max(output.time_used, int(time_used_ms))
                all_time_used_ms += time_used_ms
                logger.debug(f"Total time wasted: {all_time_used_ms} on submission\n")

                if time_used_ms >= (task_time_limit_ms - tle_tolerance_ms):
                    output.verdict = SubmissionVerdict.TIME_LIMIT_EXCEEDED
                    output.failed_test_index = i + 1
                    break

                # A non-zero return code indicates that
                # execution finished with an error.
                if return_code != 0:

                    # If stderr is available, try to determine
                    # the failure reason from the diagnostic output.
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

                        elif "MemoryError" in stderr:
                            output.verdict = SubmissionVerdict.MEMORY_LIMIT_EXCEEDED
                            output.failed_test_index = i + 1

                        else:
                            output.verdict = SubmissionVerdict.RUNTIME_ERROR
                            output.failed_test_index = i + 1

                        output.error_message = stderr.strip()
                        break

                    # Missing stderr usually means the process
                    # was terminated by SIGKILL.
                    else:

                        # Determine whether a time limit violation
                        # occurred, allowing a small tolerance.
                        if time_used_ms >= (task_time_limit_ms - 15.0):
                            output.verdict = SubmissionVerdict.TIME_LIMIT_EXCEEDED
                        else:
                            output.verdict = SubmissionVerdict.MEMORY_LIMIT_EXCEEDED

                        output.failed_test_index = i + 1
                        break

                # Normalize whitespace before comparing
                # expected and actual output.
                is_passed = (
                    test.stdout.strip()
                    == stdout.strip()
                )

                if not is_passed:
                    output.verdict = SubmissionVerdict.WRONG_ANSWER
                    output.failed_test_index = i + 1
                    break

                tests_passed += 1

                # Monitor total execution time regardless
                # of individual test case results.
                if all_time_used_ms > max_total_allowed_time:
                    output.verdict = SubmissionVerdict.TIME_LIMIT_EXCEEDED
                    output.failed_test_index = i + 1
                    output.error_message = "Total time limit exceeded"
                    break

            output.tests_passed = tests_passed

            if len(submission.test_cases) == tests_passed:
                output.verdict = SubmissionVerdict.ACCEPTED

            if debug_mode:
                logger.debug("Debug mode enabled")
                log_metrology_report(runner)


        except Exception as e:
            output.verdict = SubmissionVerdict.INTERNAL_ERROR
            output.error_message = str(e)

        finally:
            # Release temporary files and workspace resources
            # regardless of the execution outcome.
            runner.cleanup()

            result = RunnerOutputSchema.model_validate(
                output,
                from_attributes=True
            )

            logger.info(result)

        return result