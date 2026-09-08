# Protocol provenance and implementation scope

The primary reference is the manufacturer's **MODBUS_USER_AirPack_4_08.2022.01** register table, titled *Protokol Modbus RTU*. A public mirror is available at:

https://github.com/voyo/ThesslaGreen-modbus/blob/main/ProtokolModbusRTU_AirPack4.pdf

SHA-256 of the reviewed PDF:

```text
fe883682372761e64eaa9357ca1a328f0c1dd06baf1283070c93a27da3407bc8
```

The PDF is not redistributed in this package. Relevant pages are 2 (connection parameters, coils and request limit), 4 (input registers, serial format and temperature sentinel), 10 (measured flow and its failure sentinel), 11-13 (user commands), 15 (ERV), and 16-17 (alarms).

Secondary cross-checks:

- Community register configuration: https://bartekbuduje.pl/rekuperator-thessla-green-polaczenie-z-home-assistant/
- Existing implementation: https://github.com/aLAN-LDZ/ThesslaGreen_HA
- Component and repository structure reference: https://github.com/Tom-Bom-badil/trovis-modbus/
- Modelling framework source: https://github.com/home-assistant-libs/modbus-connection/

The source code was independently implemented against the device table and the public modelling API. Community configuration is a cross-check, not authority for undocumented writes.

## Corrections relative to the community configuration

| Topic | Implemented interpretation |
| --- | --- |
| Input 16-19, 22 | Signed tenths of Celsius; raw 32768 is unavailable |
| Holding 256-257 | Unsigned measured flow; 65535 is unavailable |
| Coil 11 | Fan-power relay, not the distinct coil-10 run-confirmation output |
| Holding 4224 | One enumerated special mode, not independent switches |
| Holding 4320 | Bypass disable flag; zero permits automatic operation |
| Holding 4212-4213 | Half-degree physical values, 10-45 degrees Celsius |
| Holding 8443/8444 | 8443 is documented duct-filter replacement; 8444 is an opt-in, unverified extension |

The supplied YAML's device reads and commands are represented, with 8444 deliberately opt-in. Optional comfort and ERV controls from the secondary project are also represented. Mathematical energy estimates, UI templates and time accumulation are application responsibilities, not registers or measured device energy. No nominal airflow such as 320 m3/h is hardcoded.

## Scope boundaries

This initial library models operational readings, user commands and selected diagnostics for AirPack4. It does **not** implement every register in the 17-page manual: weekly schedules, the controller clock, factory/installer calibration, access levels, product unlocking, filter-reset commands and extended Expansion/GWC controls are outside this release. Unsupported registers are not silently scanned or written. Future extensions should add dedicated components and independently verified register fixtures.

No hardware test has been performed for this release. Before deployment, verify controller firmware, serial identity, readings and individual commands against the local panel. Do not infer a chassis model or serial from network addresses. The six-byte controller serial is available when the device reports a valid value; an unknown serial remains None rather than becoming a fabricated identity.

## Framework choices

The reviewed framework includes integer and scaled fields, enums, booleans, flags, packed bits, raw registers, strings, multiword numeric/network fields and repeating component groups. This device map needs integer, gauge, enum, boolean and coil descriptors. The one custom descriptor is the serial: the table specifies six one-byte register values, which is not a standard packed three-register MAC address.

The application supplies `ModbusUnit`. No private framework attributes are modified and no backend client is imported by the library. Public components, descriptors, field restriction, pooled reads and update listeners are used directly.
