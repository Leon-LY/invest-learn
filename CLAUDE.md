# CLAUDE.md — 基智学 (InvestLearn)

> 基金投资学习平台 · 个人项目 · by Leon

---

## 项目概述

基智学是一个面向基金投资新手的全栈学习平台。前端 Vue 3 + Tailwind，后端 Python FastAPI，部署在腾讯云轻量服务器。

| 属性 | 值 |
|------|-----|
| **项目名称** | 基智学 InvestLearn |
| **类型** | 全栈 Web 应用 |
| **开发者** | Leon |
| **GitHub** | https://github.com/Leon-LY/invest-learn |
| **线上地址** | http://49.232.49.175:8080 |
| **API 文档** | http://49.232.49.175:8080/api/docs |

---

## 服务器

| 属性 | 值 |
|------|-----|
| **IP** | 49.232.49.175 |
| **SSH** | `ssh root@49.232.49.175` |
| **系统** | Ubuntu 22.04 |
| **面板** | https://console.cloud.tencent.com/lighthouse/instance/index |
| **端口** | 8080 (Web), 8000 (API 内部) |
| **项目路径** | `/opt/invest-learn` |

### 服务器防火墙（腾讯云控制台操作）
- 登录腾讯云 → 轻量应用服务器 → VM-0-8-ubuntu → 防火墙
- 已开放端口：8080 (TCP), 8000 (TCP), 22 (SSH)

---

## 技术栈

| 层 | 技术 |
|------|------|
| **前端** | Vue 3 + TypeScript + Tailwind CSS v4 + ECharts |
| **状态** | Pinia + localStorage |
| **后端** | Python 3.11 + FastAPI + SQLAlchemy 2.0 (async) |
| **数据库** | PostgreSQL 15 + Redis 7 |
| **部署** | Docker Compose (4 容器: nginx + backend + postgres + redis) |
| **数据源** | AKShare (A股/基金) + yfinance (全球) + RSS (新闻) |
| **图表** | ECharts 5 |

---

## 容器架构

```
investlearn-frontend  (nginx:alpine)     → :8080 (Web + API 代理)
investlearn-backend   (FastAPI + Python)  → :8000 (内部)
investlearn-db        (PostgreSQL 15)     → :5432 (内部)
investlearn-redis     (Redis 7)           → :6379 (内部)
```

Nginx 配置：
- `/*` → Vue 静态文件 (SPA 回退到 index.html)
- `/api/*` → 代理到 backend:8000

---

## 常用命令

### 本地开发

```bash
# 前端
cd frontend && npm install && npm run dev    # http://localhost:3000

# 后端
cd backend && pip install -r requirements.txt
uvicorn main:app --reload                     # http://localhost:8000
```

### 服务器更新

```bash
# 方法1：GitHub 直连（可能超时）
cd /opt/invest-learn && git pull origin master

# 方法2：镜像克隆（推荐）
cd /opt/invest-learn && git clone https://ghfast.top/https://github.com/Leon-LY/invest-learn.git /tmp/inv && cp -r /tmp/inv/.[!.]* /tmp/inv/* /opt/invest-learn/ 2>/dev/null && rm -rf /tmp/inv

# 重建并重启所有容器（含前端构建）
docker compose -f /opt/invest-learn/deploy/docker-compose.prod.yml up -d --build

# 导入种子数据（含 AI 分析）
docker compose -f /opt/invest-learn/deploy/docker-compose.prod.yml exec backend python seed_data.py

# 仅重启（不改代码时）
docker compose -f /opt/invest-learn/deploy/docker-compose.prod.yml restart
```

### 服务器管理

```bash
# 查看容器状态
docker ps

# 查看日志
docker compose -f /opt/invest-learn/deploy/docker-compose.prod.yml logs -f backend

# 导入种子数据（学习文章+新闻+术语）
docker compose -f /opt/invest-learn/deploy/docker-compose.prod.yml exec backend python seed_data.py

# 手动触发爬虫（4种）
curl -X POST http://localhost:8080/api/v1/crawl/trigger/a_stock
curl -X POST http://localhost:8080/api/v1/crawl/trigger/global
curl -X POST http://localhost:8080/api/v1/crawl/trigger/funds
curl -X POST http://localhost:8080/api/v1/crawl/trigger/news
```

---

## 项目结构

```
invest-learn/
├── frontend/                         # Vue 3 前端
│   ├── src/
│   │   ├── api/                      # axios 接口 (market/news/watchlist/learn)
│   │   ├── components/
│   │   │   ├── common/               # PriceText, ChangeBadge, BottomNav, SearchOverlay
│   │   │   ├── charts/               # KLineChart, LineChart
│   │   │   └── market/               # DailyBrief, SearchOverlay
│   │   ├── mock/                     # Mock 数据系统
│   │   │   ├── data.ts               # 基金数据, 新闻, 诊断, 每日简报, 学习内容
│   │   │   ├── experts.ts            # 5位基金经理档案 + AI分析数据
│   │   │   └── index.ts              # Mock API 拦截器
│   │   ├── layouts/AppShell.vue      # 主布局（顶栏+底部导航+搜索）
│   │   ├── router/index.ts           # 所有路由（Hash 模式）
│   │   ├── stores/                   # Pinia (app, market)
│   │   ├── styles/main.css           # Tailwind v4 + 自定义主题
│   │   ├── views/
│   │   │   ├── dashboard/            # 首页（每日简报+自选+新闻+工具）
│   │   │   ├── market/               # 基金诊断、基金详情、板块、资金流向
│   │   │   ├── watchlist/            # 自选列表管理
│   │   │   ├── news/                 # 新闻列表+详情
│   │   │   ├── analysis/             # AI分析、大佬追踪、对比、筛选
│   │   │   ├── learn/                # 知识库、术语百科、策略库、文章阅读
│   │   │   ├── portfolio/            # 模拟交易
│   │   │   ├── journal/              # 投资笔记
│   │   │   └── settings/             # 设置（主题/数据源/API地址）
│   │   └── types/market.ts           # TypeScript 类型定义
│   └── deploy/                       # 不对外
├── backend/                          # Python FastAPI 后端
│   ├── app/
│   │   ├── api/v1/                   # REST API (market/news/watchlist/learn/crawl)
│   │   ├── core/                     # 配置、数据库、缓存
│   │   ├── crawlers/                 # 爬虫 (AKShare/yfinance/RSS)
│   │   ├── models/                   # SQLAlchemy 模型 (6 个文件)
│   │   ├── schemas/                  # Pydantic 校验
│   │   ├── services/                 # 业务逻辑层
│   │   └── tasks/                    # APScheduler 定时任务
│   ├── main.py                       # FastAPI 入口
│   ├── requirements.txt              # Python 依赖
│   ├── Dockerfile
│   └── seed_data.py                  # 种子数据（30条新闻+6篇文章+20术语+5策略）
└── deploy/
    ├── docker-compose.prod.yml       # 生产 Docker Compose（4 容器）
    ├── nginx.conf                     # Nginx 配置
    └── setup.sh                      # 一键部署脚本
```

---

## 数据流

### Mock 模式（默认）
```
Vue 组件 → axios → Mock 拦截器 → 返回内置假数据
```
- 可通过 `localStorage.setItem('mock-api', 'false')` 关闭
- 关闭后通过设置页配置真实 API 地址

### 真实模式
```
Vue 组件 → axios → Nginx(:8080) → FastAPI(:8000) → PostgreSQL/Redis
```

---

## 路由表

| 路由 | 页面 | 功能 |
|------|------|------|
| `/` | 仪表盘 | 每日简报+自选快照+新闻+工具入口 |
| `/diagnosis` `/:code` | 基金诊断 | 综合评分+5维分析+优缺点+建议 |
| `/watchlist` | 自选列表 | 搜索添加/删除/管理 |
| `/analysis` | 智能分析 | 大佬预测/AI分析/大佬追踪 三栏 |
| `/analysis/expert/:id` | 大佬详情 | 操作记录+预测+业绩 |
| `/news` | 新闻列表 | 分类筛选+加载更多 |
| `/news/:id` | 新闻详情 | 全文+AI影响分析 |
| `/learn` | 知识库 | 分类文章列表 |
| `/learn/glossary` | 术语百科 | 搜索+分类筛选 |
| `/learn/strategies` | 策略库 | 5条投资策略 |
| `/learn/:slug` | 文章阅读 | 完整文章内容 |
| `/compare` | 对比分析 | 多基金对比 |
| `/screener` | 筛选器 | 条件筛选基金 |
| `/journal` | 投资笔记 | CRUD+localStorage |
| `/settings` | 设置 | 主题/数据源/API配置 |

---

## 关键设计决策

- **Hash 路由** (`createWebHashHistory`)：不依赖服务端 SPA fallback，手机上更稳定
- **红涨绿跌**：中国投资习惯，`PriceText` 和 `ChangeBadge` 组件统一处理
- **Mock 默认开启**：无后端也能完整展示，适合 Demo
- **新闻自动生成**：RSS 抓取只有摘要，后端 `_generate_article_content()` 自动补全 AI 分析全文
- **新闻分类**：基于标题关键词匹配（非数据库字段），支持 基金/行业/大佬/策略 四类
- **定时爬虫**：APScheduler 内嵌 FastAPI 进程，每天 17:00 A股日线，21:00 基金净值，每 15 分钟新闻，每 60 分钟全球指数
- **清华镜像**：pip 和 apt 都用清华镜像，解决国内网络问题
- **GitHub 访问**：服务器到 GitHub 直连不稳定，用 `ghfast.top` 镜像

---

## 定时任务

| 时间 | 任务 | 说明 |
|------|------|------|
| 每 15 分钟 | 新闻 RSS 抓取 | 24×7 |
| 每 60 分钟 | 全球指数 (yfinance) | S&P, NASDAQ, 恒生等 |
| 每天 17:00 | A 股日线同步 (AKShare) | 收盘后 |
| 每天 21:00 | 基金净值同步 (AKShare) | 净值公布后 |

调度器随容器启动自动运行，查看日志：`docker logs investlearn-backend | grep -i scheduler`

---

## 备份和更新流程

```bash
# 完整更新（改代码后）— 前端会自动在 Docker 内构建
cd /opt/invest-learn
git clone https://ghfast.top/https://github.com/Leon-LY/invest-learn.git /tmp/inv
cp -r /tmp/inv/.[!.]* /tmp/inv/* /opt/invest-learn/ 2>/dev/null
rm -rf /tmp/inv
docker compose -f deploy/docker-compose.prod.yml up -d --build
docker compose -f deploy/docker-compose.prod.yml exec backend python seed_data.py

# 重启（服务挂了）
docker compose -f /opt/invest-learn/deploy/docker-compose.prod.yml restart

# 查看日志
docker compose -f /opt/invest-learn/deploy/docker-compose.prod.yml logs -f --tail=50
```
