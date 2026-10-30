# SPDX-License-Identifier: MIT
"""mini_circular_buffer: a fixed-capacity ring buffer.

This package exposes a single class, :class:`CircularBuffer`, which keeps a
fixed number of items and silently overwrites the oldest one when full.
"""

from mini_circular_buffer.core import CircularBuffer, BufferEmpty

__all__ = ["CircularBuffer", "BufferEmpty"]
