"""Run the Lesson 36 terminal demo on a predefined map."""

import argparse
from os import environ
from pathlib import Path
from sqlite3 import Error as MapHistoryError
import sys
from typing import Tuple

from map_choices import (
    MAXIMUM_SIZE,
    MINIMUM_SIZE,
    PRESET_NAMES,
    RANDOM_OPTION,
    preset_grids,
    random_grid,
)
from map_loader import GridMap, load_map
from pathfinding import find_path


PROJECT_DIRECTORY = Path(__file__).resolve().parent
DEFAULT_MAP = PROJECT_DIRECTORY / "maps" / "detour.txt"
RANDOM_MAP_HISTORY = PROJECT_DIRECTORY / ".random-map-history.sqlite3"

# Reset after each character so tile colors never leak into the prose.
COLORED_TILES = {
    "S": "\033[1;92mS\033[0m",  # Bright green for the start.
    "E": "\033[1;95mE\033[0m",  # Bright magenta for the goal.
    "#": "\033[91m#\033[0m",    # Red for walls.
    "@": "\033[1;93m@\033[0m",  # Bright yellow for the selected tile.
    "o": "\033[96mo\033[0m",    # Cyan for queued tiles.
    "x": "\033[94mx\033[0m",    # Blue for tiles already checked.
}


def read_number(prompt: str, minimum: int, maximum: int) -> int:
    """Read a whole number and prompt again if it falls outside the range."""
    while True:
        response = input(f"{prompt} ({minimum} to {maximum}): ").strip()
        try:
            number = int(response)
        except ValueError:
            print(f"Enter a whole number from {minimum} to {maximum}.")
            continue
        if minimum <= number <= maximum:
            return number
        print(f"Enter a whole number from {minimum} to {maximum}.")


def choose_map(history_file: Path) -> Tuple[GridMap, str]:
    """Prompt for dimensions, then list the six choices for that size."""
    height = read_number("Number of rows", MINIMUM_SIZE, MAXIMUM_SIZE)
    width = read_number("Number of columns", MINIMUM_SIZE, MAXIMUM_SIZE)
    presets = preset_grids(height, width)
    print(f"\nChoose a map with {height} rows and {width} columns.")
    for number, name in enumerate(PRESET_NAMES, start=1):
        print(f"  {number}. {name}")
    print(f"  {RANDOM_OPTION}. New random grid")
    choice = read_number("Map choice", 1, RANDOM_OPTION)
    print()
    if choice == RANDOM_OPTION:
        return random_grid(height, width, presets, history_file), "New random grid"
    return presets[choice - 1], PRESET_NAMES[choice - 1]


def main() -> int:
    """Load the chosen map, explain its symbols, and report the search result."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "map_file", nargs="?", type=Path,
        help="solve this text map directly without opening the map menu",
    )
    parser.add_argument(
        "--choose-map", action="store_true",
        help="open the map menu even when input is redirected",
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
    if options.map_file is not None and options.choose_map:
        parser.error("Choose either a map file or --choose-map.")

    try:
        if options.choose_map or (options.map_file is None and sys.stdin.isatty()):
            grid, map_name = choose_map(RANDOM_MAP_HISTORY)
        else:
            map_file = options.map_file or DEFAULT_MAP
            grid = load_map(map_file)
            map_name = map_file.name
    except (EOFError, KeyboardInterrupt):
        print("\nMap selection canceled.", file=sys.stderr)
        return 1
    except MapHistoryError as error:
        print(f"Could not use random map history at {RANDOM_MAP_HISTORY}: {error}", file=sys.stderr)
        return 1
    except (OSError, ValueError) as error:
        print(f"Could not load {options.map_file or 'map'}: {error}", file=sys.stderr)
        return 1

    use_color = options.color == "always" or (
        options.color == "auto"
        and sys.stdout.isatty()
        and environ.get("TERM") != "dumb"
        and not environ.get("NO_COLOR")
    )

    def format_tile(symbol: str) -> str:
        return COLORED_TILES.get(symbol, symbol) if use_color else symbol

    print(f"Starting map ({map_name})")
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
