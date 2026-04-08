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
