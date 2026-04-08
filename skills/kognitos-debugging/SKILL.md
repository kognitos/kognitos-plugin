---
name: kognitos-debugging
description: Debug Kognitos applications and workflows by isolating failure boundaries, capturing evidence, and narrowing the issue quickly.
license: MIT
---

# Kognitos Debugging

Use this skill when a Kognitos-backed application or workflow is failing and you need a reliable triage path.

## Default Flow

1. Use [references/triage-flow.md](references/triage-flow.md) to identify whether the issue is UI, integration, workflow, or environment related.
2. Use [references/evidence-capture.md](references/evidence-capture.md) to collect logs, payloads, and repro notes before changing code.
3. Run [scripts/collect_debug_bundle.py](scripts/collect_debug_bundle.py) when you need a quick local evidence summary.

## When To Load More

- For narrowing the fault domain: [references/triage-flow.md](references/triage-flow.md)
- For reproducible evidence collection: [references/evidence-capture.md](references/evidence-capture.md)
- For a quick local debug bundle: [scripts/collect_debug_bundle.py](scripts/collect_debug_bundle.py)

## Notes

- Capture evidence before “fixing” anything that is not yet explained.
- Prefer narrowing one boundary at a time over shotgun instrumentation.
