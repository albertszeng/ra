import os
from typing import Optional


class Config:
    DEBUG: bool
    SECRET_KEY: str
    RESET_DATABASE: bool

    def __init__(self) -> None:
        self.DEBUG = bool(os.environ.get("DEBUG", False))
        self.SECRET_KEY = os.environ.get("SECRET_KEY", "debug" if self.DEBUG else "")
        self.RESET_DATABASE = bool(os.environ.get("DROP_ALL", False))

        assert self.SECRET_KEY

    def __str__(self) -> str:
        return str(vars(self))


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
