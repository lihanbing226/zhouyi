<template>
  <div class="bazi-view">
    <h2 class="page-title">八字命盘</h2>
    <p class="page-desc">输入出生时辰，排出四柱八字，分析五行格局。</p>

    <!-- 输入表单 -->
    <section v-if="!result" class="input-section">
      <div class="form-card">
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">出生日期</label>
            <input
              v-model="form.date"
              type="date"
              class="form-input"
              required
            />
          </div>
          <div class="form-group">
            <label class="form-label">出生时辰</label>
            <select v-model="form.hour" class="form-input">
              <option value="">请选择</option>
              <option v-for="h in hours" :key="h.value" :value="h.value">
                {{ h.label }}
              </option>
            </select>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label class="form-label">性别</label>
            <div class="radio-group">
              <label class="radio-item" :class="{ selected: form.gender === 'M' }">
                <input type="radio" v-model="form.gender" value="M" />
                <span>男</span>
              </label>
              <label class="radio-item" :class="{ selected: form.gender === 'F' }">
                <input type="radio" v-model="form.gender" value="F" />
                <span>女</span>
              </label>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">出生地点（可选）</label>
            <input
              v-model="form.location"
              type="text"
              class="form-input"
              placeholder="如：北京"
            />
          </div>
        </div>

        <div class="form-actions">
          <button
            class="submit-btn"
            :disabled="!canSubmit || loading"
            @click="calculateBazi"
          >
            {{ loading ? '计算中...' : '计算命盘' }}
          </button>
        </div>

        <p v-if="error" class="error-msg">{{ error }}</p>
      </div>
    </section>

    <!-- 结果展示 -->
    <section v-if="result" class="result-section">
      <BaziChart :bazi="result" />

      <div class="radar-section">
        <h3 class="section-title">五行分布</h3>
        <WuxingRadar :scores="result.wuxing_score" />
      </div>

      <div class="analysis-card" v-if="result.analysis">
        <h3 class="section-title">命盘分析</h3>
        <p class="analysis-text">{{ result.analysis }}</p>
      </div>

      <div class="outlook-card" v-if="result.luck_outlook">
        <h3 class="section-title">运势展望</h3>
        <p class="outlook-text">{{ result.luck_outlook }}</p>
      </div>

      <button class="reset-btn" @click="resetForm">重新排盘</button>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import BaziChart from '@/components/bazi/BaziChart.vue'
import WuxingRadar from '@/components/bazi/WuxingRadar.vue'
import apiClient from '@/api/client'
import type { BaziResponse } from '@/types/bazi'

const hours = [
  { value: '23:00', label: '子时 (23:00-01:00)' },
  { value: '01:00', label: '丑时 (01:00-03:00)' },
  { value: '03:00', label: '寅时 (03:00-05:00)' },
  { value: '05:00', label: '卯时 (05:00-07:00)' },
  { value: '07:00', label: '辰时 (07:00-09:00)' },
  { value: '09:00', label: '巳时 (09:00-11:00)' },
  { value: '11:00', label: '午时 (11:00-13:00)' },
  { value: '13:00', label: '未时 (13:00-15:00)' },
  { value: '15:00', label: '申时 (15:00-17:00)' },
  { value: '17:00', label: '酉时 (17:00-19:00)' },
  { value: '19:00', label: '戌时 (19:00-21:00)' },
  { value: '21:00', label: '亥时 (21:00-23:00)' },
]

const form = reactive({
  date: '',
  hour: '',
  gender: 'M' as 'M' | 'F',
  location: '',
})

const result = ref<BaziResponse | null>(null)
const loading = ref(false)
const error = ref('')

const canSubmit = computed(() => form.date && form.hour)

async function calculateBazi() {
  loading.value = true
  error.value = ''

  try {
    const datetime = new Date(`${form.date}T${form.hour}:00`)
    const response = await apiClient.post<BaziResponse>('/bazi/calculate', {
      birth_datetime: datetime.toISOString(),
      gender: form.gender,
      location: form.location || undefined,
    })
    result.value = response.data
  } catch (err: any) {
    if (err.code === 'ERR_NETWORK' || err.response?.status === 404) {
      result.value = createMockBazi()
    } else {
      error.value = err.response?.data?.detail || '计算失败，请稍后重试'
    }
  } finally {
    loading.value = false
  }
}

function createMockBazi(): BaziResponse {
  return {
    id: 'mock-' + Date.now(),
    year_gan: '甲', year_zhi: '子',
    month_gan: '丙', month_zhi: '寅',
    day_gan: '庚', day_zhi: '午',
    hour_gan: '壬', hour_zhi: '申',
    day_master: '庚金',
    strength: '身强',
    wuxing_score: { '金': 35, '木': 15, '水': 20, '火': 18, '土': 12 },
    analysis: '(后端 API 尚未接入，此为模拟结果) 日主庚金生于寅月，虽金不当令，但得时柱壬水泄秀，年柱甲木偏财透出。',
    luck_outlook: '近期运势平稳，宜守不宜攻。',
  }
}

function resetForm() {
  result.value = null
  error.value = ''
}
</script>

<style scoped>
.bazi-view {
  max-width: 800px;
  margin: 0 auto;
}

.page-title {
  font-size: 28px;
  color: #c9a84c;
  margin-bottom: 8px;
}

.page-desc {
  color: #a09070;
  margin-bottom: 32px;
}

/* 表单 */
.form-card {
  background: #111118;
  border: 1px solid #2a2a35;
  border-radius: 12px;
  padding: 24px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-label {
  font-size: 14px;
  color: #a09070;
}

.form-input {
  background: #0a0a0f;
  border: 1px solid #2a2a35;
  border-radius: 8px;
  padding: 10px 14px;
  color: #e8dcc8;
  font-size: 15px;
  outline: none;
  transition: border-color 0.2s;
  font-family: inherit;
}

.form-input:focus {
  border-color: #c9a84c;
}

.radio-group {
  display: flex;
  gap: 12px;
}

.radio-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: 1px solid #2a2a35;
  border-radius: 8px;
  cursor: pointer;
  color: #a09070;
  font-size: 14px;
  transition: all 0.2s;
}

.radio-item input {
  display: none;
}

.radio-item.selected {
  border-color: #c9a84c;
  color: #c9a84c;
  background: rgba(201, 168, 76, 0.08);
}

.form-actions {
  display: flex;
  justify-content: center;
  margin-top: 8px;
}

.submit-btn {
  background: linear-gradient(135deg, #c9a84c, #a0863d);
  color: #0a0a0f;
  border: none;
  border-radius: 8px;
  padding: 10px 36px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.submit-btn:hover:not(:disabled) {
  box-shadow: 0 0 20px rgba(201, 168, 76, 0.3);
}

.submit-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.error-msg {
  color: #c0392b;
  text-align: center;
  margin-top: 12px;
  font-size: 14px;
}

/* 结果 */
.result-section {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.radar-section {
  background: #111118;
  border: 1px solid #2a2a35;
  border-radius: 12px;
  padding: 24px;
}

.section-title {
  font-size: 16px;
  color: #c9a84c;
  margin-bottom: 16px;
}

.analysis-card,
.outlook-card {
  background: #111118;
  border: 1px solid #2a2a35;
  border-radius: 12px;
  padding: 24px;
}

.analysis-text,
.outlook-text {
  color: #c0b8a8;
  font-size: 14px;
  line-height: 1.8;
}

.reset-btn {
  align-self: center;
  background: rgba(201, 168, 76, 0.1);
  color: #c9a84c;
  border: 1px solid rgba(201, 168, 76, 0.3);
  border-radius: 8px;
  padding: 10px 24px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.reset-btn:hover {
  background: rgba(201, 168, 76, 0.2);
  border-color: #c9a84c;
}

@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>
