# Curl Examples

Use this reference for quick API exploration, auth validation, and debugging.

## Prerequisites

Set these environment variables (or source `.env.local`):

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `KOGNITOS_TOKEN` | Yes | — | PAT (`kgn_pat_` prefix) |
| `KOGNITOS_BASE_URL` | Yes | — | API base URL (e.g. `https://app.us-1.kognitos.com`) |
| `KOGNITOS_ORGANIZATION_ID` | For most calls | — | Organization ID |
| `KOGNITOS_WORKSPACE_ID` | For most calls | — | Workspace ID |

## Base URL

`KOGNITOS_BASE_URL` is `https://app.us-1.kognitos.com` for US customers. EU customers swap `us-1` for `eu-1`. Use it directly in snippets as `${KOGNITOS_BASE_URL}`.

## Discovery

### List organizations

```bash
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${KOGNITOS_BASE_URL}/api/v1/me/organizations?page_size=50"
```

### List workspaces in an org

```bash
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${KOGNITOS_ORGANIZATION_ID}/workspaces?page_size=50"
```

## Automations

### List automations

```bash
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${KOGNITOS_ORGANIZATION_ID}/workspaces/${KOGNITOS_WORKSPACE_ID}/automations?page_size=10"
```

### Get one automation

```bash
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${KOGNITOS_ORGANIZATION_ID}/workspaces/${KOGNITOS_WORKSPACE_ID}/automations/${AUTOMATION_ID}"
```

## Create Automation via the AI Agent (Quill / `quill2`)

See [automation-agent-api.md](automation-agent-api.md) for the full flow, event model, interrupts, and testing. Summary:

### Step 1: Create automation shell (with the Quill2 kind)

`kind: AUTOMATION_KIND_QUILL2` is required for Quill to operate on the automation.

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"display_name": "My Automation", "kind": "AUTOMATION_KIND_QUILL2"}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${KOGNITOS_ORGANIZATION_ID}/workspaces/${KOGNITOS_WORKSPACE_ID}/automations"
```

Capture the automation id from the response `name`.

### Step 2: Create a Quill thread on the automation

Variables come from the URL path — pass only a `title`. Capture the returned `thread_id`.

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"title": "Build my automation"}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${KOGNITOS_ORGANIZATION_ID}/workspaces/${KOGNITOS_WORKSPACE_ID}/automations/${AUTOMATION_ID}/agents/quill2/threads"
```

Define the thread prefix for subsequent calls:

```bash
TBASE="${KOGNITOS_BASE_URL}/api/v1/organizations/${KOGNITOS_ORGANIZATION_ID}/workspaces/${KOGNITOS_WORKSPACE_ID}/automations/${AUTOMATION_ID}/agents/quill2/threads/${THREAD_ID}"
```

### Step 3: Send a message (async)

`POST .../input` is fire-and-forget; it returns `{"ok": true}`. Observe results on the event stream. The message is a single `message` object with `content` (and optional `documents`/`images`) — **not** the legacy double-nested `user_message`.

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"message": {"content": "Build an automation that adds 1 and 1 and outputs the result"}}' \
  "${TBASE}/input"
```

### Step 4: Read the events until the turn ends

Poll the thread until `status.state` is no longer a working state: `THREAD_STATUS_STATE_IDLE` (turn done), `..._AWAITING_ANSWER` / `..._AWAITING_APPROVAL` / `..._AWAITING_TOOL` (you must respond), or `..._FAILED`. Then read the events. Or subscribe to `GET .../stream` (SSE) for live events. The full state table is in [agents-api.md](agents-api.md).

```bash
curl -sS -H "Authorization: Bearer ${KOGNITOS_TOKEN}" "${TBASE}" | jq '.status'
curl -sS -H "Authorization: Bearer ${KOGNITOS_TOKEN}" "${TBASE}/events"
```

Answer an interrupt by posting an `interrupt_reply` back to `/input` (see automation-agent-api.md). Quill validates, tests (if asked), and **autosaves** at the end of the turn.

### Step 5: Invoke a run (stage selects which version)

`stage` chooses the **version**, not a test mode: `AUTOMATION_STAGE_DRAFT` runs the latest draft (test/preview); `AUTOMATION_STAGE_PUBLISHED` runs the latest published version (production). Quill autosaves drafts but never publishes — invoking `PUBLISHED` before publishing returns `FAILED_PRECONDITION`.

```bash
# Invoke the DRAFT (test/preview of the work in progress)
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"stage": "AUTOMATION_STAGE_DRAFT", "inputs": {}}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${KOGNITOS_ORGANIZATION_ID}/workspaces/${KOGNITOS_WORKSPACE_ID}/automations/${AUTOMATION_ID}:invoke"
```

### Step 6: Publish, then run in production

```bash
# Publish the current draft → creates version N.0
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" -d '{}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${KOGNITOS_ORGANIZATION_ID}/workspaces/${KOGNITOS_WORKSPACE_ID}/automations/${AUTOMATION_ID}:publish"

# Run the PUBLISHED version (production)
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"stage": "AUTOMATION_STAGE_PUBLISHED", "inputs": {}}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${KOGNITOS_ORGANIZATION_ID}/workspaces/${KOGNITOS_WORKSPACE_ID}/automations/${AUTOMATION_ID}:invoke"
```

### Step 7: Poll run status

Look for `state.completed.outputs` in the response.

```bash
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${KOGNITOS_BASE_URL}/api/v1/${RUN_ID}"
```

## Agents (Agent Builder)

Every Kognitos agent uses the same thread calls as Quill above. See [agents-api.md](agents-api.md) for the built-in agents, configuring an agent, versions, and export/import.

### List and create agents

```bash
curl -sS -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${KOGNITOS_ORGANIZATION_ID}/workspaces/${KOGNITOS_WORKSPACE_ID}/agents"

curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"name": "Support Triage"}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${KOGNITOS_ORGANIZATION_ID}/workspaces/${KOGNITOS_WORKSPACE_ID}/agents"
# → {"id": "support-triage", "name": "Support Triage", "version": "1"}
```

### Talk to an agent

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"title": "First chat"}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${KOGNITOS_ORGANIZATION_ID}/workspaces/${KOGNITOS_WORKSPACE_ID}/agents/${AGENT_ID}/threads"

TBASE="${KOGNITOS_BASE_URL}/api/v1/organizations/${KOGNITOS_ORGANIZATION_ID}/workspaces/${KOGNITOS_WORKSPACE_ID}/agents/${AGENT_ID}/threads/${THREAD_ID}"

curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"message": {"content": "Hello"}}' \
  "${TBASE}/input"

# Poll until status.state is THREAD_STATUS_STATE_IDLE (or a waiting/failed state), then read the reply
curl -sS -H "Authorization: Bearer ${KOGNITOS_TOKEN}" "${TBASE}" | jq '.status'
curl -sS -H "Authorization: Bearer ${KOGNITOS_TOKEN}" "${TBASE}/events" \
  | jq -r '[.events[] | .output_text.text // empty] | join("")'
```

The `jq` join prints every reply on the thread; slice the events after your last `input_text` for just the latest one.
