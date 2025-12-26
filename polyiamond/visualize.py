"""
Visualization of polyiamonds and their coronas.

Uses matplotlib to render polyiamonds on the triangular grid.
"""

import math
from typing import FrozenSet, List, Optional, Tuple
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.collections import PatchCollection
import numpy as np

from .grid import Cell
from .polyiamond import Polyiamond
from .corona_sat import Placement


# Colors for visualization
COLORS = [
    '#FF6B6B',  # Red - base polyiamond
    '#4ECDC4',  # Teal - corona 1
    '#45B7D1',  # Blue - corona 2
    '#96CEB4',  # Green - corona 3
    '#FFEAA7',  # Yellow - corona 4
    '#DDA0DD',  # Plum - corona 5
    '#98D8C8',  # Mint - corona 6
    '#F7DC6F',  # Gold - corona 7
]


def get_triangle_height() -> float:
    """Return the height of an equilateral triangle with unit side."""
    return math.sqrt(3) / 2


def draw_grid(ax: plt.Axes, min_x: int, max_x: int, min_y: int, max_y: int,
              padding: int = 2, color: str = '#CCCCCC', linewidth: float = 0.3) -> None:
    """
    Draw the underlying triangular grid in the background.

    Args:
        ax: Matplotlib axes to draw on
        min_x, max_x, min_y, max_y: Bounding box of cells (in cell coordinates)
        padding: Extra cells to draw beyond the bounds
        color: Color for grid lines
        linewidth: Width of grid lines
    """
    h = get_triangle_height()

    # Extend bounds by padding
    x_start = min_x - padding
    x_end = max_x + padding
    y_start = min_y - padding
    y_end = max_y + padding

    # Draw all triangles in the extended area
    for y in range(y_start, y_end + 1):
        for x in range(x_start, x_end + 1):
            cell = Cell(x, y)
            vertices = cell_to_vertices(cell)
            # Close the triangle by repeating first vertex
            xs = list(vertices[:, 0]) + [vertices[0, 0]]
            ys = list(vertices[:, 1]) + [vertices[0, 1]]
            ax.plot(xs, ys, color=color, linewidth=linewidth, zorder=0)


def get_cell_edges(cell: Cell) -> List[Tuple[Tuple[float, float], Tuple[float, float]]]:
    """
    Get the three edges of a cell as pairs of vertices.

    Returns:
        List of 3 edges, each edge is ((x1, y1), (x2, y2))
    """
    vertices = cell_to_vertices(cell)
    edges = []
    for i in range(3):
        p1 = (vertices[i, 0], vertices[i, 1])
        p2 = (vertices[(i + 1) % 3, 0], vertices[(i + 1) % 3, 1])
        # Normalize edge so (smaller, larger) for consistent comparison
        if p1 > p2:
            p1, p2 = p2, p1
        edges.append((p1, p2))
    return edges


def compute_boundary_edges(cells: FrozenSet[Cell]) -> List[Tuple[Tuple[float, float], Tuple[float, float]]]:
    """
    Compute the boundary edges of a set of cells.

    An edge is a boundary edge if it belongs to exactly one cell in the set.

    Args:
        cells: Set of cells forming a polyiamond

    Returns:
        List of boundary edges as ((x1, y1), (x2, y2)) tuples
    """
    edge_count = {}
    for cell in cells:
        for edge in get_cell_edges(cell):
            edge_count[edge] = edge_count.get(edge, 0) + 1

    # Boundary edges appear exactly once
    return [edge for edge, count in edge_count.items() if count == 1]


def draw_tile_boundary(ax: plt.Axes, cells: FrozenSet[Cell],
                       color: str = 'black', linewidth: float = 2.0) -> None:
    """
    Draw the boundary edges of a tile (polyiamond).

    Args:
        ax: Matplotlib axes to draw on
        cells: Set of cells forming the tile
        color: Color for boundary lines
        linewidth: Width of boundary lines
    """
    boundary_edges = compute_boundary_edges(cells)
    for (x1, y1), (x2, y2) in boundary_edges:
        ax.plot([x1, x2], [y1, y2], color=color, linewidth=linewidth, zorder=10)


def cell_to_vertices(cell: Cell) -> np.ndarray:
    """
    Convert a cell to its triangle vertices in 2D coordinates.

    The triangular grid is laid out so that:
    - Up triangles point upward
    - Down triangles point downward
    - Unit height is 1

    Returns:
        3x2 numpy array of vertex coordinates
    """
    # Height of equilateral triangle with unit side
    h = math.sqrt(3) / 2

    # Base x position (cells are offset by 0.5 in alternating rows)
    x = cell.x * 0.5
    y = cell.y * h

    if cell.is_up:
        # Up-pointing triangle
        return np.array([
            [x - 0.5, y],
            [x + 0.5, y],
            [x, y + h],
        ])
    else:
        # Down-pointing triangle
        return np.array([
            [x - 0.5, y + h],
            [x + 0.5, y + h],
            [x, y],
        ])


def create_triangle_patch(cell: Cell, color: str, alpha: float = 0.8) -> patches.Polygon:
    """Create a matplotlib patch for a cell."""
    vertices = cell_to_vertices(cell)
    return patches.Polygon(vertices, facecolor=color, edgecolor='black',
                          linewidth=0.5, alpha=alpha)


def visualize_polyiamond(
    polyiamond: Polyiamond,
    ax: Optional[plt.Axes] = None,
    color: str = '#FF6B6B',
    show: bool = True,
    show_grid: bool = True,
    show_tile_boundaries: bool = True
) -> plt.Figure:
    """
    Visualize a single polyiamond.

    Args:
        polyiamond: The polyiamond to visualize
        ax: Matplotlib axes to draw on (creates new figure if None)
        color: Fill color for the triangles
        show: If True, display the figure
        show_grid: If True, draw the underlying triangular grid
        show_tile_boundaries: If True, draw tile boundaries with thick lines

    Returns:
        The matplotlib Figure object
    """
    if ax is None:
        fig, ax = plt.subplots(1, 1, figsize=(8, 8))
    else:
        fig = ax.figure

    # Compute bounding box and draw grid
    if polyiamond.cells:
        min_x = min(c.x for c in polyiamond.cells)
        max_x = max(c.x for c in polyiamond.cells)
        min_y = min(c.y for c in polyiamond.cells)
        max_y = max(c.y for c in polyiamond.cells)

        if show_grid:
            draw_grid(ax, min_x, max_x, min_y, max_y, padding=2)

    # Create patches for each cell
    for cell in polyiamond.cells:
        patch = create_triangle_patch(cell, color)
        ax.add_patch(patch)

    # Draw tile boundary
    if show_tile_boundaries and polyiamond.cells:
        draw_tile_boundary(ax, polyiamond.cells, color='black', linewidth=2.0)

    # Set axis properties
    ax.set_aspect('equal')
    ax.autoscale()
    ax.margins(0.1)

    # Remove axis ticks for cleaner look
    ax.set_xticks([])
    ax.set_yticks([])

    if show:
        plt.show()

    return fig


def visualize_coronas(
    polyiamond: Polyiamond,
    coronas: List[List[Placement]],
    ax: Optional[plt.Axes] = None,
    show: bool = True,
    title: Optional[str] = None,
    save_path: Optional[str] = None,
    show_grid: bool = True,
    show_tile_boundaries: bool = True
) -> plt.Figure:
    """
    Visualize a polyiamond with its coronas.

    Args:
        polyiamond: The base polyiamond
        coronas: List of corona placements (from find_coronas)
        ax: Matplotlib axes to draw on
        show: If True, display the figure
        title: Optional title for the figure
        save_path: If provided, save the figure to this path
        show_grid: If True, draw the underlying triangular grid
        show_tile_boundaries: If True, draw tile boundaries with thick lines

    Returns:
        The matplotlib Figure object
    """
    if ax is None:
        fig, ax = plt.subplots(1, 1, figsize=(12, 12))
    else:
        fig = ax.figure

    # Collect all cells to compute bounding box
    all_cells = set(polyiamond.cells)
    for corona in coronas:
        for placement in corona:
            all_cells.update(placement.cells)

    # Compute bounding box
    if all_cells:
        min_x = min(c.x for c in all_cells)
        max_x = max(c.x for c in all_cells)
        min_y = min(c.y for c in all_cells)
        max_y = max(c.y for c in all_cells)

        # Draw the underlying grid
        if show_grid:
            draw_grid(ax, min_x, max_x, min_y, max_y, padding=2)

    # Draw base polyiamond fill
    for cell in polyiamond.cells:
        patch = create_triangle_patch(cell, COLORS[0])
        ax.add_patch(patch)

    # Draw corona fills
    for i, corona in enumerate(coronas):
        color = COLORS[(i + 1) % len(COLORS)]
        for placement in corona:
            for cell in placement.cells:
                patch = create_triangle_patch(cell, color, alpha=0.7)
                ax.add_patch(patch)

    # Draw tile boundaries
    if show_tile_boundaries:
        # Draw base polyiamond boundary
        draw_tile_boundary(ax, polyiamond.cells, color='black', linewidth=2.0)

        # Draw corona tile boundaries
        for corona in coronas:
            for placement in corona:
                draw_tile_boundary(ax, placement.cells, color='black', linewidth=2.0)

    # Set axis properties
    ax.set_aspect('equal')
    ax.autoscale()
    ax.margins(0.1)
    ax.set_xticks([])
    ax.set_yticks([])

    if title:
        ax.set_title(title, fontsize=14)

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches='tight')

    if show:
        plt.show()

    return fig


def visualize_heesch_result(
    polyiamond: Polyiamond,
    heesch_number: int,
    coronas: List[List[Placement]],
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Create a complete visualization of a Heesch number computation result.

    Args:
        polyiamond: The base polyiamond
        heesch_number: The computed Heesch number
        coronas: The corona placements
        save_path: Optional path to save the figure

    Returns:
        The matplotlib Figure object
    """
    fig, ax = plt.subplots(1, 1, figsize=(12, 12))

    title = f"{polyiamond.size}-iamond with Heesch number {heesch_number}"

    visualize_coronas(polyiamond, coronas, ax=ax, show=False, title=title)

    # Add legend
    legend_patches = [
        patches.Patch(color=COLORS[0], label='Base polyiamond'),
    ]
    for i in range(len(coronas)):
        legend_patches.append(
            patches.Patch(color=COLORS[(i + 1) % len(COLORS)],
                         label=f'Corona {i + 1}')
        )
    ax.legend(handles=legend_patches, loc='upper right')

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches='tight')

    plt.show()
    return fig


def polyiamond_to_ascii(polyiamond: Polyiamond) -> str:
    """Convert a polyiamond to ASCII art representation."""
    if not polyiamond.cells:
        return "(empty)"

    cells = polyiamond.cells
    min_x = min(c.x for c in cells)
    max_x = max(c.x for c in cells)
    min_y = min(c.y for c in cells)
    max_y = max(c.y for c in cells)

    lines = []
    for y in range(max_y, min_y - 1, -1):
        line = ""
        for x in range(min_x, max_x + 1):
            cell = Cell(x, y)
            if cell in cells:
                line += "△" if cell.is_up else "▽"
            else:
                line += " "
        lines.append(line.rstrip())

    return "\n".join(lines)
