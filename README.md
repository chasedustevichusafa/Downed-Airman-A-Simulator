# Downed Airman: A* Simulator

Downed Airman is a CS471 Python project that uses A* (pronounced “A-star”) to find the shortest path through a fictional grid.

## Checkpoint 1 testing procedure (Lesson 36)

Open a terminal in the repository folder, where `main.py`, `maps/`, and `tests/` are located. Run `python3 --version` and confirm you have Python 3.7 or later. The simulator uses the Python standard library and needs no package installation.

### 1. Watch A* find a path around a wall

```sh
python3 main.py --trace maps/detour.txt
```

The file argument loads the same map each time and skips the interactive menu. The first grid shows `S` for start, `E` for extraction, `#` for a wall, and `.` for an open tile. The airman moves one tile up, down, left, or right per step.

```text
S # . . E
. . . . .
```

Watch the selected tile (`@`), tiles waiting in the queue (`o`), and tiles whose neighbors have been checked (`x`). Each step displays **moves so far** plus **estimated moves remaining** to get **estimated total moves**. A* selects the tile with the lowest total estimate.

The start is at `(0, 0)` and the goal is at `(0, 4)`. The initial estimate is four moves, but the wall forces the first move down to `(1, 0)`. Look for the **Shortest-path check** once A* selects the goal. The goal has zero moves remaining, and a shorter route would have had a lower estimate somewhere in the queue. The last two lines should read:

```text
Steps: 6
Path cost: 6 (one unit per move)
```

### 2. Check a direct route and an unreachable goal

```sh
python3 main.py maps/direct.txt
python3 main.py --trace maps/unreachable.txt
```

- **Direct route** ends with `Steps: 4` and a path cost of 4.
- **Unreachable goal** ends with `Frontier exhausted before reaching the goal.` and `No path to extraction.` This shows that A* stops cleanly when there are no more tiles to check.

### 3. Run the automated tests

```sh
python3 -m unittest discover -s tests -v
```

The suite should report **14 tests** and finish with `OK`. It checks map validation, expected path costs, unreachable goals, the terminal menu, and trace behavior.

## Project Status

The Lesson 36 terminal checkpoint is implemented. Dynamic simulation and the Lesson 41 evaluation are later milestones. The final evaluation compares A* with Dijkstra on static maps and measures path cost, nodes expanded, and extraction rate in reproducible dynamic simulations.

- [Project scoping worksheet](CS471%20Final%20Project%20Scoping%20Worksheet.docx)
- [Milestone plan and exit criteria](PROJECT_PLAN.md)
- [Lesson 36 checkpoint build plan](PROJECT_PLAN.md#lesson-36--terminal-checkpoint)
- [Contributor guidelines](AGENTS.md)
- [Desktop app implementation plan](GUI_PLAN.md)

## Try the interactive map menu

Run `python3 main.py` from the repository root in a terminal. Enter the number of rows and columns, each from 5 to 40, then choose a layout. Choices 1 through 5 are fixed for each size.

1. Open grid
2. Middle gate
3. Bottom gate
4. Staggered gates
5. Wide barrier
6. New random grid
7. Dead-end maze

Choice 7 turns on the search trace automatically and pauses for one second after each displayed search iteration. Try 5 rows and 5 columns for a shorter demo, or 9 rows and 13 columns to see A* investigate four branches that end near the goal. On the larger example, the shortest route goes around the branches along the bottom edge and takes 28 moves.

Choice 6 guarantees a walkable route and records the layout in the local `.random-map-history.sqlite3` file. It avoids the five presets and every random layout recorded for that size. Keep the history file to preserve that guarantee across runs. If the available layouts ever run out, the script asks you to choose another size. Git ignores the history file.

Run `python3 main.py --trace` to see the search for any menu layout. With redirected input and no map file, the script loads the bundled detour map unless you pass `--choose-map`.

## Map file format

Maps are rectangular UTF-8 text grids. Use exactly one `S` for the start and one `E` for extraction. A `.` is open and a `#` is a wall. Coordinates are zero-based `(row, column)`, starting at the upper left. Each horizontal or vertical move costs one.

## How A* works

The terminal leaves one space between tiles so equal row and column counts look closer to square in a typical terminal font. It colors the start green, the goal magenta, and walls red. During the search, the selected tile is yellow, queued tiles are cyan, and checked tiles are blue. Open tiles use the terminal’s default text color. Redirected output uses plain text by default. Use `--color never` to turn colors off or `--color always` to force them.

1. **Score routes.** Moves so far counts the moves in the best route found to a tile. Estimated moves remaining counts the horizontal and vertical moves needed to reach the goal on an open grid. Estimated total moves adds the two values. Walls can only add moves, so the estimate never exceeds the moves actually needed.
2. **Check neighbors.** Select the tile with the lowest estimated total moves from the frontier, the queue of tiles waiting to be checked. The map supplies only legal one-step destinations. When a route improves the number of moves needed to reach a neighbor, remember the previous tile and add the neighbor to the queue.
3. **Confirm the shortest path.** Once the goal is selected, the remaining estimate is zero. Any shorter route would still have a tile in the queue with a lower estimate. Follow the remembered tiles from the goal back to the start, then reverse their order. If the queue empties before the goal is selected, there is no path.

Follow the numbered comments in [pathfinding.py](pathfinding.py) to see each step in code.

## Contribution Log

### 2026-11-20 12:53 MST — Plan the cross-platform desktop app

- Created the `codex/astar-desktop-app` branch and wrote `GUI_PLAN.md`. The plan covers shared A* iterations, map selection, playback controls, Windows, macOS, and Linux testing, and the conditions for merging into `main`.
- Verified the README plan link and ran the existing checkpoint suite. Desktop implementation and platform testing are future work on the feature branch.

### 2026-11-19 09:44 MST — Put the checkpoint testing procedure first

- Added a first-run checklist to `README.md` with setup requirements, fixed-map commands, expected results, and a walkthrough of the detour trace. Moved interactive map selection below the checkpoint procedure.
- Verified the documented commands and results. The detour takes six moves, the direct route takes four, the unreachable trace exhausts its queue, and all fourteen tests pass.

### 2026-11-19 09:41 MST — Prevent the checkpoint tests from waiting for menu input

- Updated the terminal test helper in `tests/test_checkpoint.py` to pipe empty input by default and use scripted answers for menu tests. All fourteen tests passed with both redirected input and interactive terminal input.

### 2026-11-18 14:16 MST — Pace each dead-end maze iteration

- Updated `main.py` and `pathfinding.py` so option 7 prints each search iteration and waits one second before continuing. The final path prints immediately after the goal iteration’s pause.
- All fourteen tests passed. The maze test confirms one one-second pause per displayed iteration and checks that pauses occur after the iteration details are printed.

### 2026-11-18 14:13 MST — Add a dead-end maze for the search demo

- Added option 7 in `main.py` and a repeatable maze in `map_choices.py`. The maze gives A* several promising branches to explore before it reaches the goal by the bottom row. The menu choice turns on the trace automatically.
- All fourteen tests passed. The new terminal test verifies that A* explores four dead ends outside the final 28-move path on a 9 × 13 grid.

### 2026-11-18 14:07 MST — Space terminal map columns

- Added one space between columns in the starting map and search snapshots. Updated terminal output assertions in `tests/test_checkpoint.py`.
- All thirteen tests passed. Verified the row counts and column spacing for 5 × 5, 40 × 5, and 5 × 40 grids in both views.

### 2026-11-18 14:04 MST — Add map size and layout selection

- Added the startup menu in `main.py` and layout generation in `map_choices.py`. Rows and columns can each range from 5 to 40. Each size has five fixed layouts and a random layout that excludes presets and prior random selections through local history.
- Updated the checkpoint instructions to show both the menu and the direct fixture commands. All thirteen tests passed, covering menu input validation, distinct and solvable presets, and twenty nonrepeating random maps.

### 2026-11-18 14:00 MST — Trace only legal moves

- Added walkable neighbor generation to `map_loader.py` and updated `pathfinding.py` to score and display only those destinations. The map still shows walls as part of the grid.
- All ten tests passed. The trace test confirms that the first detour step lists the single legal move and omits the wall and off-grid coordinates.

### 2026-11-18 13:56 MST — Color the terminal map

- Added distinct colors to the starting map, search snapshots, and their legends in `main.py` and `pathfinding.py`. The map symbols remain visible in plain text. Added a color option for forcing or disabling terminal colors.
- All nine tests passed. The new terminal test verifies six distinct tile styles, plain redirected output, and identical trace text with or without color.

### 2026-11-18 13:55 MST — Spell out search terms in the terminal

- Replaced the one-letter score names with full labels in `pathfinding.py`, the README walkthrough, and `PROJECT_PLAN.md`. The trace defines the three scores, the queue, and the search markers before showing any decisions. The starting map explains its coordinates and symbols.
- Updated `AGENTS.md` to keep terminal wording and teaching comments explicit. Updated the terminal test to check the new wording and verified all eight tests.

### 2026-11-18 13:49 MST — Align the checkpoint docs with the terminal demo

- Updated `AGENTS.md`, `PROJECT_PLAN.md`, and the README command list to cover the starting grid and `--trace` walkthrough. The demo steps now show how to explain both optimality and an exhausted frontier.
- Reran all eight tests and checked the traced detour and unreachable runs before committing the terminal UI changes.

### 2026-11-18 13:49 MST — Use h in the A* explanation

- Updated the helper name and trace in `pathfinding.py` and the explanations in `README.md` and `PROJECT_PLAN.md` to use `h` for the estimated moves remaining. Verified the traced demo and all eight tests.

### 2026-11-18 13:47 MST — Show the starting map

- Updated `main.py` to display the loaded map and its tile legend before A* starts, in both the standard output and trace modes.
- Updated the terminal tests to check that the unmarked map appears first for the default, unreachable, and traced runs. All eight tests passed.

### 2026-11-18 13:46 MST — Show A* exploration in the terminal

- Added `--trace` in `main.py` and connected it to the search in `pathfinding.py`. The trace shows grid snapshots, scores, neighbor decisions, and the reason A* can stop at the goal or report no route.
- Added a terminal regression test for the case where A* proves the result optimal while other tiles are still queued. All eight tests passed, and both the detour and unreachable traces were checked manually.

### 2026-11-18 13:39 MST — Implement the Python terminal checkpoint

- Added `map_loader.py` for grid validation, `pathfinding.py` for A* with detailed comments, and `main.py` for the terminal demo. Added three static map fixtures, Python tests, and a Git ignore rule for Python bytecode caches.
- Documented the map format, exact run and test commands, and an A* walkthrough using the detour map.
- All seven tests passed. The terminal demos returned six moves, four moves, and no path as expected. A* also agreed with breadth-first search on all 1,024 wall layouts for a 3 × 4 grid with fixed endpoints.

### 2026-11-18 13:37 MST — Detail the Lesson 36 build plan

- Expanded `PROJECT_PLAN.md` with a proposed Python file layout, map and CLI contracts, the A* implementation sequence, and a demo checklist. Added three static fixture designs with expected costs and step counts.
- Verified the planned fixture results independently with breadth-first search. The planned Python modules, fixtures, and tests are the next implementation work.

### 2026-11-18 09:01 MST — Add the README and logging rule

- Created `README.md` with the project overview, checkpoint status, reference links, and a record of work to date.
- Updated `AGENTS.md` to require a detailed, timestamped README entry with each contribution, including the affected work and verification results.
- Checked the README links against the workspace and reviewed Git history to confirm the setup and ignore-rule entries below.

### 2026-11-18 08:58 MST — Turn instructor feedback into a milestone plan

- Reviewed the instructor’s feedback and created `PROJECT_PLAN.md` with tasks and exit criteria for the scope refinement, Lesson 36 terminal checkpoint, dynamic simulation, and Lesson 41 defense.
- Planned fresh A* searches when the grid changes, a consistent movement-cost model, and a Dijkstra comparison on static maps. Planned at least 100 reproducible dynamic trials across multiple map sizes.

### 2026-11-18 08:56 MST — Add the worksheet feedback ignore rule

- Added `.gitignore` so the local worksheet feedback Markdown stays out of version control. Commit `3db14b2`.

### 2026-11-17 21:40 MST — Set up the repository and contributor guide

- Added the CS471 scoping worksheet and `AGENTS.md` in the initial commit, `c3253b9`.
- Used the worksheet to document the project scope, Python conventions, terminal checkpoint, and final evaluation metrics in the contributor guide.
