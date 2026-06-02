# CLAUDE.md — 远见 (FarSight)

> 洞察趋势，智选未来 · 基金投资智能分析平台 · by Leon

---

## 项目概述

远见是一个面向基金投资者的全栈智能分析平台。AI 驱动的大佬追踪、持仓分析、市场解读，前端 Vue 3，后端 Python FastAPI，部署在腾讯云轻量服务器。

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
| **端口** | 8080 (Web + API 代理), 8000 (API 内部) |
| **项目路径** | `/opt/invest-learn` |

---

## 技术栈

| 层 | 技术 |
|------|------|
| **前端** | Vue 3 + TypeScript + Tailwind CSS v4 + ECharts 5 |
| **状态** | Pinia + localStorage |
| **后端** | Python 3.11 + FastAPI + SQLAlchemy 2.0 (async) |
| **AI** | DeepSeek API — 新闻分析/大佬预测 |
| **数据库** | PostgreSQL 15 + Redis 7 |
| **部署** | Docker Compose (4 容器) |
| **数据源** | AKShare / RSS / 天天基金 / 新浪财经 |

---

## 容器架构

```
investlearn-frontend  (nginx:alpine)    → :8080
investlearn-backend   (FastAPI)          → :8000
investlearn-db        (PostgreSQL 15)    → :5432
investlearn-redis     (Redis 7)          → :6379
```

---

## 常用命令

### 服务器部署

```bash
cd /opt/invest-learn
git clone https://ghfast.top/https://github.com/Leon-LY/invest-learn.git /tmp/inv
cp -r /tmp/inv/.[!.]* /tmp/inv/* /opt/invest-learn/ 2>/dev/null
rm -rf /tmp/inv

docker compose -f deploy/docker-compose.prod.yml up -d --build
docker compose -f deploy/docker-compose.prod.yml exec backend python seed_data.py
```

### 缓存管理

```bash
# 重新生成全部大佬数据
docker compose -f deploy/docker-compose.prod.yml exec backend python3 -c "
import asyncio
from app.core.cache import cache_delete
from app.tasks.jobs import refresh_expert_tracker, generate_expert_predictions
async def run():
    await cache_delete('analysis:expert_tracker')
    await cache_delete('analysis:expert_predictions')
    for eid in ['zhangkun','xiezhiyu','gelan','houhao','zhushaoxing','xiaonan','wangzonghe','renzeping','honghao','libei','linyuan','danbin','qiuguolu','lidaxiao','zhaodanyang']:
        await cache_delete(f'analysis:expert_detail:{eid}')
    await refresh_expert_tracker()
    await generate_expert_predictions()
asyncio.run(run())
"

# 手动触发爬虫
curl -X POST http://localhost:8080/api/v1/crawl/trigger/news
```

---

## 定时任务（全自动）

| 周期 | 任务 | 说明 |
|------|------|------|
| 每60秒 | 市场摘要预生成 | Sina API → Redis |
| 每3分钟 | A股行情 spot | 50只核心个股 |
| 每5分钟 | AI 分析新新闻 | DeepSeek 批量生成 |
| 每15分钟 | 新闻 RSS 抓取 | 6源+关键词过滤 |
| 每30分钟 | 全球指数+大佬预测 | AKShare+DeepSeek |
| 每2小时 | 大佬追踪数据 | 15位大佬全量爬取 |
| 每天 | 基金净值/ETF/A股日线 | 按固定时间 |

---

## 关键设计决策

- **Mock 默认关闭**（生产环境安全）：API 没数据显示"暂无"，不回退假数据
- **所有慢操作预生成 + Redis 缓存**：摘要60s、大佬预测30min、大佬追踪2h、AI分析5min
- **BottomNav 全局化**：在 App.vue 层渲染，路由切换不销毁，消除闪烁
- **基金懒加载**：6位代码自动从天天基金 API 抓取并缓存
- **`<keep-alive :max="5">`**：Tab 切换不重复请求
- **RSS 关键词过滤**：60+组财经关键词，7种分类
- **数据源可靠性**：Sina > TianTian > AKShare 三层降级

---

## 路由表

| 路由 | 功能 |
|------|------|
| `/` | 仪表盘：市场摘要+自选+新闻 |
| `/news` | 新闻列表（全部/基金/行业/宏观/策略/海外/大佬） |
| `/news/:id` | 新闻详情：Markdown内容+AI分析 |
| `/diagnosis/:code` | 基金诊断：净值走势+风险指标+费率 |
| `/watchlist` | 自选：搜索添加（懒加载基金） |
| `/analysis` | 大佬预测+大佬追踪（15位） |
| `/analysis/expert-prediction/:id` | 大佬预测详情（多新闻分析） |
| `/analysis/expert/:id` | 大佬详情（持仓/净值/动态/启示） |
| `/learn` | 知识库（12篇文章/40术语/10策略） |

---

## 大佬阵容（15位）

**基金经理（7位）**：张坤、谢治宇、葛兰、侯昊、朱少醒、萧楠、王宗合  
**经济学家（3位）**：任泽平、洪灏、李蓓  
**投资家（3位）**：林园、但斌、赵丹阳  
**私募/分析师（2位）**：邱国鹭、李大霄

---

## 组合分析 API

```bash
curl -X POST http://localhost:8080/api/v1/market/portfolio/summary \
  -H "Content-Type: application/json" \
  -d '{"funds":[{"code":"005827","amount":50000},{"code":"161725","amount":30000}]}'
```
返回：配置分布 / 风险评分 / 建议
