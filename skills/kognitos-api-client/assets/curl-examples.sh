#!/usr/bin/env bash

# Public Kognitos API examples.
# Required: KOGNITOS_TOKEN
# Optional: KOGNITOS_REGION (default: us), KOGNITOS_ENV (default: prod),
#           KOGNITOS_ORGANIZATION_ID, KOGNITOS_WORKSPACE_ID

set -euo pipefail

: "${KOGNITOS_TOKEN:?Set KOGNITOS_TOKEN}"
: "${KOGNITOS_REGION:=us}"
: "${KOGNITOS_ENV:=prod}"

if [ "${KOGNITOS_ENV}" = "prod" ]; then
  BASE_URL="https://app.${KOGNITOS_REGION}-1.kognitos.com"
else
  BASE_URL="https://app.${KOGNITOS_REGION}-1.${KOGNITOS_ENV}.kognitos.com"
fi

# List current-user organizations
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${BASE_URL}/api/v1/me/organizations?page_size=10"

# Get one workspace (requires KOGNITOS_ORGANIZATION_ID and KOGNITOS_WORKSPACE_ID)
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${BASE_URL}/api/v1/organizations/${KOGNITOS_ORGANIZATION_ID}/workspaces/${KOGNITOS_WORKSPACE_ID}"

# List automations
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${BASE_URL}/api/v1/organizations/${KOGNITOS_ORGANIZATION_ID}/workspaces/${KOGNITOS_WORKSPACE_ID}/automations?page_size=10"
