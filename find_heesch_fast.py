#!/usr/bin/env python3
"""
Find polyiamonds with high Heesch numbers (optimized version).
"""

import sys
from polyiamond.grid import Cell
from polyiamond.polyiamond import Polyiamond
from polyiamond.generator import generate_fixed_polyiamonds
from polyiamond.corona_sat import find_coronas


def search_high_heesch(n: int, max_coronas: int = 5, min_hc: int = 2):
    """
    Search for n-iamonds with Heesch numbers >= min_hc.

    Prints results as they are found.
    """
    print(f"Generating {n}-iamonds...")
    fixed_polys = generate_fixed_polyiamonds(n)
    print(f"Found {len(fixed_polys)} fixed {n}-iamonds")

    seen_canonical = set()
    hc_counts = {}
    high_hc_examples = {}

    for i, cells in enumerate(fixed_polys):
        if (i + 1) % 100 == 0:
            print(f"  Processed {i + 1}/{len(fixed_polys)}...", file=sys.stderr)

        poly = Polyiamond(cells)

        # Skip if we've seen this canonical form
        canon_key = tuple(sorted((c.x, c.y) for c in poly.canonical_cells()))
        if canon_key in seen_canonical:
            continue
        seen_canonical.add(canon_key)

        # Compute Heesch number
        hc, coronas = find_coronas(poly, max_coronas=max_coronas)

        # Track counts
        if hc not in hc_counts:
            hc_counts[hc] = 0
            high_hc_examples[hc] = []
        hc_counts[hc] += 1

        # Report interesting finds immediately
        if hc >= min_hc and hc < max_coronas:
            print(f"\n*** Found {n}-iamond with Hc={hc} ***")
            print(f"Cells: {sorted((c.x, c.y) for c in poly.cells)}")
            print(poly)
            print(f"Corona sizes: {[len(c) for c in coronas]}")
            high_hc_examples[hc].append((poly, coronas))

    print(f"\n{'='*60}")
    print(f"Searched {len(seen_canonical)} unique {n}-iamonds")
    print("Heesch number distribution:")
    for hc in sorted(hc_counts.keys()):
        tiler = "(tiles plane)" if hc >= max_coronas else ""
        print(f"  Hc={hc}: {hc_counts[hc]} polyiamonds {tiler}")

    return high_hc_examples


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 10

    print("=" * 60)
    print(f"Searching for {n}-iamonds with high Heesch numbers")
    print("=" * 60)

    examples = search_high_heesch(n, max_coronas=5, min_hc=2)

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for hc in sorted(examples.keys()):
        if hc < 5:  # Non-tilers
            print(f"\nHc={hc}: {len(examples[hc])} examples")
            for poly, coronas in examples[hc][:3]:  # Show first 3
                print(f"  Cells: {sorted((c.x, c.y) for c in poly.cells)}")
