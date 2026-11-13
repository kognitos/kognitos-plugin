---
name: kognitos-debugging
description: Debug Kognitos applications and workflows by isolating failure boundaries, capturing evidence, and narrowing the issue quickly.
license: MIT
---

# Kognitos Debugging

Use this skill when a Kognitos-backed application or workflow is failing and you need a reliable triage path.

## Default Flow

1. Use [references/triage-flow.md](references/triage-flow.md) to identify whether the issue is UI, integration, workflow, or environment related.
2. Use [references/evidence-capture.md](references/evidence-capture.md) to collect logs, payloads, and repro notes before changing code.
3. Run [scripts/collect_debug_bundle.py](scripts/collect_debug_bundle.py) when you need a quick local evidence summary.

## API-Driven Debugging

When debugging run failures or exceptions, use the API endpoints from the `kognitos-api-client` skill. If the Kognitos MCP server is connected, its `kognitos_runs`, `kognitos_inspect_exceptions`, and `kognitos_reply_to_exception` tools cover the same steps from the assistant (see [mcp-server.md](../kognitos-bootstrap/references/mcp-server.md)).

1. **List recent runs** to find the failing run — see [runs-api.md](../kognitos-api-client/references/runs-api.md).
2. **List run events** for the step-by-step execution log — the primary debugging view.
3. **Check the run's stage.** A draft run (`AUTOMATION_STAGE_DRAFT`) that needs guidance raises no exception: it waits in `awaiting_guidance` with a `description` and `location`, and the fix goes through the automation builder agent's thread (see [automation-agent-api.md](../kognitos-api-client/references/automation-agent-api.md)). Continue below only for published runs.
4. **Inspect exceptions** to see error details, group, and resolution status — see [exceptions-api.md](../kognitos-api-client/references/exceptions-api.md).
5. **Read the resolution thread** (the exception's Workbench work item chat) to see what the agent tried.
6. **Reply in the work item's chat** to guide resolution, submit a retry or stop decision, or **assign** to an operator. One work item can group several exceptions that failed the same way, so a fix agreed there can apply to all of them.
7. **Check guide entries** for known resolutions before escalating.
8. **Generate a run report** from [run-report-template.md](../kognitos-api-client/assets/run-report-template.md) to capture the full audit trail.

## When To Load More

- For narrowing the fault domain and reading HTTP failures: [references/triage-flow.md](references/triage-flow.md)
- For reproducible evidence collection: [references/evidence-capture.md](references/evidence-capture.md)
- For a quick local debug bundle: [scripts/collect_debug_bundle.py](scripts/collect_debug_bundle.py)
- For run event logs and run control: [kognitos-api-client/references/runs-api.md](../kognitos-api-client/references/runs-api.md)
- For exception inspection and resolution: [kognitos-api-client/references/exceptions-api.md](../kognitos-api-client/references/exceptions-api.md)
- For structured run audit trails: [kognitos-api-client/assets/run-report-template.md](../kognitos-api-client/assets/run-report-template.md)

## Notes

- Capture evidence before “fixing” anything that is not yet explained.
- Prefer narrowing one boundary at a time over shotgun instrumentation.
- `awaiting_guidance` is recoverable, not failed: guidance (a retry, a corrected value, or a fix) lets the run continue.
- Use the run report template to document findings — it converts cleanly to HTML, PDF, or Confluence.
