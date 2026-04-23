#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_JSON_PATH = PACKAGE_ROOT / "package.json"
CODEX_MANIFEST_PATH = PACKAGE_ROOT / ".codex-plugin" / "plugin.json"
CODEX_MARKETPLACE_PATH = PACKAGE_ROOT / ".agents" / "plugins" / "marketplace.json"


def load_package_metadata() -> dict:
    return json.loads(PACKAGE_JSON_PATH.read_text())


def build_codex_manifest(package_metadata: dict) -> dict:
    plugin_metadata = package_metadata.get("codexPlugin", {})
    return {
        "name": package_metadata["name"],
        "version": package_metadata["version"],
        "description": package_metadata["description"],
        "author": {
            "name": package_metadata["author"]["name"],
            "email": package_metadata["author"].get("email"),
            "url": package_metadata["author"]["url"],
        },
        "homepage": package_metadata["homepage"],
        "repository": package_metadata["repository"],
        "license": package_metadata["license"],
        "keywords": package_metadata["keywords"],
        "skills": "./skills/",
        "interface": plugin_metadata.get("interface", {}),
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
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n")


def build_codex_marketplace(package_metadata: dict) -> dict:
    marketplace_metadata = package_metadata.get("codexPlugin", {}).get("marketplace", {})
    return {
        "name": marketplace_metadata["name"],
        "interface": {
            "displayName": marketplace_metadata["displayName"],
        },
        "plugins": [
            {
                "name": package_metadata["name"],
                "source": {
                    "source": "local",
                    "path": marketplace_metadata["sourcePath"],
                },
                "policy": {
                    "installation": "AVAILABLE",
                    "authentication": "ON_INSTALL",
                },
                "category": marketplace_metadata["category"],
            }
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate plugin manifests from package.json metadata.")
    parser.add_argument("--check", action="store_true", help="Fail if manifests differ from generated output.")
    args = parser.parse_args()

    package_metadata = load_package_metadata()
    expected_codex = build_codex_manifest(package_metadata)
    expected_marketplace = build_codex_marketplace(package_metadata)

    if args.check:
        actual_codex = json.loads(CODEX_MANIFEST_PATH.read_text())
        actual_marketplace = json.loads(CODEX_MARKETPLACE_PATH.read_text())
        if actual_codex != expected_codex or actual_marketplace != expected_marketplace:
            print("Plugin manifests are out of sync with package.json.", file=sys.stderr)
            return 1
        return 0

    _write_json(CODEX_MANIFEST_PATH, expected_codex)
    _write_json(CODEX_MARKETPLACE_PATH, expected_marketplace)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
