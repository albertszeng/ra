# ra

## How to Run the Game

Currently, the game can be run using the command: `python3 ra.py -n 2 --p1 Albert --p2 Belinda`

See `python3 ra.py -h` for more options to start the game with.

In general, a `RaGame` instance must be initialized, then the function `start_game` function should be called from within the instance. For example, the below code initializes a two-player game between "Albert" and "Belinda":

```
game = RaGame(["Albert", "Belinda"], outfile = "game3.txt")
game.start_game()
```

## Python Requirements

### `pipenv` and `pyenv`

As of the latest update, we recommend leveraging `pipenv` and `pyenv` to maintain a hermetic static for dependencies. The other options are left here only for reference as they are not maintained/tested often.

On Mac, make sure you have [Homebrew](https://brew.sh/) installed. You can install `pipenv` and `pyenv` with:

```sh
brew install pipenv
brew install pyenv
````

After installing, you navigate to the root of the project directory, and run:

```sh
pipenv install
```

This will install all the required dependencies as well as the appropriate Python version (using pyenv). You can then run:

```sh
pipenv shell
````

When installing future dependencies, just make sure you use `pipenv`. For example:
```sh
pipenv install flask
```

## Type Checking

For development purposes, you want to also install the dev dependencies by running `pipenv install -d`. For type-checking, we use `pyre`. See [here](https://pyre-check.org/docs/getting-started/) to install.

You should be able to type check by running:

```sh
# Assumes you're in the right shell.
pyre
```

## Testing TODO

Testing for the `RaGame` class and for the newer functions of the `GameState` class are still needed. Existing tests can be found in the `tests` folder, where each file is a set of tests.

We use the `unittest` framework. To run the tests, run:

```sh
python -m unittest
```

Note that above automatically runs all tests found in `test_*.py` files.

## Specifications

Runs on Python3.8.9. Probably works on any Python3 version, but not Python2. 
