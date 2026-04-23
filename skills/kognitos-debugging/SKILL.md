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

When debugging run failures or exceptions, use the API endpoints from the `kognitos-api-client` skill:

1. **List recent runs** to find the failing run — see [runs-api.md](../kognitos-api-client/references/runs-api.md).
2. **List run events** for the step-by-step execution log — the primary debugging view.
3. **Inspect exceptions** to see error details, group, and resolution status — see [exceptions-api.md](../kognitos-api-client/references/exceptions-api.md).
4. **Read the resolution thread** (`list_events` on the exception) to see what the agent tried.
5. **Reply to the exception agent** to guide resolution, or **assign** to an operator.
6. **Check troubleshooting guides** for known resolutions before escalating.
7. **Generate a run report** from [run-report-template.md](../kognitos-api-client/assets/run-report-template.md) to capture the full audit trail.

## When To Load More

- For narrowing the fault domain: [references/triage-flow.md](references/triage-flow.md)
- For reproducible evidence collection: [references/evidence-capture.md](references/evidence-capture.md)
- For a quick local debug bundle: [scripts/collect_debug_bundle.py](scripts/collect_debug_bundle.py)
- For run event logs and run control: [kognitos-api-client/references/runs-api.md](../kognitos-api-client/references/runs-api.md)
- For exception inspection and resolution: [kognitos-api-client/references/exceptions-api.md](../kognitos-api-client/references/exceptions-api.md)
- For structured run audit trails: [kognitos-api-client/assets/run-report-template.md](../kognitos-api-client/assets/run-report-template.md)

## Notes

- Capture evidence before “fixing” anything that is not yet explained.
- Prefer narrowing one boundary at a time over shotgun instrumentation.
- Use the run report template to document findings — it converts cleanly to HTML, PDF, or Confluence.
