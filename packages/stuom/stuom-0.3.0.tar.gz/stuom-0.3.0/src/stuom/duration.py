"""Units of measurement for working with durations."""

import math
from typing import TypeVar

from stuom.uom import HasSiOrder

DurationT = TypeVar("DurationT", bound="Duration")


class Duration(HasSiOrder):
    """Represents a duration and is functionally equivalent to its base."""

    def convert_duration(self, to_cls: type[DurationT]) -> DurationT:
        return self.convert_si(to_cls)

    @classmethod
    def from_duration(cls, other: "Duration"):
        return other.convert_duration(cls)


class Hours(Duration):
    """hrs."""

    def __str__(self) -> str:
        return super().__str__() + " hrs"

    @staticmethod
    def order() -> float:
        return -math.log(3600, 10)


class Minutes(Duration):
    """mins."""

    def __str__(self) -> str:
        return super().__str__() + " mins"

    @staticmethod
    def order() -> float:
        return -(math.log(6, 10) + 1)


# Seconds-based SI units
class Seconds(Duration):
    """s."""

    def __str__(self) -> str:
        return super().__str__() + "s"

    @staticmethod
    def order() -> float:
        return 0


class Milliseconds(Duration):
    """ms."""

    def __str__(self) -> str:
        return super().__str__() + "ms"

    @staticmethod
    def order() -> float:
        return 3


class Microseconds(Duration):
    """us."""

    def __str__(self) -> str:
        return super().__str__() + "us"

    @staticmethod
    def order() -> float:
        return 6


class HundredNanoseconds(Duration):
    """hns."""

    def __str__(self) -> str:
        return super().__str__() + "hns"

    @staticmethod
    def order() -> float:
        return 7


class Nanoseconds(Duration):
    """ns."""

    def __str__(self) -> str:
        return super().__str__() + "ns"

    @staticmethod
    def order() -> float:
        return 9
