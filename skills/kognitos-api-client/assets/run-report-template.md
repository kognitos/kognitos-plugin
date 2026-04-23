# Run Report: {{automation_name}}

> **Run ID:** {{run_id}}
> **Automation:** {{automation_display_name}} (`{{automation_id}}`)
> **Stage:** {{stage}} (v{{stage_version}})
> **Invoked by:** {{invocation_user}} | **Source:** {{invocation_source}}
> **Started:** {{create_time}} | **Completed:** {{end_time}} | **Duration:** {{duration}}
> **Final state:** {{state}}

---

## Inputs

| Name | Type | Value |
|------|------|-------|
| {{input_name}} | {{input_type}} | {{input_value}} |

<!-- For file inputs, include the file resource name and original filename. -->
<!-- Omit this section if the automation has no inputs. -->

---

## Execution Log

Step-by-step record of actions taken during the run.

| # | Timestamp | Step | Detail |
|---|-----------|------|--------|
| 1 | {{event_time}} | {{step_label}} | {{step_detail}} |
| 2 | {{event_time}} | {{step_label}} | {{step_detail}} |

<!-- Populated from the run events endpoint (list_events). -->
<!-- Include the step type, any procedure/book calls, and relevant intermediate values. -->

---

## Outputs

| Name | Type | Value |
|------|------|-------|
| {{output_name}} | {{output_type}} | {{output_value}} |

<!-- Populated from get_run_outputs. -->
<!-- For file outputs, link to the file resource name. -->
<!-- For numeric outputs, show the unwrapped value (e.g. 500500, not the protobuf envelope). -->

---

## Exceptions

<!-- Omit this section entirely if the run completed with no exceptions. -->

### Exception: {{exception_id}}

- **Group:** {{exception_group}} (`missing_values` | `user_system_error` | `internal_error`)
- **State:** {{exception_state}} (`PENDING` | `RESOLVED` | `ARCHIVED`)
- **Location:** {{exception_location}}
- **Message:** {{exception_message}}
- **Assignee:** {{assignee}}

#### Resolution Thread

| # | Timestamp | Sender | Message |
|---|-----------|--------|---------|
| 1 | {{event_time}} | {{sender}} | {{message}} |

<!-- Populated from exception list_events. Shows the conversation between operators and the resolution agent. -->

---

## Guidance Applied

<!-- Record any troubleshooting guides or operator decisions that influenced the run outcome. -->

| Guide ID | Title | Applied To | Decision |
|----------|-------|------------|----------|
| {{guide_id}} | {{guide_title}} | {{exception_id}} | {{decision_summary}} |

<!-- Populated from get_guide / list_guides. -->
<!-- Also record manual operator decisions not captured in guides: -->
<!-- e.g. "Operator replied with 'use backup email' to resolve missing_values exception" -->

---

## Summary

- **Result:** {{COMPLETED / FAILED / AWAITING GUIDANCE / STOPPED — with reason}}
- **Exceptions raised:** {{count}} ({{resolved_count}} resolved, {{pending_count}} pending)
- **Guidance entries applied:** {{guide_count}}
- **Notes:** {{free-text notes from the reviewer}}

---

<!-- USAGE NOTES

This template is designed to be populated from Kognitos API responses:

1. Run metadata         → GET .../runs/{run_id}
2. Inputs               → from the invocation request or run object
3. Execution log        → GET .../runs/{run_id}/events
4. Outputs              → GET .../runs/{run_id}:getOutputs (or from run state.completed.outputs)
5. Exceptions           → GET .../exceptions?filter=run="..."
6. Resolution threads   → GET .../exceptions/{id}/events
7. Guides               → GET .../automations/{id}/guides

The markdown structure is intentionally flat and table-heavy so it converts cleanly to:
- HTML via any CommonMark renderer (pandoc, marked, remark)
- PDF via pandoc or a markdown-to-PDF pipeline
- CSV/JSON by extracting the table rows programmatically
- Confluence/Notion via paste or import

Replace all {{placeholder}} values with actual data. Remove sections that don't apply (e.g. Exceptions section when none were raised).
-->
