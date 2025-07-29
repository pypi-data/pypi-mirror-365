import argparse
import logging
from typing import ClassVar

from textual import on
from textual.app import App, ComposeResult
from textual.binding import BindingType
from textual.containers import Horizontal, Vertical
from textual.logging import TextualHandler
from textual.reactive import reactive
from textual.widgets import Footer, Header, Input

from digitalis.reader import create_reader
from digitalis.reader.mcap import ChannelData
from digitalis.ui.datapanel import DataPanel
from digitalis.ui.search import TopicSearch
from digitalis.ui.timecontrol import TimeControl
from digitalis.utilities import NANOSECONDS_PER_SECOND

logging.basicConfig(
    level="NOTSET",
    handlers=[TextualHandler()],
)


FPS = 20


class DigitalisApp(App):
    """MCAP Topic Browser app."""

    CSS_PATH = "app.tcss"
    BINDINGS: ClassVar[list[BindingType]] = [
        ("q", "quit", "Quit"),
        ("r", "reload", "Reload Data"),
        ("space", "toggle_playback", "Play/Pause"),
        ("slash", "focus_search", "Search"),
        ("t", "toggle_topic_search", "Toggle Topics"),
    ]
    TITLE = "Digitalis 🪻"

    selected_topic: reactive[ChannelData | None] = reactive(None)
    start_end: reactive[tuple[int, int]] = reactive((0, 0))
    current_time: reactive[int] = reactive(0)
    speed: reactive[float] = reactive(1.0)

    def __init__(self, file_or_url: str) -> None:
        super().__init__()
        self.reader = create_reader(file_or_url)

        self.title = f"Digitalis 🪻 - File: {file_or_url}"

    def compose(self) -> ComposeResult:
        """Compose our UI."""
        yield Header()

        with Vertical():
            with Horizontal(id="main-panel"):
                yield TopicSearch()
                yield DataPanel(id="details-panel")
            yield TimeControl(id="time-bar")

        yield Footer()

    def load_data(self) -> None:
        """Load data source and extract channel information."""
        search = self.query_one(TopicSearch)
        search.topics = self.reader.channels
        self.start_end = self.reader.start_end_time

    def watch_start_end(self, se: tuple[int, int]) -> None:
        """Update slider range when start/end times change."""
        time_control = self.query_one("#time-bar", TimeControl)
        time_control.start_end = se
        self.current_time = se[0]

    async def fetch_data(self) -> None:
        # Only update the selected channel if one is selected
        if self.selected_topic:
            msg = await self.reader.get_message_at_time(
                self.selected_topic.channel_id, self.current_time
            )
            data_panel = self.query_one("#details-panel", DataPanel)
            data_panel.data = msg

    async def watch_current_time(self, ct: int) -> None:
        """Update time display when current time changes."""
        time_control = self.query_one("#time-bar", TimeControl)
        time_control.current_time = ct
        self.run_worker(self.fetch_data(), exclusive=True)

    async def watch_selected_topic(self, _topic: ChannelData | None) -> None:
        self.run_worker(self.fetch_data(), exclusive=True)

    def on_mount(self) -> None:
        """Initialize the app when mounted."""
        self.load_data()

        self.update_timer = self.set_interval(1 / FPS, self.update_time, pause=True)

    def update_time(self) -> None:
        """Update current time from data source."""
        try:
            # Calculate time step based on speed and frame rate
            time_step = int(NANOSECONDS_PER_SECOND / FPS * self.speed)
            new_time = self.current_time + time_step

            self.current_time = new_time
        except Exception:
            logging.exception("Error updating time")
            # End of data, pause playback
            self.update_timer.pause()

    @on(TopicSearch.Changed)
    def topic_selected(self, event: TopicSearch.Changed) -> None:
        self.selected_topic = event.selected

    @on(TimeControl.TimeChanged)
    def time_changed(self, event: TimeControl.TimeChanged) -> None:
        self.current_time = event.value

    @on(TimeControl.PlaybackChanged)
    def playback_changed(self, event: TimeControl.PlaybackChanged) -> None:
        if event.playing:
            self.update_timer.resume()
        else:
            self.update_timer.pause()

    @on(TimeControl.SpeedChanged)
    def speed_changed(self, event: TimeControl.SpeedChanged) -> None:
        self.speed = event.speed

    def action_reload(self) -> None:
        """Reload the data source."""
        self.load_data()
        self.selected_topic = None

    def action_toggle_playback(self) -> None:
        time_control = self.query_one(TimeControl)
        time_control.toggle()

    def action_focus_search(self) -> None:
        """Focus the search input."""
        search_input = self.query_one(Input)
        search_input.focus()

    def action_toggle_topic_search(self) -> None:
        """Toggle the TopicSearch visibility."""
        topic_search = self.query_one(TopicSearch)
        topic_search.display = not topic_search.display


def main() -> None:
    parser = argparse.ArgumentParser(description="Digitalis - MCAP Topic Browser")
    parser.add_argument("file_or_url", help="Path to MCAP file or WebSocket URL to browse")

    args = parser.parse_args()
    DigitalisApp(args.file_or_url).run()


if __name__ == "__main__":
    main()
