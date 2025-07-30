# Copyright (c) 2025 Jifeng Wu
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
import ctypes
import sys

from typing import Iterable, Optional, Sized
from fixed_width_int import Signed, Unsigned

# Type definitions
SIZE_T_BIT_WIDTH = ctypes.sizeof(ctypes.c_size_t) * 8

PY_SSIZE_T = Signed[SIZE_T_BIT_WIDTH]
PY_HASH_T = Signed[SIZE_T_BIT_WIDTH]
PY_UHASH_T = Unsigned[SIZE_T_BIT_WIDTH]

if sys.version_info < (3, 8):
    # Constants
    _PyHASH_MULTIPLIER = PY_UHASH_T(1000003)

    # Pre-initialized magic numbers
    # To prevent repetitive construction of immutable objects
    PY_SSIZE_T_1 = PY_SSIZE_T(1)
    PY_UHASH_T_0x345678 = PY_UHASH_T(0x345678)
    PY_UHASH_T_82520 = PY_UHASH_T(82520)
    PY_UHASH_T_97531 = PY_UHASH_T(97531)
    PY_UHASH_T_NEG_1 = PY_UHASH_T(-1)
    PY_UHASH_T_NEG_2 = PY_UHASH_T(-2)


    def tuplehash(iterable, length=None):
        # type: (Iterable, Optional[int]) -> int
        if length is None:
            if isinstance(iterable, Sized):
                length = len(iterable)
            else:
                raise TypeError('Cannot determine the length of iterable. Please explicitly pass a non-negative int to the length argument.')
        elif not isinstance(length, int) or length < 0:
            raise ValueError('length should a non-negative int')

        remaining_length = PY_SSIZE_T(length - 1)  # type: PY_SSIZE_T
        mult = _PyHASH_MULTIPLIER  # type: PY_UHASH_T
        x = PY_UHASH_T_0x345678  # type: PY_UHASH_T

        for p in iterable:
            y = PY_HASH_T(hash(p))  # type: PY_HASH_T
            x = (x ^ y) * mult
            mult += PY_HASH_T(PY_UHASH_T_82520 + remaining_length + remaining_length)
            remaining_length -= PY_SSIZE_T_1

        x += PY_UHASH_T_97531
        if x == PY_UHASH_T_NEG_1:
            x = PY_UHASH_T_NEG_2

        return int(PY_HASH_T(x))
else:
    # Pre-initialized magic numbers
    # To prevent repetitive construction of immutable objects
    PY_UHASH_T_13 = PY_UHASH_T(13)
    PY_UHASH_T_19 = PY_UHASH_T(19)
    PY_UHASH_T_31 = PY_UHASH_T(31)
    PY_UHASH_T_33 = PY_UHASH_T(33)
    PY_UHASH_T_3527539 = PY_UHASH_T(3527539)
    PY_UHASH_T_NEG_1 = PY_UHASH_T(-1)

    if SIZE_T_BIT_WIDTH > 32:
        _PyHASH_XXPRIME_1 = PY_UHASH_T(11400714785074694791)
        _PyHASH_XXPRIME_2 = PY_UHASH_T(14029467366897019727)
        _PyHASH_XXPRIME_5 = PY_UHASH_T(2870177450012600261)


        def _PyHASH_XXROTATE(x):
            # type: (PY_UHASH_T) -> PY_UHASH_T
            return (x << PY_UHASH_T_31) | (x >> PY_UHASH_T_33)  # type: ignore
    else:
        _PyHASH_XXPRIME_1 = PY_UHASH_T(2654435761)
        _PyHASH_XXPRIME_2 = PY_UHASH_T(2246822519)
        _PyHASH_XXPRIME_5 = PY_UHASH_T(374761393)


        def _PyHASH_XXROTATE(x):
            # type: (PY_UHASH_T) -> PY_UHASH_T
            return (x << PY_UHASH_T_13) | (x >> PY_UHASH_T_19)  # type: ignore


    def tuplehash(iterable, length=None):
        # type: (Iterable, Optional[int]) -> int
        if length is None:
            if isinstance(iterable, Sized):
                length = len(iterable)
            else:
                raise TypeError('Cannot determine the length of iterable. Please explicitly pass a non-negative int to the length argument.')
        elif not isinstance(length, int) or length < 0:
            raise ValueError('length should a non-negative int')

        fixed_width_length = PY_SSIZE_T(length)  # type: PY_SSIZE_T
        acc = _PyHASH_XXPRIME_5  # type: PY_UHASH_T
        for item in iterable:
            lane = PY_UHASH_T(hash(item))  # type: PY_UHASH_T
            acc += lane * _PyHASH_XXPRIME_2
            acc = _PyHASH_XXROTATE(acc)
            acc *= _PyHASH_XXPRIME_1

        # Add input length, mangled to keep the historical value of hash(())
        acc += fixed_width_length ^ (_PyHASH_XXPRIME_5 ^ PY_UHASH_T_3527539)

        if acc == PY_UHASH_T_NEG_1:
            return 1546275796

        return int(PY_HASH_T(acc))
