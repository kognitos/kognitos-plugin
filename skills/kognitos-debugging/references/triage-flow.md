# Triage Flow

Use this reference to reduce a broad failure report into a smaller, testable problem.

## Order Of Operations

1. Reproduce the issue.
2. Identify the failing boundary:
   - UI state
   - API client or transport
   - SOP or workflow logic
   - environment/configuration
3. Check the most recent change touching that boundary.
4. Capture concrete evidence before changing implementation.

## Useful Questions

- Is the workflow wrong, or is the app showing the workflow incorrectly?
- Did the failure happen before or after a remote call?
- Is the problem data-specific, environment-specific, or deterministic?
