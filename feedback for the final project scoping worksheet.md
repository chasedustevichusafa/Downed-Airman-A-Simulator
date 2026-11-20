Operational Problem 5/5

Environment Model 5/5

Core Algorithm 4/5

Checkpoint Baseline 5/5

Evaluation Plan 4.5/5



Strong project design with a clearly defined simulation, an appropriate A* implementation, and a realistic terminal-based checkpoint. Your proposed evaluation metrics of path cost, nodes expanded, and completion rate are meaningful. The main technical clarification concerns how standard A* handles changes in the environment.



Standard A* does not automatically update an existing search when obstacles change. For this project, rerunning A* from the current position is a reasonable approach. Define a consistent path-cost function and include a comparison baseline, such as Dijkstra's algorithm, for static pathfinding experiments. Evaluate static shortest-path performance separately from performance in a dynamic simulation using synthetic patrol behavior.