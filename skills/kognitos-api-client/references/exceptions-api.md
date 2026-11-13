# Exceptions API

Use this reference when you need to inspect, triage, or resolve exceptions raised during automation runs.

## Overview

This API covers exception handling for **published** automations, which is managed by **Astral** (the exception-resolution agent). It does **not** apply to draft runs: draft-stage runs — both Quill's own test runs and draft `:invoke` runs you trigger — disable exception handling, so a failure parks the run in `awaiting_guidance` with an empty `exception` and a plain `description`/`location` and **no Astral exception is created**. For those, drive the fix through Quill on its thread (it reads the run's traceback and patches the code). Use this API for the runtime exceptions raised by **published** automations. See [automation-agent-api.md](automation-agent-api.md) for the draft-vs-published distinction.

An exception is an error that requires human attention. When a published run enters `awaiting_guidance`, Astral raises an exception and the run's `state.awaiting_guidance.exception` holds its resource name. Responses report the exception `state` as `EXCEPTION_STATE_PENDING`, `EXCEPTION_STATE_RESOLVED` or `EXCEPTION_STATE_ARCHIVED` (filters accept the short `PENDING`, `RESOLVED`, `ARCHIVED`). An exception may belong to a `group`; `""` means ungrouped. List the workspace's groups with `GET .../exceptionGroups` (currently `missing_values`, `invalid_values`, `user_system_error`, `internal_error`, `validation_error`).

Astral then files the exception to the **Workbench** as a work unit on a work item. The work item's chat with the `hermes` agent is where the exception is discussed and resolved, and the work unit takes a direct decision (retry or stop). See "Resolving an exception" below.

## Inspection Endpoints

### List exceptions

```bash
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/exceptions?page_size=20"
```

Supports `filter` by `state`, `automation`, `group`, `run`, `create_time` (AIP-160):

```bash
# Pending exceptions for a specific automation
...exceptions?filter=state%20%3D%20PENDING%20AND%20automation%20%3D%20%22${AUTO_ID}%22

# All missing_values exceptions
...exceptions?filter=group%20%3D%20%22missing_values%22

# Exceptions of one run (bare run id)
...exceptions?filter=run%20%3D%20%22${RUN_ID}%22
```

### Get exception details

```bash
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/exceptions/${EXCEPTION_ID}"
```

Returns `name`, `run` (run resource name), `automation` (bare id), `title`, `description` (a readable summary), `message` (the raw traceback), `location`, `group`, `state`, `stage`, `assignee`, `execution_id`, and `typed_extra` diagnostics such as `book_name`, `procedure_id` and `stack_trace`.

### Count exceptions

Aggregate counts by dimension — useful for dashboards and triage. Each is a `GET` with an optional `filter` (same fields as list) and `page_size`/`page_token`.

```bash
# Count by group
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/exceptions:countByGroup?filter=state%20%3D%20PENDING"

# Count by automation
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/exceptions:countByAutomation"

# Count by assignee
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/exceptions:countByAssignee"
```

Responses carry `group_counts` (each with a `group` object: `name`, `title`, `description`, `suggested_action`), `automation_counts` (`automation` resource name and `count`) or `assignee_counts` (`assignee` and `count`), plus `total_size` and `total_exception_count`.

## Management Endpoints

### Assign exceptions

Assign a single exception by resource name (`name`):

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"name": "organizations/'"${ORG}"'/workspaces/'"${WS}"'/exceptions/'"${EXCEPTION_ID}"'", "assignee": "users/'"${USER_ID}"'"}' \
  "${BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/exceptions:assign"
```

Bulk assign pending exceptions by filter (`group`, `automation`, `create_time`, `run`, `stage`):

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"filter": "automation = \"'"${AUTO_ID}"'\" AND group = \"missing_values\"", "assignee": "users/'"${USER_ID}"'"}' \
  "${BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/exceptions:assign"
```

Pass exactly one of `name` or `filter`. Set `assignee` to `""` (empty string) to unassign. The response is `{"assigned_count": N}`. This is the exception's own assignee, not the owner of its Workbench work item.

### Archive exceptions

Move PENDING exceptions to ARCHIVED state. Filter is required (do NOT filter by state — archive only targets PENDING).

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"filter": "automation = \"'"${AUTO_ID}"'\""}' \
  "${BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/exceptions:archive"
```

Filter fields: `run`, `automation`, `create_time`, `group`. To abandon whole runs together with their pending exceptions, archive the runs instead (`runs:archive`, see [runs-api.md](runs-api.md)).

### Unarchive exceptions

Restore ARCHIVED exceptions back to PENDING.

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"filter": "automation = \"'"${AUTO_ID}"'\""}' \
  "${BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/exceptions:unarchive"
```

## Resolving an exception

A published run's exception is resolved in the Workbench. Set a workspace prefix for the calls below:

```bash
WS_API="${BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}"
EXCEPTION_NAME="organizations/${ORG}/workspaces/${WS}/exceptions/${EXCEPTION_ID}"
```

### 1. Find the exception's work unit

The work unit's `source_ref` is the exception's resource name. A rejected fix files a new unit with the same `source_ref`, so take the newest.

```bash
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${WS_API}/workUnits?filter=source_ref%20%3D%20%22${EXCEPTION_NAME}%22"
```

From the newest unit keep `name` (`.../workUnits/{work_unit}`), `kind` (e.g. `astral.automation_exception`), `status`, `work_item` (`.../workItems/{work_item}`) and `answer_form`, which lists the decisions the unit accepts (field `action` with options `patch`, `retry`, `stop`, plus an optional `reason`). Only a unit with `status` `WORK_UNIT_STATUS_WAITING_FOR_INPUT` takes an answer.

### 2a. Submit a decision (retry or stop)

When the user has decided to retry the failed step unchanged or to stop the run, submit it straight to the work unit:

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"answer": {"kind": "astral.automation_exception", "values": {"action": {"text": "stop"}, "reason": {"text": "Duplicate invoice, not needed"}}}}' \
  "${WS_API}/workUnits/${WORK_UNIT_ID}/submissions"
```

Use the unit's own `kind`, and an `action` its `answer_form` offers. `retry` resumes the run with the failed step unchanged; `stop` stops the run and archives it, and the exception becomes `EXCEPTION_STATE_RESOLVED`. The unit moves to `WORK_UNIT_STATUS_ANSWERED`.

### 2b. Reply in the work item's chat

To guide the resolution (for example, ask for a corrected value), message the `hermes` agent in the work item's chat. The work item's `kind` maps to its agent through `GET /api/v1/workItemKinds` (`astral.automation_exception` → `hermes`). The Workbench usually opens the chat itself; find its thread by the `workItemId` variable:

```bash
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${WS_API}/agents/hermes/threads?filter=variables.workItemId%20%3D%3D%20%22${WORK_ITEM_ID}%22"
```

Then send the message to the newest `thread_id` (it is fire-and-forget and returns `{"ok": true}`):

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"message": {"content": "Use the backup email address instead"}}' \
  "${WS_API}/agents/hermes/threads/${THREAD_ID}/input"
```

Read the reply with `GET ${WS_API}/agents/hermes/threads/${THREAD_ID}/events` (ordered events: `input_text`, streamed `output_text` chunks, then `generation_complete`). The agent shows the user only the text inside its `<user-message>` blocks. A work item can group several exceptions that failed the same way, so a fix agreed in its chat can affect all of them; the agent applies a fix or a stop only after the user confirms it in the chat.

### Legacy automations

Automations of a kind other than `AUTOMATION_KIND_QUILL2` are resolved by the in-process `astral` agent instead. Its thread is the run-scoped event stream: read it with `GET .../automations/${AUTO_ID}/runs/${RUN_ID}/agents/astral/events` and reply with `POST` to the same path and a body of `{"user_message": {"content": "..."}, "exception": "<exception resource name>"}`. For Quill-built automations that stream is empty.

## Troubleshooting Guides

Guide entries record how earlier exceptions of an automation were resolved.

### List guide entries for an automation

```bash
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/automations/${AUTO_ID}/guideEntries?page_size=20"
```

Returns `guide_entries`, `next_page_token` and `total_size`.

### Get a guide entry

```bash
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/automations/${AUTO_ID}/guideEntries/${GUIDE_ENTRY_ID}"
```

A guide entry has `title`, `root_cause`, `resolution_steps`, `resolution_notes`, `source_exception`, `source_run` and a `state` (`STATE_PENDING_APPROVAL`, `STATE_APPROVED`, `STATE_REJECTED`, `STATE_ARCHIVED`).

## Triage Flow

1. **Assess volume**: count exceptions with `exceptions:countByGroup` (or by automation or assignee) to see where the problems cluster.
2. **List and filter**: list PENDING exceptions for the target automation or group.
3. **Inspect**: get exception details, then find its work unit and read the work item's chat.
4. **Act**: reply in the work item's chat, submit a retry or stop decision, assign an owner, or archive if resolved externally.
5. **Check guides**: look for existing guide entries before escalating.
