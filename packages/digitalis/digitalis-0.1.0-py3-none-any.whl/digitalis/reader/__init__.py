from urllib.parse import urlparse

from digitalis.reader.base import BackendSeeking

from .mcap import McapIterator


def create_reader(path_or_url: str) -> BackendSeeking:
    """Create an appropriate reader based on the input."""
    # Check if it's a URL
    parsed = urlparse(path_or_url)

    if parsed.scheme in ("ws", "wss"):
        raise NotImplementedError("WebSocket support is not yet implemented")

    return McapIterator(path_or_url)
