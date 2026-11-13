---
name: kognitos-bootstrap
description: Set up a Kognitos application workspace, verify prerequisites, and establish the initial development baseline.
license: MIT
---

# Kognitos Bootstrap

Use this skill when a repository needs to be prepared for Kognitos application development, or when you need to verify a local environment before making changes.

## Default Flow

1. Check for a `.env.local` file in the project root. If missing, copy [assets/bootstrap-template.env](assets/bootstrap-template.env) to `.env.local` and have the user fill in `KOGNITOS_TOKEN` with an API key (see [references/setup-checklist.md](references/setup-checklist.md) for how to create one).
2. Source `.env.local` and verify the token works by calling the list-organizations endpoint (see [references/setup-checklist.md](references/setup-checklist.md)).
3. If `KOGNITOS_ORGANIZATION_ID` or `KOGNITOS_WORKSPACE_ID` are empty, list the user's orgs and workspaces and help them pick values. Pick the organization the key was created in; the key gets `403` in every other one.
4. Run the preflight helper in [scripts/preflight_check.py](scripts/preflight_check.py) to verify local CLI tools.
5. Use [references/environment-model.md](references/environment-model.md) when environment boundaries, key scope, or platform limits need to be clarified.

## MCP Server or REST API

Kognitos also runs an MCP server (`https://mcp.us-1.kognitos.com/`) that gives an AI assistant tools for automations, runs, exceptions, schedules, integrations, analytics, and files.

- Use the **MCP server** when you or the user want to explore, operate, or triage a workspace from the assistant itself, with no code to write.
- Use the **REST API** (this plugin's `kognitos-api-client` skill) for application code, scripts, and CI, and for anything the MCP tools don't cover, such as building agents in the Agent Builder.

See [references/mcp-server.md](references/mcp-server.md) to connect a client.

## When To Load More

- For the full setup checklist: [references/setup-checklist.md](references/setup-checklist.md)
- For environment boundaries, key scope, and platform limits: [references/environment-model.md](references/environment-model.md)
- For connecting an MCP client: [references/mcp-server.md](references/mcp-server.md)
- For a starter `.env.local` template: [assets/bootstrap-template.env](assets/bootstrap-template.env)

## Notes

- `KOGNITOS_BASE_URL` is the host you sign in to, without `/api/v1`: `https://app.us-1.kognitos.com` for most organizations. Organizations hosted in another region use that region's host.
- API keys (Personal Access Tokens) use the `kgn_pat_` prefix and authenticate via `Authorization: Bearer <token>`.
- A key belongs to the organization it was created in and is limited to the workspaces and permission level chosen when it was created. Org and workspace IDs still go in every request path.
