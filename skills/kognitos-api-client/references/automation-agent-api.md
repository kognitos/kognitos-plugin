# Automation Agent API

Use this reference when you need to create or refine automations programmatically through the Kognitos AI agent.

## Overview

Automation code cannot be set directly via REST. The `english_code` and `code` fields on the automation resource are read-only through PATCH — they are authored by the AI agent through a conversational thread.

In URL paths, the agent ID is the literal string `quill`.

## Base URL

```
https://app.<region>-<az>[.<env>].kognitos.com
```

| Env | Example |
|-----|---------|
| prod | `https://app.us-1.kognitos.com` |
| dev | `https://app.us-1.dev.kognitos.com` |

## End-to-End Flow

### 1. Create an automation shell

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"display_name": "My Automation"}' \
  "${BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/automations"
```

Response includes `name` with the automation ID embedded:
`organizations/{org}/workspaces/{ws}/automations/{automation_id}`

### 2. Create a thread linked to the automation

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{\"automation\": \"organizations/${ORG}/workspaces/${WS}/automations/${AUTO_ID}\"}" \
  "${BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/agents/quill/threads"
```

Response includes `name` with the thread ID:
`organizations/{org}/workspaces/{ws}/agents/quill/threads/{thread_id}`

### 3. Send a prompt to the agent

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
  "${BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/agents/quill/threads/${THREAD_ID}:sendMessage"
```

**Note the double-nested `user_message` structure.** The outer is the thread message envelope; the inner is the user message payload.

The response is **streaming NDJSON** — one JSON object per line. Key message types:

| Field | Meaning |
|-------|---------|
| `user_message` | Echo of your sent message |
| `progress_notification` | Agent thinking/heartbeat |
| `agent_message` | Agent's natural language reply |
| `tool_call_request` | Agent calling an internal tool (execute_code, save_automation, etc.) |
| `artifact` | Generated output (automation code, execution reference) |
| `thread_interrupt` | Agent needs clarification — respond with `interrupt_response` |
| `completion_response` | Terminal message — agent is done |

### 4. Poll for completion (alternative to streaming)

List thread messages after the stream ends:

```bash
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/agents/quill/threads/${THREAD_ID}/messages?page_size=50"
```

Look for `completion_response` with `state: "STATE_COMPLETE"`.

### 5. Invoke the automation

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"stage": "AUTOMATION_STAGE_DRAFT", "inputs": {}}' \
  "${BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/automations/${AUTO_ID}:invoke"
```

Returns `run_id`.

### 6. Poll the run for results

```bash
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${BASE_URL}/api/v1/${RUN_ID}"
```

The `state` field is a one-of:

| State | Meaning |
|-------|---------|
| `pending` | Queued |
| `executing` | Running |
| `completed` | Done — `outputs` map contains results |
| `failed` | Error — `description` has details |
| `awaiting_guidance` | Needs user input (exception) |
| `stopped` | Paused |

Outputs are keyed by name with `commonV1Value` types (e.g. `{"number": {"lo": 2, ...}}` or `{"text": "hello"}`).

## Refining an Automation

Send follow-up messages to the same thread to iterate:

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "user_message": {
      "user_message": {
        "user_message_type": "user_query",
        "content": "Change it to accept two input numbers instead of hardcoding 1 and 1"
      }
    }
  }' \
  "${BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/agents/quill/threads/${THREAD_ID}:sendMessage"
```

## Responding to Interrupts

If the agent returns a `thread_interrupt` with questions, respond with:

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "user_message": {
      "user_message": {
        "user_message_type": "interrupt_response",
        "content": "Yes, use the default settings",
        "interrupt_id": "<interrupt_id_from_response>"
      }
    }
  }' \
  "${BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/agents/quill/threads/${THREAD_ID}:sendMessage"
```

## Other Thread Endpoints

| Action | Method | Path |
|--------|--------|------|
| Get thread | GET | `.../agents/quill/threads/{thread_id}` |
| List threads | GET | `.../agents/quill/threads` |
| List messages | GET | `.../agents/quill/threads/{thread_id}/messages` |
| Stop thread | POST | `.../agents/quill/threads/{thread_id}:stop` |
