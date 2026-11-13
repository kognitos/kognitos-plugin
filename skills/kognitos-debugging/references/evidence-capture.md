# Evidence Capture

Use this reference when a bug needs a minimal but complete diagnostic record.

## Collect

- Reproduction steps
- Input values or payload shape
- Environment name
- Relevant logs
- User-visible error state
- Workflow or run identifiers

## Avoid

- Redacting away the fields that explain the bug
- Mixing speculation with confirmed evidence
- Capturing only screenshots when structured data is available

## Kognitos Identifiers

Record these with every report so the run can be found again:

- Organization and workspace ids, and the host (`KOGNITOS_BASE_URL`)
- Automation id, its stage (draft or published), and version
- Run id and its state (`awaiting_guidance`, `completed`, ...)
- Exception id and, for published runs, the Workbench work item
- The time window, in UTC

For "who changed what" questions (a publish, a connection's credentials, a resolved exception), check the organization's audit log in the web app (user menu, **Audit log**). Calls made with an API key show the actor as **Personal Access Token**.
