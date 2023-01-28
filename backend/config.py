import os
import pprint
from typing import Optional


class Config:
    DEBUG: bool
    SECRET_KEY: str
    RESET_DATABASE: bool
    RESET_USERS: bool
    RESET_GAMES: bool

    def __init__(self) -> None:
        _VALID_TRUE = ["true", "1", "t", "y", "yes"]
        self.DEBUG = os.environ.get("DEBUG", "false").lower() in _VALID_TRUE
        self.SECRET_KEY = os.environ.get("SECRET_KEY", "debug" if self.DEBUG else None)
        self.RESET_DATABASE = os.environ.get("DROP_ALL", "false").lower() in _VALID_TRUE
        self.RESET_USERS = os.environ.get("DROP_USERS", "false").lower() in _VALID_TRUE
        self.RESET_GAMES = os.environ.get("DROP_GAMES", "false").lower() in _VALID_TRUE

        assert self.SECRET_KEY is not None

    def __str__(self) -> str:
        return pprint.pformat(vars(self))


_CONFIG: Optional[Config] = None


def get() -> Config:
    """Returns the single global instace of this config"""
    global _CONFIG
    if not _CONFIG:
        _CONFIG = Config()
    return _CONFIG


def delete() -> None:
    """Clears the global config."""
    global _CONFIG
    _CONFIG = None
