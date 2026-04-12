# Runs API

Use this reference when you need to list, inspect, or control automation runs.

## Overview

A run is a single execution of an automation. Runs progress through states: `pending` → `executing` → `completed` | `failed` | `awaiting_guidance` | `stopped`. Each run records a step-by-step event log and, on completion, a set of typed outputs.

## Endpoints

### List runs

```bash
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/automations/${AUTO_ID}/runs?page_size=20"
```

Supports `filter` by `create_time`:

```bash
# Runs from the last 24 hours
...runs?filter=create_time%20%3E%3D%20%222026-04-10T00%3A00%3A00Z%22&page_size=20
```

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
| `completed` | Done — `outputs` map contains results |
| `failed` | Terminated with an unrecoverable error |
| `awaiting_guidance` | Paused — an exception was raised and the run is waiting for human input to resolve it. The run is **not failed**; it can resume after the exception is addressed. |
| `stopped` | Paused by a user or control action |

**Important:** `awaiting_guidance` and `failed` are distinct states. A run awaiting guidance is recoverable — resolve the exception (reply to the agent, provide missing input, fix the connection) and the run can continue. A failed run is terminal.

### Get run outputs

Returns the final output values from a completed run. Protobuf numeric values are unwrapped to plain JSON.

```bash
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/automations/${AUTO_ID}/runs/${RUN_ID}:getOutputs"
```

Output values use `commonV1Value` types:

| Type | Example |
|------|---------|
| number | `{"number": {"lo": 500500, "mid": 0, "hi": 0, "flags": 0}}` |
| text | `{"text": "hello"}` |
| file | `{"file": {"name": "organizations/.../files/...", ...}}` |

### List run events (step-by-step log)

The primary debugging view — shows each step the automation executed.

```bash
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/automations/${AUTO_ID}/runs/${RUN_ID}/events?page_size=100"
```

Supports `filter` by event type. Paginate with `page_token` from the response.

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

RUN_ID=$(echo "$RUN_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['run_id'])")

# Poll (in application code, use exponential backoff)
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${BASE_URL}/api/v1/${RUN_ID}"
```

States that stop polling: `completed`, `failed`, `awaiting_guidance`, `stopped`.

- `completed` / `failed` are final — the run is done.
- `awaiting_guidance` / `stopped` are paused — the run can resume after intervention.
