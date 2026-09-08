"""Assemble a device from components without owning its transport."""

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType

from modbus_connection import ModbusUnit
from modbus_connection.model import ComponentGroup

from .components import (
    AirPackComponent,
    Alarms,
    Bypass,
    Comfort,
    ConstantFlow,
    Controls,
    DeviceInformation,
    Erv,
    LegacyFilterAlarm,
    Temperatures,
    Ventilation,
)


@dataclass(frozen=True, slots=True)
class DeviceOptions:
    """Explicit capabilities; no speculative probes or silent fallback reads."""

    constant_flow: bool = False
    comfort: bool = False
    erv: bool = False
    legacy_filter_alarm: bool = False

    def __post_init__(self) -> None:
        if any(
            type(value) is not bool
            for value in (
                self.constant_flow,
                self.comfort,
                self.erv,
                self.legacy_filter_alarm,
            )
        ):
            raise ValueError("Capability flags must be booleans")


class AirPack4(ComponentGroup):
    """AirPack4 registers accessed through a caller-supplied ModbusUnit.

    Construction performs no I/O. The caller owns connection lifetime, polling,
    timeouts and retries. async_update() and async_read_raw() pool component
    reads through modbus-connection. Transport errors and cancellation propagate.
    """

    def __init__(
        self, unit: ModbusUnit, *, options: DeviceOptions | None = None
    ) -> None:
        self.options = options if options is not None else DeviceOptions()
        self.info = DeviceInformation(unit)
        self.temperatures = Temperatures(unit)
        self.ventilation = Ventilation(unit)
        self.controls = Controls(unit)
        self.bypass = Bypass(unit)
        self.alarms = Alarms(unit)
        self.constant_flow = ConstantFlow(unit) if self.options.constant_flow else None
        self.comfort = Comfort(unit) if self.options.comfort else None
        self.erv = Erv(unit) if self.options.erv else None
        self.legacy_filter_alarm = (
            LegacyFilterAlarm(unit) if self.options.legacy_filter_alarm else None
        )
        members: dict[str, AirPackComponent] = {
            "info": self.info,
            "temperatures": self.temperatures,
            "ventilation": self.ventilation,
            "controls": self.controls,
            "bypass": self.bypass,
            "alarms": self.alarms,
        }
        for name, component in (
            ("constant_flow", self.constant_flow),
            ("comfort", self.comfort),
            ("erv", self.erv),
            ("legacy_filter_alarm", self.legacy_filter_alarm),
        ):
            if component is not None:
                members[name] = component
        self.components: Mapping[str, AirPackComponent] = MappingProxyType(members)
        super().__init__(unit, members.values())
