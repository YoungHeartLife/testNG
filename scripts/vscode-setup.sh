#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env from .env.example"
else
  echo ".env already exists, keeping it unchanged"
fi

python -m venv backend/.venv
# shellcheck disable=SC1091
source backend/.venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r backend/requirements.txt

cd frontend
npm install
cd "$ROOT_DIR"

bash scripts/local-smoke.sh

echo "VSCode local setup completed."
echo "Open Command Palette -> Tasks: Run Task -> Backend: dev server"
echo "Then run -> Frontend: dev server, and open http://localhost:3000"
