#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PACKAGE_NAME="${1:-ai-trading-backend-sqlite}"
DIST_DIR="$ROOT_DIR/dist"
ARCHIVE_PATH="$DIST_DIR/${PACKAGE_NAME}.tar.gz"

mkdir -p "$DIST_DIR"
rm -f "$ARCHIVE_PATH"

tar \
  --exclude='.git' \
  --exclude='dist' \
  --exclude='data/*.sqlite3' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='.pytest_cache' \
  --exclude='.venv' \
  --exclude='backend/.venv' \
  --transform "s,^,${PACKAGE_NAME}/," \
  -czf "$ARCHIVE_PATH" \
  -C "$ROOT_DIR" \
  .

printf 'Package created: %s\n' "$ARCHIVE_PATH"
printf 'Extract with: tar -xzf %s\n' "$ARCHIVE_PATH"
