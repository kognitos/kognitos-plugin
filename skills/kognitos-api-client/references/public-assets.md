# Public API Assets

Use this reference before choosing whether to reach for `curl`, the public SDK, or a custom adapter.

## Public Sources

- Public OpenAPI spec:
  `https://github.com/kognitos/openapi/blob/main/latest/openapi.yaml`
- Public TypeScript SDK repository:
  `https://github.com/kognitos/kognitos-node`
- Public npm package:
  `https://www.npmjs.com/package/@kognitos/node`

## Base URL

`KOGNITOS_BASE_URL` is `https://app.us-1.kognitos.com` for US customers. EU customers swap `us-1` for `eu-1`.

## API Surfaces

### REST API (OpenAPI)

Covers organizations, workspaces, automations (metadata), runs, files, exceptions, and analytics. Auth is `Authorization: Bearer <kgn_pat_...>`.

Use `curl` first when you need to:
  - verify authentication
  - inspect raw payloads
  - reproduce a bug
  - discover org/workspace IDs

Use `@kognitos/node` first when you need to:
  - integrate Kognitos into application code
  - benefit from typed responses
  - rely on built-in retries, timeouts, pagination, or streaming support

### Automation Agent API

The Kognitos AI agent creates and refines automation code through a conversational thread. This API is **not** in the public OpenAPI spec — it is documented in [automation-agent-api.md](automation-agent-api.md).

Key points:
- Automation `english_code` and `code` are **read-only** via REST — they are authored by the AI agent.
- In URL paths, the agent ID is the literal string `quill`. The canonical thread path includes the automation: `.../automations/{auto_id}/agents/quill/threads/{thread_id}`.
- `sendMessage` returns a stream of concatenated pretty-printed JSON objects (not line-delimited NDJSON). The request uses a double-nested `user_message` structure.
- The conversation is non-deterministic — the agent may ask questions, request connections, or iterate on the code.
