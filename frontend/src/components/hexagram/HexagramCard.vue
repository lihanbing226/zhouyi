<template>
  <div class="hexagram-card">
    <div class="card-header">
      <HexagramLines
        :yao-sequence="hexagram.yao_sequence"
        :changing-yao="hexagram.changing_yao || []"
        :width="140"
        :height="160"
      />
      <div class="card-info">
        <h3 class="hex-name">{{ hexagram.hexagram_name }}</h3>
        <p class="hex-num">第 {{ hexagram.hexagram_num }} 卦</p>
        <div class="luck-score" v-if="hexagram.luck_score !== undefined">
          <span class="luck-label">吉凶指数</span>
          <div class="luck-bar">
            <div
              class="luck-fill"
              :style="{ width: `${hexagram.luck_score}%` }"
              :class="luckClass"
            />
          </div>
          <span class="luck-value">{{ hexagram.luck_score }}</span>
        </div>
      </div>
    </div>

    <div class="card-body" v-if="hexagram.interpretation">
      <h4 class="section-title">卦象解读</h4>
      <p class="interpretation-text">{{ hexagram.interpretation }}</p>
    </div>

    <div class="card-changed" v-if="hexagram.changed_hex_name">
      <h4 class="section-title">变卦</h4>
      <p class="changed-name">{{ hexagram.changed_hex_name }} (第 {{ hexagram.changed_hex_num }} 卦)</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { DivinationResponse } from '@/types/hexagram'
import HexagramLines from './HexagramLines.vue'

const props = defineProps<{
  hexagram: DivinationResponse
}>()

const luckClass = computed(() => {
  const score = props.hexagram.luck_score
  if (score >= 70) return 'luck-good'
  if (score >= 40) return 'luck-neutral'
  return 'luck-bad'
})
</script>

<style scoped>
.hexagram-card {
  background: #111118;
  border: 1px solid #2a2a35;
  border-radius: 12px;
  padding: 24px;
  transition: border-color 0.3s ease;
}

.hexagram-card:hover {
  border-color: rgba(201, 168, 76, 0.3);
}

.card-header {
  display: flex;
  gap: 24px;
  align-items: center;
  margin-bottom: 20px;
}

.card-info {
  flex: 1;
}

.hex-name {
  font-size: 24px;
  color: #c9a84c;
  margin-bottom: 4px;
}

.hex-num {
  color: #a09070;
  font-size: 14px;
  margin-bottom: 16px;
}

.luck-score {
  display: flex;
  align-items: center;
  gap: 8px;
}

.luck-label {
  color: #a09070;
  font-size: 13px;
  white-space: nowrap;
}

.luck-bar {
  flex: 1;
  height: 6px;
  background: #2a2a35;
  border-radius: 3px;
  overflow: hidden;
}

.luck-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.8s ease;
}

.luck-good { background: #c9a84c; }
.luck-neutral { background: #2c5f8a; }
.luck-bad { background: #c0392b; }

.luck-value {
  color: #e8dcc8;
  font-size: 14px;
  font-weight: 600;
  min-width: 24px;
  text-align: right;
}

.section-title {
  font-size: 15px;
  color: #c9a84c;
  margin-bottom: 8px;
  padding-top: 16px;
  border-top: 1px solid #2a2a35;
}

.interpretation-text {
  color: #c0b8a8;
  font-size: 14px;
  line-height: 1.8;
}

.changed-name {
  color: #c0392b;
  font-size: 15px;
}
</style>
