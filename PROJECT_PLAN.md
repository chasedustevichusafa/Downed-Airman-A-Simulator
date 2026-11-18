# Downed Airman Project Plan

The CS471 scoping worksheet defines the deliverables. The instructor’s feedback clarifies three implementation decisions. Rerun standard A* from the current tile when the grid changes, use a consistent path-cost model, and compare A* with Dijkstra on static maps. Report static shortest-path results and dynamic simulation results separately.

## Lesson 32 — Refine the scope

- [ ] Keep A* as the simulator’s core algorithm. Use Dijkstra as an evaluation baseline on static maps, implemented by running the same search with a zero heuristic.
- [ ] Agree on the initial map format. Use a rectangular text grid with `S` for start, `E` for extraction, `#` for walls, and `.` for open tiles. Require one start and one extraction tile.
- [ ] Define path cost as the sum of costs to enter each tile after the start. Start with cost 1 per move. If static maps later include weighted tiles, keep costs at least 1 so Manhattan distance remains a lower bound. Track extraction and capture as terminal game outcomes.

**Exit criteria.** Teammates can explain the grid rules, cost calculation, baseline, and when A* will be called again.

## Lesson 36 — Terminal checkpoint

1. Write the Python map parser and add three text fixtures under `maps/`. Include a direct route, a forced detour, and an unreachable extraction tile. Record the expected step count and cost for each reachable fixture.
2. Implement four-direction A* with Manhattan distance. Return the path and total cost, or a no-route result. Keep the parser, search, and terminal entry point independently testable.
3. Add a terminal command that loads a default fixture without prompting. Print the path and step count on success and a clear message when no path exists. An optional map argument can make switching fixtures during the demo easier.
4. Test bounds, walls, malformed maps, and unreachable extraction. Assert the expected cost and path validity when several equal-cost paths are possible. Add the verified run and test commands to the README.
5. Rehearse from a clean checkout. Demonstrate the forced detour, show its known step count, and run the unreachable map to show that the program exits cleanly.

**Exit criteria.** A teammate can follow the README, run the terminal demo, and verify the expected results without editing code. The checkpoint requires neither a GUI nor moving patrols.

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
