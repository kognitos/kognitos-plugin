---
name: kognitos-sop-development
description: Design and refine Kognitos SOPs with clear boundaries, traceable decision points, and maintainable workflow patterns.
license: MIT
---

# Kognitos SOP Development

Use this skill when you are authoring, reviewing, or restructuring Kognitos SOPs and workflow behavior.

## Default Flow

1. Use [references/workflow-boundaries.md](references/workflow-boundaries.md) to decide what belongs in the SOP versus the app.
2. Use [references/authoring-patterns.md](references/authoring-patterns.md) to structure decision points and failure handling.
3. Start from [assets/sop-design-template.md](assets/sop-design-template.md) when drafting a new SOP or refactoring a brittle one.

## Creating Automations

This skill is about *designing* SOPs — boundaries, decisions, failure handling, auditability. For the API mechanics of authoring and running an automation, use the `kognitos-api-client` skill and its [automation-agent-api.md](../kognitos-api-client/references/automation-agent-api.md) reference. Do not duplicate that flow here.

## When To Load More

- For ownership boundaries: [references/workflow-boundaries.md](references/workflow-boundaries.md)
- For SOP structure and branch design: [references/authoring-patterns.md](references/authoring-patterns.md)
- For drafting: [assets/sop-design-template.md](assets/sop-design-template.md)
- For the automation agent API (authoring and running): use the `kognitos-api-client` skill

## Notes

- Optimize for clarity and auditability over cleverness.
- Keep the workflow contract explicit: inputs, decisions, outputs, and error paths.
