<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'

const props = defineProps<{
  klineData: any
  minuteData: any[]
  quote: any
  period: string
}>()

const chartRef = ref<HTMLElement>()
let chart: echarts.ECharts | null = null

const UP = '#ef232a'
const DOWN = '#14b143'

function initChart() {
  if (!chartRef.value) return
  chart = echarts.init(chartRef.value, 'dark')
}

function renderKline(bars: any[], ind: any) {
  if (!chart) return
  const dates = bars.map((b: any) => b.date)
  const ohlc = bars.map((b: any) => [b.open, b.close, b.low, b.high])
  const vol = bars.map((b: any) => ({
    value: b.volume,
    itemStyle: { color: b.close >= b.open ? UP : DOWN },
  }))
  const ma = (a: any[]) => a.map((v: any) => (v == null ? null : v))
  const macdBar = ind.macd.hist.map((v: any) => ({
    value: v,
    itemStyle: { color: v >= 0 ? UP : DOWN },
  }))

  const opt: echarts.EChartsOption = {
    animation: false,
    backgroundColor: 'transparent',
    axisPointer: { link: [{ xAxisIndex: 'all' }], label: { backgroundColor: '#333' } },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' },
      backgroundColor: '#1c2230',
      borderColor: '#283040',
      textStyle: { color: '#c9d1d9' },
    },
    legend: {
      data: ['MA5', 'MA10', 'MA20', 'MA60', 'MACD', 'DIF', 'DEA', 'K', 'D', 'J'],
      textStyle: { color: '#8b949e' },
      top: 0,
    },
    grid: [
      { left: 56, right: 18, top: 30, height: '46%' },
      { left: 56, right: 18, top: '54%', height: '10%' },
      { left: 56, right: 18, top: '66%', height: '14%' },
      { left: 56, right: 18, top: '82%', height: '14%' },
    ],
    xAxis: [
      { type: 'category', data: dates, gridIndex: 0, axisLabel: { show: false }, axisLine: { lineStyle: { color: '#283040' } } },
      { type: 'category', data: dates, gridIndex: 1, axisLabel: { show: false }, axisLine: { lineStyle: { color: '#283040' } } },
      { type: 'category', data: dates, gridIndex: 2, axisLabel: { show: false }, axisLine: { lineStyle: { color: '#283040' } } },
      { type: 'category', data: dates, gridIndex: 3, axisLine: { lineStyle: { color: '#283040' } }, axisLabel: { color: '#8b949e' } },
    ],
    yAxis: [
      { scale: true, gridIndex: 0, splitLine: { lineStyle: { color: '#1c2230' } }, axisLabel: { color: '#8b949e' } },
      { scale: true, gridIndex: 1, splitNumber: 2, axisLabel: { color: '#8b949e' } },
      { scale: true, gridIndex: 2, splitNumber: 2, axisLabel: { color: '#8b949e' } },
      { scale: true, gridIndex: 3, splitNumber: 2, axisLabel: { color: '#8b949e' } },
    ],
    series: [
      { name: 'K', type: 'candlestick', data: ohlc, xAxisIndex: 0, yAxisIndex: 0, itemStyle: { color: UP, color0: DOWN, borderColor: UP, borderColor0: DOWN } },
      { name: 'MA5', type: 'line', data: ma(ind.ma5), xAxisIndex: 0, yAxisIndex: 0, smooth: true, symbol: 'none', lineStyle: { width: 1 } },
      { name: 'MA10', type: 'line', data: ma(ind.ma10), xAxisIndex: 0, yAxisIndex: 0, smooth: true, symbol: 'none', lineStyle: { width: 1 } },
      { name: 'MA20', type: 'line', data: ma(ind.ma20), xAxisIndex: 0, yAxisIndex: 0, smooth: true, symbol: 'none', lineStyle: { width: 1 } },
      { name: 'MA60', type: 'line', data: ma(ind.ma60), xAxisIndex: 0, yAxisIndex: 0, smooth: true, symbol: 'none', lineStyle: { width: 1 } },
      { name: '量', type: 'bar', data: vol, xAxisIndex: 1, yAxisIndex: 1 },
      { name: 'MACD', type: 'bar', data: macdBar, xAxisIndex: 2, yAxisIndex: 2 },
      { name: 'DIF', type: 'line', data: ind.macd.dif, xAxisIndex: 2, yAxisIndex: 2, symbol: 'none', lineStyle: { width: 1, color: '#58a6ff' } },
      { name: 'DEA', type: 'line', data: ind.macd.dea, xAxisIndex: 2, yAxisIndex: 2, symbol: 'none', lineStyle: { width: 1, color: '#d29922' } },
      { name: 'K', type: 'line', data: ind.kdj.k, xAxisIndex: 3, yAxisIndex: 3, symbol: 'none', lineStyle: { width: 1, color: '#58a6ff' } },
      { name: 'D', type: 'line', data: ind.kdj.d, xAxisIndex: 3, yAxisIndex: 3, symbol: 'none', lineStyle: { width: 1, color: '#14b143' } },
      { name: 'J', type: 'line', data: ind.kdj.j, xAxisIndex: 3, yAxisIndex: 3, symbol: 'none', lineStyle: { width: 1, color: '#ef232a' } },
    ],
  }
  chart.setOption(opt, true)
}

function renderMinute(data: any[], q: any) {
  if (!chart) return
  const times = data.map((d: any) => d.time)
  const prices = data.map((d: any) => d.price)
  const base = q?.preclose || null

  const opt: echarts.EChartsOption = {
    animation: false,
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#1c2230',
      borderColor: '#283040',
      textStyle: { color: '#c9d1d9' },
    },
    grid: [{ left: 56, right: 18, top: 30, height: '82%' }],
    xAxis: [{ type: 'category', data: times, axisLabel: { color: '#8b949e' }, axisLine: { lineStyle: { color: '#283040' } } }],
    yAxis: [{ scale: true, axisLabel: { color: '#8b949e' }, splitLine: { lineStyle: { color: '#1c2230' } } }],
    series: [
      {
        type: 'line',
        data: prices,
        symbol: 'none',
        lineStyle: { width: 1.5, color: UP },
        areaStyle: { color: 'rgba(239,35,42,.08)' },
        markLine: base
          ? {
              silent: true,
              symbol: 'none',
              lineStyle: { color: '#8b949e', type: 'dashed' },
              data: [{ yAxis: base }],
            }
          : undefined,
      },
    ],
  }
  chart.setOption(opt, true)
}

function handleResize() {
  chart?.resize()
}

watch(
  () => [props.klineData, props.minuteData],
  () => {
    nextTick(() => {
      if (props.klineData) {
        renderKline(props.klineData.bars, props.klineData.indicators)
      } else if (props.minuteData.length) {
        renderMinute(props.minuteData, props.quote)
      }
    })
  },
  { deep: true },
)

onMounted(() => {
  initChart()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  chart?.dispose()
})
</script>

<template>
  <div class="card">
    <h2>技术面 <small>趋势 · K线 + MA + 量 + MACD + KDJ</small></h2>
    <div ref="chartRef" class="chart-container"></div>
  </div>
</template>

<style scoped>
.card {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 10px;
  padding: 14px;
}

h2 {
  margin: 0 0 10px;
  font-size: 13px;
  color: var(--accent);
  display: flex;
  align-items: center;
  gap: 6px;
  border-left: 3px solid var(--accent);
  padding-left: 8px;
}

h2 small {
  color: var(--muted);
  font-weight: normal;
  font-size: 11px;
}

.chart-container {
  width: 100%;
  height: 760px;
}
</style>
