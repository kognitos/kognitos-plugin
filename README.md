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
├── .claude-plugin/
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

## Quick Start

### 1. Get a Kognitos PAT

Generate a Personal Access Token from the Kognitos console. The token prefix is `kgn_pat_`.

### 2. Create `.env.local`

```bash
KOGNITOS_TOKEN=kgn_pat_<your-token>
KOGNITOS_REGION=us
KOGNITOS_ENV=dev
KOGNITOS_ORGANIZATION_ID=<your-org-id>
KOGNITOS_WORKSPACE_ID=<your-workspace-id>
```

If you don't know your org/workspace IDs yet, set `KOGNITOS_TOKEN`, `KOGNITOS_REGION`, and `KOGNITOS_ENV`, then use the bootstrap skill to discover them.

### 3. Install the plugin

#### Claude Code

```bash
/plugin marketplace add https://github.com/kognitos/kognitos-plugin
```

Then install the `kognitos` plugin from the marketplace list. Use `/kognitos-bootstrap` to verify your setup.

#### Cursor

Cursor-specific packaging is included in `.cursor-plugin/plugin.json`.

#### Codex / OpenAI

Codex-facing packaging is included in `.plugin/plugin.json`.

## API Base URL

The Kognitos API base URL follows this pattern:

```
https://app.<region>-<az>[.<env>].kognitos.com
```

| Region | Env | Base URL |
|--------|-----|----------|
| us | prod | `https://app.us-1.kognitos.com` |
| us | dev | `https://app.us-1.dev.kognitos.com` |
| eu | prod | `https://app.eu-1.kognitos.com` |

## Tooling Support

- Claude Code marketplace plugin via `.claude-plugin/marketplace.json`
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
