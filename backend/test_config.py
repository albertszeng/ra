import os
import unittest
from unittest.mock import patch

from backend import config


class ConfigTest(unittest.TestCase):
    def setUp(self) -> None:
        config.delete()

    @patch.dict(os.environ, {"DEBUG": "true"})
    def test_formatting(self) -> None:
        self.assertEqual(
            str(config.get()),
            "{'DEBUG': True, 'SECRET_KEY': 'debug', 'RESET_DATABASE': False}",
        )

    @patch.dict(os.environ, {})
    def test_failure(self) -> None:
        with self.assertRaises(AssertionError):
            _ = config.get()

    @patch.dict(os.environ, {"SECRET_KEY": "secret_key"})
    def test_defaults(self) -> None:
        C = config.get()
        self.assertEqual(C.DEBUG, False)
        self.assertEqual(C.RESET_DATABASE, False)
        self.assertEqual(C.SECRET_KEY, "secret_key")

    @patch.dict(os.environ, {"DEBUG": "true"})
    def test_debug(self) -> None:
        C = config.get()
        self.assertEqual(C.DEBUG, True)
        self.assertEqual(C.RESET_DATABASE, False)
        self.assertEqual(C.SECRET_KEY, "debug")

    @patch.dict(
        os.environ,
        {"SECRET_KEY": "secret_key", "DEBUG": "true", "DROP_ALL": "true"},
    )
    def test_read_env(self) -> None:
        C = config.get()
        self.assertEqual(C.DEBUG, True)
        self.assertEqual(C.RESET_DATABASE, True)
        self.assertEqual(C.SECRET_KEY, "secret_key")
