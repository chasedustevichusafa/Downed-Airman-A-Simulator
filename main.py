"""Run the Lesson 36 terminal demo on a predefined map."""

import argparse
from pathlib import Path
import sys

from map_loader import load_map
from pathfinding import find_path


DEFAULT_MAP = Path(__file__).resolve().parent / "maps" / "detour.txt"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "map_file", nargs="?", type=Path, default=DEFAULT_MAP,
        help="text map to solve (default: maps/detour.txt)",
    )
    args = parser.parse_args()

    try:
        grid = load_map(args.map_file)
    except (OSError, ValueError) as error:
        print(f"Could not load {args.map_file}: {error}", file=sys.stderr)
        return 1

    result = find_path(grid)
    if result is None:
        print("No path to extraction.")
        return 0

    path, cost = result
    print("Path (row, column): " + " -> ".join(str(tile) for tile in path))
    # The path includes the start, so it contains one more tile than move.
    print(f"Steps: {len(path) - 1}")
    print(f"Path cost: {cost}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
