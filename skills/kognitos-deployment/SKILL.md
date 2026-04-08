---
name: kognitos-deployment
description: Prepare and promote Kognitos application changes through environments with explicit release checks and operational clarity.
license: MIT
---

# Kognitos Deployment

Use this skill when changes are moving from development toward shared environments or production.

## Default Flow

1. Use [references/release-checklist.md](references/release-checklist.md) to confirm code, workflow, and environment readiness.
2. Use [references/environment-promotion.md](references/environment-promotion.md) when a change crosses environment boundaries.
3. Use [assets/deployment-checklist.md](assets/deployment-checklist.md) as the final ship/no-ship checklist.

## When To Load More

- For pre-release gating: [references/release-checklist.md](references/release-checklist.md)
- For promotion sequencing and rollback thinking: [references/environment-promotion.md](references/environment-promotion.md)
- For final review: [assets/deployment-checklist.md](assets/deployment-checklist.md)

## Notes

- Treat SOP, app, and configuration changes as a coordinated release when they affect the same user path.
- Prefer reversible rollout steps over one-way changes.
