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
4. Use [references/integration-shape.md](references/integration-shape.md) to define the adapter boundary before writing production code.
5. Use [references/error-handling.md](references/error-handling.md) when deciding retries, surfacing errors, or mapping upstream failures.
6. Start from [assets/node-sdk-example.ts](assets/node-sdk-example.ts) or [assets/client-adapter-template.ts](assets/client-adapter-template.ts) for typed integration code.

## When To Load More

- For the public SDK and OpenAPI sources: [references/public-assets.md](references/public-assets.md)
- For `curl`-first exploration and reproductions: [references/curl-examples.md](references/curl-examples.md)
- For creating automations via the AI agent: [references/automation-agent-api.md](references/automation-agent-api.md)
- For interface design and ownership: [references/integration-shape.md](references/integration-shape.md)
- For retries, status mapping, and operator signals: [references/error-handling.md](references/error-handling.md)
- For SDK usage in application code: [assets/node-sdk-example.ts](assets/node-sdk-example.ts)
- For generic adapter scaffolding: [assets/client-adapter-template.ts](assets/client-adapter-template.ts)
- For run audit trail reports: [assets/run-report-template.md](assets/run-report-template.md)

## Key Concepts

- **Automations are built by the AI agent (Quill), not set via REST.** To create one: create an automation shell with `kind: AUTOMATION_KIND_QUILL2`, open a Quill thread on it, and converse with the agent. The agent id in URL paths is `quill2`. See [references/automation-agent-api.md](references/automation-agent-api.md).
- **Quill builds, tests, and maintains the automation itself.** Within the conversation it discovers apps, writes and validates code, **tests the automation** (running it against your sample inputs and diagnosing failures itself), and **autosaves** at the end of a turn.
- **Have Quill run/verify, not just build.** Give it realistic inputs so it runs the automation against the actual connected apps — this catches logical inconsistencies (wrong branch, mis-mapped field) and real integration mismatches that build-time validation can't. It's about confirming the automation does the right thing, not hardening against malformed input (trust Quill's judgment there). **Mind mutating automations** (`isMutation` procedures like sending email or creating records): each test is a real run with side effects, so keep those deliberate.
- **It's a conversational, multi-turn API.** Send a message (`POST .../input`), observe **events** (`GET .../events` poll, or `GET .../stream` SSE) until the turn ends, then respond. The agent is non-deterministic and may ask clarifying questions (**interrupts**) or request connections. Drive the conversation interactively rather than scripting it end-to-end.
- **Drafts vs published, and authoring vs running.** Automations are versioned `major.minor`: Quill's autosaves create **draft** minor versions (`major == 0` = never published) — **Quill never publishes**. Publishing (`:publish`) is an explicit step that bumps the major. Running uses `:invoke`, where `stage` selects the version: `AUTOMATION_STAGE_DRAFT` (test/preview) or `AUTOMATION_STAGE_PUBLISHED` (production, after publishing).
- **Draft = Quill, published = Astral (exception handling).** Draft runs (Quill's `TEST` runs *and* user `MANUAL` draft invokes) disable exception handling — failures surface inline with a traceback and **no Astral**, so you can invoke a draft yourself and ask Quill to monitor and debug that run. Published runs are managed by Astral's guidance-center flow ([exceptions-api.md](references/exceptions-api.md)).
- **What the user sees is the AOP** — a business-language Standard Operating Procedure (`english_code` on the automation, read-only). The SPy code is internal.
- **Base URL pattern**: `https://app.<region>-1[.<env>].kognitos.com` (e.g. `https://app.us-1.kognitos.com`, or `https://app.us-1.dev.kognitos.com` for dev). EU customers swap `us-1` for `eu-1`.
- **Auth**: Bearer token with a PAT (`kgn_pat_` prefix). The token identifies the user, not an org or workspace.

## Notes

- Prefer `curl` for exploration, debugging, reproductions, and confirming request shape.
- Prefer the public `@kognitos/node` SDK for application code when it covers the required endpoint.
- Keep Kognitos calls behind an adapter boundary.
- Normalize upstream data before the UI or SOP layers consume it.
