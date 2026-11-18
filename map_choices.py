"""Build repeatable and one-time layouts for a user-selected grid size."""

from contextlib import closing
from pathlib import Path
from secrets import randbelow
import sqlite3
from typing import List, Set, Tuple

from map_loader import GridMap, Position, parse_map


MINIMUM_SIZE = 5
MAXIMUM_SIZE = 40
PRESET_NAMES = ("Open grid", "Middle gate", "Bottom gate", "Staggered gates", "Wide barrier")
RANDOM_OPTION = len(PRESET_NAMES) + 1
DEAD_END_OPTION = RANDOM_OPTION + 1
DEAD_END_NAME = "Dead-end maze"


def _build_grid(height: int, width: int, walls: Set[Position]) -> GridMap:
    rows = [
        ["#" if (row, column) in walls else "." for column in range(width)]
        for row in range(height)
    ]
    rows[0][0] = "S"
    rows[0][-1] = "E"
    return parse_map("\n".join("".join(row) for row in rows))


def preset_grids(height: int, width: int) -> Tuple[GridMap, ...]:
    """Return five fixed layouts in the same order for every valid size."""
    center_row = height // 2
    center_column = width // 2
    wall_layouts = (
        set(),
        {(row, center_column) for row in range(height) if row != center_row},
        {(row, center_column) for row in range(height - 1)},
        {(row, 1) for row in range(height - 1)}
        | {(row, width - 2) for row in range(height) if row != 1},
        {(row, column) for row in range(center_row) for column in range(1, width - 1)},
    )
    return tuple(_build_grid(height, width, walls) for walls in wall_layouts)


def dead_end_grid(height: int, width: int) -> GridMap:
    """Build branches that head toward the goal and end a wall short."""
    # The left edge, bottom row, and right edge form the only route to
    # the goal. A wall separates each branch from the right edge.
    branch_rows = range(0, height - 2, 2)
    walls = {
        (row, column)
        for row in range(height - 1)
        for column in range(1, width - 1)
        if row not in branch_rows or column == width - 2
    }
    # The branches open onto the left edge and stay separate from one another
    # and from the bottom row. Their tiles look closer to the goal than
    # the bottom detour does, so A* investigates them first.
    return _build_grid(height, width, walls)


def _reserve_layout(
    history_file: Path, height: int, width: int, excluded_layouts: Set[int], total_layouts: int
) -> int:
    """Choose uniformly from the available wall patterns and record the choice."""
    with closing(sqlite3.connect(str(history_file))) as connection, connection:
        # Lock before reading so two runs cannot reserve the same layout.
        connection.execute("BEGIN IMMEDIATE")
        connection.execute(
            "CREATE TABLE IF NOT EXISTS shown_maps ("
            "height INTEGER, width INTEGER, layout TEXT, PRIMARY KEY (height, width, layout))"
        )
        previous = connection.execute(
            "SELECT layout FROM shown_maps WHERE height = ? AND width = ?", (height, width)
        )
        unavailable = sorted(excluded_layouts | {int(layout) for (layout,) in previous})
        remaining = total_layouts - len(unavailable)
        if remaining <= 0:
            raise ValueError("All random layouts for this size have been used. Choose another size.")

        # Draw a rank among unused layouts. Skip over every excluded layout
        # at or below that rank to find the corresponding full-space position.
        layout = randbelow(remaining)
        for used_layout in unavailable:
            if used_layout > layout:
                break
            layout += 1

        # Store as text because the number of wall patterns can exceed the
        # largest integer the database can store as a numeric value.
        connection.execute(
            "INSERT INTO shown_maps (height, width, layout) VALUES (?, ?, ?)",
            (height, width, str(layout)),
        )
    return layout


def random_grid(
    height: int, width: int, presets: Tuple[GridMap, ...], history_file: Path
) -> GridMap:
    """Return a new solvable layout for this size and history file."""
    # Leave a corridor down the left edge, across the middle, and back up
    # the right edge. Every wall pattern outside it still leaves a route.
    corridor = {(height // 2, column) for column in range(width)}
    for row in range(height // 2 + 1):
        corridor.update(((row, 0), (row, width - 1)))
    optional_tiles: List[Position] = [
        (row, column)
        for row in range(height)
        for column in range(width)
        if (row, column) not in corridor
    ]
    excluded_layouts = {
        int(
            "".join("1" if grid.rows[row][column] == "#" else "0"
                    for row, column in optional_tiles),
            2,
        )
        for grid in presets
        if all(grid.rows[row][column] != "#" for row, column in corridor)
    }
    layout = _reserve_layout(history_file, height, width, excluded_layouts, 2 ** len(optional_tiles))
    # One binary digit per optional tile determines whether it is a wall.
    wall_pattern = format(layout, f"0{len(optional_tiles)}b")
    walls = {tile for tile, digit in zip(optional_tiles, wall_pattern) if digit == "1"}
    return _build_grid(height, width, walls)
