# `slice-to-offset-range`

A utility function that converts Python slice objects to explicit, [canonicalized](https://github.com/jifengwu2k/canonicalize-range) `(start_offset, stop_offset, step)` offset ranges given a sequence length.

## Features

- Converts slice objects to explicit offset ranges
  - `offset = 0` refers to the first element of a sequence, `< 0` to memory before that, and `> 0` to memory after that
- Converts negative indices and None values
- Handles both positive and negative steps
- Ensures:
  - `(start_offset, stop_offset, step)` is [canonicalized](https://github.com/jifengwu2k/canonicalize-range)
  - `start_offset <= stop_offset` when `step > 0`
  - `stop_offset >= stop_offset` when `step < 0`
- Supports Python 2+

## Installation

```bash
pip install slice-to-offset-range
```

## Usage

```python
from slice_to_offset_range import slice_to_offset_range


# Basic positive step cases
assert slice_to_offset_range(slice(2, 5), 10) == (2, 5, 1)
assert slice_to_offset_range(slice(2, 5, 2), 10) == (2, 6, 2)  # Canonicalized
assert slice_to_offset_range(slice(0, 100), 10) == (0, 100, 1)  # No bound checking
assert slice_to_offset_range(slice(1, 1), 10) == (1, 1, 1)  # Empty slice
assert slice_to_offset_range(slice(1, 0), 10) == (1, 1, 1)  # Empty slice, canonicalized

# Basic negative step cases
assert slice_to_offset_range(slice(5, 2, -1), 10) == (5, 2, -1)
assert slice_to_offset_range(slice(5, 2, -2), 10) == (5, 1, -2)  # Canonicalized
assert slice_to_offset_range(slice(5, 5, -1), 10) == (5, 5, -1)  # Empty slice
assert slice_to_offset_range(slice(5, 6, -1), 10) == (5, 5, -1)  # Empty slice, canonicalized

# Negative indices with positive step
assert slice_to_offset_range(slice(-3, -1), 10) == (7, 9, 1)
assert slice_to_offset_range(slice(2, -3), 10) == (2, 7, 1)
assert slice_to_offset_range(slice(-11, -2, 2), 10) == (-1, 9, 2)  # Canonicalized, no bound checking

# Negative indices with negative step
assert slice_to_offset_range(slice(-2, -5, -1), 10) == (8, 5, -1)
assert slice_to_offset_range(slice(-1, -7, -1), 5) == (4, -2, -1)  # No bound checking
assert slice_to_offset_range(slice(-3, -6, -1), 10) == (7, 4, -1)

# None values with positive step
assert slice_to_offset_range(slice(None, 5), 10) == (0, 5, 1)
assert slice_to_offset_range(slice(2, None), 10) == (2, 10, 1)
assert slice_to_offset_range(slice(None, None), 10) == (0, 10, 1)

# None values with negative step
assert slice_to_offset_range(slice(None, None, -1), 5) == (4, -1, -1)
assert slice_to_offset_range(slice(3, None, -1), 5) == (3, -1, -1)
assert slice_to_offset_range(slice(None, 2, -1), 5) == (4, 2, -1)

# Invalid cases (should raise ValueError)
try:
    slice_to_offset_range(slice(2, 5, 0), 10)
    assert False, "Should raise ValueError for step=0"
except ValueError:
    pass

try:
    slice_to_offset_range(slice(2.5, 5), 10)
    assert False, "Should raise ValueError for non-integer start"
except ValueError:
    pass

try:
    slice_to_offset_range(slice(2, 5), -1)
    assert False, "Should raise ValueError for negative n"
except ValueError:
    pass
```

## Contributing

Contributions are welcome! Please submit pull requests or open issues on the GitHub repository.

## License

This project is licensed under the [MIT License](LICENSE).