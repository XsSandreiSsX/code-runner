from worker.debugtools import measure_execution_time
from time import perf_counter
from pathlib import Path
import logging
import subprocess
import shutil
import secrets

WORKER_DIR = Path(__file__).resolve().parent.parent

logger = logging.getLogger(__name__)


class Runner:
    def __init__(
            self,
            *,
            source_code: str,
            time_limit: int,
            memory_limit: int,
    ):
        """
        Responsible for creating an isolated execution environment using nsjail.

        Also generates a temporary workspace and executes user-submitted code.

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
        """
        Creates a temporary workspace and writes the user's
        source code into the solution file.

        Must be called before execute_code().
        """

        self.run_dir.mkdir(parents=True, exist_ok=True)

        self.code_file_path.write_text(
            self.source_code,
            encoding="utf-8"
        )

        logger.debug(
            f"A new temporary file has been created: {self.code_file_path}"
        )

    @measure_execution_time
    def execute_code(
            self,
            *,
            stdin: str,
            time_limit_padding: int = 1,
            calibrated_time_ms: float = 23.0,
    ) -> tuple[int, str, str, float]:
        """
        Executes user-submitted code inside the sandbox.

        Args:
            stdin: Input data passed to the solution.
            time_limit_padding: Additional time added to the
                sandbox hard limit.
            calibrated_time_ms: Container startup overhead
                used for execution time calibration.

        Returns:
            Tuple containing:
                - Process return code
                - Standard output
                - Standard error
                - Execution time in milliseconds
        """

        memory_limit_mb = self.memory_limit
        memory_limit_bytes = memory_limit_mb * 1024 * 1024

        command = [
            "nsjail",
            "--config", str(self.CFG_PATH),
            "--bindmount_ro", f"{self.run_dir}:/workspace",
            "--time_limit", str(self.time_limit + time_limit_padding),
            "--cgroup_mem_max", str(memory_limit_bytes),
            "--rlimit_as", str(self.memory_limit),
            "--",
            "/usr/local/bin/python3", "solution.py"
        ]

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

        return (
            result.returncode,
            result.stdout,
            result.stderr,
            time_used_ms,
        )

    def cleanup(self):
        """
        Removes the temporary workspace and all associated files.

        Should be called after execute_code().
        """

        shutil.rmtree(self.run_dir, ignore_errors=True)

        logger.debug(
            f"Temporary workspace has been removed: {self.run_dir}"
        )