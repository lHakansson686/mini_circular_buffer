# SPDX-License-Identifier: MIT
"""Unit tests for mini_circular_buffer.core.

Run with::

    PYTHONPATH=src python -m unittest discover -s tests
"""

import unittest

from mini_circular_buffer import CircularBuffer, BufferEmpty


class TestConstruction(unittest.TestCase):

    def test_default_state_is_empty(self):
        buf = CircularBuffer(3)
        self.assertEqual(len(buf), 0)
        self.assertTrue(buf.is_empty())
        self.assertFalse(buf.is_full())
        self.assertEqual(buf.capacity, 3)
        self.assertEqual(buf.to_list(), [])

    def test_capacity_must_be_positive(self):
        with self.assertRaises(ValueError):
            CircularBuffer(0)
        with self.assertRaises(ValueError):
            CircularBuffer(-1)

    def test_capacity_must_be_int(self):
        with self.assertRaises(TypeError):
            CircularBuffer("three")
        with self.assertRaises(TypeError):
            CircularBuffer(3.0)
        # bool is a subclass of int but is not a meaningful capacity
        with self.assertRaises(TypeError):
            CircularBuffer(True)


class TestPushPop(unittest.TestCase):

    def test_push_then_pop_returns_fifo_order(self):
        buf = CircularBuffer(3)
        buf.push("a")
        buf.push("b")
        buf.push("c")
        self.assertEqual(buf.pop(), "a")
        self.assertEqual(buf.pop(), "b")
        self.assertEqual(buf.pop(), "c")
        self.assertTrue(buf.is_empty())

    def test_push_returns_overwrite_flag(self):
        buf = CircularBuffer(2)
        self.assertFalse(buf.push("a"))
        self.assertFalse(buf.push("b"))
        # Buffer is now full; next push overwrites "a".
        self.assertTrue(buf.push("c"))

    def test_pop_when_empty_raises(self):
        buf = CircularBuffer(2)
        with self.assertRaises(BufferEmpty):
            buf.pop()

    def test_peek_returns_oldest_without_removing(self):
        buf = CircularBuffer(2)
        buf.push("a")
        buf.push("b")
        self.assertEqual(buf.peek(), "a")
        self.assertEqual(len(buf), 2)
        self.assertEqual(buf.pop(), "a")
        self.assertEqual(buf.peek(), "b")

    def test_peek_when_empty_raises(self):
        buf = CircularBuffer(2)
        with self.assertRaises(BufferEmpty):
            buf.peek()


class TestOverwrite(unittest.TestCase):

    def test_overwrite_drops_oldest(self):
        buf = CircularBuffer(3)
        for ch in "abc":
            buf.push(ch)
        self.assertTrue(buf.is_full())
        buf.push("d")  # overwrites "a"
        buf.push("e")  # overwrites "b"
        self.assertEqual(buf.to_list(), ["c", "d", "e"])
        self.assertEqual(buf.pop(), "c")
        self.assertEqual(buf.pop(), "d")
        self.assertEqual(buf.pop(), "e")

    def test_overwrite_after_partial_drain(self):
        buf = CircularBuffer(3)
        for ch in "abc":
            buf.push(ch)
        self.assertEqual(buf.pop(), "a")  # free one slot
        buf.push("d")
        self.assertEqual(buf.to_list(), ["b", "c", "d"])
        self.assertEqual(len(buf), 3)


class TestToList(unittest.TestCase):

    def test_to_list_is_a_copy(self):
        buf = CircularBuffer(3)
        buf.push(1)
        buf.push(2)
        snapshot = buf.to_list()
        snapshot.append(99)
        self.assertEqual(buf.to_list(), [1, 2])

    def test_to_list_after_wraparound(self):
        buf = CircularBuffer(3)
        for ch in "abcde":
            buf.push(ch)
        self.assertEqual(buf.to_list(), ["c", "d", "e"])


class TestClear(unittest.TestCase):

    def test_clear_resets_state(self):
        buf = CircularBuffer(3)
        for ch in "abc":
            buf.push(ch)
        buf.clear()
        self.assertEqual(len(buf), 0)
        self.assertTrue(buf.is_empty())
        self.assertFalse(buf.is_full())
        self.assertEqual(buf.to_list(), [])
        # Buffer must still be usable after clear.
        buf.push("x")
        self.assertEqual(buf.pop(), "x")


class TestEdgeCases(unittest.TestCase):

    def test_capacity_one(self):
        buf = CircularBuffer(1)
        self.assertFalse(buf.push("a"))
        self.assertEqual(buf.pop(), "a")
        self.assertFalse(buf.push("b"))  # buffer was empty, no overwrite
        self.assertTrue(buf.push("c"))  # overwrites "b"
        self.assertEqual(buf.pop(), "c")

    def test_interleaved_push_pop(self):
        buf = CircularBuffer(2)
        buf.push(1)
        buf.push(2)
        self.assertEqual(buf.pop(), 1)
        buf.push(3)
        self.assertEqual(buf.pop(), 2)
        self.assertEqual(buf.pop(), 3)
        with self.assertRaises(BufferEmpty):
            buf.pop()

    def test_none_is_a_valid_value(self):
        buf = CircularBuffer(2)
        buf.push(None)
        self.assertEqual(len(buf), 1)
        self.assertIsNone(buf.peek())
        self.assertIsNone(buf.pop())
        self.assertTrue(buf.is_empty())


if __name__ == "__main__":
    unittest.main()
