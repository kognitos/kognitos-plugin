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
  empty-state message instead of a blank overlay.
