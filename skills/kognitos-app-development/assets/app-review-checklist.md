# App Review Checklist

- The UI layer does not contain hidden business rules.
- Lattice or existing design-system primitives were checked first.
- Network and workflow boundaries are explicit.
- Error, loading, and empty states are handled.
- Naming is generic enough to survive template reuse.

## If the change touches a live agent chat or event stream

- The bundle (snapshot) is treated as canonical; the SSE stream is a
  fast-path optimization on top of it.
- Every reply is paired with a cancellable post-reply polling loop on the
  bundle, not a single `setTimeout` reload.
- Stream auto-close predicates defer close while messages are still
  streaming or tool-calls have unmatched results, and read state from a
  ref (not closed-over state).
- Background loops (polling, streaming) cancel cleanly on row switch and
  unmount via a monotonic run-id ref.
- Agent attachments render as interactive widgets with a computed href
  fallback; the click action actually opens the document.
