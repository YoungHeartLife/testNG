#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PACKAGE_NAME="${1:-ai-trading-system-mvp}"
DIST_DIR="$ROOT_DIR/dist"
ARCHIVE_PATH="$DIST_DIR/${PACKAGE_NAME}.tar.gz"

mkdir -p "$DIST_DIR"
rm -f "$ARCHIVE_PATH"

# Keep the archive source-only and reproducible enough for local handoff.
tar \
  --exclude='.git' \
  --exclude='dist' \
  --exclude='node_modules' \
  --exclude='.next' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='.pytest_cache' \
  --exclude='.venv' \
  --transform "s,^,${PACKAGE_NAME}/," \
  -czf "$ARCHIVE_PATH" \
  -C "$ROOT_DIR" \
  .

printf 'Package created: %s\n' "$ARCHIVE_PATH"
printf 'Extract with: tar -xzf %s\n' "$ARCHIVE_PATH"
