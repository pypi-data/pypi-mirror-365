import logging
import time
from collections.abc import Generator
from contextlib import contextmanager
from datetime import datetime

logger = logging.getLogger(__name__)


@contextmanager
def function_time(name: str) -> Generator[None, None, None]:
    start = time.perf_counter_ns()
    try:
        yield
    finally:
        end = time.perf_counter_ns()
        duration = (end - start) / 1_000_000  # Convert to milliseconds
        logger.info(f"{name} took {duration:.2f} ms")


NANOSECONDS_PER_SECOND = 1_000_000_000
STRFTIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"


def nanoseconds_to_iso(timestamp_ns: int) -> str:
    """Convert a timestamp in nanoseconds to ISO 8601 format."""
    return datetime.fromtimestamp(timestamp_ns / NANOSECONDS_PER_SECOND).strftime(STRFTIME_FORMAT)


def nanoseconds_duration(ns_total: int) -> str:
    """Format a positive duration in nanoseconds as D:HH:MM:SS.mmm."""
    whole_seconds, rem_ns = divmod(ns_total, 1_000_000_000)
    milliseconds = rem_ns // 1_000_000  # truncate to milliseconds

    minutes, seconds = divmod(whole_seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)

    return f"{days}:{hours:02}:{minutes:02}:{seconds:02}.{milliseconds:03}"
