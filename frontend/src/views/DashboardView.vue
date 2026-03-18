<template>
  <div class="dashboard-view">
    <h2 class="page-title">数据看板</h2>
    <p class="page-desc">卜卦与命盘数据统计，可视化呈现趋势与洞察。</p>

    <!-- 顶部统计卡片 -->
    <div class="stats-row">
      <div class="stat-card" v-for="stat in statCards" :key="stat.label">
        <p class="stat-value">{{ stat.value }}</p>
        <p class="stat-label">{{ stat.label }}</p>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-box">
      <p>正在加载数据...</p>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="error-box">
      <p>{{ error }}</p>
      <button class="retry-btn" @click="fetchData">重试</button>
    </div>

    <!-- 图表区域 -->
    <template v-else>
      <!-- 热力图 -->
      <section class="chart-section">
        <h3 class="section-title">六十四卦热力图</h3>
        <div class="chart-card">
          <HexagramHeatmap :data="heatmapData" />
        </div>
      </section>

      <!-- 四个大图表 2x2 -->
      <div class="charts-grid">
        <section class="chart-section">
          <h3 class="section-title">30 天占卜趋势</h3>
          <div class="chart-card">
            <LuckTrendLine :data="trendData" />
          </div>
        </section>

        <section class="chart-section">
          <h3 class="section-title">运势分布</h3>
          <div class="chart-card">
            <WuxingPie :data="wuxingData" />
          </div>
        </section>

        <section class="chart-section full-width">
          <h3 class="section-title">每日占卜次数</h3>
          <div class="chart-card">
            <UserActivityBar :data="activityData" />
          </div>
        </section>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import HexagramHeatmap from '@/components/dashboard/HexagramHeatmap.vue'
import LuckTrendLine from '@/components/dashboard/LuckTrendLine.vue'
import WuxingPie from '@/components/dashboard/WuxingPie.vue'
import UserActivityBar from '@/components/dashboard/UserActivityBar.vue'
import apiClient from '@/api/client'

interface OverviewResponse {
  today_count: number
  active_users: number
  avg_luck_score: number
}

interface HexagramListResponse {
  hexagrams: Array<{ num: number; name: string }>
}

interface HexagramStatsItem {
  num: number
  name: string
  count: number
}

interface TrendItem {
  date: string
  count: number
}

interface DistributionItem {
  label: string
  count: number
}

const loading = ref(true)
const error = ref('')

// 统计卡片
const statCards = ref([
  { label: '今日卜卦数', value: '—' },
  { label: '活跃用户', value: '—' },
  { label: '运势均值', value: '—' },
])

// 图表数据
const heatmapData = ref<{ name: string; count: number }[]>([])
const trendData = ref<{ date: string; value: number }[]>([])
const wuxingData = ref<Record<string, number>>({})
const activityData = ref<{ date: string; count: number }[]>([])

async function fetchData() {
  loading.value = true
  error.value = ''

  try {
    const [overviewResponse, hexagramListResponse, hexagramStatsResponse, trendResponse, luckDistributionResponse] = await Promise.all([
      apiClient.get<OverviewResponse>('/dashboard/overview'),
      apiClient.get<HexagramListResponse>('/divination/hexagrams', { params: { page: 1, page_size: 64 } }),
      apiClient.get<HexagramStatsItem[]>('/dashboard/hexagram-stats', { params: { days: 30 } }),
      apiClient.get<TrendItem[]>('/dashboard/user-trend', { params: { days: 30 } }),
      apiClient.get<DistributionItem[]>('/dashboard/luck-distribution', { params: { days: 30 } }),
    ])

    const overview = overviewResponse.data
    const allHexagrams = hexagramListResponse.data.hexagrams
    const hexagramCounts = new Map(hexagramStatsResponse.data.map((item) => [item.num, item.count]))
    const trend = trendResponse.data
    const luckDistribution = luckDistributionResponse.data

    statCards.value = [
      { label: '今日卜卦数', value: String(overview.today_count ?? 0) },
      { label: '活跃用户', value: String(overview.active_users ?? 0) },
      { label: '运势均值', value: String(overview.avg_luck_score ?? 0) },
    ]

    heatmapData.value = allHexagrams.map((hexagram) => ({
      name: hexagram.name,
      count: hexagramCounts.get(hexagram.num) ?? 0,
    }))

    trendData.value = trend.map((item) => ({
      date: item.date,
      value: item.count,
    }))

    wuxingData.value = Object.fromEntries(
      luckDistribution.map((item) => [item.label, item.count]),
    )

    activityData.value = trend.slice(-14)
  } catch (err: any) {
    if (err.code === 'ERR_NETWORK' || err.response?.status === 404) {
      loadMockData()
    } else {
      error.value = '获取看板数据失败'
    }
  } finally {
    loading.value = false
  }
}

function loadMockData() {
  statCards.value = [
    { label: '今日卜卦数', value: '42' },
    { label: '活跃用户', value: '18' },
    { label: '运势均值', value: '68' },
  ]

  // 64卦热力图模拟
  const hexNames = [
    '乾','坤','屯','蒙','需','讼','师','比',
    '小畜','履','泰','否','同人','大有','谦','豫',
    '随','蛊','临','观','噬嗑','贲','剥','复',
    '无妄','大畜','颐','大过','坎','离','咸','恒',
    '遁','大壮','晋','明夷','家人','睽','蹇','解',
    '损','益','夬','姤','萃','升','困','井',
    '革','鼎','震','艮','渐','归妹','丰','旅',
    '巽','兑','涣','节','中孚','小过','既济','未济',
  ]
  heatmapData.value = hexNames.map(name => ({
    name,
    count: Math.floor(Math.random() * 50),
  }))

  // 30天趋势模拟
  const today = new Date()
  trendData.value = Array.from({ length: 30 }, (_, i) => {
    const d = new Date(today)
    d.setDate(d.getDate() - 29 + i)
    return {
      date: `${d.getMonth() + 1}/${d.getDate()}`,
      value: Math.floor(1 + Math.random() * 40),
    }
  })

  wuxingData.value = {
    '大凶 (1-20)': 8,
    '小凶 (21-40)': 15,
    '平 (41-60)': 22,
    '吉 (61-80)': 18,
    '大吉 (81-100)': 12,
  }

  // 每日活动模拟
  activityData.value = Array.from({ length: 14 }, (_, i) => {
    const d = new Date(today)
    d.setDate(d.getDate() - 13 + i)
    return {
      date: `${d.getMonth() + 1}/${d.getDate()}`,
      count: Math.floor(5 + Math.random() * 30),
    }
  })
}

onMounted(() => fetchData())
</script>

<style scoped>
.dashboard-view {
  max-width: 1100px;
  margin: 0 auto;
}

.page-title {
  font-size: 28px;
  color: #c9a84c;
  margin-bottom: 8px;
}

.page-desc {
  color: #a09070;
  margin-bottom: 24px;
}

/* 统计卡片 */
.stats-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: #111118;
  border: 1px solid #2a2a35;
  border-radius: 12px;
  padding: 20px;
  text-align: center;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #c9a84c;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #a09070;
}

/* 加载/错误 */
.loading-box,
.error-box {
  text-align: center;
  padding: 48px 0;
  color: #a09070;
}

.retry-btn {
  margin-top: 12px;
  background: rgba(201, 168, 76, 0.1);
  color: #c9a84c;
  border: 1px solid rgba(201, 168, 76, 0.3);
  border-radius: 8px;
  padding: 8px 20px;
  cursor: pointer;
}

/* 图表区域 */
.chart-section {
  margin-bottom: 24px;
}

.section-title {
  font-size: 16px;
  color: #e8dcc8;
  margin-bottom: 12px;
}

.chart-card {
  background: #111118;
  border: 1px solid #2a2a35;
  border-radius: 12px;
  padding: 16px;
}

.charts-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.charts-grid .full-width {
  grid-column: 1 / -1;
}

@media (max-width: 768px) {
  .stats-row {
    grid-template-columns: 1fr;
  }

  .charts-grid {
    grid-template-columns: 1fr;
  }
}
</style>
