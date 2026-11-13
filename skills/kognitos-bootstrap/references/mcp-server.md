# Kognitos MCP Server

Use this reference when the user wants their AI assistant to work in Kognitos directly, through the Model Context Protocol, instead of through code that calls the REST API.

## Server

- URL: `https://mcp.us-1.kognitos.com/` (Streamable HTTP transport, nothing to install). Organizations hosted in another region use that region's host, for example `https://mcp.uk-1.kognitos.com/`.
- Auth: **OAuth** for interactive clients (the client opens the Kognitos sign-in page and refreshes the token itself), or an **API key** in `Authorization: Bearer <key>` for scripts and CI. The key's workspace scope and permission level apply to the tools too.
- The OAuth callback port is `3777`. Clients that let you set it must use it, or sign-in fails with a callback URL mismatch.

## Connect A Client

Claude Code, with OAuth:

```bash
claude mcp add --transport http --callback-port 3777 kognitos https://mcp.us-1.kognitos.com/
```

Claude Code, with an API key:

```bash
claude mcp add --transport http kognitos https://mcp.us-1.kognitos.com/ \
  --header "Authorization: Bearer ${KOGNITOS_TOKEN}"
```

Cursor, Claude Desktop, VS Code, and other clients take the same URL, transport, and callback port in their MCP settings. Claude.ai and ChatGPT add it as a custom connector with the URL only. Verify by asking the assistant to list your Kognitos workspaces.

The public setup guide is the Kognitos documentation's "Connect an AI Client" page.

## Tools

The server exposes 19 tools. Read and write actions on a resource are separate tools.

| Area | Tools |
| --- | --- |
| Organizations and workspaces | `kognitos_list_organizations`, `kognitos_list_workspaces` |
| Automations | `kognitos_automations`, `kognitos_create_automation`, `kognitos_manage_automation`, `kognitos_invoke_automation` |
| Automation builder threads | `kognitos_threads`, `kognitos_manage_thread` |
| Runs | `kognitos_runs`, `kognitos_control_run` |
| Schedules | `kognitos_get_schedule`, `kognitos_manage_schedule` |
| Exceptions | `kognitos_inspect_exceptions`, `kognitos_reply_to_exception`, `kognitos_manage_exceptions` |
| Integrations | `kognitos_books` |
| Analytics | `kognitos_analytics` |
| Files | `kognitos_read_file`, `kognitos_upload_file` |

## MCP Or REST

| Need | Use |
| --- | --- |
| Ask about, run, or triage automations from the assistant | MCP |
| Reply in an exception's Workbench chat from the assistant | MCP (`kognitos_inspect_exceptions` then `kognitos_reply_to_exception`) |
| Application code, scripts, CI, or a UI on top of Kognitos | REST, through the `kognitos-api-client` skill |
| Agent Builder agents and other agents' threads | REST (`kognitos-api-client` agents reference) |

## Safety

The assistant acts on what it reads. Don't point it at automations that ingest untrusted documents or messages without review: a crafted input can try to instruct it.
