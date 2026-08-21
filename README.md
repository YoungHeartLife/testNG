# AI 情绪交易系统（MVP 第一版）

本仓库提供一个可本地部署的 AI 情绪交易辅助平台 MVP，核心原则是：

```text
环境 > 情绪 > 个股 > 技术
```

## 已实现能力

- 大盘环境监控：上涨家数、下跌家数、涨停数量、跌停数量、炸板率、AI 风险等级、是否允许开仓。
- AI 选股系统：基于第一阶段手动规则因子扫描近期涨停、放量长上影、缩量抗跌、横盘突破、一进二。
- AI 提示系统：根据市场环境和风控规则生成可解释交易提示。
- Web 实时页面：Next.js 页面展示市场环境、AI 选股池、风险提示，并通过 WebSocket 定时刷新。
- Docker 本地部署：包含 frontend、backend、redis、postgres、nginx。

## 快速启动

```bash
docker compose up --build
```

启动后访问：

- 前端页面：http://localhost:3000
- Nginx 入口：http://localhost:8080
- FastAPI 文档：http://localhost:8000/docs


## VSCode 本地安装

本仓库已内置 VSCode 工作区配置、推荐插件、调试配置和一键安装脚本。

```bash
bash scripts/vscode-setup.sh
```

更多步骤见：[`docs/vscode-setup.md`](docs/vscode-setup.md)。

## API

### 市场环境

```http
GET /api/market/status
```

示例响应：

```json
{
  "market_status": "弱修复",
  "up_count": 3521,
  "down_count": 1487,
  "limit_up": 53,
  "limit_down": 4,
  "broken_limit_rate": 0.18,
  "risk_level": "medium",
  "allow_buy": true
}
```

### AI 选股池

```http
GET /api/selector/list
```

### AI 提示

```http
GET /api/ai/signals
```

### 实时仪表盘

```http
GET /api/dashboard
WS /ws/realtime
```

## 数据源说明

后端优先使用 AkShare 获取 A 股快照；如果本地未安装或容器尚未联网，会自动使用内置演示数据，保证 MVP 可启动、可演示、可复盘。

## 目录结构

```text
frontend/                 Next.js + React + Tailwind 实时页面
backend/gateway/          FastAPI API Gateway 与 WebSocket
backend/services/         市场环境、选股、风控服务
backend/ai/               AI Agent 与因子规则引擎
backend/database/         PostgreSQL 初始化 SQL
infra/                    Nginx 等部署配置
docs/                     设计文档
```

## 风险声明

本项目仅用于本地研究、辅助决策与软件开发演示，不构成任何投资建议。实盘交易前必须由人工验证交易逻辑、数据质量、风控规则和合规要求。

## 每日股票 AI 研究自动化

本仓库新增了一个独立的 Python 自动化流程，可由 GitHub Actions 每个交易日触发：

```text
股票数据源 → Python 获取行情 → 计算技术指标 → 整理数据 → 调用多个 AI 模型 → 综合模型结果 → 生成 Markdown/HTML 报告 → Email 发送 → 次日继续执行
```

### 本地运行

```bash
python -m pytest -q
python -m stock_research.main
```

默认会研究 `AAPL,MSFT,NVDA`，并在 `reports/` 下生成 `daily_stock_report.md` 与 `daily_stock_report.html`。可通过环境变量调整：

- `STOCK_SYMBOLS`：逗号分隔股票代码，例如 `AAPL,MSFT,NVDA`。
- `LOOKBACK_DAYS`：拉取的历史交易日数量，默认 `120`。
- `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` / `GEMINI_API_KEY`：配置后启用对应模型；未配置时使用本地规则分析兜底。
- `EMAIL_ENABLED=true`：启用邮件发送。
- `EMAIL_TO`、`EMAIL_FROM`、`SMTP_HOST`、`SMTP_PORT`、`SMTP_USERNAME`、`SMTP_PASSWORD`：SMTP 邮件配置。

### GitHub Actions 配置

工作流文件位于 `.github/workflows/daily-stock-research.yml`，默认在 UTC 时间周一到周五 12:30 运行，也支持手动触发。建议在 GitHub 仓库中配置：

- Repository Variables：`STOCK_SYMBOLS`、`LOOKBACK_DAYS`、`EMAIL_ENABLED`。
- Repository Secrets：AI API Key 与 SMTP 账号密码。

生成的报告会作为 `daily-stock-report` artifact 保存；如果启用 SMTP，也会自动发送到手机邮箱。
