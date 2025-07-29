from mcap_ros2.decoder import DecoderFactory

from digitalis.exceptions import InvalidFileFormatError, MessageNotFoundError
from digitalis.reader.base import BackendSeeking, ChannelData, ChannelMessage
from digitalis.reader.mcap_read import McapReader
from digitalis.utilities import NANOSECONDS_PER_SECOND


class McapIterator(BackendSeeking):
    def __init__(self, path: str) -> None:
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

    @property
    def start_end_time(self) -> tuple[int, int]:
        """Return the start and end time of the messages in nanoseconds."""
        return self._stats.message_start_time, self._stats.message_end_time

    @property
    def channels(self) -> dict[int, ChannelData]:
        """Return a dictionary of channel data."""
        return self._channels

    async def get_message_at_time(
        self, channel_id: int, timestamp_ns: int
    ) -> ChannelMessage | None:
        """Get the most recent message for a specific channel at the given timestamp."""
        try:
            decoded_msg = self._mcap_reader.get_msg_decoded_by_timestamp(channel_id, timestamp_ns)
            channel = self._mcap_reader.summary.channels.get(channel_id)
            schema = self._mcap_reader.summary.schemas.get(channel.schema_id) if channel else None

            return ChannelMessage(
                message=decoded_msg,
                schema=schema.name if schema else None,
            )
        except (MessageNotFoundError, ValueError):
            # No message found for this channel at this timestamp
            return None

    def close(self) -> None:
        """Close the MCAP reader."""
        self._mcap_reader.close()

    def __enter__(self) -> "McapIterator":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:  # noqa: ANN001
        self.close()
