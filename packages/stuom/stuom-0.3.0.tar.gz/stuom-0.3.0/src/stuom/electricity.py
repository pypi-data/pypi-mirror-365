"""Contains units of measurement for working with electricity units such as power."""

from typing import TypeVar

from stuom.uom import HasSiOrder

PotentialT = TypeVar("PotentialT", bound="ElectricPotential")


class ElectricPotential(HasSiOrder):
    """A unit of measurement representing electric potential."""

    def convert_potential(self, to_cls: type[PotentialT]) -> PotentialT:
        return self.convert_si(to_cls)

    @classmethod
    def from_potential(cls: type[PotentialT], other: "ElectricPotential") -> PotentialT:
        return other.convert_potential(cls)


class Kilovolts(ElectricPotential):
    """kV."""

    def __str__(self) -> str:
        return super().__str__() + "kV"

    @staticmethod
    def order() -> int:
        return -3


class Volts(ElectricPotential):
    """V."""

    def __str__(self) -> str:
        return super().__str__() + "V"

    @staticmethod
    def order() -> int:
        return 0


class Millivolts(ElectricPotential):
    """mV."""

    def __str__(self) -> str:
        return super().__str__() + "mV"

    @staticmethod
    def order() -> int:
        return 3


PowerT = TypeVar("PowerT", bound="Power")


class Power(HasSiOrder):
    """The amount of energy transferred per unit time."""

    def convert_power(self, to_cls: type[PowerT]) -> PowerT:
        return self.convert_si(to_cls)

    @classmethod
    def from_power(cls: type[PowerT], other: "Power") -> PowerT:
        return other.convert_power(cls)


class Watts(Power):
    """W."""

    def __str__(self) -> str:
        return super().__str__() + "W"

    @staticmethod
    def order() -> int:
        return 0

    @staticmethod
    def from_current_and_potential(
        current: "Current", potential: ElectricPotential
    ) -> "Watts":
        return Watts(Amps.from_si(current) * Volts.from_si(potential))


class Deciwatts(Power):
    """dW."""

    def __str__(self) -> str:
        return super().__str__() + "dW"

    @staticmethod
    def order() -> int:
        return 1


class Milliwatts(Power):
    """mW."""

    def __str__(self) -> str:
        return super().__str__() + "mW"

    @staticmethod
    def order() -> int:
        return 3


CurrentT = TypeVar("CurrentT", bound="Current")


class Current(HasSiOrder):
    """A unit of measurement representing electric current."""

    def convert_current(self, to_cls: type[CurrentT]) -> CurrentT:
        return self.convert_si(to_cls)

    @classmethod
    def from_current(cls: type[CurrentT], other: "Current") -> CurrentT:
        return other.convert_current(cls)


class Amps(Current):
    """A."""

    def __str__(self) -> str:
        return super().__str__() + "A"

    @staticmethod
    def order() -> int:
        return 0


class Milliamps(Current):
    """mA."""

    def __str__(self) -> str:
        return super().__str__() + "mA"

    @staticmethod
    def order() -> int:
        return 3


class Microamps(Current):
    """uA."""

    def __str__(self) -> str:
        return super().__str__() + "uA"

    @staticmethod
    def order() -> int:
        return 6
