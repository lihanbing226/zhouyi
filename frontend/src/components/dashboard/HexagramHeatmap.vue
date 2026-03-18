<template>
  <div class="heatmap-chart" ref="chartRef" />
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'

const props = withDefaults(defineProps<{
  /** 64卦数据 [{ name: string, count: number }] 按卦序排列 */
  data: { name: string; count: number }[]
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

  const maxCount = Math.max(...props.data.map(d => d.count), 1)

  // 8x8 网格
  const heatmapData = props.data.map((item, i) => {
    const x = i % 8
    const y = Math.floor(i / 8)
    return [x, y, item.count]
  })

  chart.setOption({
    tooltip: {
      position: 'top',
      backgroundColor: '#111118',
      borderColor: '#2a2a35',
      textStyle: { color: '#e8dcc8' },
      formatter: (params: any) => {
        const idx = params.data[1] * 8 + params.data[0]
        const item = props.data[idx]
        return item ? `${item.name}<br/>次数: ${item.count}` : ''
      },
    },
    grid: {
      top: 10,
      bottom: 10,
      left: 10,
      right: 10,
      containLabel: false,
    },
    xAxis: { type: 'category', show: false, data: Array.from({ length: 8 }, (_, i) => i) },
    yAxis: { type: 'category', show: false, data: Array.from({ length: 8 }, (_, i) => i) },
    visualMap: {
      show: false,
      min: 0,
      max: maxCount,
      inRange: {
        color: ['#111118', '#2c3a1c', '#4a6520', '#8a7640', '#c9a84c'],
      },
    },
    series: [{
      type: 'heatmap',
      data: heatmapData,
      itemStyle: {
        borderColor: '#0a0a0f',
        borderWidth: 2,
        borderRadius: 4,
      },
      emphasis: {
        itemStyle: {
          borderColor: '#c9a84c',
          borderWidth: 2,
          shadowBlur: 10,
          shadowColor: 'rgba(201,168,76,0.3)',
        },
      },
      animationDuration: 800,
    }],
  })
}

onMounted(() => initChart())

watch(() => props.data, () => updateChart(), { deep: true })

onBeforeUnmount(() => {
  chart?.dispose()
  chart = null
})
</script>

<style scoped>
.heatmap-chart {
  width: 100%;
  height: 300px;
}
</style>
