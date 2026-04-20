# Curl Examples

Use this reference for quick API exploration, auth validation, and debugging.

## Prerequisites

Set these environment variables (or source `.env.local`):

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `KOGNITOS_TOKEN` | Yes | — | PAT (`kgn_pat_` prefix) |
| `KOGNITOS_REGION` | No | `us` | Region |
| `KOGNITOS_ENV` | No | `prod` | Environment (`prod` or `dev`) |
| `KOGNITOS_ORGANIZATION_ID` | For most calls | — | Organization ID |
| `KOGNITOS_WORKSPACE_ID` | For most calls | — | Workspace ID |

## Base URL

```bash
# prod
BASE_URL="https://app.${KOGNITOS_REGION}-1.kognitos.com"

# dev
BASE_URL="https://app.${KOGNITOS_REGION}-1.${KOGNITOS_ENV}.kognitos.com"
```

## Discovery

### List organizations

```bash
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${BASE_URL}/api/v1/me/organizations?page_size=50"
```

### List workspaces in an org

```bash
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${BASE_URL}/api/v1/organizations/${KOGNITOS_ORGANIZATION_ID}/workspaces?page_size=50"
```

## Automations

### List automations

```bash
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${BASE_URL}/api/v1/organizations/${KOGNITOS_ORGANIZATION_ID}/workspaces/${KOGNITOS_WORKSPACE_ID}/automations?page_size=10"
```

### Get one automation

```bash
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${BASE_URL}/api/v1/organizations/${KOGNITOS_ORGANIZATION_ID}/workspaces/${KOGNITOS_WORKSPACE_ID}/automations/${AUTOMATION_ID}"
```

## Create Automation via the AI Agent

See [automation-agent-api.md](automation-agent-api.md) for the full flow. Summary:

### Step 1: Create automation shell

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"display_name": "My Automation"}' \
  "${BASE_URL}/api/v1/organizations/${KOGNITOS_ORGANIZATION_ID}/workspaces/${KOGNITOS_WORKSPACE_ID}/automations"
```

### Step 2: Create an agent thread linked to the automation

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{\"automation\": \"organizations/${KOGNITOS_ORGANIZATION_ID}/workspaces/${KOGNITOS_WORKSPACE_ID}/automations/${AUTOMATION_ID}\"}" \
  "${BASE_URL}/api/v1/organizations/${KOGNITOS_ORGANIZATION_ID}/workspaces/${KOGNITOS_WORKSPACE_ID}/agents/quill/threads"
```

Capture the returned `name` as `THREAD_NAME` — it includes the `automations/{auto_id}` segment and is the correct URL prefix for all subsequent thread operations.

### Step 3: Send prompt (response is a stream of JSON objects)

Note the double-nested `user_message` structure. The response body is concatenated pretty-printed JSON, not line-delimited NDJSON — parse with an incremental decoder (`json.JSONDecoder().raw_decode` in Python).

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "user_message": {
      "user_message": {
        "user_message_type": "user_query",
        "content": "Create an automation that adds 1 and 1 and outputs the result"
      }
    }
  }' \
  "${BASE_URL}/api/v1/${THREAD_NAME}:sendMessage"
```

### Step 4: Invoke the automation

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"stage": "AUTOMATION_STAGE_DRAFT", "inputs": {}}' \
  "${BASE_URL}/api/v1/organizations/${KOGNITOS_ORGANIZATION_ID}/workspaces/${KOGNITOS_WORKSPACE_ID}/automations/${AUTOMATION_ID}:invoke"
```

### Step 5: Poll run status

Look for `state.completed.outputs` in the response.

```bash
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${BASE_URL}/api/v1/${RUN_ID}"
```
