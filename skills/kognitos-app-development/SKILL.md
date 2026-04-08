---
name: kognitos-app-development
description: Build Kognitos-backed applications with clear architecture boundaries, Lattice-aligned UI patterns, and durable implementation conventions.
license: MIT
---

# Kognitos App Development

Use this skill when you are building or refactoring application code around Kognitos workflows, screens, and integrations.

## Default Flow

1. Start with [references/architecture.md](references/architecture.md) to keep the app layer thin and the workflow layer explicit.
2. Use [references/lattice-ui.md](references/lattice-ui.md) before changing UI components or interaction patterns.
3. Apply the review checklist in [assets/app-review-checklist.md](assets/app-review-checklist.md) before finishing the change.

## When To Load More

- For layering and module boundaries: [references/architecture.md](references/architecture.md)
- For design-system usage and UI consistency: [references/lattice-ui.md](references/lattice-ui.md)
- For final self-review: [assets/app-review-checklist.md](assets/app-review-checklist.md)

## Notes

- Keep names generic and domain-facing; avoid coupling the skill to a single starter template.
- Mention template-specific patterns only when they generalize into a broader application-development rule.
