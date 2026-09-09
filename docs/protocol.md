# Protocol provenance and compatibility scope

The library targets Thessla Green ventilation controllers using documented Modbus interfaces rather than one chassis model.

Primary manufacturer references reviewed for the common register map:

- Home-family protocol: https://thesslagreen.com/wp-content/uploads/MODBUS_USER_AirPack_Home_08.2021.01.pdf
- Series-4 protocol: https://thesslagreen.com/wp-content/uploads/MODBUS_USER_AirPack_4_10.2022.01.pdf
- Large-f protocol: https://thesslagreen.com/wp-content/uploads/MODBUS_USER_AirPack_S2_08.2021.01.pdf
- Current product/documentation catalogue: https://thesslagreen.com/products/rekuperatory/

The Home protocol covers the Home h, Home v and Home f product families. The series-4 protocol covers the corresponding h/v generation. The large-f protocol explicitly covers AirPack 1450f/1850f and L variants.

## Verified common behaviour

The reviewed Home, series-4 and large-f tables align on the conservative core areas used by this package, including firmware/controller identity, temperatures, measured airflow, user mode/season/manual speed, special mode, bypass, enable state and the principal alarm ranges. They impose a maximum of 16 simultaneously accessed registers and document factory serial defaults of 9600 8/N/1 with unit address 10.

Important interpretations:

| Topic | Implementation |
| --- | --- |
| Input 16-19, 22 | Signed tenths of Celsius; raw 32768 is unavailable |
| Holding 256-257 | Unsigned measured flow; 65535 is unavailable |
| Coil 11 | Fan-power relay, distinct from run-confirmation coil 10 |
| Holding 4224 | One enumerated special mode, not independent switches |
| Holding 4320 | Bypass disable flag; zero permits automatic operation |
| Holding 4212 | Manual comfort setpoint; raw 20-90 with multiplier 0.5, therefore physical 10-45 °C |
| Holding 4211/4213 | Readable temporary setpoints; not directly writable here |
| Holding 4400-4405 | Atomic temporary-mode command blocks required by the manufacturer |
| Holding 8443 | Duct-filter replacement alarm in the reviewed tables |
| Holding 8444 | Pressure-switch filter alarm in reviewed Home/large-f tables; absent from reviewed series-4 table |

## Scope boundaries

The default device uses only the conservative register set verified across the reviewed generations. Optional Constant Flow, comfort, ERV and pressure-filter ranges require explicit opt-in and are never discovered by scanning reserved addresses.

The `DeviceFamily` value is metadata, not proof of a capability. `UNKNOWN` is intentionally supported so future or unlisted Thessla Green models can use the common map without pretending their optional hardware has been identified.

No hardware test has yet been performed. Before deployment, verify firmware, controller serial, readings and each write against the local controller. Weekly schedules, controller clock, factory/installer calibration, access levels, product unlocking, filter reset and extended expansion controls remain outside this release.
