"""A* shortest-path search on a static, four-direction grid."""

from dataclasses import dataclass
from heapq import heappop, heappush
from typing import Callable, Iterator, List, Optional, Set, Tuple, Union

from map_loader import GridMap, Position


@dataclass(frozen=True)
class SearchIteration:
    """One selected tile and the changes the search made to the queue."""

    selected: Position
    moves_so_far: int
    estimated_moves_remaining: int
    newly_queued: Tuple[Position, ...]


@dataclass(frozen=True)
class SearchResult:
    """The final route, or no route, and the number of tiles expanded."""

    path: Optional[Tuple[Position, ...]]
    cost: Optional[int]
    tiles_expanded: int


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
        " ".join(
            format_tile(marks.get((row, column), tile))
            for column, tile in enumerate(line)
        )
        for row, line in enumerate(grid.rows)
    )


def search_steps(
    grid: GridMap,
    *,
    estimate: Callable[[Position, Position], int] = estimate_remaining_moves,
    trace: Optional[Callable[[str], None]] = None,
    format_tile: Callable[[str], str] = str,
) -> Iterator[Union[SearchIteration, SearchResult]]:
    """Yield selected tiles followed by one final shortest-path result.

    Moves so far is the length of the best route found to a tile.
    A* estimates remaining moves from the open-grid distance. Each move
    changes one coordinate by one, and walls can only add moves, so this
    estimate never exceeds the actual moves still needed. Setting the
    estimate to zero ranks tiles by moves so far, as in Dijkstra's algorithm.
    Estimated total moves adds those two values to rank routes in the queue.

    The optional terminal trace formats decisions made by this same search.
    """
    start, goal = grid.start, grid.goal

    # 1. Put the start in the frontier, the queue of tiles awaiting a check.
    #    Each entry stores estimated total moves, moves so far, and the tile.
    #    The start takes zero moves. When total estimates tie, the queue
    #    orders entries by fewer moves so far, then by row and column.
    frontier = [(estimate(start, goal), 0, start)]
    best_cost = {start: 0}
    predecessor = {}
    expanded = set()
    tiles_expanded = 0
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
            yield SearchIteration(current, current_cost, 0, ())
            yield SearchResult(tuple(path), current_cost, tiles_expanded)
            return

        # 4. Consider only destinations the map allows. Record and queue a neighbor
        #    only when this route improves its best known cost. Update the
        #    predecessor at the same time so reconstruction follows that route.
        if trace is not None:
            expanded.add(current)
        # Count only tiles whose neighbors are actually examined.
        tiles_expanded += 1
        newly_queued = []
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
            remaining_moves = estimate(neighbor, goal)
            priority = candidate_cost + remaining_moves
            heappush(frontier, (priority, candidate_cost, neighbor))
            newly_queued.append(neighbor)
            if trace is not None:
                trace(
                    f"  {neighbor}: add to queue (moves so far: {candidate_cost}, "
                    f"estimated moves remaining: {remaining_moves}, "
                    f"estimated total moves: {priority})."
                )
        yield SearchIteration(
            current, current_cost, current_priority - current_cost, tuple(newly_queued)
        )

    # 5. The frontier is empty. Every reachable tile has been considered,
    #    so the goal cannot be reached on this grid.
    if trace is not None:
        trace("\nFrontier exhausted before reaching the goal.")
    yield SearchResult(None, None, tiles_expanded)


def dijkstra_result(grid: GridMap) -> SearchResult:
    """Get the static comparison result using the same queue and move costs."""
    for event in search_steps(grid, estimate=lambda position, goal: 0):
        if isinstance(event, SearchResult):
            return event
    raise RuntimeError("The search ended without reporting a result.")


def find_path(
    grid: GridMap,
    *,
    trace: Optional[Callable[[str], None]] = None,
    format_tile: Callable[[str], str] = str,
    after_iteration: Optional[Callable[[], None]] = None,
) -> Optional[Tuple[List[Position], int]]:
    """Return the route and cost for the existing terminal interface."""
    for event in search_steps(grid, trace=trace, format_tile=format_tile):
        if isinstance(event, SearchResult):
            if event.path is None or event.cost is None:
                return None
            return list(event.path), event.cost
        if after_iteration is not None:
            after_iteration()
    return None
