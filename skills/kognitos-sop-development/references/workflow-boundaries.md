# Workflow Boundaries

Use this reference to decide which logic belongs in a SOP and which logic belongs elsewhere.

## SOP-Owned Concerns

- Procedural business rules
- Approval or escalation paths
- Domain-specific decision trees
- Repeatable operator guidance

## App-Owned Concerns

- Screen composition and routing
- Client-side interaction state
- Local form ergonomics
- Presentation-only formatting

## Smells

- A UI component is deciding eligibility or workflow routing.
- A SOP is encoding display logic or component structure.
- The same decision logic exists in both the app and the SOP.

## Automation Or Agent

- Use an **automation** (an SOP) when the steps are known, repeatable, and need an audit trail: it runs the same way every time, versions through draft and publish, and raises exceptions for people to resolve.
- Use a **workspace agent** (built in the Agent Builder) when the work is a conversation or the steps can't be fixed in advance, such as answering questions or triaging requests. See the `kognitos-api-client` skill's [agents-api.md](../../kognitos-api-client/references/agents-api.md).
- Don't hide a business rule in an agent's instructions when an automation must enforce it on every run.
