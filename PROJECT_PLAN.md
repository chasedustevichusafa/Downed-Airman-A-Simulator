# Downed Airman Project Plan

The CS471 scoping worksheet defines the deliverables. The instructor’s feedback clarifies three implementation decisions. Rerun standard A* from the current tile when the grid changes, use a consistent path-cost model, and compare A* with Dijkstra on static maps. Report static shortest-path results and dynamic simulation results separately.

## Lesson 32 — Refine the scope

- [ ] Keep A* as the simulator’s core algorithm. Use Dijkstra as an evaluation baseline on static maps, implemented by running the same search with a zero heuristic.
- [ ] Agree on the initial map format. Use a rectangular text grid with `S` for start, `E` for extraction, `#` for walls, and `.` for open tiles. Require one start and one extraction tile.
- [ ] Define path cost as the sum of costs to enter each tile after the start. Start with cost 1 per move. If static maps later include weighted tiles, keep costs at least 1 so the remaining-moves estimate remains a lower bound. Track extraction and capture as terminal game outcomes.

**Exit criteria.** Teammates can explain the grid rules, cost calculation, baseline, and when A* will be called again.

## Lesson 36 — Terminal checkpoint

**Deliverable.** A Python 3 program that opens a predefined text map without prompting, finds an optimal four-direction path with A*, and prints the path and step count. This checkpoint uses static maps and Python’s standard library.

### 1. Define maps and write the parser

Put text fixtures in `maps/` and the parser in `map_loader.py`. Use zero-based `(row, column)` coordinates with `(0, 0)` at the upper left. Accept rectangular maps with exactly one `S` and one `E`. Reject empty maps, uneven rows, unknown symbols, and missing or repeated endpoints with a clear error.

| Fixture | Rows, top to bottom | Expected result |
| --- | --- | --- |
| `direct.txt` | `S...E` | 4 moves, cost 4 |
| `detour.txt` | `S#..E` / `.....` | 6 moves, cost 6 |
| `unreachable.txt` | `S#E` / `.#.` | No path |

### 2. Implement A* in `pathfinding.py`

Generate only in-bounds, non-wall neighbors, with one unit of cost per move. Order the queue by estimated total moves. Add the moves in the best known route from the start to the estimated moves remaining on an open grid. Track predecessors and update them when a cheaper route to a tile is found. Skip stale queue entries and stop when the goal is popped. Return the reconstructed path including both endpoints and its cost, or a no-path result if the queue empties. Compute steps as `len(path) - 1`.

### 3. Connect the terminal entry point

Use `main.py` to load the bundled `detour.txt` fixture by default and accept an optional path for alternate maps. Display the original grid and tile legend before searching. Print the coordinate sequence and step count on success. Print `No path to extraction.` for a valid unreachable map. Report malformed or missing files with a readable error and a nonzero exit status.

Use `--trace` to show each selected tile, the frontier, and the neighbor decisions. At the goal, use the zero remaining-moves estimate and the lowest score in the queue to explain why A* can stop. On the unreachable map, demonstrate what happens when the frontier empties.

### 4. Test and rehearse

- Use `unittest` in `tests/` for parser validation and the three known outcomes. Check that successful paths start at `S`, end at `E`, avoid walls, and move exactly one tile per step. Check optimal cost and step count so equally short paths can pass.
- After implementation, verify the commands below from a clean checkout and record them with the map symbols in `README.md`.

```sh
python3 -m unittest discover -s tests -v
python3 main.py
python3 main.py --trace
python3 main.py maps/direct.txt
python3 main.py --trace maps/unreachable.txt
```

**Exit criteria.** The tests pass, the default run prints a valid six-move detour, and the unreachable run finishes cleanly. During the demo, explain why the wall forces the detour and how the estimated moves remaining guide the search. Moving patrols and replanning follow this checkpoint.

## After the checkpoint — Add the dynamic simulation

1. Add scripted patrols to fictional grid maps. Make each tick deterministic by defining an update order. Advance patrols, update the blocked tiles, run A* from the current airman tile when the grid changes, and execute the next move.
2. Use the current tick’s grid for each search. Define outcomes for extraction, capture, an unavailable route for the current tick, and the tick limit. If a route is temporarily unavailable, wait for the next tick and retry until a terminal outcome.
3. Add fixed scenarios that demonstrate extraction, rerouting after a tile becomes blocked, temporary route loss, and timeout. Use a small terminal trace to show when the search restarts and which outcome occurred.

**Exit criteria.** The same map and patrol script produce the same trace and outcome, and a test verifies replanning from the current tile after a grid change.

## Lesson 41 — Evaluate and defend

| Experiment | Procedure | Report |
| --- | --- | --- |
| Static shortest paths | Run A* and Dijkstra on the same maps, starts, goals, and movement costs across multiple map sizes. | Verify equal optimal cost on reachable maps and agreement on unreachable maps. Compare nodes expanded and report total path cost. |
| Dynamic simulation | Run at least 100 trials across multiple map sizes using recorded maps and patrol scripts or seeds. Include corresponding stationary-patrol runs for comparison. | Report extraction rate, outcome counts, total path cost for completed runs, and nodes expanded across all replans per trial. Give the trial count for each group. |

- [ ] Define a node expansion consistently across both algorithms, such as a queue entry whose neighbors are examined after stale entries are discarded.
- [ ] Save the trial inputs, raw results, and commands needed to reproduce the tables or charts. Include a successful run and one failure case in the presentation.
- [ ] Prepare a short defense explaining the heuristic, the cost model, and the measured tradeoff between search effort and path cost. Explain that static optimality applies to each fixed grid and that future patrol changes can alter the best route.

**Exit criteria.** A teammate can reproduce a static A* versus Dijkstra comparison and a dynamic simulation result from the README. The presentation reports both sets of results and explains the simulator’s limitations.
