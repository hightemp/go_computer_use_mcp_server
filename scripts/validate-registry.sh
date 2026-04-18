#!/usr/bin/env bash
set -euo pipefail

SCHEMA_URL="https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json"
SCHEMA_FILE="$(mktemp --suffix=.json)"

cleanup() {
  rm -f "$SCHEMA_FILE"
}
trap cleanup EXIT

curl -fsSL "$SCHEMA_URL" -o "$SCHEMA_FILE"
npx -y ajv-cli@5 validate --spec=draft7 --strict=false --validate-formats=false -s "$SCHEMA_FILE" -d server.json --errors=text
