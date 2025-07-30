from collections.abc import Iterable
from dataclasses import dataclass

import numpy as np
from rich.console import Console, ConsoleOptions, RenderResult
from rich.segment import Segment
from rich.style import Style

from digitalis.turbo import interpolate_turbo_color

HalfCellSize = tuple[int, int]  # (width_chars, height_chars)
CenterPoint = tuple[float, float]  # (center_x, center_y)
CH_SPACE = " "
CH_UPPER = "▀"
CH_LOWER = "▄"
CH_FULL = "█"


@dataclass(slots=True, frozen=True)
class RichRender:
    segments: list[Segment]

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        yield from self.segments


@dataclass(slots=True)
class HalfCellPointCloud:
    """
    Rich renderable for a 2D point cloud using half-cell characters.

    Each terminal character encodes two vertical 'pixel rows':
    - ' '  : no occupancy
    - '▀'  : top half occupied
    - '▄'  : bottom half occupied
    - '█'  : both halves occupied

    Parameters
    ----------
    points : np.ndarray
        Array of shape (N, 3) with columns [x, y, z].
    size :
        Target render size in terminal characters (width, height).
    resolution :
        Meters per character cell (e.g., 0.1 = 10cm per cell).
    center_point :
        World coordinates (x, y) at the center of the display.
    background_style :
        Rich style for background (spaces). Default "" (inherit).
    """

    points: np.ndarray
    size: HalfCellSize
    resolution: float
    center_point: CenterPoint
    background_style: Style | str | None = ""

    # Pre-computed grid cache (filled on first render)
    _grid_occ: np.ndarray | None = None  # shape: (2*H, W), dtype=bool
    _grid_z: np.ndarray | None = None  # shape: (2*H, W), dtype=float - max z per cell

    def __post_init__(self) -> None:
        self._validate_inputs()

    # ------------- Public API -------------

    def render(self) -> RichRender:
        # Build occupancy and z-value grids once per renderable creation
        # or whenever size/range/points change
        grid_occ, grid_z = self._bin_points_to_halfcell_grid()

        width_chars, height_chars = self.size
        # Compose segments line by line (top row first).
        # For char row c (0..height-1 bottom->top), the corresponding two grid rows are:
        #   bottom_idx = 2*c
        #   top_idx    = 2*c + 1
        # We print from top to bottom, so iterate c from height-1 down to 0.
        # yield from self._compose_segments_from_grid(grid_occ, grid_z, width_chars, height_chars)
        return RichRender(
            segments=list(
                self._compose_segments_from_grid(grid_occ, grid_z, width_chars, height_chars)
            )
        )

    # ------------- Internals -------------

    def _validate_inputs(self) -> None:
        if not isinstance(self.points, np.ndarray):
            raise TypeError("points must be a numpy.ndarray")
        if self.points.ndim != 2 or self.points.shape[1] != 3:
            raise ValueError("points must have shape (N, 3)")
        if len(self.size) != 2:
            raise ValueError("size must be a tuple (width_chars, height_chars)")
        if len(self.center_point) != 2:
            raise ValueError("center_point must be (center_x, center_y)")

        w, h = self.size
        if not (isinstance(w, int) and isinstance(h, int) and w > 0 and h > 0):
            msg = f"size must contain positive integers ({w=}, {h=})"
            raise ValueError(msg)

        if not np.isfinite(self.resolution):
            raise ValueError("resolution must be a finite float")
        if not (self.resolution > 0):
            raise ValueError("resolution must be positive")

        center_x, center_y = self.center_point
        if not (np.isfinite(center_x) and np.isfinite(center_y)):
            raise ValueError("center_point must be finite floats")

    def _bin_points_to_halfcell_grid(self) -> tuple[np.ndarray, np.ndarray]:
        """Bin points into occupancy and z-value grids of shape (2*H, W)."""
        if self._grid_occ is not None and self._grid_z is not None:
            return self._grid_occ, self._grid_z

        width_chars, height_chars = self.size
        grid_h = height_chars * 2
        grid_w = width_chars

        grid_occ = np.zeros((grid_h, grid_w), dtype=bool)
        grid_z = np.full((grid_h, grid_w), -np.inf, dtype=float)  # Initialize with -inf

        if self.points.size == 0:
            self._grid_occ = grid_occ
            self._grid_z = grid_z
            return grid_occ, grid_z

        # Drop NaNs/Infs quickly
        pts = self.points
        mask = np.isfinite(pts).all(axis=1)
        if not mask.all():
            pts = pts[mask]
            if pts.size == 0:
                self._grid_occ = grid_occ
                self._grid_z = grid_z
                return grid_occ, grid_z

        center_x, center_y = self.center_point
        width_chars, height_chars = self.size

        # Calculate world bounds based on resolution and display size
        # Each character represents resolution meters, and we use half-cell precision
        # so each character row represents 2 * resolution meters in height
        world_width = width_chars * self.resolution
        world_height = height_chars * 2 * self.resolution  # 2x because of half-cell encoding

        min_x = center_x - world_width / 2
        max_x = center_x + world_width / 2
        min_y = center_y - world_height / 2
        max_y = center_y + world_height / 2

        wx = max_x - min_x
        wy = max_y - min_y

        # Normalize to [0,1)
        nx = (pts[:, 0] - min_x) / wx
        ny = (pts[:, 1] - min_y) / wy

        # Filter points to only include those within the display range
        in_rng = (nx >= 0.0) & (nx < 1.0) & (ny >= 0.0) & (ny < 1.0)
        if not in_rng.any():
            self._grid_occ = grid_occ
            self._grid_z = grid_z
            return grid_occ, grid_z

        nx = nx[in_rng]
        ny = ny[in_rng]
        z_vals = pts[:, 2][in_rng]

        # Scale to integer pixel indices
        ix = (nx * grid_w).astype(np.int64)
        it = (ny * grid_h).astype(np.int64)

        # Guard against rounding to boundary (rare if clipped above, but safe)
        ix = np.clip(ix, 0, grid_w - 1)
        it = np.clip(it, 0, grid_h - 1)

        # Accumulate occupancy and max z values
        grid_occ[it, ix] = True

        # Update z grid with maximum z value per cell
        for i in range(len(ix)):
            current_z = grid_z[it[i], ix[i]]
            if z_vals[i] > current_z:
                grid_z[it[i], ix[i]] = z_vals[i]

        self._grid_occ = grid_occ
        self._grid_z = grid_z
        return grid_occ, grid_z

    def _map_z_to_color(self, z_value: float, z_min: float, z_max: float) -> str:
        """Map z value to a turbo colormap hex color string."""
        if not np.isfinite(z_value) or z_value == -np.inf:
            return "white"  # Default for empty cells

        if z_max <= z_min:
            return "white"

        # Normalize z to [0, 1]
        normalized_z = (z_value - z_min) / (z_max - z_min)
        normalized_z = np.clip(normalized_z, 0.0, 1.0)

        # Get RGB from turbo colormap
        r, g, b = interpolate_turbo_color(normalized_z)

        # Convert to hex format for Rich
        return f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"

    def _compose_segments_from_grid(
        self, grid_occ: np.ndarray, grid_z: np.ndarray, width_chars: int, height_chars: int
    ) -> Iterable[Segment]:
        """Turn the 2*H x W boolean grid into segments using half blocks with z-based colors."""
        background_style = (
            Style.parse(self.background_style)
            if isinstance(self.background_style, str)
            else self.background_style
        )

        # Calculate z range for color mapping
        valid_z = grid_z[grid_occ & (grid_z != -np.inf)]
        if len(valid_z) > 0:
            z_min, z_max = np.min(valid_z), np.max(valid_z)
        else:
            z_min = z_max = 0.0

        # Iterate from the top visible char row to bottom (terminal prints downward)
        for c in range(
            height_chars - 1, -1, -1
        ):  # c is char-row index from bottom (0) to top (H-1)
            top_idx = 2 * c + 1
            bot_idx = 2 * c

            top_row_occ = grid_occ[top_idx, :]
            bot_row_occ = grid_occ[bot_idx, :]
            top_row_z = grid_z[top_idx, :]
            bot_row_z = grid_z[bot_idx, :]

            # Compose the characters for this row
            # We deliberately do not compress runs into fewer segments to
            # keep mapping simple and explicit.
            row_chars = []
            row_styles = []
            for x in range(width_chars):
                top = bool(top_row_occ[x])
                bot = bool(bot_row_occ[x])

                if top and bot:
                    ch = CH_FULL
                    # Use the higher z value for color
                    z_val = max(top_row_z[x], bot_row_z[x])
                    color = self._map_z_to_color(z_val, z_min, z_max)
                    st = Style.parse(color)
                elif top and not bot:
                    ch = CH_UPPER
                    color = self._map_z_to_color(top_row_z[x], z_min, z_max)
                    st = Style.parse(color)
                elif bot and not top:
                    ch = CH_LOWER
                    color = self._map_z_to_color(bot_row_z[x], z_min, z_max)
                    st = Style.parse(color)
                else:
                    ch = CH_SPACE
                    st = background_style

                row_chars.append(ch)
                row_styles.append(st)

            # Emit one Segment per column (explicit loop, as requested)
            for ch, st in zip(row_chars, row_styles, strict=False):
                yield Segment(ch, st)

            # Newline after the row
            yield Segment.line()
