<template>
  <div ref="chartRef" class="chart"></div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  data: Array,
  quote: Object
})

const chartRef = ref(null)
let chart = null

const UP = '#ef232a'

function initChart() {
  if (!chartRef.value) return
  chart = echarts.init(chartRef.value, 'dark')
  window.addEventListener('resize', () => chart?.resize())
}

function updateChart() {
  if (!chart || !props.data?.length) return
  
  const times = props.data.map(d => d.time)
  const prices = props.data.map(d => d.price)
  const base = props.quote?.preclose || null
  
  const option = {
    animation: false,
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#1c2230',
      borderColor: '#283040',
      textStyle: { color: '#c9d1d9' }
    },
    grid: [{ left: 56, right: 18, top: 30, height: '82%' }],
    xAxis: [{
      type: 'category',
      data: times,
      axisLabel: { color: '#8b949e' },
      axisLine: { lineStyle: { color: '#283040' } }
    }],
    yAxis: [{
      scale: true,
      axisLabel: { color: '#8b949e' },
      splitLine: { lineStyle: { color: '#1c2230' } }
    }],
    series: [{
      type: 'line',
      data: prices,
      symbol: 'none',
      lineStyle: { width: 1.5, color: UP },
      areaStyle: { color: 'rgba(239, 35, 42, .08)' },
      markLine: base ? {
        silent: true,
        symbol: 'none',
        lineStyle: { color: '#8b949e', type: 'dashed' },
        data: [{ yAxis: base }]
      } : undefined
    }]
  }
  
  chart.setOption(option, true)
}

watch(() => [props.data, props.quote], () => {
  nextTick(updateChart)
}, { deep: true })

onMounted(() => {
  initChart()
  nextTick(updateChart)
})

onUnmounted(() => {
  chart?.dispose()
})
</script>

<style scoped>
.chart {
  width: 100%;
  height: 760px;
}
</style>
