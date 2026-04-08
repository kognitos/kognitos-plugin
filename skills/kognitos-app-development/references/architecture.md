# Architecture Guidance

Use this reference when deciding what belongs in the app, what belongs in workflow logic, and what belongs in integration code.

## Preferred Split

- Presentation layer: routes, screens, state coordination, user feedback.
- Workflow layer: business rules, SOP sequencing, procedural decisions.
- Data and integration layer: API clients, persistence, domain adapters.

## Rules

- Do not bury business logic inside UI components.
- Keep workflow decisions explicit and traceable.
- Prefer typed boundaries between UI state and workflow execution.
- Centralize cross-cutting config rather than scattering environment checks.

## App Review Questions

- Can a reader tell where a user action becomes a workflow invocation?
- Are side effects isolated behind clear interfaces?
- Would a SOP change require a UI rewrite? If yes, the boundary is likely wrong.
