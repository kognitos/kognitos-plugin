# Environment Model

Use this reference when bootstrap work depends on clear environment boundaries.

## Base URL

`KOGNITOS_BASE_URL` is the host you sign in to, without `/api/v1`. It is `https://app.us-1.kognitos.com` for most organizations; organizations hosted in another region use that region's host (for example `https://app.uk-1.kognitos.com`). API paths start at `${KOGNITOS_BASE_URL}/api/v1`.

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `KOGNITOS_TOKEN` | Yes | API key (Personal Access Token, `kgn_pat_` prefix) |
| `KOGNITOS_BASE_URL` | Yes | Host you sign in to |
| `KOGNITOS_ORGANIZATION_ID` | Yes | Organization to operate against |
| `KOGNITOS_WORKSPACE_ID` | Yes | Workspace to operate against |

## Key Scope

- A key belongs to the **organization** it was created in. `GET /me/organizations` lists every organization the user belongs to, but the key gets `403` in all of them except its own.
- A key covers **all workspaces** of that organization or only **specific workspaces**, chosen when it is created.
- A key has a **permission level**: **All** (read and write), **Read only** (list, get, and query calls), or **Restricted** (permissions picked per resource). A read-only key gets `403` on invoke, publish, reply, assign, and archive calls.
- Keys expire after the period chosen at creation (7 days to 1 year), and an organization can hold at most 10 keys. A key that stops authenticating has usually expired or been deleted: create a new one.
- Actions taken with a key show as **Personal Access Token** in the organization's audit log.

## Platform Limits

Design clients around these limits:

- A REST request that runs longer than **15 seconds** fails with `504`. Run events and agent conversations are allowed longer. Narrow slow list and search calls (for example with a time range filter) rather than retrying them unchanged.
- An uploaded file can be at most **800 MB**.
- IDP reads at most 100 pages of a document (20 with an AWS Bedrock connection) and skips the rest without an exception.

The Kognitos documentation's "Platform Limits" page has the full list.

## What To Clarify Early

- Which org and workspace to target, and whether the key's scope includes that workspace.
- Whether the key's permission level allows write operations (invoking automations, managing exceptions), or only reads.
- Whether the user will work through the REST API, the MCP server ([mcp-server.md](mcp-server.md)), or both.
