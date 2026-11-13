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

## Platform Constraints

- An automation with required inputs cannot run on a schedule. If it must run on a schedule, make its inputs optional or have it read the data from a connected system.
- Webhook and email triggers pass the event or the email (with attachments) to the run. Design the inputs around what the trigger delivers.
- Files have limits: an upload can be at most 800 MB, and IDP reads at most 100 pages of a document (the rest is skipped without an exception). Split long documents before extracting from them.
- Exceptions on published runs are resolved by people in the Workbench, and the resolution can be saved as a guide entry that later runs follow. Write exception messages and decision names an operator can act on without reading the automation's steps.
- Draft runs raise no exceptions. Test failure paths on the draft with realistic inputs, but expect their exceptions only once the automation is published.
