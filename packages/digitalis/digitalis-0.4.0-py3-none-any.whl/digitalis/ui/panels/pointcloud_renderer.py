from collections.abc import Iterable

import numpy as np
from rich.segment import Segment
from rich.style import Style

from digitalis.turbo import interpolate_turbo_color

HalfCellSize = tuple[int, int]  # (width_chars, height_chars)
CenterPoint = tuple[float, float]  # (center_x, center_y)
CH_SPACE = " "
CH_UPPER = "▀"
CH_LOWER = "▄"
CH_FULL = "█"


def _validate_inputs(
    points: np.ndarray, size: HalfCellSize, resolution: float, center_point: CenterPoint
) -> None:
    """Validate input parameters."""
    if not isinstance(points, np.ndarray) or points.shape[-1:] != (3,):
        raise ValueError("points must be a numpy array with shape (..., 3)")

    w, h = size
    if not (isinstance(w, int) and isinstance(h, int) and w > 0 and h > 0):
        raise ValueError(f"size must contain positive integers, got ({w}, {h})")

    if not (np.isfinite([resolution, *center_point]).all() and resolution > 0):
        raise ValueError("resolution and center_point must be finite with resolution > 0")


def _create_grids(
    points: np.ndarray, size: HalfCellSize, resolution: float, center_point: CenterPoint
) -> tuple[np.ndarray, np.ndarray]:
    """Create occupancy and z-value grids from points using histogram2d."""
    width_chars, height_chars = size
    grid_h, grid_w = height_chars * 2, width_chars
    empty_grids = (np.zeros((grid_h, grid_w), dtype=bool), np.full((grid_h, grid_w), -np.inf))

    if points.size == 0 or not np.isfinite(points).all(axis=1).any():
        return empty_grids

    # Filter finite points
    mask = np.isfinite(points).all(axis=1)
    pts = points[mask] if not mask.all() else points

    # Calculate world bounds
    center = np.array(center_point)
    world_size = np.array([width_chars * resolution, height_chars * 2 * resolution])
    bounds = np.column_stack([center - world_size / 2, center + world_size / 2])
    hist_range = [[bounds[0, 0], bounds[0, 1]], [bounds[1, 0], bounds[1, 1]]]

    # Get occupancy and use np.maximum.at for z-values (more efficient than two histograms)
    count_hist, _, _ = np.histogram2d(pts[:, 0], pts[:, 1], bins=[grid_w, grid_h], range=hist_range)

    # Create z-grid using maximum.at approach
    grid_z = np.full((grid_h, grid_w), -np.inf)
    ix = np.clip(
        np.digitize(pts[:, 0], np.linspace(bounds[0, 0], bounds[0, 1], grid_w + 1)) - 1,
        0,
        grid_w - 1,
    )
    it = np.clip(
        np.digitize(pts[:, 1], np.linspace(bounds[1, 0], bounds[1, 1], grid_h + 1)) - 1,
        0,
        grid_h - 1,
    )
    np.maximum.at(grid_z, (it, ix), pts[:, 2])

    return count_hist.T > 0, grid_z


def _get_z_color_range(grid_occ: np.ndarray, grid_z: np.ndarray) -> tuple[float, float]:
    """Calculate z range for color mapping."""
    masked_z = np.where(grid_occ, grid_z, np.nan)
    return (np.nanmin(masked_z), np.nanmax(masked_z)) if grid_occ.any() else (0.0, 0.0)


def _map_z_to_color(z_value: float, z_min: float, z_max: float) -> str:
    """Map z value to a turbo colormap hex color string."""
    if not np.isfinite(z_value) or z_value == -np.inf or z_max <= z_min:
        return "white"

    normalized_z = np.clip((z_value - z_min) / (z_max - z_min), 0.0, 1.0)
    r, g, b = interpolate_turbo_color(normalized_z)
    return f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"


def _compose_segments_from_grid(
    grid_occ: np.ndarray,
    grid_z: np.ndarray,
    width_chars: int,
    height_chars: int,
    background_style: Style | str | None,
) -> Iterable[Segment]:
    """Convert grid to Rich segments using half-block characters."""
    bg_style = (
        Style.parse(background_style) if isinstance(background_style, str) else background_style
    )
    z_min, z_max = _get_z_color_range(grid_occ, grid_z)

    # Pre-compute color styles for z-values to avoid repeated Style.parse() calls
    color_cache = {}

    def get_color_style(z_val: float) -> Style:
        color = _map_z_to_color(z_val, z_min, z_max)
        if color not in color_cache:
            color_cache[color] = Style.parse(color)
        return color_cache[color]

    # Character lookup: [top_occ, bot_occ] -> character
    chars = [CH_SPACE, CH_LOWER, CH_UPPER, CH_FULL]

    for c in range(height_chars - 1, -1, -1):
        top_idx, bot_idx = 2 * c + 1, 2 * c

        for x in range(width_chars):
            top_occ, bot_occ = grid_occ[top_idx, x], grid_occ[bot_idx, x]

            # Use bit manipulation for faster lookup: top=2, bot=1
            char_idx = int(top_occ) * 2 + int(bot_occ)
            ch = chars[char_idx]

            if char_idx == 0:  # No occupancy
                style = bg_style
            else:
                top_z, bot_z = grid_z[top_idx, x], grid_z[bot_idx, x]
                z_val = top_z if char_idx == 2 else (bot_z if char_idx == 1 else max(top_z, bot_z))
                style = get_color_style(z_val)

            yield Segment(ch, style)

        yield Segment.line()


def render_pointcloud(
    points: np.ndarray,
    size: HalfCellSize,
    resolution: float,
    center_point: CenterPoint,
    background_style: Style | str | None = "",
) -> list[Segment]:
    """
    Render a 2D point cloud using half-cell characters.

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

    Returns
    -------
        Rich segments for rendering the point cloud.
    """
    _validate_inputs(points, size, resolution, center_point)
    grid_occ, grid_z = _create_grids(points, size, resolution, center_point)
    width_chars, height_chars = size
    return list(
        _compose_segments_from_grid(grid_occ, grid_z, width_chars, height_chars, background_style)
    )
