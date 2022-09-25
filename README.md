# ra

## How to Run the Game

Currently, the game can be run using the command: `python3 ra.py -n 2 --p1 Albert --p2 Belinda`

See `python3 ra.py -h` for more options to start the game with.

In general, a `RaGame` instance must be initialized, then the function `start_game` function should be called from within the instance. For example, the below code initializes a two-player game between "Albert" and "Belinda":

```
game = RaGame(["Albert", "Belinda"], outfile = "game3.txt")
game.start_game()
```

## Development Setup

Install `pipenv` and `pyenv`. If you already have `brew` installed, just run:

```sh
brew install pipenv pyenv
```

Once installed, initialize your local, self-contained development environment by running:

```sh
pipenv install -d
# This drops you into a shell that is running the right version of Python + required deps.
pipenv shell
```

When installing future dependencies, just make sure you use `pipenv`. For example:
```sh
pipenv install flask
```

## Testing TODO

Testing for the `RaGame` class and for the newer functions of the `GameState` class are still needed. Existing tests can be found in the `tests` folder, where each file is a set of tests.

## Specifications

Runs on Python3.8.9. Probably works on any Python3 version, but not Python2. 
