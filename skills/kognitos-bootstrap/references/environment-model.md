# Environment Model

Use this reference when bootstrap work depends on clear environment boundaries.

## Recommended Separation

- Local development: safe defaults, mock data where possible, minimal secrets.
- Shared development: real integrations with reversible test data.
- Staging: production-like dependencies and promotion checks.
- Production: no exploratory changes, no undocumented secrets handling.

## What To Clarify Early

- Which environment variables are required for the app to start.
- Which variables are optional and feature-gated.
- Which credentials allow write operations.
- Which external systems are safe to call from development.

## Kognitos Guidance

- Keep workflow logic ownership separate from UI code ownership.
- Prefer explicit environment names and config files over implicit defaults.
- Treat auth and execution credentials as separate concerns where possible.
