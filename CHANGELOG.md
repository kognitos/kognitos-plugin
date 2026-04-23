# Changelog

## 1.0.0 (2026-04-23)

Initial public release of the Kognitos plugin — structured skills for working with the Kognitos platform from Claude Code, Codex, and Cursor.

### Skills

* **kognitos-bootstrap** — workspace setup, prerequisite verification, and initial development baseline
* **kognitos-api-client** — integration with Kognitos APIs (automation agent, runs, exceptions, scheduling, files, books, analytics) with curl and Node SDK examples
* **kognitos-app-development** — building Kognitos-backed applications with Lattice-aligned UI patterns
* **kognitos-sop-development** — designing SOPs with clear boundaries, traceable decision points, and maintainable workflow patterns
* **kognitos-debugging** — isolating failure boundaries and capturing evidence
* **kognitos-deployment** — promoting changes through environments with explicit release checks

### Platform Integrations

* Claude Code marketplace manifest (`.claude-plugin/marketplace.json`)
* Codex plugin manifest (`.codex-plugin/plugin.json`)
* Cursor rules (`.cursor/rules/kognitos.mdc`)
* Agents marketplace manifest (`.agents/plugins/marketplace.json`)

### Tooling

* `scripts/generate_manifests.py` — single-source manifest generation from `package.json`
* `scripts/validate_repo.py` — skill structure and manifest-sync validation
* Automated PR review workflow via team-request trigger ([#8](https://github.com/kognitos/kognitos-plugin/pull/8))
* GitHub Actions CI (validate + CodeQL + semantic-release)
