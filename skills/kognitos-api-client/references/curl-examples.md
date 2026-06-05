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

Poll `GET .../events` (full ordered list each call) until the last event is `generation_complete` (turn done), `interrupt` / `tool_approval_requested` (you must respond), or `generation_failed` (error). Or subscribe to `GET .../stream` (SSE) for live events.

```bash
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
