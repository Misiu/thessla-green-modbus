# thessla-green-modbus

Asynchronous, transport-independent Python library for **Thessla Green** ventilation units using Modbus.

The caller supplies a `modbus_connection.ModbusUnit`. This package owns the verified register map, typed components, physical-unit decoding and validated commands. It does not own a socket, serial port, polling loop or connection lifecycle.

**Status: alpha, protocol/mock tested; not yet verified on physical hardware.** The conservative common map has been cross-checked against manufacturer protocols for Home-family, series-4 and large-f controllers. Optional registers remain explicit opt-ins because their presence still depends on controller family, firmware and installed hardware.

## Installation

```sh
python -m pip install thessla-green-modbus
```

Python 3.12 or newer is required.

## Device API

```python
from modbus_connection import ModbusUnit
from thessla_green_modbus import (
    DeviceFamily,
    OperatingMode,
    ThesslaGreenDevice,
)


async def use_device(unit: ModbusUnit) -> None:
    device = ThesslaGreenDevice(unit, family=DeviceFamily.HOME_V)
    await device.async_update()

    print(device.info.serial_number)
    print(device.info.firmware_version)
    print(device.temperatures.outside)
    print(device.ventilation.supply_flow)

    await device.controls.write("manual_speed", 50)
    await device.controls.write("operating_mode", OperatingMode.MANUAL)
    await device.async_update()
```

Construction performs no I/O. Reading attributes performs no I/O. Transport errors and cancellation propagate to the caller, and cached values are not presented as a successful new reading after a failed refresh.

### Product families

`DeviceFamily` currently identifies these manufacturer product families:

- `HOME_H`
- `HOME_V`
- `HOME_F`
- `SERIES_4_H`
- `SERIES_4_V`
- `AIRPACK_F`
- `UNKNOWN`

The family is metadata and a future compatibility hook. It deliberately does **not** turn optional register ranges on automatically. `UNKNOWN` exists so a new or unlisted Thessla Green model is not rejected merely because the package predates it.

### Optional capabilities

```python
from thessla_green_modbus import DeviceOptions, ThesslaGreenDevice

device = ThesslaGreenDevice(
    unit,
    options=DeviceOptions(
        constant_flow=True,
        comfort=True,
        erv=True,
        pressure_filter_alarm=True,
    ),
)
```

Only enable capabilities supported by the actual controller. The pressure-switch filter alarm at 8444 is documented for relevant Home and large-f hardware but is not present in the reviewed series-4 table.

### Safety and protocol details

Requests never exceed the manufacturer's 16-register limit and never read across undeclared holes. Input, holding and coil spaces remain separate.

Temperatures use signed 16-bit tenths and `0x8000` as unavailable. Measured airflow uses `0xffff` as unavailable. Unknown enum/boolean values decode to `None`.

All public writes validate before I/O. The manual comfort temperature follows the manufacturer encoding raw **20–90** with multiplier **0.5**, therefore the physical writable range is **10–45 °C** in 0.5 °C steps. Temporary airflow and temporary temperature registers are intentionally **read-only** in this release: manufacturer protocols require atomic three-register activation commands at 4400–4402 and 4403–4405, so a single-register write would be incomplete.

Special functions share holding register 4224 and are represented as one mutually exclusive enum. `bypass.disabled=False` permits automatic bypass operation; it does not force the damper open.

See [protocol provenance and compatibility scope](docs/protocol.md).

## Read-only query tool

```sh
python script/query.py 192.168.1.179 --port 9999 --unit 10 --framer rtu
python script/query.py 192.168.1.179 --port 502 --unit 10 --framer socket
python script/query.py /dev/ttyUSB0 --transport serial --unit 10
python script/query.py unused --snapshot tests/fixtures/thessla_green.json
```

The CLI never writes.

## Development

```sh
python -m pip install -e '.[dev]'
bash script/run_checks.sh
```

Changes target `develop`. Releases are tag-driven after a green merge to `main`; the tag must match the package version exactly.

## License

Apache-2.0. This is an independent project, not an official manufacturer package.
