<template>
  <div class="divination-view">
    <h2 class="page-title">卜卦问事</h2>
    <p class="page-desc">心诚则灵，虚拟铜钱六次投掷，得出卦象。</p>

    <!-- 输入问题阶段 -->
    <section v-if="stage === 'input'" class="input-section">
      <div class="question-box">
        <label class="question-label">请输入您的问题</label>
        <textarea
          v-model="question"
          class="question-input"
          placeholder="诚心默念您想问的事情..."
          rows="3"
          maxlength="200"
        />
        <div class="input-footer">
          <span class="char-count">{{ question.length }}/200</span>
          <button
            class="cast-btn"
            :disabled="!question.trim()"
            @click="startDivination"
          >
            开始卜卦
          </button>
        </div>
      </div>
    </section>

    <!-- 投掷铜钱阶段 -->
    <section v-if="stage === 'tossing'" class="tossing-section">
      <div class="toss-progress">
        <p class="toss-round">第 {{ currentRound }} 爻 / 共 6 爻</p>
        <div class="progress-dots">
          <span
            v-for="i in 6"
            :key="i"
            class="dot"
            :class="{
              active: i === currentRound,
              done: i < currentRound,
            }"
          />
        </div>
      </div>

      <CoinToss
        :results="currentCoinResults"
        :tossing="isTossing"
        @toss-complete="onTossComplete"
      />

      <button
        v-if="!isTossing && currentRound <= 6"
        class="toss-btn"
        @click="tossCoins"
      >
        {{ currentRound === 1 ? '投掷铜钱' : '继续投掷' }}
      </button>
    </section>

    <!-- 结果展示阶段 -->
    <section v-if="stage === 'result'" class="result-section">
      <div v-if="loading" class="loading">
        <p>正在解析卦象...</p>
      </div>

      <div v-else-if="error" class="error-box">
        <p class="error-text">{{ error }}</p>
        <button class="retry-btn" @click="reset">重新卜卦</button>
      </div>

      <template v-else-if="result">
        <HexagramCard :hexagram="result" />
        <button class="retry-btn" @click="reset">重新卜卦</button>
      </template>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import CoinToss from '@/components/hexagram/CoinToss.vue'
import HexagramCard from '@/components/hexagram/HexagramCard.vue'
import apiClient from '@/api/client'
import type { DivinationResponse } from '@/types/hexagram'

type Stage = 'input' | 'tossing' | 'result'

const stage = ref<Stage>('input')
const question = ref('')
const currentRound = ref(1)
const isTossing = ref(false)
const currentCoinResults = ref<boolean[]>([])
const yaoResults = ref<number[]>([]) // 收集6次投掷结果(6-9)
const result = ref<DivinationResponse | null>(null)
const loading = ref(false)
const error = ref('')

function startDivination() {
  stage.value = 'tossing'
  currentRound.value = 1
  yaoResults.value = []
  result.value = null
  error.value = ''
}

function tossCoins() {
  // 随机生成三枚铜钱结果
  const results = Array.from({ length: 3 }, () => Math.random() > 0.5)
  currentCoinResults.value = results
  isTossing.value = true
}

function onTossComplete() {
  isTossing.value = false
  // 计算本次爻值：字=3, 背=2，三枚之和
  const sum = currentCoinResults.value.reduce((acc, v) => acc + (v ? 3 : 2), 0)
  yaoResults.value.push(sum)

  currentRound.value++

  if (currentRound.value > 6) {
    // 6爻全部完成，提交到后端
    submitDivination()
  }
}

async function submitDivination() {
  stage.value = 'result'
  loading.value = true
  error.value = ''

  try {
    const yaoSequence = yaoResults.value.join('')
    const response = await apiClient.post<DivinationResponse>('/divination/cast', {
      question: question.value,
      method: 'coins',
      yao_sequence: yaoSequence,
    })
    result.value = response.data
  } catch (err: any) {
    // 后端可能未就绪，显示模拟结果
    if (err.code === 'ERR_NETWORK' || err.response?.status === 404) {
      result.value = createMockResult()
    } else {
      error.value = err.response?.data?.detail || '卜卦失败，请稍后重试'
    }
  } finally {
    loading.value = false
  }
}

function createMockResult(): DivinationResponse {
  const yaoSequence = yaoResults.value.join('')
  const changingYao = yaoResults.value
    .map((v, i) => (v === 6 || v === 9) ? i + 1 : -1)
    .filter(i => i >= 0)

  return {
    id: 'mock-' + Date.now(),
    hexagram_num: Math.floor(Math.random() * 64) + 1,
    hexagram_name: '乾为天',
    yao_sequence: yaoSequence,
    changing_yao: changingYao.length > 0 ? changingYao : null,
    changed_hex_num: changingYao.length > 0 ? Math.floor(Math.random() * 64) + 1 : null,
    changed_hex_name: changingYao.length > 0 ? '坤为地' : null,
    luck_score: Math.floor(Math.random() * 100),
    interpretation: '(后端 API 尚未接入，此为模拟结果) 乾卦，元亨利贞。天行健，君子以自强不息。',
  }
}

function reset() {
  stage.value = 'input'
  question.value = ''
  currentRound.value = 1
  yaoResults.value = []
  result.value = null
  error.value = ''
  isTossing.value = false
  currentCoinResults.value = []
}
</script>

<style scoped>
.divination-view {
  max-width: 700px;
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

/* 输入阶段 */
.question-box {
  background: #111118;
  border: 1px solid #2a2a35;
  border-radius: 12px;
  padding: 24px;
}

.question-label {
  display: block;
  color: #a09070;
  font-size: 14px;
  margin-bottom: 12px;
}

.question-input {
  width: 100%;
  background: #0a0a0f;
  border: 1px solid #2a2a35;
  border-radius: 8px;
  padding: 12px 16px;
  color: #e8dcc8;
  font-size: 15px;
  resize: vertical;
  outline: none;
  font-family: inherit;
  transition: border-color 0.2s;
}

.question-input:focus {
  border-color: #c9a84c;
}

.question-input::placeholder {
  color: #665e50;
}

.input-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 12px;
}

.char-count {
  color: #665e50;
  font-size: 13px;
}

.cast-btn {
  background: linear-gradient(135deg, #c9a84c, #a0863d);
  color: #0a0a0f;
  border: none;
  border-radius: 8px;
  padding: 10px 28px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.cast-btn:hover:not(:disabled) {
  box-shadow: 0 0 20px rgba(201, 168, 76, 0.3);
}

.cast-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* 投掷阶段 */
.tossing-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 32px;
}

.toss-progress {
  text-align: center;
}

.toss-round {
  color: #a09070;
  font-size: 15px;
  margin-bottom: 12px;
}

.progress-dots {
  display: flex;
  gap: 8px;
  justify-content: center;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #2a2a35;
  transition: all 0.3s ease;
}

.dot.active {
  background: #c9a84c;
  box-shadow: 0 0 8px rgba(201, 168, 76, 0.5);
}

.dot.done {
  background: #a0863d;
}

.toss-btn {
  background: rgba(201, 168, 76, 0.1);
  color: #c9a84c;
  border: 1px solid rgba(201, 168, 76, 0.3);
  border-radius: 8px;
  padding: 10px 28px;
  font-size: 15px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.toss-btn:hover {
  background: rgba(201, 168, 76, 0.2);
  border-color: #c9a84c;
}

/* 结果阶段 */
.result-section {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.loading {
  text-align: center;
  color: #a09070;
  padding: 48px 0;
}

.error-box {
  text-align: center;
  padding: 32px;
  background: #111118;
  border: 1px solid rgba(192, 57, 43, 0.3);
  border-radius: 12px;
}

.error-text {
  color: #c0392b;
  margin-bottom: 16px;
}

.retry-btn {
  background: rgba(201, 168, 76, 0.1);
  color: #c9a84c;
  border: 1px solid rgba(201, 168, 76, 0.3);
  border-radius: 8px;
  padding: 10px 24px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  align-self: center;
}

.retry-btn:hover {
  background: rgba(201, 168, 76, 0.2);
  border-color: #c9a84c;
}
</style>
