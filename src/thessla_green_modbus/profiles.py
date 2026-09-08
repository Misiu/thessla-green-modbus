"""Product-family metadata for Thessla Green ventilation units."""

from enum import StrEnum


class DeviceFamily(StrEnum):
    """Known Thessla Green product families.

    The family is metadata, not a promise that every optional register is present.
    UNKNOWN keeps the common, conservative register map usable for future models.
    """

    UNKNOWN = "unknown"
    HOME_H = "home_h"
    HOME_V = "home_v"
    HOME_F = "home_f"
    SERIES_4_H = "series_4_h"
    SERIES_4_V = "series_4_v"
    AIRPACK_F = "airpack_f"
