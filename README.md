# Kognitos Plugin

`kognitos-plugin` is a skills-first repository for Kognitos application development workflows.

The canonical content lives under `skills/`. The repo also includes Vercel-style packaging in `.plugin/plugin.json` and `.cursor-plugin/plugin.json`.

## Scope

The initial skill set covers:

- Kognitos bootstrap and environment setup
- Application architecture and UI development
- SOP and workflow development
- API client integration
- Debugging and evidence capture
- Deployment and environment promotion

## Repository Layout

```text
kognitos-plugin/
├── .claude/
├── .cursor-plugin/
├── .plugin/
├── package.json
├── scripts/
└── skills/
```

Each skill uses progressive disclosure:

- `SKILL.md` for the default workflow
- `references/` for deeper guidance
- `scripts/` for repeatable helpers
- `assets/` for templates and examples

## Skills

- `kognitos-bootstrap`
- `kognitos-app-development`
- `kognitos-sop-development`
- `kognitos-api-client`
- `kognitos-debugging`
- `kognitos-deployment`

## Using The Repo

### Local Use

Clone the repository and use `skills/` as the canonical skill source:

```bash
git clone https://github.com/kognitos/kognitos-plugin.git
cd kognitos-plugin
```

### Cursor

Cursor-specific packaging is included in `.cursor-plugin/plugin.json`.

- Use this repo as the source for Cursor plugin installation or local plugin development.
- The plugin manifest points Cursor at the shared `skills/` directory.

### Codex / OpenAI

Codex-facing packaging is included in `.plugin/plugin.json`.

- The repo is ready for Codex-compatible packaging and local workflow use.
- Today, treat `skills/` as the main portable integration surface.
- Keep `.plugin/` in place so the repo stays aligned with the expected plugin path as that distribution model matures.

### Claude Code

Claude workspace support is included via `.claude/settings.json`.

- Use the shared `skills/` directory as the canonical content source.
- Keep `.claude/` minimal and avoid maintaining a second skill tree.

## Tooling Support

- Agent Skills-compatible skill layout via `skills/`
- Codex/OpenAI packaging readiness via `.plugin/plugin.json`
- Cursor plugin packaging via `.cursor-plugin/plugin.json`
- Claude Code workspace support via `.claude/settings.json`

## Validation

Generate plugin manifests from `package.json`:

```bash
python3 scripts/generate_manifests.py
```

Check that manifests and skill structure are valid:

```bash
python3 scripts/generate_manifests.py --check
python3 scripts/validate_repo.py
```

Or run the npm-style scripts from `package.json`:

```bash
npm run build:manifests
npm run build:manifests:check
npm run validate
```

## Open Source Notes

- `package.json` is the canonical source for package name, version, description, and author metadata.
- `.plugin/plugin.json` and `.cursor-plugin/plugin.json` are generated from `package.json`.
- Keep the skill content in `skills/`; do not duplicate it per tool.
