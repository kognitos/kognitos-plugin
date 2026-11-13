# Agents API

Use this reference when you need to talk to a Kognitos AI agent over the API, or to create and manage your own agents with the Agent Builder.

## What agents are on Kognitos

Every Kognitos agent runs on the same agent runtime and speaks the same **thread protocol**: you open a thread (a conversation), post messages to it, and read back a stream of events until the agent finishes its turn. What differs between agents is where the thread lives (its scope) and what the agent does.

There are two kinds of agents:

- **Built-in agents** ship with Kognitos. Each has a fixed id and is attached to a resource: an automation, a run, a connection, or the workspace itself.
- **Workspace agents** are agents you build in the **Agent Builder**. You create them, configure them by conversation, version and tag them, and export or import them between workspaces.

All paths below are relative to:

```text
${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}
```

Auth is a PAT: `Authorization: Bearer ${KOGNITOS_TOKEN}`. The agent endpoints are not in the public OpenAPI spec yet; they are being added. Until they land there, this page and [automation-agent-api.md](automation-agent-api.md) are the reference.

## Built-in agents

| Agent | Id | Thread collection (relative path) | What it does |
|-------|----|-----------------------------------|--------------|
| Automation Builder Agent (Quill) | `quill2` | `/automations/{automation_id}/agents/quill2/threads` | Builds, tests, and maintains one automation. See [automation-agent-api.md](automation-agent-api.md). |
| Step Tuning Agent | `prime` | `/automations/{automation_id}/agents/prime/threads` | Tunes a step of an automation. |
| Workbench Agent | `astral2` | `/automations/{automation_id}/runs/{run_id}/agents/astral2/threads` | Diagnoses what went wrong in a run. |
| Workbench Report Agent | `astral-lite` | `/automations/{automation_id}/runs/{run_id}/agents/astral-lite/threads` | Writes a report about a run. |
| Exception Chat Agent | `hermes` | `/agents/hermes/threads` | The chat in which exceptions are discussed and resolved. |
| Agent Builder Assistant | `smith` | `/agents/smith/threads` | Configures a workspace agent from a plain-language description. See [Building an agent](#building-an-agent-with-the-agent-builder-assistant). |
| Integration Assistant | `shifu` | `/books/{integration}/versions/{version}/connections/{connection_id}/agents/shifu/threads` | Helps set up a connection, for example by filling in a trigger form. Mostly driven by the web UI. |

Notes:

- Use the scope shown. The same agent id under a different scope returns `404` (for example `quill2` only exists under an automation).
- Not every built-in agent exposes every thread endpoint to API keys. For example, `prime` and `shifu` threads have no get or rename.
- Exceptions on published runs have their own API with a resolution flow on top of these agents. Prefer [exceptions-api.md](exceptions-api.md) over driving `hermes` or `astral2` directly.

## Workspace agents (Agent Builder)

### List and read agents

```bash
curl -sS -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/agents?query=support&page_size=20&page=1"
# → {"agents": [{"id", "name", "description", "read_only", "latest_version", "latest_tags",
#                "labels", "abilities", "stats", "has_plan", "created_by", "last_updated_at", ...}],
#    "total_size": 1, "order_by": "id"}

curl -sS -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/agents/${AGENT_ID}"
# → {"id", "name", "description", "version", "tags", "variables", "abilities", "icon", ...}
```

- `query` searches id, name, and description. `page` is 1-based; leave `page_size` unset to get everything in one page.
- `read_only: true` marks a template that ships with the workspace, such as `assistant`. Run your own agents: threads on read-only templates can't be opened from the workspace path (`404`).
- 64-bit numbers (`version`, `latest_version`, `event_count`) are JSON **strings**, for example `"version": "3"`.
- An empty list can come back as `{}` with the array omitted. Default missing arrays to empty.

### Create an agent

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"name": "Support Triage"}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/agents"
# → {"id": "support-triage", "name": "Support Triage", "version": "1"}
```

The id is derived from the name (lowercase, dashed). A new agent starts with a default model and no instructions, tools, or memory, and it already answers messages. Give it a job with the Agent Builder Assistant (below).

### Rename or relabel

`PATCH` only changes the display name and labels. It does not change instructions, tools, or the model; those are configured on a thread. Each `PATCH` saves a new version.

```bash
curl -sS -X PATCH \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"name": "Support Triage v2", "labels": {"values": ["support"]}}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/agents/${AGENT_ID}"
```

Send `labels` to replace the whole label set (an empty `values` clears it). Omit it to leave labels as they are.

### Building an agent with the Agent Builder Assistant

An agent's configuration (instructions, persona, tone, tools, integrations) is edited on a thread of that agent, then deployed as a new version. The **Agent Builder Assistant** (`smith`) does the editing for you:

1. Create the agent (above), then a thread on it. This is the **config thread**: the assistant writes the agent's configuration onto it, and you test the agent by messaging it.

   ```bash
   curl -sS -X POST \
     -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
     -H "Content-Type: application/json" \
     -d '{"title": "Configure Support Triage"}' \
     "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/agents/${AGENT_ID}/threads"
   # → {"thread_id": "<config-thread-id>", "agent_version": "1", "status": {"state": "THREAD_STATUS_STATE_IDLE"}, ...}
   ```

2. Open an assistant thread that targets the agent and its config thread. The organization and workspace come from the path; the two target variables are required.

   ```bash
   curl -sS -X POST \
     -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
     -H "Content-Type: application/json" \
     -d '{"title": "Build Support Triage", "variables": {"targetAgentId": "'"${AGENT_ID}"'", "targetThreadId": "'"${CONFIG_THREAD_ID}"'"}}' \
     "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/agents/smith/threads"
   ```

3. Describe the agent you want on the assistant thread (`POST .../agents/smith/threads/{thread_id}/input`) and follow the [thread protocol](#the-thread-protocol). The assistant reads the current configuration, writes the changes, and may ask questions through interrupts.
4. Test by messaging the **config thread**. It runs the configuration the assistant just wrote.
5. Deploy from the web UI. Deploying saves the configuration as a new agent version. Deploy is not available to API keys (`403`), so an API client can build and test an agent but a person deploys it.

### Versions and tags

Every save creates an immutable, numbered version. A thread is pinned to the version it was created on (`agent_version` on the thread).

| Action | Method | Path | Notes |
|--------|--------|------|-------|
| List versions | GET | `/agents/{agent_id}/versions` | `{"versions": [{"version", "tags", "created_at", "created_by"}]}`, oldest first |
| Get a version | GET | `/agents/{agent_id}/versions/{version}` | Same shape as get agent |
| Restore a version | POST | `/agents/{agent_id}/versions/{version}:restore` | Body `{}`. Copies that version to a **new** head version and returns it |
| Tag a version | POST | `/agents/{agent_id}/versions/{version}:tag` | Body `{"tag": "production"}`. Returns `204` |
| Get the tagged version | GET | `/agents/{agent_id}/tags/{tag}` | `404` once the tag is removed |
| Remove a tag | DELETE | `/agents/{agent_id}/tags/{tag}` | Returns `204` |

### Duplicate, export, import, delete

```bash
# Duplicate (name is optional; default is "Copy of <name>")
curl -sS -X POST -H "Authorization: Bearer ${KOGNITOS_TOKEN}" -H "Content-Type: application/json" \
  -d '{"name": "Support Triage Copy"}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/agents/${AGENT_ID}:duplicate"
# → {"id": "support-triage-copy", "name": "Support Triage Copy"}

# Export as YAML ("kubernetes" is the other format)
curl -sS -X POST -H "Authorization: Bearer ${KOGNITOS_TOKEN}" -H "Content-Type: application/json" \
  -d '{"format": "yaml"}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/agents/${AGENT_ID}:export"
# → {"data": "<base64 YAML>", "filename": "support-triage.yaml", "content_type": "application/x-yaml"}

# Import (data is base64 of the exported file)
curl -sS -X POST -H "Authorization: Bearer ${KOGNITOS_TOKEN}" -H "Content-Type: application/json" \
  -d '{"format": "yaml", "data": "<base64 YAML>"}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/agents:import"
# → {"agent_id": "support-triage", "agent_name": "Support Triage", "version": "1"}

# Delete (returns 204)
curl -sS -X DELETE -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/agents/${AGENT_ID}"
```

- The exported file carries the agent's `id`, `name`, and full configuration, including the organization and workspace ids it came from. To import a copy next to the original, change `id` and `name` in the file first.
- Duplicating fails with `ALREADY_EXISTS` if the new name's id is taken.

---

## The thread protocol

Everything in this section applies to every agent above. Set `${TBASE}` to the thread you are working with, for example:

```bash
TBASE="${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/agents/${AGENT_ID}/threads/${THREAD_ID}"
```

### Drive it as a conversation

Agents are non-deterministic and multi-turn. Treat each turn as `send → observe → decide → send`: post one message, wait for the turn to end, read what the agent said or asked, then decide what to send next. A turn can end with a question (interrupt), an approval request, or a remote tool call that you must answer, so a script that fires every call and reads only the end will hang or reply with the wrong shape.

### Create and find threads

```bash
# Create (title, description, and variables are optional)
curl -sS -X POST -H "Authorization: Bearer ${KOGNITOS_TOKEN}" -H "Content-Type: application/json" \
  -d '{"title": "Order lookup"}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/agents/${AGENT_ID}/threads"

# List (most recently active first)
curl -sS -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/agents/${AGENT_ID}/threads"
```

The response is a thread: `thread_id`, `title`, `variables` (organization, workspace, and any ids from the path are filled in for you), `agent_version`, `event_count`, `status`, `status_updated_at`, `created_by`. Reuse an existing thread to continue a conversation instead of starting a parallel one.

### Send a message

`POST ${TBASE}/input` is asynchronous. It returns `{"ok": true}` as soon as the message is accepted, and the agent works in the background.

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"message": {"content": "Summarize the open orders for ACME."}}' \
  "${TBASE}/input"
```

The body holds exactly one of:

| Field | Use |
|-------|-----|
| `message` | A normal message: `{"content": "...", "documents": [{"uri", "filename"}], "images": [{"uri"}]}` |
| `interrupt_reply` | An answer to a question the agent asked (see below) |
| `tool_approval_reply` | Approve or deny a tool call (see below) |

Wait for the turn to end before sending the next `message`. Depending on the agent, a message sent mid-turn is either queued until the current turn ends or rejected with `412 FAILED_PRECONDITION`.

### Know when the turn is done

Poll `GET ${TBASE}` and read `status.state`:

| `status.state` | Meaning | What to do |
|----------------|---------|------------|
| `THREAD_STATUS_STATE_IDLE` | Turn finished; waiting for you | Read the events, then send the next message |
| `THREAD_STATUS_STATE_AWAITING_ANSWER` | The agent asked a question | Send an `interrupt_reply` |
| `THREAD_STATUS_STATE_AWAITING_APPROVAL` | A tool call needs approval | Send a `tool_approval_reply` |
| `THREAD_STATUS_STATE_AWAITING_TOOL` | A remote tool call needs a result (`status.remote_count` open calls) | Post to `/tool-results` |
| `THREAD_STATUS_STATE_FAILED` | The turn failed (`status.error_kind`, `status.error_message`) | Report it; retry if it makes sense |
| `THREAD_STATUS_STATE_STOPPED` | The turn was stopped | Send a new message to continue |
| `THINKING`, `RESPONDING`, `EXECUTING_TOOL`, `DELEGATING`, `COMPACTING`, `TRANSFERRING`, `RETRYING` (all `THREAD_STATUS_STATE_`-prefixed) | Working | Keep polling |
| `THREAD_STATUS_STATE_SLEEPING` | The agent paused itself until `status.wake_at` (for example between checks on a run) | Keep polling, or `:wake` it |

Poll every few seconds with an overall timeout, and stop on every waiting or final state, not only `IDLE`. Right after you post, the thread can still show the `IDLE` from the previous turn: treat `IDLE` as done only once `status_updated_at` is later than the time you posted, or once the events show your message followed by output.

### Read the events

```bash
# Full ordered history, every call
curl -sS -H "Authorization: Bearer ${KOGNITOS_TOKEN}" "${TBASE}/events"
# → {"events": [{"id": "1", "recorded_at_ms": "...", "deleted": false, "input_text": {"text": "..."}}, ...]}

# Live server-sent events
curl -sS -N -H "Authorization: Bearer ${KOGNITOS_TOKEN}" -H "Accept: text/event-stream" "${TBASE}/stream"
```

Each event has an increasing `id`, a `recorded_at_ms`, a `deleted` flag, and exactly one payload field:

| Field | Meaning |
|-------|---------|
| `input_text` | Your message, echoed |
| `reasoning_text` | The agent's thinking, streamed in pieces |
| `output_text` | The agent's reply, streamed in pieces. Each piece is its own event; join consecutive `output_text.text` values in order |
| `tool_call_start` | The agent called a tool (`id`, `name`, `is_remote`). `id` is the `tool_call_id` you use when replying |
| `tool_call_argument` | One argument of the current tool call |
| `tool_result` | A tool's result (`tool_call_id`, `success`, `content`) |
| `interrupt` | The agent asked a question and paused |
| `interrupt_answer` | Your recorded answer |
| `tool_approval_requested` | A tool call is waiting for approval |
| `sleep_requested` | The agent paused itself for a while |
| `generation_complete` | One model call finished (`model`, `usage`, `agent_version`). A turn can contain several |
| `generation_failed` | The turn failed (`message`, `kind`, `retryable`) |

`/stream` replays the thread's history from the first event, then stays open for new events. Each message is a `data:` line with one JSON event followed by an `id:` line; lines starting with `:` are keep-alives. Resume after a dropped connection with the `Last-Event-ID` header. Hold the connection for the whole turn, or poll `/events` instead.

Tool calls the agent runs internally are informational: the set of tools can change, so don't depend on their names, and don't show tool names or raw arguments to business users. You only act on **remote** tool calls (`is_remote: true`).

### Answer a question (interrupt)

```json
{"id": "377", "interrupt": {"interrupt_id": "toolu_...", "questions": [{
  "id": "email_app", "question": "Which email app would you like to use?", "header": "Email App",
  "options": [{"label": "Gmail (Recommended)", "description": "..."}, {"label": "Outlook", "description": "..."}],
  "multi_select": false}]}}
```

Reply on the same thread. `selected` holds option **labels**, verbatim (including suffixes such as `(Recommended)`), keyed by the question `id`:

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"interrupt_reply": {"interrupt_id": "toolu_...", "answers": [{"question_id": "email_app", "selected": ["Gmail (Recommended)"]}]}}' \
  "${TBASE}/input"
```

Sending a normal `message` while a question is pending records an empty answer and redirects the agent with your message.

### Approve a tool call

When the agent emits `tool_approval_requested`, approve or deny with the `id` from the matching `tool_call_start` (`reason` is used only on denial):

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"tool_approval_reply": {"tool_call_id": "<id from tool_call_start>", "approved": true}}' \
  "${TBASE}/input"
```

### Return a remote tool result

A remote tool call (`is_remote: true`) is executed by the client, not the agent. The turn waits until you post the result:

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"tool_call_id": "<id from tool_call_start>", "content": {"string_value": "<result>"}, "success": true}' \
  "${TBASE}/tool-results"
```

On failure send `"success": false` with an `"error"` message. Quill's `request_connection` is the common case; see [automation-agent-api.md](automation-agent-api.md).

### Attach files

Upload to the thread, then reference the returned `uploads://` URI in `message.documents` (or `message.images`):

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -F "file=@./Invoice.pdf;type=application/pdf" \
  "${TBASE}/uploads"
# → {"uri": "uploads://Invoice.pdf", "mime_type": "application/pdf", "size": 19518, "filename": "Invoice.pdf"}
```

The agent needs a tool that can read artifacts. Attaching a document to an agent without one is rejected with `400` ("attachments require the artifact_read tool").

### Artifacts

Some agents keep working files on the thread (Quill stores the automation there). Artifact URIs contain `://`, so **percent-encode** them in the path; unencoded URIs are rejected.

```bash
# Read one artifact: {"artifact": {...}, "data": "<base64 content>"}
curl -sS -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${TBASE}/artifacts/grimoire%3A%2F%2Faop.md:content"

# Pending (uncommitted) changes
curl -sS -H "Authorization: Bearer ${KOGNITOS_TOKEN}" "${TBASE}/artifacts:staging"
```

`GET ${TBASE}/artifacts` lists them, but agents whose files live in Kognitos file storage (Quill, the Agent Builder Assistant) may answer the list call with `500` ("list is not yet supported"). Read artifacts by their known URI instead.

### Other thread endpoints

Paths are relative to `${TBASE}` unless noted. Built-in agents may expose a subset.

| Action | Method | Path | Notes |
|--------|--------|------|-------|
| Get thread | GET | `${TBASE}` | Includes `status` |
| Rename | PATCH | `${TBASE}` | `{"title": "...", "description": "..."}` |
| Delete thread | DELETE | `${TBASE}` | `204` |
| Stop the current turn | POST | `${TBASE}:stop` | Body `{}`. `{"stopped": false}` when nothing was running |
| Wake a sleeping thread | POST | `${TBASE}:wake` | Body `{}`. `{"woken": false}` when it wasn't sleeping |
| Fork | POST | `${TBASE}:fork` | `{"title": "..."}`; copies the history into a new thread |
| Compact history | POST | `${TBASE}:compact` | Summarizes older events to free context |
| Context usage | GET | `${TBASE}/context` | Token use per context item and the model's limits |
| Feedback on a reply | POST | `${TBASE}/feedback` | `{"generation_id": "<generation_complete.id>", "feedback_type": "FEEDBACK_TYPE_LIKE"}` (or `FEEDBACK_TYPE_DISLIKE`) |
| Active plan | GET | `${TBASE}/plan/active` | `404` when the thread has no plan |

Avoid `POST ${TBASE}/events` (a synchronous send-and-stream call). Use `POST /input` with `/events` or `/stream`.
