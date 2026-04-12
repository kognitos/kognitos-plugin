#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_JSON_PATH = PACKAGE_ROOT / "package.json"
GENERATE_SCRIPT = PACKAGE_ROOT / "scripts" / "generate_manifests.py"


def parse_semver(version: str) -> tuple[int, int, int]:
    parts = version.split(".")
    if len(parts) != 3:
        raise ValueError(f"Invalid semver: {version}")
    return int(parts[0]), int(parts[1]), int(parts[2])


def bump(version: str, part: str) -> str:
    major, minor, patch = parse_semver(version)
    if part == "major":
        return f"{major + 1}.0.0"
    if part == "minor":
        return f"{major}.{minor + 1}.0"
    if part == "patch":
        return f"{major}.{minor}.{patch + 1}"
    raise ValueError(f"Unknown bump part: {part}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Bump the plugin version and regenerate all manifests.",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("part", nargs="?", choices=["major", "minor", "patch"],
                       help="Semver component to bump.")
    group.add_argument("--set", dest="explicit_version", metavar="VERSION",
                       help="Set an explicit version (e.g. 1.0.0).")
    args = parser.parse_args()

    package_data = json.loads(PACKAGE_JSON_PATH.read_text())
    old_version = package_data["version"]

    if args.explicit_version:
        parse_semver(args.explicit_version)  # validate
        new_version = args.explicit_version
    else:
        new_version = bump(old_version, args.part)

    if new_version == old_version:
        print(f"Version is already {old_version}.", file=sys.stderr)
        return 1

    package_data["version"] = new_version
    PACKAGE_JSON_PATH.write_text(json.dumps(package_data, indent=2) + "\n")
    print(f"{old_version} -> {new_version}")

    result = subprocess.run(
        [sys.executable, str(GENERATE_SCRIPT)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"Manifest generation failed:\n{result.stderr}", file=sys.stderr)
        return 1

    print("Manifests regenerated.")

    check = subprocess.run(
        [sys.executable, str(GENERATE_SCRIPT), "--check"],
        capture_output=True,
        text=True,
    )
    if check.returncode != 0:
        print(f"Manifest check failed:\n{check.stderr}", file=sys.stderr)
        return 1

    print(f"All files updated to {new_version}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
