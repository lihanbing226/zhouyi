<template>
  <div class="wuxing-radar" ref="chartRef" :style="{ width: width + 'px', height: height + 'px' }" />
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'

const props = withDefaults(defineProps<{
  /** 五行分数 { 金: number, 木: number, 水: number, 火: number, 土: number } */
  scores: Record<string, number>
  width?: number
  height?: number
}>(), {
  width: 360,
  height: 360,
})

const chartRef = ref<HTMLElement>()
let chart: echarts.ECharts | null = null

const wuxingColors: Record<string, string> = {
  '金': '#d4af37',
  '木': '#66bb6a',
  '水': '#5c9fd4',
  '火': '#e06050',
  '土': '#c0a060',
}

const indicators = ['金', '木', '水', '火', '土']

function initChart() {
  if (!chartRef.value) return
  chart = echarts.init(chartRef.value)
  updateChart()
}

function updateChart() {
  if (!chart) return

  const values = indicators.map(k => props.scores[k] || 0)
  const maxVal = Math.max(...values, 10)

  chart.setOption({
    radar: {
      indicator: indicators.map(name => ({
        name,
        max: maxVal,
        color: wuxingColors[name],
      })),
      shape: 'polygon',
      splitNumber: 4,
      axisName: {
        fontSize: 14,
        fontWeight: 'bold',
      },
      splitArea: {
        areaStyle: {
          color: ['rgba(201,168,76,0.02)', 'rgba(201,168,76,0.04)', 'rgba(201,168,76,0.06)', 'rgba(201,168,76,0.08)'],
        },
      },
      splitLine: {
        lineStyle: {
          color: 'rgba(201,168,76,0.15)',
        },
      },
      axisLine: {
        lineStyle: {
          color: 'rgba(201,168,76,0.2)',
        },
      },
    },
    series: [{
      type: 'radar',
      data: [{
        value: values,
        name: '五行分布',
        lineStyle: {
          color: '#c9a84c',
          width: 2,
        },
        areaStyle: {
          color: 'rgba(201,168,76,0.15)',
        },
        itemStyle: {
          color: '#c9a84c',
          borderColor: '#e8c56a',
          borderWidth: 2,
        },
        symbol: 'circle',
        symbolSize: 8,
      }],
      animationDuration: 1200,
      animationEasing: 'cubicOut',
    }],
    tooltip: {
      trigger: 'item',
      backgroundColor: '#111118',
      borderColor: '#2a2a35',
      textStyle: {
        color: '#e8dcc8',
      },
    },
  })
}

onMounted(() => {
  initChart()
})

watch(() => props.scores, () => {
  updateChart()
}, { deep: true })

onBeforeUnmount(() => {
  chart?.dispose()
  chart = null
})
</script>

<style scoped>
.wuxing-radar {
  margin: 0 auto;
}
</style>
