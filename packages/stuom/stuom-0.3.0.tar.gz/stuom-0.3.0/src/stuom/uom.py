"""Simple statically-typed unit of measurements with order conversions."""

from abc import abstractmethod
from typing import SupportsFloat, TypeAlias, TypeVar

HAS_PYDANTIC_CORE = False
"""Whether the environment is configured with the pydantic_core package installed."""

# Attempt to import pydantic_core, and determine whether validation support is to be added or not.
try:
    from collections.abc import Callable
    from typing import Any

    from pydantic_core import core_schema

    HAS_PYDANTIC_CORE = True
except ImportError:
    pass


SiT = TypeVar("SiT", bound="HasSiOrder")
IntT: TypeAlias = int | float


# SI unit types
class HasSiOrder(float):
    """Represents a unit of measurement type that has an SI order at the type level."""

    @staticmethod
    @abstractmethod
    def order() -> float:
        raise NotImplementedError()

    def convert_si(self, to_cls: type[SiT]) -> SiT:
        return _convert_si(self, to_cls)

    @classmethod
    def from_si(cls: type[SiT], other: "HasSiOrder") -> SiT:
        return other.convert_si(cls)

    def __mul__(self: SiT, value: IntT) -> SiT:
        self_type = type(self)
        return self_type(float.__mul__(self, value))

    def __add__(self: SiT, value: IntT) -> SiT:
        self_type = type(self)
        return self_type(float.__add__(self, value))

    def __sub__(self: SiT, value: IntT) -> SiT:
        self_type = type(self)
        return self_type(float.__sub__(self, value))

    def __truediv__(self: SiT, value: IntT) -> SiT:
        self_type = type(self)
        return self_type(float.__truediv__(self, value))

    def __floordiv__(self: SiT, value: IntT) -> SiT:
        self_type = type(self)
        return self_type(float.__floordiv__(self, value))

    if HAS_PYDANTIC_CORE:

        @classmethod
        def validate(cls, value: object, _):
            if not isinstance(value, SupportsFloat):
                raise TypeError(f"Unsupported standard unit number type: {type(value)}")

            return cls(float(value))

        @classmethod
        def __get_pydantic_json_schema__(
            cls,
            schema: core_schema.CoreSchema,  # type: ignore
            handler: Callable[[Any], core_schema.CoreSchema],  # type: ignore
        ) -> core_schema.CoreSchema:  # type: ignore
            return handler(core_schema.float_schema())

        @classmethod
        def __get_pydantic_core_schema__(cls, source, handler):
            return core_schema.with_info_plain_validator_function(cls.validate)


def _convert_si(from_value: HasSiOrder, to_cls: type[SiT]) -> SiT:
    return to_cls(from_value * 10 ** (to_cls.order() - from_value.order()))
