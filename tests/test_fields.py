"""Independent examples for device-specific representations and metadata."""

import math

import pytest

from thessla_green_modbus import NumberRange, OperatingMode
from thessla_green_modbus.fields import SerialNumberField
from thessla_green_modbus.validation import EnumValues


@pytest.mark.parametrize(
    "words,expected",
    [
        ([0x1A, 0x2B, 0x3C, 0x4D, 0x5E, 0x6F], "1a2b3c4d5e6f"),
        ([0, 0, 0, 0, 0, 1], "000000000001"),
        ([0] * 6, None),
        ([255] * 6, None),
        ([256, 0, 0, 0, 0, 1], None),
        ([-1, 0, 0, 0, 0, 1], None),
        ([1, 2, 3], None),
    ],
)
def test_serial(words: list[int], expected: str | None) -> None:
    assert SerialNumberField(24).decode(words) == expected


@pytest.mark.parametrize(
    "minimum,maximum,step", [(2, 1, 1), (0, 1, 0), (0, 1, -1), (math.nan, 1, 1)]
)
def test_invalid_range_metadata(minimum: float, maximum: float, step: float) -> None:
    with pytest.raises(ValueError):
        NumberRange(minimum, maximum, step)


def test_enum_accepts_documented_integer_code() -> None:
    assert EnumValues(OperatingMode)(1) is OperatingMode.MANUAL
