# Release Checklist

Use this reference before promoting a change.

## Code And Workflow Readiness

- The code change is reviewed and validated.
- The relevant SOP or workflow change is reviewed and versioned appropriately.
- Config changes are documented.
- Required migrations or environment variables are identified.

## Operational Readiness

- Observability or logs are sufficient to confirm the change worked.
- Rollback or mitigation steps are known.
- Stakeholders know whether the change is user-visible.

## Kognitos Readiness

- The draft was run end to end with realistic inputs before publishing, and `:validatePublish` passes.
- The connections the automation uses are ready in the target workspace.
- The API key the app uses covers the target workspace, has the permission level the app needs (a read-only key cannot invoke), and does not expire during the release window.
- App calls fit the platform limits: REST requests finish within 15 seconds (longer ones fail with `504`), and uploads stay under 800 MB.
- Someone owns the Workbench for the automation's exceptions after release.
