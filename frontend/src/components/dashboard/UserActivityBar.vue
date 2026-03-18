<template>
  <div class="bar-chart" ref="chartRef" />
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'

const props = withDefaults(defineProps<{
  /** [{ date: string, count: number }] */
  data: { date: string; count: number }[]
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
      splitLine: { lineStyle: { color: '#1a1a24' } },
      axisLabel: { color: '#665e50' },
    },
    series: [{
      type: 'bar',
      data: props.data.map(d => d.count),
      barWidth: '60%',
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#c9a84c' },
          { offset: 1, color: '#6a5a30' },
        ]),
        borderRadius: [4, 4, 0, 0],
      },
      emphasis: {
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#e8c56a' },
            { offset: 1, color: '#c9a84c' },
          ]),
        },
      },
      animationDuration: 800,
      animationEasing: 'cubicOut',
    }],
  })
}

onMounted(() => initChart())
watch(() => props.data, () => updateChart(), { deep: true })
onBeforeUnmount(() => { chart?.dispose(); chart = null })
</script>

<style scoped>
.bar-chart {
  width: 100%;
  height: 300px;
}
</style>
