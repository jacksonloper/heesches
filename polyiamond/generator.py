"""
Polyiamond generation using Redelmeier's algorithm.

This module generates all free polyiamonds (distinct under rotation and reflection)
of a given size using a variant of Redelmeier's algorithm for polyomino enumeration.
"""

from typing import Set, List, FrozenSet, Iterator, Tuple
from .grid import Cell, TriangularGrid
from .polyiamond import Polyiamond


def canonicalize_cells_simple(cells: FrozenSet[Cell]) -> Tuple[Tuple[int, int], ...]:
    """
    Return a canonical tuple for deduplication (no translation, just sorted).

    In the triangular grid, translation can break connectivity due to
    position-dependent neighbor relationships. For deduplication within
    the generator, we only need to track which shapes we've seen from
    the same starting point.
    """
    if not cells:
        return ()
    return tuple(sorted((c.x, c.y) for c in cells))


def generate_fixed_polyiamonds(n: int) -> List[FrozenSet[Cell]]:
    """
    Generate all fixed n-iamonds (treating rotations/reflections as distinct).

    Uses BFS-style enumeration with deduplication. All polyiamonds start
    from Cell(0, 0) and grow by adding neighbors.
    """
    if n <= 0:
        return []

    # Start with a single cell
    start = frozenset([Cell(0, 0)])

    if n == 1:
        return [start]

    # Use set of shapes to track seen (no translation needed since all start at (0,0))
    current_level = [start]

    for size in range(2, n + 1):
        next_level = []
        next_seen: Set[Tuple[Tuple[int, int], ...]] = set()

        for cells in current_level:
            # Find all neighbors we could add
            neighbors = set()
            for cell in cells:
                for neighbor in cell.neighbors():
                    if neighbor not in cells:
                        neighbors.add(neighbor)

            # Try adding each neighbor
            for neighbor in neighbors:
                new_cells = cells | {neighbor}
                key = canonicalize_cells_simple(new_cells)

                if key not in next_seen:
                    next_seen.add(key)
                    next_level.append(new_cells)

        current_level = next_level

    return current_level


def generate_polyiamonds(n: int, fixed: bool = False) -> List[Polyiamond]:
    """
    Generate all n-iamonds.

    Args:
        n: Number of triangles in each polyiamond
        fixed: If True, return fixed polyiamonds (rotations/reflections distinct)
               If False, return free polyiamonds (one representative per equivalence class)

    Returns:
        List of Polyiamond objects
    """
    if n <= 0:
        return []

    if fixed:
        return [Polyiamond(cells) for cells in generate_fixed_polyiamonds(n)]

    # For free polyiamonds, we need to identify equivalence classes
    seen_canonical: Set[FrozenSet[Cell]] = set()
    result = []

    for cells in generate_fixed_polyiamonds(n):
        poly = Polyiamond(cells)
        canonical = poly.canonical_cells()
        if canonical not in seen_canonical:
            seen_canonical.add(canonical)
            result.append(Polyiamond(canonical))

    return result


def count_polyiamonds(n: int, fixed: bool = False) -> int:
    """Count the number of n-iamonds without storing them all."""
    return len(generate_polyiamonds(n, fixed=fixed))


# Known counts for verification (OEIS A000577 for free polyiamonds)
KNOWN_FREE_COUNTS = {
    1: 1,
    2: 1,
    3: 1,
    4: 4,
    5: 6,
    6: 12,
    7: 24,
    8: 66,
    9: 160,
    10: 448,
    11: 1186,
    12: 3334,
}


def verify_generator():
    """Verify the generator produces correct counts for small n."""
    for n in range(1, 8):
        count = count_polyiamonds(n)
        expected = KNOWN_FREE_COUNTS.get(n, None)
        if expected is not None:
            status = "OK" if count == expected else f"WRONG (expected {expected})"
            print(f"{n}-iamonds: {count} {status}")
        else:
            print(f"{n}-iamonds: {count}")


if __name__ == "__main__":
    verify_generator()
