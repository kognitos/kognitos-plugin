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
  "${BASE_URL}/api/v1/books:search"
```

### Search books (workspace-scoped)

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"query": "email"}' \
  "${BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/books:search"
```

### Search procedures (actions)

Find specific actions across all books:

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"query": "send email"}' \
  "${BASE_URL}/api/v1/procedures:search"
```

Workspace-scoped:

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"query": "create invoice"}' \
  "${BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/procedures:search"
```

### List workspace books

See which books are available in a workspace:

```bash
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/books?page_size=20"
```

### Get book details

```bash
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${BASE_URL}/api/v1/books/${BOOK_NAME}/${BOOK_VERSION}"
```

### List book procedures

```bash
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${BASE_URL}/api/v1/books/${BOOK_NAME}/${BOOK_VERSION}/procedures"
```

### List book concepts (data types)

```bash
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${BASE_URL}/api/v1/books/${BOOK_NAME}/${BOOK_VERSION}/concepts"
```

## Workspace Connections

### List connections

```bash
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/connections?page_size=20"
```

### Get connection details

```bash
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/connections/${CONNECTION_ID}"
```

### Create a connection

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{}' \
  "${BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/books/${BOOK_NAME}/${BOOK_VERSION}/connections"
```

### Authorize a connection (OAuth)

```bash
curl -sS -X PUT \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{}' \
  "${BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/connections/${CONNECTION_ID}/authorize"
```

Returns an authorization URL for the user to complete OAuth.

## Integration Discovery Flow

1. **Search** for the integration by keyword (`books:search`).
2. **Inspect** what it offers (`/procedures`, `/concepts`).
3. **Create a connection** in the workspace if needed.
4. **Authorize** the connection (OAuth redirect).
5. **Reference** the connection in the automation's code and connections map.
