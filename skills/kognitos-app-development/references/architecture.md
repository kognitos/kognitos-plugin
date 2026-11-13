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
- Call Kognitos from the server side. The API key stays in server config and never reaches the browser.
- Start long work and poll for it: invoke the automation, then poll the run. A REST request that takes longer than 15 seconds fails with `504`, so never hold a request open waiting for a run to finish.

## App Review Questions

- Can a reader tell where a user action becomes a workflow invocation?
- Are side effects isolated behind clear interfaces?
- Would a SOP change require a UI rewrite? If yes, the boundary is likely wrong.
