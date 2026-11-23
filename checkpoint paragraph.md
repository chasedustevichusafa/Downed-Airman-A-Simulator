For our A* Downed Airman Evasion Simulation we began by constructing an
MVP with a static domain to test the heuristic for A*. This training method
allows us to build a model that works before adding the complexity of a
dynamic map domain. Our github repo includes our current working
prototype and has a detailed read me describing the desired end state from
our current product. The current training set used a set of fixed maps for
tests against edge cases such as an unreachable goal state to see how the
model handles those types of scenarios which are more likely to occur in
our dynamic model. Our implementation of A* uses simple state
representation of the map domain with S being the start and E being the
extraction point. Our test cases only allow a single start point and end point
but further iterations could include multiple extraction points for added
complexity in the model. After the dynamic model is introduced we will test
against stationary patrol runs for efficiency of our model. We expect that
after the initial static display is confirmed and successful we can implement
dynamic arrays that allow user input to determine location and setup. Each
member of our team contributed evenly to this checkpoint.
