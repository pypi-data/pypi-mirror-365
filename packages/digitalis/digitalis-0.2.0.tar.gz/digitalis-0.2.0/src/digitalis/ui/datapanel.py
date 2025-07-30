from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static

from digitalis.reader.base import ChannelMessage
from digitalis.ui.data.diagnostics import DiagnosticTree
from digitalis.ui.data.image import ImageViewer
from digitalis.ui.data.pointcloud import PointCloud
from digitalis.ui.data.tree import LazyTree


class DataView(Widget, can_focus=True):
    data: reactive[ChannelMessage | str | None] = reactive(None)

    DEFAULT_CLASSES = "raw"
    DEFAULT_CSS = """

    DataView > * {
        display: none;
    }

    DataView.raw > Static {
        display: block;
    }

    DataView.tree > LazyTree {
        display: block;
    }

    DataView.image > ImageViewer {
        display: block;
    }

    DataView.pointcloud > PointCloud {
        display: block;
    }

    DataView.diagnostic > DiagnosticTree {
        display: block;
    }

"""

    def __init__(
        self,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)

    def compose(self) -> ComposeResult:
        """Compose the DataView widget."""
        yield ImageViewer()
        yield Static("No data received", id="raw")
        yield LazyTree()
        yield PointCloud()
        yield DiagnosticTree()

    def watch_data(self, data: ChannelMessage | str | None) -> None:
        """Update the displayed data when the data changes."""
        content = self.query_one("#raw", Static)
        img_view = self.query_one(ImageViewer)
        tree = self.query_one(LazyTree)
        pointcloud = self.query_one(PointCloud)
        diagnostic = self.query_one(DiagnosticTree)

        cls = "raw"
        if isinstance(data, ChannelMessage):
            if data.schema == "sensor_msgs/msg/CompressedImage":
                cls = "image"
                img_view.data = data
            elif data.schema == "sensor_msgs/msg/PointCloud2":
                cls = "pointcloud"
                pointcloud.data = data
            elif data.schema == "diagnostic_msgs/msg/DiagnosticArray":
                cls = "diagnostic"
                diagnostic.update_diag(data)
            else:
                cls = "tree"
                tree.data = data
        elif isinstance(data, str):
            # Display the string directly
            content.update(data)
        else:
            # No data available
            content.update("No data available")

        self.remove_class("raw")
        self.remove_class("image")
        self.remove_class("tree")
        self.remove_class("pointcloud")
        self.remove_class("diagnostic")
        self.add_class(cls)
