#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_JSON_PATH = PACKAGE_ROOT / "package.json"
PLUGIN_MANIFEST_PATH = PACKAGE_ROOT / ".plugin" / "plugin.json"
CURSOR_MANIFEST_PATH = PACKAGE_ROOT / ".cursor-plugin" / "plugin.json"


def load_package_metadata() -> dict:
    return json.loads(PACKAGE_JSON_PATH.read_text())


def build_plugin_manifest(package_metadata: dict) -> dict:
    return {
        "name": package_metadata["name"],
        "version": package_metadata["version"],
        "description": package_metadata["description"],
        "author": {
            "name": package_metadata["author"]["name"],
            "url": package_metadata["author"]["url"],
        },
        "repository": package_metadata["repository"],
        "license": package_metadata["license"],
        "keywords": package_metadata["keywords"],
    }


def build_cursor_manifest(package_metadata: dict) -> dict:
    cursor_metadata = package_metadata.get("kognitosPlugin", {})
    return {
        "name": cursor_metadata.get("cursorName", package_metadata["name"]),
        "version": package_metadata["version"],
        "description": cursor_metadata.get("cursorDescription", package_metadata["description"]),
        "author": {
            "name": package_metadata["author"]["name"],
            "email": package_metadata["author"]["email"],
        },
        "homepage": package_metadata["homepage"],
        "repository": package_metadata["repository"],
        "license": package_metadata["license"],
        "keywords": package_metadata["keywords"],
        "skills": "skills",
    }


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate plugin manifests from package.json metadata.")
    parser.add_argument("--check", action="store_true", help="Fail if manifests differ from generated output.")
    args = parser.parse_args()

    package_metadata = load_package_metadata()
    expected_plugin = build_plugin_manifest(package_metadata)
    expected_cursor = build_cursor_manifest(package_metadata)

    if args.check:
        actual_plugin = json.loads(PLUGIN_MANIFEST_PATH.read_text())
        actual_cursor = json.loads(CURSOR_MANIFEST_PATH.read_text())

        if actual_plugin != expected_plugin or actual_cursor != expected_cursor:
            print("Plugin manifests are out of sync with package.json.", file=sys.stderr)
            return 1
        return 0

    _write_json(PLUGIN_MANIFEST_PATH, expected_plugin)
    _write_json(CURSOR_MANIFEST_PATH, expected_cursor)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
