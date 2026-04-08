# Environment Promotion

Use this reference when deciding how a change should move between environments.

## Promotion Guidance

- Promote the smallest coherent unit of change.
- Keep environment-specific configuration explicit.
- Validate the same critical path in each environment.
- Confirm that test data and production data assumptions do not diverge silently.

## Rollback Thinking

- Know whether the change can be reverted in code only.
- Identify coupled workflow or config changes that also need rollback.
- Prefer feature-gated rollout when the blast radius is uncertain.
