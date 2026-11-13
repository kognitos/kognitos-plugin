# Setup Checklist

Use this checklist when you need the shortest path to a working Kognitos development environment.

## 1. Local Tools

- Confirm `git`, `python3`, `node`, and `npm` are installed.
- Confirm the target repository's package manager and framework.

## 2. Kognitos Credentials

- Create an API key (Personal Access Token) in the Kognitos web app: open the user menu (your name, bottom left), select **API Keys**, then **Create API Key**. Pick an expiration, the workspaces the key may access, and a permission level (**All**, **Read only**, or **Restricted**). The key is shown once and uses the `kgn_pat_` prefix.
- Create the key in the organization you will work in: a key only works in its own organization.
- Create a `.env.local` in the project root (see [assets/bootstrap-template.env](../assets/bootstrap-template.env)):

```bash
KOGNITOS_TOKEN=kgn_pat_<your-token>
KOGNITOS_BASE_URL=https://app.us-1.kognitos.com
KOGNITOS_ORGANIZATION_ID=
KOGNITOS_WORKSPACE_ID=
```

`KOGNITOS_BASE_URL` is the host you sign in to. Organizations hosted outside the US region use their region's host (for example `https://app.uk-1.kognitos.com`).

## 3. Verify Token and Discover IDs

List organizations:

```bash
curl -sS -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${KOGNITOS_BASE_URL}/api/v1/me/organizations?page_size=50"
```

List workspaces for an org (`ORG` is the organization id):

```bash
curl -sS -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces?page_size=50"
```

IDs are the last segment of each `name` (`organizations/{org}`, `organizations/{org}/workspaces/{workspace}`). The organization list includes every organization the user belongs to; workspace calls return `403` for all but the key's own organization. A key limited to specific workspaces is refused in the others.

Set `KOGNITOS_ORGANIZATION_ID` and `KOGNITOS_WORKSPACE_ID` in `.env.local` with the chosen values.

## 4. Repository Setup

- Install dependencies.
- Verify the application starts locally.
- Verify linting or validation commands run cleanly.

## Exit Criteria

- The token authenticates successfully against the target environment.
- `KOGNITOS_ORGANIZATION_ID` and `KOGNITOS_WORKSPACE_ID` are set.
- The app boots locally or there is a concrete blocker with evidence.
- The engineer knows which skill to use next, and whether to work through the REST API or the MCP server ([mcp-server.md](mcp-server.md)).
