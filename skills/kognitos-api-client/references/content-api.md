# Assets, Folders and Collections API

Use this reference when an automation needs workspace content that outlives a single run: reference documents and templates (**assets**, organized in **folders**), or tables of records it reads and writes (**collections**).

## Overview

- An **asset** is a file kept in the workspace library with a display name, description, tags and a folder. Its bytes are an ordinary uploaded file (see [files-api.md](files-api.md)); the asset adds the library metadata.
- A **folder** organizes assets. Folders nest to any depth; names must be unique within a parent.
- A **collection** is a typed table with a schema (columns) and rows. It has a **draft** and a **published** stage.

All paths below are workspace-scoped:

```text
${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}
```

`PATCH` on these resources requires an `update_mask` query parameter naming the fields you change (`?update_mask=display_name,tags`). Without it the call fails with `400`.

## Folders

```bash
# Create (set parent_folder_name to nest it)
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"display_name": "Invoices"}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/folders"
# → {"name": "organizations/{org}/workspaces/{ws}/folders/{folder_id}", "display_name": "Invoices",
#    "parent_folder_name": "", "asset_count": 0, "folder_count": 0, ...}

# Root folders, or the children of one folder
curl -sS -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/folders?parent_folder_name=${FOLDER_NAME}"

# The whole tree in one call: {"roots": [{"folder": {...}, "children": [...]}]}
curl -sS -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/folders:tree"

# Rename
curl -sS -X PATCH \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"display_name": "Invoices 2026"}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/folders/${FOLDER_ID}?update_mask=display_name"

# Delete. A folder that still holds assets or folders needs force=true, which deletes its contents too
curl -sS -X DELETE -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/folders/${FOLDER_ID}?force=true"
```

`FOLDER_NAME` is the full resource name (`organizations/{org}/workspaces/{ws}/folders/{folder_id}`); `FOLDER_ID` is its last segment. Moving (`:move` with `destination_parent_folder_name`) and copying (`:duplicate`, which copies the whole subtree and prefixes the copy's name with "Copy of ") work the same way as for assets below.

## Assets

Creating an asset takes two steps: upload the bytes, then register the uploaded file as an asset.

```bash
# 1. Upload the file; keep metadata.name
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -F "file=@terms.pdf" \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/files:upload"

# 2. Register it (file_name is the uploaded file's resource name)
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"asset": {"display_name": "Standard terms", "description": "Contract template", "folder_name": "'"${FOLDER_NAME}"'", "tags": ["legal"]}, "file_name": "'"${FILE_NAME}"'"}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/assets"
# → {"name": "organizations/{org}/workspaces/{ws}/assets/{asset_id}", "display_name": "Standard terms",
#    "folder_name": "...", "file_name": "{asset_id}", "mime_type": "application/pdf", "size_bytes": "48211",
#    "tags": ["legal"], "reference_uri": "bishop://{asset_id}", ...}
```

Leave `folder_name` out to put the asset at the workspace root.

```bash
# List: no folder_name = root only, a folder's resource name = that folder, "*" = every asset
curl -sS -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/assets?folder_name=*&order_by=create_time%20desc"

# Search by name or type (":" is a substring match)
curl -sS -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/assets?folder_name=*&filter=display_name%20%3A%20%22terms%22"

# Update metadata
curl -sS -X PATCH \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"display_name": "Standard terms v2", "tags": ["legal", "2026"]}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/assets/${ASSET_ID}?update_mask=display_name,tags"

# Move or copy to another folder
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"destination_folder_name": "'"${FOLDER_NAME}"'"}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/assets/${ASSET_ID}:move"

# Short-lived download link (fetch it without the Authorization header)
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/assets/${ASSET_ID}:generateDownloadUrl"
# → {"download_uri": "https://..."}

# Which automations use it: {"automations": [...]}
curl -sS -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/assets/${ASSET_ID}:traceAssetUsage"

# Delete
curl -sS -X DELETE -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/assets/${ASSET_ID}"
```

- Use `:duplicate` (same body as `:move`) to copy; the copy is named "Copy of ...".
- `GET .../assets:tags` returns every tag used in the workspace.
- Batch variants (`assets:batchMove`, `:batchDuplicate`, `:batchDelete`, `:batchDownload`, and the same for folders) take `{"names": [...]}` and return per-item `results`; `:batchDownload` returns one ZIP link.

## Collections

A collection holds typed rows. Its schema is a list of fields with a value type. Create it with a schema:

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "collection": {"display_name": "Approved vendors", "description": "Vendors cleared by finance", "tags": ["finance"]},
    "schema": {"fields": [
      {"name": "vendor", "type": {"scalar_type": "VALUE_SCALAR_TYPE_TEXT"}, "required": true},
      {"name": "limit", "type": {"scalar_type": "VALUE_SCALAR_TYPE_NUMBER"}},
      {"name": "active", "type": {"scalar_type": "VALUE_SCALAR_TYPE_BOOLEAN"}}
    ]}
  }' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/collections"
# → {"name": "organizations/{org}/workspaces/{ws}/collections/{collection_id}", "schema_version": 1,
#    "field_count": 3, "record_count": "0", "has_unpublished_changes": true, ...}
```

Scalar types: `VALUE_SCALAR_TYPE_TEXT`, `_NUMBER`, `_BOOLEAN`, `_DATETIME`, `_DATE`, `_TIME`, `_FILE`. Change the schema with `:addField` (`{"field": {...}}`), `:updateField`, `:deleteField` (`{"field_name": "..."}`) or `:updateSchema`; each bumps `schema_version`. `GET .../collections/{collection_id}/schema` returns the current fields.

### Rows

Row values are typed: `{"text": "..."}`, `{"bool_value": true}`, and numbers as a decimal `{"number": {"lo": ..., "mid": ..., "hi": ..., "flags": ...}}`. A number is a 96-bit integer (`lo`, `mid`, `hi`, 32 bits each) scaled down by the power of ten in bits 16 to 23 of `flags`; bit 31 of `flags` is the sign. So `{"lo": 125, "flags": 65536}` is 12.5, and `{"lo": 5, "flags": 2147483648}` is -5. Plain JSON values (`"Acme"`, `5`) are rejected.

```bash
# Insert one row: the body is the row itself
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"vendor": {"text": "Acme"}, "limit": {"number": {"lo": 125, "flags": 65536}}, "active": {"bool_value": true}}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/collections/${COLLECTION_ID}/rows"
# → {"row": {"vendor": {"text": "Acme"}, ..., "__row_id__": {"number": {"lo": 0, ...}}}}

# Insert many
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"rows": [{"fields": {"vendor": {"text": "Globex"}}}, {"fields": {"vendor": {"text": "Initech"}}}]}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/collections/${COLLECTION_ID}/rows:batchInsert"

# Query (POST). structured_filter takes comparison, logical (AND/OR of filters), negation or fuzzy_match
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"page_size": 100,
       "structured_filter": {"comparison": {"field": "vendor", "operator": "COMPARISON_OPERATOR_EQUAL", "value": {"text": "Acme"}}},
       "structured_order_by": [{"field": "vendor", "direction": "SORT_DIRECTION_ASCENDING"}]}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/collections/${COLLECTION_ID}/rows:query"
# → {"rows": [{"fields": {...}}], "next_page_token": "", "total_size": 1}
```

- Every row carries `__row_id__` (a number, starting at 0). Use it as `{row_id}` in `GET`, `PATCH` and `DELETE .../rows/{row_id}`; `PATCH` takes the changed columns as the body. `rows:batchDelete` takes `{"row_ids": ["1", "2"]}`.
- Operators: `COMPARISON_OPERATOR_EQUAL`, `_NOT_EQUAL`, `_LESS_THAN`, `_LESS_THAN_OR_EQUAL`, `_GREATER_THAN`, `_GREATER_THAN_OR_EQUAL`, `_HAS`, `_IN`. `fuzzy_match` (`{"field", "query", "threshold"}`) tolerates typos; the default threshold is 0.8.
- `page_size` is at most 1000.

### CSV in and out

```bash
# Import an uploaded CSV (source_uri is the file resource name from files:upload)
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"source_uri": "'"${FILE_NAME}"'", "options": {"first_row": "IMPORT_FIRST_ROW_MODE_HEADER"}}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/collections/${COLLECTION_ID}/rows:importCsv"
# → {"rows_imported": "2", "column_count": 2, "schema_version": 1}

# Export to a CSV download link
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/collections/${COLLECTION_ID}/rows:exportCsv"
# → {"download_uri": "https://..."}
```

### Draft and published

Schema edits and row writes go to the **draft** stage unless you pass `stage`. `:publish` promotes the draft **schema** to published:

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"published_by": "api"}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/collections/${COLLECTION_ID}:publish"
```

- Rows are kept per stage and publishing does not copy them. To read or write published rows, pass `"stage": "COLLECTION_STAGE_PUBLISHED"` in the `rows:query` / `rows:batchInsert` body, or `?stage=COLLECTION_STAGE_PUBLISHED` on the single-row routes.
- `GET .../collections?stage=COLLECTION_STAGE_PUBLISHED` lists published collections with a `preview` of their first rows. `has_unpublished_changes` tells you a draft schema is waiting to be published.

### Other collection calls

- `GET .../collections?filter=display_name%20%3A%20%22vendor%22` searches by name; `tags : "finance"` matches a tag.
- `PATCH .../collections/{collection_id}?update_mask=description` updates name, description or tags.
- `GET .../collections/{collection_id}:traceCollectionUsage` lists the automations that read or write it (`usage_type` `COLLECTION_USAGE_TYPE_READ` / `_WRITE`).
- `DELETE .../collections/{collection_id}` deletes the collection and its rows.

## Gotchas

- Some `400`s from these endpoints have an empty body. The reason is in the `grpc-message` response header (for example `Folder%20has%201%20assets`), so print headers with `-i` when a call fails without a message.
- An asset's id is the uploaded file's id, so the asset and the file share the last path segment.
- `created_by` can come back empty.
- `size_bytes` and `record_count` are 64-bit integers serialized as JSON strings.
