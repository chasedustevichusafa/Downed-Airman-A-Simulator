# A* desktop app implementation plan

Build and test the full Python desktop app on `codex/astar-desktop-app` for Windows, macOS, and Linux. Keep `main` as the stable Lesson 36 submission. Review the complete app and its validation results on the feature branch before deciding whether to merge.

This plan follows the [scoping worksheet](CS471%20Final%20Project%20Scoping%20Worksheet.docx), the [instructor feedback](feedback%20for%20the%20final%20project%20scoping%20worksheet.md), and the [course milestone plan](PROJECT_PLAN.md).

The desktop branch now has a static viewer with playback controls, bundled and custom maps, and a separate **Final routes** view. It draws the A* and Dijkstra routes on clean grids side by side and reports path cost and tiles expanded. The open comparison map demonstrates equal cost of eight moves with different search effort. The full map menu, dynamic simulation, experiment runner, and remaining platform checks are still planned.

## What the finished app should demonstrate

| Course goal | What a reviewer can see or reproduce |
| --- | --- |
| Lesson 36 static A* checkpoint | Open the bundled detour, watch each tile selection, and see why the shortest path takes six moves. The terminal fixture still runs without prompting. |
| Lesson 41 changing grid | Run a repeatable fictional scenario where a scripted obstacle changes the legal tiles. See the route recomputed from the current tile and the agent take its next move. |
| Instructor feedback on search | Each replan starts a fresh standard A* search on the current grid. Show when a new search starts and how many tiles it expands. |
| Instructor feedback on evaluation | Compare A* and Dijkstra on the same static inputs. Report dynamic simulation outcomes in a separate experiment using reproducible synthetic scenarios. |

## 1. Build the desktop window and map workflow

- Use Python and Tkinter for the first release. Start the app from a separate `gui.py` entry point. Keep the terminal entry point available for checkpoint grading and regression tests. Start by checking that `python3 -m tkinter` opens a test window on each target system. Document any setup needed by that system.
- Open to the bundled detour map with the grid visible and **Run**, **Step**, **Pause**, and **Reset** easy to find. Put the map selector and speed control above the grid, and the selected tile, scores, and decisions in a details panel beside it. Use the available drawing area to keep cells square and fit both tall and wide maps.
- Reuse `map_loader.py` and `map_choices.py`. Offer the direct, detour, and unreachable fixtures, the size-based menu with its five presets, a new random grid, and the dead-end maze. Add **Open text map** for custom files. Validate dimensions and map contents before replacing the current map. Show a readable error and keep the current map available if loading fails or the file picker is canceled.
- Show a legend for start, goal, walls, open cells, the selected tile, tiles waiting in the queue, tiles already checked, and the final path. Use symbols or outlines alongside color. Keep start and goal identifiable when the final path is drawn.

**Ready when:** A first-time user can launch the app, switch between the bundled maps and a rectangular preset, resize the window, and recover from a bad file.

## 2. Make the existing A* search observable

- Refactor `pathfinding.py` around an iterator that yields one structured update per selected tile. An update should include the position, moves so far, estimated moves remaining, estimated total moves, changes to the queue, and the decision for each legal neighbor. Report the final path, total cost, and expansion count on success, or an explicit no-path result on exhaustion. Keep the terminal adapter on the same search implementation.
- Preserve four-direction movement, the current tie-breaking order, legal-neighbor filtering, and unit movement costs. The remaining-moves estimate counts the horizontal and vertical distance on an open grid. When the goal is removed from the queue, its remaining estimate is zero. An unfinished route that could improve the result would still have a lower estimate in the queue.
- Count a tile as expanded when the search examines its neighbors. Exclude outdated queue entries and the goal when it ends the search before neighbor checks. Count queue entries and expansions separately so the display and experiment tables use the same definitions.
- Make **Step** show exactly one search iteration while paused. **Run** starts or resumes timed playback. **Pause** cancels the next update. **Reset** returns to the loaded map and clears the search. Changing maps cancels pending updates so a previous run cannot modify the new grid. Schedule playback with the window timer, with no waiting inside the search code.
- Show why a legal neighbor was added to the queue or skipped, and display the final cost and the shortest-path explanation beside the highlighted route. For unreachable maps, explain that the queue ran out. A speed change affects playback only. The result must agree with a fast terminal run on the same input.

**Ready when:** The detour returns six moves in both interfaces. On the 9 × 13 maze, the user can pause on a dead end, step once, and resume to the 28-move final route.

## 3. Add a deterministic dynamic simulation

Start with repeatable fictional scenarios where scripted moving obstacles change which grid cells are available. This is the proposed interpretation of the instructor’s synthetic patrol feedback. The original worksheet described sightlines, active pursuit, and separate enemy and drone behavior. The first complete app uses scripted grid pieces and tile contact for capture, with no sightline or pursuit model. Record that scope decision in the final presentation so the evaluation claims match what the simulator does.

- Give each scenario a stable name, a base map, initial obstacle positions, a per-turn movement script, and a maximum turn count. Store a seed only if generation uses randomness and record the generator settings. Bundled scenarios should include a detour, temporary loss of a route, and a case that does not reach extraction.
- On each turn, advance the scripted pieces, freeze the resulting grid, and check whether a piece occupies the agent’s tile. End in capture if it does. Otherwise, use the current route if its grid snapshot is still valid. Start a fresh A* search from the agent’s current position when the blocked tiles change or there is no reusable route. Execute only the next move on that snapshot. If no route exists, wait for the next turn. End upon extraction or at the turn limit.
- Give the display separate **Step search** and **Step turn** actions in dynamic mode. Search steps explain a single replan on a frozen grid. A turn advances the simulation once, with automatic playback showing the replan before the agent moves. Show the turn number, why the route changed, planned route, and distance actually traveled. Record a trace entry for each replan, wait, and terminal outcome.
- Use one unit of path cost per actual move. Count waits and turns separately. Track extraction, capture, and timeout as outcomes. The worksheet’s proposed negative move and failure rewards and positive extraction reward can be shown as a separate game score if needed for the defense. Keep rewards out of the A* queue and out of the reported path cost.
- Visualize what happens when the route changes after a move. Explain that A* optimizes the route on the current snapshot. Future obstacle positions can change the best route over the entire run.

**Ready when:** Replaying the same scenario produces the same positions, reroutes, costs, expansion counts, and outcome. A test confirms that a fresh search starts from the current tile after a change. The screen distinguishes waiting for a route from a finished run.

## 4. Collect and display Lesson 41 evidence

Keep the experiment runner independent of the desktop window so a teammate can repeat the results without opening it. Use the same simulation and search functions as the app. Save trial records as comma-separated values and let the app load those results for review.

| Experiment | Inputs and controls | Report |
| --- | --- | --- |
| Static shortest paths | Use the same start, goal, walls, movement costs, and tie-breaking for A* and Dijkstra. Run Dijkstra through the same search with the remaining-moves estimate set to zero. Include open maps, detours, a maze, and unreachable maps at several sizes. | Check that both searches agree on reachability and optimal cost. Compare expansions for each paired map. Report cost and expansions separately. Document any cases where the estimate gives little benefit. |
| Dynamic simulation | Run at least 100 dynamic trials across several sizes. Pair each with a stationary-obstacle run using the same base map, initial positions, and turn limit. Record the map, script or seed, and trial identifier. | Report the trial count, extraction rate, capture and timeout counts, completed-route cost, turns waited, replans, and total expansions across all searches. Show the number of successful runs used to summarize cost. |

- Compute extraction rate as successful extractions divided by all trials in the group. Count expansions across failed as well as successful searches. Record actual movement cost in every trial and report completed-route cost with its sample size so early failures do not make one group appear more efficient.
- In the app, show static and dynamic results in separate views. Give the static view a side-by-side cost and expansion comparison. Give the dynamic view outcome counts and per-size summaries, with a way to pick a saved run and replay it.
- Use fixtures with independently known answers to test correctness because A* and Dijkstra share search code. Save the exact command and inputs used to produce the results. For the defense, show the six-move checkpoint, one dynamic reroute, one failure, and one table for each experiment. Explain why equal static costs show agreement and why different expansion counts measure search effort.

**Ready when:** A teammate can regenerate both reports, verify the static cost agreement, and replay a dynamic success and failure from the recorded inputs.

## 5. Verify before proposing a merge

| Verification | Pass condition |
| --- | --- |
| Terminal regression | The existing checkpoint commands and tests still pass, including four moves, six moves, no path, and option 7 pacing. |
| Search and simulation tests | Structured updates agree with final results. Costs and expansion counts follow their definitions. Seeded or scripted runs reproduce all recorded outcomes. |
| Playback tests | Pause, single-step, speed changes, reset, and map changes behave consistently. A timer from a canceled run cannot advance another run. |
| Cross-platform test | On Windows, macOS, and Linux, record the Python and Tk versions and verify launch, file selection, resizing, timed playback, keyboard navigation, and clean close. Check 40 × 40, 40 × 5, and 5 × 40 grids. |
| Reproducibility | Run the automated checks and both experiments from a clean checkout using the README. Record the commit tested and the platform results. |

The first release runs from source. Package standalone installers after the source release has been tested if the class needs them. Prepare a feature-branch review with screenshots, a short demo recording, the evaluation results, and any platform checks still pending. Merge only after the whole app has been reviewed and the team explicitly approves bringing it into `main`.
