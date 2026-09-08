"""Assemble a Thessla Green device without owning its transport."""

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType

from modbus_connection import ModbusUnit
from modbus_connection.model import ComponentGroup

from .components import (
    Alarms,
    Bypass,
    Comfort,
    ConstantFlow,
    Controls,
    DeviceInformation,
    Erv,
    PressureFilterAlarm,
    Temperatures,
    ThesslaGreenComponent,
    Ventilation,
)
from .profiles import DeviceFamily


@dataclass(frozen=True, slots=True)
class DeviceOptions:
    """Explicit capabilities; no speculative probes or silent fallback reads."""

    constant_flow: bool = False
    comfort: bool = False
    erv: bool = False
    pressure_filter_alarm: bool = False

    def __post_init__(self) -> None:
        if any(
            type(value) is not bool
            for value in (
                self.constant_flow,
                self.comfort,
                self.erv,
                self.pressure_filter_alarm,
            )
        ):
            raise ValueError("Capability flags must be booleans")


class ThesslaGreenDevice(ComponentGroup):
    """Thessla Green registers accessed through a caller-supplied ModbusUnit.

    The default component set is the conservative map verified against multiple
    manufacturer protocol generations. ``family`` records product metadata for
    applications and future profile-specific extensions; it does not implicitly
    enable optional register ranges.

    Construction performs no I/O. The caller owns connection lifetime, polling,
    timeouts and retries. Transport errors and cancellation propagate.
    """

    def __init__(
        self,
        unit: ModbusUnit,
        *,
        family: DeviceFamily = DeviceFamily.UNKNOWN,
        options: DeviceOptions | None = None,
    ) -> None:
        if not isinstance(family, DeviceFamily):
            raise ValueError("family must be a DeviceFamily")
        self.family = family
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
        self.pressure_filter_alarm = (
            PressureFilterAlarm(unit) if self.options.pressure_filter_alarm else None
        )
        members: dict[str, ThesslaGreenComponent] = {
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
            ("pressure_filter_alarm", self.pressure_filter_alarm),
        ):
            if component is not None:
                members[name] = component
        self.components: Mapping[str, ThesslaGreenComponent] = MappingProxyType(members)
        super().__init__(unit, members.values())
