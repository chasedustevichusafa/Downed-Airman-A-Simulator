# Downed Airman: A Simulator

Downed Airman is a CS471 Python project that uses A* to find paths through a fictional 2D grid. The Lesson 36 checkpoint is a terminal demo that loads a predefined text map and prints the path and step count. The Lesson 41 evaluation compares A* with Dijkstra on static maps and measures path cost, nodes expanded, and extraction rate in reproducible dynamic simulations.

## Project Status

The Lesson 36 terminal checkpoint is implemented. It uses Python 3.7 or later and the standard library. Dynamic simulation and the Lesson 41 evaluation are later milestones.

- [Project scoping worksheet](CS471%20Final%20Project%20Scoping%20Worksheet.docx)
- [Milestone plan and exit criteria](PROJECT_PLAN.md)
- [Lesson 36 checkpoint build plan](PROJECT_PLAN.md#lesson-36--terminal-checkpoint)
- [Contributor guidelines](AGENTS.md)

## Run the Lesson 36 demo

Run these commands from the repository root. The first command loads the bundled detour map without prompting.

```sh
python3 main.py
python3 main.py maps/direct.txt
python3 main.py maps/unreachable.txt
python3 -m unittest discover -s tests -v
```

Maps are rectangular UTF-8 text grids. Use exactly one `S` for the start and one `E` for extraction. A `.` is open and a `#` is a wall. Coordinates are zero-based `(row, column)`, starting at the upper left. Each horizontal or vertical move costs one.

| Map | Expected output |
| --- | --- |
| `detour.txt` | A path of 6 moves with cost 6 |
| `direct.txt` | A path of 4 moves with cost 4 |
| `unreachable.txt` | `No path to extraction.` |

## How A* works

1. **Score routes.** For each tile, `g` is the cost of the best route discovered from the start, and `h` is its Manhattan distance to the goal. A min-heap picks the route with the lowest `f = g + h`. Manhattan distance counts how many horizontal and vertical moves are needed on an open grid, so walls can only make the true route cost higher.
2. **Expand a tile.** Pop the next route from the heap. Skip its entry if a cheaper route to the same tile is already recorded. Check the four neighboring tiles and discard walls and out-of-bounds tiles. For each cheaper route discovered, record its new cost and predecessor, then queue it.
3. **Finish and reconstruct.** When the goal is popped, its heuristic is zero, so its priority equals its actual cost. If a cheaper route existed, some tile on that route would still have a lower estimated total cost and would be popped first. Follow predecessors from the goal back to the start and reverse the list. If the heap empties first, the goal is unreachable.

On the detour map, the start at `(0, 0)` has `g = 0` and `h = 4`. The wall blocks the direct move to the right. Moving down to `(1, 0)` gives `g = 1` and `h = 5`. A* finds a route around the wall in six moves. Follow the numbered comments in [pathfinding.py](pathfinding.py) to see each step in code.

## Contribution Log

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
