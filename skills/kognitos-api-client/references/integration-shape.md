# Integration Shape

Use this reference before adding or expanding a Kognitos client.

## Preferred Boundary

- One adapter per upstream capability or bounded surface.
- Typed request and response models at the edge.
- Small translation layer between remote payloads and internal domain models.

## Rules

- Do not let raw transport details leak across the app.
- Keep authentication, retries, and logging centralized.
- Separate command-like operations from query-like operations where practical.

## Review Questions

- Would a schema change be isolated to the adapter?
- Are consumers insulated from transport details?
- Is the failure mode explicit to the caller?
