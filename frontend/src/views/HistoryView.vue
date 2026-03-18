<template>
  <div class="history-view">
    <h2 class="page-title">历史记录</h2>
    <p class="page-desc">查看您的卜卦与八字历史记录。</p>

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <div class="filter-tabs">
        <button
          v-for="tab in tabs"
          :key="tab.value"
          class="filter-tab"
          :class="{ active: currentTab === tab.value }"
          @click="currentTab = tab.value; currentPage = 1; fetchHistory()"
        >
          {{ tab.label }}
        </button>
      </div>
      <select v-model="sortBy" class="sort-select" @change="currentPage = 1; fetchHistory()">
        <option value="newest">最新优先</option>
        <option value="oldest">最早优先</option>
      </select>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-box">
      <p>正在加载...</p>
    </div>

    <!-- 空状态 -->
    <div v-else-if="records.length === 0" class="empty-box">
      <p class="empty-text">暂无历史记录</p>
      <router-link to="/divination" class="empty-action">去卜卦</router-link>
    </div>

    <!-- 记录列表 -->
    <div v-else class="record-list">
      <div
        v-for="record in records"
        :key="record.id"
        class="record-card"
      >
        <div class="record-header">
          <span class="record-type" :class="record.type">
            {{ record.type === 'divination' ? '卜卦' : '八字' }}
          </span>
          <span class="record-date">{{ record.created_at }}</span>
        </div>

        <div class="record-body">
          <h4 class="record-title">{{ record.title }}</h4>
          <p class="record-summary">{{ record.summary }}</p>
        </div>

        <div class="record-actions">
          <button class="action-btn view-btn" @click="viewDetail(record)">查看</button>
          <button class="action-btn delete-btn" @click="deleteRecord(record.id)">删除</button>
        </div>
      </div>
    </div>

    <!-- 分页 -->
    <div v-if="totalPages > 1" class="pagination">
      <button
        class="page-btn"
        :disabled="currentPage <= 1"
        @click="currentPage--; fetchHistory()"
      >
        上一页
      </button>
      <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
      <button
        class="page-btn"
        :disabled="currentPage >= totalPages"
        @click="currentPage++; fetchHistory()"
      >
        下一页
      </button>
    </div>

    <!-- 详情弹窗 -->
    <Teleport to="body">
      <div v-if="detailRecord" class="modal-overlay" @click.self="detailRecord = null">
        <div class="modal-content">
          <div class="modal-header">
            <h3>{{ detailRecord.title }}</h3>
            <button class="modal-close" @click="detailRecord = null">&times;</button>
          </div>
          <div class="modal-body">
            <p class="detail-type">
              类型：{{ detailRecord.type === 'divination' ? '卜卦' : '八字' }}
            </p>
            <p class="detail-date">时间：{{ detailRecord.created_at }}</p>
            <p class="detail-summary">{{ detailRecord.summary }}</p>
            <p v-if="detailRecord.detail" class="detail-text">{{ detailRecord.detail }}</p>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import apiClient from '@/api/client'

interface HistoryRecord {
  id: string
  type: 'divination' | 'bazi'
  title: string
  summary: string
  detail?: string
  created_at: string
}

interface HistoryListResponse {
  items: HistoryRecord[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

const tabs = [
  { value: 'all', label: '全部' },
  { value: 'divination', label: '卜卦' },
  { value: 'bazi', label: '八字' },
]

const currentTab = ref('all')
const sortBy = ref('newest')
const loading = ref(false)
const records = ref<HistoryRecord[]>([])
const currentPage = ref(1)
const totalPages = ref(1)
const pageSize = 10
const detailRecord = ref<HistoryRecord | null>(null)

async function fetchHistory() {
  loading.value = true

  try {
    const response = await apiClient.get<HistoryListResponse>('/history', {
      params: {
        page: currentPage.value,
        page_size: pageSize,
        sort: sortBy.value,
        type: currentTab.value,
      },
    })

    records.value = response.data.items.map((record) => ({
      ...record,
      created_at: formatDate(record.created_at),
    }))
    totalPages.value = response.data.total_pages || 1
  } catch (err: any) {
    if (err.code === 'ERR_NETWORK' || err.response?.status === 404) {
      loadMockRecords()
    } else {
      records.value = []
      totalPages.value = 1
    }
  } finally {
    loading.value = false
  }
}

function formatDate(value: string): string {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) {
    return value
  }

  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hour = String(date.getHours()).padStart(2, '0')
  const minute = String(date.getMinutes()).padStart(2, '0')
  return `${year}-${month}-${day} ${hour}:${minute}`
}

function loadMockRecords() {
  const mockData: HistoryRecord[] = [
    {
      id: '1',
      type: 'divination',
      title: '乾为天',
      summary: '问事业发展：元亨利贞，天行健君子以自强不息。',
      detail: '乾卦六爻皆阳，为纯阳之卦。问事业发展前景光明，宜积极进取。',
      created_at: '2026-03-12 14:30',
    },
    {
      id: '2',
      type: 'bazi',
      title: '甲子年 丙寅月 庚午日 壬申时',
      summary: '日主庚金，身强格局，五行偏金。',
      detail: '庚金生于寅月，虽不当令但得年时之助，五行以金水为主。',
      created_at: '2026-03-11 10:15',
    },
    {
      id: '3',
      type: 'divination',
      title: '坤为地',
      summary: '问感情走向：地势坤，君子以厚德载物。',
      created_at: '2026-03-10 16:45',
    },
  ]

  if (currentTab.value !== 'all') {
      records.value = mockData.filter(r => r.type === currentTab.value)
  } else {
    records.value = mockData
  }

  if (sortBy.value === 'oldest') {
    records.value.reverse()
  }

  totalPages.value = 1
}

function viewDetail(record: HistoryRecord) {
  detailRecord.value = record
}

async function deleteRecord(id: string) {
  const record = records.value.find((item) => item.id === id)
  if (!record) {
    return
  }

  try {
    await apiClient.delete(`/history/${record.type}/${id}`)
  } catch {
    // 后端未就绪时静默处理
  }

  if (detailRecord.value?.id === id) {
    detailRecord.value = null
  }

  records.value = records.value.filter(r => r.id !== id)
  await fetchHistory()
}

onMounted(() => fetchHistory())
</script>

<style scoped>
.history-view {
  max-width: 900px;
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

/* 筛选栏 */
.filter-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.filter-tabs {
  display: flex;
  gap: 4px;
}

.filter-tab {
  background: none;
  border: 1px solid #2a2a35;
  border-radius: 6px;
  padding: 6px 16px;
  color: #a09070;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-tab.active {
  background: rgba(201, 168, 76, 0.12);
  border-color: #c9a84c;
  color: #c9a84c;
}

.sort-select {
  background: #111118;
  border: 1px solid #2a2a35;
  border-radius: 6px;
  padding: 6px 12px;
  color: #a09070;
  font-size: 14px;
  outline: none;
  font-family: inherit;
}

/* 加载/空状态 */
.loading-box,
.empty-box {
  text-align: center;
  padding: 48px 0;
  color: #665e50;
}

.empty-text {
  margin-bottom: 16px;
}

.empty-action {
  color: #c9a84c;
  border: 1px solid rgba(201, 168, 76, 0.3);
  padding: 8px 20px;
  border-radius: 6px;
  text-decoration: none;
}

/* 记录列表 */
.record-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.record-card {
  background: #111118;
  border: 1px solid #2a2a35;
  border-radius: 10px;
  padding: 16px 20px;
  transition: border-color 0.2s;
}

.record-card:hover {
  border-color: rgba(201, 168, 76, 0.2);
}

.record-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.record-type {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 4px;
}

.record-type.divination {
  background: rgba(201, 168, 76, 0.12);
  color: #c9a84c;
}

.record-type.bazi {
  background: rgba(44, 95, 138, 0.12);
  color: #5c9fd4;
}

.record-date {
  color: #665e50;
  font-size: 13px;
}

.record-title {
  font-size: 16px;
  color: #e8dcc8;
  margin-bottom: 4px;
}

.record-summary {
  color: #a09070;
  font-size: 14px;
  line-height: 1.6;
}

.record-actions {
  display: flex;
  gap: 8px;
  margin-top: 12px;
  justify-content: flex-end;
}

.action-btn {
  border: none;
  border-radius: 6px;
  padding: 5px 14px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.view-btn {
  background: rgba(201, 168, 76, 0.1);
  color: #c9a84c;
}

.view-btn:hover {
  background: rgba(201, 168, 76, 0.2);
}

.delete-btn {
  background: rgba(192, 57, 43, 0.1);
  color: #c0392b;
}

.delete-btn:hover {
  background: rgba(192, 57, 43, 0.2);
}

/* 分页 */
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-top: 24px;
}

.page-btn {
  background: rgba(201, 168, 76, 0.1);
  color: #c9a84c;
  border: 1px solid rgba(201, 168, 76, 0.3);
  border-radius: 6px;
  padding: 6px 16px;
  font-size: 14px;
  cursor: pointer;
}

.page-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.page-info {
  color: #a09070;
  font-size: 14px;
}

/* 详情弹窗 */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 24px;
}

.modal-content {
  background: #111118;
  border: 1px solid #2a2a35;
  border-radius: 12px;
  width: 100%;
  max-width: 560px;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid #2a2a35;
}

.modal-header h3 {
  color: #c9a84c;
  font-size: 18px;
}

.modal-close {
  background: none;
  border: none;
  color: #a09070;
  font-size: 24px;
  cursor: pointer;
}

.modal-close:hover {
  color: #e8dcc8;
}

.modal-body {
  padding: 24px;
}

.detail-type,
.detail-date {
  color: #a09070;
  font-size: 14px;
  margin-bottom: 8px;
}

.detail-summary {
  color: #c0b8a8;
  font-size: 15px;
  line-height: 1.7;
  margin-top: 16px;
}

.detail-text {
  color: #c0b8a8;
  font-size: 14px;
  line-height: 1.8;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #2a2a35;
}
</style>
