# Changelog

## 0.1.0a4 - 2026-09-09

- Correct the Comfort manual temperature to the physical 10-45 °C range documented by Thessla Green (raw 20-90 with a 0.5 multiplier).
- Keep the temporary airflow and temperature setpoints read-only because their activation requires atomic three-register commands.
- Extend protocol provenance notes to the reviewed large-f protocol and clarify the model-dependent pressure-filter alarm.
- Export `ThesslaGreenComponent` as part of the public API for integrations that need a stable component type.

## 0.1.0a3 - 2026-09-08

- Generalize the public API from a single product generation to Thessla Green devices.
- Add product-family metadata with a future-proof unknown profile.
- Correct the documented Comfort temperature range to 20-90 °C.
- Make temporary airflow and temperature setpoints read-only until the required atomic command blocks are implemented.
- Replace the ambiguous legacy 8444 option with an explicitly model-dependent pressure-filter alarm.
- Cross-check the common map against manufacturer Home and series-4 protocols.

## 0.1.0a2 - 2026-09-08

- Replace the release-on-GitHub-Release workflow with a tag-driven release workflow.
- Publish to PyPI automatically after validating the tag and green CI on `main`.
- Create the GitHub Release automatically after a successful PyPI publication.

## 0.1.0a1 - 2026-09-08

- Add backend-independent asynchronous Thessla Green components and validated writes.
- Respect the 16-register request limit and avoid undeclared address gaps.
- Decode temperature/airflow failure sentinels and the six-register controller serial.
- Represent special functions as one mutually exclusive mode.
- Add opt-in Constant Flow, comfort and ERV components.
- Add mock-based protocol regression tests, strict typing, CI, packaging checks and OIDC publishing.
