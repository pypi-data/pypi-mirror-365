"""Test unit of measurement types."""

import math

from stuom import (
    Angstroms,
    Deciwatts,
    Hours,
    HundredNanoseconds,
    Kilovolts,
    Meters,
    Microamps,
    Microseconds,
    Milimeters,
    Milliseconds,
    Minutes,
    Nanoseconds,
    ReciprocalCentimeters,
    ReciprocalMeters,
    Seconds,
    Watts,
)
from stuom.electricity import Amps, Volts
from stuom.length import Centimeters, Micrometers


def test_uom_operators():
    mins_sum = Minutes(2) + 4
    assert isinstance(mins_sum, Minutes)
    assert mins_sum == Minutes(6)

    mins_prod = Minutes(2) * 4
    assert isinstance(mins_prod, Minutes)
    assert mins_prod == Minutes(8)

    mins_truediv = Minutes(4) / 2
    assert isinstance(mins_truediv, Minutes)
    assert mins_truediv == Minutes(2)

    mins_floordiv = Minutes(4.5) // 2
    assert isinstance(mins_floordiv, Minutes)
    assert mins_floordiv == Minutes(2)

    mins_sub = Minutes(9) - 2
    assert isinstance(mins_sub, Minutes)
    assert mins_sub == Minutes(7)


def test_duration_uom():
    assert math.isclose(Minutes.from_duration(Hours(2)), Minutes(60 * 2))
    assert math.isclose(Hours(2).convert_duration(Minutes), Minutes(60 * 2))
    assert math.isclose(Minutes.from_duration(Seconds(10)), Minutes(1 / 6))
    assert math.isclose(Seconds.from_duration(Minutes(10)), 10 * 60)
    assert math.isclose(Milliseconds.from_duration(Minutes(10)), 10 * 60 * 1000)
    assert math.isclose(Microseconds.from_duration(Minutes(10)), 10 * 60 * 1000 * 1000)
    assert math.isclose(
        Nanoseconds.from_duration(Minutes(10)), 10 * 60 * 1000 * 1000 * 1000
    )
    assert math.isclose(
        HundredNanoseconds.from_duration(Minutes(10)), 10 * 60 * 1000 * 1000 * 10
    )


def test_length_uom():
    assert math.isclose(Meters(0.005), Milimeters(5).convert_length(Meters))
    assert math.isclose(Meters(1), Meters.from_length(Milimeters(1000)))
    assert math.isclose(Meters(2), Meters.from_length(Angstroms.from_length(Meters(2))))
    assert math.isclose(Meters(2).convert_length(Angstroms), Angstroms(2e10))
    assert math.isclose(Angstroms(2e10).convert_length(Meters), Meters(2))

    assert math.isclose(
        ReciprocalMeters(10e-2)
        .convert_from_reciprocal_length(ReciprocalCentimeters)
        .convert_from_reciprocal_length(ReciprocalMeters),
        ReciprocalMeters(10e-2),
    )

    assert math.isclose(
        ReciprocalMeters(1).convert_from_reciprocal_length(ReciprocalCentimeters),
        ReciprocalCentimeters(100),
    )

    assert math.isclose(ReciprocalMeters(10e-2).to_meters(), Meters(1 / 10e-2))


def test_electricity_uom():
    power = Watts.from_current_and_potential(Microamps(225), Kilovolts(20))
    assert power == Watts(4.5)
    assert Deciwatts.from_power(power) == 45
    assert Volts.from_potential(Kilovolts(20)) == Volts(20000)
    assert Amps.from_current(Microamps(225)) == Amps(0.000225)


def test_uom_str_representations():
    # Length
    assert str(Micrometers(10)) == "10.0um"
    assert str(Milimeters(10)) == "10.0mm"
    assert str(Meters(10)) == "10.0m"
    assert str(Centimeters(10)) == "10.0cm"

    # Electricity
    assert str(Microamps(10)) == "10.0uA"
    assert str(Amps(10)) == "10.0A"

    assert str(Watts(10)) == "10.0W"
    assert str(Deciwatts(10)) == "10.0dW"

    assert str(Volts(10)) == "10.0V"
    assert str(Kilovolts(10)) == "10.0kV"

    # Duration
    assert str(Nanoseconds(10)) == "10.0ns"
    assert str(Microseconds(10)) == "10.0us"
    assert str(Seconds(10)) == "10.0s"
    assert str(Minutes(10)) == "10.0 mins"
    assert str(Hours(10)) == "10.0 hrs"
