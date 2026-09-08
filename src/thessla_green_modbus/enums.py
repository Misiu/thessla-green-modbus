"""Values documented in MODBUS_USER_AirPack_4_08.2022.01."""

from enum import IntEnum


class OperatingMode(IntEnum):
    """Ventilation control source."""

    AUTOMATIC = 0
    MANUAL = 1
    TEMPORARY = 2


class Season(IntEnum):
    """Automatic schedule selection."""

    SUMMER = 0
    WINTER = 1


class SpecialMode(IntEnum):
    """Mutually exclusive functions sharing holding register 4224."""

    NONE = 0
    HOOD = 1
    FIREPLACE = 2
    AIRING_BUTTON = 3
    AIRING_SWITCH = 4
    AIRING_HUMIDITY = 5
    AIRING_AIR_QUALITY = 6
    AIRING = 7
    AIRING_AUTOMATIC = 8
    AIRING_MANUAL = 9
    OPEN_WINDOWS = 10
    EMPTY_HOUSE = 11


class FrostStage(IntEnum):
    """Frost protection stage, not the heater's power state."""

    OFF = 0
    FPX1 = 1
    FPX2 = 2


class ThermalState(IntEnum):
    """Current thermal function."""

    INACTIVE = 0
    HEATING = 1
    COOLING = 2


class ComfortMode(IntEnum):
    """Supply-air temperature control selection."""

    ECO = 0
    COMFORT = 1


class ErvMode(IntEnum):
    """ERV post-heater mode; available from firmware 4.85."""

    OFF = 0
    MODE_1 = 1
    MODE_2 = 2
