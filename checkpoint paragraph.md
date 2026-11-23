# Downed Airman A* Simulation

**CS471 · Checkpoint 1 · Lesson 36**

## Static prototype

We built a working prototype on fixed grids to verify how A* finds the shortest path before introducing moving patrols. Each map has one start tile (`S`) and one extraction tile (`E`). The airman moves one tile at a time up, down, left, or right, and each move costs one unit. A* estimates the moves remaining by counting the horizontal and vertical distance to extraction.

## Checkpoint results

| Fixed map | Result |
| --- | --- |
| [Direct route](maps/direct.txt) | 4 moves, path cost 4 |
| [Forced detour](maps/detour.txt) | 6 moves, path cost 6 |
| [Unreachable extraction](maps/unreachable.txt) | The search ran out of tiles to check and reported no path. |

The final two lines of the detour trace show the step count and path cost.

```text
Steps: 6
Path cost: 6 (one unit per move)
```

See the [README](README.md#checkpoint-1-testing-procedure-lesson-36) for the demo commands and [project plan](PROJECT_PLAN.md) for later milestones.

## Next steps

We plan to add moving patrols and compare those runs with stationary patrol scenarios using total path cost and tiles expanded. Later iterations could let users configure the map and support multiple extraction points.

## Team contributions

Each team member contributed equally to this checkpoint.
