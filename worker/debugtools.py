import logging
import statistics
from time import perf_counter

logger = logging.getLogger(__name__)


def measure_execution_time(func):
    """Decorator that collects execution time samples for performance analysis."""

    def wrapper(*args, **kwargs):
        start_time = perf_counter()
        res = func(*args, **kwargs)
        end_time = perf_counter()

        instance = args[0]
        elapsed_ms = (end_time - start_time) * 1000
        instance.measure.append(elapsed_ms)
        return res

    return wrapper


def log_metrology_report(instance, target_sleep_ms: float = 100.0) -> None:
    """
    Logs execution time statistics used to estimate runner overhead
    and timing measurement stability.

    Args:
        instance: Object that stores execution time samples in `measure`.
        target_sleep_ms: Expected reference sleep duration in milliseconds.
    """
    measurements = instance.measure

    if not measurements:
        logger.warning("Metrology report skipped: no measurements collected.")
        return

    samples_count = len(measurements)
    average_wall_time_ms = sum(measurements) / samples_count
    estimated_system_overhead_ms = average_wall_time_ms - target_sleep_ms

    if samples_count > 1:
        standard_deviation_ms = statistics.stdev(measurements)
    else:
        standard_deviation_ms = 0.0

    stability_margin_ms = standard_deviation_ms * 3

    logger.info(
        "Runner metrology report | \n"
        "samples=%d | \n"
        "reference_sleep_ms=%.2f | \n"
        "avg_wall_time_ms=%.4f | \n"
        "estimated_overhead_ms=%.4f | \n"
        "stddev_ms=%.4f | \n"
        "stability_margin_ms=%.4f | \n"
        "recommended_timer_formula='clean_time_ms = wall_time_ms - %.1f' | \n"
        "stability_range_ms='%.2f..%.2f'",
        samples_count,
        target_sleep_ms,
        average_wall_time_ms,
        estimated_system_overhead_ms,
        standard_deviation_ms,
        stability_margin_ms,
        estimated_system_overhead_ms,
        average_wall_time_ms - stability_margin_ms,
        average_wall_time_ms + stability_margin_ms,
    )
