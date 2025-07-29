from datetime import datetime

from textual import on
from textual.app import ComposeResult
from textual.containers import HorizontalGroup, VerticalGroup
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import Button, Label, Select
from textual_slider import Slider

from digitalis.utilities import NANOSECONDS_PER_SECOND

SPEEDS: list[float] = [
    0.01,
    0.02,
    0.05,
    0.1,
    0.2,
    0.5,
    1.0,
    2.0,
    3.0,
    5.0,
    10.0,
    20.0,
    50.0,
]


class ButtonGroup(HorizontalGroup):
    DEFAULT_CSS = """
        ButtonGroup {
            align: center middle;
        }

        ButtonGroup > #stop {
            display: none;
        }

        ButtonGroup.started > #start {
            display: none;
        }

        ButtonGroup.started > #stop {
            display: block;
        }
    """

    class Changed(Message):
        def __init__(self, value: bool) -> None:
            super().__init__()
            self.value: bool = value

    def on_button_pressed(self, _event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        self.toggle()

    def toggle(self) -> None:
        """Toggle playback with space bar."""
        if self.has_class("started"):
            self.remove_class("started")
            self.post_message(self.Changed(False))
        else:
            self.add_class("started")
            self.post_message(self.Changed(True))

    def compose(self) -> ComposeResult:
        """Create child widgets of a stopwatch."""
        yield Button("Start", id="start", variant="success", compact=True)
        yield Button("Stop", id="stop", variant="error", compact=True)


class TimeControl(VerticalGroup):
    DEFAULT_CSS = """
        TimeControl {
            Slider {
                width: 100%;
            }
            Select {
                width: 25;
            }
        }
    """

    current_time: reactive[int] = reactive(0)
    start_end: reactive[tuple[int, int]] = reactive((0, 0))
    speed: reactive[float] = reactive(1.0)

    class TimeChanged(Message):
        def __init__(self, value: int) -> None:
            super().__init__()
            self.value: int = value

    class PlaybackChanged(Message):
        def __init__(self, playing: bool) -> None:
            super().__init__()
            self.playing: bool = playing

    class SpeedChanged(Message):
        def __init__(self, speed: float) -> None:
            super().__init__()
            self.speed: float = speed

    def compose(self) -> ComposeResult:
        """Compose the TimeControl widget."""
        yield Slider(id="time-slider", min=0, max=10)
        with HorizontalGroup(id="time-control"):
            yield Label("00:00:00", id="time-current")
            yield ButtonGroup()
            yield Select(
                ((f"{line}x", line) for line in SPEEDS),
                prompt="Speed",
                value=1.0,
                compact=True,
            )

    def watch_start_end(self, se: tuple[int, int]) -> None:
        """Update slider range when start/end times change."""
        slider = self.query_one(Slider)
        slider.min = se[0]
        slider.max = se[1]

    def watch_current_time(self, ct: int) -> None:
        """Update time display when current time changes."""
        label = self.query_one("#time-current", Label)
        label.update(datetime.fromtimestamp(ct / NANOSECONDS_PER_SECOND).isoformat())
        # Update slider position
        slider = self.query_one(Slider)
        with slider.prevent(Slider.Changed):
            slider.value = ct

    @on(Slider.Changed)
    def time_change(self, change: Slider.Changed) -> None:
        """Handle slider time changes."""
        self.post_message(self.TimeChanged(change.value))

    @on(ButtonGroup.Changed)
    def play_pause(self, event: ButtonGroup.Changed) -> None:
        self.post_message(self.PlaybackChanged(event.value))

    @on(Select.Changed)
    def speed_changed(self, event: Select.Changed) -> None:
        val = event.value
        if isinstance(val, float):
            self.post_message(self.SpeedChanged(val))

    def toggle(self) -> None:
        """Toggle playback with space bar."""
        button_group = self.query_one(ButtonGroup)
        button_group.toggle()
