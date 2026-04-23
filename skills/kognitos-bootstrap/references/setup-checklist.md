# Setup Checklist

Use this checklist when you need the shortest path to a working Kognitos development environment.

## 1. Local Tools

- Confirm `git`, `python3`, `node`, and `npm` are installed.
- Confirm the target repository's package manager and framework.

## 2. Kognitos Credentials

- Obtain a Personal Access Token (PAT) from the Kognitos console. Tokens use the `kgn_pat_` prefix.
- Create a `.env.local` in the project root (see [assets/bootstrap-template.env](../assets/bootstrap-template.env)):

```bash
KOGNITOS_TOKEN=kgn_pat_<your-token>
KOGNITOS_BASE_URL=https://app.us-1.kognitos.com
KOGNITOS_ORGANIZATION_ID=
KOGNITOS_WORKSPACE_ID=
```

EU customers swap `us-1` for `eu-1` in `KOGNITOS_BASE_URL`.

## 3. Verify Token and Discover IDs

List organizations:

```bash
curl -sS -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${KOGNITOS_BASE_URL}/api/v1/me/organizations?page_size=50"
```

List workspaces for an org:

```bash
curl -sS -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG_ID}/workspaces?page_size=50"
```

Set `KOGNITOS_ORGANIZATION_ID` and `KOGNITOS_WORKSPACE_ID` in `.env.local` with the chosen values.

## 4. Repository Setup

- Install dependencies.
- Verify the application starts locally.
- Verify linting or validation commands run cleanly.

## Exit Criteria

- The token authenticates successfully against the target environment.
- `KOGNITOS_ORGANIZATION_ID` and `KOGNITOS_WORKSPACE_ID` are set.
- The app boots locally or there is a concrete blocker with evidence.
- The engineer knows which skill to use next.
