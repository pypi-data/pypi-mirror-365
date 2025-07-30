import asyncio
import contextlib
import json
import logging
import struct
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any

import websockets
from mcap.well_known import SchemaEncoding
from mcap_ros2._dynamic import DecoderFunction, generate_dynamic

from .base import Backend, ChannelData, ChannelMessage

logger = logging.getLogger(__name__)


class OpCodes(Enum):
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"
    ADVERTISE = "advertise"
    UNADVERTISE = "unadvertise"
    SERVER_INFO = "serverInfo"


@dataclass
class AdvertisedChannel:
    id: int
    topic: str
    encoding: str
    schema_name: str
    schema: str
    schema_encoding: str


class ROS2DecodeError(Exception):
    """Raised if a MCAP message record cannot be decoded as a ROS2 message."""


def get_decoder(schema: AdvertisedChannel, cache: dict[int, DecoderFunction]) -> DecoderFunction:
    if schema is None or schema.schema_encoding != SchemaEncoding.ROS2:
        msg = f"Invalid schema for ROS2 decoding: {schema.schema_encoding}"
        raise ROS2DecodeError(msg)
    decoder = cache.get(schema.id)
    if decoder is None:
        type_dict = generate_dynamic(schema.schema_name, schema.schema)
        if schema.schema_name not in type_dict:
            raise ROS2DecodeError(f'schema parsing failed for "{schema.schema_name}"')
        decoder = type_dict[schema.schema_name]
        cache[schema.id] = decoder
    return decoder


class WebSocketBackend(Backend):
    """Non-seeking WebSocket backend for real-time data streaming."""

    def __init__(self, uri: str, subprotocol: str = "foxglove.websocket.v1") -> None:
        logger.info(f"WebSocket: {uri}")
        self.uri = uri
        self.subprotocol = subprotocol

        self._ws: websockets.ClientConnection | None = None
        self._advertised_channels: dict[int, AdvertisedChannel] = {}
        self._next_sub_id = 0
        self._active_subscriptions: set[int] = set()
        self._subscription_to_channel: dict[int, int] = {}
        self._channel_to_subscription: dict[int, int] = {}
        self._decoder_cache: dict[int, DecoderFunction] = {}

        self._current_time: int | None = None
        self._channel_callback: Callable[[list[ChannelData]], None] | None = None
        self._message_callback: Callable[[int, ChannelMessage], None] | None = None

        self._running = False
        self._message_task: asyncio.Task | None = None

    @property
    def current_time(self) -> int | None:
        return self._current_time

    @property
    def can_seek(self) -> bool:
        return False

    @property
    def time_range(self) -> tuple[int, int] | None:
        return None

    async def subscribe(self, channel_id: int) -> None:
        if channel_id in self._channel_to_subscription:
            logger.info(f"Already subscribed to channel {channel_id}")
            return

        if not self._running:
            logger.warning("Backend not connected yet, queueing subscription")

        try:
            await self._subscribe_async(channel_id)
        except RuntimeError:
            logger.warning("No event loop running, cannot subscribe")

    async def unsubscribe(self, channel_id: int) -> None:
        """Unsubscribe from a specific channel."""
        sub_id = self._channel_to_subscription.get(channel_id)
        if sub_id is None:
            logger.warning(f"Not subscribed to channel {channel_id}")
            return

        if not self._running or not self._ws:
            logger.warning("Backend not connected, cannot unsubscribe")
            return

        try:
            await self._unsubscribe_async(sub_id, channel_id)
        except RuntimeError:
            logger.warning("No event loop running, cannot unsubscribe")

    def on_new_channel(self, callback: Callable[[list[ChannelData]], None]) -> None:
        self._channel_callback = callback

    def on_new_message(self, callback: Callable[[int, ChannelMessage], None]) -> None:
        self._message_callback = callback

    async def start(self) -> None:
        """Start the WebSocket connection and message loop."""
        if self._running:
            return

        try:
            await self._connect()
            self._running = True
            self._message_task = asyncio.create_task(self._handle_messages_loop())
        except Exception:
            logger.exception("Failed to connect to WebSocket server")
            self._running = False

    async def stop(self) -> None:
        """Stop the WebSocket connection."""
        if not self._running:
            return

        self._running = False
        if self._message_task:
            self._message_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._message_task

        if self._ws and self._active_subscriptions:
            await self._ws.send(
                json.dumps(
                    {
                        "op": OpCodes.UNSUBSCRIBE.value,
                        "subscriptionIds": list(self._active_subscriptions),
                    }
                )
            )

        if self._ws:
            await self._ws.close()

        logger.info("WebSocket backend stopped")

    async def _connect(self) -> None:
        subprotocol = websockets.Subprotocol(self.subprotocol)
        self._ws = await websockets.connect(self.uri, subprotocols=[subprotocol])
        logger.info(f"Connected to {self.uri}")

    async def _subscribe_async(self, channel_id: int) -> None:
        if not self._ws:
            logger.warning("Not connected, cannot subscribe")
            return

        sub_id = self._next_sub_id
        self._next_sub_id += 1

        msg = {
            "op": OpCodes.SUBSCRIBE.value,
            "subscriptions": [{"id": sub_id, "channelId": channel_id}],
        }
        await self._ws.send(json.dumps(msg))
        logger.info(f"Subscribed to channel {channel_id} with subscription ID {sub_id}")
        self._active_subscriptions.add(sub_id)
        self._subscription_to_channel[sub_id] = channel_id
        self._channel_to_subscription[channel_id] = sub_id

    async def _unsubscribe_async(self, sub_id: int, channel_id: int) -> None:
        if not self._ws:
            logger.warning("Not connected, cannot unsubscribe")
            return

        msg = {
            "op": OpCodes.UNSUBSCRIBE.value,
            "subscriptionIds": [sub_id],
        }
        await self._ws.send(json.dumps(msg))
        logger.info(f"Unsubscribed from channel {channel_id} (subscription ID {sub_id})")

        # Clean up tracking
        self._active_subscriptions.discard(sub_id)
        self._subscription_to_channel.pop(sub_id, None)
        self._channel_to_subscription.pop(channel_id, None)

    async def _handle_messages_loop(self) -> None:
        if not self._ws:
            return

        try:
            async for raw in self._ws:
                if isinstance(raw, bytes):
                    await self._handle_binary(raw)
                elif isinstance(raw, str):
                    await self._handle_json(raw)
                else:
                    logger.warning(f"Received unknown message type: {type(raw)}")
        except websockets.ConnectionClosed:
            logger.info("WebSocket connection closed")
        except Exception:
            logger.exception("Error in message loop")
        finally:
            self._running = False

    async def _handle_json(self, text: str) -> None:
        msg = json.loads(text)
        op = msg.get("op")

        if op == OpCodes.SERVER_INFO.value:
            logger.info(f"Server info: {msg}")
        elif op == OpCodes.ADVERTISE.value:
            new_channels = []
            for ch in msg.get("channels", []):
                channel = AdvertisedChannel(
                    id=ch["id"],
                    topic=ch["topic"],
                    encoding=ch["encoding"],
                    schema_name=ch["schemaName"],
                    schema=ch["schema"],
                    schema_encoding=ch["schemaEncoding"],
                )
                self._advertised_channels[ch["id"]] = channel

                channel_data = ChannelData(
                    channel_id=ch["id"],
                    topic=ch["topic"],
                    schema_id=ch["id"],
                    schema_name=ch["schemaName"],
                )
                new_channels.append(channel_data)

                logger.info(f"Channel advertised: {ch['topic']} (ID: {ch['id']})")

            if new_channels and self._channel_callback:
                self._channel_callback(new_channels)

        elif op == OpCodes.UNADVERTISE.value:
            for cid in msg.get("channelIds", []):
                self._advertised_channels.pop(cid, None)
                logger.info(f"Channel unadvertised: {cid}")
        else:
            logger.debug(f"Unknown JSON operation: {op}")

    async def _handle_binary(self, data: bytes) -> None:
        opcode = data[0]
        if opcode == 0x01:  # Message Data
            sub_id = struct.unpack_from("<I", data, 1)[0]
            timestamp = struct.unpack_from("<Q", data, 5)[0]
            payload = data[1 + 4 + 8 :]

            self._current_time = timestamp

            logger.debug(f"Received message on subscription {sub_id}, {len(payload)} bytes")

            if self._message_callback:
                # Get the actual channel ID from subscription mapping
                channel_id = self._subscription_to_channel.get(sub_id)
                if channel_id is None:
                    logger.warning(f"No channel mapping for subscription {sub_id}")
                    return

                message_obj: Any = payload
                schema_str = None

                if channel_id in self._advertised_channels:
                    channel = self._advertised_channels[channel_id]
                    try:
                        decoder = get_decoder(channel, self._decoder_cache)
                        message_obj = decoder(payload)
                        schema_str = channel.schema_name
                    except Exception:  # noqa: BLE001
                        logger.debug(f"Failed to decode message for channel {channel_id}")

                channel_message = ChannelMessage(
                    channel_id=channel_id,
                    message=message_obj,
                    schema=schema_str,
                    timestamp_ns=timestamp,
                )
                self._message_callback(channel_id, channel_message)
        else:
            logger.debug(f"Unknown binary opcode: {opcode}")
