# tuplehash

Pure Python reimplementation of CPython's `tuplehash` function with exact overflow behavior, designed for hashing user-defined immutable sequences.

## The Current Pain Point

Currently in Python, if you want your custom immutable sequence to hash like a tuple:

```python
from typing import TypeVar, Sequence

T = TypeVar('T', covariant=True)


class MySequence(Sequence[T]):
    def __hash__(self):
        return hash(tuple(self))
```

This creates memory overhead for large collections.

Until such stdlib functionality exists, `tuplehash` provides:

```python
from typing import TypeVar, Sequence

from tuplehash import tuplehash

T = TypeVar('T', covariant=True)


class MySequence(Sequence[T]):
    def __hash__(self):
        return tuplehash(self)
```

This gives you stdlib-quality hashing today.

## Features

- **Strict overflow behavior** using [custom fixed-width integer types](https://github.com/jifengwu2k/fixed-width-int)
- **Version-specific implementations** matching:
    - Python 2.7/3.0-3.7: Original multiplicative hash
    - Python 3.8+: Simplified [xxHash algorithm](https://github.com/Cyan4973/xxHash/blob/master/doc/xxhash_spec.md)

## Installation

```bash
pip install tuplehash
```

## Usage

```python
from tuplehash import tuplehash

# Basic usage
assert tuplehash((1, 2, 3)) == hash((1, 2, 3))

# Works with any collection
from collections import namedtuple

Point = namedtuple('Point', ['x', 'y'])
assert tuplehash(Point(3, 4)) == hash(Point(3, 4))
```

## Implementation Details

### Version-Specific Algorithms

| Python Version | Algorithm           | Key Characteristics                                                     |
|----------------|---------------------|-------------------------------------------------------------------------|
| <3.8           | Multiplicative hash | Initial value `0x345678`, multiplier `1000003`, length-dependent addend |
| ≥3.8           | Simplified xxHash   | Single accumulator, 31/13-bit rotations, prime multiplications          |

### Overflow Handling

Uses [custom `Signed`/`Unsigned` types]((https://github.com/jifengwu2k/fixed-width-int)) to exactly replicate:

- 32-bit overflow on 32-bit platforms
- 64-bit overflow on 64-bit platforms
- All intermediate casting behaviors

## Limitations

- Performance overhead vs native implementation

## Contributing

Contributions are welcome! Please submit pull requests or open issues on the GitHub repository.

## License

This project is licensed under the [MIT License](LICENSE).