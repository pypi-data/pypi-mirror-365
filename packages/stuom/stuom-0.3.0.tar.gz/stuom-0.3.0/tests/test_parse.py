"""Test unit of measurement parsing."""

import pytest
from stuom.duration import (
    Hours,
    HundredNanoseconds,
    Microseconds,
    Milliseconds,
    Minutes,
    Nanoseconds,
    Seconds,
)
from stuom.parse import find_minimal_si, parse_duration, parse_minimal_si


def test_parse_minimal_si():
    assert type(find_minimal_si(Milliseconds(0.05))) is Microseconds
    assert type(find_minimal_si(Milliseconds(5000))) is Seconds
    assert type(find_minimal_si(Milliseconds(5))) is Milliseconds
    assert parse_minimal_si(Milliseconds(0.05)) == "50.0us"
    assert parse_minimal_si(Milliseconds(5000)) == "5.0s"
    assert parse_minimal_si(Seconds(0.01)) == "10.0ms"


def test_parse():
    assert parse_duration("10hrs") == Hours(10)
    assert parse_duration("10mins") == Minutes(10)
    assert parse_duration("10s") == Seconds(10)
    assert parse_duration("10ms") == Milliseconds(10)
    assert parse_duration("10us") == Microseconds(10)
    assert parse_duration("10hns") == HundredNanoseconds(10)
    assert parse_duration("10ns") == Nanoseconds(10)

    with pytest.raises(ValueError):
        parse_duration("10x")

    with pytest.raises(ValueError):
        parse_duration("1")
