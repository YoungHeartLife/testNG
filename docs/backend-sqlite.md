# DeepSeek + SQLite 纯后端架构说明

## 扫描链路

```text
AkShare / Demo Data
    ↓
MarketDataProvider
    ↓
analyze_market：市场环境、风险等级、是否允许开仓
    ↓
NewsCrawler：爬取财经新闻、公告、RSS、自定义页面
    ↓
scan_stocks：横盘突破 / 缩量抗跌 / 最近涨停 / 一进二预备 / 强于指数
    ↓
DeepSeekAnalyzer：结合爬取数据 + 市场环境 + 候选股进行AI诊断
    ↓
decide_strategy：策略根据DeepSeek分析和硬风控做最终决策
    ↓
RealtimeNotifier：终端通知 + 可选Webhook实时通知
    ↓
SQLite：scan_runs / market_status / crawled_items / ai_analysis / ai_signals / strategy_decisions / notifications / trade_logs
```

## DeepSeek 配置

```bash
export DEEPSEEK_API_KEY="你的Key"
export DEEPSEEK_BASE_URL="https://api.deepseek.com"
export DEEPSEEK_MODEL="deepseek-chat"
```

如果不配置 Key，系统使用本地规则 AI 兜底，不影响策略扫描和 SQLite 留痕。

## 爬取数据源

环境变量：

```bash
export CRAWL_URLS="https://example.com/rss.xml,https://example.com/news.html"
```

命令行：

```bash
python -m backend.main scan --crawl-url "https://example.com/rss.xml"
```

## 1小时扫描

```bash
python -m backend.main scan --loop --interval 3600
```

## 实时通知

```bash
export NOTIFY_WEBHOOK_URL="https://your-webhook.example.com/notify"
python -m backend.main scan --loop --interval 3600
```

每轮扫描结束后，系统会立刻 POST 策略结果 JSON。
