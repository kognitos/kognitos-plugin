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

Automation code is authored by the **Kognitos AI agent** through a conversational thread, not set directly via REST. The workflow is:

1. Create an automation shell via `POST .../automations`
2. Create an agent thread linked to it via `POST .../agents/quill/threads`
3. Describe what you want in natural language via `POST .../threads/{id}:sendMessage`
4. The agent prototypes, tests, saves, and validates the code
5. Send follow-up messages to the same thread to iterate

The conversation is non-deterministic — the agent may ask clarifying questions or take multiple turns. Drive it interactively.

For full API details, see the `kognitos-api-client` skill's [automation-agent-api.md](../kognitos-api-client/references/automation-agent-api.md).

## Integration Discovery

When an SOP needs a third-party integration, use the Books API to find available connectors:

1. **Search books** by keyword (e.g. "Salesforce", "email") to find matching integrations.
2. **Search procedures** to find specific actions (e.g. "create invoice", "send notification").
3. **List workspace books** to see what's already available.

See [books-api.md](../kognitos-api-client/references/books-api.md) for the full reference.

## When To Load More

- For ownership boundaries: [references/workflow-boundaries.md](references/workflow-boundaries.md)
- For SOP structure and branch design: [references/authoring-patterns.md](references/authoring-patterns.md)
- For drafting: [assets/sop-design-template.md](assets/sop-design-template.md)
- For the automation agent API: [kognitos-api-client/references/automation-agent-api.md](../kognitos-api-client/references/automation-agent-api.md)
- For integration discovery and procedures: [kognitos-api-client/references/books-api.md](../kognitos-api-client/references/books-api.md)
- For file handling in workflows: [kognitos-api-client/references/files-api.md](../kognitos-api-client/references/files-api.md)

## Notes

- Optimize for clarity and auditability over cleverness.
- Keep the workflow contract explicit: inputs, decisions, outputs, and error paths.
- When an SOP requires file inputs, document the expected file format and use the Files API for upload.
