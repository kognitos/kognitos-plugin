---
name: kognitos-bootstrap
description: Set up a Kognitos application workspace, verify prerequisites, and establish the initial development baseline.
license: MIT
---

# Kognitos Bootstrap

Use this skill when a repository needs to be prepared for Kognitos application development, or when you need to verify a local environment before making changes.

## Default Flow

1. Check for a `.env.local` file in the project root. If missing, copy [assets/bootstrap-template.env](assets/bootstrap-template.env) to `.env.local` and have the user fill in `KOGNITOS_TOKEN`.
2. Source `.env.local` and verify the token works by calling the list-organizations endpoint (see [references/setup-checklist.md](references/setup-checklist.md)).
3. If `KOGNITOS_ORGANIZATION_ID` or `KOGNITOS_WORKSPACE_ID` are empty, list the user's orgs and workspaces and help them pick values.
4. Run the preflight helper in [scripts/preflight_check.py](scripts/preflight_check.py) to verify local CLI tools.
5. Use [references/environment-model.md](references/environment-model.md) when environment boundaries need to be clarified.

## When To Load More

- For the full setup checklist: [references/setup-checklist.md](references/setup-checklist.md)
- For environment boundaries and URL patterns: [references/environment-model.md](references/environment-model.md)
- For a starter `.env.local` template: [assets/bootstrap-template.env](assets/bootstrap-template.env)

## Notes

- `KOGNITOS_BASE_URL` is `https://app.us-1.kognitos.com` for US customers. EU customers swap `us-1` for `eu-1`.
- PATs use the `kgn_pat_` prefix and authenticate via `Authorization: Bearer <token>`.
- The token identifies the user, not a specific org or workspace. Org and workspace must be specified separately.
