import logging
from collections.abc import Callable
from functools import partial
from typing import ClassVar

from textual import on
from textual.app import ComposeResult
from textual.binding import BindingType
from textual.command import Hit, Hits, Provider
from textual.constants import MAX_FPS
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Footer, Header, Input

from digitalis.reader import create_reader
from digitalis.reader.base import BackendWrapper, ChannelData, ChannelMessage
from digitalis.ui.datapanel import DataView
from digitalis.ui.search import TopicSearch
from digitalis.ui.timecontrol import TimeControl
from digitalis.utilities import NANOSECONDS_PER_SECOND


class PanelSetTopic(Provider):
    def _set_channel(self, screen: "DataScreen", channel: ChannelData) -> None:
        """Set the selected topic in the DataScreen."""
        screen.selected_topic = channel

    async def search(self, query: str) -> Hits:
        """Search for Python files."""
        matcher = self.matcher(query)

        datascreen = None
        for screen in self.app.screen_stack:
            if isinstance(screen, DataScreen):
                datascreen = screen
                break
        else:
            logging.warning("No DataScreen found in app screen stack")
            return

        for channel in datascreen.channels.values():
            topic = channel.topic
            score = matcher.match(topic)

            if score > 0:
                help_text = f"{channel.schema_name}"
                if channel.message_count:
                    help_text += f" - {channel.message_count} msgs"
                yield Hit(
                    score,
                    matcher.highlight(topic),
                    partial(self._set_channel, datascreen, channel),
                    help=help_text,
                )


class PanelType(Provider):
    def _set_channel(self, screen: "DataScreen", channel: ChannelData) -> None:
        """Set the selected topic in the DataScreen."""
        screen.selected_topic = channel

    async def search(self, query: str) -> Hits:
        """Search for Python files."""
        matcher = self.matcher(query)

        datascreen = None
        for screen in self.app.screen_stack:
            if isinstance(screen, DataScreen):
                datascreen = screen
                break
        else:
            logging.warning("No DataScreen found in app screen stack")
            return

        dataview = datascreen.query_one(DataView)

        for panel in dataview.available_panels:
            name = f"Panel: {panel.__name__}"
            score = matcher.match(name)

            if score > 0:
                yield Hit(
                    score,
                    matcher.highlight(name),
                    partial(dataview.action_switch_panel, panel),
                    help=f"Switch to {panel.__name__} panel",
                )


class DataScreen(Screen):
    COMMANDS: ClassVar[set[type[Provider] | Callable[[], type[Provider]]]] = {
        PanelSetTopic,
        PanelType,
    }

    BINDINGS: ClassVar[list[BindingType]] = [
        ("space", "toggle_playback", "Play/Pause"),
        ("slash", "focus_search", "Search"),
        # BUG: after hiding we can unhide it again
        # ("t", "toggle_topic_search", "Toggle Topics"),
    ]
    TITLE = "Digitalis 🪻"

    selected_topic: reactive[ChannelData | None] = reactive(None)
    start_end: reactive[tuple[int, int]] = reactive((0, 0))
    current_time: reactive[int] = reactive(0)
    speed: reactive[float] = reactive(1.0)

    channels: reactive[dict[int, ChannelData]] = reactive({})

    def __init__(self, file_or_url: str) -> None:
        super().__init__()
        self.title = f"Digitalis 🪻 - {file_or_url} - FPS: {MAX_FPS}"

        self.reader = BackendWrapper(create_reader(file_or_url))
        logging.info(f"BACKEND: {type(self.reader)}")

    def on_new_channel(self, channel: list[ChannelData]) -> None:
        for ch in channel:
            self.channels[ch.channel_id] = ch

        self.mutate_reactive(DataScreen.channels)

    def on_new_message(self, channel_id: int, message: ChannelMessage) -> None:
        if self.selected_topic and self.selected_topic.channel_id == channel_id:
            data_panel = self.query_one(DataView)
            data_panel.data = message

        # Update current time from message timestamp for non-seeking backends
        if not self.reader.can_seek and message.timestamp_ns:
            self.current_time = message.timestamp_ns

    def compose(self) -> ComposeResult:
        """Compose our UI."""
        yield Header(icon="🪻")

        with Vertical():
            with Horizontal(id="main-panel"):
                yield TopicSearch().data_bind(topics=DataScreen.channels)
                yield DataView().data_bind(topic=DataScreen.selected_topic)
            yield TimeControl()

        yield Footer()

    def load_data(self) -> None:
        """Load data source and extract channel information."""
        if self.reader.can_seek:
            time_range = self.reader.time_range
            if time_range:
                self.start_end = time_range

    def watch_start_end(self, start_end: tuple[int, int]) -> None:
        """Update slider range when start/end times change."""
        time_control = self.query_one(TimeControl)
        time_control.start_end = start_end
        self.current_time = start_end[0]

    def watch_current_time(self, current_time: int) -> None:
        """Update time display when current time changes."""
        time_control = self.query_one(TimeControl)
        time_control.current_time = current_time

        if self.reader.can_seek:
            self.reader.seek_to_time(current_time)

    def watch_selected_topic(self, topic: ChannelData | None) -> None:
        # Unsubscribe from all channels first
        if topic:
            data_panel = self.query_one(DataView)
            data_panel.data = None
            self.run_worker(self.reader.subscribe(topic.channel_id, self.on_new_message))

    def on_mount(self) -> None:
        """Initialize the app when mounted."""
        self.load_data()

        # Configure time control based on backend capabilities
        time_control = self.query_one(TimeControl)
        time_control.can_seek = self.reader.can_seek

        # Only set up time updates for seeking backends
        if self.reader.can_seek:
            self.update_timer = self.set_interval(1 / MAX_FPS, self.update_time, pause=True)
        else:
            # For non-seeking, sync current_time with backend's current_time
            self.set_interval(1 / MAX_FPS, self.sync_time)

        self.run_worker(self.reader.start(), start=True, exit_on_error=True)
        self.reader.on_new_channel(self.on_new_channel)

    def update_time(self) -> None:
        """Update current time for seeking backends."""
        try:
            # Calculate time step based on speed and frame rate
            time_step = int(NANOSECONDS_PER_SECOND / MAX_FPS * self.speed)
            new_time = self.current_time + time_step

            self.current_time = new_time
        except Exception:
            logging.exception("Error updating time")
            # End of data, pause playback
            self.update_timer.pause()

    def sync_time(self) -> None:
        """Sync current time with backend for non-seeking backends."""
        backend_time = self.reader.current_time
        if backend_time is not None and backend_time != self.current_time:
            self.current_time = backend_time

    @on(TopicSearch.Changed)
    def topic_selected(self, event: TopicSearch.Changed) -> None:
        self.selected_topic = event.selected
        logging.info(f"New selection: {self.selected_topic}")

    @on(TimeControl.TimeChanged)
    def time_changed(self, event: TimeControl.TimeChanged) -> None:
        self.current_time = event.value

    @on(TimeControl.PlaybackChanged)
    def playback_changed(self, event: TimeControl.PlaybackChanged) -> None:
        # Only handle playback for seeking backends
        if self.reader.can_seek and hasattr(self, "update_timer"):
            if event.playing:
                self.update_timer.resume()
            else:
                self.update_timer.pause()

    @on(TimeControl.SpeedChanged)
    def speed_changed(self, event: TimeControl.SpeedChanged) -> None:
        self.speed = event.speed

    def action_toggle_playback(self) -> None:
        # Only allow playback for seeking backends
        if self.reader.can_seek:
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
