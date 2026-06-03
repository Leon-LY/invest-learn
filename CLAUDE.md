# CLAUDE.md — 远见 (FarSight)

> 洞察趋势，智选未来 · 基金投资智能分析平台 · by Leon

---

## 项目概述

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

## 服务器 & 技术栈

| 层 | 技术 |
|------|------|
| **前端** | Vue 3 + TypeScript + Tailwind CSS v4 + ECharts |
| **后端** | Python 3.11 + FastAPI + SQLAlchemy 2.0 (async) |
| **AI** | DeepSeek (文字分析) + 通义千问 VL (截图分析) |
| **数据库** | PostgreSQL 15 + Redis 7 |
| **部署** | Docker Compose (4 容器: nginx + backend + postgres + redis) |
| **数据源** | AKShare / RSS / 天天基金 / 新浪财经 |

| 服务 | 端口 | 说明 |
|------|------|------|
| investlearn-frontend | 8080 | nginx + Vue SPA + API 代理 |
| investlearn-backend | 8000 | FastAPI |
| investlearn-db | 5432 | PostgreSQL |
| investlearn-redis | 6379 | Redis (缓存) |

---

## 常用命令

### 服务器部署

```bash
cd /opt/invest-learn
git pull origin master 2>/dev/null || {
  git clone https://ghfast.top/https://github.com/Leon-LY/invest-learn.git /tmp/inv
  cp -r /tmp/inv/.[!.]* /tmp/inv/* /opt/invest-learn/ 2>/dev/null
  rm -rf /tmp/inv
}
docker compose -f deploy/docker-compose.prod.yml up -d --build
```

### 缓存管理

```bash
# 重新生成全部大佬数据（预测+追踪+详情）
docker compose -f deploy/docker-compose.prod.yml exec backend python3 -c "
import asyncio
from app.core.cache import cache_delete
from app.tasks.jobs import refresh_expert_tracker, generate_expert_predictions
async def run():
    for k in ['analysis:expert_tracker','analysis:expert_predictions','market:summary']:
        await cache_delete(k)
    await refresh_expert_tracker()
    await generate_expert_predictions()
asyncio.run(run())
"

# 手动触发爬虫
curl -X POST http://localhost:8080/api/v1/crawl/trigger/news
```

---

## 路由表

| 路由 | 功能 |
|------|------|
| `/` | 仪表盘：市场摘要 + 自选 + 新闻 |
| `/diagnosis/:code` | 基金诊断：净值走势 + 风险指标 + 费率 + 投资建议 |
| `/watchlist` | 自选管理（搜索添加 + 懒加载基金） |
| `/analysis` | 智能分析（4个Tab：大佬预测/大佬追踪/组合分析/市场声音） |
| `/analysis/expert/:id` | 大佬详情（持仓/净值/调仓/新闻/投资启示） |
| `/analysis/expert-prediction/:id` | 大佬预测详情（对多条新闻的独立分析） |
| `/news` | 资讯列表（7类筛选：全部/基金/行业/宏观/策略/海外/大佬） |
| `/news/:id` | 资讯详情（Markdown渲染 + DeepSeek AI分析） |
| `/learn` | 知识库（14篇文章 + 40术语 + 10策略） |
| `/learn/glossary` | 术语百科 |
| `/learn/strategies` | 策略库 |
| `/settings` | 设置（主题/数据源/API配置） |

---

## 底部导航

移动端 5 Tab 底部导航（`md:hidden`），桌面端在 AppShell 头部显示内嵌导航链接。

| Tab | 内容 |
|------|------|
| 发现 | 市场摘要 + 自选快照 + 新闻快照 |
| 自选 | 管理自选列表 |
| 分析 | 大佬预测 / 大佬追踪 / 组合分析 / 市场声音 |
| 资讯 | 新闻列表 |
| 学习 | 知识库 |

---

## 定时任务（10个后台Job）

| 周期 | 任务 | 说明 |
|------|------|------|
| 每60秒 | 市场摘要预生成 | Redis缓存，秒出 |
| 每3分钟 | A股行情 spot | 50只核心个股 |
| 每5分钟 | AI分析新新闻 | DeepSeek批量生成 |
| 每15分钟 | 新闻RSS抓取 | 6源+关键词过滤 |
| 每30分钟 | 全球指数 + 大佬预测 | DeepSeek多视角生成 |
| 每2小时 | 大佬追踪数据 | 15位大佬全量爬取 |
| 每天 | 基金净值/ETF/A股日线 | 按固定时间 |

---

## 大佬阵容（15位）

| 类型 | 人物 |
|------|------|
| 基金经理(7) | 张坤、谢治宇、葛兰、侯昊、朱少醒、萧楠、王宗合 |
| 经济学家(3) | 任泽平、洪灏、李蓓 |
| 投资家(3) | 林园、但斌、赵丹阳 |
| 私募/分析师(2) | 邱国鹭、李大霄 |

---

## 关键设计决策

- **Mock 默认关闭**：生产环境 API 无数据时显示"暂无"，不回退假数据
- **所有慢操作预生成 + Redis 缓存**：摘要60s、大佬预测30min、大佬追踪2h、AI分析5min
- **`red_up_green_down` 配色**：中国投资习惯，涨红跌绿（可在设置切换）
- **`<keep-alive :max="5">`**：Tab切换不重复请求
- **BottomNav 全局化**：在 App.vue 层渲染，路由切换不销毁
- **基金懒加载**：6位代码自动从天天基金API抓取
- **截图视觉分析**：通义千问VL，支持小红书/备忘录/持仓截图
- **httpx 同步调用已消除**：全部改用 `asyncio.to_thread` 或 `AsyncClient`
- **N+1 查询已修复**：News 列表和详情使用 JOIN 加载 source name
- **DEBUG 默认关闭**：生产环境 `DEBUG=False`，避免 SQL echo 性能损耗
- **Vite 分包**：echarts / vue-vendor / ui-utils 独立 chunk，优化加载
- **Deep watcher 优化**：图表组件监听 `data.length` 替代 `deep: true`
- **桌面导航**：AppShell 头部内嵌桌面端导航链接，替代仅移动端的 BottomNav

---

## 暗色模式

通过 Tailwind `dark:` 变体 + 全局 `!important` 规则确保对比度。`localStorage.setItem('theme', 'dark')` 切换。

---

## 环境变量 (.env)

```bash
DEEPSEEK_API_KEY=sk-xxx          # DeepSeek API
QWEN_API_KEY=sk-xxx              # 通义千问VL（截图分析）
DB_PASSWORD=xxx                  # 数据库密码
```
