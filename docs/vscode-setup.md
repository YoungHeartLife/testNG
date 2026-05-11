# VSCode 本地安装与测试指南

> 说明：我无法直接操作你电脑上的 VSCode，但已经把 VSCode 工作区配置、推荐插件、启动任务、调试配置和一键安装脚本放进项目。你在本地打开项目后按下面步骤执行即可。

## 1. 解压并打开项目

```bash
tar -xzf ai-trading-system-mvp.tar.gz
cd ai-trading-system-mvp
code .
```

VSCode 打开后会提示安装推荐插件，建议全部安装。

## 2. 一键安装本地依赖

在 VSCode 顶部菜单执行：

```text
Terminal -> Run Task -> MVP: setup VSCode local deps
```

该任务会：

1. 复制 `.env.example` 为 `.env`。
2. 创建 `backend/.venv` Python 虚拟环境。
3. 安装后端依赖。
4. 安装前端 npm 依赖。
5. 运行本地 smoke check。

也可以在终端手动执行：

```bash
bash scripts/vscode-setup.sh
```

## 3. 启动后端

VSCode 执行：

```text
Terminal -> Run Task -> Backend: dev server
```

或用调试面板启动：

```text
Run and Debug -> Backend: FastAPI uvicorn
```

后端地址：

```text
http://localhost:8000
```

检查接口：

```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/market/status
curl http://localhost:8000/api/selector/list
curl http://localhost:8000/api/ai/signals
```

## 4. 启动前端

VSCode 执行：

```text
Terminal -> Run Task -> Frontend: dev server
```

打开页面：

```text
http://localhost:3000
```

页面应显示：

- 市场环境
- AI 选股池
- AI 实时提示
- WebSocket 连接状态

## 5. Docker 启动方式

如果你本地已安装 Docker Desktop，可以直接执行：

```text
Terminal -> Run Task -> Docker: compose up
```

或终端执行：

```bash
docker compose up --build
```

## 6. 常见问题

### pip 安装失败

如果公司网络或代理导致 PyPI 无法访问，可先配置国内镜像，例如：

```bash
python -m pip install -r backend/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### npm 安装失败

可切换 npm 镜像：

```bash
npm config set registry https://registry.npmmirror.com
cd frontend
npm install
```

### WebSocket 未连接

确认后端正在运行，并检查 `.env` 中：

```text
NEXT_PUBLIC_API_BASE=http://localhost:8000
NEXT_PUBLIC_WS_BASE=ws://localhost:8000
```
