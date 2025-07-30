"""Contains computer memory size units of memory size following the EIC decimal convention."""

from stuom.memory_size.memory_size import MemorySize


class KiloBytes(MemorySize):
    """1_000 bytes."""

    def __str__(self) -> str:
        return super().__str__() + " kB"

    @staticmethod
    def order() -> int:
        return -3


class MegaBytes(MemorySize):
    """1_000_000 bytes."""

    def __str__(self) -> str:
        return super().__str__() + " MB"

    @staticmethod
    def order() -> int:
        return -6


class GigaBytes(MemorySize):
    """1_000_000_000 bytes."""

    def __str__(self) -> str:
        return super().__str__() + " GB"

    @staticmethod
    def order() -> int:
        return -9


class TeraBytes(MemorySize):
    """1_000_000_000_000 bytes."""

    def __str__(self) -> str:
        return super().__str__() + " TB"

    @staticmethod
    def order() -> int:
        return -12


class PetaBytes(MemorySize):
    """1_000_000_000_000 bytes."""

    def __str__(self) -> str:
        return super().__str__() + " PB"

    @staticmethod
    def order() -> int:
        return -15
