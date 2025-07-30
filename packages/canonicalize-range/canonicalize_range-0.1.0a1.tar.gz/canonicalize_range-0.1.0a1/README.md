# `canonicalize-range`

This Python module provides utilities for normalizing and canonicalizing range objects to ensure they contain complete steps from their start value.

## Functions

### `normalize_stop(start, stop, step)`

Normalizes the stop value of a range to make it a multiple of step from start.

**Parameters:**
- `start`: The starting value of the range (int)
- `stop`: The original stop value of the range (int)
- `step`: The step size between values (must be non-zero) (int)

**Returns:**
- A new stop value that ensures complete steps from the start (int)

**Raises:**
- `ValueError`: If step is 0

### `canonicalize_range(range_object)`

Creates a canonical version of a range object with adjusted stop value.

**Parameters:**
- `range_object`: The original range object to canonicalize (range)

**Returns:**
- A new range object with adjusted stop value (range)

## Examples

```python
from canonicalize_range import canonicalize_range


# Range may stop before completing the final step
# Canonicalized range completes the step pattern
r1 = range(0, 10, 3)  # Contains 0, 3, 6, 9
canonical_r1 = canonicalize_range(r1)  # Produces range(0, 12, 3), which also contains 0, 3, 6, 9
assert (canonical_r1.start, canonical_r1.stop, canonical_r1.step) == (0, 12, 3)
assert list(r1) == list(canonical_r1)

r2 = range(10, 0, -3)  # Contains 10, 7, 4, 1
canonical_r2 = canonicalize_range(r2)  # Produces range(10, -2, -3), which also contains 10, 7, 4, 1
assert (canonical_r2.start, canonical_r2.stop, canonical_r2.step) == (10, -2, -3)
assert list(r2) == list(canonical_r2)

# Range may be empty
# Canonicalized range makes that explicit with `start = stop`
r3 = range(10, 0, 3)  # Empty
canonical_r3 = canonicalize_range(r3)  # Produces range(10, 10, 3), which is also empty
assert (canonical_r3.start, canonical_r3.stop, canonical_r3.step) == (10, 10, 3)
assert list(r3) == list(canonical_r3)

r4 = range(0, 10, -3)  # Empty
canonical_r4 = canonicalize_range(r4)  # Produces range(0, 0, -3), which is also empty
assert (canonical_r4.start, canonical_r4.stop, canonical_r4.step) == (0, 0, -3)
assert list(r4) == list(canonical_r4)
```

## Installation

```bash
pip install canonicalize-range
```

## Contributing

Contributions are welcome! Please submit pull requests or open issues on the GitHub repository.

## License

This project is licensed under the [MIT License](LICENSE).