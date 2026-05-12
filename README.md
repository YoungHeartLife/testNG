# AI 情绪交易系统（DeepSeek + SQLite 纯后端版）

当前版本不包含 Web 页面，核心是一个可以在终端运行的 Python 后端扫描器：

```text
爬取数据 + A股快照 → DeepSeek AI 分析 → 策略决策 → SQLite留痕 → 实时通知
```

系统仍遵循：

```text
环境 > 情绪 > 个股 > 技术
```

## 功能

- 每 1 小时策略扫描一次，支持 `--loop --interval 3600` 常驻运行。
- 数据源优先使用 AkShare 获取 A 股快照；失败时自动使用演示数据。
- 可配置爬取财经新闻、公告、RSS 或你自己的数据页面，作为 DeepSeek 分析上下文。
- DeepSeek API 可选：配置 `DEEPSEEK_API_KEY` 后调用 DeepSeek；不配置时使用本地规则 AI 兜底。
- 策略在 DeepSeek 分析后做最终决策：是否允许开仓、动作、建议仓位、理由。
- 使用 SQLite 保存扫描、市场环境、爬取数据、DeepSeek 分析、策略决策、通知记录。
- 每次扫描完成后立即终端通知；配置 `NOTIFY_WEBHOOK_URL` 后会实时 POST JSON 到你的通知服务。
- 支持 JSON 输出，方便后续接入企业微信、Server 酱、飞书、自建服务等。

## 快速开始

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r backend/requirements.txt
python -m backend.main scan --demo --no-deepseek
```

## 使用 DeepSeek AI

```bash
export DEEPSEEK_API_KEY="你的DeepSeek Key"
python -m backend.main scan \
  --crawl-url "https://example.com/finance-rss.xml"
```

也可以写入 `.env` 或直接使用命令行参数：

```bash
python -m backend.main scan \
  --deepseek-api-key "你的DeepSeek Key" \
  --crawl-url "https://example.com/finance-rss.xml"
```

> 没有 DeepSeek Key 时不会中断，系统会自动走本地规则 AI 兜底，方便离线测试。

## 1小时循环扫描

```bash
python -m backend.main scan --loop --interval 3600
```

或：

```bash
make scan-loop
```

## 实时通知

终端会在每次扫描完成后立即输出通知摘要。

如果你有自己的 Webhook：

```bash
export NOTIFY_WEBHOOK_URL="https://your-webhook.example.com/notify"
python -m backend.main scan --loop --interval 3600
```

通知 JSON 包含：

- `scan_run_id`
- `market_status`
- `risk_level`
- `allow_buy`
- `action`
- `position`
- `ai_provider`
- `ai_risk_score`
- `ai_summary`
- `top_signal`
- `reasons`

## SQLite 数据库

默认数据库路径：

```text
data/ai_trading.sqlite3
```

查看最近一次扫描：

```bash
python -m backend.main latest
```

## 终端输出内容

每轮扫描会输出：

1. 市场环境：上涨/下跌/涨停/跌停/炸板率/风险/是否允许开仓。
2. 爬取数据：爬到的新闻、公告或RSS标题和摘要。
3. DeepSeek AI 分析：情绪、风险分、建议动作、关键依据。
4. 策略最终决策：动作、仓位、是否允许开仓、决策理由。
5. AI 选股池：候选股票、评分、命中因子、解释。
6. 实时通知摘要和 SQLite 写入编号。

## JSON 输出

```bash
python -m backend.main scan --json
```

主要结构：

```json
{
  "scan_run_id": 1,
  "data_source": "akshare.stock_zh_a_spot_em",
  "market": {},
  "crawled_items": [],
  "signals": [],
  "ai": {
    "deepseek": {},
    "decision": {},
    "message": "..."
  },
  "decision": {},
  "notification": {}
}
```

## 常用命令

```bash
make scan              # 扫描一次，优先 AkShare + DeepSeek
make scan-demo         # 强制演示数据扫描一次
make scan-demo-ai-off  # 演示数据 + 禁用DeepSeek，完全离线测试
make scan-loop         # 每 1 小时循环扫描
make latest            # 查看最近一次 SQLite 结果
make smoke             # 本地检查
make package           # 打包纯后端代码
```

## 风险声明

本项目仅用于本地研究、策略验证和软件开发演示，不构成任何投资建议。实盘前必须人工验证数据质量、交易逻辑、风控规则和合规要求。
