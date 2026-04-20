# Automation Agent API

Use this reference when you need to create or refine automations programmatically through the Kognitos AI agent.

## Do not script this end-to-end

This is a **conversational API**, not a pipeline. Treat each step as `send → observe → decide → send`, running one request at a time and reading the response before issuing the next. Do not wrap the flow in a single script that blasts all the calls through and parses the end.

Concretely:

- The agent may return a `thread_interrupt` asking for clarification, a connection, or a credential. A script that doesn't branch on the terminal object shape will hang or reply with the wrong message type.
- The same prompt can produce different code across runs. Inspect the `artifact` and `agent_message` output before moving on; don't assume the first artifact is the final one.
- Multi-turn refinement is the norm, not the exception. Expect to send follow-up messages on the same thread after reading the previous turn's output.
- Running a saved automation is a separate mechanism (`POST .../automations/{id}:invoke` against the automation resource, not a thread message). Don't conflate "ask the agent to run it" with "invoke the automation."

If you're tempted to write a wrapper script that does `create_shell → create_thread → send_message → wait_for_completion → invoke → poll → print`, stop. Drive the conversation; don't automate it.

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

### 2. Find or create the Quill thread

Before creating, list threads filtered by the automation — if one already exists, reuse it rather than creating a parallel thread. This matches how the web app behaves and keeps the conversation history on one thread.

```bash
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  --get \
  --data-urlencode "page_size=1" \
  --data-urlencode "filter=automation = \"organizations/${ORG}/workspaces/${WS}/automations/${AUTO_ID}\"" \
  "${BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/agents/quill/threads"
```

If the response is empty, create one:

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{\"automation\": \"organizations/${ORG}/workspaces/${WS}/automations/${AUTO_ID}\"}" \
  "${BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/agents/quill/threads"
```

Response includes `name`, the canonical thread path — note the `automations/{auto_id}` segment:
`organizations/{org}/workspaces/{ws}/automations/{auto_id}/agents/quill/threads/{thread_id}`

Capture that whole string as `THREAD_NAME` and use it as the URL prefix for every subsequent thread operation. Do not rebuild the path from parts; the `automations/` segment is required.

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
  "${BASE_URL}/api/v1/${THREAD_NAME}:sendMessage"
```

**Note the double-nested `user_message` structure.** The outer is the thread message envelope; the inner is the user message payload.

The response is a **stream of JSON objects** — concatenated pretty-printed JSON, not line-delimited NDJSON. A naive per-line reader won't parse it; use an incremental decoder (`json.JSONDecoder().raw_decode` in Python, `JSONStream` or equivalent elsewhere). Key message types:

| Field | Meaning |
|-------|---------|
| `user_message` | Echo of your sent message |
| `progress_notification` | Agent thinking/heartbeat |
| `agent_message` | Agent's natural language reply |
| `tool_call_request` | Agent calling an internal tool (execute_code, save_automation, etc.) |
| `artifact` | Generated output (automation code, execution reference) |
| `thread_interrupt` | Agent needs clarification — respond with `interrupt_response` |
| `completion_response` | Terminal message — agent is done |

### 4. Resume a disconnected stream

If your client drops the connection while the most recent message is still in a non-terminal state, resume the stream in place rather than sending a new message:

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{}' \
  "${BASE_URL}/api/v1/${THREAD_NAME}:resumeStream"
```

### 5. Poll for completion (alternative to streaming)

List thread messages after the stream ends:

```bash
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${BASE_URL}/api/v1/${THREAD_NAME}/messages?page_size=50"
```

Look for `completion_response` with `state: "STATE_COMPLETE"`.

## Authoring vs. running — different mechanisms

Once the automation is saved, there are two separate surfaces. Do not confuse them:

| Goal | Mechanism | Endpoint |
|------|-----------|----------|
| Change, refine, or debug the code | Send another message on the Quill thread | `POST .../<THREAD_NAME>:sendMessage` |
| Execute a saved automation and capture outputs | Invoke the automation resource and poll the run | `POST .../automations/{id}:invoke` then `GET .../runs/{run_id}` |

**Do not send a thread message like "please run it"** to get outputs. The agent authors code; it does not produce an auditable run record with `outputs`. The `:invoke` endpoint does. There is also no "draft runs are blocked in the same turn they're saved" restriction — invoke as soon as the `completion_response` arrives.

### 6. Invoke the automation

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"stage": "AUTOMATION_STAGE_DRAFT", "inputs": {}}' \
  "${BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/automations/${AUTO_ID}:invoke"
```

Returns `run_id`.

### 7. Poll the run for results

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
  "${BASE_URL}/api/v1/${THREAD_NAME}:sendMessage"
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
  "${BASE_URL}/api/v1/${THREAD_NAME}:sendMessage"
```

## Other Thread Endpoints

Paths marked `<THREAD_NAME>` expand to the full `automations/{auto_id}/agents/quill/threads/{thread_id}` resource returned by the create-thread response.

| Action | Method | Path |
|--------|--------|------|
| Get thread | GET | `.../<THREAD_NAME>` |
| List threads | GET | `.../workspaces/{ws}/agents/quill/threads` |
| List messages | GET | `.../<THREAD_NAME>/messages` |
| Resume most recent stream | POST | `.../<THREAD_NAME>:resumeStream` |
| Stop thread | POST | `.../<THREAD_NAME>:stop` |
