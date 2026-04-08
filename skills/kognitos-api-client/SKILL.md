---
name: kognitos-api-client
description: Integrate Kognitos APIs and clients through explicit adapters, stable request contracts, and predictable error handling.
license: MIT
---

# Kognitos API Client

Use this skill when you are wiring application code to Kognitos APIs, SDKs, or internal service adapters.

## Default Flow

1. Use [references/integration-shape.md](references/integration-shape.md) to define the adapter boundary before writing code.
2. Use [references/error-handling.md](references/error-handling.md) when deciding retries, surfacing errors, or mapping upstream failures.
3. Start from [assets/client-adapter-template.ts](assets/client-adapter-template.ts) for a typed integration shape.

## When To Load More

- For interface design and ownership: [references/integration-shape.md](references/integration-shape.md)
- For retries, status mapping, and operator signals: [references/error-handling.md](references/error-handling.md)
- For scaffolding: [assets/client-adapter-template.ts](assets/client-adapter-template.ts)

## Notes

- Keep Kognitos calls behind an adapter boundary.
- Normalize upstream data before the UI or SOP layers consume it.
