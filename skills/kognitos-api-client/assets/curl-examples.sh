#!/usr/bin/env bash

# Public Kognitos API examples.
# Set KOGNITOS_TOKEN, KOGNITOS_REGION, ORGANIZATION_ID, and WORKSPACE_ID first.

set -euo pipefail

: "${KOGNITOS_TOKEN:?Set KOGNITOS_TOKEN}"
: "${KOGNITOS_REGION:=us}"

BASE_URL="https://api.${KOGNITOS_REGION}.kognitos.com"

# List current-user organizations
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${BASE_URL}/api/v1/me/organizations?page_size=10"

# Get one workspace
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${BASE_URL}/api/v1/organizations/${ORGANIZATION_ID}/workspaces/${WORKSPACE_ID}"

# List automations
curl -sS \
  -H "Authorization: Bearer ${KOGNITOS_TOKEN}" \
  "${BASE_URL}/api/v1/organizations/${ORGANIZATION_ID}/workspaces/${WORKSPACE_ID}/automations?page_size=10"
