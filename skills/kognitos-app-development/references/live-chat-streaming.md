# Live Chat Streaming Guidance

Use this reference whenever Kognitos application work surfaces an exception
or run agent conversation in the UI (live chat, resolution panels, in-app
guidance threads, etc.).

The Kognitos `events:stream` endpoint is fast but **best-effort**. New-turn
events can be dropped on reconnect, the underlying socket auto-closes after
a `STATE_COMPLETE` completion, and history-replay can re-emit old events on
every reconnect. Treat the stream as a fast-path UX optimization, not as a
source of truth for what the agent has said.

## Default Expectations

- Treat the snapshot bundle (`exceptions/{id}` or equivalent run/agent
  resource) as canonical. The stream is a UX optimization on top of it.
- Pair every reply (`POST` to the agent's events endpoint) with a
  short-lived bundle polling loop, even if the SSE stream is open.
- Show optimistic outgoing bubbles immediately, then dedup against the
  server echo by content + timestamp (with a small skew tolerance).
- Never close the stream while client-side merge work is still pending.

## Post-reply Polling Pattern

After a successful reply, run an async loop that:

1. Waits ~1.5s so the server can enqueue the user echo.
2. Re-fetches the bundle every ~2.5s.
3. Stops 8s after the bundle stops changing (settled), or after a 50s cap.
4. Is cancellable via a monotonic run-id ref so a new send, row switch, or
   unmount supersedes any earlier loop.

Without this loop, agent replies that arrive 5–15s after the user's
message commonly fail to render until the next bundle refresh — the user
experiences a silent chat.

## Stream Auto-close

If your stream hook supports `closeOnCompletion`-style behavior, supply a
real predicate (not `() => true`). Defer close while:

- any chat message is still in a streaming state (partial snapshot waiting
  on its `STATE_COMPLETE` follow-up); or
- any tool-call message has no matching tool result yet.

The predicate fires from a deferred timer — read state from a `ref` synced
from the merged message list, not from a captured closure, or it will see
stale data.

## Document & Attachment Widgets

Agent attachments typically arrive as a file id, not a URL. Always compute
a usable `href` in the UI layer (e.g.
`/api/{provider}/files/{encodeURIComponent(fileId)}`) before rendering, or
the card will silently render as a non-interactive label.

For "open in popup" UX, prefer a `window.open(href, "_blank", "popup=yes,width=...")`
click handler with a graceful fallback to a regular new tab when the
browser blocks the popup. A bare `<a target="_blank">` opens a regular
tab, not a popup window.

## App Review Questions

- Does the chat keep working when the SSE stream silently drops a turn?
- Does sending a reply produce a visible agent response within ~15s
  without a manual page refresh?
- If you switch to a different conversation mid-turn, do background
  loops cancel cleanly?
- Do agent attachments render as interactive widgets that actually open
  the document?
