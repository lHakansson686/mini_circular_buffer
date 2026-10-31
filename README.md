# mini_circular_buffer

A fixed-capacity ring buffer that overwrites its oldest entry when full.

```python
from mini_circular_buffer import CircularBuffer, BufferEmpty

buf = CircularBuffer(3)
buf.push("a")
buf.push("b")
buf.push("c")
buf.push("d")        # "a" is silently discarded
assert buf.to_list() == ["b", "c", "d"]
assert buf.pop() == "b"
assert buf.peek() == "c"
assert len(buf) == 2
assert buf.capacity == 3
```

## Why this exists

When you need to keep the last *N* of something — recent log lines, the most
recent sensor readings, a bounded event trail — a ring buffer is the right
data structure: O(1) push, O(1) pop, no allocations on the hot path.  This
library is a small, dependency-free implementation of exactly that.

The deliberate trade-off is that `push` **never raises on full**.  It
overwrites the oldest item and returns `True` to tell you it did so.  If you
would rather reject a push when the buffer is full, call `is_full()` first.

## The edge you will hit

`None` is a perfectly legal value to push.  The buffer does not use `None` as
an internal sentinel, so storing `None` and then `pop()`-ing it back works as
expected.  The one exception is `pop()` and `peek()` on an *empty* buffer:
those raise `BufferEmpty`, because returning `None` would be indistinguishable
from a stored `None`.

Also note that `bool` is rejected as a capacity even though it is a subclass
of `int` — `CircularBuffer(True)` is almost certainly a bug.
