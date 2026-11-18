# Repository Guidelines

## Project Scope

Downed Airman is a CS471 Python simulation game. The airman moves up, down, left, or right on a fictional 2D grid with blocked cells, simulated patrols, and an extraction tile. A* is the single core course algorithm. Use the [project scoping worksheet](CS471%20Final%20Project%20Scoping%20Worksheet.docx) as the reference for milestones and evaluation criteria.

## Project Structure & Local Development

The repository currently contains the worksheet and this guide. As implementation begins, keep map parsing, A* search, and simulation rules independently testable. Store predefined text maps separately from Python code and document the map symbols in the README. Use four spaces for indentation, `snake_case` for Python functions and modules, and descriptive names for map fixtures and tests.

The Lesson 36 checkpoint runs from a terminal, reads a predefined text map without prompting, and prints the path and step count. A GUI is optional. Add the exact Python run and test commands to the README once the entry point and test runner exist.

## Testing & Evaluation

Use small maps with known answers to verify path cost, blocked cells, and unreachable goals. Record the expected path cost and step count for each fixture. When dynamic patrols are added, use fixed scenarios or seeds so contributors can reproduce failures.

For Lesson 41, report total path cost as the primary metric and track nodes expanded to assess heuristic efficiency. Compare static and dynamic patrol scenarios across different map sizes over 100 or more simulations. Record the maps and settings used so teammates can repeat the evaluation and explain the algorithm and results during the defense.

## Commits & Pull Requests

Use short, imperative commit subjects, such as `Add text map parser`. Keep pull requests focused and describe what changed, why, and how it was verified. Link related issues when available. Include sample terminal output for changes to the checkpoint or a screenshot for visible interface changes.
