from io import BytesIO

from PIL import Image
from rich_pixels import Pixels
from textual.app import RenderResult
from textual.reactive import reactive
from textual.widget import Widget

from digitalis.reader.base import ChannelMessage


class ImageViewer(Widget):
    data: reactive[ChannelMessage | None] = reactive(None)
    _backimage = Image.new("RGB", (100, 100), (255, 0, 0))

    def __init__(self) -> None:
        super().__init__()

    def render(self) -> RenderResult:
        img = None
        if self.data and self.data.schema == "sensor_msgs/msg/CompressedImage":
            img = Image.open(BytesIO(self.data.message.data))
        img = img or self._backimage

        # Calculate aspect ratio preserving dimensions
        img_width, img_height = img.size
        widget_width, widget_height = self.size
        widget_height *= 2  # account for HalfcellRender

        # Calculate scale factor to fit image within widget while preserving aspect ratio
        scale_width = widget_width / img_width
        scale_height = widget_height / img_height
        scale = min(scale_width, scale_height)

        # Calculate new dimensions
        new_width = int(img_width * scale)
        new_height = int(img_height * scale)

        return Pixels.from_image(img, resize=(new_width, new_height))
