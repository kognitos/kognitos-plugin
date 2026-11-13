# Triggers API

Use this reference when an automation (or a workspace agent) should start on its own when something happens in a connected app: an email arrives, a webhook fires, or a poll finds new records. It also covers connection maintenance calls that [books-api.md](books-api.md) does not: waking an idle connection and choosing what a connection discovers.

For time-based runs, use [scheduling-api.md](scheduling-api.md) instead.

## Overview

An integration declares what can start a run in its descriptor (`GET .../books/{integration}/{version}`):

- `triggers`: push events, such as `new_email` on the `email` integration. Each has an `id`, a `configuration` schema and an `event_type` describing the event's fields.
- `polls`: checks the platform runs every few minutes, with an `id` and a `configuration` schema.

Wiring one to an automation takes three calls, in two services:

1. Create a **trigger instance** (or poll instance) on a connection, with its configuration.
2. Attach the automation to the instance.
3. Register an **automation trigger** on the automation, mapping event fields to automation inputs.

All paths below are relative to:

```text
${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}
```

## Start an automation on incoming email

The `email` integration's `email-book-connection` connection receives mail sent to addresses on your Kognitos domain (`app.us-1.kognitos.com` receives at `@us-1.kognitos.com`). The web UI uses `automation-{automation_id}-draft@...` for a draft and `...-published@...` for the published version.

```bash
# 1. Trigger instance on the connection (EMAIL_BOOK_VERSION is the connection's book_version from GET .../connections)
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"trigger_id": "new_email", "name": "Invoices inbox",
       "configuration": {"email_address": {"text_value": "automation-'"${AUTO_ID}"'-draft@us-1.kognitos.com"}}}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/books/email/${EMAIL_BOOK_VERSION}/connections/email-book-connection/triggers"
# → {"trigger_instance": {"id": "email-book-connection-trigger-qzl85", "trigger_id": "new_email", "automation_ids": [], ...}}

# 2. Attach the automation (replaces the instance's automation list)
curl -sS -X PUT \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"automation_ids": ["'"${AUTO_ID}"'"], "connection_id": "email-book-connection"}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/triggers/${TRIGGER_INSTANCE_ID}/automations"

# 3. Register it on the automation: map automation inputs to event fields
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"trigger_id": "'"${TRIGGER_INSTANCE_ID}"'", "phase_type": "PHASE_TYPE_PRE",
       "input_mapping": {"subject": "email.subject", "invoice": "email.attachments"}}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/automations/${AUTO_ID}/triggers?stage=AUTOMATION_STAGE_DRAFT"
# → {"trigger_id": "...", "automation": "...", "input_mapping": {...}, "phase_type": "PHASE_TYPE_PRE", "is_active": true}
```

- `input_mapping` keys are the automation's input names; values are paths into the event, `{event}.{field}` (the email event's fields include `subject`, `body`, `sender`, `recipients`, `attachments`).
- `trigger_id` in step 3 is the **instance** id from step 1, not the integration's trigger id (`new_email`).
- `automation_ids` sent in step 1 is not applied; step 2 sets it.
- `stage` selects the draft or the published version of the automation. Register the trigger on the stage that should run.
- A new instance reports `status.state` `TRIGGER_INSTANCE_STATE_PENDING` until the connection has set it up.

### Manage automation triggers

```bash
# List (defaults to the draft; pass the stage for a published automation)
curl -sS -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/automations/${AUTO_ID}/triggers?stage=AUTOMATION_STAGE_PUBLISHED"

# Pause and resume without removing it
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"stage": "AUTOMATION_STAGE_DRAFT"}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/automations/${AUTO_ID}/triggers/${TRIGGER_INSTANCE_ID}:deactivate"
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"stage": "AUTOMATION_STAGE_DRAFT"}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/automations/${AUTO_ID}/triggers/${TRIGGER_INSTANCE_ID}:activate"

# Remove
curl -sS -X DELETE -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/automations/${AUTO_ID}/triggers/${TRIGGER_INSTANCE_ID}?stage=AUTOMATION_STAGE_DRAFT"
```

Removing the automation trigger also removes its trigger instance. Check `GET .../triggers` afterwards and delete any leftover instance with `DELETE .../connections/{connection_id}/triggers/{trigger_instance_id}`.

For a published automation with no draft, the trigger list without `stage` returns `404` (`Draft for automation ... doesn't exist`).

## Trigger and poll instances

```bash
# Everything configured in the workspace (filter by connection_id if needed)
curl -sS -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/triggers?filter=connection_id%20%3D%20%22email-book-connection%22"
curl -sS -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/polls"
curl -sS -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/agent-triggers"

# Change an instance's name or configuration
curl -sS -X PUT \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"name": "Invoices inbox (EU)", "configuration": {"email_address": {"text_value": "..."}}}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/connections/${CONNECTION_ID}/triggers/${TRIGGER_INSTANCE_ID}"
```

Each instance has `status.state` and `status.state_category`; webhook-style triggers also return the `endpoint` that receives events.

### Polls

A poll instance is created the same way, with `poll_id` and `poll_interval_minutes`, then attached and registered like a trigger instance:

1. `POST .../books/{integration}/{version}/connections/{connection_id}/polls` with `{"poll_id": "...", "poll_interval_minutes": 15, "configuration": {...}}`. The response's `poll_instance.id` is the instance id.
2. `PUT .../polls/{poll_instance_id}/automations` with `{"automation_ids": [...], "connection_id": "..."}`.
3. `POST .../automations/{automation_id}/triggers?stage=...` with `trigger_id` set to the poll instance id, as above.

Update with `PUT .../connections/{connection_id}/polls/{poll_instance_id}`; remove with `DELETE` on the same path.

### Agent triggers

An agent trigger starts **workspace agents** instead of an automation (see [agents-api.md](agents-api.md)). Create it with `POST .../books/{integration}/{version}/connections/{connection_id}/agent-triggers` and a body of `trigger_id`, `configuration`, `agent_ids` (the agents to start; each gets its own thread) and `prompt` (the message sent to them). Update or remove it with `PUT` / `DELETE .../connections/{connection_id}/agent-triggers/{trigger_instance_id}`.

## Connection maintenance

```bash
# Wake an idle connection (status INACTIVE, "scaled to zero") before calling it directly
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/connections/${CONNECTION_ID}:reactivate"

# The actions this connection offers, or a semantic search over them
curl -sS -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/connections/${CONNECTION_ID}/procedures"
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"query": "read rows", "top_k": 3}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/connections/${CONNECTION_ID}/procedures:search"

# Discoverables: objects in the connected app (tables, objects, sheets) it can expose as actions
curl -sS -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/connections/${CONNECTION_ID}/discoverables?search=invoice&limit=50"
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"what": ["Invoice", "Vendor"]}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/connections/${CONNECTION_ID}/discover"

# The account the connection is signed in as
curl -sS -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/connections/${CONNECTION_ID}/user-info"
```

- `:reactivate` returns the connection with its old state; poll `GET .../connections/{connection_id}` until `status.state` is `BOOK_CONNECTION_STATE_READY` (about 20 seconds in our tests). Runs wake a connection on their own; reactivate before calls that don't, such as `discoverables` and `user-info`, which fail with `500` (`not proxied by the activator`) while the connection is inactive.
- `discover` takes the names of the discoverables to expose (`what`). Only integrations with `discover_capable: true` have discoverables; others return an empty list.
- `user-info` only works for integrations with `userinfo_capable: true`; others return `500` (`No @userinfo function found in book`).
