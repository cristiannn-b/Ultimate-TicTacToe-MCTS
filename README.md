# P2: TTT MCTS

## Authors
Cristian Barragan (cbarrag2) and Chloe Liang (cliang53)

## Description
This project revolves around a collection of bots with the ability to play Ultimate Tic-Tac-Toe. The game itself, as well as two of the bots, were provided to us. Our objective, however, was to implement two more bots, each better than the other, *hopefully*. Both bots required us to implement a Monte Carlo Tree Search as the algorithm used to play the game. This involved building up each of the sub-algorithms for MCTS (Selection, Expansion, Simulation, and Backpropagation) and to, ultimately, combine them all to build a bot that played the game better than the two provided bots. The second bot we implemented was a copy of the first, but with a heuristic rollout strategy in the rollout phase rather than a random simulation.

## Who Did What?
#### Cristian Barragan (cbarrag2)
~~~
- Implemented the intitial MCTS bot, mcts_vanilla.py, and its functions and algorithms
- Ran Experiment 1 (and some of 2, for the sake of time)
- Did Experiment 1 write-up
~~~

#### Chloe Liang (cliang53)
~~~
- Designed and implemented a series of heuristic tests used in the rollout portion of the mcts_modified.py bot
- Ran most of Experiment 2
- Did Experiment 2 write-up
~~~