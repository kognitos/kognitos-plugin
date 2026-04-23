# Kognitos Plugin

Structured Kognitos development skills — bootstrap, app development, SOP design, API integration, debugging, and deployment — packaged for Claude Code, Codex CLI, and Cursor.

The canonical content is the skill set under `skills/`. Each skill is a self-contained playbook with a default `SKILL.md` workflow and progressive-disclosure references, scripts, and assets.

## What you get

Six skills, installable as a single plugin:

| Skill | Use when you need to… |
| --- | --- |
| `kognitos-bootstrap` | Set up a Kognitos workspace, verify prerequisites, discover org/workspace IDs from a PAT. |
| `kognitos-app-development` | Build a Kognitos-backed app with clear architecture and Lattice UI patterns. |
| `kognitos-sop-development` | Design and refine Kognitos SOPs with traceable decision points. |
| `kognitos-api-client` | Integrate Kognitos APIs through explicit adapters and stable request contracts. |
| `kognitos-debugging` | Isolate failure boundaries and capture evidence for a Kognitos bug. |
| `kognitos-deployment` | Promote changes across environments with explicit release checks. |

## Install

The plugin supports three surfaces. Pick the one that matches your editor or CLI.

### Claude Code

```
/plugin marketplace add https://github.com/kognitos/kognitos-plugin
/plugin install kognitos
```

After install, skills auto-invoke when your prompt matches one of the descriptions above. To verify the install end-to-end, ask Claude Code to run the bootstrap skill:

> run the kognitos bootstrap skill

It will walk through the credential check and, if your PAT is set, confirm API connectivity.

### Codex CLI

This repo includes both the plugin manifest at `.codex-plugin/plugin.json` and a repo-local marketplace entry at `.agents/plugins/marketplace.json`, which points Codex at the repo root (`./`) for local distribution.

```bash
git clone https://github.com/kognitos/kognitos-plugin.git
cd kognitos-plugin
codex
```

Then in the Codex CLI:

1. Run `/plugins`
2. Open the `Local Kognitos Plugins` marketplace
3. Select `Kognitos Plugin`
4. Choose `Install plugin`

After install, start a new thread and ask Codex to use a Kognitos skill directly or describe the task in natural language. Skills load from the `./skills/` path declared in the manifest and can also be invoked explicitly with `@Kognitos Plugin` or by naming the skill.

If the plugin does not appear immediately, restart Codex from the repo root and reopen `/plugins`.

See the [Codex plugins overview](https://developers.openai.com/codex/plugins), [build plugins guide](https://developers.openai.com/codex/plugins/build), and [skills docs](https://developers.openai.com/codex/skills) for the current Codex plugin and skill conventions.

### Cursor

Cursor does not have a plugin system — it uses project rules under `.cursor/rules/`. This repo ships `.cursor/rules/kognitos.mdc`, which tells Cursor's model that the canonical Kognitos guidance lives in `skills/` and how to find the right one.

To use it in your own Kognitos project:

1. Copy the `skills/` directory and `.cursor/rules/kognitos.mdc` into your project (or reference this repo as a git submodule).
2. Open the project in Cursor. The rule is `alwaysApply: true`, so it attaches to every chat automatically.
3. Ask about any Kognitos task — Cursor will open the matching `SKILL.md` before proposing changes.

If you'd rather not copy files, you can open this repo alongside your project in a Cursor multi-root workspace; the rule will still apply.

## First run

After install, set up credentials once.

### 1. Get a Kognitos PAT

Generate a Personal Access Token from the Kognitos console. Tokens are prefixed `kgn_pat_`.

### 2. Create `.env.local`

In the root of the project where you'll use the plugin:

```bash
KOGNITOS_TOKEN=kgn_pat_<your-token>
KOGNITOS_BASE_URL=https://app.us-1.kognitos.com
KOGNITOS_ORGANIZATION_ID=<your-org-id>
KOGNITOS_WORKSPACE_ID=<your-workspace-id>
```

If you don't know your org or workspace IDs yet, leave them blank. Set `KOGNITOS_TOKEN` and `KOGNITOS_BASE_URL`, then run `kognitos-bootstrap` — it discovers the IDs from your token.

### 3. API base URL

`KOGNITOS_BASE_URL` is `https://app.us-1.kognitos.com` for US customers. EU customers swap `us-1` for `eu-1`.

## Repository layout

```text
kognitos-plugin/
├── .agents/plugins/     # Codex repo-local marketplace entry (generated)
├── .claude-plugin/      # Claude Code marketplace manifest
├── .codex-plugin/       # Codex plugin manifest (generated)
├── .cursor/rules/       # Cursor project rules (hand-authored)
├── package.json         # Canonical metadata source
├── scripts/             # Manifest generation and repo validation
└── skills/              # Canonical skill content (SKILL.md + references/scripts/assets)
```

Each skill follows progressive disclosure:

- `SKILL.md` — default workflow
- `references/` — deeper guidance, pulled in only when `SKILL.md` links there
- `scripts/` — repeatable helpers
- `assets/` — templates and examples

## Troubleshooting

**"Plugin installed but nothing happens when I ask about Kognitos."**
Skills auto-invoke based on prompt matches against their descriptions. Try referring to the domain directly: "use the kognitos bootstrap skill" or "build a Kognitos app that…".

**`.env.local` values not picked up.**
Confirm the file sits at the root of the working directory the agent is running in. The skills read from the current working directory, not from any parent.

**Bootstrap reports "unknown region" or a 404 on the base URL.**
Cross-check the region/env combination against the table above. Dev in EU is not publicly available yet.

**Cursor rule isn't being applied.**
Check that `.cursor/rules/kognitos.mdc` exists in the project opened in Cursor (not just in a sibling folder). Cursor loads rules from the root of the active project.

## Maintaining the repo

`package.json` is the single source of truth for plugin metadata. The Codex manifest and repo-local marketplace file are generated from it.

```bash
npm run build:manifests          # regenerate Codex plugin and marketplace manifests
npm run build:manifests:check    # fail if manifest is out of sync
npm run validate                 # validate skills, manifests, and cursor rules
```

Or call the Python scripts directly:

```bash
python3 scripts/generate_manifests.py
python3 scripts/generate_manifests.py --check
python3 scripts/validate_repo.py
```

## Contributing

Keep skill content in `skills/` only — don't duplicate it per tool. Claude Code reads it directly, Codex installs it through the plugin manifest and repo marketplace entry, and Cursor points at it through the rule in `.cursor/rules/`.

## License

MIT — see [LICENSE](LICENSE).
