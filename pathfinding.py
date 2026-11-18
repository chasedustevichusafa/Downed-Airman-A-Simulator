"""A* shortest-path search on a static, four-direction grid."""

from heapq import heappop, heappush
from typing import List, Optional, Tuple

from map_loader import GridMap, Position


ORTHOGONAL_MOVES = ((-1, 0), (1, 0), (0, -1), (0, 1))


def manhattan_distance(position: Position, goal: Position) -> int:
    """Return the minimum moves required if all tiles were open."""
    return abs(position[0] - goal[0]) + abs(position[1] - goal[1])


def find_path(grid: GridMap) -> Optional[Tuple[List[Position], int]]:
    """Return the optimal path (including both endpoints) and its cost, or None.

    The priority of a queued route is f = g + h. The value g is the number
    of moves already made and h is the Manhattan distance still remaining.
    Each move changes one coordinate by one and costs one. Thus h can never
    overestimate the remaining cost. Walls can force extra moves.
    """
    start, goal = grid.start, grid.goal

    # 1. Initialize the frontier with the start. Heap entries are (f, g, tile).
    #    The start has g = 0 because we have yet to make a move. The heap
    #    breaks equal-f ties using g and then the tile coordinates.
    frontier = [(manhattan_distance(start, goal), 0, start)]
    best_cost = {start: 0}
    predecessor = {}

    while frontier:
        # 2. Take the route with the smallest estimated total cost. A cheaper
        #    route to this tile may have been queued since this entry was added.
        #    Keep the heap simple by leaving older entries in it and skipping
        #    them when popped.
        _, current_cost, current = heappop(frontier)
        if current_cost != best_cost[current]:
            continue

        # 3. Stop when the goal is popped. At the goal h = 0, so its priority
        #    equals its actual cost. Any cheaper unfinished route would have
        #    had a smaller f somewhere on the frontier and been considered
        #    first. Follow the recorded predecessors back to the start.
        if current == goal:
            path = [goal]
            while path[-1] != start:
                path.append(predecessor[path[-1]])
            path.reverse()
            return path, current_cost

        # 4. Expand the four legal directions. Record and queue a neighbor
        #    only when this route improves its best known cost. Update the
        #    predecessor at the same time so reconstruction follows that route.
        row, column = current
        for row_delta, column_delta in ORTHOGONAL_MOVES:
            neighbor = (row + row_delta, column + column_delta)
            if not grid.is_walkable(neighbor):
                continue

            candidate_cost = current_cost + 1
            previous_cost = best_cost.get(neighbor)
            if previous_cost is not None and candidate_cost >= previous_cost:
                continue

            best_cost[neighbor] = candidate_cost
            predecessor[neighbor] = current
            priority = candidate_cost + manhattan_distance(neighbor, goal)
            heappush(frontier, (priority, candidate_cost, neighbor))

    # 5. The frontier is empty. Every reachable tile has been considered,
    #    so the goal cannot be reached on this grid.
    return None
