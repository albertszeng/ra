import unittest

from game import encoding


class EncodingTest(unittest.TestCase):
    def test_compress_fails(self) -> None:
        with self.assertRaises(ValueError):
            encoding.compress((1.0, 2.0, 3.0, 4.0, 5.0, 6.0))

    def test_compress(self) -> None:
        self.assertEqual(
            325848187306968940035072, encoding.compress((1.0, 2.0, 3.0, 4.0, 5.0))
        )

    def test_decompress(self) -> None:
        self.assertEqual(
            (1.0, 2.0, 3.0, 4.0, 5.0), encoding.decompress(325848187306968940035072)
        )

    def test_compress_and_decompress(self) -> None:
        def id_fn(x):
            return encoding.decompress(encoding.compress(x))

        self.assertEqual((1.0, 0.0, 0.0, 0.0, 0.0), id_fn((1.0,)))
        self.assertEqual((2.0, 3.0, 0.0, 0.0, 0.0), id_fn((2.0, 3.0)))
        self.assertEqual((4.0, 5.0, 6.0, 0.0, 0.0), id_fn((4.0, 5.0, 6.0)))
        self.assertEqual((7.0, 8.0, 9.0, 10.0, 0.0), id_fn((7.0, 8.0, 9.0, 10.0)))
