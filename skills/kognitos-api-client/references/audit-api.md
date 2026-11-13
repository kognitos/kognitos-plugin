# Audit Log API

Use this reference when you need to answer "who did what, and when" in an organization: runs started and stopped, automations created, published or deleted, exceptions raised and assigned, API keys created, files downloaded.

## Overview

Kognitos services record actions as **audit events**. Events are kept per organization and cover all of its workspaces. The API is read-only. Not every action is audited yet: automation and run actions are, but check that the actions you care about appear before you rely on the log for them.

All paths are organization-scoped:

```text
${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/auditEvents
```

Reading the audit log needs the audit permissions on your organization role. A `403` means your role does not grant them.

## List events

Newest first by default:

```bash
curl -sS -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/auditEvents?page_size=50"
```

```json
{
  "audit_events": [
    {
      "name": "organizations/{org}/auditEvents/{event_id}",
      "event_time": "2026-11-13T07:10:56.256308Z",
      "workspace_id": "{workspace_id}",
      "category": "AUDIT_CATEGORY_RUN_LIFECYCLE",
      "event_type": "AUDIT_EVENT_TYPE_RUN_PAUSED",
      "action": "pause",
      "actor": {"user_id": "", "display_name": "", "email": "", "actor_type": "AUDIT_ACTOR_TYPE_SERVICE", "pat_id": ""},
      "resource_name": "organizations/{org}/workspaces/{ws}/automations/{automation_id}/runs/{run_id}",
      "before_json": "",
      "after_json": "",
      "status": "AUDIT_STATUS_SUCCESS",
      "metadata": {"reason": "..."},
      "source_service": "jeeves"
    }
  ],
  "next_page_token": "..."
}
```

Page with `page_token`. Get one event with `GET .../auditEvents/{event_id}` (the last segment of `name`):

```bash
curl -sS -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/auditEvents/${EVENT_ID}"
```

## Filter

`filter` is an AIP-160 expression. Only these fields are accepted; any other field returns `400` (`unknown filter field`):

| Field | Example |
|-------|---------|
| `event_type` | `event_type = "AUDIT_EVENT_TYPE_AUTOMATION_CREATED"` |
| `category` | `category = "AUDIT_CATEGORY_RUN_LIFECYCLE"` |
| `actor` (alias `actor_user_id`) | `actor = "{user_id}"`. Your own id: `GET /api/v1/me` returns `name: users/{user_id}` |
| `workspace_id` | `workspace_id = "{workspace_id}"` |
| `event_time` | `event_time >= "2026-11-01T00:00:00Z"` |
| `status` | `status = "AUDIT_STATUS_FAILURE"` |
| `source_service` | `source_service = "grimoire"` |

Combine with `AND`, `OR` and parentheses. Sort with `order_by=event_time asc` for oldest first.

```bash
# What happened to automations in one workspace since November 1
FILTER='workspace_id = "'"${WS}"'" AND category = "AUDIT_CATEGORY_AUTOMATION_LIFECYCLE" AND event_time >= "2026-11-01T00:00:00Z"'
curl -sS -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/auditEvents?filter=$(jq -rn --arg f "${FILTER}" '$f|@uri')"
```

## Key fields

- `category` groups event types, for example `AUDIT_CATEGORY_RUN_LIFECYCLE`, `AUDIT_CATEGORY_AUTOMATION_LIFECYCLE`, `AUDIT_CATEGORY_VERSIONING_PUBLISHING`, `AUDIT_CATEGORY_EXCEPTIONS_RUN_INTERVENTION`, `AUDIT_CATEGORY_WORK_ITEMS`, `AUDIT_CATEGORY_AUTHENTICATION_SECURITY`, `AUDIT_CATEGORY_DATA_ACCESS_EXPORTS`, `AUDIT_CATEGORY_ORG_WORKSPACE_ADMINISTRATION`.
- `event_type` is the specific action (`AUDIT_EVENT_TYPE_RUN_STARTED`, `..._PUBLISH_SUCCEEDED`, `..._EXCEPTION_ASSIGNED`, `..._API_KEY_CREATED`, ...). `action` is a short verb (`create`, `publish`, `pause`).
- `actor.actor_type` is `AUDIT_ACTOR_TYPE_USER`, `AUDIT_ACTOR_TYPE_SERVICE` (the platform acting on its own, for example a run completing) or `AUDIT_ACTOR_TYPE_SUPPORT`. For users, `user_id`, `display_name` and `email` are filled in; `pat_id` can be empty even when the action came through an API key, so don't use it to tell API-key actions apart.
- `resource_name` is the full resource name of the affected object. Use it to correlate with runs, automations and exceptions.
- `status` is `AUDIT_STATUS_SUCCESS`, `AUDIT_STATUS_FAILURE` or `AUDIT_STATUS_PENDING`.

## Export

`POST .../auditEvents:export` builds a CSV of the events matching `filter` and returns a short-lived link:

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"filter": "event_time >= \"2026-11-01T00:00:00Z\"", "format": "EXPORT_FORMAT_CSV"}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/auditEvents:export"
# → {"download_uri": "https://...", "expire_time": "..."}
```

Download `download_uri` without the `Authorization` header before `expire_time`.

## Gotchas

- `before_json` and `after_json` are JSON **strings**, and are often empty. Parse them before use.
- An empty `workspace_id` means an organization-level event.
- Empty values come back as `""` rather than being omitted, and `credits_delta` is omitted when zero.
- The audit log records actions, not run content. For what a run did step by step, use the run's events in [runs-api.md](runs-api.md).
