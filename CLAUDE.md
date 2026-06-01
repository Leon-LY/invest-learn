# CLAUDE.md — 远见 (FarSight)

> 洞察趋势，智选未来 · 基金投资智能分析平台 · by Leon

---

## 项目概述

远见是一个面向基金投资者的全栈智能分析平台。前端 Vue 3 + Tailwind CSS v4 + ECharts，后端 Python FastAPI + DeepSeek AI，部署在腾讯云轻量服务器。

| 属性 | 值 |
|------|-----|
| **项目名称** | 远见 FarSight |
| **版本** | v0.3.0 |
| **类型** | 全栈 Web 应用 |
| **开发者** | Leon |
| **GitHub** | https://github.com/Leon-LY/invest-learn |
| **线上地址** | http://49.232.49.175:8080 / http://leon-ly.cloud:8080 |
| **API 文档** | http://49.232.49.175:8080/api/docs |

---

## 服务器

| 属性 | 值 |
|------|-----|
| **IP** | 49.232.49.175 |
| **SSH** | `ssh root@49.232.49.175` |
| **域名** | leon-ly.cloud / www.leon-ly.cloud |
| **系统** | Ubuntu 22.04 |
| **面板** | https://console.cloud.tencent.com/lighthouse/instance/index |
| **端口** | 8080 (Web + API 代理), 8000 (API 内部) |
| **项目路径** | `/opt/invest-learn` |

---

## 技术栈

| 层 | 技术 |
|------|------|
| **前端** | Vue 3 + TypeScript + Tailwind CSS v4 + ECharts 5 |
| **状态** | Pinia + localStorage + sessionStorage |
| **后端** | Python 3.11 + FastAPI + SQLAlchemy 2.0 (async) |
| **AI** | DeepSeek API (OpenAI-compatible) — 新闻影响分析 |
| **数据库** | PostgreSQL 15 + Redis 7 |
| **部署** | Docker Compose (4 容器: nginx + backend + postgres + redis) |
| **数据源** | AKShare (A股/基金/指数) + RSS (新闻) + 天天基金 API |
| **图表** | ECharts 5 |

---

## 容器架构

```
investlearn-frontend  (nginx:alpine)      → :8080 (Web + API 代理)
investlearn-backend   (FastAPI + Python)   → :8000 (内部)
investlearn-db        (PostgreSQL 15)      → :5432 (内部)
investlearn-redis     (Redis 7)            → :6379 (内部)
```

Nginx 配置 (`deploy/nginx.conf`)：
- `/*` → Vue SPA 静态文件 (try_files → index.html)
- `/api/*` → 代理到 backend:8000
- `/health` → 代理到 backend:8000/health

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
# 拉取最新代码
cd /opt/invest-learn
git clone https://ghfast.top/https://github.com/Leon-LY/invest-learn.git /tmp/inv
cp -r /tmp/inv/.[!.]* /tmp/inv/* /opt/invest-learn/ 2>/dev/null
rm -rf /tmp/inv

# 重建并重启所有容器（前端在 Docker 内自动构建）
docker compose -f deploy/docker-compose.prod.yml up -d --build

# 导入种子数据（学习内容 + RSS 源初始化）
docker compose -f deploy/docker-compose.prod.yml exec backend python seed_data.py

# 仅重启
docker compose -f deploy/docker-compose.prod.yml restart
```

### 服务器管理

```bash
# 查看容器状态
docker ps

# 查看日志
docker compose -f deploy/docker-compose.prod.yml logs -f backend

# 手动触发爬虫
curl -X POST http://localhost:8080/api/v1/crawl/trigger/news
curl -X POST http://localhost:8080/api/v1/crawl/trigger/funds
curl -X POST http://localhost:8080/api/v1/crawl/trigger/global
curl -X POST http://localhost:8080/api/v1/crawl/trigger/a_stock
```

---

## 项目结构

```
invest-learn/
├── frontend/                         # Vue 3 前端
│   ├── Dockerfile                    # 多阶段构建 (node build + nginx serve)
│   ├── src/
│   │   ├── api/                      # axios 接口 (market/news/watchlist/learn)
│   │   ├── components/common/        # PriceText, ChangeBadge, BottomNav, EmptyState
│   │   ├── components/market/        # DailyBrief, SearchOverlay
│   │   ├── components/charts/        # KLineChart, LineChart
│   │   ├── mock/                     # Mock 系统（默认开启）
│   │   │   ├── data.ts               # 38只基金 + 36条新闻模板 + 学习内容
│   │   │   ├── experts.ts            # 5位基金经理档案 + AI分析
│   │   │   └── index.ts              # Mock API 拦截器 + 关键词分类过滤
│   │   ├── layouts/AppShell.vue      # 主布局（毛玻璃顶栏 + 搜索）
│   │   ├── router/index.ts           # Hash 路由
│   │   ├── stores/                   # Pinia (app, market)
│   │   ├── styles/main.css           # Tailwind v4 + 科技感主题 + 暗色模式
│   │   ├── types/market.ts           # TypeScript 类型定义
│   │   └── views/
│   │       ├── dashboard/            # 首页（每日简报+LIVE指示+自选+新闻）
│   │       ├── market/               # 基金诊断（图表+指标+费率）、基金详情、板块
│   │       ├── watchlist/            # 自选列表管理
│   │       ├── news/                 # 新闻列表（分类筛选+自动刷新）+ 详情（Markdown+AI分析）
│   │       ├── analysis/             # AI分析、大佬追踪、对比、筛选
│   │       ├── learn/                # 知识库、术语百科、策略库
│   │       ├── portfolio/            # 模拟交易
│   │       ├── journal/              # 投资笔记
│   │       └── settings/             # 设置（主题/数据源）
│   └── index.html                    # 入口 + 远见 splash screen
├── backend/                          # Python FastAPI 后端
│   ├── app/
│   │   ├── api/v1/                   # REST API
│   │   │   ├── news.py               # 新闻列表/详情/分析轮询
│   │   │   ├── market.py             # 搜索/基金详情/行情/筛选
│   │   │   ├── watchlist.py          # 自选 CRUD
│   │   │   ├── learn.py              # 学习内容
│   │   │   └── crawl.py              # 手动触发爬虫
│   │   ├── core/                     # 配置、数据库、缓存
│   │   ├── crawlers/                 # 数据爬虫
│   │   │   ├── news.py               # RSS 抓取 (6源) + 关键词过滤 + 自动分类
│   │   │   ├── a_stock.py            # A股 (50只核心个股 + 6大指数)
│   │   │   ├── a_fund.py             # 基金净值 + ETF列表 + 元数据补全
│   │   │   ├── global_stock.py       # 全球指数 (AKShare替代yfinance)
│   │   │   └── base.py               # 基类 + UA伪装 + asyncio重试
│   │   ├── models/                   # SQLAlchemy 模型
│   │   ├── schemas/                  # Pydantic 校验
│   │   ├── services/
│   │   │   ├── news_service.py       # 新闻业务 + AI分析生成
│   │   │   ├── market_service.py     # 行情/基金详情/搜索 + 懒加载
│   │   │   └── llm_service.py        # DeepSeek API 调用
│   │   └── tasks/                    # APScheduler 定时任务
│   │       ├── scheduler.py          # 调度配置 + 启动自检
│   │       └── jobs.py               # 7 个定时任务
│   ├── main.py                       # FastAPI 入口 + lifespan
│   ├── requirements.txt
│   ├── Dockerfile
│   └── seed_data.py                  # 学习内容种子 + RSS 源初始化
└── deploy/
    ├── docker-compose.prod.yml       # 生产部署 (4 容器)
    ├── nginx.conf                     # Nginx 配置
    └── setup.sh                      # 一键部署脚本
```

---

## 定时任务（全自动）

| 周期 | 任务 | 说明 |
|------|------|------|
| 启动10秒后 | 全量首次爬取 | A股列表+ETF+全球指数+基金+新闻+AI分析 |
| 每3分钟 | A股行情 spot | 50只核心个股（轻量化，防限流） |
| 每5分钟 | AI 分析新新闻 | 批量5条 DeepSeek 生成 + sentiment 同步 |
| 每15分钟 | 新闻 RSS 抓取 | 6个国内源 + 关键词过滤 + 自动分类 |
| 每30分钟 | 全球指数更新 | AKShare global indices |
| 每天8:00 | ETF 列表同步 | |
| 每天17:00 | A股日线同步 | |
| 每天21:00 | 基金净值 + 元数据 | 所有 is_active 基金 |

---

## 数据流

### Mock 模式（默认）
```
Vue 组件 → axios → Mock 拦截器 → 内置数据 / 穿透到真实 API
```
- `localStorage.setItem('mock-api', 'false')` 关闭

### 真实模式
```
Vue 组件 → axios → Nginx(:8080) → FastAPI(:8000) → PostgreSQL/Redis
```

### 基金懒加载
```
用户搜索6位代码 → market/search → 本地DB查找
  → 未命中 → 天天基金API → 存入funds表 → 返回结果
  → 每日21:00 自动更新净值+元数据
```

### AI 分析流水线
```
RSS抓取(15min) → 新闻入库 → auto_analyze(5min)
  → DeepSeek API → 生成分析 → 存入news_analyses表
  → 同步 article.sentiment
```

---

## 路由表

| 路由 | 页面 | 功能 |
|------|------|------|
| `/` | 仪表盘 | 每日简报+LIVE指示+自选快照+新闻 |
| `/diagnosis` `/:code` | 基金诊断 | 净值走势图+阶段涨幅+风险指标+年度收益+费率 |
| `/watchlist` | 自选列表 | 搜索添加（懒加载）/删除/管理 |
| `/analysis` | 智能分析 | 大佬预测/AI分析/大佬追踪 |
| `/news` | 新闻列表 | 分类筛选+自动刷新+滚动恢复 |
| `/news/:id` | 新闻详情 | Markdown渲染+AI分析异步加载 |
| `/learn` | 知识库 | 分类文章列表 |
| `/learn/glossary` | 术语百科 | 搜索+分类筛选 |
| `/learn/strategies` | 策略库 | 投资策略 |
| `/learn/:slug` | 文章阅读 | 完整文章内容 |
| `/compare` | 对比分析 | 多基金对比 |
| `/screener` | 筛选器 | 条件筛选 |
| `/journal` | 投资笔记 | CRUD+localStorage |
| `/settings` | 设置 | 主题/数据源/API配置 |

---

## 关键设计决策

- **Hash 路由**：不依赖服务端 SPA fallback，手机端更稳定
- **红涨绿跌**：中国投资习惯，PriceText/ChangeBadge 统一处理
- **Mock 默认开启**：无后端也能完整展示，搜不到自动穿透到真实 API
- **BottomNav 全局化**：在 App.vue 层渲染，路由切换不销毁，彻底消除闪烁
- **AI 分析异步**：先渲染文章内容，AI 分析单独 Loading（3-8s）
- **新闻自动分类**：标题关键词匹配（70+组），前后端统一
- **基金懒加载**：6位代码自动从天天空 API 抓取，每日定时更新净值
- **RSS 关键词过滤**：60+组财经关键词，自动过滤非财经内容
- **AKShare 轻量化**：个股仅追踪50只核心，EAST Money 反爬 UA 伪装
- **DeepSeek 降级**：LLM 失败自动回退模板分析
- **清华镜像**：pip 和 apt 都用清华镜像

---

## 服务器部署速查

```bash
# 完整更新
cd /opt/invest-learn
git clone https://ghfast.top/https://github.com/Leon-LY/invest-learn.git /tmp/inv
cp -r /tmp/inv/.[!.]* /tmp/inv/* /opt/invest-learn/ 2>/dev/null
rm -rf /tmp/inv
docker compose -f deploy/docker-compose.prod.yml up -d --build
docker compose -f deploy/docker-compose.prod.yml exec backend python seed_data.py

# .env 配置（DeepSeek API Key 等）
# DEEPSEEK_API_KEY=sk-xxx
# DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
# DEEPSEEK_MODEL=deepseek-chat
```
