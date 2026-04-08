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
