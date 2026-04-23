# Environment Model

Use this reference when bootstrap work depends on clear environment boundaries.

## Base URL

`KOGNITOS_BASE_URL` is `https://app.us-1.kognitos.com` for US customers. EU customers swap `us-1` for `eu-1`.

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `KOGNITOS_TOKEN` | Yes | PAT from the Kognitos console (`kgn_pat_` prefix) |
| `KOGNITOS_BASE_URL` | Yes | API base URL |
| `KOGNITOS_ORGANIZATION_ID` | Yes | Organization to operate against |
| `KOGNITOS_WORKSPACE_ID` | Yes | Workspace to operate against |

## Token Scope

- A PAT authenticates the **user**, not a specific org or workspace.
- The user may have access to multiple orgs. Use the list-organizations endpoint to discover them.
- Workspace access is scoped per org. A token may be forbidden from orgs the user can see but doesn't own.

## What To Clarify Early

- Which org and workspace to target.
- Which credentials allow write operations (invoking automations, managing exceptions).
