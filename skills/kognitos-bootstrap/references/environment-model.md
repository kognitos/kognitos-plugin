# Environment Model

Use this reference when bootstrap work depends on clear environment boundaries.

## Kognitos Environments

| Environment | Base URL Pattern | Use |
|-------------|-----------------|-----|
| dev | `https://app.<region>-1.dev.kognitos.com` | Development and testing |
| prod | `https://app.<region>-1.kognitos.com` | Production |

Regions: `us`, `eu`, `uk`. The availability zone defaults to `1`.

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `KOGNITOS_TOKEN` | Yes | — | PAT from the Kognitos console (`kgn_pat_` prefix) |
| `KOGNITOS_REGION` | No | `us` | API region |
| `KOGNITOS_ENV` | No | `prod` | Target environment (`prod` or `dev`) |
| `KOGNITOS_ORGANIZATION_ID` | Yes | — | Organization to operate against |
| `KOGNITOS_WORKSPACE_ID` | Yes | — | Workspace to operate against |

## Token Scope

- A PAT authenticates the **user**, not a specific org or workspace.
- The user may have access to multiple orgs. Use the list-organizations endpoint to discover them.
- Workspace access is scoped per org. A token may be forbidden from orgs the user can see but doesn't own.

## Recommended Separation

- **Dev**: real integrations with reversible test data. Safe for exploratory API calls.
- **Prod**: no exploratory changes, no undocumented secrets handling.

## What To Clarify Early

- Which environment the PAT was issued against (dev tokens won't authenticate against prod).
- Which org and workspace to target.
- Which credentials allow write operations (invoking automations, managing exceptions).
