# Exceptions API

Use this reference when you need to inspect, triage, or resolve exceptions raised during automation runs.

## Overview

An exception is an error that requires human attention. When a run enters `awaiting_guidance`, one or more exceptions have been raised. Exceptions have states (`PENDING`, `RESOLVED`, `ARCHIVED`) and belong to groups (`missing_values`, `user_system_error`, `internal_error`).

Each exception has a resolution thread — a conversation between the exception resolution agent and human operators. You can reply to guide the agent toward resolution.

## Inspection Endpoints

### List exceptions

```bash
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/exceptions?page_size=20"
```

Supports `filter` by `state`, `automation`, `group`, `run`, `create_time`:

```bash
# Pending exceptions for a specific automation
...exceptions?filter=state%20%3D%20%22PENDING%22%20AND%20automation%20%3D%20%22${AUTO_ID}%22

# All missing_values exceptions
...exceptions?filter=group%20%3D%20%22missing_values%22
```

### Get exception details

```bash
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/exceptions/${EXCEPTION_ID}"
```

Returns: message, location in the automation, group, resolution status, assignee.

### Count exceptions

Aggregate counts by dimension — useful for dashboards and triage.

```bash
# Count by group (missing_values, user_system_error, internal_error)
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"count_by": "group"}' \
  "${BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/exceptions:count"
```

Valid `count_by` values: `group`, `automation`, `assignee`.

Supports the same `filter` fields as list (state, automation, group, run, create_time).

### List exception events (resolution thread)

View the conversation between the exception agent and operators. Requires the automation and run that raised the exception.

```bash
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/automations/${AUTO_ID}/runs/${RUN_ID}/exceptions/${EXCEPTION_ID}/events?page_size=50"
```

## Management Endpoints

### Assign exceptions

Assign a single exception by resource name:

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"exception_name": "organizations/${ORG}/workspaces/${WS}/exceptions/${EXCEPTION_ID}", "assignee": "users/${USER_ID}"}' \
  "${BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/exceptions:assign"
```

Bulk assign by filter:

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"filter": "automation = \"${AUTO_ID}\" AND group = \"missing_values\"", "assignee": "users/${USER_ID}"}' \
  "${BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/exceptions:assign"
```

Set `assignee` to `""` (empty string) to unassign.

### Archive exceptions

Move PENDING exceptions to ARCHIVED state. Filter is required (do NOT filter by state — archive only targets PENDING).

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"filter": "automation = \"${AUTO_ID}\""}' \
  "${BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/exceptions:archive"
```

Filter fields: `run`, `automation`, `create_time`, `group`.

### Unarchive exceptions

Restore ARCHIVED exceptions back to PENDING.

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"filter": "automation = \"${AUTO_ID}\""}' \
  "${BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/exceptions:unarchive"
```

### Reply to the exception resolution agent

Send guidance to the agent resolving an exception. The agent processes the message asynchronously — use `list_events` to check for the reply.

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"message": "Use the backup email address instead", "exception_id": "${EXCEPTION_ID}"}' \
  "${BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/automations/${AUTO_ID}/runs/${RUN_ID}/exceptions:reply"
```

Omit `exception_id` to send to the general resolution thread.

## Troubleshooting Guides

### Get a guide entry

```bash
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/automations/${AUTO_ID}/guides/${GUIDE_ID}"
```

### List guides for an automation

```bash
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/automations/${AUTO_ID}/guides?page_size=20"
```

## Triage Flow

1. **Assess volume**: count exceptions by `group` to see where the problems cluster.
2. **List and filter**: list PENDING exceptions for the target automation or group.
3. **Inspect**: get exception details and read the resolution thread (`list_events`).
4. **Act**: reply to guide the agent, assign to an owner, or archive if resolved externally.
5. **Check guides**: look for existing troubleshooting guides before escalating.
