import os
import unittest
from unittest.mock import patch

from backend import config


class ConfigTest(unittest.TestCase):
    def setUp(self) -> None:
        config.delete()

    @patch.dict(os.environ, {"DEBUG": "true"}, clear=True)
    def test_formatting(self) -> None:
        self.assertEqual(
            str(config.get()),
            """{'DEBUG': True,
 'RESET_DATABASE': False,
 'RESET_GAMES': False,
 'RESET_USERS': False,
 'SECRET_KEY': 'debug'}""",
        )

    @patch.dict(os.environ, {}, clear=True)
    def test_failure(self) -> None:
        with self.assertRaises(AssertionError):
            _ = config.get()

    @patch.dict(os.environ, {"SECRET_KEY": "secret_key"}, clear=True)
    def test_defaults(self) -> None:
        C = config.get()
        self.assertEqual(C.DEBUG, False)
        self.assertEqual(C.RESET_DATABASE, False)
        self.assertEqual(C.RESET_GAMES, False)
        self.assertEqual(C.RESET_USERS, False)
        self.assertEqual(C.SECRET_KEY, "secret_key")

    @patch.dict(os.environ, {"DEBUG": "true"}, clear=True)
    def test_debug(self) -> None:
        C = config.get()
        self.assertEqual(C.DEBUG, True)
        self.assertEqual(C.RESET_DATABASE, False)
        self.assertEqual(C.RESET_GAMES, False)
        self.assertEqual(C.RESET_USERS, False)
        self.assertEqual(C.SECRET_KEY, "debug")

    @patch.dict(
        os.environ,
        {
            "SECRET_KEY": "secret_key",
            "DEBUG": "true",
            "DROP_ALL": "false",
            "DROP_GAMES": "true",
            "DROP_USERS": "yes",
        },
        clear=True,
    )
    def test_read_env(self) -> None:
        C = config.get()
        self.assertEqual(C.DEBUG, True)
        self.assertEqual(C.RESET_DATABASE, False)
        self.assertEqual(C.RESET_GAMES, True)
        self.assertEqual(C.RESET_USERS, True)
        self.assertEqual(C.SECRET_KEY, "secret_key")
