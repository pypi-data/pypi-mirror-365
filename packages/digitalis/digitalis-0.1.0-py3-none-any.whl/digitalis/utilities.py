import logging
import time
from collections.abc import Generator
from contextlib import contextmanager

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
