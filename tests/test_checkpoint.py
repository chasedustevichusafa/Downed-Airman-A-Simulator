"""Verify parsing, path optimality, and the terminal checkpoint entry point."""

from pathlib import Path
import re
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

from map_loader import load_map, parse_map
from pathfinding import find_path


ROOT = Path(__file__).resolve().parent.parent
MAPS = ROOT / "maps"


class MapTests(unittest.TestCase):
    def test_reads_endpoints_and_rejects_out_of_bounds_tiles(self):
        grid = parse_map("S#..E\r\n.....\r\n")
        self.assertEqual(grid.start, (0, 0))
        self.assertEqual(grid.goal, (0, 4))
        self.assertTrue(grid.is_walkable((1, 0)))
        for tile in ((0, 1), (-1, 0), (0, -1), (2, 0), (0, 5)):
            with self.subTest(tile=tile):
                self.assertFalse(grid.is_walkable(tile))
        self.assertEqual(list(grid.walkable_neighbors(grid.start)), [(1, 0)])

    def test_rejects_invalid_maps(self):
        for text in ("", "\nSE", "SE\n.", "S?E", "S..", ".E", "SSE", "SEE"):
            with self.subTest(text=text):
                with self.assertRaises(ValueError):
                    parse_map(text)


class SearchTests(unittest.TestCase):
    def test_reachable_maps_have_valid_optimal_paths(self):
        for filename, expected_steps in (("direct.txt", 4), ("detour.txt", 6)):
            with self.subTest(filename=filename):
                grid = load_map(MAPS / filename)
                path, cost = find_path(grid)
                self.assertEqual(path[0], grid.start)
                self.assertEqual(path[-1], grid.goal)
                self.assertEqual(len(path) - 1, expected_steps)
                self.assertEqual(cost, expected_steps)
                for tile in path:
                    self.assertTrue(grid.is_walkable(tile))
                for (row, column), (next_row, next_column) in zip(path, path[1:]):
                    self.assertEqual(abs(row - next_row) + abs(column - next_column), 1)

    def test_unreachable_map_has_no_path(self):
        self.assertIsNone(find_path(load_map(MAPS / "unreachable.txt")))


class TerminalTests(unittest.TestCase):
    def run_demo(self, directory, *args):
        return subprocess.run(
            [sys.executable, str(ROOT / "main.py"), *args],
            cwd=directory,
            capture_output=True,
            text=True,
        )

    def test_default_map_works_outside_repository(self):
        with TemporaryDirectory() as directory:
            result = self.run_demo(directory)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(result.stdout.startswith("Starting map (detour.txt)\nS#..E\n.....\n"))
        self.assertIn("Path (row, column):", result.stdout)
        self.assertIn("Steps: 6", result.stdout)
        self.assertIn("Path cost: 6", result.stdout)

    def test_unreachable_map_is_a_valid_result(self):
        result = self.run_demo(ROOT, "maps/unreachable.txt")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(result.stdout.startswith("Starting map (unreachable.txt)\nS#E\n.#.\n"))
        self.assertTrue(result.stdout.rstrip().endswith("No path to extraction."))

    def test_trace_shows_search_and_why_goal_is_optimal(self):
        with TemporaryDirectory() as directory:
            (Path(directory) / "open.txt").write_text("S.E\n...\n", encoding="utf-8")
            result = self.run_demo(directory, "--trace", "open.txt")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(result.stdout.startswith("Starting map (open.txt)\nS.E\n...\n"))
        self.assertIn("@.E\n...", result.stdout)
        self.assertIn("moves so far: 1, estimated moves remaining: 3", result.stdout)
        self.assertLess(
            result.stdout.index("(0, 2): add to queue (moves so far: 2"),
            result.stdout.index("Select (0, 2) from the queue"),
        )
        self.assertIn("Lowest estimated total among remaining routes: 4 moves.", result.stdout)
        self.assertIn("Shortest-path check: the goal has zero moves remaining", result.stdout)
        self.assertIn("Steps: 2", result.stdout)

    def test_trace_only_shows_walkable_neighbors(self):
        result = self.run_demo(ROOT, "--trace")
        self.assertEqual(result.returncode, 0, result.stderr)
        first_step = result.stdout.split("Select (1, 0) from the queue", 1)[0]
        self.assertIn("(1, 0): add to queue", first_step)
        for impossible_move in ("(-1, 0):", "(0, -1):", "(0, 1):"):
            with self.subTest(move=impossible_move):
                self.assertNotIn(impossible_move, first_step)
        self.assertNotIn("blocked or outside the grid", result.stdout)

    def test_missing_and_invalid_files_return_errors(self):
        with TemporaryDirectory() as directory:
            (Path(directory) / "invalid.txt").write_text("S?E\n", encoding="utf-8")
            for filename in ("missing.txt", "invalid.txt"):
                with self.subTest(filename=filename):
                    result = self.run_demo(directory, filename)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(f"Could not load {filename}", result.stderr)
                    self.assertNotIn("Traceback", result.stderr)

    def test_color_distinguishes_map_tiles_and_keeps_plain_text_readable(self):
        colored = self.run_demo(ROOT, "--trace", "--color", "always")
        plain = self.run_demo(ROOT, "--trace", "--color", "never")
        redirected = self.run_demo(ROOT, "--trace")
        for result in (colored, plain, redirected):
            self.assertEqual(result.returncode, 0, result.stderr)

        # Check that each marker has its own style and resets after the tile.
        styles = re.findall(r"\x1b\[([0-9;]+)m([SE#@ox])\x1b\[0m", colored.stdout)
        color_by_tile = {tile: style for style, tile in styles}
        self.assertEqual(set(color_by_tile), set("SE#@ox"))
        self.assertEqual(len(set(color_by_tile.values())), 6)
        self.assertEqual(re.sub(r"\x1b\[[0-9;]+m", "", colored.stdout), plain.stdout)
        self.assertEqual(redirected.stdout, plain.stdout)
