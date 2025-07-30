from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Generic, TypeVar


@dataclass(slots=True, frozen=True)
class ChannelData:
    """Data structure to hold channel information."""

    channel_id: int
    topic: str

    schema_id: int
    hz: float | None = None
    message_count: int | None = None
    schema_name: str | None = None


T = TypeVar("T", bound=Any)


@dataclass(slots=True, frozen=True)
class ChannelMessage(Generic[T]):
    """Data structure to hold a channel message."""

    channel_id: int
    message: T
    timestamp_ns: int
    schema: str | None = None


class Backend(ABC):
    """Unified backend interface for both seeking and non-seeking data sources."""

    @property
    @abstractmethod
    def current_time(self) -> int | None:
        """Return current timestamp in nanoseconds. None if no data processed yet."""
        ...

    @property
    @abstractmethod
    def can_seek(self) -> bool:
        """Return True if this backend supports seeking to specific times."""
        ...

    @property
    @abstractmethod
    def time_range(self) -> tuple[int, int] | None:
        """Return (start, end) time range in nanoseconds. None for non-seeking backends."""
        ...

    @abstractmethod
    async def subscribe(self, channel_id: int) -> None:
        """Subscribe to receive messages from a channel."""
        ...

    @abstractmethod
    async def unsubscribe(self, channel_id: int) -> None:
        """Unsubscribe from receiving messages from a channel."""
        ...

    @abstractmethod
    def on_new_channel(self, callback: Callable[[list[ChannelData]], None]) -> None:
        """Register callback for new channels. Optional for seeking backends."""

    @abstractmethod
    def on_new_message(self, callback: Callable[[int, ChannelMessage], None]) -> None:
        """Register callback for new messages. Optional for seeking backends."""

    def seek_to_time(self, timestamp_ns: int) -> None:  # noqa: B027, seeking only
        """Seek to a specific time. No-op for non-seeking backends."""

    async def start(self) -> None:  # noqa: B027
        """Start the backend. Default implementation does nothing."""


class BackendWrapper:
    """A wrapper for the backend to provide a consistent interface."""

    def __init__(self, backend: Backend) -> None:
        self._backend = backend

        self._channel_subscribers: set[Callable[[list[ChannelData]], None]] = set()
        self._channels: dict[int, ChannelData] = {}
        self._backend.on_new_channel(self._internal_on_new_channel)

        self._message_subscribers: dict[int, set[Callable[[int, ChannelMessage], None]]] = {}
        self._message_cache: dict[int, ChannelMessage] = {}
        self._backend.on_new_message(self._internal_on_new_message)

    def _internal_on_new_channel(self, channel: list[ChannelData]) -> None:
        # update channel cache
        for ch in channel:
            self._channels[ch.channel_id] = ch

        for callback in self._channel_subscribers:
            callback(channel)

    def on_new_channel(self, callback: Callable[[list[ChannelData]], None]) -> None:
        """Register a callback for new channel data."""
        self._channel_subscribers.add(callback)
        callback(list(self._channels.values()))

    def _internal_on_new_message(self, channel: int, message: ChannelMessage) -> None:
        self._message_cache[channel] = message
        for callback in self._message_subscribers.get(channel, []):
            callback(channel, message)

    async def subscribe(
        self, channel_id: int, callback: Callable[[int, ChannelMessage], None]
    ) -> None:
        subs = self._message_subscribers.get(channel_id)
        if subs is None:
            await self._backend.subscribe(channel_id)
            self._message_subscribers[channel_id] = subs = set()
        subs.add(callback)
        if message := self._message_cache.get(channel_id):
            callback(channel_id, message)

    async def unsubscribe(self, callback: Callable[[int, ChannelMessage], None]) -> None:
        """Unsubscribe from a channel."""
        for channel_id, subs in self._message_subscribers.items():
            if callback in subs:
                subs.remove(callback)
                if not subs:
                    # If no more subscribers, unsubscribe from backend
                    del self._message_subscribers[channel_id]
                    await self._backend.unsubscribe(channel_id)
                break

    @property
    def can_seek(self) -> bool:
        return self._backend.can_seek

    def seek_to_time(self, timestamp: int) -> None:
        self._backend.seek_to_time(timestamp)

    @property
    def time_range(self) -> tuple[int, int] | None:
        return self._backend.time_range

    @property
    def current_time(self) -> int | None:
        return self._backend.current_time

    async def start(self) -> None:
        """Start the backend."""
        return await self._backend.start()
