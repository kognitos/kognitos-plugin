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

### Step 3: Send prompt (response is streaming NDJSON)

Note the double-nested `user_message` structure.

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
  "${BASE_URL}/api/v1/organizations/${KOGNITOS_ORGANIZATION_ID}/workspaces/${KOGNITOS_WORKSPACE_ID}/agents/quill/threads/${THREAD_ID}:sendMessage"
```

### Step 4: Confirm with the user before running

After the automation is created and saved, **ask the user if they want to invoke it**. Do not automatically run. Only proceed if the user confirms.

### Step 5: Invoke the automation

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"stage": "AUTOMATION_STAGE_DRAFT", "inputs": {}}' \
  "${BASE_URL}/api/v1/organizations/${KOGNITOS_ORGANIZATION_ID}/workspaces/${KOGNITOS_WORKSPACE_ID}/automations/${AUTOMATION_ID}:invoke"
```

### Step 6: Poll run status

Look for `state.completed.outputs` in the response.

```bash
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${BASE_URL}/api/v1/${RUN_ID}"
```

## Runs

See [runs-api.md](runs-api.md) for the full reference.

### List runs for an automation

```bash
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${BASE_URL}/api/v1/organizations/${KOGNITOS_ORGANIZATION_ID}/workspaces/${KOGNITOS_WORKSPACE_ID}/automations/${AUTOMATION_ID}/runs?page_size=20"
```

### List run events (step-by-step log)

```bash
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${BASE_URL}/api/v1/organizations/${KOGNITOS_ORGANIZATION_ID}/workspaces/${KOGNITOS_WORKSPACE_ID}/automations/${AUTOMATION_ID}/runs/${RUN_ID}/events?page_size=100"
```

### Pause a run

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"reason": "Investigating unexpected behavior"}' \
  "${BASE_URL}/api/v1/organizations/${KOGNITOS_ORGANIZATION_ID}/workspaces/${KOGNITOS_WORKSPACE_ID}/automations/${AUTOMATION_ID}/runs/${RUN_ID}:pause"
```

## Exceptions

See [exceptions-api.md](exceptions-api.md) for the full reference.

### List pending exceptions

```bash
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${BASE_URL}/api/v1/organizations/${KOGNITOS_ORGANIZATION_ID}/workspaces/${KOGNITOS_WORKSPACE_ID}/exceptions?filter=state%20%3D%20%22PENDING%22&page_size=20"
```

### Count exceptions by group

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"count_by": "group"}' \
  "${BASE_URL}/api/v1/organizations/${KOGNITOS_ORGANIZATION_ID}/workspaces/${KOGNITOS_WORKSPACE_ID}/exceptions:count"
```

### Reply to the exception resolution agent

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"message": "Use the backup email address", "exception_id": "${EXCEPTION_ID}"}' \
  "${BASE_URL}/api/v1/organizations/${KOGNITOS_ORGANIZATION_ID}/workspaces/${KOGNITOS_WORKSPACE_ID}/automations/${AUTOMATION_ID}/runs/${RUN_ID}/exceptions:reply"
```

## Scheduling

See [scheduling-api.md](scheduling-api.md) for the full reference.

### Get schedule

```bash
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${BASE_URL}/api/v1/organizations/${KOGNITOS_ORGANIZATION_ID}/workspaces/${KOGNITOS_WORKSPACE_ID}/automations/${AUTOMATION_ID}/schedule"
```

### Create a daily schedule

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "start": {
        "start_date": {"year": 2026, "month": 4, "day": 14},
        "time": {"hours": 9, "minutes": 0},
        "time_zone": "America/New_York"
      },
      "repeat_interval": {"unit": "FREQUENCY_UNIT_DAY", "interval": 1}
    }
  }' \
  "${BASE_URL}/api/v1/organizations/${KOGNITOS_ORGANIZATION_ID}/workspaces/${KOGNITOS_WORKSPACE_ID}/automations/${AUTOMATION_ID}/schedule"
```

## Files

See [files-api.md](files-api.md) for the full reference.

### Upload a file

```bash
CONTENT_B64=$(base64 < input.csv)
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{\"filename\": \"input.csv\", \"content_base64\": \"${CONTENT_B64}\"}" \
  "${BASE_URL}/api/v1/organizations/${KOGNITOS_ORGANIZATION_ID}/files:upload"
```

## Books (Integrations)

See [books-api.md](books-api.md) for the full reference.

### Search for integrations

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"query": "Salesforce"}' \
  "${BASE_URL}/api/v1/organizations/${KOGNITOS_ORGANIZATION_ID}/workspaces/${KOGNITOS_WORKSPACE_ID}/books:search"
```

### Search for procedures (actions)

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"query": "send email"}' \
  "${BASE_URL}/api/v1/organizations/${KOGNITOS_ORGANIZATION_ID}/workspaces/${KOGNITOS_WORKSPACE_ID}/procedures:search"
```

## Analytics

See [analytics-api.md](analytics-api.md) for the full reference.

### Organization insights

```bash
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${BASE_URL}/api/v1/organizations/${KOGNITOS_ORGANIZATION_ID}/analytics/insights?start_date=2026-04-01T00:00:00Z&end_date=2026-04-11T23:59:59Z"
```

### Daily run statistics

```bash
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${BASE_URL}/api/v1/organizations/${KOGNITOS_ORGANIZATION_ID}/workspaces/${KOGNITOS_WORKSPACE_ID}/analytics/run_stats?daily=true&start_date=2026-04-01T00:00:00Z&end_date=2026-04-11T23:59:59Z"
```
