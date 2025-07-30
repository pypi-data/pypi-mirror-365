from io import BytesIO
from typing import ClassVar

import PIL.Image
from textual.app import ComposeResult
from textual_image.widget import HalfcellImage

from digitalis.reader.base import ChannelMessage
from digitalis.ui.panels.base import BasePanel


class ImageViewer(BasePanel):
    SUPPORTED_SCHEMAS: ClassVar[set[str]] = {"sensor_msgs/msg/CompressedImage"}

    DEFAULT_CSS = """
    ImageViewer * {
        width: auto;
        height: auto;
    }
    """

    def __init__(self) -> None:
        super().__init__()

    def compose(self) -> ComposeResult:
        yield HalfcellImage()

    def watch_data(self, _data: ChannelMessage | None) -> None:
        img = None
        if self.data and self.data.schema == "sensor_msgs/msg/CompressedImage":
            img = PIL.Image.open(BytesIO(self.data.message.data))

        img_container = self.query_one(HalfcellImage)
        img_container.image = img
