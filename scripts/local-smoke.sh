#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

python -m compileall backend
python -m json.tool frontend/package.json >/dev/null
python -m json.tool frontend/tsconfig.json >/dev/null

if command -v docker >/dev/null 2>&1; then
  docker compose config >/dev/null
  echo "docker compose config: ok"
else
  echo "docker compose config: skipped, docker not installed" >&2
fi
