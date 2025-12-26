# Polyiamond Corona SAT Solver

Implementation of the method from ["Heesch Numbers of Unmarked Polyforms"](https://arxiv.org/abs/2105.09438) by Craig S. Kaplan for computing polyiamond coronas using a SAT solver.

## Overview

A **Heesch number** is the maximum number of complete coronas (rings of copies) that can be placed around a shape that doesn't tile the plane. This project implements a SAT-based algorithm to compute Heesch numbers of polyiamonds (shapes made from edge-connected equilateral triangles).

## Results

The search found the following 10-iamonds with high Heesch numbers:

### 10-iamond with Hc=4 (highest found!)

```
  ▲▼▲▼
▼▲▼▲
   ▼▲
```
Cells: [(0, 1), (1, 1), (2, 1), (2, 2), (3, 0), (3, 1), (3, 2), (4, 0), (4, 2), (5, 2)]
Corona sizes: [5, 10, 15, 21]

### 10-iamonds with Hc=3

1. ```
     ▲▼▲▼
   ▼▲▼▲
   ▲▼
   ```
   Cells: [(0, 0), (0, 1), (1, 0), (1, 1), (2, 1), (2, 2), (3, 1), (3, 2), (4, 2), (5, 2)]
   Corona sizes: [6, 12, 19]

2. ```
     ▲▼
    ▲▼▲▼
   ▲▼ ▼
   ▼
   ```
   Cells: [(1, 0), (1, 1), (2, 1), (2, 2), (3, 2), (3, 3), (4, 1), (4, 2), (4, 3), (5, 2)]
   Corona sizes: [6, 12, 18]

### Distribution of 10-iamonds by Heesch number

| Hc | Count | Notes |
|----|-------|-------|
| 0  | 10    | Cannot even complete first corona |
| 1  | 321   | Complete 1 corona only |
| 2  | 7     | Complete 2 coronas |
| 3  | 2     | Complete 3 coronas |
| 4  | 1     | Complete 4 coronas |
| 5+ | 107   | Tiles the plane |

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Find polyiamonds with high Heesch numbers

```bash
python find_heesch_fast.py 10  # Search 10-iamonds
python find_heesch_fast.py 7   # Search 7-iamonds
```

### Compute Heesch number of a specific polyiamond

```python
from polyiamond.grid import Cell
from polyiamond.polyiamond import Polyiamond
from polyiamond.corona_sat import compute_heesch_number

# Create a polyiamond
cells = frozenset([Cell(0, 0), Cell(1, 0), Cell(2, 0)])
poly = Polyiamond(cells)

# Compute Heesch number
hc = compute_heesch_number(poly, max_coronas=5, verbose=True)
print(f"Heesch number: {hc}")
```

## Algorithm

The algorithm works by:

1. **Generating all placements**: Find all ways to place copies of the polyiamond that touch the boundary of the current configuration
2. **SAT constraint encoding**: Create boolean variables for each placement and add constraints:
   - No two placements can overlap (pairwise exclusion clauses)
   - Every boundary cell must be covered (at-least-one clauses)
3. **Iterative solving**: Try to complete successive coronas until SAT returns UNSAT

## References

- C.S. Kaplan, "Heesch Numbers of Unmarked Polyforms", arXiv:2105.09438
- [heesch-sat](https://github.com/isohedral/heesch-sat) - C++ implementation by Craig Kaplan

## License

MIT
