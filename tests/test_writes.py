"""Writes must be explicit, validated and routed to the correct address/FC."""

import math

import pytest
from modbus_connection import ModbusConnectionError
from modbus_connection.mock import MockModbusUnit, WriteEvent

from thessla_green_modbus import (
    ComfortMode,
    DeviceOptions,
    ErvMode,
    OperatingMode,
    Season,
    SpecialMode,
    ThesslaGreenDevice,
)


@pytest.mark.parametrize(
    "component,field,value,address,encoded",
    [
        ("controls", "manual_speed", 10, 4210, 10),
        ("controls", "manual_speed", 100, 4210, 100),
        ("controls", "operating_mode", OperatingMode.MANUAL, 4208, 1),
        ("controls", "season", Season.WINTER, 4209, 1),
        ("controls", "special_mode", SpecialMode.AIRING, 4224, 7),
        ("controls", "special_mode", SpecialMode.FIREPLACE, 4224, 2),
        ("controls", "special_mode", SpecialMode.OPEN_WINDOWS, 4224, 10),
        ("controls", "special_mode", SpecialMode.EMPTY_HOUSE, 4224, 11),
        ("controls", "special_mode", SpecialMode.NONE, 4224, 0),
        ("controls", "enabled", True, 4387, 1),
        ("controls", "enabled", False, 4387, 0),
        ("bypass", "disabled", True, 4320, 1),
        ("bypass", "disabled", False, 4320, 0),
        ("comfort", "mode", ComfortMode.COMFORT, 4304, 1),
        ("comfort", "manual_temperature", 10, 4212, 20),
        ("comfort", "manual_temperature", 21.5, 4212, 43),
        ("comfort", "manual_temperature", 45, 4212, 90),
        ("erv", "mode", ErvMode.MODE_2, 4711, 2),
    ],
)
async def test_exact_write(
    unit: MockModbusUnit,
    component: str,
    field: str,
    value: object,
    address: int,
    encoded: int,
) -> None:
    device = ThesslaGreenDevice(unit, options=DeviceOptions(comfort=True, erv=True))
    writes: list[WriteEvent] = []
    unit.on_write(writes.append)
    before = unit.holding.copy()
    await device.components[component].write(field, value)
    assert writes == [WriteEvent("holding", address, [encoded], 6)]
    assert unit.holding == before | {address: encoded}
    assert unit.read_events == []


@pytest.mark.parametrize(
    "component,field",
    [
        ("controls", "temporary_speed"),
        ("comfort", "temporary_temperature"),
    ],
)
async def test_temporary_setpoints_are_read_only(
    unit: MockModbusUnit, component: str, field: str
) -> None:
    device = ThesslaGreenDevice(unit, options=DeviceOptions(comfort=True))
    writes: list[WriteEvent] = []
    unit.on_write(writes.append)
    with pytest.raises(AttributeError):
        await device.components[component].write(field, 50)
    assert writes == []


@pytest.mark.parametrize(
    "value", [-1, 0, 9, 101, 65536, True, False, "50", None, 50.5, math.nan, math.inf]
)
async def test_invalid_speed_never_reaches_device(
    unit: MockModbusUnit, value: object
) -> None:
    device = ThesslaGreenDevice(unit)
    writes: list[WriteEvent] = []
    unit.on_write(writes.append)
    with pytest.raises(ValueError):
        await device.controls.write("manual_speed", value)
    assert writes == []


@pytest.mark.parametrize("value", [-1, 3, "1", 1.0, True, Season.WINTER])
async def test_invalid_mode(unit: MockModbusUnit, value: object) -> None:
    with pytest.raises(ValueError):
        await ThesslaGreenDevice(unit).controls.write("operating_mode", value)
    assert unit.holding[4208] == 1


@pytest.mark.parametrize("value", ["false", 0, 1, None])
async def test_boolean_write_is_strict(unit: MockModbusUnit, value: object) -> None:
    with pytest.raises(ValueError):
        await ThesslaGreenDevice(unit).controls.write("enabled", value)
    assert unit.holding[4387] == 1


@pytest.mark.parametrize("value", [9.5, 45.5, 21.25, True, math.nan, math.inf])
async def test_invalid_temperature(unit: MockModbusUnit, value: object) -> None:
    device = ThesslaGreenDevice(unit, options=DeviceOptions(comfort=True))
    assert device.comfort is not None
    with pytest.raises(ValueError):
        await device.comfort.write("manual_temperature", value)
    assert unit.holding[4212] == 43


@pytest.mark.parametrize(
    "component,field",
    [("alarms", "error"), ("bypass", "actuator_on"), ("controls", "typo")],
)
async def test_unknown_or_readonly_rejected(
    unit: MockModbusUnit, component: str, field: str
) -> None:
    device = ThesslaGreenDevice(unit)
    with pytest.raises(AttributeError):
        await device.components[component].write(field, True)


async def test_write_error_propagates_and_cache_is_not_optimistic(
    unit: MockModbusUnit,
) -> None:
    device = ThesslaGreenDevice(unit)
    await device.async_update()
    unit.fail_write(4210, ModbusConnectionError("Offline"))
    with pytest.raises(ModbusConnectionError):
        await device.controls.write("manual_speed", 70)
    assert device.controls.manual_speed == 50
    unit.fail_write(4210, None)
    await device.controls.write("manual_speed", 70)
    assert device.controls.manual_speed == 50
    await device.async_update()
    assert device.controls.manual_speed == 70
