import math
from datetime import datetime
from io import BytesIO
from typing import Any

from PIL import Image
from rich.highlighter import ReprHighlighter
from rich.text import Text
from rich_pixels import Pixels
from textual.app import ComposeResult, RenderResult
from textual.containers import VerticalScroll
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static, Tree
from textual.widgets.tree import TreeNode

from digitalis.reader.mcap import ChannelMessage
from digitalis.utilities import NANOSECONDS_PER_SECOND


def _quaternion_to_euler(x: float, y: float, z: float, w: float) -> tuple[float, float, float]:
    """Convert quaternion to Euler angles."""

    # Convert quaternion to Euler angles (roll, pitch, yaw)
    t0 = +2.0 * (w * x + y * z)
    t1 = +1.0 - 2.0 * (x * x + y * y)
    roll_x = math.atan2(t0, t1)

    t2 = +2.0 * (w * y - z * x)
    t2 = min(t2, +1.0)
    t2 = max(t2, -1.0)
    pitch_y = math.asin(t2)

    t3 = +2.0 * (w * z + x * y)
    t4 = +1.0 - 2.0 * (y * y + z * z)
    yaw_z = math.atan2(t3, t4)

    return roll_x, pitch_y, yaw_z


class ImageViewer(Widget):
    image: reactive[Image.Image | None] = reactive(None)
    _backimage = Image.new("RGB", (100, 100), (255, 0, 0))

    def __init__(self) -> None:
        super().__init__()

    def render(self) -> RenderResult:
        img = self.image or self._backimage

        # Calculate aspect ratio preserving dimensions
        img_width, img_height = img.size
        widget_width, widget_height = self.size

        # Calculate scale factor to fit image within widget while preserving aspect ratio
        scale_width = widget_width / img_width
        scale_height = widget_height / img_height
        scale = min(scale_width, scale_height)

        # Calculate new dimensions
        new_width = int(img_width * scale)
        new_height = int(img_height * scale)

        return Pixels.from_image(img, resize=(new_width, new_height))


def add_json(node: TreeNode, json_data: object) -> None:
    """Adds JSON data to a node.

    Args:
        node (TreeNode): A Tree node.
        json_data (object): An object decoded from JSON.
    """

    highlighter = ReprHighlighter()

    def add_node(name: str, node: TreeNode, obj: Any) -> None:
        """Adds a node to the tree.

        Args:
            name (str): Name of the node.
            node (TreeNode): Parent node.
            data (object): Data associated with the node.
        """
        if not hasattr(obj, "__slots__"):
            node.allow_expand = False
            if name:
                label = Text.assemble(Text.from_markup(f"[b]{name}[/b]="), highlighter(repr(obj)))
            else:
                label = Text(repr(obj))
            node.set_label(label)
            return

        if obj.__slots__ == ["sec", "nanosec"]:
            # Convert timestamp to ISO format
            timestamp = datetime.fromtimestamp(
                obj.sec + obj.nanosec / NANOSECONDS_PER_SECOND
            ).isoformat()
            stamp_label = Text.from_markup(f"[b]{name}[/b]=[dim]{timestamp}[/dim]")
            node.set_label(stamp_label)
        elif obj.__slots__ == ["x", "y", "z", "w"]:
            # convert quaternion to Euler angles
            roll, pitch, yaw = _quaternion_to_euler(obj.x, obj.y, obj.z, obj.w)
            euler_label = Text.from_markup(
                f"[b]{name}[/b] [dim]r={roll:.2f}, p={pitch:.2f}, y={yaw:.2f}[/dim]"
            )
            node.set_label(euler_label)

        for slot in obj.__slots__:
            data = getattr(obj, slot)
            child = node.add(slot)
            if isinstance(data, (list, tuple)):
                child.set_label(Text(f"{slot}[{len(data)}]"))
                for index, value in enumerate(data):
                    new_node = child.add(f"[{index}]")
                    add_node(str(index), new_node, value)
            else:
                add_node(slot, child, data)

    add_node("JSON", node, json_data)


class DataView(Widget):
    data: reactive[ChannelMessage | str | None] = reactive(None)

    DEFAULT_CLASSES = "raw"
    DEFAULT_CSS = """

    DataView * {
        display: none;
        height: 100%;
    }

    DataView.raw > Static {
        display: block;
    }

    DataView.tree > Tree {
        display: block;
    }

    DataView.image > ImageViewer {
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
        yield Static()
        yield Tree("Root").data_bind(guide_depth=2, show_root=False)

    def watch_data(self, data: ChannelMessage | str | None) -> None:
        """Update the displayed data when the data changes."""
        content = self.query_one(Static)
        img_view = self.query_one(ImageViewer)
        tree = self.query_one(Tree)
        cls = "raw"
        if isinstance(data, ChannelMessage):
            if data.schema == "sensor_msgs/msg/CompressedImage":
                img_view.image = Image.open(BytesIO(data.message.data))
                cls = "image"
            else:
                cls = "tree"
                tree.clear()
                add_json(tree.root, data.message)
                tree.root.expand_all()
        elif isinstance(data, str):
            # Display the string directly
            content.update(data)
        else:
            # No data available
            content.update("No data available")

        self.remove_class("raw")
        self.remove_class("image")
        self.remove_class("tree")
        self.add_class(cls)


class DataPanel(VerticalScroll):
    DEFAULT_CSS = """
        DataPanel {
            border-right: $primary;
        }
    """

    data: reactive[ChannelMessage | str | None] = reactive(None)

    def compose(self) -> ComposeResult:
        """Compose the DataPanel widget."""
        yield DataView(
            "Select a topic to view details",
            id="topic-details",
        )

    def watch_data(self, data: ChannelMessage | str | None) -> None:
        """Update the data view when data changes."""
        data_view = self.query_one("#topic-details", DataView)
        data_view.data = data
