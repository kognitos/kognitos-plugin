# Changelog

## [0.2.0](https://github.com/kognitos/kognitos-plugin/compare/v0.1.0...v0.2.0) (2026-04-11)


### Features

* **api-client:** add runs API reference (list, get, events, outputs, pause/continue) ([#runs-api](references/runs-api.md))
* **api-client:** add exceptions API reference (inspect, manage, assign, reply, guides) ([#exceptions-api](references/exceptions-api.md))
* **api-client:** add scheduling API reference (CRUD, enable/disable, patterns) ([#scheduling-api](references/scheduling-api.md))
* **api-client:** add files API reference (upload, read, metadata) ([#files-api](references/files-api.md))
* **api-client:** add books/integrations API reference (search, procedures, connections) ([#books-api](references/books-api.md))
* **api-client:** add analytics API reference (run stats, insights, exception insights) ([#analytics-api](references/analytics-api.md))
* **api-client:** add run report template for structured audit trails ([#run-report](assets/run-report-template.md))
* **ci:** add GitHub Actions workflow for validation and semantic-release
* **ci:** add semantic-release config with conventional commits


### Bug Fixes

* **api-client:** distinguish awaiting_guidance from failed in run state documentation
* **api-client:** add user confirmation step before invoking automations


### Chores

* remove unused .claude/ directory
* add .claude-plugin/marketplace.json to manifest generation pipeline
* add bump_version.py script for local version management


## [0.1.0](https://github.com/kognitos/kognitos-plugin/releases/tag/v0.1.0) (2026-04-11)


### Features

* initial plugin with 6 skills: bootstrap, app-development, sop-development, api-client, debugging, deployment
* automation creation and invocation via AI agent API
* multi-platform manifests (Claude Code, Cursor, Codex)
* validation scripts for skill structure and manifest sync
