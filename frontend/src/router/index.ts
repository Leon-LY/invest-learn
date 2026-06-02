import { createRouter, createWebHashHistory, RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('@/views/dashboard/DashboardView.vue'),
    meta: { title: '市场概览', layout: 'dashboard' },
  },
  {
    path: '/diagnosis',
    name: 'FundDiagnosis',
    component: () => import('@/views/market/FundDiagnosisView.vue'),
    meta: { title: '基金诊断', layout: 'default' },
  },
  {
    path: '/diagnosis/:code',
    name: 'FundDiagnosisCode',
    component: () => import('@/views/market/FundDiagnosisView.vue'),
    meta: { title: '基金诊断', layout: 'default' },
  },
  {
    path: '/market/:code',
    name: 'StockDetail',
    component: () => import('@/views/market/StockDetailView.vue'),
    meta: { title: '个股详情', layout: 'fullscreen' },
  },
  {
    path: '/fund/:code',
    name: 'FundDetail',
    component: () => import('@/views/market/FundDetailView.vue'),
    meta: { title: '基金详情', layout: 'default' },
  },
  {
    path: '/sectors',
    name: 'Sectors',
    component: () => import('@/views/market/SectorView.vue'),
    meta: { title: '板块分析', layout: 'default' },
  },
  {
    path: '/capital-flow',
    name: 'CapitalFlow',
    component: () => import('@/views/market/CapitalFlowView.vue'),
    meta: { title: '资金流向', layout: 'default' },
  },
  {
    path: '/watchlist',
    name: 'Watchlist',
    component: () => import('@/views/watchlist/WatchlistView.vue'),
    meta: { title: '自选列表', layout: 'default' },
  },
  {
    path: '/news',
    name: 'NewsList',
    component: () => import('@/views/news/NewsListView.vue'),
    meta: { title: '财经新闻', layout: 'default' },
  },
  {
    path: '/news/:id',
    name: 'NewsDetail',
    component: () => import('@/views/news/NewsDetailView.vue'),
    meta: { title: '新闻详情', layout: 'article' },
  },
  {
    path: '/learn',
    name: 'KnowledgeBase',
    component: () => import('@/views/learn/KnowledgeBase.vue'),
    meta: { title: '投资知识库', layout: 'default' },
  },
  {
    path: '/learn/glossary',
    name: 'Glossary',
    component: () => import('@/views/learn/GlossaryView.vue'),
    meta: { title: '术语百科', layout: 'default' },
  },
  {
    path: '/learn/strategies',
    name: 'Strategies',
    component: () => import('@/views/learn/StrategiesView.vue'),
    meta: { title: '投资策略库', layout: 'default' },
  },
  {
    path: '/learn/:slug',
    name: 'Article',
    component: () => import('@/views/learn/ArticleView.vue'),
    meta: { title: '文章阅读', layout: 'article' },
  },
  {
    path: '/portfolio',
    name: 'Portfolio',
    component: () => import('@/views/portfolio/SimPortfolioView.vue'),
    meta: { title: '模拟交易', layout: 'dashboard' },
  },
  {
    path: '/compare',
    name: 'Compare',
    component: () => import('@/views/analysis/ComparisonView.vue'),
    meta: { title: '对比分析', layout: 'default' },
  },
  {
    path: '/analysis',
    name: 'Analysis',
    component: () => import('@/views/analysis/AnalysisView.vue'),
    meta: { title: '智能分析', layout: 'default' },
  },
  {
    path: '/analysis/expert/:id',
    name: 'ExpertDetail',
    component: () => import('@/views/analysis/ExpertDetailView.vue'),
    meta: { title: '大佬详情', layout: 'default' },
  },
  {
    path: '/portfolio-analysis',
    name: 'PortfolioAnalysis',
    component: () => import('@/views/analysis/PortfolioAnalysis.vue'),
    meta: { title: '组合分析', layout: 'default' },
  },
  {
    path: '/analysis/expert-prediction/:id',
    name: 'ExpertPredictionDetail',
    component: () => import('@/views/analysis/ExpertPredictionDetail.vue'),
    meta: { title: '大佬预测详情', layout: 'default' },
  },
  {
    path: '/screener',
    name: 'Screener',
    component: () => import('@/views/analysis/ScreenerView.vue'),
    meta: { title: '股票筛选', layout: 'default' },
  },
  {
    path: '/journal',
    name: 'Journal',
    component: () => import('@/views/journal/JournalView.vue'),
    meta: { title: '投资笔记', layout: 'default' },
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/views/settings/SettingsView.vue'),
    meta: { title: '设置', layout: 'default' },
  },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  },
})

router.beforeEach((to) => {
  document.title = `${to.meta.title || '远见'} — 洞察趋势，智选未来`
})

export default router
