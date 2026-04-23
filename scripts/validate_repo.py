#!/usr/bin/env python3

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = PACKAGE_ROOT / "skills"
PACKAGE_JSON_PATH = PACKAGE_ROOT / "package.json"
CODEX_MANIFEST_PATH = PACKAGE_ROOT / ".codex-plugin" / "plugin.json"
CODEX_MARKETPLACE_PATH = PACKAGE_ROOT / ".agents" / "plugins" / "marketplace.json"
CURSOR_RULES_DIR = PACKAGE_ROOT / ".cursor" / "rules"
FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
REQUIRED_FRONTMATTER_KEYS = {"name", "description"}


def parse_frontmatter(skill_path: Path) -> dict[str, str]:
    content = skill_path.read_text()
    match = FRONTMATTER_RE.match(content)
    if not match:
        raise ValueError(f"{skill_path} is missing YAML frontmatter")

    data: dict[str, str] = {}
    for raw_line in match.group(1).splitlines():
        if ":" not in raw_line:
            continue
        key, value = raw_line.split(":", 1)
        data[key.strip()] = value.strip().strip('"')

    missing = REQUIRED_FRONTMATTER_KEYS - set(data)
    if missing:
        raise ValueError(f"{skill_path} is missing frontmatter keys: {', '.join(sorted(missing))}")
    return data


def validate_links(markdown_path: Path) -> list[str]:
    errors: list[str] = []
    content = markdown_path.read_text()
    for target in LINK_RE.findall(content):
        if target.startswith("http://") or target.startswith("https://") or target.startswith("#"):
            continue
        target_path = (markdown_path.parent / target).resolve()
        if not target_path.exists():
            errors.append(f"{markdown_path}: missing link target {target}")
    return errors


def validate_skill_dir(skill_dir: Path) -> list[str]:
    errors: list[str] = []
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.exists():
        return [f"{skill_dir}: missing SKILL.md"]

    try:
        frontmatter = parse_frontmatter(skill_file)
    except ValueError as exc:
        return [str(exc)]

    if frontmatter["name"] != skill_dir.name:
        errors.append(f"{skill_file}: frontmatter name must match directory name")

    references_dir = skill_dir / "references"
    if not references_dir.exists():
        errors.append(f"{skill_dir}: missing references/ directory")

    errors.extend(validate_links(skill_file))

    for extra_markdown in skill_dir.rglob("*.md"):
        if extra_markdown.name == "SKILL.md":
            continue
        errors.extend(validate_links(extra_markdown))

    return errors


def validate_manifests() -> list[str]:
    errors: list[str] = []
    package_metadata = json.loads(PACKAGE_JSON_PATH.read_text())
    marketplace_metadata = package_metadata.get("codexPlugin", {}).get("marketplace", {})
    codex_manifest = json.loads(CODEX_MANIFEST_PATH.read_text())
    marketplace_manifest = json.loads(CODEX_MARKETPLACE_PATH.read_text())

    if codex_manifest.get("name") != package_metadata["name"]:
        errors.append(".codex-plugin/plugin.json name is out of sync with package.json")
    if codex_manifest.get("version") != package_metadata["version"]:
        errors.append(".codex-plugin/plugin.json version is out of sync with package.json")
    if codex_manifest.get("skills") != "./skills/":
        errors.append(".codex-plugin/plugin.json must point skills at ./skills/")
    if codex_manifest.get("homepage") != package_metadata["homepage"]:
        errors.append(".codex-plugin/plugin.json homepage is out of sync with package.json")
    if codex_manifest.get("author", {}).get("email") != package_metadata["author"]["email"]:
        errors.append(".codex-plugin/plugin.json author email is out of sync with package.json")
    if not codex_manifest.get("interface"):
        errors.append(".codex-plugin/plugin.json must include interface metadata for install surfaces")
    if marketplace_manifest.get("plugins", [{}])[0].get("name") != package_metadata["name"]:
        errors.append(".agents/plugins/marketplace.json plugin name is out of sync with package.json")
    marketplace_path = marketplace_manifest.get("plugins", [{}])[0].get("source", {}).get("path")
    if marketplace_path != marketplace_metadata.get("sourcePath"):
        errors.append(".agents/plugins/marketplace.json source.path is out of sync with package.json")
    return errors


def validate_cursor_rules() -> list[str]:
    if not CURSOR_RULES_DIR.exists():
        return [".cursor/rules/ directory is missing"]
    if not any(CURSOR_RULES_DIR.glob("*.mdc")):
        return [".cursor/rules/ must contain at least one .mdc rule"]
    return []


def main() -> int:
    errors: list[str] = []

    if not SKILLS_ROOT.exists():
        errors.append("skills/ directory is missing")
    else:
        for skill_dir in sorted(path for path in SKILLS_ROOT.iterdir() if path.is_dir()):
            errors.extend(validate_skill_dir(skill_dir))

    errors.extend(validate_manifests())
    errors.extend(validate_cursor_rules())

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
