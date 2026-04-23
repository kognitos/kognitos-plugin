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

- **Automation code is authored by the AI agent**, not set directly via REST. To create an automation: create a shell, open an agent thread, and converse with the agent. See [references/automation-agent-api.md](references/automation-agent-api.md).
- The agent conversation is non-deterministic — it may ask clarifying questions (interrupts), take multiple turns, or produce different code for the same prompt. Drive the conversation interactively rather than scripting it end-to-end.
- **Base URL pattern**: `https://app.<region>-1[.<env>].kognitos.com` (e.g. `https://app.us-1.dev.kognitos.com` for dev).
- **Auth**: Bearer token with a PAT (`kgn_pat_` prefix). The token identifies the user, not an org or workspace.

## Key Concepts

- **Automation code is authored by the AI agent**, not set directly via REST. To create an automation: create a shell, open an agent thread, and converse with the agent. See [references/automation-agent-api.md](references/automation-agent-api.md).
- The agent conversation is non-deterministic — it may ask clarifying questions (interrupts), take multiple turns, or produce different code for the same prompt. Drive the conversation interactively rather than scripting it end-to-end.
- **Base URL**: `KOGNITOS_BASE_URL` is `https://app.us-1.kognitos.com` for US customers. EU customers swap `us-1` for `eu-1`.
- **Auth**: Bearer token with a PAT (`kgn_pat_` prefix). The token identifies the user, not an org or workspace.

## Notes

- Prefer `curl` for exploration, debugging, reproductions, and confirming request shape.
- Prefer the public `@kognitos/node` SDK for application code when it covers the required endpoint.
- Keep Kognitos calls behind an adapter boundary.
- Normalize upstream data before the UI or SOP layers consume it.
