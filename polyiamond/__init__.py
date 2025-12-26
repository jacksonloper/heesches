"""
Polyiamond Corona SAT Solver

Implementation of the method from "Heesch Numbers of Unmarked Polyforms"
(arXiv:2105.09438) by Craig S. Kaplan for computing polyiamond coronas
using a SAT solver.
"""

from .grid import TriangularGrid, Cell
from .polyiamond import Polyiamond
from .generator import generate_polyiamonds
from .corona_sat import compute_heesch_number, find_coronas
from .visualize import visualize_coronas

__all__ = [
    'TriangularGrid',
    'Cell',
    'Polyiamond',
    'generate_polyiamonds',
    'compute_heesch_number',
    'find_coronas',
    'visualize_coronas',
]
