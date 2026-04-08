# Public API Assets

Use this reference before choosing whether to reach for `curl`, the public SDK, or a custom adapter.

## Public Sources

- Public OpenAPI spec:
  `https://github.com/kognitos/kognitos-node/blob/main/.openapi/openapi.yaml`
- Public TypeScript SDK repository:
  `https://github.com/kognitos/kognitos-node`
- Public npm package:
  `https://www.npmjs.com/package/@kognitos/node`

## Recommended Split

- Use `curl` first when you need to:
  - verify authentication
  - inspect raw payloads
  - reproduce a bug
  - confirm endpoint behavior before writing code
- Use `@kognitos/node` first when you need to:
  - integrate Kognitos into application code
  - benefit from typed responses
  - rely on built-in retries, timeouts, pagination, or streaming support

## What The Public Spec Suggests

The public OpenAPI surface is PAT/bearer-token based and covers broad application concerns including organizations, workspaces, automations, runs, files, exceptions, and analytics.

That makes the API skill worth structuring around two modes:

- exploration mode with `curl`
- production mode with the public SDK behind a local adapter
