# SOP Authoring Patterns

Use this reference when a SOP needs to be maintainable under iteration.

## Preferred Structure

- State the trigger and expected inputs.
- Normalize or validate inputs early.
- Make decision points explicit and named.
- Record what happens on success, retry, and terminal failure.
- Keep outputs stable for downstream systems.

## Good Practices

- Name branches in domain language.
- Keep side effects near the decision that requires them.
- Capture operator-facing explanations where ambiguity is likely.
- Prefer a few clear branches over deeply nested, implicit logic.
