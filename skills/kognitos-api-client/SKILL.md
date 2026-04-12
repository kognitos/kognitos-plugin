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
4. Use [references/runs-api.md](references/runs-api.md) when invoking automations, polling runs, or inspecting step-by-step event logs.
5. Use [references/exceptions-api.md](references/exceptions-api.md) when triaging, assigning, or resolving exceptions.
6. Use [references/scheduling-api.md](references/scheduling-api.md) when setting up or managing automation schedules.
7. Use [references/files-api.md](references/files-api.md) when uploading or reading files used as automation inputs or outputs.
8. Use [references/books-api.md](references/books-api.md) when discovering integrations, searching for procedures, or managing connections.
9. Use [references/analytics-api.md](references/analytics-api.md) when building dashboards or checking platform health metrics.
10. Use [references/integration-shape.md](references/integration-shape.md) to define the adapter boundary before writing production code.
11. Use [references/error-handling.md](references/error-handling.md) when deciding retries, surfacing errors, or mapping upstream failures.
12. Start from [assets/node-sdk-example.ts](assets/node-sdk-example.ts) or [assets/client-adapter-template.ts](assets/client-adapter-template.ts) for typed integration code.
13. Use [assets/run-report-template.md](assets/run-report-template.md) to generate structured audit trail reports from run data.

## When To Load More

- For the public SDK and OpenAPI sources: [references/public-assets.md](references/public-assets.md)
- For `curl`-first exploration and reproductions: [references/curl-examples.md](references/curl-examples.md)
- For creating automations via the AI agent: [references/automation-agent-api.md](references/automation-agent-api.md)
- For run lifecycle, events, outputs, and pause/continue: [references/runs-api.md](references/runs-api.md)
- For exception inspection, triage, assignment, and resolution: [references/exceptions-api.md](references/exceptions-api.md)
- For schedule creation, patterns, and enable/disable: [references/scheduling-api.md](references/scheduling-api.md)
- For file upload, read, and use as automation inputs: [references/files-api.md](references/files-api.md)
- For integration discovery, procedure search, and connections: [references/books-api.md](references/books-api.md)
- For run stats, org insights, and exception resolution metrics: [references/analytics-api.md](references/analytics-api.md)
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

## Notes

- Prefer `curl` for exploration, debugging, reproductions, and confirming request shape.
- Prefer the public `@kognitos/node` SDK for application code when it covers the required endpoint.
- Keep Kognitos calls behind an adapter boundary.
- Normalize upstream data before the UI or SOP layers consume it.
