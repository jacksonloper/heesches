"""
Polyiamond representation and transformations.

A polyiamond is a plane geometric figure constructed by joining n equilateral
triangles edge-to-edge. We represent polyiamonds as frozen sets of Cells.
"""

from typing import FrozenSet, Set, List, Tuple, Optional
from .grid import Cell, TriangularGrid


class Polyiamond:
    """
    A polyiamond represented as a set of cells in the triangular grid.

    The polyiamond is stored in canonical form (translated so min x and y are 0).
    """

    def __init__(self, cells: FrozenSet[Cell]):
        """Create a polyiamond from a set of cells."""
        self._cells = TriangularGrid.canonical_position(cells)
        self._hash: Optional[int] = None

    @property
    def cells(self) -> FrozenSet[Cell]:
        """Return the cells of this polyiamond."""
        return self._cells

    @property
    def size(self) -> int:
        """Return the number of cells (triangles) in this polyiamond."""
        return len(self._cells)

    def is_connected(self) -> bool:
        """Check if the polyiamond is connected."""
        if not self._cells:
            return True
        if len(self._cells) == 1:
            return True

        visited = set()
        to_visit = [next(iter(self._cells))]

        while to_visit:
            cell = to_visit.pop()
            if cell in visited:
                continue
            visited.add(cell)
            for neighbor in cell.neighbors():
                if neighbor in self._cells and neighbor not in visited:
                    to_visit.append(neighbor)

        return len(visited) == len(self._cells)

    def boundary(self) -> Set[Cell]:
        """Return the boundary cells (cells adjacent to this polyiamond)."""
        return TriangularGrid.boundary(self._cells)

    def translate(self, dx: int, dy: int) -> 'Polyiamond':
        """Return a translated copy of this polyiamond."""
        new_cells = TriangularGrid.translate(self._cells, dx, dy)
        # Don't re-canonicalize, keep the actual position
        result = Polyiamond.__new__(Polyiamond)
        result._cells = new_cells
        result._hash = None
        return result

    def _get_vertex(self, cell: Cell, vertex_index: int) -> tuple:
        """
        Get the Cartesian coordinates of a vertex of a cell.

        vertex_index: 0, 1, or 2
        For up triangle: 0=bottom-left, 1=bottom-right, 2=top
        For down triangle: 0=top-left, 1=top-right, 2=bottom
        """
        import math
        h = math.sqrt(3) / 2
        x, y = cell.x, cell.y

        if cell.is_up:
            if vertex_index == 0:  # bottom-left
                return (x * 0.5 - 0.5, y * h)
            elif vertex_index == 1:  # bottom-right
                return (x * 0.5 + 0.5, y * h)
            else:  # top
                return (x * 0.5, (y + 1) * h)
        else:
            if vertex_index == 0:  # top-left
                return (x * 0.5 - 0.5, (y + 1) * h)
            elif vertex_index == 1:  # top-right
                return (x * 0.5 + 0.5, (y + 1) * h)
            else:  # bottom
                return (x * 0.5, y * h)

    def _apply_transform_around_vertex(self, transform_func, vertex: tuple) -> 'Polyiamond':
        """
        Apply a transformation centered on a specific vertex (Cartesian coordinates).

        The transformation rotates/reflects the entire polyiamond as a rigid body.
        """
        vx, vy = vertex

        new_cells = set()
        for cell in self._cells:
            cx, cy = TriangularGrid.cell_to_cartesian(cell)
            # Translate to vertex
            dx = cx - vx
            dy = cy - vy
            # Apply transformation
            new_dx, new_dy = transform_func(dx, dy)
            # Translate back
            new_x = new_dx + vx
            new_y = new_dy + vy
            new_cell = TriangularGrid.cartesian_to_cell(new_x, new_y)
            new_cells.add(new_cell)

        return Polyiamond(frozenset(new_cells))

    def rotate_60(self) -> 'Polyiamond':
        """Return the polyiamond rotated 60 degrees clockwise."""
        import math
        cos60 = 0.5
        sin60 = math.sqrt(3) / 2

        def transform(dx, dy):
            return (dx * cos60 + dy * sin60, -dx * sin60 + dy * cos60)

        # Use the bottom-right vertex of the first cell as rotation center
        # (this is a vertex of the triangular lattice where 6 triangles meet)
        first_cell = min(self._cells, key=lambda c: (c.x, c.y))
        vertex = self._get_vertex(first_cell, 1)  # bottom-right for up, top-right for down
        return self._apply_transform_around_vertex(transform, vertex)

    def rotate_120(self) -> 'Polyiamond':
        """Return the polyiamond rotated 120 degrees clockwise."""
        return self.rotate_60().rotate_60()

    def rotate_180(self) -> 'Polyiamond':
        """Return the polyiamond rotated 180 degrees."""
        return self.rotate_60().rotate_60().rotate_60()

    def reflect_x(self) -> 'Polyiamond':
        """Return the polyiamond reflected across a horizontal axis through a vertex."""
        def transform(dx, dy):
            return (dx, -dy)

        first_cell = min(self._cells, key=lambda c: (c.x, c.y))
        vertex = self._get_vertex(first_cell, 1)
        return self._apply_transform_around_vertex(transform, vertex)

    def reflect_y(self) -> 'Polyiamond':
        """Return the polyiamond reflected across a vertical axis through a vertex."""
        def transform(dx, dy):
            return (-dx, dy)

        first_cell = min(self._cells, key=lambda c: (c.x, c.y))
        vertex = self._get_vertex(first_cell, 1)
        return self._apply_transform_around_vertex(transform, vertex)

    def all_rotations(self) -> List['Polyiamond']:
        """Return all 6 rotations (0, 60, 120, 180, 240, 300 degrees)."""
        rotations = [self]
        current = self
        for _ in range(5):
            current = current.rotate_60()
            rotations.append(current)
        return rotations

    def all_transformations(self) -> List['Polyiamond']:
        """Return all 12 transformations (6 rotations x 2 reflections)."""
        transforms = []
        for rot in self.all_rotations():
            transforms.append(rot)
            transforms.append(rot.reflect_x())
        return transforms

    def canonical_form(self) -> 'Polyiamond':
        """
        Return the canonical form of this polyiamond.

        The canonical form is the lexicographically smallest among all
        transformations, making it suitable for comparing polyiamonds
        for equivalence.
        """
        def cells_key(p: 'Polyiamond') -> Tuple:
            sorted_cells = sorted((c.x, c.y) for c in p._cells)
            return tuple(sorted_cells)

        all_forms = self.all_transformations()
        return min(all_forms, key=cells_key)

    def canonical_cells(self) -> FrozenSet[Cell]:
        """Return the cells of the canonical form."""
        return self.canonical_form()._cells

    def __eq__(self, other) -> bool:
        if not isinstance(other, Polyiamond):
            return False
        return self._cells == other._cells

    def __hash__(self) -> int:
        if self._hash is None:
            self._hash = hash(self._cells)
        return self._hash

    def __repr__(self) -> str:
        return f"Polyiamond({len(self._cells)}-iamond)"

    def __str__(self) -> str:
        if not self._cells:
            return "Empty polyiamond"

        min_x = min(c.x for c in self._cells)
        max_x = max(c.x for c in self._cells)
        min_y = min(c.y for c in self._cells)
        max_y = max(c.y for c in self._cells)

        lines = []
        for y in range(max_y, min_y - 1, -1):
            line = ""
            for x in range(min_x, max_x + 1):
                cell = Cell(x, y)
                if cell in self._cells:
                    line += "▲" if cell.is_up else "▼"
                else:
                    line += " "
            lines.append(line)
        return "\n".join(lines)

    def to_tuple(self) -> Tuple[Tuple[int, int], ...]:
        """Convert to a tuple representation for serialization."""
        return tuple(sorted((c.x, c.y) for c in self._cells))

    @classmethod
    def from_tuple(cls, data: Tuple[Tuple[int, int], ...]) -> 'Polyiamond':
        """Create a polyiamond from a tuple representation."""
        cells = frozenset(Cell(x, y) for x, y in data)
        return cls(cells)


def are_equivalent(p1: Polyiamond, p2: Polyiamond) -> bool:
    """Check if two polyiamonds are equivalent under rotation/reflection."""
    return p1.canonical_cells() == p2.canonical_cells()
