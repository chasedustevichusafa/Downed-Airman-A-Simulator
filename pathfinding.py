"""A* shortest-path search on a static, four-direction grid."""

from heapq import heappop, heappush
from typing import Callable, List, Optional, Set, Tuple

from map_loader import GridMap, Position


ORTHOGONAL_MOVES = ((-1, 0), (1, 0), (0, -1), (0, 1))


def h(position: Position, goal: Position) -> int:
    """Return the minimum moves required if all tiles were open."""
    return abs(position[0] - goal[0]) + abs(position[1] - goal[1])


def _draw_search(
    grid: GridMap, current: Position, queued: Set[Position], expanded: Set[Position]
) -> str:
    """Draw a snapshot just after the current tile leaves the frontier."""
    marks = dict.fromkeys(expanded, "x")
    marks.update(dict.fromkeys(queued, "o"))
    marks[current] = "@"
    return "\n".join(
        "".join(marks.get((row, column), tile) for column, tile in enumerate(line))
        for row, line in enumerate(grid.rows)
    )


def find_path(
    grid: GridMap, *, trace: Optional[Callable[[str], None]] = None
) -> Optional[Tuple[List[Position], int]]:
    """Return the optimal path (including both endpoints) and its cost, or None.

    The priority of a queued route is f = g + h. The value g is the number
    of moves already made and h is the number of moves remaining on an open grid.
    Each move changes one coordinate by one and costs one. Thus h can never
    overestimate the remaining cost. Walls can force extra moves.

    Pass a trace callback to display the actual decisions made by this search.
    """
    start, goal = grid.start, grid.goal

    # 1. Initialize the frontier with the start. Heap entries are (f, g, tile).
    #    The start has g = 0 because we have yet to make a move. The heap
    #    breaks equal-f ties using g and then the tile coordinates.
    frontier = [(h(start, goal), 0, start)]
    best_cost = {start: 0}
    predecessor = {}
    expanded = set()
    if trace is not None:
        trace("A* picks the lowest f = g + h. The value h counts moves to the goal on an open grid.")
        trace("Map: @ current, o queued, x expanded, S start, E goal, # wall.")

    while frontier:
        # 2. Take the route with the smallest estimated total cost. A cheaper
        #    route to this tile may have been queued since this entry was added.
        #    Keep the heap simple by leaving older entries in it and skipping
        #    them when popped.
        current_priority, current_cost, current = heappop(frontier)
        if current_cost != best_cost[current]:
            if trace is not None:
                trace(f"Skip stale entry {current}: g={current_cost}, best g={best_cost[current]}.")
            continue

        if trace is not None:
            # The heap can contain stale entries. Filter them before drawing
            # the frontier or reporting its best remaining lower bound.
            pending = {
                tile: priority for priority, cost, tile in frontier
                if cost == best_cost[tile]
            }
            trace(
                f"\nPop {current}: g={current_cost}, h={current_priority - current_cost}, "
                f"f={current_priority} (lowest queued f)"
            )
            trace(_draw_search(grid, current, set(pending), expanded))

        # 3. Stop when the goal is popped. At the goal h = 0, so its priority
        #    equals its actual cost. Any cheaper unfinished route would have
        #    had a smaller f somewhere on the frontier and been considered
        #    first. Follow the recorded predecessors back to the start.
        if current == goal:
            if trace is not None:
                remaining_bound = min(pending.values(), default=None)
                if remaining_bound is None:
                    trace("Frontier is empty after removing the goal.")
                else:
                    trace(f"Lowest remaining frontier f: {remaining_bound}.")
                trace(
                    f"Optimality check: goal h=0, so its f equals its cost ({current_cost}). "
                    "Any cheaper route would still have a frontier tile with a lower f "
                    "because h is a lower bound."
                )
            path = [goal]
            while path[-1] != start:
                path.append(predecessor[path[-1]])
            path.reverse()
            return path, current_cost

        # 4. Expand the four legal directions. Record and queue a neighbor
        #    only when this route improves its best known cost. Update the
        #    predecessor at the same time so reconstruction follows that route.
        if trace is not None:
            expanded.add(current)
        row, column = current
        for row_delta, column_delta in ORTHOGONAL_MOVES:
            neighbor = (row + row_delta, column + column_delta)
            if not grid.is_walkable(neighbor):
                if trace is not None:
                    trace(f"  {neighbor}: blocked or outside the grid")
                continue

            candidate_cost = current_cost + 1
            previous_cost = best_cost.get(neighbor)
            if previous_cost is not None and candidate_cost >= previous_cost:
                if trace is not None:
                    trace(f"  {neighbor}: skip g={candidate_cost}; already have g={previous_cost}")
                continue

            best_cost[neighbor] = candidate_cost
            predecessor[neighbor] = current
            estimate = h(neighbor, goal)
            priority = candidate_cost + estimate
            heappush(frontier, (priority, candidate_cost, neighbor))
            if trace is not None:
                trace(f"  {neighbor}: queue g={candidate_cost}, h={estimate}, f={priority}")

    # 5. The frontier is empty. Every reachable tile has been considered,
    #    so the goal cannot be reached on this grid.
    if trace is not None:
        trace("\nFrontier exhausted before reaching the goal.")
    return None
