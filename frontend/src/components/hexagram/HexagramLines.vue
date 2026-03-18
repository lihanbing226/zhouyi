<template>
  <svg
    :width="width"
    :height="height"
    :viewBox="`0 0 ${width} ${height}`"
    class="hexagram-lines"
  >
    <g v-for="(yao, i) in yaoLines" :key="i" :transform="`translate(0, ${(5 - i) * lineSpacing})`">
      <!-- 阳爻：一条完整横线 -->
      <template v-if="yao.type === 'yang'">
        <line
          :x1="padding"
          y1="0"
          :x2="width - padding"
          y2="0"
          :stroke="yao.changing ? '#c0392b' : '#c9a84c'"
          :stroke-width="strokeWidth"
          stroke-linecap="round"
          :class="{ changing: yao.changing }"
          :ref="(el) => setLineRef(i, el)"
        />
      </template>
      <!-- 阴爻：中间断开的两段线 -->
      <template v-else>
        <line
          :x1="padding"
          y1="0"
          :x2="width / 2 - gapHalf"
          y2="0"
          :stroke="yao.changing ? '#c0392b' : '#c9a84c'"
          :stroke-width="strokeWidth"
          stroke-linecap="round"
          :class="{ changing: yao.changing }"
          :ref="(el) => setLineRef(i, el)"
        />
        <line
          :x1="width / 2 + gapHalf"
          y1="0"
          :x2="width - padding"
          y2="0"
          :stroke="yao.changing ? '#c0392b' : '#c9a84c'"
          :stroke-width="strokeWidth"
          stroke-linecap="round"
          :class="{ changing: yao.changing }"
        />
      </template>
    </g>
  </svg>
</template>

<script setup lang="ts">
import { computed, watch, nextTick } from 'vue'
import gsap from 'gsap'

const props = withDefaults(defineProps<{
  /** 爻序列字符串，从下到上 6 个数字 (6=老阴, 7=少阳, 8=少阴, 9=老阳) */
  yaoSequence?: string
  /** 变爻位置列表 (1-based, 从下到上) */
  changingYao?: number[]
  /** 是否播放绘制动画 */
  animate?: boolean
  width?: number
  height?: number
}>(), {
  yaoSequence: '',
  changingYao: () => [],
  animate: false,
  width: 160,
  height: 180,
})

const padding = 20
const strokeWidth = 5
const gapHalf = 10
const lineSpacing = computed(() => (props.height - 20) / 6)

const lineRefs: Record<number, Element | null> = {}
function setLineRef(i: number, el: unknown) {
  lineRefs[i] = el as Element | null
}

const yaoLines = computed(() => {
  if (!props.yaoSequence) return []
  return props.yaoSequence.split('').map((ch, i) => {
    const num = parseInt(ch)
    const isYang = num === 7 || num === 9 // 7=少阳, 9=老阳
    const isChanging = props.changingYao.includes(i + 1)
    return {
      type: isYang ? 'yang' : 'yin',
      changing: isChanging,
    }
  })
})

watch(() => props.animate, (val) => {
  if (val && props.yaoSequence) {
    nextTick(() => animateLines())
  }
})

function animateLines() {
  Object.values(lineRefs).forEach((el) => {
    if (!el) return
    const line = el as SVGLineElement
    const length = line.getTotalLength?.() || 120
    gsap.fromTo(line,
      { strokeDasharray: length, strokeDashoffset: length },
      { strokeDashoffset: 0, duration: 0.5, ease: 'power2.out' }
    )
  })
}
</script>

<style scoped>
.hexagram-lines {
  display: block;
}

.changing {
  animation: pulse-glow 1.5s ease-in-out infinite;
}

@keyframes pulse-glow {
  0%, 100% { filter: drop-shadow(0 0 2px #c0392b); opacity: 1; }
  50% { filter: drop-shadow(0 0 8px #c0392b); opacity: 0.8; }
}
</style>
