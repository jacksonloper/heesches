#!/usr/bin/env python3
"""
Find polyiamonds with high Heesch numbers.

This script searches for polyiamonds with specific Heesch numbers,
particularly the 10-iamond with Hc=3.
"""

import sys
from polyiamond.grid import Cell
from polyiamond.polyiamond import Polyiamond
from polyiamond.generator import generate_fixed_polyiamonds
from polyiamond.corona_sat import compute_heesch_number, find_coronas
from polyiamond.visualize import visualize_heesch_result


def search_polyiamonds(n: int, max_coronas: int = 5, target_hc: int = None):
    """
    Search for n-iamonds with high Heesch numbers.

    Args:
        n: Size of polyiamonds to search
        max_coronas: Maximum coronas to check
        target_hc: If set, only report polyiamonds with this Heesch number

    Returns:
        List of (polyiamond, heesch_number, coronas) tuples
    """
    print(f"Generating {n}-iamonds...")
    fixed_polys = generate_fixed_polyiamonds(n)
    print(f"Found {len(fixed_polys)} fixed {n}-iamonds")

    # Track results by canonical form to avoid duplicates
    results = {}
    seen_canonical = set()

    for i, cells in enumerate(fixed_polys):
        if (i + 1) % 10 == 0:
            print(f"  Processing {i + 1}/{len(fixed_polys)}...", end='\r')

        poly = Polyiamond(cells)

        # Skip if we've seen this canonical form
        canon_key = tuple(sorted((c.x, c.y) for c in poly.canonical_cells()))
        if canon_key in seen_canonical:
            continue
        seen_canonical.add(canon_key)

        # Compute Heesch number
        hc, coronas = find_coronas(poly, max_coronas=max_coronas)

        if target_hc is None or hc == target_hc:
            if hc not in results:
                results[hc] = []
            results[hc].append((poly, coronas))

    print(f"\nSearched {len(seen_canonical)} unique {n}-iamonds")
    return results


def main():
    # Search for 10-iamonds with Hc=3
    print("=" * 60)
    print("Searching for 10-iamond with Heesch number 3")
    print("=" * 60)

    results = search_polyiamonds(10, max_coronas=5, target_hc=3)

    if 3 in results:
        print(f"\nFound {len(results[3])} 10-iamonds with Hc=3:")
        for i, (poly, coronas) in enumerate(results[3]):
            print(f"\n{'='*40}")
            print(f"10-iamond #{i+1} with Hc=3:")
            print(f"Cells: {sorted((c.x, c.y) for c in poly.cells)}")
            print(poly)
            print(f"Corona sizes: {[len(c) for c in coronas]}")

            # Save visualization
            try:
                from polyiamond.visualize import visualize_heesch_result
                visualize_heesch_result(poly, 3, coronas,
                                       save_path=f"10iamond_hc3_{i+1}.png")
            except Exception as e:
                print(f"Could not save visualization: {e}")
    else:
        print("\nNo 10-iamonds with Hc=3 found!")

        # Show what we found
        print("\nHeesch number distribution:")
        for hc in sorted(results.keys()):
            print(f"  Hc={hc}: {len(results[hc])} polyiamonds")


if __name__ == "__main__":
    main()
