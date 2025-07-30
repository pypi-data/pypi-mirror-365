import logging
from urllib.parse import urlparse

from mcap.reader import make_reader

from digitalis.reader.base import Backend

from .mcap.mcap_nonseeking import McapNonSeeking
from .mcap.mcap_seeking import McapSeeking
from .websocket_backend import WebSocketBackend

logger = logging.getLogger(__name__)


def create_reader(path_or_url: str) -> Backend:
    """Create an appropriate reader based on the input."""

    parsed = urlparse(path_or_url)
    logger.info(f"Selecting backend: {path_or_url}")

    if parsed.scheme in ("ws", "wss"):
        return WebSocketBackend(path_or_url)

    try:
        with open(path_or_url, "rb") as f:  # noqa: PTH123
            reader = make_reader(f)
            assert reader.get_summary() is not None, "MCAP file must have a summary"
        return McapSeeking(path_or_url)
    except Exception:  # noqa: BLE001, assume broken MCAP
        return McapNonSeeking(path_or_url)
