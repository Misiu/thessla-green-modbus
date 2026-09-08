# Changelog

## 0.1.0a2 - 2026-09-08

- Replace the release-on-GitHub-Release workflow with a tag-driven release workflow.
- Publish to PyPI automatically after validating the tag and green CI on `main`.
- Create the GitHub Release automatically after a successful PyPI publication.

## 0.1.0a1 - 2026-09-08

- Add backend-independent asynchronous AirPack4 components and validated writes.
- Respect the 16-register request limit and avoid undeclared address gaps.
- Decode temperature/airflow failure sentinels and the six-register controller serial.
- Represent special functions as one mutually exclusive mode.
- Add opt-in Constant Flow, comfort, ERV and legacy filter-alarm components.
- Add mock-based protocol regression tests, strict typing, CI, packaging checks and OIDC publishing.
- Document the 8443/8444 discrepancy and limits of hardware/firmware coverage.
