# Automation Lifecycle API

Use this reference when you manage automations as objects rather than build them: copy, rename, label, export and import between workspaces, look at or roll back to earlier versions, switch them off, set default inputs and marked outputs, delete them, and move workspace agents with their automations.

Building and changing an automation's logic is done by talking to Quill ([automation-agent-api.md](automation-agent-api.md)); publishing and forking are covered there too. Running is in [runs-api.md](runs-api.md).

All paths below are relative to:

```text
${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}
```

## List compactly

```bash
curl -sS -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/automations:listSummaries?page_size=100"
# → {"automation_summaries": [{"name", "display_name", "description", "version", "latest_published_version",
#     "activation_state", "labels", "steps": [{"number", "title", "overview"}], "has_english_code", "update_time"}],
#    "next_page_token": ""}
```

Summaries are much smaller than full automations (no code, artifacts or AOP) and include the step titles. Use them for catalogs and pickers.

## Versions and revisions

Every save is a **revision**, named by its version (`0.3`, `1.0`, `1.1`).

```bash
# Newest first
curl -sS -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/automations/${AUTO_ID}/revisions:listSummaries?page_size=20"

# One revision (REVISION_ID is a version such as 1.0): the full automation as it was ("snapshot") and what changed in its inputs ("input_diff")
curl -sS -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/automations/${AUTO_ID}/revisions/${REVISION_ID}"

# Roll back: copy an old revision into a new draft
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"revision_id": "0.3"}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/automations/${AUTO_ID}:restore"
# → {"automation": {"version": "1.1", "latest_published_version": "1.0", ...}}

# Discard the current draft (on a never-published automation this deletes the automation)
curl -sS -X DELETE -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/automations/${AUTO_ID}/drafts"
```

- `:restore` never changes what is published. It creates a new draft from the old revision; publish it to make it live.
- Discarding a draft records a revision with `delete_time` set. Afterwards `GET .../automations/{automation_id}` can still report the discarded draft's version; use `:query?stage=AUTOMATION_STAGE_PUBLISHED` to read what is live.

## Copy, rename, label

```bash
# Duplicate a version into a new automation (a never-published draft)
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"stage": "AUTOMATION_STAGE_PUBLISHED", "display_name": "Invoice intake (EU)"}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/automations/${AUTO_ID}:duplicate"

curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"display_name": "Invoice intake v2"}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/automations/${AUTO_ID}:rename"

# Replaces the whole label set
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"labels": ["finance", "eu"]}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/automations/${AUTO_ID}:setLabels"
```

`:move` (`{"destination_workspace": "...", "revision_id": "..."}`) moves an automation to another workspace of the organization.

## Export and import

Export writes one revision to an encrypted ZIP that only Kognitos can read back. Import creates a new automation from that ZIP, in any workspace you can write to.

`revision_id` is required (without it, export returns `400`). Each export saves the ZIP as a new workspace file: the `{file_id}` in `zip_uri`'s path. Files can't be listed, so delete it with `DELETE .../files/{file_id}` ([files-api.md](files-api.md)) after downloading.

```bash
# 1. Export
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"revision_id": "1.0"}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/automations/${AUTO_ID}:export"
# → {"zip_uri": "https://.../files/{file_id}:download?...", "expire_time": "..."}   (link valid for about an hour)

curl -sS -o automation.zip "${ZIP_URI}"

# 2. Upload the ZIP to the target workspace; keep metadata.name
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -F "file=@automation.zip" \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${TARGET_WS}/files:upload"

# 3. Import
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"zip_resource": "'"${FILE_NAME}"'"}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${TARGET_WS}/automations:import"
# → {"automation": {"name": ".../automations/{new_automation_id}", "version": "0.1", ...}}

# 4. What the copy still needs before it can run
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${TARGET_WS}/automations/${NEW_AUTO_ID}:validateImport"
# → {"is_imported_automation": true,
#    "missing_connections": [{"phase": "main", "alias": "file", "book_name": "file", "book_version": "1.17.0", "source_connection_display_name": "File"}],
#    "missing_trigger_kinds": []}
```

- The import is a never-published draft. Create the `missing_connections` in the target workspace (see [books-api.md](books-api.md)), recreate any triggers listed in `missing_trigger_kinds` (see [triggers-api.md](triggers-api.md)), then publish.
- The ZIP carries the automation's code, AOP, inputs, outputs and connection references (integration and version), plus the source organization and workspace names. Schedules and run history are not included.

## Agent bundles

A workspace agent built in the Agent Builder can be exported together with the automations it uses, as one bundle:

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/agentBundles/${AGENT_ID}:export"
# → {"zip_uri": "https://...", "expire_time": "...", "automation_names": [...], "agent_connections": [...], "warnings": [...]}

curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"zip_resource": "'"${FILE_NAME}"'"}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${TARGET_WS}/agentBundles:import"
# → {"agent": "...", "automation_names": [...], "agent_connections": [...], "warnings": [...]}
```

The upload step is the same as for automations. `agent_version` in the export body optionally picks an agent version. `POST .../agentBundles/{agent_id}:validateImport` (`{}`) reports the imported agent's `missing_connections` and `missing_trigger_kinds`. To move only the agent's configuration, use the agent `:export` / `:import` in [agents-api.md](agents-api.md).

## Switch off, defaults, outputs

```bash
# Block new runs, and allow them again
curl -sS -X POST -H "Authorization: Bearer ${KOGNITOS_TOKEN}" -H "Content-Type: application/json" -d '{}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/automations/${AUTO_ID}:deactivate"
curl -sS -X POST -H "Authorization: Bearer ${KOGNITOS_TOKEN}" -H "Content-Type: application/json" -d '{}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/automations/${AUTO_ID}:activate"

# Default inputs used when a run doesn't supply them (typed values, per stage)
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"stage": "AUTOMATION_STAGE_DRAFT", "default_inputs": {"note": {"text": "hello"}}}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/automations/${AUTO_ID}:setDefaultInputs"
curl -sS -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/automations/${AUTO_ID}:listDefaultInputsHistory"

# Mark or unmark an output key (marked keys are listed in marked_outputs)
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"marked_output": "report"}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/automations/${AUTO_ID}:setMarkedOutputs"
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"marked_output": "report"}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/automations/${AUTO_ID}:unsetMarkedOutput"
```

- `:deactivate` sets `activation_state` to `AUTOMATION_ACTIVATION_STATE_DEACTIVATED`; invoking it then fails with `400` (`automation is deactivated`). `:activate`, `:deactivate`, `:setMarkedOutputs` and `:unsetMarkedOutput` act on the published version and return `400` / `404` for an automation that was never published.
- Default input values use the same typed form as run inputs. Each change is kept in `:listDefaultInputsHistory` with `change_time` and `change_actor`.

## Connections across automations

```bash
# How many automations use each connection (check before deleting or replacing one)
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"connection_ids": ["'"${CONNECTION_ID}"'"]}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/automations:countConnectionUsage"
# → {"connection_counts": [{"connection_id": "...", "count": 1}]}

# Point an automation at a different connection of the same integration
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"switches": [{"old_connection_id": "'"${OLD_CONNECTION_ID}"'", "new_connection_id": "'"${NEW_CONNECTION_ID}"'", "connection_alias": "'"${ALIAS}"'"}]}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/automations/${AUTO_ID}:switchConnections"
```

`connection_alias` is the key under the automation's `connections` map.

## Delete

```bash
curl -sS -X DELETE -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/automations/${AUTO_ID}"
```

This deletes an automation that has been published. An automation that was never published returns `404` (`Published version doesn't exist`); delete it with `DELETE .../automations/{automation_id}/drafts` instead.
