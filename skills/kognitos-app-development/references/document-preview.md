# Document Preview Guidance

Use this reference whenever Kognitos application work renders an extracted
document (invoice, ID, form, contract) with the per-field overlay produced by
Kognitos IDP — bounding boxes, confidence, and a side panel of extracted
values. The same patterns apply to any single-document preview built on a
Kognitos run output, not just invoices.

The IDP payload is a free-form `Struct` under
`state.completed.outputs.idp_extraction_results`. The OpenAPI spec does not
schematize its inner shape, so the application owns the contract end-to-end:
parser, overlay geometry, and panel UX must all agree on one canonical
field model.

## Default Expectations

- Treat the run payload as canonical. If the parser yields zero highlights,
  log a one-line diagnostic at the fetch boundary and surface a
  user-visible empty state — never render an empty overlay silently.
- Normalize the payload in an adapter, not in the UI. The viewer consumes a
  flat `FieldHighlight[]`; it does not walk protobuf wrappers.
- Drive canvas, mask, and overlay layers from a single `layout` object so
  they pixel-align across zoom and resize.
- Keep all interactive UI (overlay boxes, panel rows, toolbar) keyboard- and
  screen-reader-accessible — overlay buttons get `aria-label`, panel rows
  use real `<button>` elements with focus styling, tooltips have text.
- Open the viewer in a modal dialog. Do not navigate away from the dashboard
  context to view a document.

## Window Chrome and Color Scheme

The preview is a centered modal with a viewport-relative size, not a
full-screen takeover. Use a three-band dark palette so the document itself
is the only light surface — the eye lands on the page automatically.

| Surface | Role | Intent |
|---|---|---|
| Dialog shell | Frame around the entire preview | Near-black with a thin neutral border; close button in the dialog header |
| Page rail (left) | Per-page thumbnails for multi-page docs | Slightly lighter than the dialog; thumbnails use a subtle outline when selected |
| Document workspace (center) | The PDF canvas, overlay, dim mask, and bottom toolbar | Mid-dark neutral so a white page reads as "centered on a desk" |
| Right panel | Extracted-fields list and filters | Same family as the page rail; collapsible; never floats over the document |
| Document surface | The PDF page itself | The only white surface in the entire dialog |

Other rules:

- Borders are 1px and neutral. Do not stack drop shadows inside the dialog;
  the modal already has its own elevation.
- Avoid colored backgrounds on the rails. Color is reserved for state
  (focused box, hovered row, active page).
- Dialog header height stays small and shows only the document title and
  the close button. The toolbar lives in the workspace footer (see below).

## Document Positioning

The document fits the workspace width on first render and stays centered
through every zoom and panel-toggle. Three rules drive this:

1. **Single source of truth for layout.** Read PDF.js base viewport once
   (`{ baseW, baseH }` at scale 1), then derive `cssW`/`cssH` for the
   active zoom in one helper. Use the same numbers for the canvas size,
   the SVG mask viewBox, and the overlay container. Do not let PDF.js
   compute a viewport per layer — floating-point drift will desync them.
2. **Reserve the side-panel width even while the panel is collapsed.**
   Subtract a fixed panel-width constant (mirroring the panel's max width)
   from the workspace measurement. This prevents the document from
   reflowing when the user opens the panel for the first time.
3. **Lock the fit cap when the panel is open.** Once measured with the
   panel open, stash that cap in a ref. When the panel is later closed,
   `min(cap, currentRaw)` keeps the document at the narrower size and
   only re-centers — no surprise enlargement.

Render the page in a vertically scrollable container above a sticky bottom
toolbar (see next section). Re-fit on `ResizeObserver` callbacks so window
resize and dialog resize behave the same.

## Bottom Toolbar (Document Controls)

A pill-shaped, floating toolbar pinned to the bottom of the workspace.

| Order | Control | Notes |
|---|---|---|
| 1 | Zoom out | Disabled at min zoom |
| 2 | Zoom in | Disabled at max zoom |
| 3 | Fit to width | Resets to fit-cap |
| 4 | Toggle field highlights | Pressed-state visually distinct (subtle accent fill) |
| 5 | Download PDF | Streams from the document fetch endpoint |
| — | Divider | Visually separates document controls from panel control |
| 6 | Toggle right panel | Distinct visual treatment (outlined) so it reads as "panel" not "document" |

Rules:

- Buttons are square (~31×31 px), neutral hover, tooltip-on-top.
- The container row is `pointer-events-none` so it does not block document
  clicks; the pill itself re-enables pointer events. This matters when the
  toolbar overlaps the bottom of the document during zoom.
- Disabled-state for zoom limits is required — do not let the operator
  click into a no-op.
- Min/max zoom and step factor are constants near the component. Pick a
  step that yields ~12% change per click so two clicks roughly double or
  halve the perceived size.
- The toolbar re-centers itself on workspace resize via the same fit
  measurement used for the document.

## Bounding Box Overlays

Three layers, all sized in CSS pixels matching the canvas exactly:

1. **SVG `<defs><mask>`** sized `cssW × cssH`. Inside the mask, draw a
   white rect over the whole page, then a black rect per field bbox. This
   is a luminance mask — black areas become transparent in the dim layer.
2. **Dim layer** (`pointer-events-none`, z-index 10). A solid
   semi-transparent dark fill (~52% opacity) covers the entire page; the
   mask cuts holes only where field boxes sit, producing a "spotlight"
   effect. Do not use `backdrop-filter` — it doubles the cost without
   improving legibility.
3. **Overlay button layer** (z-index 20). One transparent `<button>` per
   field, positioned in either CSS percentages (when the bbox is
   normalized) or scaled PDF-point units. Three visual states stacked by
   z-index inside the layer:
   - Idle (z-21): neutral white border, no fill.
   - Linked-hover from panel (z-22): cool accent border (e.g. sky), still
     no fill.
   - Focused (z-23): warm accent border + outer ring (e.g. amber). Only
     one box is focused at a time.

Hover state is bidirectional: pointer enter on either the box or the
panel row sets a `linkedHoverFieldId`; both sides observe it. Activation
(click) sets a `focusedFieldId`, jumps to the field's page, scrolls the
panel row into view, and scrolls the box into the document viewport.

Coordinate mode is per-field, inferred from the decoded bbox magnitudes
(see "IDP Payload Contract" below). Both modes resolve into the same
percentage layout against the PDF base viewport, so the overlay code does
not branch on units.

## Right Panel — Extracted Values + Confidence

A collapsible side panel rendered to the right of the document, never
floating over it. Width matches the constant reserved by the document
fit measurement (typically ~320 px, capped at viewport width on small
screens).

Header:

- Title (e.g. "All extracted fields").
- Pill counter ("13 Fields", with the singular spelled out at 1).
- Close button.

Toolbar row beneath the header:

- Page filter dropdown — "All fields" plus one entry per page present
  in the parsed highlights ("Page 1 only", "Page 2 only", …).
- Search toggle — opens a single-line filter input below the toolbar.
  Input filters by label or value, case-insensitive, trimmed.
- Sort cycle — one icon-button that cycles through three modes: page +
  name, name A–Z, confidence high-first.

Field rows:

- Type icon (monospace text icon for plain fields).
- Monospace label (e.g. `vendor_invoice_number`).
- Page badge (`p1`, `p2`).
- Three-bar signal-style confidence meter: zero bars when confidence is
  null, one bar < 55, two bars < 85, three bars otherwise. Tooltip text:
  `Confidence: 98%` for fractional inputs (`0–1`), the bare number for
  larger inputs, and `No confidence score` for null.
- The extracted value rendered in a read-only-styled chip on its own
  row, with overflow scrolling for long values.

Interactions:

- Hover sets `linkedHoverFieldId` (two-way with overlay).
- Activate (click) sets `focusedFieldId`, switches the document to the
  field's page, scrolls the box into view in the document, scrolls the
  row into view inside the panel.
- Empty filter result shows a quiet inline message; the empty-payload
  state shows a different message that tells the operator the run had
  no extracted fields.

## IDP Payload Contract

Tool-agnostic spec — the parser must accept all of this:

- **Source path:** `payload.state.completed.outputs.idp_extraction_results`
  (or `idpExtractionResults`).
- **Tree shape:** root is a protobuf `Struct`, either
  `{ dictionary: { entries: [...] } }` or a top-level `entries` array of
  `{ key, value }` rows.
- **Fields list:** under the root, find the entry whose key text is
  `"fields"`. The value holds a list — resolve `value.list.items`,
  falling back to `list.items`, then `items`.
- **Field row:** each item is `{ dictionary: { entries } }` and contains
  `element_type`, `name`, `values` (list of value objects), `page_number`,
  `confidence`, and `bounding_box` (a nested dictionary with `x`, `y`,
  `width`, `height`).
- **Element type alias:** accept both `extracted_field` (legacy) and
  `document_field` (current `book-idp` shape), case-insensitive. Use a
  single `isExtractedFieldElementType` helper — never inline the literal
  comparison. New aliases must extend the helper, not the call sites.
  Bumblebee's `normalizeDocumentField` is the upstream canonical mapping.
- **Number decoding:** numbers may arrive as primitives, as protobuf
  `Value` wrappers (`{ number: ... }`, nested `{ value: ... }` layers),
  or as C# `Decimal`-style bits `{ lo, hi, mid?, flags? }`. Decode the
  `Decimal` shape as `Decimal.GetBits` (96-bit unsigned magnitude
  composed of `lo | mid << 32 | hi << 64`, scale in `flags` bits 16–23
  capped at 28, sign in bit 31). Do **not** use `lo / 2^32` — that
  decoder produced wrong bbox fractions on real payloads.
- **Bbox coordinate mode:** if `max(x + width, y + height) ≤ 1.0005`,
  treat the bbox as normalized 0–1 fractions. Otherwise treat it as PDF
  user-space points relative to the PDF.js base viewport at scale 1.
  Both modes resolve into the same percentage layout downstream.
- **Name blocklist:** skip rows whose name is in a small blocklist
  (`payment_recommendation`, `result_type`, `document_count`, `document`,
  `page_count`, `confidence`, empty), or contains `markdown_report`, or
  matches `summary` / starts with `summary_`. These are aggregate keys,
  not extracted fields, and they pollute the panel if rendered.

## Document Fetch and Payload Fetch

Two server endpoints owned by the application's adapter layer. The viewer
consumes URLs only — it does not see Kognitos credentials or file ids.

- **PDF bytes:** stream the document through a server route that resolves
  the file id from the run inputs and downloads via the Files API. See
  [`kognitos-api-client/references/runs-api.md`](../../kognitos-api-client/references/runs-api.md)
  for the run shape and the Files API for the download endpoint.
- **Run payload JSON:** a server route that returns the raw payload object
  (the same JSON used to build `KognitosRun`, but unmapped). Log a single
  one-line diagnostic on every fetch:

  ```
  payloadIsObject, hasIdpExtractionResults, fieldsListItemsLength,
  extractedFieldItemsCount, normalizedHighlightsCount
  ```

  When Kognitos renames an `element_type` (it has happened), this log is
  the fastest signal — `extractedFieldItemsCount` will go to zero while
  `fieldsListItemsLength` stays positive.

The viewer fetches both URLs once on mount, keyed by `runId` so changing
the row resets the in-flight requests cleanly.

## App Review Questions

- If Kognitos adds a new element-type alias tomorrow, is there exactly
  one place in the parser to add it?
- Does the payload-fetch endpoint log `extractedFieldItemsCount` so a
  silent regression is visible at the next on-call check?
- Does toggling the right panel reflow the document, or does the fit cap
  stay locked?
- Does activating a panel row both jump the document to the field's page
  and scroll the row into view inside the panel?
- Are canvas, dim mask, and overlay layers driven by the same `layout`
  object, so they stay pixel-aligned across zoom and resize?
- Does the toolbar's `pointer-events-none` container leave the document
  clickable beneath it, with the pill itself re-enabling pointer events?
- When the parser yields zero highlights, does the UI render an explicit
  empty-state message instead of a blank overlay?
