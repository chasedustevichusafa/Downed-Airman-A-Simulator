"""Run the Lesson 36 terminal demo on a predefined map."""

import argparse
from os import environ
from pathlib import Path
import sys

from map_loader import load_map
from pathfinding import find_path


DEFAULT_MAP = Path(__file__).resolve().parent / "maps" / "detour.txt"

# Reset after each character so tile colors never leak into the prose.
COLORED_TILES = {
    "S": "\033[1;92mS\033[0m",  # Bright green for the start.
    "E": "\033[1;95mE\033[0m",  # Bright magenta for the goal.
    "#": "\033[91m#\033[0m",    # Red for walls.
    "@": "\033[1;93m@\033[0m",  # Bright yellow for the selected tile.
    "o": "\033[96mo\033[0m",    # Cyan for queued tiles.
    "x": "\033[94mx\033[0m",    # Blue for tiles already checked.
}


def main() -> int:
    """Load the chosen map, explain its symbols, and report the search result."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "map_file", nargs="?", type=Path, default=DEFAULT_MAP,
        help="text map to solve (default: maps/detour.txt)",
    )
    parser.add_argument(
        "--trace", action="store_true",
        help="show the grid, neighbor checks, and why the search stops",
    )
    parser.add_argument(
        "--color", choices=("auto", "always", "never"), default="auto",
        help="color map tiles automatically in a terminal, always, or never",
    )
    options = parser.parse_args()

    try:
        grid = load_map(options.map_file)
    except (OSError, ValueError) as error:
        print(f"Could not load {options.map_file}: {error}", file=sys.stderr)
        return 1

    use_color = options.color == "always" or (
        options.color == "auto"
        and sys.stdout.isatty()
        and environ.get("TERM") != "dumb"
        and not environ.get("NO_COLOR")
    )

    def format_tile(symbol: str) -> str:
        return COLORED_TILES.get(symbol, symbol) if use_color else symbol

    print(f"Starting map ({options.map_file.name})")
    for row in grid.rows:
        print("".join(format_tile(symbol) for symbol in row))
    print(
        f"Map symbols: {format_tile('S')} start, {format_tile('E')} extraction goal, "
        f"{format_tile('#')} impassable wall, . open tile."
    )
    print("Coordinates use (row, column), with (0, 0) at the upper left.\n", flush=True)

    result = find_path(grid, trace=print if options.trace else None, format_tile=format_tile)
    if result is None:
        print("No path to extraction.")
        return 0

    path, cost = result
    print("Path (row, column): " + " -> ".join(str(tile) for tile in path))
    # The path includes the start, so it contains one more tile than move.
    print(f"Steps: {len(path) - 1}")
    print(f"Path cost: {cost} (one unit per move)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
