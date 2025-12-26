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
    show: bool = True
) -> plt.Figure:
    """
    Visualize a single polyiamond.

    Args:
        polyiamond: The polyiamond to visualize
        ax: Matplotlib axes to draw on (creates new figure if None)
        color: Fill color for the triangles
        show: If True, display the figure

    Returns:
        The matplotlib Figure object
    """
    if ax is None:
        fig, ax = plt.subplots(1, 1, figsize=(8, 8))
    else:
        fig = ax.figure

    # Create patches for each cell
    for cell in polyiamond.cells:
        patch = create_triangle_patch(cell, color)
        ax.add_patch(patch)

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
    save_path: Optional[str] = None
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

    Returns:
        The matplotlib Figure object
    """
    if ax is None:
        fig, ax = plt.subplots(1, 1, figsize=(12, 12))
    else:
        fig = ax.figure

    # Draw base polyiamond
    for cell in polyiamond.cells:
        patch = create_triangle_patch(cell, COLORS[0])
        ax.add_patch(patch)

    # Draw coronas
    for i, corona in enumerate(coronas):
        color = COLORS[(i + 1) % len(COLORS)]
        for placement in corona:
            for cell in placement.cells:
                patch = create_triangle_patch(cell, color, alpha=0.7)
                ax.add_patch(patch)

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
