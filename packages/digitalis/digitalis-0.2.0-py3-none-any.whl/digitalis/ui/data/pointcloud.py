import logging
from typing import ClassVar

import numpy as np
import pointcloud2
from rich.text import Text
from textual import events, work
from textual.app import ComposeResult, RenderResult
from textual.binding import Binding, BindingType
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static

from digitalis.reader.base import ChannelMessage
from digitalis.ui.data.pointcloud_renderer import HalfCellPointCloud, RichRender
from digitalis.utilities import nanoseconds_to_iso


class PointCloud(Widget, can_focus=True):
    data: reactive[ChannelMessage | None] = reactive(None)
    center: reactive[tuple[float, float]] = reactive((0, 0))
    resolution: reactive[float] = reactive(0.1)
    _rendered: reactive[RichRender | None] = reactive(None)

    points3d: None | np.ndarray = None

    # Zoom constraints
    MIN_RESOLUTION = 0.001
    MAX_RESOLUTION = 10.0
    ZOOM_FACTOR = 1.1

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("+", "zoom_in", "Zoom In"),
        Binding("-", "zoom_out", "Zoom Out"),
        Binding("r", "reset_view", "Reset View"),
    ]

    def compose(self) -> ComposeResult:
        yield Static(id="top")

    def watch_data(self, data: ChannelMessage | None) -> None:
        """Update the point cloud data."""
        if not data or data.schema != "sensor_msgs/msg/PointCloud2":
            return
        cls = pointcloud2.read_points(data.message)
        names = cls.dtype.names
        if names is None or "x" not in names or "y" not in names or "z" not in names:
            logging.error("Invalid point cloud data: missing x, y, or z coordinates")
            self.data = None
            return

        self.points3d = np.column_stack((cls["x"], cls["y"], cls["z"]))
        self._trigger_background_render()

    @work(exclusive=True)
    async def _process_pointcloud_render(self) -> None:
        """Background worker to process point cloud rendering."""
        if self.points3d is None:
            return

        size = self.size
        if size.width <= 0 or size.height <= 0:
            # If not mounted, skip rendering
            return

        render_result = HalfCellPointCloud(
            points=self.points3d,
            size=(size.width, size.height),
            resolution=self.resolution,
            center_point=self.center,
            background_style="",
        )

        # Update UI from background thread
        self._rendered = render_result.render()

        top = self.query_one("#top", Static)
        ts = nanoseconds_to_iso(self.data.timestamp_ns) if self.data else ""

        range_x = self.size.width * self.resolution
        range_y = (self.size.height * 2) * self.resolution  # 2 due to half-cell rendering
        bounds_x = (self.center[0] - range_x / 2, self.center[0] + range_x / 2)
        bounds_y = (self.center[1] - range_y / 2, self.center[1] + range_y / 2)

        bounds_str = (
            f"X: {bounds_x[0]:.2f} to {bounds_x[1]:.2f} | Y: {bounds_y[0]:.2f} to {bounds_y[1]:.2f}"
        )
        center_str = f"Center: {self.center[0]:.2f}, {self.center[1]:.2f}"
        top.update(f"{ts} | {self.resolution:.2f} m/cell | {center_str} | {bounds_str}")

    def _trigger_background_render(self) -> None:
        """Trigger background rendering."""
        if self.points3d is not None:
            self._process_pointcloud_render()

    def watch_center(self, _center: tuple[float, float]) -> None:
        """Re-render when center changes."""
        self._trigger_background_render()

    def watch_resolution(self, _resolution: float) -> None:
        """Re-render when resolution changes."""
        self._trigger_background_render()

    def on_resize(self, _event: events.Resize) -> None:
        """Re-render when widget size changes."""
        self._trigger_background_render()

    def render(self) -> RenderResult:
        """Render the point cloud widget."""
        if self.data is None or self.points3d is None:
            return Text("No point cloud data available")

        if self._rendered is None:
            return Text("Processing point cloud...")

        return self._rendered

    def on_mouse_move(self, event: events.MouseMove) -> None:
        # Only mouse downs
        if event.button != 1:
            return
        self.center = (
            self.center[0] - event.delta_x * self.resolution,
            self.center[1] + event.delta_y * self.resolution,
        )

    def action_zoom(self, zoom_in: bool, mouse_pos: tuple[int, int] | None = None) -> None:
        """Natural zoom with exponential scaling and optional zoom-to-cursor."""
        old_resolution = self.resolution

        if zoom_in:
            new_resolution = self.resolution / self.ZOOM_FACTOR
        else:
            new_resolution = self.resolution * self.ZOOM_FACTOR

        # Apply constraints
        new_resolution = max(self.MIN_RESOLUTION, min(self.MAX_RESOLUTION, new_resolution))

        if mouse_pos and new_resolution != old_resolution:
            # Zoom towards cursor position
            widget_center = (self.size.width / 2, self.size.height / 2)

            # Convert mouse position to world coordinates
            world_x = self.center[0] + (mouse_pos[0] - widget_center[0]) * old_resolution
            world_y = self.center[1] - (mouse_pos[1] - widget_center[1]) * old_resolution

            # Calculate new center to keep the point under cursor stable
            new_center_x = world_x - (mouse_pos[0] - widget_center[0]) * new_resolution
            new_center_y = world_y + (mouse_pos[1] - widget_center[1]) * new_resolution

            self.center = (new_center_x, new_center_y)

        self.resolution = new_resolution

    def action_zoom_in(self) -> None:
        """Zoom in from center (keyboard shortcut)."""
        self.action_zoom(zoom_in=True)

    def action_zoom_out(self) -> None:
        """Zoom out from center (keyboard shortcut)."""
        self.action_zoom(zoom_in=False)

    def on_mouse_scroll_down(self, event: events.MouseScrollDown) -> None:
        """Zoom out with cursor-based zooming."""
        mouse_pos = (event.x, event.y)
        self.action_zoom(zoom_in=False, mouse_pos=mouse_pos)

    def on_mouse_scroll_up(self, event: events.MouseScrollUp) -> None:
        """Zoom in with cursor-based zooming."""
        mouse_pos = (event.x, event.y)
        self.action_zoom(zoom_in=True, mouse_pos=mouse_pos)

    def action_reset_view(self) -> None:
        """Reset the view to default center and resolution."""
        self.center = (0, 0)
        self.resolution = 0.1
