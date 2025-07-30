from textual.app import ComposeResult
from textual.containers import Container
from textual.reactive import reactive
from textual.suggester import SuggestFromList
from textual.widgets import Input, Label, Static

from digitalis.reader.base import ChannelData
from digitalis.ui.data.base import BasePanel


class SettingsRenderer(Container):
    """Handles rendering of panel-specific settings in the UI."""

    panel: reactive[BasePanel | None] = reactive(None)
    topics: reactive[dict[int, ChannelData]] = reactive({})

    def get_topic_suggestions(self) -> list[str]:
        """Get list of available topic names for suggestions."""
        return [ch.topic for ch in self.topics.values()]

    def compose(self) -> ComposeResult:
        yield Static("Select a panel to edit its settings.")

    def watch_panel(self, panel: BasePanel | None) -> None:
        """Update the panel settings UI based on the focused panel."""
        self.remove_children()

        if not panel:
            self.mount(Static("No panel selected."))
            return

        if not panel.SETTINGS:
            self.mount(Static("No settings available for this panel."))
            return

        self.mount(Static(f"Settings for {type(panel).__name__}:"))
        for setting in panel.SETTINGS:
            self.mount(Label(setting.label))

            # Add topic suggester if this is a topic setting
            topic_suggestions = self.get_topic_suggestions()
            suggester = SuggestFromList(topic_suggestions, case_sensitive=False)
            self.mount(Input(placeholder=setting.description, suggester=suggester))
