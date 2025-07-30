import bisect
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

from digitalis.reader.base import ChannelData


class TopicSearch(VerticalGroup):
    DEFAULT_CSS = """
        TopicSearch {
            Input {
                border: solid $primary;
            }
            ListView {
                border-right: $primary;

                ListItem {
                    padding: 0 1;
                }
            }
            # This allows us to use the cursor_up/down actions
            ListItem:disabled {
                display: none;
            }
        }
    """

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("down", "navigate(False)", show=False),
        Binding("up", "navigate(True)", show=False),
        Binding("c", "copy_topic", "Copy topic"),
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
            restrict=r"^[a-zA-Z0-9_/]*$",
        )
        self.nothing = ListItem(Label("No topics found"), id="no-topics")
        self.nothing.display = False
        yield ListView(self.nothing)

    async def update_topic_list(self) -> None:
        """Update the topic list with current stats and search filter."""
        topic_list = self.query_one(ListView)

        if not self.topics:
            # Hide all existing items
            for child in topic_list.children:
                child.disabled = True

            self.nothing.display = True
            return

        self.nothing.display = False

        # Filter topics based on search query
        query = self.search_query.lower()

        for child in topic_list.children:
            if child.id and child.id.startswith("c"):
                channel_id = int(child.id[1:])
                if channel_id in self.topics:
                    channel_data = self.topics[channel_id]
                    topic_name = channel_data.topic

                    # Show/hide based on search query
                    if query and query not in topic_name.lower():
                        child.disabled = True
                    else:
                        child.disabled = False

                else:
                    # Channel no longer exists, hide it
                    child.disabled = True

    def create_list_item(self, channel: ChannelData) -> ListItem:
        topic_name = channel.topic
        label_text = f"{topic_name}"
        if channel.message_count is not None:
            label_text += f"\n[dim]{channel.message_count} msgs[/dim]"

        item = ListItem(Label(label_text), id=f"c{channel.channel_id}")
        item.tooltip = Table(
            title=Text(topic_name, style="bold"),
            show_header=False,
            expand=True,
            box=box.MINIMAL,
        )
        item.tooltip.add_row("Channel ID", repr(channel.channel_id))
        item.tooltip.add_row("Schema", channel.schema_name)
        if channel.message_count is not None:
            item.tooltip.add_row("Message Count", repr(channel.message_count))
        if channel.hz is not None:
            item.tooltip.add_row("Hz", f"{channel.hz:.2f} Hz")

        return item

    async def add_new_topics(self) -> None:
        """Add any new topics that don't exist in the ListView yet."""
        topic_list = self.query_one(ListView)
        existing_ids = {
            int(child.id[1:])
            for child in topic_list.children
            if child.id and child.id.startswith("c")
        }

        # Get sorted list of existing topic children for bisect
        topic_children = [
            child
            for child in topic_list.children
            if child.id and child.id.startswith("c") and int(child.id[1:]) in self.topics
        ]
        topic_names = [self.topics[int(child.id[1:])].topic for child in topic_children if child.id]

        for channel_id, channel_data in sorted(self.topics.items(), key=lambda x: x[1].topic):
            if channel_id in existing_ids:
                continue

            item = self.create_list_item(channel_data)
            topic_name = channel_data.topic

            insert_index = bisect.bisect_left(topic_names, topic_name)
            insert_before = (
                topic_children[insert_index] if insert_index < len(topic_children) else None
            )

            await topic_list.append(item)
            if insert_before:
                topic_list.move_child(item, before=insert_before)

    def watch_topics(self, _stats: dict[int, ChannelData]) -> None:
        """Called when topic_stats changes."""
        self.call_later(self.add_new_topics)
        self.call_later(self.update_topic_list)

    def watch_search_query(self, _query: str) -> None:
        """Called when search_query changes."""
        self.call_later(self.update_topic_list)

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        """Called when a topic is highlighted in the list."""
        event.stop()
        if event.item and event.item.id and event.item.id.startswith("c"):
            selected_id = int(event.item.id[1:])
            self.selected = self.topics.get(selected_id)

    def watch_selected(self, selected: ChannelData | None) -> None:
        self.post_message(self.Changed(selected))

    def on_input_changed(self, event: Input.Changed) -> None:
        self.search_query = event.value

    def action_navigate(self, go_up: bool) -> None:
        """Navigate to next item in ListView when input is focused."""
        search_input = self.query_one(Input)
        topic_list = self.query_one(ListView)

        if search_input.has_focus:
            if go_up:
                topic_list.action_cursor_up()
            else:
                topic_list.action_cursor_down()

    def action_copy_topic(self) -> None:
        """Copy the selected topic to clipboard."""
        if self.selected:
            topic = self.selected.topic
            self.app.copy_to_clipboard(topic)
            self.notify(f"Copied topic '{topic}' to clipboard.")
