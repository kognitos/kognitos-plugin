# Runs API

Use this reference when you need to list, inspect, or control automation runs.

## Overview

A run is a single execution of an automation. Runs progress through states: `pending` → `executing` → `completed` | `failed` | `awaiting_guidance` | `awaiting_answer` | `stopped`. Each run records a step-by-step event log and, on completion, a set of typed outputs.

## Endpoints

### List runs

```bash
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/automations/${AUTO_ID}/runs?page_size=20"
```

Newest first; at most 10 per page unless `page_size` is set. Supports `filter` (AIP-160) on `create_time`, `runState` (`Pending`, `Executing`, `Stopped`, `WaitingForGuidance`, `Completed`, …), `stage` (`Draft`, `Published`), `invocation_source`, `stage_version`, `archived`, and free-text `search : "term"` over inputs, outputs and file contents:

```bash
# Runs from the last 24 hours
...runs?filter=create_time%20%3E%3D%20%222026-04-10T00%3A00%3A00Z%22&page_size=20

# Completed published runs
...runs?filter=runState%20%3D%20%22Completed%22%20AND%20stage%20%3D%20%22Published%22
```

Archived runs are left out unless the filter has `archived = true`.

### Get a run

```bash
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/automations/${AUTO_ID}/runs/${RUN_ID}"
```

The `state` field is a one-of:

| State | Meaning |
|-------|---------|
| `pending` | Queued, not yet started |
| `executing` | Currently running |
| `stopping` | Transitioning to `stopped` after a pause/stop request |
| `completed` | Done — `outputs` map contains results |
| `failed` | Terminated with an unrecoverable error |
| `awaiting_guidance` | Paused — an exception was raised and the run is waiting for human input to resolve it. The run is **not failed**; it can resume after the exception is addressed. |
| `awaiting_answer` | Intentionally waiting for a person to answer a question the automation asked (`prompt`, `form`). Planned waiting, not an exception. |
| `stopped` | Paused by a user or control action |

An archived run keeps its last state and gets an `archived_time`; it cannot be paused, continued or resolved any more.

Other useful fields: `stage` (`AUTOMATION_STAGE_DRAFT` or `AUTOMATION_STAGE_PUBLISHED`), `stage_version`, `user_inputs`, and `invocation_details.invocation_source`: `INVOCATION_SOURCE_MANUAL`, `INVOCATION_SOURCE_TRIGGER`, `INVOCATION_SOURCE_SCHEDULE`, `INVOCATION_SOURCE_PAT` (API key) or `INVOCATION_SOURCE_TEST` (Quill's test runs).

**Important:** `awaiting_guidance` and `failed` are distinct states. A run awaiting guidance is recoverable — resolve it and the run can continue. A failed run is terminal.

How `awaiting_guidance` is handled depends on the stage:

- **Published runs** are managed by **Astral**: the `awaiting_guidance` state references a real `exception` resource, which is resolved in the Workbench ([exceptions-api.md](exceptions-api.md)).
- **Draft runs** (Quill's `TEST` runs and user `MANUAL` draft invokes) disable exception handling: `awaiting_guidance` has an **empty `exception`** and just a `description`/`location` — no Astral. Drive the fix through Quill on its thread (it reads the traceback and patches the code). See [automation-agent-api.md](automation-agent-api.md).

### Get run outputs

A completed run carries its outputs in the run itself, under `state.completed.outputs`.

Outputs set so far by a run that has not completed (paused, stopped or awaiting guidance) are read from its execution. Take the `execution_id` from the run's events (`execution_journal.execution_id`; a resumed run can have several, use the latest) or from its exception, then:

```bash
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/executions/${EXECUTION_ID}/outputs"
```

This returns `outputs`, each entry a `{"value": ..., "type": ...}` pair.

Output values use `common.v1.Value` types:

| Type | Example |
|------|---------|
| number | `{"number": {"lo": 500500, "mid": 0, "hi": 0, "flags": 0}}` (a 96-bit decimal: `lo`/`mid`/`hi` words plus scale and sign in `flags`) |
| text | `{"text": "hello"}` |
| file | `{"file": {"remote": "organizations/.../workspaces/.../files/..."}}` |

### List run events (step-by-step log)

The primary debugging view — shows each step the automation executed.

```bash
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/automations/${AUTO_ID}/runs/${RUN_ID}/events?page_size=100"
```

Returns `run_events`: `run_update` events (state changes) and `execution_journal` events (`started`, `node_started`, `node_executed`, `completed`, …), each with its `execution_id`. Paginate with `page_token` from the response.

## Run Control

### Pause a run

Stops a currently executing run. Requires a reason.

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"reason": "Investigating unexpected behavior"}' \
  "${BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/automations/${AUTO_ID}/runs/${RUN_ID}:pause"
```

### Archive runs

Archive runs that should not be resumed; their pending exceptions are archived with them. Runs still executing are skipped. Archiving cannot be undone.

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"names": ["organizations/'"${ORG}"'/workspaces/'"${WS}"'/automations/'"${AUTO_ID}"'/runs/'"${RUN_ID}"'"]}' \
  "${BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/automations/${AUTO_ID}/runs:archive"
```

### Continue a paused run

Resumes a run that was paused or stopped.

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{}' \
  "${BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/automations/${AUTO_ID}/runs/${RUN_ID}:continue"
```

## Polling Pattern

After invoking an automation, poll the run until a terminal state:

```bash
# Invoke
RUN_RESPONSE=$(curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"stage": "AUTOMATION_STAGE_DRAFT", "inputs": {}}' \
  "${BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/automations/${AUTO_ID}:invoke")

# run_id is the run's full resource name: organizations/.../automations/.../runs/{run}
RUN_NAME=$(echo "$RUN_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['run_id'])")
RUN_ID="${RUN_NAME##*/}"

# Poll (in application code, use exponential backoff)
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/automations/${AUTO_ID}/runs/${RUN_ID}"
```

Because `run_id` is the full resource name, `${BASE_URL}/api/v1/${RUN_NAME}` is the same URL.

States that stop polling: `completed`, `failed`, `awaiting_guidance`, `awaiting_answer`, `stopped`.

- `completed` / `failed` are final — the run is done.
- `awaiting_guidance` / `awaiting_answer` / `stopped` are paused — the run can resume after intervention.
