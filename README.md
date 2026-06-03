# 🔭 远见 (FarSight)

> **洞察趋势，智选未来** — AI 驱动的基金投资智能分析平台

[![Version](https://img.shields.io/badge/version-v0.3.0-blue)](https://github.com/Leon-LY/invest-learn)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Deploy](https://img.shields.io/badge/deploy-Docker%20Compose-brightgreen)](deploy/)

<p align="center">
  <img src="frontend/public/favicon.svg" alt="远见 Logo" width="120" />
</p>

**远见** 是一个面向基金投资者的全栈智能分析平台。通过追踪 15 位顶级投资人（基金经理、经济学家、私募大佬），结合 DeepSeek AI 深度分析，帮助投资者看清市场趋势，做出更明智的投资决策。

---

## ✨ 核心功能

| 功能模块 | 说明 |
|----------|------|
| 📊 **市场仪表盘** | 实时指数、板块热度、资金流向、市场情绪一览 |
| 🤖 **AI 智能分析** | DeepSeek 驱动的新闻影响分析、大佬预测、组合诊断 |
| 👤 **大佬追踪** | 15 位顶流投资人持仓变化、业绩走势、操作动态 |
| 📰 **财经资讯** | 6 大 RSS 源自动抓取、7 类标签筛选、AI 自动分析 |
| 📚 **投资知识库** | 14 篇文章 + 40 金融术语 + 10 套策略框架 |
| 🔬 **基金诊断** | 净值走势、风险指标、费率分析、投资建议 |
| 💼 **组合分析** | 持仓配置分布、风险评分、优化建议 |
| 🔍 **股票筛选** | PE/PB/ROE 多维度筛选器 |
| 🌙 **暗色模式** | 支持亮色/暗色/跟随系统，完整暗色适配 |
| 📱 **响应式设计** | 移动端优先，桌面端完整导航，PWA 就绪 |

---

## 🏗️ 技术架构

```
┌─────────────────────────────────────────────────┐
│                    Nginx :8080                    │
│         (SPA 静态服务 + API 反向代理)              │
└──────────┬──────────────────────┬────────────────┘
           │                      │
     ┌─────▼──────┐        ┌─────▼──────┐
     │  Vue 3 SPA │        │  FastAPI   │
     │  Tailwind  │        │  :8000     │
     │  ECharts   │        │  SQLAlchemy│
     └────────────┘        └──┬─────┬───┘
                              │     │
                      ┌───────▼┐ ┌──▼──────┐
                      │PostgreSQL│ │ Redis 7 │
                      │  :5432  │ │ :6379   │
                      └─────────┘ └─────────┘
```

### 技术栈

| 层 | 技术选型 |
|----|----------|
| **前端框架** | Vue 3 + TypeScript + Pinia |
| **样式方案** | Tailwind CSS v4 + 自定义设计系统 |
| **图表可视化** | ECharts 5 (K线/折线/面积图) |
| **后端框架** | Python 3.11 + FastAPI (async) |
| **ORM** | SQLAlchemy 2.0 (async) |
| **AI 引擎** | DeepSeek API (新闻分析) + 通义千问 VL (截图分析) |
| **数据库** | PostgreSQL 15 + Redis 7 |
| **任务调度** | APScheduler (10 个定时 Job) |
| **部署** | Docker Compose (4 容器) |
| **数据源** | AKShare / RSS / 天天基金 / 新浪财经 |

---

## 🚀 快速开始

### 前置要求

- Docker & Docker Compose
- Node.js 20+ (前端开发)
- Python 3.11+ (后端开发)

### Docker 一键部署

```bash
git clone https://github.com/Leon-LY/invest-learn.git
cd invest-learn

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入你的 API Keys

# 启动所有服务
docker compose -f deploy/docker-compose.prod.yml up -d --build

# 初始化数据（可选）
docker compose -f deploy/docker-compose.prod.yml exec backend python seed_data.py
```

访问: `http://localhost:8080` | API 文档: `http://localhost:8080/api/docs`

### 前端开发

```bash
cd frontend
npm install
npm run dev          # http://localhost:3000
```

### 后端开发

```bash
cd backend
pip install -r requirements.txt

# 启动 PostgreSQL + Redis (Docker)
docker compose up -d db redis

# 启动 FastAPI
python main.py       # http://localhost:8000
```

---

## 📂 项目结构

```
invest-learn/
├── frontend/                # Vue 3 前端
│   ├── src/
│   │   ├── api/             # API 请求层 (axios)
│   │   ├── components/      # 通用组件
│   │   │   ├── charts/      # ECharts 图表组件
│   │   │   ├── common/      # UI 组件 (Badge/Skeleton/...)
│   │   │   └── market/      # 市场组件 (DailyBrief/Search)
│   │   ├── layouts/         # 布局组件 (AppShell)
│   │   ├── mock/            # 开发 Mock 数据
│   │   ├── router/          # Vue Router (22 路由)
│   │   ├── stores/          # Pinia 状态管理
│   │   ├── styles/          # 全局样式 + Tailwind 主题
│   │   ├── types/           # TypeScript 类型定义
│   │   ├── utils/           # 工具函数
│   │   └── views/           # 页面视图
│   │       ├── analysis/    # 智能分析
│   │       ├── dashboard/   # 仪表盘
│   │       ├── learn/       # 知识库
│   │       ├── market/      # 市场详情
│   │       ├── news/        # 新闻资讯
│   │       ├── portfolio/   # 模拟交易
│   │       ├── settings/    # 设置
│   │       └── watchlist/   # 自选管理
│   └── vite.config.ts
├── backend/                 # FastAPI 后端
│   ├── app/
│   │   ├── api/v1/          # REST API 路由
│   │   ├── core/            # 配置/数据库/缓存
│   │   ├── crawlers/        # 数据爬虫 (AKShare/RSS)
│   │   ├── models/          # SQLAlchemy 模型
│   │   ├── schemas/         # Pydantic 验证
│   │   ├── services/        # 业务逻辑层
│   │   ├── tasks/           # 定时任务 (APScheduler)
│   │   └── utils/           # 工具函数
│   ├── main.py              # 应用入口
│   └── seed_data.py         # 种子数据
├── deploy/                  # 部署配置
│   ├── docker-compose.prod.yml
│   ├── nginx.conf
│   └── setup.sh
├── CLAUDE.md                # AI 助手指南
└── README.md                # 本文件
```

---

## 🎨 设计系统

远见采用自研设计语言，核心特点：

- **玻璃拟态卡片** — 半透明背景 + 模糊效果，科技感十足
- **渐变网格背景** — 动态 CSS 渐变动画，减少视觉疲劳
- **中国红涨绿跌** — 符合国内投资者习惯（可在设置中切换）
- **完整暗色模式** — 所有组件 100% 暗色适配
- **交错入场动画** — 列表项依次淡入，提升浏览体验
- **扫描线/辉光边框** — 关键卡片使用动态发光边框

---

## 🤖 AI 分析系统

远见内置多层 AI 分析能力：

1. **新闻影响分析** — DeepSeek 自动评估新闻对基金的影响，包含：
   - 综合影响评分 (-100 ~ +100)
   - 受影响基金列表及具体影响
   - 短期/中期走势预判
   - 操作建议

2. **大佬预测** — 从多位大佬视角分析市场，30 分钟更新

3. **组合分析** — 输入基金持仓，AI 评估配置合理性

4. **截图分析** — 上传小红书/持仓截图，通义千问 VL 提取关键信息

---

## 🔧 环境变量

| 变量 | 说明 | 必填 |
|------|------|------|
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥 | 否* |
| `QWEN_API_KEY` | 通义千问 VL 密钥 | 否* |
| `DATABASE_URL` | PostgreSQL 连接串 | 是 |
| `REDIS_URL` | Redis 连接串 | 是 |
| `SECRET_KEY` | JWT 签名密钥 | 是 |

*未配置时 AI 分析功能不可用，但不影响其他功能

---

## 📡 API 概览

| 前缀 | 说明 | 端点数 |
|------|------|--------|
| `/api/v1/market` | 市场数据 | 17 |
| `/api/v1/news` | 新闻 + AI 分析 | 13 |
| `/api/v1/watchlist` | 自选管理 | 8 |
| `/api/v1/learn` | 学习内容 | 7 |
| `/api/v1/crawl` | 爬虫触发 | 1 |

完整 API 文档: `http://<server>:8080/api/docs`

---

## 🗓️ 定时任务

| 频率 | 任务 | 说明 |
|------|------|------|
| 60s | 市场摘要 | Sina API → Redis 缓存 |
| 3min | A股行情 | 50 只核心个股实时价 |
| 5min | AI 新闻分析 | DeepSeek 批量生成 |
| 15min | RSS 抓取 | 6 源 + 60+ 关键词过滤 |
| 30min | 全球指数 + 大佬预测 | AKShare + DeepSeek |
| 2h | 大佬追踪 | 15 位大佬全量数据 |
| 每日 | 基金净值/ETF/日线 | 盘中/盘后分时执行 |

---

## 🙏 免责声明

远见（FarSight）是一个**学习和技术演示项目**。所有数据来自公开 API（AKShare、天天基金、新浪财经等），AI 分析由大模型生成。**平台展示的所有内容仅供参考学习，不构成任何投资建议。** 投资有风险，入市需谨慎。

---

## 👨‍💻 开发者

**Leon** — 全栈独立开发

- GitHub: [@Leon-LY](https://github.com/Leon-LY)
- 线上地址: [leon-ly.cloud:8080](http://leon-ly.cloud:8080)

---

## 📄 License

MIT © 2025 Leon
