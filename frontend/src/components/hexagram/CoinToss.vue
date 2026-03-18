<template>
  <div class="coin-toss">
    <div class="coins-container" ref="coinsRef">
      <div
        v-for="(coin, i) in coins"
        :key="i"
        class="coin"
        :class="{ landed: coin.landed }"
        :ref="(el) => { if (el) coinEls[i] = el as HTMLElement }"
      >
        <div class="coin-inner">
          <div class="coin-front">字</div>
          <div class="coin-back">背</div>
        </div>
      </div>
    </div>
    <p class="toss-label" v-if="resultText">{{ resultText }}</p>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import gsap from 'gsap'

const props = defineProps<{
  /** 每枚铜钱的结果：true=字(正面), false=背(反面) */
  results?: boolean[]
  /** 是否正在投掷 */
  tossing?: boolean
}>()

const emit = defineEmits<{
  'toss-complete': []
}>()

const coinsRef = ref<HTMLElement>()
const coinEls = ref<HTMLElement[]>([])
const coins = ref([
  { landed: false },
  { landed: false },
  { landed: false },
])
const resultText = ref('')

watch(() => props.tossing, (val) => {
  if (val) {
    startToss()
  }
})

function startToss() {
  resultText.value = ''
  coins.value.forEach(c => c.landed = false)

  const results = props.results || [true, true, false]
  const heads = results.filter(r => r).length

  coinEls.value.forEach((el, i) => {
    const targetRotation = results[i] ? 0 : 180 // 字=0, 背=180

    gsap.fromTo(el.querySelector('.coin-inner'),
      {
        rotateY: 0,
        y: -120,
        scale: 0.6,
        opacity: 0,
      },
      {
        rotateY: 720 + targetRotation, // 多转几圈
        y: 0,
        scale: 1,
        opacity: 1,
        duration: 1.2,
        delay: i * 0.15,
        ease: 'bounce.out',
        onComplete: () => {
          coins.value[i].landed = true
          if (i === 2) {
            // 所有铜钱落地
            const labels = ['三背 (老阴 ⚋)', '两背一字 (少阳 ⚊)', '两字一背 (少阴 ⚋)', '三字 (老阳 ⚊)']
            resultText.value = labels[heads]
            emit('toss-complete')
          }
        },
      }
    )
  })
}

onMounted(() => {
  // 初始隐藏
  coinEls.value.forEach(el => {
    const inner = el.querySelector('.coin-inner') as HTMLElement
    if (inner) {
      gsap.set(inner, { opacity: 0 })
    }
  })
})
</script>

<style scoped>
.coin-toss {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.coins-container {
  display: flex;
  gap: 24px;
  perspective: 600px;
}

.coin {
  width: 64px;
  height: 64px;
}

.coin-inner {
  width: 100%;
  height: 100%;
  position: relative;
  transform-style: preserve-3d;
}

.coin-front,
.coin-back {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  font-size: 20px;
  font-weight: 700;
  backface-visibility: hidden;
}

.coin-front {
  background: radial-gradient(circle at 30% 30%, #e8c56a, #a0863d);
  color: #3a2a0a;
  border: 2px solid #c9a84c;
  box-shadow: 0 2px 8px rgba(201, 168, 76, 0.3);
}

.coin-back {
  background: radial-gradient(circle at 30% 30%, #8a7640, #5a4a20);
  color: #c9a84c;
  border: 2px solid #8a7640;
  transform: rotateY(180deg);
  box-shadow: 0 2px 8px rgba(138, 118, 64, 0.3);
}

.coin.landed .coin-inner {
  animation: coin-glow 1s ease-out;
}

@keyframes coin-glow {
  0% { filter: brightness(1.5); }
  100% { filter: brightness(1); }
}

.toss-label {
  color: #a09070;
  font-size: 14px;
  margin-top: 8px;
}
</style>
