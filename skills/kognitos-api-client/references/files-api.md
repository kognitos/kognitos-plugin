# Files API

Use this reference when you need to upload, inspect, or read files used by automations.

## Overview

Files are workspace-scoped resources named `organizations/{org}/workspaces/{ws}/files/{file}`. Automations that accept file inputs expect a file resource name (not raw content). The typical flow is: upload the file, get its resource name, then pass it as an automation input.

Older files may be organization-scoped (`organizations/{org}/files/{file}`). Read them through the matching org-scoped routes below; new uploads must be workspace-scoped. Use the scope the file's resource name carries: a workspace file is not found on the org-scoped routes.

## Endpoints

### Upload a file

Upload the content as `multipart/form-data` with the file in a form field named `file`:

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -F "file=@input.csv" \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/files:upload"
```

The response (HTTP 201) holds the file's metadata; `metadata.name` is the file resource name:

```json
{"metadata": {"name": "organizations/.../workspaces/.../files/...", "filename": "input.csv", "sizeBytes": 8, "mimeType": "text/csv", "createTime": "..."}}
```

To let someone without the token upload (for example, a browser or another machine), generate a pre-signed upload URL:

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/files:generateUploadUrl"
```

The response's `upload_uri` takes the same multipart POST without an `Authorization` header, and returns the same `metadata` body. It expires after one hour. Quote the URL and pass `--globoff`:

```bash
curl -sS --globoff -F "file=@large-report.pdf" "${UPLOAD_URI}"
```

### Get file metadata

```bash
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/files/${FILE_ID}/metadata"
```

Returns `name`, `filename`, `mime_type`, `size_bytes` (a string), `create_time` and `sha256_hash`. For an org-scoped file use `.../organizations/${ORG}/files/${FILE_ID}/metadata`.

### Download file content

Stream the file's bytes with the token (the response carries `Content-Type` and `Content-Disposition`):

```bash
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -o input.csv \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/files/${FILE_ID}:download"
```

For an org-scoped file use `.../organizations/${ORG}/files/${FILE_ID}:download`.

### Generate a download URL

To hand a file to a client that has no token, generate a pre-signed download URL (valid for one hour):

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/files/${FILE_ID}:generateDownloadUrl"
```

Returns `download_uri`. For an Arrow table (`application/vnd.apache.arrow.file`), pass `{"format": "DOWNLOAD_FORMAT_CSV"}` to download it converted to CSV. For an org-scoped file use `.../organizations/${ORG}/files/${FILE_ID}:generateDownloadUrl`.

### Delete a file

```bash
curl -sS -X DELETE \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/files/${FILE_ID}"
```

Returns `{}`; the metadata call then returns `404`. For an org-scoped file use `.../organizations/${ORG}/files/${FILE_ID}`.

There is no call that lists files. Keep every file id you create (uploads, and the ZIP each automation `:export` writes) if you need to delete it later.

## Using Files as Automation Inputs

Pass the file resource name as a `remote` file value when invoking an automation:

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "stage": "AUTOMATION_STAGE_DRAFT",
    "inputs": {
      "input_file": {"file": {"remote": "organizations/'"${ORG}"'/workspaces/'"${WS}"'/files/'"${FILE_ID}"'"}}
    }
  }' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/automations/${AUTO_ID}:invoke"
```

File values in run inputs and outputs use the same shape, `{"file": {"remote": "<file resource name>"}}`. A file value keyed `name` instead of `remote` is rejected with `INVALID_ARGUMENT`.
