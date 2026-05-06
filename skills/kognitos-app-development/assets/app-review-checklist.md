# App Review Checklist

- The UI layer does not contain hidden business rules.
- Lattice or existing design-system primitives were checked first.
- Network and workflow boundaries are explicit.
- Error, loading, and empty states are handled.
- Naming is generic enough to survive template reuse.

## If the change renders an extracted-document preview

- The IDP payload is normalized in an adapter (parser + helpers), not in
  the UI; the viewer consumes a flat field-highlight model.
- The element-type alias check is centralized in one helper that accepts
  every known literal (`extracted_field`, `document_field`, …); call
  sites do not inline the comparison.
- The payload-fetch endpoint logs `extractedFieldItemsCount` and
  `normalizedHighlightsCount` on every call so contract drift is visible
  in server logs without operator action.
- Canvas, dim mask (SVG luminance cutout), and overlay button layer all
  derive from a single `layout` object so they pixel-align across zoom
  and resize.
- The right panel is collapsible and never floats over the document; the
  document fit cap is locked while the panel is open so toggling the
  panel does not reflow the document.
- Hover and focus state are bidirectional between overlay boxes and
  panel rows; activating a row jumps the document to the right page and
  scrolls both the row and the box into view.
- When the parser yields zero highlights, the UI shows an explicit
  empty-state message (banner, not a small text strip) instead of a
  blank overlay.
- The PDF.js worker is loaded from a same-origin URL, copied during
  install or build, and pinned to the app's `pdfjs-dist` version.
- The PDF download adapter tries `workspaces/{ws}/files/{id}:download`
  before `files/{id}:download` so workspace-scoped files don't 404.
- The `<canvas>` mounts on `PDFDocumentProxy` ready, not on layout —
  layout is derived from the first `page.render()`.
- The dialog uses `key={runId}` (or equivalent) and aborts in-flight
  payload requests via `AbortController` when closing or switching runs.
- The initial page is `min(field.pageNumber)` from the parsed
  highlights, not an unconditional `1`.
- Bounding-box buttons re-enable highlights when off; clicking a panel
  row or its confidence meter does the same.
- SVG mask ids are namespaced via `useId()` and sanitized.
- The right-panel value chip recursively unwraps nested dictionaries,
  lists, and decimal-bit numbers; it never falls back to
  `JSON.stringify`.
- For non-normalized bounding boxes, the Y-axis flip decision is made
  per page via overlap scoring against the page rectangle.
- For chat-surfaced attachments: PDFs with a `runId` route to the rich
  viewer; images route to an in-app modal; the browser popup is the
  last-resort fallback only. MIME sniffing covers both the filename
  AND the URL path.
- The dialog title shows the document filename across all entry points
  (dashboard table, chat attachment, expert queue), not a generic
  "Document Processing" label.
