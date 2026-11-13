---
name: kognitos-api-client
description: Integrate Kognitos APIs and clients through explicit adapters, stable request contracts, and predictable error handling.
license: MIT
---

# Kognitos API Client

Use this skill when you are wiring application code to Kognitos APIs or SDKs, or when you need to create and run automations programmatically.

## Default Flow

1. Use [references/public-assets.md](references/public-assets.md) to ground the work in the public OpenAPI spec and public SDK.
2. Use [references/curl-examples.md](references/curl-examples.md) to validate auth, payload shape, and endpoint behavior quickly.
3. Use [references/automation-agent-api.md](references/automation-agent-api.md) when creating or refining automations through the AI agent.
4. Use [references/agents-api.md](references/agents-api.md) when talking to any other Kognitos agent, or building your own agents with the Agent Builder.
5. Use [references/integration-shape.md](references/integration-shape.md) to define the adapter boundary before writing production code.
6. Use [references/error-handling.md](references/error-handling.md) when deciding retries, surfacing errors, or mapping upstream failures.
7. Start from [assets/node-sdk-example.ts](assets/node-sdk-example.ts) or [assets/client-adapter-template.ts](assets/client-adapter-template.ts) for typed integration code.

## When To Load More

- For the public SDK and OpenAPI sources: [references/public-assets.md](references/public-assets.md)
- For `curl`-first exploration and reproductions: [references/curl-examples.md](references/curl-examples.md)
- For creating automations via the AI agent: [references/automation-agent-api.md](references/automation-agent-api.md)
- For other agents, the Agent Builder, and the thread protocol all agents share: [references/agents-api.md](references/agents-api.md)
- For interface design and ownership: [references/integration-shape.md](references/integration-shape.md)
- For retries, status mapping, and operator signals: [references/error-handling.md](references/error-handling.md)
- For assets, folders, and collections (workspace files and tables automations use): [references/content-api.md](references/content-api.md)
- For the Workbench queue (work items, work units, guides): [references/workbench-api.md](references/workbench-api.md)
- For starting automations or agents from email, webhooks, and polls, and for waking or discovering on a connection: [references/triggers-api.md](references/triggers-api.md)
- For exporting, importing, copying, versioning, and configuring automations: [references/automation-lifecycle-api.md](references/automation-lifecycle-api.md)
- For credentials (secrets) and OAuth apps: [references/secrets-api.md](references/secrets-api.md)
- For the organization audit log: [references/audit-api.md](references/audit-api.md)
- For SDK usage in application code: [assets/node-sdk-example.ts](assets/node-sdk-example.ts)
- For generic adapter scaffolding: [assets/client-adapter-template.ts](assets/client-adapter-template.ts)
- For run audit trail reports: [assets/run-report-template.md](assets/run-report-template.md)

## Key Concepts

- **Automations are built by the AI agent (Quill), not set via REST.** To create one: create an automation shell with `kind: AUTOMATION_KIND_QUILL2`, open a Quill thread on it, and converse with the agent. The agent id in URL paths is `quill2`. See [references/automation-agent-api.md](references/automation-agent-api.md).
- **Quill builds, tests, and maintains the automation itself.** Within the conversation it discovers apps, writes and validates code, **tests the automation** (running it against your sample inputs and diagnosing failures itself), and **autosaves** at the end of a turn.
- **Have Quill run/verify, not just build.** Give it realistic inputs so it runs the automation against the actual connected apps — this catches logical inconsistencies (wrong branch, mis-mapped field) and real integration mismatches that build-time validation can't. It's about confirming the automation does the right thing, not hardening against malformed input (trust Quill's judgment there). **Mind mutating automations** (`isMutation` procedures like sending email or creating records): each test is a real run with side effects, so keep those deliberate.
- **It's a conversational, multi-turn API.** Send a message (`POST .../input`), observe **events** (`GET .../events` poll, or `GET .../stream` SSE) until the turn ends, then respond. The agent is non-deterministic and may ask clarifying questions (**interrupts**) or request connections. Drive the conversation interactively rather than scripting it end-to-end.
- **Drafts vs published, and authoring vs running.** Automations are versioned `major.minor`: Quill's autosaves create **draft** minor versions (`major == 0` = never published) — **Quill never publishes**. Publishing (`:publish`) is an explicit step that bumps the major. Running uses `:invoke`, where `stage` selects the version: `AUTOMATION_STAGE_DRAFT` (test/preview) or `AUTOMATION_STAGE_PUBLISHED` (production, after publishing).
- **Draft = Quill, published = Astral (exception handling).** Draft runs (Quill's `TEST` runs *and* user `MANUAL` draft invokes) disable exception handling — failures surface inline with a traceback and **no Astral**, so you can invoke a draft yourself and ask Quill to monitor and debug that run. On a published run, Astral raises an exception and files it to the Workbench as a work item, where it is resolved in the work item's chat or by a retry or stop decision ([exceptions-api.md](references/exceptions-api.md), [workbench-api.md](references/workbench-api.md)).
- **Quill is one of several agents, and they all share one thread protocol.** Built-in agents hang off an automation, a run, a connection, or the workspace; workspace agents are built in the Agent Builder (create, configure by talking to the Agent Builder Assistant, version, tag, export/import). Every agent uses the same create-thread, `POST .../input`, poll `status.state`, read events loop. Deploying a workspace agent is a UI step. See [references/agents-api.md](references/agents-api.md).
- **What the user sees is the AOP** — a business-language Standard Operating Procedure (`english_code` on the automation, read-only). The SPy code is internal.
- **Base URL**: `KOGNITOS_BASE_URL` is the host you sign in to, without `/api/v1`: `https://app.us-1.kognitos.com` for most organizations. Organizations hosted in another region use that region's host.
- **Auth**: Bearer token with a PAT (`kgn_pat_` prefix). The token identifies the user, not an org or workspace.

## Notes

- Prefer `curl` for exploration, debugging, reproductions, and confirming request shape.
- Prefer the public `@kognitos/node` SDK for application code when it covers the required endpoint.
- Keep Kognitos calls behind an adapter boundary.
- Normalize upstream data before the UI or SOP layers consume it.
