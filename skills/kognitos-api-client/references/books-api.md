# Books API (Integrations)

Use this reference when you need to discover available integrations, search for specific actions, or manage workspace connections.

## Overview

A **book** is a Kognitos integration package — it provides procedures (actions) and concepts (data types) for a specific service (e.g. Salesforce, email, databases). Books are installed into workspaces and may require **connections** (configured credentials) to operate.

## Discovery Endpoints

### Search books (global)

Find integrations by keyword across the full library:

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"query": "Salesforce"}' \
  "${KOGNITOS_BASE_URL}/api/v1/books:search"
```

### Search books (workspace-scoped)

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"query": "email"}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/books:search"
```

### Search procedures (actions)

Find specific actions across all books:

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"query": "send email"}' \
  "${KOGNITOS_BASE_URL}/api/v1/procedures:search"
```

Workspace-scoped:

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"query": "create invoice"}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/procedures:search"
```

### List workspace books

See which books are available in a workspace:

```bash
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/books?page_size=20"
```

### Get book details

```bash
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${KOGNITOS_BASE_URL}/api/v1/books/${BOOK_NAME}/${BOOK_VERSION}"
```

### List book procedures

```bash
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${KOGNITOS_BASE_URL}/api/v1/books/${BOOK_NAME}/${BOOK_VERSION}/procedures"
```

### List book concepts (data types)

```bash
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${KOGNITOS_BASE_URL}/api/v1/books/${BOOK_NAME}/${BOOK_VERSION}/concepts"
```

## Workspace Connections

### List connections

```bash
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/connections?page_size=20"
```

### Get connection details

```bash
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/connections/${CONNECTION_ID}"
```

### Create a connection

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/books/${BOOK_NAME}/${BOOK_VERSION}/connections"
```

An empty body works only for integrations that need no credentials (`connection_required: false` on the book). An integration that needs credentials returns `401` ("authentication is required"). Pick a method from the book's `authentications` list and pass its id in `authentication.authentication_id`, with the values in `authentication.authentication_credentials`.

For an **OAuth** method, also send `"oauth_flow": "OAuthFlowAuthorizationCode"` and a `Referer` header with your Kognitos host (the redirect URI is built from it; without it the call returns `404` "missing referer"):

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -H "Referer: ${KOGNITOS_BASE_URL}/" \
  -d '{"connection_name": "Team Slack", "authentication": {"authentication_id": "<oauth authentication id>"}, "oauth_flow": "OAuthFlowAuthorizationCode"}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/books/${BOOK_NAME}/${BOOK_VERSION}/connections"
# → {"authorize_url": {"url": "https://<provider>/oauth/...?client_id=...&redirect_uri=...&state=..."}}
```

The response has only the `authorize_url`, no connection id. Open the URL for the user; the connection appears in the list once they finish the OAuth flow. An integration can list several OAuth methods. If one returns `401` ("authentication is required"), it expects values in `authentication_credentials`; try another OAuth method or supply them.

Deleting a connection is not available to API keys (`403`). Remove connections in the web UI.

### Authorize a connection (OAuth)

```bash
curl -sS -X PUT \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/connections/${CONNECTION_ID}/authorize"
```

This is a `PUT` on the `/authorize` sub-path (not a `:authorize` custom method). Use it to re-authorize an existing OAuth connection, for example after its token expired. It returns `{"authorize_url": {"url": "..."}}`; open that URL for the user to complete OAuth. An unknown connection returns `404`.

## Integration Discovery Flow

1. **Search** for the integration by keyword (`books:search`).
2. **Inspect** what it offers (`/procedures`, `/concepts`).
3. **Create a connection** in the workspace if needed. For OAuth, the create call returns the authorize URL.
4. **Authorize**: the user completes OAuth in the browser. Re-authorize an existing connection with `PUT .../authorize`.
5. **Reference** the connection in the automation's code and connections map.
