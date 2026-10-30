# SPDX-License-Identifier: MIT
"""Core implementation of the circular buffer.

A circular (ring) buffer stores items in a fixed-size backing list.  Two
indices walk around that list: a ``head`` that points at the slot where the
next item will be written and a ``tail`` that points at the slot from which
the next item will be read.  Because the indices wrap modulo the capacity we
never need to shift elements, which makes both :meth:`push` and
:meth:`pop` O(1).

The buffer is *not* thread-safe.  Adding a lock would make every operation
pay for synchronisation even in the common single-threaded case; callers that
share the buffer across threads are expected to wrap it in their own lock.
"""


class BufferEmpty(Exception):
    """Raised by :meth:`CircularBuffer.pop` when the buffer holds no items."""


class CircularBuffer:
    """A fixed-capacity ring buffer that overwrites oldest entries when full.

    Parameters
    ----------
    capacity:
        Maximum number of items the buffer can hold at once.  Must be a
        positive integer.

    The buffer is homogeneous only in the sense that ``pop`` returns whatever
    was most recently ``push``\ ed; mixing types is permitted but rarely
    useful.
    """

    __slots__ = ("_data", "_capacity", "_head", "_tail", "_count")

    def __init__(self, capacity):
        if not isinstance(capacity, int) or isinstance(capacity, bool):
            raise TypeError("capacity must be an int")
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self._data = [None] * capacity
        self._capacity = capacity
        # ``_head`` is the write cursor; ``_tail`` is the read cursor.
        self._head = 0
        self._tail = 0
        self._count = 0

    # ------------------------------------------------------------------ #
    # Capacity queries
    # ------------------------------------------------------------------ #

    @property
    def capacity(self):
        """Return the fixed maximum number of items the buffer can hold."""
        return self._capacity

    def __len__(self):
        """Return the number of items currently stored."""
        return self._count

    def is_empty(self):
        """Return ``True`` when the buffer holds no items."""
        return self._count == 0

    def is_full(self):
        """Return ``True`` when the buffer is at capacity.

        A full buffer is *not* an error condition: the next :meth:`push` will
        overwrite the oldest item and ``is_full`` will remain ``True``.
        """
        return self._count == self._capacity

    # ------------------------------------------------------------------ #
    # Core operations
    # ------------------------------------------------------------------ #

    def push(self, item):
        """Append *item*, overwriting the oldest entry if the buffer is full.

        Overwrite is deliberate — this is the defining behaviour of the
        library.  If you need "raise on full" semantics, check
        :meth:`is_full` first.

        Returns
        -------
        bool
            ``True`` if an item was overwritten, ``False`` otherwise.
        """
        overwrote = self._count == self._capacity
        self._data[self._head] = item
        self._head = (self._head + 1) % self._capacity
        if overwrote:
            # When full, head and tail coincide; advancing head means we must
            # also advance tail so that the oldest surviving item is still the
            # next one to be popped.
            self._tail = self._head
        else:
            self._count += 1
        return overwrote

    def pop(self):
        """Remove and return the oldest item.

        Raises
        ------
        BufferEmpty
            If the buffer holds no items.
        """
        if self._count == 0:
            raise BufferEmpty("pop from an empty buffer")
        item = self._data[self._tail]
        # Clear the slot so we do not keep a stray reference to an object the
        # caller believes they have taken ownership of.
        self._data[self._tail] = None
        self._tail = (self._tail + 1) % self._capacity
        self._count -= 1
        return item

    def peek(self):
        """Return the oldest item without removing it.

        Raises
        ------
        BufferEmpty
            If the buffer holds no items.
        """
        if self._count == 0:
            raise BufferEmpty("peek into an empty buffer")
        return self._data[self._tail]

    def to_list(self):
        """Return the buffer's contents as a list, oldest item first.

        The returned list is a fresh copy; mutating it does not affect the
        buffer.
        """
        if self._count == 0:
            return []
        out = [None] * self._count
        idx = self._tail
        for i in range(self._count):
            out[i] = self._data[idx]
            idx = (idx + 1) % self._capacity
        return out

    def clear(self):
        """Remove every item, resetting the buffer to its initial state."""
        self._data = [None] * self._capacity
        self._head = 0
        self._tail = 0
        self._count = 0
