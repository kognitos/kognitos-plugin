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
CLAUDE_MARKETPLACE_PATH = PACKAGE_ROOT / ".claude-plugin" / "marketplace.json"
CLAUDE_PLUGIN_PATH = PACKAGE_ROOT / ".claude-plugin" / "plugin.json"


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


def build_claude_marketplace(package_metadata: dict) -> dict:
    plugin_name = package_metadata.get("kognitosPlugin", {}).get("cursorName", package_metadata["name"])
    return {
        "$schema": "https://anthropic.com/claude-code/marketplace.schema.json",
        "name": package_metadata["name"],
        "owner": {
            "name": package_metadata["author"]["name"],
            "email": package_metadata["author"]["email"],
        },
        "metadata": {
            "description": package_metadata["description"],
        },
        "plugins": [
            {
                "name": plugin_name,
                "source": "./",
                "description": package_metadata["description"],
                "version": package_metadata["version"],
                "category": "development",
            }
        ],
    }


def build_claude_plugin(package_metadata: dict) -> dict:
    plugin_name = package_metadata.get("kognitosPlugin", {}).get("cursorName", package_metadata["name"])
    return {
        "name": plugin_name,
        "version": package_metadata["version"],
        "description": package_metadata["description"],
        "author": {
            "name": package_metadata["author"]["name"],
            "email": package_metadata["author"]["email"],
        },
        "homepage": package_metadata["homepage"],
        "repository": package_metadata["repository"],
        "license": package_metadata["license"],
        "keywords": package_metadata["keywords"],
    }


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate plugin manifests from package.json metadata.")
    parser.add_argument("--check", action="store_true", help="Fail if manifests differ from generated output.")
    args = parser.parse_args()

    package_metadata = load_package_metadata()
    expected = {
        PLUGIN_MANIFEST_PATH: build_plugin_manifest(package_metadata),
        CURSOR_MANIFEST_PATH: build_cursor_manifest(package_metadata),
        CLAUDE_MARKETPLACE_PATH: build_claude_marketplace(package_metadata),
        CLAUDE_PLUGIN_PATH: build_claude_plugin(package_metadata),
    }

    if args.check:
        ok = True
        for path, expected_data in expected.items():
            actual_data = json.loads(path.read_text())
            if actual_data != expected_data:
                rel = path.relative_to(PACKAGE_ROOT)
                print(f"{rel} is out of sync with package.json.", file=sys.stderr)
                ok = False
        return 0 if ok else 1

    for path, expected_data in expected.items():
        _write_json(path, expected_data)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
