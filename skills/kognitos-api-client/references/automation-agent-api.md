# Automation Agent API (Quill)

Use this reference when you need to create, refine, or test automations programmatically through the Kognitos AI agent.

Quill is the Kognitos agent that **builds, tests, and maintains** automations. You drive it through a conversational thread: you send messages, it streams back events (its reasoning, tool calls, questions, and results), and it produces a validated automation. In URL paths the agent id is the literal string **`quill2`**.

## Do not script this end-to-end

This is a **conversational API**, not a pipeline. Treat each turn as `send → observe → decide → send`: send one message, read the event stream until the turn ends, then decide the next message based on what you saw. Do not wrap the whole flow in a single script that fires every call and parses only the end.

Concretely:

- A turn can end with an **interrupt** (the agent asks you to pick an option or answer a question) or a **remote tool call** (e.g. choosing/creating a connection). A script that doesn't branch on the terminal event will hang or reply with the wrong shape.
- The agent is **non-deterministic** — the same prompt can produce different code, different questions, or a different number of turns. Inspect the events before moving on.
- **Multi-turn refinement is the norm.** Expect to send follow-up messages on the same thread after reading the previous turn's output.
- Quill **tests automations itself** during the conversation and **autosaves a new draft version** at the end of a turn — it never publishes. Running the automation (invoking a draft to preview, or publishing and running in production) is a separate mechanism (the automations `:invoke`/`:publish` endpoints). Don't conflate "ask Quill to test it" with "invoke/publish the automation." See [Automation lifecycle](#automation-lifecycle-drafts-publishing-and-stages).

If you're tempted to write a wrapper that does `create_shell → create_thread → send → wait → invoke → poll → print`, stop. Drive the conversation; don't automate it.

## What Quill produces

Quill's deliverable is an **automation**: internal code (the SPy language) plus an **AOP** (Automation Operating Procedure) — a business-language Standard Operating Procedure. The AOP is what the user sees; the code is an internal detail.

On the automation resource (public REST), this surfaces as:

- `english_code` — the AOP (markdown). **Read-only** via REST; authored by Quill.
- `code` — reserved; empty for Quill-authored automations (the SPy lives in the agent's artifacts).
- `input_specs`, `connections`, `display_name`, `description`, `version` — populated by Quill as it builds.
- `kind` — **`AUTOMATION_KIND_QUILL2`** (see below).

You cannot set automation code via `PATCH`. Code is authored only through the conversational thread.

## Base URL, auth, and permissions

- `KOGNITOS_BASE_URL` is `https://app.us-1.kognitos.com` for US customers; EU customers swap `us-1` for `eu-1`. Dev environments look like `https://app.us-1.dev.kognitos.com`.
- Auth is a PAT: `Authorization: Bearer ${KOGNITOS_TOKEN}` (`kgn_pat_` prefix). The token identifies the user, not an org/workspace.
- Use the **automation-scoped path** for all thread calls (see below). The workspace-scoped agent path (`/api/v1/agents/quill2/...`) is **not** authorized for PAT clients and returns `403`.

## Path structure

Threads are scoped to an automation. Every thread call is prefixed with:

```text
${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/automations/${AUTO_ID}/agents/quill2/threads/${THREAD_ID}
```

Capture that prefix once as `${TBASE}` after creating the thread, and append the sub-resource (`/input`, `/events`, `/stream`, etc.) for each call.

---

## End-to-End Flow

### 1. Create an automation shell — with the Quill2 kind

The automation must be created with `kind: AUTOMATION_KIND_QUILL2`. This is **required** for Quill to operate on it.

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"display_name": "My Automation", "kind": "AUTOMATION_KIND_QUILL2"}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/automations"
```

The response `name` embeds the automation id:
`organizations/{org}/workspaces/{ws}/automations/{automation_id}`. Capture the last segment as `${AUTO_ID}`.

### 2. Create the Quill thread

Create a thread under the automation. Variables (`organizationId`, `workspaceId`, `automationId`) are taken from the **URL path** — you only pass a `title`.

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"title": "Build my automation"}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/automations/${AUTO_ID}/agents/quill2/threads"
```

Response includes `thread_id` and the resolved `variables`. Capture `thread_id` as `${THREAD_ID}` and build the prefix:

```bash
TBASE="${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/automations/${AUTO_ID}/agents/quill2/threads/${THREAD_ID}"
```

To reuse an existing conversation, list threads for the automation and reuse one instead of creating a parallel thread:

```bash
curl -sS -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/automations/${AUTO_ID}/agents/quill2/threads"
```

### 3. Send a message (async)

Send the user's request with `POST .../input`. This is **fire-and-forget**: it returns `{"ok": true}` immediately and the agent processes the turn in the background. You observe the result on the event stream (step 4).

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "content": "Build an automation that takes an invoice PDF and extracts the invoice number, date, vendor, and total amount due."
    }
  }' \
  "${TBASE}/input"
```

The message envelope supports more than text:

```json
{
  "message": {
    "content": "Test it with this invoice.",
    "documents": [{ "uri": "uploads://Invoice.pdf", "filename": "Invoice.pdf" }],
    "images":    [{ "uri": "uploads://screenshot.png" }]
  }
}
```

`uploads://` URIs come from the upload endpoint — see [Attaching files](#attaching-files).

> The message shape is a single `message` object with a `content` string. This is **not** the legacy double-nested `user_message` / `user_message_type` structure.

### 4. Observe the event stream

A turn emits a stream of **events**. You have two ways to read them:

**(a) Poll `GET .../events`** — returns the full ordered event list each call. Simplest and most robust for scripted/agent clients. Poll every few seconds until the **last** event is terminal (step 5).

```bash
curl -sS -H "Authorization: Bearer ${KOGNITOS_TOKEN}" "${TBASE}/events"
# → {"events": [ {event}, {event}, ... ]}
```

**(b) Subscribe to `GET .../stream` (SSE)** — a live `text/event-stream` of events as they happen. Best for real-time UIs. Each SSE message has an `id:` line and a `data:` line with one JSON event. Resume after a dropped connection with the `Last-Event-ID` header. A real client must **hold the connection open** for the whole turn; a short-lived process will miss events (poll `/events` instead).

```bash
curl -sS -N -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Accept: text/event-stream" \
  "${TBASE}/stream"
```

Each event is a flat JSON object with an `id` plus exactly one payload field. Key payload types:

| Field | Meaning |
|-------|---------|
| `input_text` | Echo of a user message |
| `reasoning_text` | The agent's extended thinking |
| `output_text` | The agent's natural-language reply (streamed in deltas — concatenate by `id`) |
| `tool_call_start` | The agent invoked a tool (`name`, `is_remote`, `id` — this `id` is the `tool_call_id` you pass when replying via `/tool-results` or `tool_approval_reply`) |
| `tool_call_argument` | One streamed argument for the current tool call |
| `tool_result` | Result of a tool call (`success`, `content`) |
| `interrupt` | The agent needs an answer — **pauses the turn** (see step 6) |
| `interrupt_answer` | Your recorded answer to an interrupt |
| `tool_approval_requested` | The agent needs approval to run a tool — pauses the turn |
| `sleep_requested` | The agent is sleeping (e.g. between run polls) — informational |
| `generation_complete` | A model generation finished |
| `generation_failed` | The turn errored (`message`, `kind`, `retryable`) |

Tool names you'll see Quill use internally (you don't call these — you only observe them): `artifact_list`, `artifact_read`, `artifact_write`, `search_apps`, `search_procedures`, `prepare_code_manifest` (validation), `create_run` / `get_run` (self-testing), `save_automation`, `request_connection`. Treat these as internal detail — never surface tool names, code, or connection IDs to a business user.

### 5. Detect when the turn is done

The agent loops internally (think → call tools → read results → think again), so you will see **multiple `generation_complete` events within a single turn**. The turn is finished when the **latest** event is `generation_complete` **and** there is no pending `interrupt`, `tool_approval_requested`, or unfulfilled remote `tool_call_start`.

If the latest event is `generation_failed`, the turn errored — read `message`/`kind`/`retryable`.

A practical poll loop: fetch `/events` and look at the latest event. Stop when it's `interrupt` or `tool_approval_requested` (you must respond), `generation_failed` (error), or `generation_complete` **with nothing pending** — i.e. no unanswered `interrupt`/`tool_approval_requested` and no unfulfilled remote `tool_call_start` (the turn is done, per the rule above). Because `generation_complete` also fires mid-turn, don't treat a bare `generation_complete` as done without that check.

> **One active generation per thread.** A turn may span several internal generations (you'll see multiple `generation_complete` events as the agent thinks, calls tools, and continues). Do not send the next message until the agent is actually idle and waiting on you — posting to `/input` while a generation is still active returns `412 FAILED_PRECONDITION` (`generation already active for thread`). The exceptions are the inputs the agent is explicitly waiting for: an `interrupt_reply`, a `tool_approval_reply`, or a `/tool-results` for a pending remote tool call.

### 6. Respond to interrupts

When the agent asks a question, it emits an `interrupt` event and pauses:

```json
{
  "id": "377",
  "interrupt": {
    "interrupt_id": "toolu_...",
    "questions": [{
      "id": "email_app",
      "question": "Which email app would you like to use?",
      "header": "Email App",
      "options": [
        { "label": "Gmail (Recommended)", "description": "Send via a connected Google account" },
        { "label": "Outlook",             "description": "Send via Microsoft / Office 365" }
      ],
      "multi_select": false
    }]
  }
}
```

Reply on the **same thread** via `/input` with an `interrupt_reply`. `selected` carries the chosen option **label(s)** (an array — multiple only when `multi_select` is true), keyed by `question_id`. Pass the option's `label` **verbatim**, including any suffix like `(Recommended)` — it's the label string that's matched, not the question/option `id`:

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "interrupt_reply": {
      "interrupt_id": "toolu_...",
      "answers": [
        { "question_id": "email_app", "selected": ["Gmail (Recommended)"] }
      ]
    }
  }' \
  "${TBASE}/input"
```

The agent records an `interrupt_answer` event and resumes. Sending a normal `message` while an interrupt is pending records an empty answer and redirects the agent with your new message instead.

#### Tool approvals (rare)

A `tool_approval_requested` event pauses the turn until you approve or deny. This is **rare** — only entity-discovery activation requires approval, so most clients never see one. Reply on the same thread via `/input` with a `tool_approval_reply` (`tool_call_id` is the `id` from the `tool_call_start`; `reason` is used only on denial):

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"tool_approval_reply": {"tool_call_id": "<id from tool_call_start>", "approved": true}}' \
  "${TBASE}/input"
```

### 7. Remote tool calls (e.g. choosing a connection)

Some tools are **remote** (`"is_remote": true` on `tool_call_start`) — most notably `request_connection`, which asks the user to pick or create a connection for an app the automation needs. The turn pauses until the result is provided. In the web UI this is fulfilled by a connection picker; the result is the chosen **connection id**.

A headless client fulfils it in two steps. First, ensure a connection exists for the requested `appName`/`appVersion` (the `request_connection` arguments name both). If none exists, create one — standalone integrations need no OAuth, so an empty body returns a usable connection id (see [books-api.md](books-api.md)):

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" -d '{}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/books/${APP_NAME}/${APP_VERSION}/connections"
# → { "book_connection_descriptor": { "connection_id": "<connection-id>", ... } }
```

Then post the connection id back as the tool result. The `tool_call_id` is the `id` field from the `tool_call_start` event you're fulfilling:

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"tool_call_id": "<the id from tool_call_start>", "content": {"string_value": "<connection-id>"}, "success": true}' \
  "${TBASE}/tool-results"
```

The agent resumes immediately with that connection. It will not save an automation that depends on an unresolved connection. (Apps requiring OAuth also need an `:authorize` step — see [books-api.md](books-api.md).)

---

## Attaching files

To give Quill a document (e.g. a sample invoice to design around or to test with), upload it to the thread, then reference the returned `uploads://` URI in `message.documents`:

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -F "file=@./Invoice.pdf;type=application/pdf" \
  "${TBASE}/uploads"
# → {"uri":"uploads://Invoice.pdf","mime_type":"application/pdf","size":19518,"filename":"Invoice.pdf"}
```

Files inform the automation's design; they are example inputs, not data for the agent to process directly.

---

## How Quill tests automations (no separate orchestration)

Quill **runs and tests the automation itself** as part of the conversation. When you ask it to test (or after a build, when it wants to verify), it:

1. Calls `create_run` with a draft run of the staged automation and the `inputs` for `main()` (e.g. an uploaded file). Test runs use `INVOCATION_SOURCE_TEST` and run with **exception handling disabled** — failures surface directly so Quill can diagnose them itself. There is no separate exception-resolution agent in this loop.
2. Polls `get_run` until the run reaches a terminal state, **sleeping between polls** (you'll see `sleep_requested` events).
3. Reports the outcome to you in business language (e.g. a table of extracted fields).

You don't orchestrate any of this — you just ask, observe the events, and read the agent's summary. To test, make sure Quill has values for every `main()` input (upload files and/or state values in your message); Quill will ask (via an interrupt) if something is missing.

### Have it verify behavior, not just build

Quill produces more reliable automations when you have it **run** the work against real inputs and the actual connected apps, rather than building and stopping. The value is in catching two things its build-time validation can't:

- **Logical correctness** — run it on realistic inputs and confirm the result is actually right (the intended branch is taken, fields map to the right places, totals/derived values come out correct). This surfaces logic inconsistencies that pass validation but produce the wrong answer.
- **Real app behavior** — exercising the live procedures reveals where an app behaves differently than the code assumed (a field that isn't returned, a different response shape), which Quill can then fix against ground truth instead of a guess.

Supply the inputs (or sample files) so Quill can run it. Quill drives its own build → test → diagnose → fix loop from there.

This is about confirming the automation does the right thing — not about hardening it against malformed input. Trust Quill's judgment on how the automation should handle the data; your job is to give it realistic cases to run.

**Mind mutating procedures.** Each test is a *real run* — it triggers real app procedures and costs execution time. For automations that call **mutating** procedures (`isMutation: true` — e.g. sending email, creating records), keep test runs deliberate and minimal; Quill confirms before testing a mutating automation.

---

## Automation lifecycle: drafts, publishing, and stages

An automation is versioned `major.minor`:

- **Create** → `0.1`. Every edit to the working copy bumps the **minor** (`0.1 → 0.2 → 0.3`). This working copy is the **draft**. `major == 0` means it has **never been published**.
- **Publish** is a separate, explicit action that bumps the **major** and resets minor to 0 (`0.3 → 1.0`), records `published_at`/`published_by`, and produces the **published** version. A version with `minor == 0` is a published version.
- After publishing, more edits bump minor again (`1.0 → 1.1`), and the next publish makes `2.0`. So an automation can have both a **latest draft** and a **latest published** version, and they can differ.

**Quill only works on the draft.** Its autosaves create new draft minor versions — **Quill never publishes**. Publishing is an explicit, separate step you (or a UI/operator) take when the draft is ready:

```bash
# Optional: check the draft is publishable first
curl -sS -X POST -H "Authorization: Bearer ${KOGNITOS_TOKEN}" -H "Content-Type: application/json" -d '{}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/automations/${AUTO_ID}:validatePublish"

# Publish the current draft → creates version N.0
curl -sS -X POST -H "Authorization: Bearer ${KOGNITOS_TOKEN}" -H "Content-Type: application/json" -d '{}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/automations/${AUTO_ID}:publish"
```

> Quill **autosaves** at the end of a turn once work has settled and validated (a new draft minor version; earlier versions remain available). You don't issue a save call or grant permission — but Quill won't save a state that fails validation or a turn where nothing changed. Saving ≠ publishing.

## Running an automation — the `:invoke` API and stages

`POST .../automations/{id}:invoke` runs an automation and returns `{run_id}`; poll the run with `GET .../{run_id}`. The `stage` field selects **which version** runs — it is **not** a "test mode" flag:

| `stage` | Runs | Use |
|---------|------|-----|
| `AUTOMATION_STAGE_DRAFT` | the latest **draft** | testing / preview of work in progress |
| `AUTOMATION_STAGE_PUBLISHED` | the latest **published** version | production |

Invoking `PUBLISHED` before the automation has ever been published returns `FAILED_PRECONDITION` ("Automation not published"). Two related surfaces, not to be confused:

| Goal | Mechanism |
|------|-----------|
| Change / refine / debug / have Quill **test** the draft | Send a message on the Quill thread (`POST ${TBASE}/input`) — Quill drives `create_run` itself |
| **Invoke the draft yourself** (test/preview) | `:invoke` with `AUTOMATION_STAGE_DRAFT` |
| **Run in production** | **Publish first**, then `:invoke` with `AUTOMATION_STAGE_PUBLISHED` (or a schedule/trigger) |

```bash
# Invoke the DRAFT (returns {"run_id": "...full run resource name..."})
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"stage": "AUTOMATION_STAGE_DRAFT", "inputs": {}}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/automations/${AUTO_ID}:invoke"

# Poll the run by its resource name
curl -sS -H "Authorization: Bearer ${KOGNITOS_TOKEN}" "${KOGNITOS_BASE_URL}/api/v1/${RUN_ID}"
```

The run `state` is a one-of: `pending`, `executing`, `stopping`, `stopped`, `completed` (outputs in `state.completed.outputs`), `failed` (`id`/`description`/`location`), `awaiting_guidance` (`exception`/`description`/`location`), `archived`. Outputs are keyed by name with `commonV1Value` types, e.g. `{"text": "INV-112233"}` or `{"number": {"lo": 114800, "mid": 0, "hi": 0, "flags": 0}}`. **File** outputs are returned as a `bishop://<file-id>` reference; download the bytes from the files API (`GET .../files/<file-id>:download` — the `:download` verb, not the bare resource). See [runs-api.md](runs-api.md) and [files-api.md](files-api.md).

### `invocation_source` — who triggered the run

Each run records `invocation_details.invocation_source`:

| Value | Set when |
|-------|----------|
| `INVOCATION_SOURCE_TEST` | Quill triggered the run to test the **draft** (its `create_run`) |
| `INVOCATION_SOURCE_MANUAL` | A user invoked via the `:invoke` API — including PAT-authenticated calls (the PAT resolves to a user; `user_id` is recorded) |
| `INVOCATION_SOURCE_SCHEDULE` | A schedule fired the run (typically a published automation) |
| `INVOCATION_SOURCE_TRIGGER` | An event/trigger fired the run |

(`INVOCATION_SOURCE_PAT` exists in the enum but the standard `:invoke` records `MANUAL`.)

## Exception handling: draft (Quill) vs published (Astral)

How a run *failure* is handled depends on the stage:

- **Draft runs have no Astral.** Draft-stage runs set `disable_exception_handling = true` — this is true for **both** Quill's `TEST` runs **and** your own `MANUAL` draft `:invoke`. On failure the run parks in `awaiting_guidance` with an **empty `exception`** and a human-readable `description` (the traceback / missing-input message) plus a `location`. No exception resource is created.
- **Published runs are managed by Astral.** Published-stage runs always use standard Astral exception handling (the `disable_exception_handling` flag does not apply). A failure creates a real `Exception` resource and drives the guidance-center resolution flow (assign / reply / skip / patch / retry — see [exceptions-api.md](exceptions-api.md)).

**You can invoke a draft yourself and ask Quill to debug it.** Beyond "Quill builds and tests," this is a supported workflow: invoke the draft (`AUTOMATION_STAGE_DRAFT`), and because draft runs surface failures inline (no Astral), tell Quill on the thread to monitor and fix that run — give it the run name (or just describe the failure) and it will read the run's `description`/`location`, diagnose, edit the code, and re-test.

---

## Refining an automation

Send follow-up messages on the same thread to iterate. Each accepted change is validated and (when it settles) autosaved as a new version.

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"message": {"content": "Also output the line items as a table."}}' \
  "${TBASE}/input"
```

---

## Grimoire artifacts (advanced)

Internally Quill stores the automation as artifacts on the thread (`grimoire://`): `aop.spy` (SPy code), `aop.md` (the user-facing AOP), `connections.json`, `metadata.json`, `code_manifest.json`, and `context.md` (private agent notes). You can read these via the thread artifacts API, but for most integrations you only need the automation resource (`english_code` is the AOP) and the conversation.

```bash
# List artifacts on the thread
curl -sS -H "Authorization: Bearer ${KOGNITOS_TOKEN}" "${TBASE}/artifacts"

# Read one artifact's content
curl -sS -H "Authorization: Bearer ${KOGNITOS_TOKEN}" "${TBASE}/artifacts/grimoire://aop.md:content"
```

---

## Other thread endpoints

Paths are relative to `${TBASE}` unless noted.

| Action | Method | Path |
|--------|--------|------|
| Get thread | GET | `${TBASE}` |
| List threads | GET | `.../automations/{auto_id}/agents/quill2/threads` |
| List events | GET | `${TBASE}/events` |
| Send message (async) | POST | `${TBASE}/input` |
| Live event stream (SSE) | GET | `${TBASE}/stream` |
| Fulfil a remote tool call | POST | `${TBASE}/tool-results` |
| Stop the current turn | POST | `${TBASE}:stop` |
| Wake a sleeping thread | POST | `${TBASE}:wake` |
| Fork the thread | POST | `${TBASE}:fork` |
| Compact history | POST | `${TBASE}:compact` |
| Upload a file | POST | `${TBASE}/uploads` (multipart) |
| Read context (memory blocks) | GET | `${TBASE}/context` |
| Submit feedback | POST | `${TBASE}/feedback` |
| Thread artifacts | GET/PUT/DELETE | `${TBASE}/artifacts[...]` |

> **Note on the sync endpoint.** Rain also defines `POST ${TBASE}/events` (a synchronous "send message and stream this turn's events on the response") but it is **not usable** on the PAT/automation-scoped path — it fails to resolve the agent. Use async `POST /input` plus `/stream` or `/events` polling instead.
