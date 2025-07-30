from dataclasses import dataclass
from typing import ClassVar

from textual.message import Message
from textual.widget import Widget

from digitalis.reader.base import ChannelMessage


@dataclass
class Settings:
    action: str
    label: str
    description: str = ""


class BasePanel:
    SETTINGS: ClassVar[list[Settings]] = []

    class Subscribe(Message):
        def __init__(self, channel_id: int) -> None:
            super().__init__()
            self.channel_id: int = channel_id

    class Unsubscribe(Message):
        def __init__(self, channel_id: int) -> None:
            super().__init__()
            self.channel_id: int = channel_id

    def on_message(self, message: ChannelMessage) -> None:
        """Handle incoming messages."""
