<template>
  <div class="minute-chart-wrapper">
    <div ref="chartRef" class="chart"></div>
    <div class="signal-legend">
      <span class="signal-buy">▲ 入</span>
      <span class="signal-sell">▼ 出</span>
      <span class="signal-info">基于分时价格异动</span>
    </div>
  </div>
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
const DOWN = '#14b143'

// 计算分时买卖信号
function calculateMinuteSignals(data) {
  if (!data || data.length < 10) return { buySignals: [], sellSignals: [] }
  
  const buySignals = []
  const sellSignals = []
  
  // 计算移动平均
  const maWindow = 5
  const ma = []
  for (let i = 0; i < data.length; i++) {
    if (i < maWindow - 1) {
      ma.push(null)
    } else {
      let sum = 0
      for (let j = i - maWindow + 1; j <= i; j++) {
        sum += data[j].price
      }
      ma.push(sum / maWindow)
    }
  }
  
  // 计算价格变化率
  for (let i = 2; i < data.length; i++) {
    const prev2 = data[i-2].price
    const prev1 = data[i-1].price
    const curr = data[i].price
    
    const change1 = (prev1 - prev2) / prev2 * 100
    const change2 = (curr - prev1) / prev1 * 100
    
    // 买入信号：价格连续上涨且突破均线
    if (change1 > 0 && change2 > 0.05 && ma[i] && curr > ma[i] && prev1 <= ma[i-1]) {
      buySignals.push({
        coord: [data[i].time, data[i].price],
        value: data[i].price,
        reasons: ['分时突破均线', '连续上涨']
      })
    }
    
    // 买入信号：价格急跌后反弹
    if (change1 < -0.3 && change2 > 0.15) {
      buySignals.push({
        coord: [data[i].time, data[i].price],
        value: data[i].price,
        reasons: ['急跌反弹', '超卖回升']
      })
    }
    
    // 卖出信号：价格连续下跌且跌破均线
    if (change1 < 0 && change2 < -0.05 && ma[i] && curr < ma[i] && prev1 >= ma[i-1]) {
      sellSignals.push({
        coord: [data[i].time, data[i].price],
        value: data[i].price,
        reasons: ['分时跌破均线', '连续下跌']
      })
    }
    
    // 卖出信号：价格急涨后回落
    if (change1 > 0.3 && change2 < -0.15) {
      sellSignals.push({
        coord: [data[i].time, data[i].price],
        value: data[i].price,
        reasons: ['急涨回落', '超买回调']
      })
    }
  }
  
  return { buySignals, sellSignals }
}

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
  
  // 计算买卖信号
  const { buySignals, sellSignals } = calculateMinuteSignals(props.data)
  
  // 计算移动平均
  const maWindow = 5
  const maData = []
  for (let i = 0; i < prices.length; i++) {
    if (i < maWindow - 1) {
      maData.push(null)
    } else {
      let sum = 0
      for (let j = i - maWindow + 1; j <= i; j++) {
        sum += prices[j]
      }
      maData.push(parseFloat((sum / maWindow).toFixed(2)))
    }
  }
  
  const option = {
    animation: false,
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#1c2230',
      borderColor: '#283040',
      textStyle: { color: '#c9d1d9', fontSize: 12 },
      formatter: function(params) {
        let result = ''
        let signalInfo = ''
        
        const time = params[0]?.axisValue || ''
        result += `<div style="font-weight:bold;margin-bottom:5px;color:#58a6ff">${time}</div>`
        
        params.forEach(p => {
          if (p.seriesName === '分时' && p.value != null) {
            const color = base && p.value >= base ? UP : DOWN
            result += `<div><span style="color:#8b949e">价格:</span> <span style="color:${color};font-weight:bold">${p.value}</span></div>`
          } else if (p.seriesName === '均线' && p.value != null) {
            result += `<div><span style="color:#d29922">MA5:</span> ${p.value}</div>`
          } else if (p.seriesName === '入' && p.data && p.data.reasons) {
            signalInfo += `<div style="color:#14b143;font-weight:bold;margin-top:8px">▲ 入场信号</div>`
            signalInfo += `<div style="color:#14b143">价格: ${p.value}</div>`
            signalInfo += `<div style="color:#14b143">原因: ${p.data.reasons.join(', ')}</div>`
          } else if (p.seriesName === '出' && p.data && p.data.reasons) {
            signalInfo += `<div style="color:#ef232a;font-weight:bold;margin-top:8px">▼ 出场信号</div>`
            signalInfo += `<div style="color:#ef232a">价格: ${p.value}</div>`
            signalInfo += `<div style="color:#ef232a">原因: ${p.data.reasons.join(', ')}</div>`
          }
        })
        
        if (base) {
          const change = prices[params[0]?.dataIndex] - base
          const changePct = (change / base * 100).toFixed(2)
          const color = change >= 0 ? UP : DOWN
          result += `<div style="margin-top:4px;color:${color}">涨跌: ${change >= 0 ? '+' : ''}${change.toFixed(2)} (${change >= 0 ? '+' : ''}${changePct}%)</div>`
        }
        
        return result + signalInfo
      }
    },
    legend: {
      data: ['分时', '均线', '入', '出'],
      textStyle: { color: '#8b949e', fontSize: 11 },
      top: 0
    },
    grid: [{ left: 56, right: 18, top: 30, height: '82%' }],
    xAxis: [{
      type: 'category',
      data: times,
      axisLabel: { color: '#8b949e', fontSize: 10 },
      axisLine: { lineStyle: { color: '#283040' } }
    }],
    yAxis: [{
      scale: true,
      axisLabel: { color: '#8b949e', fontSize: 10 },
      splitLine: { lineStyle: { color: '#1c2230' } }
    }],
    series: [
      // 分时线
      {
        name: '分时',
        type: 'line',
        data: prices,
        symbol: 'none',
        lineStyle: { width: 1.5, color: UP },
        areaStyle: { color: 'rgba(239, 35, 42, .08)' }
      },
      // 均线
      {
        name: '均线',
        type: 'line',
        data: maData,
        symbol: 'none',
        lineStyle: { width: 1, color: '#d29922' }
      },
      // 昨收参考线
      ...(base ? [{
        name: '昨收',
        type: 'line',
        data: Array(prices.length).fill(base),
        symbol: 'none',
        lineStyle: { width: 1, color: '#8b949e', type: 'dashed' },
        silent: true
      }] : []),
      // 买入信号
      {
        name: '入',
        type: 'scatter',
        data: buySignals.map(s => ({
          value: s.coord[1],
          coord: s.coord,
          reasons: s.reasons,
          symbol: 'triangle',
          symbolSize: 12,
          itemStyle: { color: '#14b143', borderColor: '#fff', borderWidth: 1 }
        })),
        symbol: 'triangle',
        symbolSize: 12,
        itemStyle: { color: '#14b143', borderColor: '#fff', borderWidth: 1 },
        label: {
          show: true,
          position: 'bottom',
          formatter: '入',
          color: '#14b143',
          fontSize: 10,
          fontWeight: 'bold'
        }
      },
      // 卖出信号
      {
        name: '出',
        type: 'scatter',
        data: sellSignals.map(s => ({
          value: s.coord[1],
          coord: s.coord,
          reasons: s.reasons,
          symbol: 'pin',
          symbolSize: 12,
          itemStyle: { color: '#ef232a', borderColor: '#fff', borderWidth: 1 }
        })),
        symbol: 'pin',
        symbolSize: 12,
        itemStyle: { color: '#ef232a', borderColor: '#fff', borderWidth: 1 },
        label: {
          show: true,
          position: 'top',
          formatter: '出',
          color: '#ef232a',
          fontSize: 10,
          fontWeight: 'bold'
        }
      }
    ]
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
.minute-chart-wrapper {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.chart {
  flex: 1;
  min-height: 400px;
  width: 100%;
}

.signal-legend {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 8px 12px;
  background: var(--card2, #1c2230);
  border-radius: 6px;
  margin-top: 8px;
  font-size: 12px;
  flex-shrink: 0;
}

.signal-buy {
  color: #14b143;
  font-weight: bold;
}

.signal-sell {
  color: #ef232a;
  font-weight: bold;
}

.signal-info {
  color: #8b949e;
  font-size: 11px;
}
</style>
