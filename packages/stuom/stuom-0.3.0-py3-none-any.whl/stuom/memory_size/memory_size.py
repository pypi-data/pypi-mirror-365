"""Units of measurement base class for working with computer memory sizes."""

from typing import TypeVar

from stuom.uom import HasSiOrder

MemorySizeT = TypeVar("MemorySizeT", bound="MemorySize")


class MemorySize(HasSiOrder):
    """Represents a byte-based unit of measuring memory size.

    Note that there are two standards for describing computer memory size. One is the International
    System of Units (SI) definition, in which the decimal number system is used: 1000 bytes is
    kilobytes (kB). The other is binary-based, in where 1024 bytes is 1 KB. The IEC recommends the
    use of Kibi as a prefix in place of Kilo however. We intend to follow the IEC80000-13
    international standard on this matter and distinguish KiloBytes vs. KibiBytes.
    """

    def convert_memmory_size(self, to_cls: type[MemorySizeT]) -> MemorySizeT:
        return self.convert_si(to_cls)

    @classmethod
    def from_memory_size(cls: type[MemorySizeT], other: "MemorySize") -> MemorySizeT:
        return other.convert_memmory_size(cls)


class Bytes(MemorySize):
    """8 bits."""

    def __str__(self) -> str:
        return super().__str__() + " B"

    @staticmethod
    def order() -> int:
        return 0
