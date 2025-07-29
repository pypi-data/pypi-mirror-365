from typing import ClassVar

from rich import box
from rich.table import Table
from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import VerticalGroup
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import (
    Input,
    Label,
    ListItem,
    ListView,
)

from digitalis.reader.mcap import ChannelData


class TopicSearch(VerticalGroup):
    DEFAULT_CSS = """
        TopicSearch {
            width: 30%;
            Input {
                border: solid $primary;
            }
            ListView {
                border-right: $primary;

                ListItem {
                    padding: 0 1;
                }

            }
        }
    """

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("down", "navigate_down(False)", show=False),
        Binding("up", "navigate_up(True)", show=False),
    ]

    topics: reactive[dict[int, ChannelData]] = reactive({})
    search_query: reactive[str] = reactive("")

    selected: reactive[ChannelData | None] = reactive(None)

    class Changed(Message):
        def __init__(self, selected: ChannelData | None) -> None:
            super().__init__()
            self.selected: ChannelData | None = selected

    def compose(self) -> ComposeResult:
        """Create child widgets of a stopwatch."""
        yield Input(
            placeholder="Search topics...",
            id="search-input",
        )
        yield ListView()

    async def update_topic_list(self) -> None:
        """Update the topic list with current stats and search filter."""
        topic_list = self.query_one(ListView)

        if not self.topics:
            await topic_list.clear()
            await topic_list.append(ListItem(Label("No topics found")))
            return

        # Filter topics based on search query
        query = self.search_query.lower()
        filtered_items = []
        for channel_id, channel_data in sorted(self.topics.items(), key=lambda x: x[1].topic):
            topic_name = channel_data.topic
            if query and query not in topic_name.lower():
                continue
            message_count = channel_data.message_count
            label_text = f"{topic_name}\n[dim]{message_count} msgs[/dim]"
            item = ListItem(Label(label_text), id=f"c{channel_id}")

            table = Table(
                title=Text(topic_name, style="bold"),
                show_header=False,
                expand=True,
                box=box.MINIMAL,
            )

            table.add_row("Channel ID", repr(channel_id))
            table.add_row("Message Count", repr(channel_data.message_count))
            table.add_row("Schema", channel_data.schema_name)
            if channel_data.hz is not None:
                table.add_row("Hz", f"{channel_data.hz:.2f} Hz")

            item.tooltip = table

            filtered_items.append(item)
        await topic_list.clear()
        await topic_list.extend(filtered_items)

    def watch_topics(self, _stats: dict[int, ChannelData]) -> None:
        """Called when topic_stats changes."""
        self.call_later(self.update_topic_list)

    def watch_search_query(self, _query: str) -> None:
        """Called when search_query changes."""
        self.call_later(self.update_topic_list)

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        """Called when a topic is highlighted in the list."""
        event.stop()
        if event.item and event.item.id:
            selected_id = int(event.item.id[1:])
            self.selected = self.topics.get(selected_id)

    def watch_selected(self, selected: ChannelData | None) -> None:
        self.post_message(self.Changed(selected))

    def on_input_changed(self, event: Input.Changed) -> None:
        self.search_query = event.value

    def action_navigate_down(self, go_up: bool) -> None:
        """Navigate to next item in ListView when input is focused."""
        search_input = self.query_one(Input)
        topic_list = self.query_one(ListView)

        if search_input.has_focus:
            if go_up < 0:
                topic_list.action_cursor_up()
            else:
                topic_list.action_cursor_down()
