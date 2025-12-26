"""
Triangular grid coordinate system for polyiamonds.

In the triangular grid, each cell is an equilateral triangle. We use
axial coordinates (x, y) where:
- The triangle orientation (up/down) is determined by (x + y) % 2
- Up triangles have (x + y) even
- Down triangles have (x + y) odd

Neighbors of a triangle depend on its orientation:
- Up triangle (x, y): neighbors at (x-1, y), (x+1, y), (x, y-1)
- Down triangle (x, y): neighbors at (x-1, y), (x+1, y), (x, y+1)
"""

from dataclasses import dataclass
from typing import List, Tuple, Set, FrozenSet


@dataclass(frozen=True)
class Cell:
    """A cell in the triangular grid."""
    x: int
    y: int

    @property
    def is_up(self) -> bool:
        """Return True if this is an up-pointing triangle."""
        return (self.x + self.y) % 2 == 0

    @property
    def is_down(self) -> bool:
        """Return True if this is a down-pointing triangle."""
        return (self.x + self.y) % 2 == 1

    def neighbors(self) -> List['Cell']:
        """Return the three neighboring cells."""
        if self.is_up:
            # Up triangle (▲): neighbors on left, right, and bottom
            # The horizontal base is shared with the down triangle below
            return [
                Cell(self.x - 1, self.y),  # left (shares left slant edge)
                Cell(self.x + 1, self.y),  # right (shares right slant edge)
                Cell(self.x, self.y - 1),  # bottom (shares horizontal base)
            ]
        else:
            # Down triangle (▼): neighbors on left, right, and top
            # The horizontal top edge is shared with the up triangle above
            return [
                Cell(self.x - 1, self.y),  # left (shares left slant edge)
                Cell(self.x + 1, self.y),  # right (shares right slant edge)
                Cell(self.x, self.y + 1),  # top (shares horizontal top edge)
            ]

    def __repr__(self) -> str:
        orient = "↑" if self.is_up else "↓"
        return f"Cell({self.x}, {self.y}, {orient})"


class TriangularGrid:
    """Operations on the triangular grid."""

    @staticmethod
    def neighbors(cell: Cell) -> List[Cell]:
        """Get all neighbors of a cell."""
        return cell.neighbors()

    @staticmethod
    def boundary(cells: FrozenSet[Cell]) -> Set[Cell]:
        """
        Get the boundary of a set of cells.
        The boundary consists of all cells not in the set that are
        adjacent to at least one cell in the set.
        """
        boundary = set()
        for cell in cells:
            for neighbor in cell.neighbors():
                if neighbor not in cells:
                    boundary.add(neighbor)
        return boundary

    @staticmethod
    def exterior_boundary(cells: FrozenSet[Cell]) -> Set[Cell]:
        """
        Get the exterior boundary - cells adjacent to the configuration
        that are not enclosed by it. For simple polyiamonds, this is
        the same as boundary().
        """
        # For now, we use all boundary cells
        # A more sophisticated version would detect holes
        return TriangularGrid.boundary(cells)

    @staticmethod
    def translate(cells: FrozenSet[Cell], dx: int, dy: int) -> FrozenSet[Cell]:
        """Translate a set of cells by (dx, dy)."""
        return frozenset(Cell(c.x + dx, c.y + dy) for c in cells)

    @staticmethod
    def cell_to_cartesian(cell: Cell) -> Tuple[float, float]:
        """
        Convert cell coordinates to Cartesian coordinates (center of triangle).

        In our coordinate system:
        - x-coord in Cartesian = cell.x * 0.5
        - y-coord depends on whether it's up or down triangle
        """
        import math
        h = math.sqrt(3) / 2  # Height of equilateral triangle with unit base

        cx = cell.x * 0.5
        # The y-coordinate of the center depends on orientation
        if cell.is_up:
            cy = cell.y * h + h / 3
        else:
            cy = cell.y * h + 2 * h / 3
        return (cx, cy)

    @staticmethod
    def cartesian_to_cell(x: float, y: float) -> Cell:
        """
        Convert Cartesian coordinates to the nearest cell.

        This finds which triangle contains (or is nearest to) the given point.
        """
        import math
        h = math.sqrt(3) / 2

        # Better estimation: consider the triangular grid structure
        # The y-coordinate helps estimate the row
        # But we need to account for the offset of cell centers

        # For up triangles: center_y = row * h + h/3
        # For down triangles: center_y = row * h + 2h/3
        # Average center_y for row = row * h + h/2

        row_est = int(math.floor(y / h))

        # The x-coordinate with cell width of 0.5
        col_est = int(round(x * 2))

        # Search a wider neighborhood to find the closest cell
        best_cell = None
        best_dist = float('inf')

        for dr in range(-3, 4):
            for dc in range(-3, 4):
                c = Cell(col_est + dc, row_est + dr)
                cx, cy = TriangularGrid.cell_to_cartesian(c)
                dist = (cx - x) ** 2 + (cy - y) ** 2
                if dist < best_dist:
                    best_dist = dist
                    best_cell = c

        return best_cell

    @staticmethod
    def rotate_60_cw(cell: Cell) -> Cell:
        """
        Rotate a cell 60 degrees clockwise around the Cartesian origin (0, 0).

        The origin (0, 0) is a vertex of the triangular lattice where 6 triangles meet.
        This rotation maps cells to cells exactly (in integer coordinates).
        """
        import math

        cx, cy = TriangularGrid.cell_to_cartesian(cell)

        # 60 degree clockwise rotation around origin
        cos60 = 0.5
        sin60 = math.sqrt(3) / 2
        new_x = cx * cos60 + cy * sin60
        new_y = -cx * sin60 + cy * cos60

        return TriangularGrid.cartesian_to_cell(new_x, new_y)

    @staticmethod
    def rotate_60(cell: Cell) -> Cell:
        """Rotate a cell 60 degrees clockwise around the Cartesian origin."""
        return TriangularGrid.rotate_60_cw(cell)

    @staticmethod
    def rotate_120(cell: Cell) -> Cell:
        """Rotate a cell 120 degrees clockwise around the origin."""
        return TriangularGrid.rotate_60(TriangularGrid.rotate_60(cell))

    @staticmethod
    def rotate_180(cell: Cell) -> Cell:
        """Rotate a cell 180 degrees around the origin."""
        return TriangularGrid.rotate_60(TriangularGrid.rotate_60(TriangularGrid.rotate_60(cell)))

    @staticmethod
    def reflect_x(cell: Cell) -> Cell:
        """Reflect a cell across the x-axis (y -> -y in Cartesian)."""
        import math
        cx, cy = TriangularGrid.cell_to_cartesian(cell)
        return TriangularGrid.cartesian_to_cell(cx, -cy)

    @staticmethod
    def reflect_y(cell: Cell) -> Cell:
        """Reflect a cell across the y-axis (x -> -x in Cartesian)."""
        import math
        cx, cy = TriangularGrid.cell_to_cartesian(cell)
        return TriangularGrid.cartesian_to_cell(-cx, cy)

    @staticmethod
    def canonical_position(cells: FrozenSet[Cell]) -> FrozenSet[Cell]:
        """
        Translate cells to a canonical position while preserving connectivity.

        In the triangular grid, neighbor relationships depend on absolute
        coordinates. To preserve connectivity, we must translate by (dx, dy)
        where dx + dy is EVEN (which preserves all neighbor relationships).

        We translate so that min_x is 0 or 1 (depending on parity needed),
        and min_y is as small as possible while keeping dx + dy even.
        """
        if not cells:
            return cells

        min_x = min(c.x for c in cells)
        min_y = min(c.y for c in cells)

        # We want to translate by (-min_x, -min_y), but need dx + dy even
        # If min_x + min_y is even, we're good
        # If min_x + min_y is odd, adjust min_x by 1
        if (min_x + min_y) % 2 != 0:
            min_x -= 1  # Now dx + dy = (-min_x) + (-min_y) is even

        return TriangularGrid.translate(cells, -min_x, -min_y)
