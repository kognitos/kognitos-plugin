# Files API

Use this reference when you need to upload, inspect, or read files used by automations.

## Overview

Files are organization-scoped resources. Automations that accept file inputs expect a file resource name (not raw content). The typical flow is: upload the file, get its resource name, then pass it as an automation input.

## Endpoints

### Upload a file

For small files (under 1 MB), encode the content as base64 and upload directly:

```bash
# Encode and upload
CONTENT_B64=$(base64 < input.csv)

curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{\"filename\": \"input.csv\", \"content_base64\": \"${CONTENT_B64}\"}" \
  "${BASE_URL}/api/v1/organizations/${ORG}/files:upload"
```

For larger or binary files, omit `content_base64` to get a pre-signed upload URL:

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"filename": "large-report.pdf"}' \
  "${BASE_URL}/api/v1/organizations/${ORG}/files:upload"
```

The response includes an `upload_url` — use it to PUT the file content directly.

### Get file metadata

```bash
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${BASE_URL}/api/v1/organizations/${ORG}/files/${FILE_ID}"
```

Returns: filename, size, MIME type, creation time.

### Read file content

```bash
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${BASE_URL}/api/v1/organizations/${ORG}/files/${FILE_ID}:read"
```

- Text files (`text/*`, JSON, CSV, XML, YAML) — content returned inline.
- Binary files — metadata and a download URL returned.

## Using Files as Automation Inputs

After uploading, the file resource name (e.g. `organizations/{org}/files/{file_id}`) can be passed as an input when invoking an automation:

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "stage": "AUTOMATION_STAGE_DRAFT",
    "inputs": {
      "input_file": {"file": {"name": "organizations/${ORG}/files/${FILE_ID}"}}
    }
  }' \
  "${BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/automations/${AUTO_ID}:invoke"
```
