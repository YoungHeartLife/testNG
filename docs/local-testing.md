# 本地测试完整包说明

## 1. 解压完整包

```bash
tar -xzf ai-trading-system-mvp.tar.gz
cd ai-trading-system-mvp
```

## 2. 准备环境变量

```bash
cp .env.example .env
```

默认配置会启动：

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Nginx: http://localhost:8080
- PostgreSQL: localhost:5432
- Redis: localhost:6379

## 3. Docker 一键启动

```bash
docker compose up --build
```

启动后检查：

```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/market/status
curl http://localhost:8000/api/selector/list
curl http://localhost:8000/api/ai/signals
```

## 4. 页面检查

浏览器打开：

```text
http://localhost:3000
```

应看到：

- 市场环境：上涨家数、下跌家数、涨停数量、跌停数量、炸板率、允许开仓。
- AI 选股池：股票代码、名称、评分、命中因子、解释。
- AI 实时提示：当前市场状态、风险提示、适合策略、禁止追高提示。
- WebSocket 状态：连接成功后显示 `WebSocket 已连接`。

## 5. 不使用 Docker 的后端测试

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd ..
PYTHONPATH=. uvicorn backend.gateway.main:app --reload --host 0.0.0.0 --port 8000
```

## 6. 不使用 Docker 的前端测试

另开一个终端：

```bash
cd frontend
npm install
npm run dev
```

## 7. 重新打包

在项目根目录执行：

```bash
make package
```

或：

```bash
bash scripts/package.sh
```

输出文件：

```text
dist/ai-trading-system-mvp.tar.gz
```

## 8. 注意事项

- 第一版是 MVP，默认包含演示数据兜底；如果 AkShare 可用，后端会优先读取 AkShare A 股快照。
- 当前系统仅用于本地研究和辅助决策，不构成投资建议。
- 后续接入真实行情、回测、自动交易前，需要人工验证数据质量、因子逻辑和风控规则。
