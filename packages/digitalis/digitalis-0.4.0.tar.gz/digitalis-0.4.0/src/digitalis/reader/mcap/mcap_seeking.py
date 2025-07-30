import logging
from collections.abc import Callable

from mcap_ros2.decoder import DecoderFactory

from digitalis.exceptions import InvalidFileFormatError, MessageNotFoundError
from digitalis.reader.base import Backend, ChannelData, ChannelMessage
from digitalis.reader.mcap.mcap_read import McapReader
from digitalis.utilities import NANOSECONDS_PER_SECOND

logger = logging.getLogger(__name__)


class McapSeeking(Backend):
    def __init__(self, path: str) -> None:
        logger.info(f"McapSeeking: {path}")
        self._mcap_reader = McapReader(path, decoder_factories=[DecoderFactory()])

        summary = self._mcap_reader.summary
        stats = summary.statistics
        if stats is None:
            raise InvalidFileFormatError("Statistics not found in MCAP file")
        self._stats = stats

        duration_ns = stats.message_end_time - stats.message_start_time
        self._channels: dict[int, ChannelData] = {}
        for channel in summary.channels.values():
            schema = summary.schemas.get(channel.schema_id)
            message_count = stats.channel_message_counts.get(channel.id, 0)
            self._channels[channel.id] = ChannelData(
                channel_id=channel.id,
                topic=channel.topic,
                schema_id=channel.schema_id,
                message_count=message_count,
                schema_name=schema.name if schema else None,
                hz=(
                    message_count / (duration_ns / NANOSECONDS_PER_SECOND)
                    if duration_ns > 0 and message_count > 0
                    else None
                ),
            )

        self._current_time = stats.message_start_time
        self._subscribed_channels: set[int] = set()
        self._new_message_callback: Callable[[int, ChannelMessage], None] | None = None

    @property
    def current_time(self) -> int | None:
        """Return current seek position in nanoseconds."""
        return self._current_time

    @property
    def can_seek(self) -> bool:
        """Return True since this backend supports seeking."""
        return True

    @property
    def time_range(self) -> tuple[int, int] | None:
        """Return the start and end time of the messages in nanoseconds."""
        return self._stats.message_start_time, self._stats.message_end_time

    def seek_to_time(self, timestamp_ns: int) -> None:
        """Seek to a specific time."""
        self._current_time = timestamp_ns
        self._fetch_and_notify()

    async def subscribe(self, channel_id: int) -> None:
        """Subscribe to a channel."""
        if channel_id not in self._channels:
            raise ValueError(f"Channel ID {channel_id} does not exist.")
        if channel_id in self._subscribed_channels:
            logger.info(f"Already subscribed to channel {channel_id}")
            return
        self._subscribed_channels.add(channel_id)
        logger.info(f"Subscribed to channel {channel_id}")
        self._fetch_and_notify()

    async def unsubscribe(self, channel_id: int) -> None:
        """Unsubscribe from a channel."""
        if channel_id not in self._subscribed_channels:
            logger.warning(f"Not subscribed to channel {channel_id}")
            return
        self._subscribed_channels.discard(channel_id)
        logger.info(f"Unsubscribed from channel {channel_id}")

    def get_message_at_time(self, channel_id: int, timestamp_ns: int) -> ChannelMessage | None:
        """Get the most recent message for a specific channel at the given timestamp."""
        try:
            decoded_msg = self._mcap_reader.get_msg_decoded_by_timestamp(channel_id, timestamp_ns)
            channel = self._mcap_reader.summary.channels.get(channel_id)
            schema = self._mcap_reader.summary.schemas.get(channel.schema_id) if channel else None

            return ChannelMessage(
                channel_id=channel_id,
                message=decoded_msg,
                schema=schema.name if schema else None,
                timestamp_ns=timestamp_ns,
            )
        except (MessageNotFoundError, ValueError):
            # No message found for this channel at this timestamp
            return None

    def _fetch_and_notify(self) -> None:
        """Fetch current message and notify callback if available."""
        if not self._subscribed_channels or self._new_message_callback is None:
            return

        for channel_id in self._subscribed_channels:
            msg = self.get_message_at_time(channel_id, self._current_time)
            if msg is not None:
                self._new_message_callback(channel_id, msg)

    def close(self) -> None:
        """Close the MCAP reader."""
        self._mcap_reader.close()

    def on_new_channel(self, callback: Callable[[list[ChannelData]], None]) -> None:
        callback(list(self._channels.values()))

    def on_new_message(self, callback: Callable[[int, ChannelMessage], None]) -> None:
        """Register callback for new messages."""

        self._new_message_callback = callback
        # If we already have subscriptions, immediately notify with current messages
        if self._subscribed_channels:
            self._fetch_and_notify()

    async def start(self) -> None:
        """Start the backend. For MCAP seeking, already initialized in __init__."""
