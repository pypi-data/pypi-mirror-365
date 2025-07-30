# `rangeutils`

Utility functions for working with Python ranges represented as (start, stop, step) tuples.

**NOTE: to support both Python 2 and Python 3, we represent ranges as a `Tuple[int, int, int]` standing
for `(start, stop, step)`.**

## Functions

### `contains(start: int, stop: int, step: int, element: int) -> bool`

Checks if a given element is part of a range.

**Example:**

```python
from range_tools import contains

assert contains(0, 10, 2, 4)
assert not contains(0, 10, 2, 10)
assert not contains(0, 10, 2, 5)

assert contains(10, 0, -2, 4)
assert not contains(10, 0, -2, 0)
assert not contains(10, 0, -2, 5)
```

### `get_length(start: int, stop: int, step: int) -> int`

Get the length of a range (how many elements it contains).

**Example:**

```python
from range_tools import get_length

# Range contains the elements [10, 13, 16, 19]
assert get_length(10, 20, 3) == 4
assert get_length(10, 22, 3) == 4

# Range contains the elements [10, 13, 16, 19, 22]
assert get_length(10, 23, 3) == 5

# Range contains the elements [20, 17, 14, 11]
assert get_length(20, 10, -3) == 4
assert get_length(20, 8, -3) == 4

# Range contains the elements [20, 17, 14, 11, 8]
assert get_length(20, 7, -3) == 5

# Range is empty
assert get_length(5, 5, 1) == 0
assert get_length(5, 5, -1) == 0
assert get_length(5, 4, 1) == 0
assert get_length(5, 6, -1) == 0
```

### `canonicalize_range(start: int, stop: int, step: int) -> Tuple[int, int, int]`

Canonicalizes a range tuple to ensure it contains complete steps from its start value.

**Example:**

```python
from range_tools import canonicalize_range

# Range may stop before completing the final step
# Canonicalized range completes the step pattern
assert canonicalize_range(0, 10, 3) == (0, 12, 3)
assert canonicalize_range(10, 0, -3) == (10, -2, -3)

# Empty ranges are canonicalized to start=stop
assert canonicalize_range(10, 0, 3) == (10, 10, 3)
assert canonicalize_range(0, 10, -3) == (0, 0, -3)
```

### `reverse_range(start: int, stop: int, step: int) -> Tuple[int, int, int]`

Creates a canonicalized, reversed version of the range.

**Example:**

```python
from range_tools import reverse_range

assert reverse_range(1, 5, 1) == (4, 0, -1)
assert reverse_range(4, 0, -1) == (1, 5, 1)
assert reverse_range(1, 5, -1) == (1, 1, 1)  # Handles empty ranges
assert reverse_range(4, 0, 1) == (4, 4, -1)  # Handles empty ranges
```

### `extend_range(start: int, stop: int, step: int, k: int) -> Tuple[Tuple[int, int, int], Tuple[int, int, int]]`

Extends a range by k steps (can be negative) and returns a tuple containing:

- The canonicalized extended range (original range + k steps)
- The canonicalized extension part (just the added k steps)

**Example:**

```python
from range_tools import extend_range

assert extend_range(1, 5, 1, 2) == ((1, 7, 1), (5, 7, 1))
assert extend_range(1, 5, 1, 0) == ((1, 5, 1), (5, 5, 1))  # Empty extension
assert extend_range(1, 5, 1, -2) == ((1, 3, 1), (5, 5, 1))  # Backward extension
assert extend_range(1, 5, 1, -10) == ((1, 1, 1), (5, 5, 1))  # Clips backward extensions that go too far
```

### `slice_to_offset_range(sequence_length: int, slice_object: object) -> Tuple[int, int, int]`

Given a sequence length, converts a Python slice object to a canonicalized offset range
`(offset_start, offset_stop, offset_step)` describing which elements would be selected by that slice object.

```python
from range_tools import slice_to_offset_range

# Basic positive step cases
assert slice_to_offset_range(10, slice(2, 5)) == (2, 5, 1)
assert slice_to_offset_range(10, slice(2, 5, 2)) == (2, 6, 2)  # Canonicalized
assert slice_to_offset_range(10, slice(0, 100)) == (0, 100, 1)  # No bound checking
assert slice_to_offset_range(10, slice(1, 1)) == (1, 1, 1)  # Empty slice
assert slice_to_offset_range(10, slice(1, 0)) == (1, 1, 1)  # Empty slice, canonicalized

# Basic negative step cases
assert slice_to_offset_range(10, slice(5, 2, -1)) == (5, 2, -1)
assert slice_to_offset_range(10, slice(5, 2, -2)) == (5, 1, -2)  # Canonicalized
assert slice_to_offset_range(10, slice(5, 5, -1)) == (5, 5, -1)  # Empty slice
assert slice_to_offset_range(10, slice(5, 6, -1)) == (5, 5, -1)  # Empty slice, canonicalized

# Negative indices with positive step
assert slice_to_offset_range(10, slice(-3, -1)) == (7, 9, 1)
assert slice_to_offset_range(10, slice(2, -3)) == (2, 7, 1)
assert slice_to_offset_range(10, slice(-11, -2, 2)) == (-1, 9, 2)  # Canonicalized, no bound checking

# Negative indices with negative step
assert slice_to_offset_range(10, slice(-2, -5, -1)) == (8, 5, -1)
assert slice_to_offset_range(5, slice(-1, -7, -1)) == (4, -2, -1)  # No bound checking
assert slice_to_offset_range(10, slice(-3, -6, -1)) == (7, 4, -1)

# None values with positive step
assert slice_to_offset_range(10, slice(None, 5)) == (0, 5, 1)
assert slice_to_offset_range(10, slice(2, None)) == (2, 10, 1)
assert slice_to_offset_range(10, slice(None, None)) == (0, 10, 1)

# None values with negative step
assert slice_to_offset_range(5, slice(None, None, -1)) == (4, -1, -1)
assert slice_to_offset_range(5, slice(3, None, -1)) == (3, -1, -1)
assert slice_to_offset_range(5, slice(None, 2, -1)) == (4, 2, -1)

# Invalid cases (should raise ValueError)
try:
    slice_to_offset_range(10, slice(2, 5, 0))
    assert False, "Should raise ValueError for step=0"
except ValueError:
    pass

try:
    slice_to_offset_range(10, slice(2.5, 5))
    assert False, "Should raise ValueError for non-integer start"
except ValueError:
    pass

try:
    slice_to_offset_range(-1, slice(2, 5))
    assert False, "Should raise ValueError for negative n"
except ValueError:
    pass
```

### `slice_range(start: int, stop: int, step: int, slice_object: slice) -> Tuple[int, int, int]`

Applies a slice operation to an existing range, returning a canonicalized new range.

```python
from range_tools import slice_range

# Range contains [0, 2, 4, 6, 8]
original_range = (0, 9, 2)
# Take elements at indices 1, 2, 3
slicer = slice(1, 4)
# Range contains [2, 4, 6]
assert slice_range(*original_range, slice_object=slicer) == (2, 8, 2)

# Range contains [0, 2, 4, 6, 8]
original_range = (0, 9, 2)
# Reverse range
slicer = slice(None, None, -1)
# Range contains [8, 6, 4, 2, 0]
assert slice_range(*original_range, slice_object=slicer) == (8, -2, -2)

# Range contains [0, 1, 2, ..., 9]
original_range = (0, 10, 1)
# Empty slice
slicer = slice(5, 2)
assert slice_range(*original_range, slice_object=slicer) == (5, 5, 1)  # Empty range
```

## Installation

```bash
pip install range-tools
```

## Contributing

Contributions are welcome! Please submit pull requests or open issues on the GitHub repository.

## License

This project is licensed under the [MIT License](LICENSE).