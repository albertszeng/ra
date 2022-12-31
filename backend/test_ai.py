import unittest
from unittest.mock import patch

from backend import ai, ai_names


class TestAI(unittest.TestCase):
    def test_ai_level_from_str(self) -> None:

        self.assertIsNone(ai.AILevel.from_str(None))
        self.assertIsNone(ai.AILevel.from_str("invalid"))
        self.assertEqual(ai.AILevel.from_str("easy"), ai.AILevel.EASY)
        self.assertEqual(ai.AILevel.from_str("Medium"), ai.AILevel.MEDIUM)
        self.assertEqual(ai.AILevel.from_str("haRD"), ai.AILevel.HARD)

    @patch.object(ai_names, "ALL", new=["koala"])  # pyre-ignore[56]
    def test_generate_name(self) -> None:
        self.assertEqual(ai.generate_name([]), "AI Koala")
        self.assertEqual(ai.generate_name(["AI Koala"]), "AI Koala-1")
        self.assertEqual(ai.generate_name(["AI Koala", "test"]), "AI Koala-1")
        self.assertEqual(ai.generate_name(["AI Koala", "AI Koala-1"]), "AI Koala-2")

    def test_get(self) -> None:
        self.assertSequenceEqual(
            list(ai.get().keys()), [ai.AILevel.EASY, ai.AILevel.MEDIUM, ai.AILevel.HARD]
        )
