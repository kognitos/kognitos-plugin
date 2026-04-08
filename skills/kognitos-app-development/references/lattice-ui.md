# Lattice UI Guidance

Use this reference whenever Kognitos application work touches UI composition or styling.

## Default Expectations

- Reuse Lattice primitives before introducing custom elements.
- Prefer component props, variants, and tokens over ad hoc styling.
- Keep feature code dependent on exported design-system APIs rather than wrapped third-party primitives.

## Practical Rules

- Check whether the component already exists before creating a new one.
- Prefer semantic layout primitives over raw div-based layout when the design system provides them.
- Keep user-facing copy and states consistent across related screens.
- Avoid one-off styling that bypasses the design system unless there is a concrete gap.

## Escalation Path

- If the design system lacks a required primitive, document the gap and propose the smallest reusable addition.
- If the screen needs domain-specific composition, build it from Lattice components rather than embedding design-system logic in the feature layer.
