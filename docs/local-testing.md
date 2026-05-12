# 本地测试说明（DeepSeek + SQLite 纯后端版）

## 完全离线测试

```bash
python -m backend.main scan --demo --no-deepseek
```

## 使用 DeepSeek 测试

```bash
export DEEPSEEK_API_KEY="你的DeepSeek Key"
python -m backend.main scan --demo
```

## 加入爬取URL

```bash
python -m backend.main scan \
  --demo \
  --crawl-url "https://example.com/finance-rss.xml"
```

## 1小时循环扫描

```bash
python -m backend.main scan --loop --interval 3600
```

## Webhook通知测试

```bash
export NOTIFY_WEBHOOK_URL="https://your-webhook.example.com/notify"
python -m backend.main scan --demo --no-deepseek
```

## 查看 SQLite 最新结果

```bash
python -m backend.main latest
```

## 本地检查

```bash
bash scripts/local-smoke.sh
```
