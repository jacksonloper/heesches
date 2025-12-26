"""
SAT-based corona computation for polyiamonds.

This module implements the algorithm from "Heesch Numbers of Unmarked Polyforms"
(arXiv:2105.09438) by Craig S. Kaplan for computing the Heesch number of a
polyiamond using a SAT solver.

The key ideas:
1. A corona is a complete ring of copies of the shape around a configuration
2. We enumerate all possible placements of the shape that touch the boundary
3. We use SAT constraints to ensure:
   - No overlaps between placements
   - Complete coverage of the boundary
4. We iteratively build coronas until no more can be added
"""

from typing import FrozenSet, Set, List, Dict, Tuple, Optional
from dataclasses import dataclass
from pysat.solvers import Solver
from pysat.formula import CNF

from .grid import Cell, TriangularGrid
from .polyiamond import Polyiamond


@dataclass
class Placement:
    """A placement of a polyiamond at a specific position and orientation."""
    cells: FrozenSet[Cell]
    transform_id: int  # Which transformation was applied (0-11)
    dx: int  # Translation in x
    dy: int  # Translation in y

    def __hash__(self):
        return hash(self.cells)

    def __eq__(self, other):
        return isinstance(other, Placement) and self.cells == other.cells


def find_valid_placements(
    polyiamond: Polyiamond,
    occupied: FrozenSet[Cell],
    boundary: Set[Cell]
) -> List[Placement]:
    """
    Find all valid placements of the polyiamond that:
    1. Touch at least one boundary cell
    2. Don't overlap with occupied cells

    Args:
        polyiamond: The polyiamond to place
        occupied: Cells currently occupied by the base + previous coronas
        boundary: Cells adjacent to occupied that need to be covered

    Returns:
        List of valid Placement objects
    """
    placements = []

    # Get all transformations of the polyiamond
    transforms = polyiamond.all_transformations()

    # For each transformation, try all translations that could touch the boundary
    for trans_id, transformed in enumerate(transforms):
        base_cells = transformed.cells

        # For each boundary cell, try placing the polyiamond so it covers that cell
        for boundary_cell in boundary:
            for base_cell in base_cells:
                # Compute translation to align base_cell with boundary_cell
                dx = boundary_cell.x - base_cell.x
                dy = boundary_cell.y - base_cell.y

                # CRITICAL: Only allow translations that preserve triangle orientation
                # If (dx + dy) is odd, triangles flip orientation and connectivity breaks
                # This happens when boundary_cell and base_cell have different parities
                if (dx + dy) % 2 != 0:
                    continue

                # Apply translation to get placed cells
                placed_cells = frozenset(
                    Cell(c.x + dx, c.y + dy) for c in base_cells
                )

                # Check if this placement overlaps with occupied cells
                if not placed_cells.isdisjoint(occupied):
                    continue

                # Create the placement
                placement = Placement(placed_cells, trans_id, dx, dy)

                # Check if we've already seen this placement
                if placement not in placements:
                    placements.append(placement)

    return placements


def build_sat_formula(
    placements: List[Placement],
    boundary: Set[Cell],
    require_complete: bool = True
) -> Tuple[CNF, Dict[int, Placement], Dict[Cell, List[int]]]:
    """
    Build a SAT formula for finding a valid corona.

    Variables:
        - One variable per placement (is this placement used?)

    Constraints:
        - No two placements can overlap (if placements share a cell, at most one is true)
        - If require_complete: every boundary cell must be covered by at least one placement

    Args:
        placements: List of valid placements
        boundary: Set of boundary cells that need to be covered
        require_complete: If True, require all boundary cells to be covered

    Returns:
        (formula, var_to_placement, cell_to_vars) tuple
    """
    formula = CNF()

    # Create variable mapping
    var_to_placement = {}
    placement_to_var = {}
    for i, placement in enumerate(placements):
        var = i + 1  # SAT variables are 1-indexed
        var_to_placement[var] = placement
        placement_to_var[id(placement)] = var

    # Build cell-to-variables mapping (which placements cover each cell)
    cell_to_vars: Dict[Cell, List[int]] = {}
    for placement in placements:
        var = placement_to_var[id(placement)]
        for cell in placement.cells:
            if cell not in cell_to_vars:
                cell_to_vars[cell] = []
            cell_to_vars[cell].append(var)

    # Constraint 1: No overlapping placements
    # For each cell covered by multiple placements, at most one can be true
    for cell, vars_covering in cell_to_vars.items():
        if len(vars_covering) > 1:
            # Add pairwise exclusion clauses: not(v1 and v2) = (not v1 or not v2)
            for i in range(len(vars_covering)):
                for j in range(i + 1, len(vars_covering)):
                    formula.append([-vars_covering[i], -vars_covering[j]])

    # Constraint 2: Every boundary cell must be covered
    if require_complete:
        for cell in boundary:
            if cell in cell_to_vars:
                # At least one of the covering placements must be true
                formula.append(cell_to_vars[cell])
            else:
                # No placement covers this boundary cell - UNSAT
                formula.append([])  # Empty clause = always false

    return formula, var_to_placement, cell_to_vars


def solve_corona(
    polyiamond: Polyiamond,
    occupied: FrozenSet[Cell],
    boundary: Set[Cell],
    solver_name: str = "Glucose3"
) -> Optional[List[Placement]]:
    """
    Try to find a complete corona around the current configuration.

    Args:
        polyiamond: The polyiamond being tiled
        occupied: Currently occupied cells
        boundary: Cells that need to be covered

    Returns:
        List of placements forming the corona, or None if impossible
    """
    # Find all valid placements
    placements = find_valid_placements(polyiamond, occupied, boundary)

    if not placements:
        return None

    # Check if all boundary cells can be covered
    covered_boundary = set()
    for placement in placements:
        covered_boundary.update(placement.cells & boundary)

    if covered_boundary != boundary:
        # Some boundary cells cannot be covered
        return None

    # Build and solve SAT formula
    formula, var_to_placement, cell_to_vars = build_sat_formula(
        placements, boundary, require_complete=True
    )

    # Solve
    solver = Solver(name=solver_name, bootstrap_with=formula)
    if solver.solve():
        model = solver.get_model()
        result = []
        for lit in model:
            if lit > 0 and lit in var_to_placement:
                result.append(var_to_placement[lit])
        solver.delete()
        return result
    else:
        solver.delete()
        return None


def find_coronas(
    polyiamond: Polyiamond,
    max_coronas: int = 10,
    solver_name: str = "Glucose3",
    verbose: bool = False
) -> Tuple[int, List[List[Placement]]]:
    """
    Find all possible coronas around a polyiamond.

    Args:
        polyiamond: The polyiamond to surround
        max_coronas: Maximum number of coronas to search for
        solver_name: SAT solver to use
        verbose: If True, print progress

    Returns:
        (heesch_number, coronas) where coronas is a list of placement lists
    """
    # Start with the base polyiamond
    occupied = polyiamond.cells
    coronas = []

    for corona_num in range(1, max_coronas + 1):
        # Find the boundary of current configuration
        boundary = TriangularGrid.boundary(occupied)

        if verbose:
            print(f"Corona {corona_num}: boundary has {len(boundary)} cells")

        # Try to complete this corona
        corona = solve_corona(polyiamond, occupied, boundary, solver_name)

        if corona is None:
            if verbose:
                print(f"  Could not complete corona {corona_num}")
            break

        if verbose:
            print(f"  Found corona with {len(corona)} placements")

        coronas.append(corona)

        # Update occupied cells
        for placement in corona:
            occupied = occupied | placement.cells

    return len(coronas), coronas


def compute_heesch_number(
    polyiamond: Polyiamond,
    max_coronas: int = 10,
    solver_name: str = "Glucose3",
    verbose: bool = False
) -> int:
    """
    Compute the Heesch number of a polyiamond.

    The Heesch number is the maximum number of complete coronas that can
    surround the polyiamond.

    Args:
        polyiamond: The polyiamond to analyze
        max_coronas: Maximum number of coronas to search for
        solver_name: SAT solver to use
        verbose: If True, print progress

    Returns:
        The Heesch number (0 to max_coronas)
    """
    hc, _ = find_coronas(polyiamond, max_coronas, solver_name, verbose)
    return hc


def analyze_polyiamond(
    polyiamond: Polyiamond,
    max_coronas: int = 10,
    verbose: bool = True
) -> Dict:
    """
    Perform a complete analysis of a polyiamond's Heesch number.

    Returns a dictionary with:
        - heesch_number: The computed Heesch number
        - coronas: List of corona placements
        - tiles_per_corona: Number of tiles in each corona
    """
    hc, coronas = find_coronas(polyiamond, max_coronas, verbose=verbose)

    tiles_per_corona = [len(c) for c in coronas]

    return {
        'heesch_number': hc,
        'coronas': coronas,
        'tiles_per_corona': tiles_per_corona,
    }
