# 周易 · 智能算命平台

> 融合传统周易六十四卦与八字命理，借助现代技术为您解惑指引。

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Vue](https://img.shields.io/badge/Vue-3.5+-4FC08D?logo=vuedotjs&logoColor=white)](https://vuejs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.6+-3178C6?logo=typescript&logoColor=white)](https://typescriptlang.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## ✨ 功能特性

| 模块 | 功能 |
|------|------|
| **☇ 铜钱卜卦** | 虚拟三枚铜钱六次投掷，得出本卦与变卦；GSAP 3D 动画 + SVG 六爻实时渲染 |
| **☰ 八字命盘** | 输入出生时间自动排出四柱，五行统计雷达图，日主强弱分析 |
| **📊 数据看板** | 六十四卦频率热力图、运势走势折线图、五行饼图、每日活跃柱状图 |
| **📜 历史记录** | 卜卦与命盘历史管理，支持分页筛选和删除 |
| **🔐 用户认证** | JWT 注册/登录/刷新，bcrypt 密码加密，登录状态持久化 |

---

---

## 🛠️ 技术栈

### 后端

| 类别 | 技术 | 版本 |
|------|------|------|
| Web 框架 | FastAPI | 0.115+ |
| ASGI 服务器 | Uvicorn | 0.30+ |
| ORM | SQLAlchemy (asyncio) | 2.0+ |
| 数据库驱动 | aiosqlite / asyncpg | — |
| 数据验证 | Pydantic v2 + pydantic-settings | 2.0+ |
| 鉴权 | python-jose (JWT) + bcrypt | — |
| 中国历法 | ephem（节气计算） | 4.1+ |
| AI 解读 | anthropic SDK（可选） | 0.40+ |
| 测试 | pytest + pytest-asyncio + httpx | — |

### 前端

| 类别 | 技术 | 版本 |
|------|------|------|
| 框架 | Vue 3 (`<script setup>`) | 3.5+ |
| 构建工具 | Vite | 6.0+ |
| 语言 | TypeScript | 5.6+ |
| 路由 | Vue Router | 4.4+ |
| 状态管理 | Pinia | 2.2+ |
| UI 组件库 | Element Plus（暗色主题定制） | 2.8+ |
| 数据可视化 | Apache ECharts + vue-echarts | 5.5+ |
| 动画 | GSAP | 3.12+ |
| CSS | UnoCSS | 0.61+ |
| HTTP | axios + 拦截器（自动注入 JWT） | 1.7+ |

---

## 📁 项目结构

```
zhou-yi/
├── backend/
│   └── app/
│       ├── main.py                    # FastAPI 入口，lifespan 自动建表
│       ├── core/
│       │   ├── config.py              # pydantic-settings 环境变量
│       │   ├── database.py            # 异步 engine + session
│       │   └── security.py            # JWT 签发/验证 + bcrypt
│       ├── models/                    # SQLAlchemy ORM 模型
│       │   ├── user.py
│       │   ├── divination.py          # 卜卦记录
│       │   └── bazi.py                # 八字命盘记录
│       ├── schemas/                   # Pydantic 请求/响应 schema
│       │   ├── divination.py
│       │   ├── bazi.py
│       │   └── dashboard.py
│       ├── api/
│       │   ├── deps.py                # get_db, get_current_user
│       │   └── v1/
│       │       ├── router.py          # 路由聚合
│       │       ├── auth.py            # 认证端点
│       │       ├── divination.py      # 卜卦端点
│       │       ├── bazi.py            # 八字端点
│       │       ├── history.py         # 历史删除端点
│       │       └── dashboard.py       # 看板聚合端点
│       ├── services/
│       │   ├── hexagram/
│       │   │   ├── hexagram_data.py   # 六十四卦完整数据（King Wen 序列）
│       │   │   ├── coins.py           # 掷铜钱爻序列生成算法
│       │   │   └── interpreter.py     # 卦象解读引擎 + 运势评分
│       │   ├── bazi/
│       │   │   ├── calendar.py        # 公历→四柱干支转换（ephem 计算节气）
│       │   │   ├── wuxing.py          # 五行统计和日主强弱判断
│       │   │   └── analyzer.py        # 命盘分析和运势展望
│       │   └── dashboard/
│       │       └── aggregator.py      # 看板数据聚合 SQL
│       └── tests/
│           ├── conftest.py
│           ├── test_hexagram.py       # 44 个卜卦单元测试
│           └── test_bazi.py           # 25 个八字单元测试
├── frontend/
│   └── src/
│       ├── main.ts                    # 应用入口
│       ├── App.vue                    # 根组件
│       ├── router/index.ts            # 路由（含认证守卫）
│       ├── stores/
│       │   ├── auth.ts                # Pinia 认证状态
│       │   └── ...
│       ├── api/
│       │   └── client.ts              # axios 实例 + JWT 拦截器
│       ├── types/                     # TypeScript 类型定义
│       ├── components/
│       │   ├── hexagram/              # CoinToss, HexagramLines, HexagramCard
│       │   ├── bazi/                  # BaziChart, WuxingRadar, GanzhiPill
│       │   └── dashboard/             # HexagramHeatmap, LuckTrendLine, WuxingPie, UserActivityBar
│       └── views/                     # HomeView, DivinationView, BaziView, DashboardView, HistoryView, AuthView
├── pyproject.toml                     # Python 项目配置（uv）
└── README.md
```

---

## 🚀 快速开始

### 环境要求

- **Python** ≥ 3.12
- **Node.js** ≥ 18
- **[uv](https://docs.astral.sh/uv/)** — Python 包管理器

```bash
# 安装 uv（如果尚未安装）
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 1. 克隆项目

```bash
git clone https://github.com/lihanbing226/zhouyi.git
cd zhouyi
```

### 2. 启动后端

```bash
# 安装 Python 依赖
uv sync

# 配置环境变量（首次）
cp backend/.env.example .env
# 编辑 .env，至少修改 SECRET_KEY

# 启动开发服务器（首次启动自动建表）
uv run uvicorn backend.app.main:app --reload --port 8000
```

访问 **http://localhost:8000/docs** 查看完整的 Swagger API 文档。

### 3. 启动前端

```bash
cd frontend

# 安装 npm 依赖
npm install

# 启动开发服务器
npm run dev
```

访问 **http://localhost:5173** 查看前端应用。

---

## ⚙️ 环境变量

在项目根目录创建 `.env` 文件（参考 `backend/.env.example`）：

```ini
# 数据库（开发用 SQLite，生产换 PostgreSQL）
DATABASE_URL=sqlite+aiosqlite:///./zhou_yi.db
# DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/zhou_yi

# JWT 认证（生产环境必须改为随机强密钥）
SECRET_KEY=your-secret-key-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# 跨域（允许前端域名）
CORS_ORIGINS=["http://localhost:5173"]

# 运行环境
ENVIRONMENT=development

# Claude API（可选，用于 AI 解读功能）
ANTHROPIC_API_KEY=
```

生成安全的 `SECRET_KEY`：

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

---

## 📡 API 文档

所有端点可在 Swagger UI（`/docs`）或 ReDoc（`/redoc`）中查看和测试。

### 认证

```
POST   /api/v1/auth/register          # 注册（用户名 + 密码）
POST   /api/v1/auth/login             # 登录，返回 JWT access_token
POST   /api/v1/auth/refresh           # 刷新 token
GET    /api/v1/auth/me                # 获取当前用户信息（需 JWT）
```

### 卜卦

```
POST   /api/v1/divination/cast                # 执行卜卦（需 JWT）
GET    /api/v1/divination/hexagrams           # 查询全部六十四卦（分页）
GET    /api/v1/divination/hexagrams/{num}     # 查询单个卦象详情（1-64）
GET    /api/v1/divination/history             # 个人卜卦历史（需 JWT）
```

### 八字

```
POST   /api/v1/bazi/calculate         # 计算八字命盘（需 JWT）
GET    /api/v1/bazi/records/{id}      # 查询单个命盘记录（需 JWT）
GET    /api/v1/bazi/history           # 个人八字历史（需 JWT）
```

### 看板（无需认证）

```
GET    /api/v1/dashboard/overview              # 概览：今日卜卦数、活跃用户、运势均值
GET    /api/v1/dashboard/hexagram-stats        # 六十四卦频率统计（支持 ?days=30）
GET    /api/v1/dashboard/user-trend            # 用户活跃趋势（支持 ?days=7）
GET    /api/v1/dashboard/luck-distribution     # 运势评分分布
```

### 历史管理

```
DELETE /api/v1/history/{type}/{id}    # 删除记录（type: divination | bazi，需 JWT）
```

### JWT 使用示例

```bash
# 1. 注册
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"password123"}'

# 2. 登录，获取 token
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"password123"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# 3. 带 token 卜卦
curl -X POST http://localhost:8000/api/v1/divination/cast \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"question":"今年事业运势如何","method":"coins"}'
```

---

## 🧪 测试

```bash
# 运行全部测试
uv run pytest

# 查看详细输出
uv run pytest -v

# 运行单个模块
uv run pytest backend/app/tests/test_hexagram.py
uv run pytest backend/app/tests/test_bazi.py

# 生成覆盖率报告
uv run pytest --cov=backend --cov-report=html
# 报告在 htmlcov/index.html
```

当前测试状态：**104 个测试，全部通过** ✅

---

## 🔮 卜卦算法说明

采用传统**掷铜钱法**：

```
每爻投三枚铜钱，正面（字）= 3，反面（背）= 2，求三枚之和：

  6（老阴 ·· ）→ 初始为阴爻，有变，变后为阳
  7（少阳 —  ）→ 阳爻，不变
  8（少阴 -  ）→ 阴爻，不变
  9（老阳 ×  ）→ 初始为阳爻，有变，变后为阴

从初爻（第一爻）到上爻（第六爻）投六次，
得到六位爻序列（如 "679867"），
阳爻=1/阴爻=0 → 6 位二进制 → 映射到 King Wen 序 1-64 卦号。
变爻取反后得到变卦。
```

---

## 🗂️ 数据库说明

开发环境默认使用 **SQLite**（零配置，首次启动自动建表）。生产环境推荐切换 **PostgreSQL**：

```ini
# .env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/zhou_yi
```

数据库表结构：

| 表名 | 说明 |
|------|------|
| `users` | 用户账号（id, username, email, hashed_password） |
| `divination_records` | 卜卦记录（yao_sequence, hexagram_num, changing_yao, luck_score, interpretation） |
| `bazi_records` | 八字命盘（四柱干支, wuxing_score, day_master, strength, analysis） |

---

## 🚢 生产部署

### 构建前端静态资源

```bash
cd frontend
npm run build
# 产物在 frontend/dist/，可用 Nginx 静态托管
```

### 后端生产启动

```bash
# 多 worker 模式
uv run uvicorn backend.app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4
```

### 生产环境检查清单

- [ ] `SECRET_KEY` 已替换为强随机值（≥ 32 字节）
- [ ] `DATABASE_URL` 已指向 PostgreSQL
- [ ] `CORS_ORIGINS` 已配置为实际前端域名
- [ ] `ENVIRONMENT=production`（关闭 SQL 调试日志）
- [ ] 已配置 HTTPS / 反向代理（Nginx / Caddy）
- [ ] 前端已执行 `npm run build`
- [ ] 已配置日志收集和监控告警

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

```bash
# 1. Fork 本仓库并克隆
git clone https://github.com/your-username/zhouyi.git

# 2. 创建功能分支
git checkout -b feature/your-feature-name

# 3. 安装开发依赖
uv sync --extra dev
cd frontend && npm install

# 4. 开发并编写测试
uv run pytest          # 后端测试
npm run build          # 前端构建验证

# 5. 提交 Pull Request
```

**代码规范**：

```bash
# Python 格式化和 lint
uv run ruff check backend/
uv run ruff format backend/

# 类型检查
uv run mypy backend/
```

---

## 📄 许可证

本项目基于 [MIT License](LICENSE) 开源。

---

## 🙏 致谢

- [周易·易经](https://zh.wikipedia.org/wiki/易經) — 本项目的思想来源
- [FastAPI](https://fastapi.tiangolo.com) — 高性能 Python Web 框架
- [Vue.js](https://vuejs.org) — 渐进式前端框架
- [Apache ECharts](https://echarts.apache.org) — 强大的数据可视化库
- [GSAP](https://greensock.com/gsap/) — 专业级 Web 动画库
- [ephem](https://rhodesmill.org/pyephem/) — 精确的天文计算库
