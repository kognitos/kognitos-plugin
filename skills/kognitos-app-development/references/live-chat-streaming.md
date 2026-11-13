# Live Agent Chat

Use this reference when the app shows a conversation with a Kognitos agent: an exception's Workbench chat, the automation builder agent, or a workspace agent. Every agent uses the same thread protocol; see the `kognitos-api-client` skill's [agents-api.md](../../kognitos-api-client/references/agents-api.md) for the endpoints.

## Default Expectations

- Treat the thread's event history (`GET .../events`) as the source of truth. The live stream (`GET .../stream`) is a fast path on top of it, not a replacement.
- Merge events by their `id`. `/stream` replays the whole history when it connects, so a reconnect re-sends events you already have; resume with the `Last-Event-ID` header and drop ids you have seen.
- Decide that a turn is over from the thread's `status.state`, not from a pause in the stream. A turn can end waiting on a question, an approval, or a tool result, and the UI has to offer that answer.
- After the user sends a message, poll the thread (every few seconds, with an overall cap) until `status_updated_at` is later than the send and the state is no longer a working state. Stop polling when the user switches threads or leaves the screen.
- Show the user's message at once, then replace it with the server's `input_text` echo when it arrives.
- Join consecutive `output_text` pieces in order to render a reply. Don't show tool names, tool arguments, or reasoning to business users. In an exception's Workbench chat (the `hermes` agent), show only the text inside `<user-message>` blocks, as the Workbench does (see [exceptions-api.md](../../kognitos-api-client/references/exceptions-api.md)).
- Keep the API key on the server. The browser talks to your backend, which proxies the thread calls.

## Background Work

- Give each polling loop and stream a cancellation handle (an `AbortController`, or a run counter held in a ref) so a new send, a thread switch, or unmount stops the old one.
- Read the latest merged events from a ref inside timers and stream callbacks, not from state captured when they were created.

## Attachments

Agent messages can reference files by id rather than URL. Build the link in your app (for example a route on your backend that downloads the file with the server's credentials) so the attachment opens instead of rendering as plain text.

## App Review Questions

- Does the chat recover when the stream drops or reconnects, without duplicated or missing messages?
- Does a reply appear without a page refresh, and does the UI show when the agent is waiting on the user?
- Do background loops stop when the user switches conversations?
- Do attachments open the document?
