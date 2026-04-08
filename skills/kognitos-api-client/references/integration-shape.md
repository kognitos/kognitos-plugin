# Integration Shape

Use this reference before adding or expanding a Kognitos client.

## Preferred Boundary

- One adapter per upstream capability or bounded surface.
- Typed request and response models at the edge.
- Small translation layer between remote payloads and internal domain models.
- Prefer the public `@kognitos/node` SDK as the transport layer when it covers the endpoint, and wrap it in a local adapter rather than passing the SDK directly through the app.

## Rules

- Do not let raw transport details leak across the app.
- Keep authentication, retries, and logging centralized.
- Separate command-like operations from query-like operations where practical.
- Keep `curl` usage in docs, debugging, tests, and reproductions; do not let ad hoc shell snippets become the production integration path.

## Review Questions

- Would a schema change be isolated to the adapter?
- Are consumers insulated from transport details?
- Is the failure mode explicit to the caller?
