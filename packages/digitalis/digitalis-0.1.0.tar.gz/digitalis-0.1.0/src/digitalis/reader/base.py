from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class ChannelData:
    """Data structure to hold channel information."""

    channel_id: int
    topic: str

    message_count: int

    schema_id: int
    hz: float | None
    schema_name: str | None = None


@dataclass
class ChannelMessage:
    """Data structure to hold a channel message."""

    message: Any
    schema: str | None = None


# class Backend(ABC):
#     pass


class BackendSeeking(ABC):
    @property
    @abstractmethod
    def start_end_time(self) -> tuple[int, int]: ...

    @property
    @abstractmethod
    def channels(self) -> dict[int, ChannelData]: ...

    @abstractmethod
    async def get_message_at_time(
        self, channel_id: int, timestamp_ns: int
    ) -> ChannelMessage | None: ...


# class BackendNonSeeking(ABC):
#     pass
