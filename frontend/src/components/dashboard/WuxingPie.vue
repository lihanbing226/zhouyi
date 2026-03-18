<template>
  <div class="pie-chart" ref="chartRef" />
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'

const props = withDefaults(defineProps<{
  /** { 金: number, 木: number, 水: number, 火: number, 土: number } */
  data: Record<string, number>
}>(), {
  data: () => ({}),
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

const fallbackColors = ['#c9a84c', '#5c9fd4', '#66bb6a', '#e06050', '#8d6e63']

function initChart() {
  if (!chartRef.value) return
  chart = echarts.init(chartRef.value)
  updateChart()

  const observer = new ResizeObserver(() => chart?.resize())
  observer.observe(chartRef.value)
}

function updateChart() {
  if (!chart) return

  const entries = Object.entries(props.data)
  if (entries.length === 0) return

  chart.setOption({
    tooltip: {
      trigger: 'item',
      backgroundColor: '#111118',
      borderColor: '#2a2a35',
      textStyle: { color: '#e8dcc8' },
      formatter: '{b}: {c} ({d}%)',
    },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['50%', '50%'],
      data: entries.map(([name, value]) => ({
        name,
        value,
        itemStyle: { color: wuxingColors[name] || fallbackColors[entries.findIndex(([entryName]) => entryName === name) % fallbackColors.length] },
      })),
      label: {
        color: '#a09070',
        fontSize: 13,
        formatter: '{b}\n{d}%',
      },
      labelLine: {
        lineStyle: { color: '#2a2a35' },
      },
      emphasis: {
        scaleSize: 6,
        itemStyle: {
          shadowBlur: 12,
          shadowColor: 'rgba(0,0,0,0.3)',
        },
      },
      animationType: 'scale',
      animationDuration: 1000,
    }],
  })
}

onMounted(() => initChart())
watch(() => props.data, () => updateChart(), { deep: true })
onBeforeUnmount(() => { chart?.dispose(); chart = null })
</script>

<style scoped>
.pie-chart {
  width: 100%;
  height: 300px;
}
</style>
