# Workbench API

Use this reference when you need the queue of things waiting for a person in a workspace: published-run exceptions, document extraction reviews, and questions an automation asks while it runs. It also covers **guides**, the standing instructions the Workbench agent follows for a work item.

## Overview

The Workbench groups requests for attention:

- A **work unit** is one request, for example one exception on one run. It carries a summary, the evidence a person needs, an `answer_form` describing the answers it accepts, and a `status`.
- A **work item** groups similar units (same automation, same cause and step) so they can be handled together. Each work item has a chat with an agent that helps resolve it.
- A **work item kind** defines what a work item is and which agent handles its chat.
- A **guide** is a standing instruction attached to a work item, telling the agent how to handle that kind of request next time.

To resolve a published run's exception (find its work unit, submit retry or stop, or reply in the work item's chat), follow [exceptions-api.md](exceptions-api.md). This page covers the rest of the Workbench.

All workspace paths below are relative to:

```text
${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}
```

## Work item kinds

```bash
curl -sS -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${KOGNITOS_BASE_URL}/api/v1/workItemKinds"
```

| Kind | What it is | Agent | Grouped by |
|------|------------|-------|------------|
| `astral.automation_exception` | A published run could not complete and needs input | `hermes` | `automation_id`, `failure_cause`, `failure_site` |
| `astral.idp_extraction_error` | Document extraction has missing or low-confidence fields | `hermes` | `automation_id`, `failure_site` |
| `jeeves.runtime_ask` | A running automation is waiting for a person to answer a question | `merlin` | `automation_id`, `question_key` |

Each kind also says whether its items can be archived (`dismissible`) and whether the UI prepares a proposal before opening the chat (`preparation_required`). Treat the list as open-ended: new kinds are added over time.

## Work items

```bash
# Items that still need someone, newest activity first
curl -sS -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/workItems?filter=has_units_with_status(WAITING_FOR_INPUT)&order_by=update_time%20desc"
# → {"work_items": [{"name": ".../workItems/{work_item_id}", "kind": "astral.automation_exception",
#     "question": "...", "assignee": "", "agg_labels": {...},
#     "unit_counts": [{"status": "WORK_UNIT_STATUS_WAITING_FOR_INPUT", "count": 2}, ...], ...}],
#    "next_page_token": "", "total_size": 1}

curl -sS -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/workItems/${WORK_ITEM_ID}"
```

Filters (AIP-160, URL-encode them):

| Filter | Meaning |
|--------|---------|
| `kind = "astral.automation_exception"` | One kind |
| `has_units_with_status(WAITING_FOR_INPUT)` | Has at least one unit in that status. Statuses: `WAITING_FOR_INPUT`, `PROCESSING`, `ANSWERED`, `DISMISSED`, `WITHDRAWN` |
| `NOT assignee:*` | Unassigned |
| `assignee = "users/{user_id}"` | Assigned to one person (a bare id is rejected) |
| `labels.automation_id = "{automation_id}"` | One of the kind's grouping labels |
| `create_time > "2026-11-01T00:00:00Z"` | Also `update_time`; `=`, `!=`, `<`, `<=`, `>`, `>=` |

`order_by` accepts `create_time` or `update_time`, each `asc` (default) or `desc`. `page_size` defaults to 50, at most 1000.

### Assign, hand back, archive

```bash
# Assign (users/{user_id}, the form this API returns in submitter and created_by)
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"assignee": "users/'"${USER_ID}"'"}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/workItems/${WORK_ITEM_ID}:assign"

# Hand an assignment back, with a reason
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"reason": "Needs finance sign-off"}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/workItems/${WORK_ITEM_ID}:decline"
```

- Assigning only works on an item with unresolved units; otherwise it fails with `400` (`is archived or has no unresolved units`). Assignment does not restrict who may answer.
- `:archive` (`{"reason": "..."}`) dismisses an item's unresolved units and `:unarchive` restores them. Only kinds with `dismissible: true` can be archived; the kinds listed above all return `400` (`kind_not_dismissible`). For exceptions, archive the run instead (see [exceptions-api.md](exceptions-api.md)).

## Work units

```bash
# Units of one work item (work_item takes the full resource name)
curl -sS -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/workUnits?filter=work_item%20%3D%20%22${WORK_ITEM_NAME}%22"

curl -sS -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/workUnits/${WORK_UNIT_ID}"
```

A unit has:

- `summary`, `detail` and `identifying_details` (label and value pairs) describing the request in business language, and `evidence`, the facts behind it (for an exception: the run, the failing code and lines, the message).
- `source_ref`, the id of what raised it (for an exception, the exception's resource name), and `labels`.
- `status`: `WORK_UNIT_STATUS_WAITING_FOR_INPUT` (needs an answer), `_PROCESSING` (being prepared, no human request yet), `_ANSWERED`, `_DISMISSED` (item archived) or `_WITHDRAWN` (the source ended it).
- `answer_form`, the fields an answer must fill, and once answered, `submission` (the accepted answer) and `delivery` (whether the source applied it: `outcome` such as `DECISION_OUTCOME_APPLIED`).

Unit filters: `work_item`, `kind`, `source_ref`, `status` (`=`, `!=`), `labels.<key>`, and `create_time`, `update_time`, `settle_time` (comparisons). `NOT work_item:*` finds units not grouped into an item.

Answers are submitted with `POST .../workUnits/{work_unit_id}/submissions` (one unit) or `POST .../workUnits/submissions:batchCreate` (several units of one work item with the same answer). The answer's shape comes from the unit's `answer_form`; [exceptions-api.md](exceptions-api.md) shows it for exceptions. Read a submission back with `GET .../workUnits/{work_unit_id}/submissions/{submission_id}`.

## Guides

Guides tell the work item's agent how to handle its requests, for example "retry once if the file is empty". They belong to one work item.

```bash
# Create
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"work_item": "'"${WORK_ITEM_NAME}"'", "title": "Empty files", "body": "Retry once if the file is empty; stop the run if it is still empty.", "scope": "Only for .docx inputs"}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/guides"
# → {"name": ".../guides/{guide_id}", "state": "GUIDE_STATE_REVIEW_REQUIRED", "etag": "...", ...}

# List a work item's guides, or search all guides by text
curl -sS -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/guides?work_item=${WORK_ITEM_NAME}"
curl -sS -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/guides?filter=text%3A%22empty%22"

# Let the agent apply it without asking (update_mask and the current etag are required)
curl -sS -X PATCH \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"state": "GUIDE_STATE_AUTO", "etag": "'"${ETAG}"'"}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/guides/${GUIDE_ID}?update_mask=state"

# Delete (pass the current etag)
curl -sS -X DELETE -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/guides/${GUIDE_ID}?etag=${ETAG}"
```

- `state`: `GUIDE_STATE_REVIEW_REQUIRED` (default; the agent proposes and asks before submitting), `GUIDE_STATE_AUTO` (the agent may apply it and submit on its own) or `GUIDE_STATE_DISABLED` (ignored; listed only with `include_disabled=true`).
- Every update returns a new `etag`. A stale one fails with `409` (`guide changed; reload before retrying`): read the guide again and retry.
- Guide filters: `state`, `create_time`, `update_time`, `text:"..."` (searches title, body and scope), `work_item.kind` and `work_item.labels.<key>`.
- Guides are separate from the guide entries an automation's exceptions produce (see [exceptions-api.md](exceptions-api.md)).

## Live updates

`GET .../workItems:stream` and `GET .../workUnits:stream?work_item={work_item_name}` are Server-Sent Events streams of changes. They open with a `: connected` comment; read them line by line with `curl -N`.

## Gotchas

- `agg_labels` on a work item is a typed dictionary (`{"dictionary": {"entries": [{"key": {"text": "automation_id"}, "value": {"text": "..."}}]}}`), while a unit's `labels` is a plain string map.
- `archive_time` is not filterable. An archived item has `archive_time` set.
- `revision` and `descriptor_version` are 64-bit numbers serialized as JSON strings.
