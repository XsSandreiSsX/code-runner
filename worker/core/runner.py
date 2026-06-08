import logging
import secrets
import shutil
import subprocess
from pathlib import Path
from time import perf_counter

from worker.debugtools import measure_execution_time

WORKER_DIR = Path(__file__).resolve().parent.parent

logger = logging.getLogger(__name__)


class Runner:
    """Runs user-submitted Python code inside an isolated nsjail sandbox.

    Creates a temporary workspace for every submission run, writes the source
    code into it, executes the code with time and memory limits, measures
    execution time, and removes temporary files after execution.
    """

    def __init__(
        self,
        *,
        source_code: str,
        time_limit: int,
        memory_limit: int,
    ):
        """Initialize runner configuration and temporary workspace paths.

        Args:
            source_code: User-submitted source code.
            time_limit: Execution time limit inside the sandbox.
            memory_limit: Memory limit inside the sandbox.
        """
        self.CFG_PATH = WORKER_DIR / "config" / "py-runner.cfg"
        self.RUNS_DIR = WORKER_DIR.parent / "sandbox" / "runs"

        self.submission_tmp_id = secrets.token_hex(16)
        self.run_dir = self.RUNS_DIR / self.submission_tmp_id
        self.code_file_path = self.run_dir / "solution.py"

        self.source_code = source_code
        self.time_limit = time_limit
        self.memory_limit = memory_limit

        # Used only for debugging and metrology reporting.
        # May be extended in the future for additional execution reports.
        self.measure = []

    def init_workspace(self):
        """Create a temporary workspace and write the solution file.

        Must be called before execute_code().
        """
        self.run_dir.mkdir(parents=True, exist_ok=True)

        self.code_file_path.write_text(self.source_code, encoding="utf-8")

        logger.debug(
            "Temporary workspace created: run_dir=%s code_file=%s",
            self.run_dir,
            self.code_file_path,
        )

    @measure_execution_time
    def execute_code(
        self,
        *,
        stdin: str,
        time_limit_padding: int = 1,
        calibrated_time_ms: float = 23.0,
    ) -> tuple[int, str, str, float]:
        """Execute user-submitted code inside the sandbox.

        Args:
            stdin: Input data passed to the solution.
            time_limit_padding: Additional time added to the sandbox hard limit.
            calibrated_time_ms: Container startup overhead used for execution
                time calibration.

        Returns:
            Tuple containing process return code, stdout, stderr, and execution
            time in milliseconds.
        """
        memory_limit_mb = self.memory_limit
        memory_limit_bytes = memory_limit_mb * 1024 * 1024

        command = [
            "nsjail",
            "--config",
            str(self.CFG_PATH),
            "--bindmount_ro",
            f"{self.run_dir}:/workspace",
            "--time_limit",
            str(self.time_limit + time_limit_padding),
            "--cgroup_mem_max",
            str(memory_limit_bytes),
            "--rlimit_as",
            str(self.memory_limit),
            "--",
            "/usr/local/bin/python3",
            "solution.py",
        ]

        logger.debug(
            "Sandbox execution started: run_dir=%s time_limit=%s memory_limit=%s",
            self.run_dir,
            self.time_limit,
            self.memory_limit,
        )

        start_time = perf_counter()

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            input=stdin,
        )

        end_time = perf_counter()

        raw_time_ms = (end_time - start_time) * 1000
        time_used_ms = max(0.0, raw_time_ms - calibrated_time_ms)

        logger.debug(
            "Sandbox execution finished: run_dir=%s return_code=%s raw_time_ms=%.2f time_used_ms=%.2f",
            self.run_dir,
            result.returncode,
            raw_time_ms,
            time_used_ms,
        )

        return (
            result.returncode,
            result.stdout,
            result.stderr,
            time_used_ms,
        )

    def cleanup(self):
        """Remove the temporary workspace and all associated files."""
        shutil.rmtree(self.run_dir, ignore_errors=True)

        logger.debug("Temporary workspace removed: run_dir=%s", self.run_dir)