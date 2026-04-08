---
name: kognitos-bootstrap
description: Set up a Kognitos application workspace, verify prerequisites, and establish the initial development baseline.
license: MIT
---

# Kognitos Bootstrap

Use this skill when a repository needs to be prepared for Kognitos application development, or when you need to sanity-check a local environment before making changes.

## Default Flow

1. Confirm the stack and deployment target.
2. Run the preflight helper in [scripts/preflight_check.py](scripts/preflight_check.py).
3. Use [references/setup-checklist.md](references/setup-checklist.md) to close any setup gaps.
4. Use [references/environment-model.md](references/environment-model.md) when environment boundaries or secrets handling need to be clarified.

## When To Load More

- For day-one environment work: [references/setup-checklist.md](references/setup-checklist.md)
- For local vs shared environment decisions: [references/environment-model.md](references/environment-model.md)
- For a concrete starter checklist or env template: [assets/bootstrap-template.env](assets/bootstrap-template.env)

## Notes

- Keep the bootstrap path generic. Template-specific guidance belongs here only as an example, not as the primary framing.
- Prefer verifying assumptions early: required CLIs, runtime versions, auth dependencies, and known environment variables.
