#!/usr/bin/env python3
"""Read-only standalone query tool. No write command is intentionally provided."""

import argparse
import asyncio
import json
from pathlib import Path

from modbus_connection import ModbusError
from modbus_connection.cli_helper import add_connection_args, connect_from_args
from modbus_connection.mock import MockModbusConnection

from thessla_green_modbus import AirPack4, DeviceOptions


async def query(args: argparse.Namespace, snapshot: dict | None) -> None:
    """Query one device and always close the connection this CLI owns."""
    if snapshot is None:
        connection = await connect_from_args(args)
        unit = connection.for_unit(args.unit)
    else:
        connection = MockModbusConnection()
        unit = connection.for_unit(args.unit)
        unit.load_raw(
            {
                space: {int(address): value for address, value in values.items()}
                for space, values in snapshot.items()
            }
        )
    try:
        device = AirPack4(
            unit,
            options=DeviceOptions(
                constant_flow=args.constant_flow,
                comfort=args.comfort,
                erv=args.erv,
                legacy_filter_alarm=args.legacy_filter_alarm,
            ),
        )
        await device.async_update()
        result = {
            name: {
                field: getattr(component, field) for field in component.resolved_fields
            }
            for name, component in device.components.items()
        }
        result["info"]["firmware_version"] = device.info.firmware_version
        print(json.dumps(result, indent=2))
    finally:
        await connection.close()


def main() -> None:
    """Parse options; file I/O happens before starting the event loop."""
    parser = argparse.ArgumentParser(description=__doc__)
    add_connection_args(
        parser, connections=(("tcp", "rtu"), ("tcp", "socket"), ("serial", "rtu"))
    )
    parser.set_defaults(framer="rtu")
    parser.add_argument("--unit", type=int, default=10)
    parser.add_argument("--snapshot", type=Path, help="Read synthetic JSON, not hardware")
    parser.add_argument("--constant-flow", action="store_true")
    parser.add_argument("--comfort", action="store_true")
    parser.add_argument("--erv", action="store_true")
    parser.add_argument("--legacy-filter-alarm", action="store_true")
    args = parser.parse_args()
    if not 1 <= args.unit <= 247:
        parser.error("The RTU unit address must be between 1 and 247")
    try:
        snapshot = json.loads(args.snapshot.read_text()) if args.snapshot else None
        asyncio.run(query(args, snapshot))
    except (ModbusError, OSError, ValueError) as err:
        parser.exit(1, f"Query failed: {err}\n")


if __name__ == "__main__":
    main()
