<template>
  <span class="ganzhi-pill" :class="wuxingClass">
    <span class="gan">{{ gan }}</span>
    <span class="zhi">{{ zhi }}</span>
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  gan: string
  zhi: string
}>()

// 天干五行映射
const ganWuxing: Record<string, string> = {
  '甲': 'wood', '乙': 'wood',
  '丙': 'fire', '丁': 'fire',
  '戊': 'earth', '己': 'earth',
  '庚': 'metal', '辛': 'metal',
  '壬': 'water', '癸': 'water',
}

const wuxingClass = computed(() => {
  return ganWuxing[props.gan] || 'earth'
})
</script>

<style scoped>
.ganzhi-pill {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 8px 12px;
  border-radius: 8px;
  border: 1px solid #2a2a35;
  min-width: 48px;
}

.gan {
  font-size: 20px;
  font-weight: 600;
}

.zhi {
  font-size: 16px;
  opacity: 0.8;
}

/* 五行颜色 */
.ganzhi-pill.metal {
  background: rgba(212, 175, 55, 0.1);
  color: #d4af37;
  border-color: rgba(212, 175, 55, 0.3);
}

.ganzhi-pill.wood {
  background: rgba(76, 175, 80, 0.1);
  color: #66bb6a;
  border-color: rgba(76, 175, 80, 0.3);
}

.ganzhi-pill.water {
  background: rgba(44, 95, 138, 0.1);
  color: #5c9fd4;
  border-color: rgba(44, 95, 138, 0.3);
}

.ganzhi-pill.fire {
  background: rgba(192, 57, 43, 0.1);
  color: #e06050;
  border-color: rgba(192, 57, 43, 0.3);
}

.ganzhi-pill.earth {
  background: rgba(160, 120, 60, 0.1);
  color: #c0a060;
  border-color: rgba(160, 120, 60, 0.3);
}
</style>
