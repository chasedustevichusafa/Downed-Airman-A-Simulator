"""Read and validate the checkpoint's plain-text grid maps."""

from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Tuple


Position = Tuple[int, int]


@dataclass(frozen=True)
class GridMap:
    """A rectangular grid with zero-based (row, column) coordinates."""

    rows: Tuple[str, ...]
    start: Position
    goal: Position

    def is_walkable(self, position: Position) -> bool:
        row, column = position
        # Check both bounds before indexing. Negative Python indices wrap around.
        return (
            0 <= row < len(self.rows)
            and 0 <= column < len(self.rows[0])
            and self.rows[row][column] != "#"
        )

    def walkable_neighbors(self, position: Position) -> Iterator[Position]:
        """Yield legal one-step destinations from a tile on the map."""
        row, column = position
        # Add a direction only when the map has a tile in that direction.
        neighbors = []
        if row > 0:
            neighbors.append((row - 1, column))
        if row + 1 < len(self.rows):
            neighbors.append((row + 1, column))
        if column > 0:
            neighbors.append((row, column - 1))
        if column + 1 < len(self.rows[row]):
            neighbors.append((row, column + 1))

        yield from filter(self.is_walkable, neighbors)


def parse_map(text: str) -> GridMap:
    """Parse a map and raise ValueError if its shape or symbols are invalid."""
    rows = tuple(text.splitlines())
    if not rows or not rows[0]:
        raise ValueError("The map is empty or starts with an empty row.")

    starts = []
    goals = []
    width = len(rows[0])
    for row_index, row in enumerate(rows):
        if len(row) != width:
            raise ValueError(f"Row {row_index + 1} must contain {width} tiles.")

        for column, tile in enumerate(row):
            if tile == "S":
                starts.append((row_index, column))
            elif tile == "E":
                goals.append((row_index, column))
            elif tile not in ".#":
                raise ValueError(
                    f"Unknown tile {tile!r} at row {row_index + 1}, "
                    f"column {column + 1}."
                )

    if len(starts) != 1 or len(goals) != 1:
        raise ValueError("The map must contain exactly one S and one E.")
    return GridMap(rows, starts[0], goals[0])


def load_map(path: Path) -> GridMap:
    """Read a UTF-8 map file and validate its contents."""
    return parse_map(path.read_text(encoding="utf-8"))
