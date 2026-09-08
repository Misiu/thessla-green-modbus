# Changelog

## 0.1.0a1 - Unreleased

- Add backend-independent asynchronous AirPack4 components and validated writes.
- Respect the 16-register request limit and avoid undeclared address gaps.
- Decode temperature/airflow failure sentinels and the six-register controller serial.
- Represent special functions as one mutually exclusive mode.
- Add opt-in Constant Flow, comfort, ERV and legacy filter-alarm components.
- Add mock-based protocol regression tests, strict typing, CI, packaging checks and OIDC publishing.
- Document the 8443/8444 discrepancy and limits of hardware/firmware coverage.
