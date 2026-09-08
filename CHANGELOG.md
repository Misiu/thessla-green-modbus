# Changelog

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
