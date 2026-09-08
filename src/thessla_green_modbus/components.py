"""Typed AirPack4 components; all addresses are zero-based wire addresses.

Source: MODBUS_USER_AirPack_4_08.2022.01, pages 2, 4, 10-17.
A writable descriptor always carries a validator. Service/calibration commands
and alarm acknowledgement are deliberately not exposed as writes.
"""

from modbus_connection.model import (
    Component,
    boolean,
    coil,
    enum,
    gauge,
    integer,
)

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


class AirPackComponent(Component):
    """Respect the device's 16-register limit; do not read across holes."""

    max_span = 16
    # In modbus-connection this is address distance, not number of missing words:
    # 1 joins adjacent addresses, but never reads an undeclared register.
    max_gap = 1


class DeviceInformation(AirPackComponent):
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


class Temperatures(AirPackComponent):
    """Signed tenths of a degree; 0x8000 denotes an unavailable sensor."""

    register_space = "input"
    outside = gauge(16, 0.1, nan=0x8000, unit="\u00b0C")
    supply = gauge(17, 0.1, nan=0x8000, unit="\u00b0C")
    extract = gauge(18, 0.1, nan=0x8000, unit="\u00b0C")
    after_fpx = gauge(19, 0.1, nan=0x8000, unit="\u00b0C")
    ambient = gauge(22, 0.1, nan=0x8000, unit="\u00b0C")


class Ventilation(AirPackComponent):
    """Measured airflows and actual relay outputs, not inferred percentages."""

    supply_flow = integer(256, signed=False, nan=0xFFFF, unit="m\u00b3/h")
    extract_flow = integer(257, signed=False, nan=0xFFFF, unit="m\u00b3/h")
    # Coil 11 is fan power, NOT the separate run-confirmation output at coil 10.
    fans_powered = coil(11)


class Controls(AirPackComponent):
    """User commands. A write changes only the named register."""

    operating_mode = enum(4208, OperatingMode, writable=EnumValues(OperatingMode))
    season = enum(4209, Season, writable=EnumValues(Season))
    manual_speed = integer(
        4210, signed=False, unit="%", writable=NumberRange(10, 100)
    )
    temporary_speed = integer(
        4211, signed=False, unit="%", writable=NumberRange(10, 100)
    )
    special_mode = enum(4224, SpecialMode, writable=EnumValues(SpecialMode))
    enabled = boolean(4387, writable=boolean_value)


class Bypass(AirPackComponent):
    """Automatic bypass. 'disabled=False' permits it; it does not force it open."""

    actuator_on = coil(9)
    disabled = boolean(4320, writable=boolean_value)
    state = enum(4330, ThermalState)


class Alarms(AirPackComponent):
    """Read-only alarms; a communication failure never becomes 'no alarm'."""

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


class ConstantFlow(AirPackComponent):
    """Optional extended Constant Flow readings, separate from measured flows."""

    register_space = "input"
    active = boolean(271)
    supply_percentage = integer(272, signed=False, unit="%")
    extract_percentage = integer(273, signed=False, unit="%")
    supply_target_flow = integer(274, signed=False, unit="m\u00b3/h")
    extract_target_flow = integer(275, signed=False, unit="m\u00b3/h")
    minimum_percentage = integer(276, signed=False, unit="%")
    maximum_percentage = integer(277, signed=False, unit="%")


class Comfort(AirPackComponent):
    """Optional duct heating/cooling controls, in physical degrees Celsius."""

    mode = enum(4304, ComfortMode, writable=EnumValues(ComfortMode))
    state = enum(4305, ThermalState)
    manual_temperature = gauge(
        4212, 0.5, unit="\u00b0C", writable=NumberRange(10, 45, 0.5)
    )
    temporary_temperature = gauge(
        4213, 0.5, unit="\u00b0C", writable=NumberRange(10, 45, 0.5)
    )


class Erv(AirPackComponent):
    """Optional ERV post-heater. Only enable on supporting firmware/hardware."""

    active = boolean(4704)
    mode = enum(4711, ErvMode, writable=EnumValues(ErvMode))


class LegacyFilterAlarm(AirPackComponent):
    """Opt-in community map extension, NOT in the 08.2022.01 manufacturer map.

    Some published configurations poll 8444. It must not be assumed to be the
    documented duct-filter alarm at 8443. Enable only after hardware validation.
    """

    filter_due = boolean(8444)
