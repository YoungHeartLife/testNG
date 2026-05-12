#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

python -m compileall backend
python -m backend.main scan --demo --no-deepseek --top 5 --database data/smoke.sqlite3 >/tmp/ai_trading_smoke.out
test -s data/smoke.sqlite3
rg "AI 情绪交易系统|爬取数据|DeepSeek AI 分析|策略最终决策|实时通知|SQLite已写入" /tmp/ai_trading_smoke.out >/dev/null
python -m backend.main scan --demo --no-deepseek --top 3 --database data/smoke.sqlite3 --json >/tmp/ai_trading_smoke.json
python -m json.tool /tmp/ai_trading_smoke.json >/dev/null
python -m backend.main latest --database data/smoke.sqlite3 >/tmp/ai_trading_latest.json
python -m json.tool /tmp/ai_trading_latest.json >/dev/null

echo "smoke check: ok"
