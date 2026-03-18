<template>
  <div class="trend-chart" ref="chartRef" />
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'

const props = withDefaults(defineProps<{
  /** [{ date: string, value: number }] */
  data: { date: string; value: number }[]
}>(), {
  data: () => [],
})

const chartRef = ref<HTMLElement>()
let chart: echarts.ECharts | null = null

function initChart() {
  if (!chartRef.value) return
  chart = echarts.init(chartRef.value)
  updateChart()

  const observer = new ResizeObserver(() => chart?.resize())
  observer.observe(chartRef.value)
}

function updateChart() {
  if (!chart || props.data.length === 0) return

  const values = props.data.map(d => d.value)
  const maxValue = Math.max(...values, 5)

  chart.setOption({
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#111118',
      borderColor: '#2a2a35',
      textStyle: { color: '#e8dcc8' },
    },
    grid: {
      top: 20,
      bottom: 30,
      left: 40,
      right: 20,
    },
    xAxis: {
      type: 'category',
      data: props.data.map(d => d.date),
      axisLine: { lineStyle: { color: '#2a2a35' } },
      axisLabel: { color: '#665e50', fontSize: 11 },
      axisTick: { show: false },
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: Math.ceil(maxValue * 1.2),
      splitLine: { lineStyle: { color: '#1a1a24' } },
      axisLabel: { color: '#665e50' },
    },
    series: [{
      type: 'line',
      data: values,
      smooth: true,
      showSymbol: false,
      emphasis: { showSymbol: true },
      lineStyle: {
        color: '#c9a84c',
        width: 2,
      },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(201,168,76,0.25)' },
          { offset: 1, color: 'rgba(201,168,76,0)' },
        ]),
      },
      itemStyle: {
        color: '#c9a84c',
        borderColor: '#e8c56a',
      },
      animationDuration: 1000,
    }],
  })
}

onMounted(() => initChart())
watch(() => props.data, () => updateChart(), { deep: true })
onBeforeUnmount(() => { chart?.dispose(); chart = null })
</script>

<style scoped>
.trend-chart {
  width: 100%;
  height: 300px;
}
</style>
