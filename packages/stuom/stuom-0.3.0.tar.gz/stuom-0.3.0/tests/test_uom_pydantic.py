"""Test that we can create basic pydantic models using units of measurement."""

import pytest
from stuom.duration import Seconds
from stuom.electricity import Kilovolts

try:
    from pydantic import BaseModel  # type: ignore

except (ImportError, ModuleNotFoundError):
    pytest.skip(allow_module_level=True)


def test_duration_fields_work_in_pydantic_models():
    """This ensures that one can construct pydantic `BaseModel`s with the `Duration` units of
    measurement.
    """

    class TestModel(BaseModel):
        duration: Seconds

    _ = TestModel(duration=Seconds(2))


def test_uom_floatlike_validates():
    class PydanticModel(BaseModel):
        voltage: Kilovolts

    model = PydanticModel.model_validate({"voltage": 10})
    assert model.voltage == 10

def test_uom_non_floatlike_fails_to_validate():
    class PydanticModel(BaseModel):
        voltage: Kilovolts

    with pytest.raises(TypeError):
        _ = PydanticModel.model_validate({"voltage": PydanticModel})
