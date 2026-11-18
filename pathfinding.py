"""A* shortest-path search on a static, four-direction grid."""

from heapq import heappop, heappush
from typing import Callable, List, Optional, Set, Tuple

from map_loader import GridMap, Position


def estimate_remaining_moves(position: Position, goal: Position) -> int:
    """Return the minimum moves required if all tiles were open."""
    return abs(position[0] - goal[0]) + abs(position[1] - goal[1])


def _draw_search(
    grid: GridMap,
    current: Position,
    queued: Set[Position],
    expanded: Set[Position],
    format_tile: Callable[[str], str],
) -> str:
    """Draw a snapshot just after the current tile leaves the frontier."""
    marks = dict.fromkeys(expanded, "x")
    marks.update(dict.fromkeys(queued, "o"))
    marks[current] = "@"
    return "\n".join(
        "".join(
            format_tile(marks.get((row, column), tile))
            for column, tile in enumerate(line)
        )
        for row, line in enumerate(grid.rows)
    )


def find_path(
    grid: GridMap,
    *,
    trace: Optional[Callable[[str], None]] = None,
    format_tile: Callable[[str], str] = str,
) -> Optional[Tuple[List[Position], int]]:
    """Return the optimal path (including both endpoints) and its cost, or None.

    Moves so far is the length of the best route found to a tile.
    Estimated moves remaining counts the row and column differences to the
    goal. Each move changes one coordinate by one, and walls can only add
    moves, so the estimate never exceeds the actual moves still needed.
    Estimated total moves adds those two values to rank routes in the queue.

    Pass a trace callback to receive each message describing the search.
    The tile formatter controls how the trace displays each map symbol.
    """
    start, goal = grid.start, grid.goal

    # 1. Put the start in the frontier, the queue of tiles awaiting a check.
    #    Each entry stores estimated total moves, moves so far, and the tile.
    #    The start takes zero moves. When total estimates tie, the queue
    #    orders entries by fewer moves so far, then by row and column.
    frontier = [(estimate_remaining_moves(start, goal), 0, start)]
    best_cost = {start: 0}
    predecessor = {}
    expanded = set()
    if trace is not None:
        trace("Moves so far: moves in the recorded route from the start to this tile.")
        trace("Estimated moves remaining: add how many rows and columns separate the tile from the goal.")
        trace("Estimated total moves: moves so far plus estimated moves remaining.")
        trace("A* selects the tile with the lowest estimated total moves.")
        trace("The frontier is the queue of tiles waiting to be checked.")
        trace(
            f"Search markers: {format_tile('@')} selected tile, "
            f"{format_tile('o')} waiting in the queue, "
            f"{format_tile('x')} neighbors already checked."
        )

    while frontier:
        # 2. Take the route with the smallest estimated total cost. A cheaper
        #    route to this tile may have been queued since this entry was added.
        #    Keep the heap simple by leaving older entries in it and skipping
        #    them when popped.
        current_priority, current_cost, current = heappop(frontier)
        if current_cost != best_cost[current]:
            if trace is not None:
                trace(
                    f"Skip outdated entry for {current}: this route takes {current_cost} moves. "
                    f"A route with {best_cost[current]} moves is already recorded."
                )
            continue

        if trace is not None:
            # The heap can contain stale entries. Filter them before drawing
            # the frontier or reporting its best remaining lower bound.
            pending = {
                tile: priority for priority, cost, tile in frontier
                if cost == best_cost[tile]
            }
            trace(
                f"\nSelect {current} from the queue (lowest estimated total moves).\n"
                f"  Moves so far: {current_cost}\n"
                f"  Estimated moves remaining: {current_priority - current_cost}\n"
                f"  Estimated total moves: {current_priority}"
            )
            trace(_draw_search(grid, current, set(pending), expanded, format_tile))

        # 3. Stop when the goal is removed from the queue. The goal has zero
        #    moves remaining, so its estimate is its actual route length.
        #    A shorter route would still have a tile with a lower estimate
        #    in the queue. Follow the recorded previous tiles to the start.
        if current == goal:
            if trace is not None:
                remaining_bound = min(pending.values(), default=None)
                if remaining_bound is None:
                    trace("Frontier is empty after removing the goal.")
                else:
                    trace(f"Lowest estimated total among remaining routes: {remaining_bound} moves.")
                trace(
                    f"Shortest-path check: the goal has zero moves remaining, so its "
                    f"estimated total is its actual route length of {current_cost} moves. "
                    "The remaining-moves estimate ignores walls and never overestimates. "
                    "A shorter route would still have a tile with a lower estimate in the queue."
                )
            path = [goal]
            while path[-1] != start:
                path.append(predecessor[path[-1]])
            path.reverse()
            return path, current_cost

        # 4. Consider only destinations the map allows. Record and queue a neighbor
        #    only when this route improves its best known cost. Update the
        #    predecessor at the same time so reconstruction follows that route.
        if trace is not None:
            expanded.add(current)
        for neighbor in grid.walkable_neighbors(current):
            candidate_cost = current_cost + 1
            previous_cost = best_cost.get(neighbor)
            if previous_cost is not None and candidate_cost >= previous_cost:
                if trace is not None:
                    trace(
                        f"  {neighbor}: skip route with {candidate_cost} moves. "
                        f"Already recorded {previous_cost} moves."
                    )
                continue

            best_cost[neighbor] = candidate_cost
            predecessor[neighbor] = current
            remaining_moves = estimate_remaining_moves(neighbor, goal)
            priority = candidate_cost + remaining_moves
            heappush(frontier, (priority, candidate_cost, neighbor))
            if trace is not None:
                trace(
                    f"  {neighbor}: add to queue (moves so far: {candidate_cost}, "
                    f"estimated moves remaining: {remaining_moves}, "
                    f"estimated total moves: {priority})."
                )

    # 5. The frontier is empty. Every reachable tile has been considered,
    #    so the goal cannot be reached on this grid.
    if trace is not None:
        trace("\nFrontier exhausted before reaching the goal.")
    return None
