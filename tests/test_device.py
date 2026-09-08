"""Exercise the real modelling framework through its supported mock backend."""

import asyncio
from unittest.mock import AsyncMock, Mock

from modbus_connection import IllegalDataAddressError, ModbusConnectionError
from modbus_connection.mock import MockModbusConnection, MockModbusUnit
import pytest

from thessla_green_modbus import (
    DeviceFamily,
    DeviceOptions,
    OperatingMode,
    SpecialMode,
    ThesslaGreenDevice,
)


async def test_read_fixture(unit: MockModbusUnit) -> None:
    device = ThesslaGreenDevice(unit)
    assert device.info.serial_number is None
    await device.async_update()
    assert device.info.serial_number == "1a2b3c4d5e6f"
    assert device.info.firmware_version == "4.84.2"
    assert device.temperatures.outside == -12.3
    assert device.temperatures.supply == 20.5
    assert device.temperatures.extract == 23.1
    assert device.temperatures.after_fpx == 5.5
    assert device.temperatures.ambient == 26.8
    assert device.ventilation.supply_flow == 160
    assert device.ventilation.extract_flow == 163
    assert device.ventilation.fans_powered is True
    assert device.controls.operating_mode is OperatingMode.MANUAL
    assert device.bypass.actuator_on is True
    assert device.alarms.warning is True


async def test_family_is_metadata(unit: MockModbusUnit) -> None:
    device = ThesslaGreenDevice(unit, family=DeviceFamily.HOME_V)
    assert device.family is DeviceFamily.HOME_V
    assert device.pressure_filter_alarm is None
    await device.async_update()


async def test_optional_components(unit: MockModbusUnit) -> None:
    device = ThesslaGreenDevice(
        unit,
        family=DeviceFamily.HOME_H,
        options=DeviceOptions(
            constant_flow=True,
            comfort=True,
            erv=True,
            pressure_filter_alarm=True,
        ),
    )
    await device.async_update()
    assert device.constant_flow is not None
    assert device.constant_flow.maximum_percentage == 120
    assert device.comfort is not None
    assert device.comfort.manual_temperature == 21.5
    assert device.erv is not None
    assert device.erv.active is True
    assert device.pressure_filter_alarm is not None
    assert device.pressure_filter_alarm.filter_due is True
    assert len(device.components) == 10


async def test_default_does_not_probe_optional_registers(unit: MockModbusUnit) -> None:
    device = ThesslaGreenDevice(unit)
    for address in (4304, 4305, 4704, 4711, 8444):
        unit.fail_read(address, IllegalDataAddressError(message="Unsupported"))
    unit.fail_read(
        271, IllegalDataAddressError(message="Unsupported"), register_type="input"
    )
    await device.async_update()
    assert device.erv is None
    assert device.comfort is None
    assert device.constant_flow is None
    assert device.pressure_filter_alarm is None


@pytest.mark.parametrize("all_features", [False, True])
async def test_read_plan_never_crosses_holes_or_device_limit(
    unit: MockModbusUnit, all_features: bool
) -> None:
    device = ThesslaGreenDevice(
        unit,
        options=DeviceOptions(
            constant_flow=all_features,
            comfort=all_features,
            erv=all_features,
            pressure_filter_alarm=all_features,
        ),
    )
    expected: dict[str, set[int]] = {}
    for component in device.components.values():
        for field in component.resolved_fields.values():
            expected.setdefault(field.space, set()).update(
                range(field.address, field.address + field.count)
            )
    await device.async_update()
    seen: dict[str, set[int]] = {}
    for event in unit.read_events:
        assert 1 <= event.count <= 16
        addresses = set(range(event.address, event.address + event.count))
        assert addresses <= expected[event.register_type]
        previous = seen.setdefault(event.register_type, set())
        assert not addresses & previous
        previous.update(addresses)
    assert seen == expected


@pytest.mark.parametrize("address", [16, 17, 18, 19, 22])
async def test_temperature_sentinel(unit: MockModbusUnit, address: int) -> None:
    unit.input[address] = 0x8000
    device = ThesslaGreenDevice(unit)
    await device.async_update()
    name = {16: "outside", 17: "supply", 18: "extract", 19: "after_fpx", 22: "ambient"}
    assert getattr(device.temperatures, name[address]) is None


@pytest.mark.parametrize("address,name", [(256, "supply_flow"), (257, "extract_flow")])
async def test_flow_sentinel(unit: MockModbusUnit, address: int, name: str) -> None:
    unit.holding[address] = 65535
    device = ThesslaGreenDevice(unit)
    await device.async_update()
    assert getattr(device.ventilation, name) is None


async def test_unknown_values_do_not_become_valid_states(unit: MockModbusUnit) -> None:
    unit.holding[4208] = 99
    unit.holding[4387] = 2
    device = ThesslaGreenDevice(unit)
    await device.async_update()
    assert device.controls.operating_mode is None
    assert device.controls.enabled is None


async def test_raw_snapshot_and_notifications(unit: MockModbusUnit) -> None:
    device = ThesslaGreenDevice(unit)
    listener = Mock()
    remove = device.temperatures.add_update_listener(listener)
    raw = await device.async_read_raw(notify=False)
    assert raw["input"][16] == 65413
    assert raw["coil"][9] is True
    listener.assert_not_called()
    await device.async_update()
    listener.assert_called_once_with()
    remove()
    remove()


@pytest.mark.parametrize("cancel", [False, True])
async def test_failed_poll_keeps_previous_snapshot_without_notifying(
    unit: MockModbusUnit, cancel: bool, monkeypatch: pytest.MonkeyPatch
) -> None:
    device = ThesslaGreenDevice(unit)
    await device.async_update()
    listener = Mock()
    device.temperatures.add_update_listener(listener)
    unit.input[17] = 999
    failure = asyncio.CancelledError if cancel else ModbusConnectionError
    monkeypatch.setattr(unit, "read_coils", AsyncMock(side_effect=failure()))
    with pytest.raises(failure):
        await device.async_update()
    assert device.temperatures.supply == 20.5
    listener.assert_not_called()


async def test_units_and_capabilities_are_isolated() -> None:
    connection = MockModbusConnection()
    first = ThesslaGreenDevice(connection.for_unit(10))
    second = ThesslaGreenDevice(
        connection.for_unit(11), options=DeviceOptions(erv=True)
    )
    connection.for_unit(10).holding[4210] = 20
    connection.for_unit(11).holding[4210] = 80
    await asyncio.gather(first.async_update(), second.async_update())
    assert first.controls.manual_speed == 20
    assert second.controls.manual_speed == 80
    assert first.erv is None and second.erv is not None
    await first.controls.write("special_mode", SpecialMode.AIRING)
    assert connection.for_unit(10).holding[4224] == 7


async def test_restrict_fields_updates_parent_plan(unit: MockModbusUnit) -> None:
    device = ThesslaGreenDevice(unit)
    await device.async_update()
    device.controls.restrict_fields(["enabled"])
    unit.read_events.clear()
    await device.async_update()
    assert device.controls.manual_speed is None
    with pytest.raises(AttributeError):
        await device.controls.write("manual_speed", 50)


@pytest.mark.parametrize("value", [1, "false", None])
def test_options_reject_non_booleans(value: object) -> None:
    with pytest.raises(ValueError):
        DeviceOptions(erv=value)  # type: ignore[arg-type]


def test_family_rejects_arbitrary_strings(unit: MockModbusUnit) -> None:
    with pytest.raises(ValueError):
        ThesslaGreenDevice(unit, family="home_v")  # type: ignore[arg-type]
