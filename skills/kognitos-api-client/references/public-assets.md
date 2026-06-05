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

### Automation Agent API (Quill)

The Kognitos AI agent (Quill) builds, tests, refines, and maintains automations through a conversational thread. This API is **not** in the public OpenAPI spec — it is documented in [automation-agent-api.md](automation-agent-api.md).

Key points:
- Automation `english_code` (the AOP) and `code` are **read-only** via REST — they are authored by the agent.
- In URL paths, the agent ID is the literal string **`quill2`**. The thread path is automation-scoped: `.../automations/{auto_id}/agents/quill2/threads/{thread_id}`. The workspace-scoped agent path is not authorized for PAT clients.
- Automations Quill operates on must be created with `kind: AUTOMATION_KIND_QUILL2`.
- You send messages with `POST .../input` (async; `{"message": {"content": "..."}}`) and observe **events** via `GET .../events` (poll) or `GET .../stream` (SSE). Events are flat JSON objects (`output_text`, `reasoning_text`, `tool_call_start`, `tool_result`, `interrupt`, `generation_complete`, ...).
- The conversation is non-deterministic and multi-turn — the agent may ask questions (interrupts), request connections, test the automation itself, and iterate on the code. It **autosaves a new draft version** at the end of a turn; it never publishes.
- Automations are versioned `major.minor`: drafts bump the minor (`major == 0` = never published); **publishing** (`:publish`) bumps the major. Running uses the automations `:invoke` endpoint, where `stage` selects the version: `AUTOMATION_STAGE_DRAFT` (test/preview) vs `AUTOMATION_STAGE_PUBLISHED` (production, requires publishing first).
- Exception handling differs by stage: **draft** runs disable it (no Astral — Quill self-diagnoses, even for user-invoked draft runs); **published** runs are managed by Astral (the guidance-center flow). See [automation-agent-api.md](automation-agent-api.md) and [exceptions-api.md](exceptions-api.md).
