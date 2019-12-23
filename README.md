# ra

## How to Run the Game

Currently, the game can be run using the command: `python3 ra.py`

In general, a `RaGame` instance must be initialized, then the function `start_game` function should be called from within the instance. For example, the below code initializes a two-player game between "Albert" and "Belinda":

```
game = RaGame(["Albert", "Belinda"], outfile = "game3.txt")
game.start_game()
```

## Testing TODO

Testing for the `RaGame` class and for the newer functions of the `GameState` class are still needed. Existing tests can be found in the `tests` folder, where each file is a set of tests.
