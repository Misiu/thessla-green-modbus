"""Typed Thessla Green components; addresses are zero-based wire addresses.

The common map is verified against manufacturer protocol tables for the Home and
series-4 product generations. Optional ranges are never probed automatically.
A writable descriptor always carries a validator. Service/calibration commands
and alarm acknowledgement are deliberately not exposed as writes.
"""

from modbus_connection.model import Component, boolean, coil, enum, gauge, integer

from .enums import (
    ComfortMode,
    ErvMode,
    FrostStage,
    OperatingMode,
    Season,
    SpecialMode,
    ThermalState,
)
from .fields import SerialNumberField
from .validation import EnumValues, NumberRange, boolean_value


class ThesslaGreenComponent(Component):
    """Respect the controller's 16-register limit and never read across holes."""

    max_span = 16
    max_gap = 1


class DeviceInformation(ThesslaGreenComponent):
    """Controller identity; its serial is not necessarily the chassis serial."""

    register_space = "input"
    firmware_major = integer(0, signed=False)
    firmware_minor = integer(1, signed=False)
    firmware_patch = integer(4, signed=False)
    serial_number = SerialNumberField(24)

    @property
    def firmware_version(self) -> str | None:
        """Return the three decimal version parts, or None before a reading."""
        parts = (self.firmware_major, self.firmware_minor, self.firmware_patch)
        if any(part is None for part in parts):
            return None
        return ".".join(str(part) for part in parts)


class Temperatures(ThesslaGreenComponent):
    """Signed tenths of a degree; 0x8000 denotes an unavailable sensor."""

    register_space = "input"
    outside = gauge(16, 0.1, nan=0x8000, unit="°C")
    supply = gauge(17, 0.1, nan=0x8000, unit="°C")
    extract = gauge(18, 0.1, nan=0x8000, unit="°C")
    after_fpx = gauge(19, 0.1, nan=0x8000, unit="°C")
    ambient = gauge(22, 0.1, nan=0x8000, unit="°C")


class Ventilation(ThesslaGreenComponent):
    """Measured airflows and actual relay outputs, not inferred percentages."""

    supply_flow = integer(256, signed=False, nan=0xFFFF, unit="m³/h")
    extract_flow = integer(257, signed=False, nan=0xFFFF, unit="m³/h")
    fans_powered = coil(11)


class Controls(ThesslaGreenComponent):
    """User controls common to the verified protocol generations."""

    operating_mode = enum(4208, OperatingMode, writable=EnumValues(OperatingMode))
    season = enum(4209, Season, writable=EnumValues(Season))
    manual_speed = integer(4210, signed=False, unit="%", writable=NumberRange(10, 100))
    # Register 4211 is the current temporary setpoint. Manufacturer protocols
    # require an atomic three-register command at 4400..4402 to activate it, so
    # exposing a single-register write here would be incomplete and unsafe.
    temporary_speed = integer(4211, signed=False, unit="%")
    special_mode = enum(4224, SpecialMode, writable=EnumValues(SpecialMode))
    enabled = boolean(4387, writable=boolean_value)


class Bypass(ThesslaGreenComponent):
    """Automatic bypass. disabled=False permits it; it does not force it open."""

    actuator_on = coil(9)
    disabled = boolean(4320, writable=boolean_value)
    state = enum(4330, ThermalState)


class Alarms(ThesslaGreenComponent):
    """Read-only alarms; a communication failure never becomes no alarm."""

    frost_protection_active = boolean(4192)
    frost_stage = enum(4198, FrostStage)
    warning = boolean(8192)
    error = boolean(8193)
    fpx_thermal_protection = boolean(8208)
    supply_fan_failure = boolean(8222)
    extract_fan_failure = boolean(8223)
    supply_flow_sensor_failure = boolean(8330)
    extract_flow_sensor_failure = boolean(8331)
    supply_filter_missing = boolean(8334)
    extract_filter_missing = boolean(8335)
    supply_filter_due = boolean(8338)
    extract_filter_due = boolean(8339)
    duct_filter_due = boolean(8443)


class ConstantFlow(ThesslaGreenComponent):
    """Optional Constant Flow readings, separate from measured airflows."""

    register_space = "input"
    active = boolean(271)
    supply_percentage = integer(272, signed=False, unit="%")
    extract_percentage = integer(273, signed=False, unit="%")
    supply_target_flow = integer(274, signed=False, unit="m³/h")
    extract_target_flow = integer(275, signed=False, unit="m³/h")
    minimum_percentage = integer(276, signed=False, unit="%")
    maximum_percentage = integer(277, signed=False, unit="%")


class Comfort(ThesslaGreenComponent):
    """Optional duct heating/cooling controls in physical degrees Celsius."""

    mode = enum(4304, ComfortMode, writable=EnumValues(ComfortMode))
    state = enum(4305, ThermalState)
    manual_temperature = gauge(
        4212, 0.5, unit="°C", writable=NumberRange(20, 90, 0.5)
    )
    # Like temporary_speed, 4213 is read-only here because activation requires
    # an atomic command at 4403..4405 in the manufacturer protocol.
    temporary_temperature = gauge(4213, 0.5, unit="°C")


class Erv(ThesslaGreenComponent):
    """Optional ERV post-heater. Enable only on supporting firmware/hardware."""

    active = boolean(4704)
    mode = enum(4711, ErvMode, writable=EnumValues(ErvMode))


class PressureFilterAlarm(ThesslaGreenComponent):
    """Optional pressure-switch filter alarm at holding register 8444.

    This register is documented for Home-family units equipped with the relevant
    pressure switch, but is absent from the reviewed series-4 table. Applications
    must therefore opt in only for hardware known to expose it.
    """

    filter_due = boolean(8444)
