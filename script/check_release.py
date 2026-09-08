#!/usr/bin/env python3
"""Validate a release tag without rewriting the source package's version."""

import re
import sys
import tomllib
from pathlib import Path


def check_release(tag: str, version: str) -> None:
    """Require an exact PEP 440-style tag (an optional leading v is allowed)."""
    normalized = tag.removeprefix("v")
    if not re.fullmatch(r"\d+\.\d+\.\d+(?:(?:a|b|rc)\d+)?", normalized):
        raise ValueError("Use X.Y.Z, X.Y.ZaN, X.Y.ZbN or X.Y.ZrcN")
    if normalized != version:
        raise ValueError(f"Tag {tag!r} does not match package version {version!r}")


if __name__ == "__main__":
    project = tomllib.loads(Path("pyproject.toml").read_text())
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python script/check_release.py TAG")
    try:
        check_release(sys.argv[1], project["project"]["version"])
    except ValueError as err:
        raise SystemExit(str(err)) from err
