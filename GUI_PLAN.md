# Cross-platform A* desktop app plan

Build a Python desktop app for Windows, macOS, and Linux that lets someone choose a map, run A*, and see why it selects each tile and when it has found the shortest path. Develop and test the app on `codex/astar-desktop-app` before proposing a merge into `main`.

## 1. Set up the desktop entry point

- Use Python’s Tkinter toolkit for the window, controls, and drawing area. Give the app its own entry point, `python3 gui.py`, and keep the terminal checkpoint available through `main.py`.
- Start with a resizable window. Put map selection and playback controls above the grid. Use a details panel for the selected tile, its scores, and the neighbor decisions. Keep the grid cells square as the window resizes, including on rectangular maps.
- Test `python3 -m tkinter` on each target platform before building the interface. Document the Python command and any Tk installation steps needed on each platform.

**Checkpoint.** The window opens and renders the bundled detour map with a readable legend.

## 2. Share the existing A* search with the app

- Refactor `pathfinding.py` to expose one iteration at a time as structured Python data. Each iteration should report the selected position, its three scores, tiles added to the queue, and rejected routes to legal neighbors that already have an equal or better cost. Report a final path and cost or a no-path result when the queue runs out.
- Adapt the current terminal trace to the same search. Preserve the existing find-path entry point, termination rule, path reconstruction, and option 7 pacing. Keep interface drawing and timing out of the search algorithm.
- Reuse `map_loader.py` and `map_choices.py` for file validation, dimensions, presets, random map history, and the dead-end maze.

**Checkpoint.** The same inputs return the same route and cost through both interfaces, and the existing terminal tests pass.

## 3. Add map selection and playback

- Offer the bundled maps, the size and layout menu, and a file picker for custom text maps. Show the starting grid and map legend as soon as a map loads. Display validation errors in the window and let the user recover by choosing another map.
- Add **Run**, **Pause**, **Step**, and **Reset** controls plus a speed selector. A step advances one displayed search iteration. Reset or a map change cancels pending playback before clearing the grid. Use the window’s timer to schedule updates so the controls stay responsive.
- Distinguish open tiles, walls, start, goal, selected tiles, queued tiles, checked tiles, and the final path. Pair color with symbols or outlines. Spell out **moves so far**, **estimated moves remaining**, and **estimated total moves**. On completion, highlight the route and explain the shortest-path check or why no route was found.

**Checkpoint.** A first-time user can load the dead-end maze, pause on a branch, advance one iteration, resume, and identify the final route.

## 4. Verify the app before merging

| Check | Expected result |
| --- | --- |
| Bundled direct, detour, and unreachable maps | Four moves, six moves, and a clear no-path result, respectively |
| Dead-end maze at 9 rows by 13 columns | The trace shows four dead ends and highlights the final 28-move path |
| Pause, step, reset, and map changes | Playback pauses promptly, one step updates one iteration, and events from a prior run never alter the new map |
| Large and rectangular grids | A 40 × 40 grid and both 40 × 5 orientations remain readable, with square cells and responsive controls |
| Windows, macOS, and Linux | Launch, open a text map, play and pause a search, resize, and close cleanly |

- Cover iteration data and playback state with automated tests that run without opening a window. Keep the existing terminal suite in the regression check.
- Add a README launch guide and record the Python version, operating system, and smoke-test results for each platform. The first release should run from source. Decide whether to build standalone installers after the app passes the platform checks.
- Open a pull request from `codex/astar-desktop-app` when the checks pass. Include screenshots or a short recording of the maze, the platform results, and the test command. Review the complete app on that branch before merging.
