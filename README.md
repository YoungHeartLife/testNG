# AI 情绪交易系统（MVP 第一版）

本仓库提供一个可本地部署的 AI 情绪交易辅助平台 MVP，核心原则是：

```text
环境 > 情绪 > 个股 > 技术
```

## 已实现能力

- 大盘环境监控：上涨家数、下跌家数、涨停数量、跌停数量、炸板率、AI 风险等级、是否允许开仓。
- AI 选股系统：基于第一阶段手动规则因子扫描近期涨停、放量长上影、缩量抗跌、横盘突破、一进二。
- AI 提示系统：根据市场环境和风控规则生成可解释交易提示。
- 今日交易报告：整合官方/主流财经新闻风险、Tushare 候选数据（可选）、重点股票池、持仓分析、执行清单与 PushPlus 微信推送。
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

### 今日交易报告与微信推送

```http
GET /api/report/today
POST /api/report/push
```

可选环境变量：

- `PUSHPLUS_TOKEN`：PushPlus 微信推送 Token。
- `TUSHARE_TOKEN`：启用 Tushare 候选股票数据适配；未配置时使用内置演示股票池。
- `HOLDINGS_JSON` / `HOLDINGS_FILE`：接入持仓后生成持仓股票交易信息。

## 数据源说明

后端优先使用 AkShare 获取 A 股快照；选股模块可在配置 `TUSHARE_TOKEN` 后读取 Tushare 日线/基础数据构造候选池；如果本地未安装、未配置 Token 或容器尚未联网，会自动使用内置演示数据，保证 MVP 可启动、可演示、可复盘。

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
