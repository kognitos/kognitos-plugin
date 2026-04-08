#!/usr/bin/env python3

from __future__ import annotations

import argparse
import shutil
import sys


DEFAULT_COMMANDS = ["git", "python3", "node", "npm"]


def main() -> int:
    parser = argparse.ArgumentParser(description="Check for required local commands.")
    parser.add_argument("commands", nargs="*", default=DEFAULT_COMMANDS)
    args = parser.parse_args()

    missing = [command for command in args.commands if shutil.which(command) is None]
    if missing:
        print(f"Missing commands: {', '.join(missing)}", file=sys.stderr)
        return 1

    print(f"All commands available: {', '.join(args.commands)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
