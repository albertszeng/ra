import unittest

from backend import ai_names


class TestAINames(unittest.TestCase):
    def test_available(self) -> None:
        self.assertGreater(len(ai_names.ALL), 0)
