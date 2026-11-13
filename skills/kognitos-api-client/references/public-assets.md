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

`KOGNITOS_BASE_URL` is the host you sign in to, for example `https://app.us-1.kognitos.com`.

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

### Agents API

Kognitos agents (the built-in agents such as Quill, and the workspace agents you build in the Agent Builder) all share one conversational thread protocol. The agent endpoints are **not yet** in the public OpenAPI spec; they are being added. Until then they are documented in [agents-api.md](agents-api.md) (all agents, the Agent Builder, and the shared thread protocol) and [automation-agent-api.md](automation-agent-api.md) (Quill, which builds automations).

Key points for Quill:

- Automation `english_code` (the AOP) and `code` are **read-only** via REST — they are authored by the agent.
- In URL paths, the agent ID is the literal string **`quill2`**. Quill threads exist only under an automation: `.../automations/{auto_id}/agents/quill2/threads/{thread_id}`.
- Automations Quill operates on must be created with `kind: AUTOMATION_KIND_QUILL2`.
- You send messages with `POST .../input` (async; `{"message": {"content": "..."}}`), poll the thread's `status.state` to know when the turn is done, and read **events** via `GET .../events` (poll) or `GET .../stream` (SSE). Events are flat JSON objects (`output_text`, `reasoning_text`, `tool_call_start`, `tool_result`, `interrupt`, `generation_complete`, ...).
- The conversation is non-deterministic and multi-turn — the agent may ask questions (interrupts), request connections, test the automation itself, and iterate on the code. It **autosaves a new draft version** at the end of a turn; it never publishes.
- Automations are versioned `major.minor`: drafts bump the minor (`major == 0` = never published); **publishing** (`:publish`) bumps the major. Running uses the automations `:invoke` endpoint, where `stage` selects the version: `AUTOMATION_STAGE_DRAFT` (test/preview) vs `AUTOMATION_STAGE_PUBLISHED` (production, requires publishing first).
- Exception handling differs by stage: **draft** runs disable it (no Astral — Quill self-diagnoses, even for user-invoked draft runs); **published** runs are managed by Astral (the guidance-center flow). See [automation-agent-api.md](automation-agent-api.md) and [exceptions-api.md](exceptions-api.md).
