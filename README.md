# thessla-green-modbus

Asynchronous, transport-independent Python library for **Thessla Green AirPack4** ventilation units.

The caller supplies a `modbus_connection.ModbusUnit`. This package owns the device's register map, typed components, physical-unit decoding and validated commands. It does not own a socket, a serial port, a polling loop or a connection lifecycle.

**Status: alpha, protocol/mock tested; not yet verified on physical hardware.** The package is not published on PyPI yet. Do not treat CI as evidence that every firmware revision has been tested.

## Installation

Python 3.12 or newer is required. From a checkout of the `develop` branch:

```sh
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows: .venv\Scripts\activate
python -m pip install -e '.[dev,cli]'
```

The base package depends only on `modbus-connection>=4.8.1,<5`. The optional `cli` extra adds the `tmodbus` backend. An application that already supplies a unit does not need a backend extra from this package.

## Device API

```python
from modbus_connection import ModbusUnit
from thessla_green_modbus import AirPack4, OperatingMode, SpecialMode

async def use_device(unit: ModbusUnit) -> None:
    device = AirPack4(unit)  # No I/O during construction.
    await device.async_update()

    print(device.info.serial_number)
    print(device.info.firmware_version)
    print(device.temperatures.outside)  # Celsius; None for a missing sensor.
    print(device.ventilation.supply_flow)  # Measured cubic metres per hour.

    # The application must deliberately choose to change these settings.
    await device.controls.write("manual_speed", 50)
    await device.controls.write("operating_mode", OperatingMode.MANUAL)
    await device.controls.write("special_mode", SpecialMode.NONE)
    await device.async_update()  # Read actual state; no optimistic cache updates.
```

`async_update()` pools reads across the selected components. `async_read_raw(notify=False)` returns a diagnostic dictionary keyed by address space and address. Each component can also be updated separately and supports `add_update_listener(callback)`, returning an unsubscribe function.

Reading attributes never performs I/O. Transport errors, Modbus exception responses and cancellation propagate to the caller. The last successful values remain cached after an I/O failure; applications must track refresh success and must not present cached data as a successful new reading. Do not run overlapping refresh loops for the same device object.

### Components

| Attribute | Data or controls |
| --- | --- |
| `info` | Controller serial number and firmware version |
| `temperatures` | Outside, supply, extract, after-FPX and ambient temperatures |
| `ventilation` | Measured supply/extract airflow and fan-power relay |
| `controls` | On/off, operating mode, season, manual/temporary speed, special mode |
| `bypass` | Actuator output, disable flag and current thermal function |
| `alarms` | Warning/error, FPX, fan, flow-sensor and filter alarms |
| `constant_flow` | Optional setpoints and dynamic percentage limits |
| `comfort` | Optional ECO/COMFORT and supply temperature settings |
| `erv` | Optional ERV post-heater state and mode |
| `legacy_filter_alarm` | Explicit opt-in for community register 8444 |

Optional components are **not probed automatically**:

```python
from thessla_green_modbus import AirPack4, DeviceOptions

device = AirPack4(unit, options=DeviceOptions(comfort=True, erv=True))
```

Only enable capabilities supported by the actual unit. ERV registers are documented from firmware 4.85. The baseline map includes firmware patch register 4 (documented from 4.82). This is an AirPack4 map, not a claim of compatibility with older AirPack controller generations.

Applications can inspect `device.components` and each component's `resolved_fields`. Descriptors carry units, enum converters, writable flags and validators. A `NumberRange` validator exposes `minimum`, `maximum` and `step` in physical units. To omit a known-unsupported register, call a component's `restrict_fields([...])`; the pooled plan is rebuilt and excluded fields become unavailable and unwritable.

### Important protocol details

Requests never exceed the manufacturer's **16-register limit**. Only declared adjacent addresses are pooled; reserved gaps are not read. Input registers, holding registers and coils remain separate address spaces.

Temperatures use signed 16-bit tenths and the `0x8000` unavailable sentinel. Measured airflow uses unsigned words and the `0xffff` failure sentinel. These values become `None`, not implausible readings. Unknown enum/boolean register values also become `None`.

Special functions all share holding register **4224**: airing, fireplace, open windows and empty house are mutually exclusive modes, not independent switches. Writing `manual_speed` does not change the operating mode. `bypass.disabled=False` permits automatic bypass operation; it does not force the damper open. Coil **11** means fan power, while the distinct run-confirmation output is coil **10**.

The manufacturer's map lists a duct-filter alarm at **8443**. The community example uses **8444**, which is not documented in that map. The latter is isolated behind `DeviceOptions(legacy_filter_alarm=True)` and is off by default. See [protocol provenance and scope](docs/protocol.md).

All public writes validate before I/O. Out-of-range values, fractions incompatible with a field's step, strings, NaN/infinity, unknown enum codes and non-boolean switch inputs are rejected. Single-register writes use FC06. No automatic alarm reset, factory reset, calibration, access-level change or device unlock is performed.

## Read-only query tool

A transparent serial gateway normally needs RTU-over-TCP; a protocol-converting gateway needs socket framing. Match the gateway configuration rather than inferring framing from a TCP port number.

```sh
# Transparent RTU-over-TCP gateway:
python script/query.py 192.168.1.179 --port 9999 --unit 10 --framer rtu

# Modbus TCP gateway:
python script/query.py 192.168.1.179 --port 502 --unit 10 --framer socket

# Serial RTU; documented factory defaults are 9600, 8N1, unit 10:
python script/query.py /dev/ttyUSB0 --transport serial --unit 10

# Offline demonstration using synthetic values, no backend or hardware needed:
python script/query.py unused --snapshot tests/fixtures/airpack4.json
```

The CLI never writes. It owns and closes only its own connection. A supplied library `ModbusUnit` remains owned by the calling application.

## Development

```sh
python -m pip install -e '.[dev]'
bash script/run_checks.sh
# Apply formatting explicitly:
bash script/format_code.sh
```

CI checks formatting, lint, strict typing, tests with branch coverage, distribution metadata and importing the installed wheel outside the checkout. Tests run on Python 3.12, 3.13 and 3.14, including the minimum supported connection-library version. The coverage gate is 95%; hardware compatibility is not a coverage metric.

Changes target `develop`; only local `develop` may open a release PR into `main`. Publishing is release-triggered and uses PyPI Trusted Publishing, not a long-lived API token. See [release setup](docs/releasing.md). Creating a GitHub release before configuring the publisher will not publish a package successfully.

## License

Apache-2.0. This is an independent project, not an official manufacturer package.
