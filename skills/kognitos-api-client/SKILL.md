---
name: kognitos-api-client
description: Integrate Kognitos APIs and clients through explicit adapters, stable request contracts, and predictable error handling.
license: MIT
---

# Kognitos API Client

Use this skill when you are wiring application code to Kognitos APIs or SDKs.

## Default Flow

1. Use [references/public-assets.md](references/public-assets.md) to ground the work in the public OpenAPI spec and public SDK.
2. Use [assets/curl-examples.sh](assets/curl-examples.sh) to validate auth, payload shape, and endpoint behavior quickly.
3. Use [references/integration-shape.md](references/integration-shape.md) to define the adapter boundary before writing production code.
4. Use [references/error-handling.md](references/error-handling.md) when deciding retries, surfacing errors, or mapping upstream failures.
5. Start from [assets/node-sdk-example.ts](assets/node-sdk-example.ts) or [assets/client-adapter-template.ts](assets/client-adapter-template.ts) for typed integration code.

## When To Load More

- For the public SDK and OpenAPI sources: [references/public-assets.md](references/public-assets.md)
- For `curl`-first exploration and reproductions: [assets/curl-examples.sh](assets/curl-examples.sh)
- For interface design and ownership: [references/integration-shape.md](references/integration-shape.md)
- For retries, status mapping, and operator signals: [references/error-handling.md](references/error-handling.md)
- For SDK usage in application code: [assets/node-sdk-example.ts](assets/node-sdk-example.ts)
- For generic adapter scaffolding: [assets/client-adapter-template.ts](assets/client-adapter-template.ts)

## Notes

- Prefer `curl` for exploration, debugging, reproductions, and confirming request shape.
- Prefer the public `@kognitos/node` SDK for application code when it covers the required endpoint.
- Keep Kognitos calls behind an adapter boundary.
- Normalize upstream data before the UI or SOP layers consume it.
