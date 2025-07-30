import logging
import threading
import time
from collections.abc import Callable
from pathlib import Path

from mcap.exceptions import McapError
from mcap.reader import NonSeekingReader
from mcap.records import Schema
from mcap.well_known import SchemaEncoding
from mcap_ros2._dynamic import (
    DecoderFunction,
    generate_dynamic,
)

from digitalis.reader.base import Backend, ChannelData, ChannelMessage
from digitalis.utilities import NANOSECONDS_PER_SECOND


class ROS2DecodeError(McapError):
    """Raised if a MCAP message record cannot be decoded as a ROS2 message."""


class ROS2EncodeError(McapError):
    """Raised if a ROS2 message cannot be encoded."""


def get_decoder(schema: Schema, cache: dict[int, DecoderFunction]) -> DecoderFunction:
    if schema is None or schema.encoding != SchemaEncoding.ROS2:
        raise ROS2DecodeError(f'can\'t parse schema with encoding "{schema}"')
    decoder = cache.get(schema.id)
    if decoder is None:
        type_dict = generate_dynamic(schema.name, schema.data.decode())
        if schema.name not in type_dict:
            raise ROS2DecodeError(f'schema parsing failed for "{schema.name}"')
        decoder = type_dict[schema.name]
        cache[schema.id] = decoder
    return decoder


logger = logging.getLogger(__name__)


class McapNonSeeking(Backend):
    def __init__(self, path: str) -> None:
        logger.info(f"McapNonSeeking: {path}")
        # callbacks
        self._new_channel_callback: Callable[[list[ChannelData]], None] | None = None
        self._new_message_callback: Callable[[int, ChannelMessage], None] | None = None

        self._channels: dict[int, ChannelData] = {}
        self._decoder_cache: dict[int, DecoderFunction] = {}
        self._subscribed_channels: set[int] = set()
        self._current_time: int | None = None

        self.file = Path(path).open("rb")  # noqa: SIM115
        reader = NonSeekingReader(self.file)
        self.iterator = iter(reader.iter_messages())

        self._worker_thread = threading.Thread(target=self._worker, daemon=True)
        self._worker_thread.start()

    def _worker(self) -> None:
        last_log_time = None
        while True:
            msg = next(self.iterator, None)
            if msg is None:
                break
            schema, channel, message = msg
            if schema is None:
                continue

            channel_id = channel.id
            if channel_id not in self._channels:
                channel_data = ChannelData(
                    channel_id=channel_id,
                    topic=channel.topic,
                    schema_id=channel.schema_id,
                    schema_name=schema.name if schema else None,
                )
                self._channels[channel_id] = channel_data
                if self._new_channel_callback:
                    self._new_channel_callback([channel_data])

            # Update current time with latest message timestamp
            self._current_time = message.log_time

            if channel.id in self._subscribed_channels:
                decoder = get_decoder(schema, self._decoder_cache)
                decoded_message = decoder(message.data)
                channel_message = ChannelMessage(
                    channel_id=channel_id,
                    message=decoded_message,
                    schema=schema.name if schema else None,
                    timestamp_ns=message.log_time,
                )

                if self._new_message_callback:
                    self._new_message_callback(channel_id, channel_message)

            if last_log_time is not None:
                diff = message.log_time - last_log_time
                time.sleep(diff / NANOSECONDS_PER_SECOND)

            last_log_time = message.log_time

    @property
    def current_time(self) -> int | None:
        """Return current timestamp from latest processed message."""
        return self._current_time

    @property
    def can_seek(self) -> bool:
        """Return False since this backend doesn't support seeking."""
        return False

    @property
    def time_range(self) -> tuple[int, int] | None:
        """Return None since non-seeking backends don't have a defined range."""
        return None

    async def subscribe(self, channel_id: int) -> None:
        """Subscribe to a channel."""
        if channel_id not in self._channels:
            raise ValueError(f"Channel ID {channel_id} does not exist.")
        if channel_id in self._subscribed_channels:
            logger.info(f"Already subscribed to channel {channel_id}")
            return
        self._subscribed_channels.add(channel_id)
        logger.info(f"Subscribed to channel {channel_id}")

    async def unsubscribe(self, channel_id: int) -> None:
        """Unsubscribe from a channel."""
        if channel_id not in self._subscribed_channels:
            logger.warning(f"Not subscribed to channel {channel_id}")
            return
        self._subscribed_channels.discard(channel_id)
        logger.info(f"Unsubscribed from channel {channel_id}")

    def close(self) -> None:
        self.file.close()

    def on_new_channel(self, callback: Callable[[list[ChannelData]], None]) -> None:
        """Register a callback for new channels."""
        self._new_channel_callback = callback

    def on_new_message(self, callback: Callable[[int, ChannelMessage], None]) -> None:
        """Register a callback for new messages."""
        self._new_message_callback = callback

    async def start(self) -> None:
        """Start the backend. For MCAP non-seeking, already started in __init__."""
