#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize existing local debug artifacts.")
    parser.add_argument("paths", nargs="*", default=["."])
    args = parser.parse_args()

    summary = []
    for raw_path in args.paths:
        path = Path(raw_path)
        if not path.exists():
            summary.append({"path": raw_path, "exists": False})
            continue

        if path.is_file():
            summary.append({"path": raw_path, "exists": True, "type": "file", "size": path.stat().st_size})
            continue

        files = sorted(str(item) for item in path.rglob("*") if item.is_file())[:25]
        summary.append({"path": raw_path, "exists": True, "type": "directory", "files": files})

    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
