# Releasing

No PyPI project or publisher is created automatically. This setup must be completed by the repository/package owner before the first release.

## One-time setup

1. Create a GitHub environment named `pypi`. Add required reviewers to protect production publishing.
2. In PyPI, register a pending Trusted Publisher (or a publisher for an existing project) with these exact values:

   | Field | Value |
   | --- | --- |
   | Project | `thessla-green-modbus` |
   | Owner | `Misiu` |
   | Repository | `thessla-green-modbus` |
   | Workflow | `publish.yml` |
   | Environment | `pypi` |

3. Confirm that the package name is available or already controlled by you. Do not store PyPI API tokens in this repository.
4. Protect `main` and `develop` with required CI checks and disallow force pushes. Workflow files alone do not configure repository branch protection.

Official publisher documentation: https://docs.pypi.org/trusted-publishers/adding-a-publisher/

## Release procedure

Update the literal version in `pyproject.toml` and document changes in `CHANGELOG.md`. Run `bash script/run_checks.sh`. Open a `develop` to `main` pull request and merge only after all checks pass. Tag the merged commit with the exact version, optionally prefixed with `v`, for example `v0.1.0a1`. Publish a GitHub release for that tag.

The release workflow reruns CI, verifies that the commit belongs to `main`, requires the tag to equal the package version, builds wheel and sdist, validates metadata, and uploads the distributions using OIDC with attestations. The publishing job has no checkout and no package build; it only downloads the verified artifacts. It runs in the protected `pypi` environment.

An alpha tag does not imply hardware validation. Record tested hardware and firmware explicitly before promoting a stable version. Do not reuse a version already uploaded to PyPI. Failed publication is not evidence of a successful release; inspect the `publish` job and the resulting PyPI project.
