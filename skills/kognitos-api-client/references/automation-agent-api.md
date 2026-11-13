# Automation Agent API (Quill)

Use this reference when you need to create, refine, or test automations programmatically through the Kognitos AI agent.

Quill is the Kognitos agent that **builds, tests, and maintains** automations. You drive it through a conversational thread: you send messages, it streams back events (its reasoning, tool calls, questions, and results), and it produces a validated automation. In URL paths the agent id is the literal string **`quill2`**.

Quill speaks the same thread protocol as every other Kognitos agent. The generic parts (sending messages, reading events, knowing when a turn is done, interrupts, tool approvals, uploads, artifacts, and the other thread endpoints) are in [agents-api.md](agents-api.md). This page covers what is specific to Quill.

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
- `input_specs`, `connections`, `display_name`, `description`, `version` — populated by Quill as it builds. Quill **replaces** a `display_name` you set at create time, so find your automations by id, not by name.
- `kind` — **`AUTOMATION_KIND_QUILL2`** (see below).

You cannot set automation code via `PATCH`. Code is authored only through the conversational thread.

## Base URL, auth, and permissions

- `KOGNITOS_BASE_URL` is the host you sign in to, for example `https://app.us-1.kognitos.com`.
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

The message can also carry `documents` and `images` (see [Attaching files](#attaching-files)). The full input envelope is in [agents-api.md](agents-api.md).

On a new automation, Quill's first turn usually drafts a **blueprint** (a plan in business language, stating its assumptions) and builds nothing. Review it, then reply on the same thread to refine it or to tell Quill to build it. Say so in the first message if you want it to build straight away.

> The message shape is a single `message` object with a `content` string. This is **not** the legacy double-nested `user_message` / `user_message_type` structure.

### 4. Follow the turn

Poll `GET ${TBASE}` until `status.state` leaves the working states, then read `GET ${TBASE}/events` (or hold `GET ${TBASE}/stream` open for live events). The states, the event types, and the rule for telling a finished turn from one that has not started yet are in [agents-api.md](agents-api.md). Quill turns are long: one turn usually contains several `generation_complete` events, and Quill shows `THREAD_STATUS_STATE_SLEEPING` while it waits on a test run. Keep polling through both. When Quill starts a test run the status can show `IDLE` for a moment before `SLEEPING`, so apply the turn-done check in [agents-api.md](agents-api.md) rather than stopping at the first `IDLE`.

As the agent works, you'll observe `tool_call_start` / `tool_call_argument` / `tool_result` events for the tools it runs internally — reading and writing its artifacts, searching for apps and procedures, validating, test-running, saving, and so on. You don't call these; you only observe them, and the exact set may change over time, so don't depend on specific tool names. The one kind you may need to act on is a **remote** tool call (`is_remote: true`) — most notably `request_connection` (see step 6) — which pauses the turn until you return a result. Treat tool calls as internal detail — never surface tool names, code, or connection IDs to a business user.

### 5. Answer questions and approvals

When Quill asks something (for example which email app to use), the thread shows `THREAD_STATUS_STATE_AWAITING_ANSWER` and the events end with an `interrupt`. One interrupt can hold several questions; answer each by its question `id` in one `interrupt_reply`, passing option labels verbatim. Tool approvals are rare but follow the same pattern with a `tool_approval_reply`. Both shapes are in [agents-api.md](agents-api.md).

### 6. Remote tool calls (e.g. choosing a connection)

Some tools are **remote** (`"is_remote": true` on `tool_call_start`) — most notably `request_connection`, which asks the user to pick or create a connection for an app the automation needs. The thread shows `THREAD_STATUS_STATE_AWAITING_TOOL` and the turn pauses until the result is provided. In the web UI this is fulfilled by a connection picker; the result is the chosen **connection id**.

The `tool_call_argument` events after the `tool_call_start` carry `appName`, `appVersion`, and a `reason` you can show the user. Integrations that already have a shared workspace connection (file, CSV, DOCX, PDF and similar) are used directly and don't trigger `request_connection`.

A headless client fulfils it in two steps. First, ensure a connection exists for the requested `appName`/`appVersion`. If none exists, create one — standalone integrations need no OAuth, so an empty body returns a usable connection id (see [books-api.md](books-api.md)):

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

The agent resumes immediately with that connection. It will not save an automation that depends on an unresolved connection.

Apps that need OAuth (Slack, Gmail, Outlook and similar) can't be connected headlessly: creating the connection returns an `authorize_url` for a person to open, and the connection id exists only after they finish (see [books-api.md](books-api.md)). If you can't provide a connection, answer with `"success": false` and an `"error"` saying why. Quill then stops, explains what is missing, and builds once the app is connected.

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

1. Starts a draft test run of the staged automation with the `inputs` for `main()` (e.g. an uploaded file). Test runs use `INVOCATION_SOURCE_TEST` and run with **exception handling disabled** — failures surface directly so Quill can diagnose them itself. There is no separate exception-resolution agent in this loop.
2. Polls the run until it reaches a terminal state, **sleeping between polls** (you'll see `sleep_requested` events).
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

### Fixing or refining a *published* automation — fork a draft first

**Quill only ever writes to the draft.** A freshly published automation can exist with **no draft working copy** (its current `version` is a published one — `minor == 0`, e.g. `7.0` — and there is no later draft). If you open a Quill thread on such an automation and ask it to change anything, Quill builds and tests the fix fine, but its autosave **fails**:

```text
gRPC error: 'Some requested entity was not found' —
"Draft for automation with ID <auto_id> doesn't exist"
```

There is nothing for Quill to save into. Before driving Quill to fix a published automation, **initialize a draft from the published version** with `:fork`:

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" -d '{}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/automations/${AUTO_ID}:fork"
```

This creates a draft whose contents match the latest published version (it's exactly what opening the automation in the Quill editor UI does under the hood). After forking, send the fix request on the thread and Quill's autosave will succeed.

**When to fork (detection rule):** before editing, check whether a draft already exists — query the automation at the **DRAFT** stage (`AUTOMATION_STAGE_DRAFT`). If the only version is published (`minor == 0`) with no later draft, fork first; then drive Quill.

> **Caution — `:fork` resets the draft to match published.** It overwrites the draft working copy with the published version. Only fork when there is **no unsaved draft work** you care about; otherwise forking discards it. If a usable draft already exists, skip the fork and go straight to the thread.

## Running an automation — the `:invoke` API and stages

`POST .../automations/{id}:invoke` runs an automation and returns `{run_id}`; poll the run with `GET .../{run_id}`. The `stage` field selects **which version** runs — it is **not** a "test mode" flag:

| `stage` | Runs | Use |
|---------|------|-----|
| `AUTOMATION_STAGE_DRAFT` | the latest **draft** | testing / preview of work in progress |
| `AUTOMATION_STAGE_PUBLISHED` | the latest **published** version | production |

Invoking `PUBLISHED` before the automation has ever been published returns `FAILED_PRECONDITION` ("Automation not published"). Two related surfaces, not to be confused:

| Goal | Mechanism |
|------|-----------|
| Change / refine / debug / have Quill **test** the draft | Send a message on the Quill thread (`POST ${TBASE}/input`) — Quill runs the test itself |
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

The run `state` holds `update_time` plus exactly one of: `pending`, `executing`, `stopping`, `stopped`, `completed` (outputs in `state.completed.outputs`), `failed` (`id`/`description`/`location`), `awaiting_guidance` (`exception`/`description`/`location`), `awaiting_answer`. Archiving is not a state: an archived run keeps its state and gains `archived_time`. Outputs are keyed by name with `commonV1Value` types, e.g. `{"text": "INV-112233"}` or `{"number": {"lo": 114800, "mid": 0, "hi": 0, "flags": 0}}`. **File** outputs come back as `{"file": {"remote": "organizations/{org}/workspaces/{ws}/files/{file_id}"}}`; download the bytes with `GET /api/v1/<that name>:download` (the `:download` verb, not the bare resource). See [runs-api.md](runs-api.md) and [files-api.md](files-api.md).

### `invocation_source` — who triggered the run

Each run records `invocation_details.invocation_source`:

| Value | Set when |
|-------|----------|
| `INVOCATION_SOURCE_TEST` | Quill triggered the run to test the **draft** |
| `INVOCATION_SOURCE_MANUAL` | A user started the run from the web app |
| `INVOCATION_SOURCE_PAT` | The `:invoke` API was called with an API key (`user_id` is the key's owner) |
| `INVOCATION_SOURCE_SCHEDULE` | A schedule fired the run (typically a published automation) |
| `INVOCATION_SOURCE_TRIGGER` | An event/trigger fired the run |

## Exception handling: draft (Quill) vs published (Workbench)

How a run *failure* is handled depends on the stage:

- **Draft runs raise no exceptions.** Draft-stage runs set `disable_exception_handling = true` — this is true for **both** Quill's `TEST` runs **and** your own draft `:invoke` (`MANUAL` or `PAT`). On failure the run parks in `awaiting_guidance` with an **empty `exception`** and a human-readable `description` (the traceback / missing-input message) plus a `location`. No exception resource is created.
- **Published runs raise exceptions that are resolved in the Workbench.** Published-stage runs always use standard exception handling (the `disable_exception_handling` flag does not apply). A failure creates a real `Exception` resource and files it as a work unit on a Workbench work item. It is resolved in that work item's chat with the `hermes` agent, or by submitting a retry or stop decision on the work unit (see [exceptions-api.md](exceptions-api.md)).

**You can invoke a draft yourself and ask Quill to debug it.** Beyond "Quill builds and tests," this is a supported workflow: invoke the draft (`AUTOMATION_STAGE_DRAFT`), and because draft runs surface failures inline (no exception is raised), tell Quill on the thread to monitor and fix that run — give it the run name (or just describe the failure) and it will read the run's `description`/`location`, diagnose, edit the code, and re-test.

---

## Refining an automation

Send follow-up messages on the same thread to iterate. Each accepted change is validated and (when it settles) autosaved as a new version.

> Editing a **published** automation that has no draft? Quill's autosave will fail until a draft exists — **fork one first** with `:fork`. See [Fixing or refining a published automation](#fixing-or-refining-a-published-automation--fork-a-draft-first).

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"message": {"content": "Also output the line items as a table."}}' \
  "${TBASE}/input"
```

---

## Grimoire artifacts (advanced)

Internally Quill stores the automation as artifacts on the thread (`grimoire://`): `aop.spy` (SPy code), `aop.md` (the user-facing AOP), `connections.json`, `metadata.json`, `code_manifest.json`, and `context.md` (private agent notes). For most integrations you only need the automation resource (`english_code` is the AOP) and the conversation.

To read one, percent-encode its URI in the path. The response carries the content base64-encoded in `data`:

```bash
curl -sS -H "Authorization: Bearer ${KOGNITOS_TOKEN}" "${TBASE}/artifacts/grimoire%3A%2F%2Faop.md:content"
# → {"artifact": {"id": "grimoire://aop.md", "mime_type": "text/markdown", ...}, "data": "<base64>"}
```

Listing Quill artifacts (`GET ${TBASE}/artifacts`) may return `500`, so read them by the names above.

---

## Other thread endpoints

Stop, wake, fork, compact, rename, delete, feedback, context, and the rest work on `${TBASE}` exactly as described in [agents-api.md](agents-api.md). List the threads on an automation with `GET .../automations/{auto_id}/agents/quill2/threads`.
