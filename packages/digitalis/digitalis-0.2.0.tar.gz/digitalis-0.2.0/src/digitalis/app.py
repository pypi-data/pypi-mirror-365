import os

from digitalis.screens.data import DataScreen

if os.environ.get("SSH_CONNECTION"):
    # Set default, overwriting still works this way
    os.environ.setdefault("TEXTUAL_FPS", "5")

import argparse
import logging
from typing import ClassVar

from textual.app import App
from textual.binding import BindingType
from textual.logging import TextualHandler

logging.basicConfig(
    level="NOTSET",
    handlers=[TextualHandler()],
)


class DigitalisApp(App):
    """MCAP Topic Browser app."""

    CSS_PATH = "app.tcss"
    BINDINGS: ClassVar[list[BindingType]] = [
        ("q", "quit", "Quit"),
    ]

    def __init__(self, file_or_url: str) -> None:
        super().__init__()
        self.file_or_url = file_or_url

    def on_mount(self) -> None:
        self.push_screen(DataScreen(self.file_or_url))


def main() -> None:
    parser = argparse.ArgumentParser(description="Digitalis - MCAP Topic Browser")
    parser.add_argument("file_or_url", help="Path to MCAP file or WebSocket URL to browse")

    args = parser.parse_args()
    DigitalisApp(args.file_or_url).run()


if __name__ == "__main__":
    main()
