# Credentials (Secrets) API

Use this reference when you manage the credentials connections sign in with: API keys, usernames and passwords, OAuth logins, and the OAuth apps those logins use. The web UI calls these **credentials**; the API calls them **secrets**.

## Overview

- A **secret** is a stored credential with a `secret_type` that fixes the shape of its value. Its value is written as **versions**; the API never returns the value.
- A **secret type** is a schema (for example the fields an integration's authentication needs). Kognitos seeds one per integration authentication method.
- An **OAuth app** is your own registered OAuth client (`client_id`, `client_secret`, endpoints, scopes). OAuth secrets authorize against one.
- A **backend** is where secret values are stored: the Kognitos-managed default, or your own store (for example AWS Secrets Manager).

Secrets, OAuth apps and backends exist at two scopes, with the same routes under each:

```text
${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}                      (organization-wide)
${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}      (one workspace)
```

A secret's `scope` reads `organizations/{org}` or `organizations/{org}/workspaces/{ws}`; `shared` secrets are visible everywhere. These calls need the credential permissions on your role. A `403` with a plain-text `Forbidden` body means the gateway refused the call for this key: your role doesn't grant the permission, or the key was created with a narrower permission level. The response doesn't say which; check the key's settings and your role in the web app.

## Secret types

```bash
curl -sS -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${KOGNITOS_BASE_URL}/api/v1/secretTypes"
curl -sS -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${KOGNITOS_BASE_URL}/api/v1/secretTypes/${SECRET_TYPE_ID}"
```

A type has `name` (`secretTypes/{name}`), `display_name`, a `schema` (`fields`, each a `key` and a value type; optional fields are wrapped in `optional_type`, redacted fields in `sensitive_type`) and a `kind`: `generic`, `api_key`, `basic` or `oauth`.

## Create a secret

Two calls: create the secret (metadata), then add its first version (the value). If the second call fails, delete the secret so no empty credential is left behind.

```bash
# 1. Create in the workspace
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"secret": {"display_name": "Billing API key", "secret_type": "'"${SECRET_TYPE_NAME}"'"}}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/secrets"
# → {"id": "{secret_id}", "name": "billing-api-key", "display_name": "Billing API key",
#    "scope": "organizations/{org}/workspaces/{ws}", "secret_type": "...", "state": "...", "etag": "...", ...}

# 2. Write the value: one field per key in the type's schema
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"payload": {"fields": [{"key": "api_key", "value": {"text": "'"${API_KEY_VALUE}"'"}}]}}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/secrets/${SECRET_ID}:addVersion"
# → {"version": {"secret_id": "...", "version": ..., "state": "ENABLED", "create_time": "..."}}
```

- Every `:addVersion` call writes a new version and makes it current: that is how you rotate a credential.
- Pass `backend_id` on create when the scope has more than one backend; with one backend the server picks it.
- `name` is a slug derived from `display_name` and cannot be changed. `PATCH .../secrets/{secret_id}` (body `{"secret": {...}, "etag": "..."}`) updates `display_name` and `labels`.
- Check a payload before writing it with `POST /api/v1/secretTypes:validateSchema` (`{"schema": {...}, "payload": {...}}`); it returns `valid` and per-field `violations` instead of failing.

### OAuth secrets

For a type of kind `oauth`, create the secret with `oauth_app_id` set, then start the consent flow instead of sending a value:

```bash
curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"oauth_payload": {"scopes": [], "arguments": {}}}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/secrets/${SECRET_ID}:addVersion"
# → {"authorize_url": "https://..."}
```

Send the user to `authorize_url`, then poll `GET .../secrets/{secret_id}` until `state` leaves `SECRET_STATE_PENDING_AUTHORIZATION` and becomes `SECRET_STATE_ACTIVE`. Empty `scopes` uses the app's configured scopes; `arguments` fills placeholders the app declares (for example a tenant).

## List, read, delete

```bash
curl -sS -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/secrets?page_size=50"
curl -sS -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/secrets/${SECRET_ID}"

# Which connections use a secret (connections carry it as credentials_id)
curl -sS -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/connections?filter=credentials_id%20%3D%20%22${SECRET_ID}%22"

curl -sS -X DELETE -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/secrets/${SECRET_ID}"
```

- `state`: `SECRET_STATE_ACTIVE` (usable), `SECRET_STATE_PENDING_AUTHORIZATION` (no value yet, or OAuth consent not completed) or `SECRET_STATE_DEGRADED` (the backing store has a problem).
- Deleting removes the Kognitos record. Add `?purge_backend=true` to also delete the stored values, including values that were adopted rather than created by Kognitos.
- Check usage before deleting: connections that use a deleted secret stop authenticating.

## Adopt existing values

If credentials already live in your own backend, wrap them instead of copying them:

```bash
# Entries in the scope's backend; already_managed marks ones Kognitos already wraps
curl -sS -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}:discoverInventory?backend_id=${BACKEND_ID}"
# → {"entries": [{"reference": {...}, "display_name": "...", "already_managed": false}], "next_page_token": ""}

curl -sS -X POST \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"backend_id": "'"${BACKEND_ID}"'", "reference": '"${REFERENCE_JSON}"', "secret": {"display_name": "Warehouse DB", "secret_type": "'"${SECRET_TYPE_NAME}"'"}}' \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/secrets:adopt"
```

`REFERENCE_JSON` is the entry's `reference` object exactly as `discoverInventory` returned it. Use the same `backend_id` you discovered it in. The adopted value must match the secret type's schema.

## OAuth apps

```bash
curl -sS -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/workspaces/${WS}/oauthApps"
```

An OAuth app has `display_name`, `secret_type` (the type its connections use; required on create), `config` (the provider's authorize and token endpoints, scopes and parameters) and `credentials` (`client_id`, plus `client_secret`, which is write-only and never returned). Create with `POST .../oauthApps` (`{"oauth_app": {...}}`), update with `PATCH .../oauthApps/{oauth_app_id}` sending the current `etag`, delete with `DELETE .../oauthApps/{oauth_app_id}`.

## Backends

```bash
curl -sS -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${KOGNITOS_BASE_URL}/api/v1/backendTypes"
curl -sS -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${KOGNITOS_BASE_URL}/api/v1/organizations/${ORG}/backends"
```

`backendTypes` lists the stores you can register and their configuration and auth fields. A backend with `kognitos_managed: true` is the platform default and can't be changed. Register your own with `POST .../backends` (`type_id`, `display_name`, `config`, `auth`); the trailing segment of its `name` is the `backend_id` used above.

## Gotchas

- The API never returns secret values or `client_secret`. Keep your own copy only if you must, and never log request bodies that carry them.
- Writes that take an `etag` fail when it is stale: read the resource again and retry.
- A secret's `secret_type` can't be changed after create; create a new secret instead.
