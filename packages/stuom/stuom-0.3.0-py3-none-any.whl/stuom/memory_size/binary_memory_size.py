"""Contains computer memory size units of memory size following the EIC binary convention.

The current implementation of these units incurs some added floating-point error. The reason this
occurs is simply because the uom.py module implements SI conversions using a base-10 exponent.
"""

import math

from stuom.memory_size.memory_size import MemorySize


class KibiBytes(MemorySize):
    """2^10 bytes."""

    def __str__(self) -> str:
        return super().__str__() + " kiB"

    @staticmethod
    def order() -> float:
        return -math.log(2**10, 10)


class MebiBytes(MemorySize):
    """2^20 bytes."""

    def __str__(self) -> str:
        return super().__str__() + " MiB"

    @staticmethod
    def order() -> float:
        return -math.log(2**20, 10)


class GibiBytes(MemorySize):
    """2^30 bytes."""

    def __str__(self) -> str:
        return super().__str__() + " GiB"

    @staticmethod
    def order() -> float:
        return -math.log(2**30, 10)


class TebiBytes(MemorySize):
    """2^40 bytes."""

    def __str__(self) -> str:
        return super().__str__() + " TiB"

    @staticmethod
    def order() -> float:
        return -math.log(2**40, 10)


class PebiBytes(MemorySize):
    """2^50 bytes."""

    def __str__(self) -> str:
        return super().__str__() + " PiB"

    @staticmethod
    def order() -> float:
        return -math.log(2**50, 10)
