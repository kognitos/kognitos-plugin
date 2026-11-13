# Error Handling

Use this reference when deciding how integration failures should behave.

## Expected Cases

- Validation errors: fail fast with actionable feedback.
- Authentication errors: distinguish misconfiguration from expired credentials.
- Transient upstream failures: retry only when the operation is safe to replay.
- Unexpected payloads: capture evidence and stop guessing.

## Guidance

- Keep user-facing errors simpler than internal diagnostic errors.
- Preserve correlation IDs or request IDs when available.
- Avoid retries on business-logic rejections.
- Prefer SDK-provided retry and timeout behavior in application code instead of rebuilding it around raw HTTP calls.
- Use `curl` reproductions to capture the exact request and response when debugging auth, payload, or endpoint issues.

## Reading Kognitos errors

- Errors from a Kognitos service are JSON with `code` and `message`; the message usually names the problem (for example `400` `Invalid semantic version format: ''`).
- A `403` with a plain-text `Forbidden` body comes from the gateway: the API key can't call that endpoint (role, the key's permission level, or a key from another organization). Retrying won't help.
- A `403` whose `x-cache` header reads `Error from cloudfront` came from the CDN in front of Kognitos, not from Kognitos. Retry it once.
- A `504` after about 15 seconds is the gateway timeout; the operation may still complete. Re-read the resource before retrying a write.
