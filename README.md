# Downed Airman: A Simulator

Downed Airman is a CS471 Python project that uses A* to find paths through a fictional 2D grid. The Lesson 36 checkpoint is a terminal demo that loads a predefined text map and prints the path and step count. The Lesson 41 evaluation compares A* with Dijkstra on static maps and measures path cost, nodes expanded, and extraction rate in reproducible dynamic simulations.

## Project Status

Repository setup and milestone planning are complete. The next checkpoint tasks are to define the text map fixtures, implement the parser and A* search, and verify the terminal demo. Add run and test commands here when the Python entry point and tests are available.

- [Project scoping worksheet](CS471%20Final%20Project%20Scoping%20Worksheet.docx)
- [Milestone plan and exit criteria](PROJECT_PLAN.md)
- [Contributor guidelines](AGENTS.md)

## Contribution Log

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
