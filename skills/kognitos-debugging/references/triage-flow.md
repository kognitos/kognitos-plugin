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

## Reading API Failures

| Signal | Usual cause |
| --- | --- |
| `401` | Missing, expired, or deleted API key |
| `403` | The key's organization, workspace scope, or permission level does not cover the call (a read-only key on a write call, or an organization other than the key's own) |
| `404` on a stage query | The automation has no version at that stage (for example never published) |
| `504` after about 15 seconds | The request hit the REST timeout. Narrow it (smaller page, time range filter) instead of retrying it unchanged |
| `FAILED_PRECONDITION` on invoke | Invoking `AUTOMATION_STAGE_PUBLISHED` on an automation that was never published |

See the `kognitos-bootstrap` skill's [environment-model.md](../../kognitos-bootstrap/references/environment-model.md) for key scope and platform limits.

## Run Or Automation?

- A run waiting in `awaiting_guidance` is recoverable. On a published run it has an exception, resolved in its Workbench work item; on a draft run it has none, and the automation builder agent fixes the draft.
- A problem that repeats on every run usually lives in the automation (its steps, inputs, or connections), not in the run: fix the draft and publish again.
- Check the connections the automation uses before debugging its steps (`GET .../connections`, see [books-api.md](../../kognitos-api-client/references/books-api.md)). A connection whose `status.state` is `BOOK_CONNECTION_STATE_FAILED` or `BOOK_CONNECTION_STATE_CONDITIONS_NOT_MET` fails the runs that use it, and its `status.conditions` name the check that failed (credentials, configuration, deployment). `BOOK_CONNECTION_STATE_INACTIVE` is only idle and reactivates on demand.
