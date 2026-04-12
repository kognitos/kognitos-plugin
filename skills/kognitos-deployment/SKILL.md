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

## Automation Scheduling and Publishing

When deploying automations, use the API endpoints from the `kognitos-api-client` skill:

- **Compare DRAFT vs PUBLISHED** — use the `query` endpoint with `stage` parameter to inspect what's in progress vs what's live. See [automation-agent-api.md](../kognitos-api-client/references/automation-agent-api.md).
- **Set up schedules** — create, update, enable, or disable recurring runs. See [scheduling-api.md](../kognitos-api-client/references/scheduling-api.md).
- **Monitor post-deployment** — use run stats and exception insights to verify the deployment is healthy. See [analytics-api.md](../kognitos-api-client/references/analytics-api.md).

## When To Load More

- For pre-release gating: [references/release-checklist.md](references/release-checklist.md)
- For promotion sequencing and rollback thinking: [references/environment-promotion.md](references/environment-promotion.md)
- For final review: [assets/deployment-checklist.md](assets/deployment-checklist.md)
- For schedule management: [kognitos-api-client/references/scheduling-api.md](../kognitos-api-client/references/scheduling-api.md)
- For post-deployment health metrics: [kognitos-api-client/references/analytics-api.md](../kognitos-api-client/references/analytics-api.md)

## Notes

- Treat SOP, app, and configuration changes as a coordinated release when they affect the same user path.
- Prefer reversible rollout steps over one-way changes.
- After deployment, review run reports from the first few scheduled runs to catch issues early.
