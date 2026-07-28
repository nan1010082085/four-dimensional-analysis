<template>
  <div class="chart-container">
    <div ref="chartRef" class="chart"></div>
    <div class="signal-legend">
      <span class="signal-buy">▲ 入</span>
      <span class="signal-sell">▼ 出</span>
      <span class="signal-info">基于MA/MACD/KDJ/RSI多指标共振</span>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  bars: Array,
  indicators: Object
})

const chartRef = ref(null)
let chart = null

const UP = '#ef232a'
const DOWN = '#14b143'

// 计算短线买卖信号
function calculateSignals(bars, indicators) {
  if (!bars || !indicators) return { buySignals: [], sellSignals: [] }
  
  const buySignals = []
  const sellSignals = []
  const ma5 = indicators.ma5 || []
  const ma10 = indicators.ma10 || []
  const ma20 = indicators.ma20 || []
  const macd = indicators.macd || {}
  const kdj = indicators.kdj || {}
  const rsi = indicators.rsi || []
  
  for (let i = 1; i < bars.length; i++) {
    const bar = bars[i]
    const prevBar = bars[i-1]
    
    // 买入信号条件（短线入场）
    let buyScore = 0
    let buyReasons = []
    
    // 1. MA金叉：MA5上穿MA10
    if (ma5[i] && ma10[i] && ma5[i-1] && ma10[i-1]) {
      if (ma5[i] > ma10[i] && ma5[i-1] <= ma10[i-1]) {
        buyScore += 2
        buyReasons.push('MA5上穿MA10')
      }
    }
    
    // 2. MACD金叉（柱状线由负转正）
    if (macd.hist && macd.hist[i] !== null && macd.hist[i-1] !== null) {
      if (macd.hist[i] > 0 && macd.hist[i-1] <= 0) {
        buyScore += 2
        buyReasons.push('MACD金叉')
      }
    }
    
    // 3. KDJ超卖回升（K从20以下上穿）
    if (kdj.k && kdj.k[i] && kdj.k[i-1]) {
      if (kdj.k[i] > 20 && kdj.k[i-1] <= 20) {
        buyScore += 1
        buyReasons.push('KDJ超卖回升')
      }
    }
    
    // 4. RSI超卖回升（RSI从30以下上穿）
    if (rsi[i] && rsi[i-1]) {
      if (rsi[i] > 30 && rsi[i-1] <= 30) {
        buyScore += 1
        buyReasons.push('RSI超卖回升')
      }
    }
    
    // 5. 价格突破MA20（趋势确认）
    if (ma20[i] && bar.close > ma20[i] && prevBar.close <= ma20[i]) {
      buyScore += 1
      buyReasons.push('突破MA20')
    }
    
    // 6. 放量上涨（量价配合）
    if (bar.close > prevBar.close && bar.volume > prevBar.volume * 1.3) {
      buyScore += 1
      buyReasons.push('放量上涨')
    }
    
    // 7. 阳包阴（反转信号）
    if (bar.close > bar.open && prevBar.close < prevBar.open) {
      if (bar.close > prevBar.open && bar.open < prevBar.close) {
        buyScore += 1
        buyReasons.push('阳包阴')
      }
    }
    
    // 卖出信号条件（短线出场）
    let sellScore = 0
    let sellReasons = []
    
    // 1. MA死叉：MA5下穿MA10
    if (ma5[i] && ma10[i] && ma5[i-1] && ma10[i-1]) {
      if (ma5[i] < ma10[i] && ma5[i-1] >= ma10[i-1]) {
        sellScore += 2
        sellReasons.push('MA5下穿MA10')
      }
    }
    
    // 2. MACD死叉（柱状线由正转负）
    if (macd.hist && macd.hist[i] !== null && macd.hist[i-1] !== null) {
      if (macd.hist[i] < 0 && macd.hist[i-1] >= 0) {
        sellScore += 2
        sellReasons.push('MACD死叉')
      }
    }
    
    // 3. KDJ超买回落（K从80以上下穿）
    if (kdj.k && kdj.k[i] && kdj.k[i-1]) {
      if (kdj.k[i] < 80 && kdj.k[i-1] >= 80) {
        sellScore += 1
        sellReasons.push('KDJ超买回落')
      }
    }
    
    // 4. RSI超买回落（RSI从70以上下穿）
    if (rsi[i] && rsi[i-1]) {
      if (rsi[i] < 70 && rsi[i-1] >= 70) {
        sellScore += 1
        sellReasons.push('RSI超买回落')
      }
    }
    
    // 5. 跌破MA20（趋势反转）
    if (ma20[i] && bar.close < ma20[i] && prevBar.close >= ma20[i]) {
      sellScore += 1
      sellReasons.push('跌破MA20')
    }
    
    // 6. 放量下跌（恐慌抛售）
    if (bar.close < prevBar.close && bar.volume > prevBar.volume * 1.3) {
      sellScore += 1
      sellReasons.push('放量下跌')
    }
    
    // 7. 阴包阳（反转信号）
    if (bar.close < bar.open && prevBar.close > prevBar.open) {
      if (bar.close < prevBar.open && bar.open > prevBar.close) {
        sellScore += 1
        sellReasons.push('阴包阳')
      }
    }
    
    // 8. 高位长上影线（见顶信号）
    if (bar.high && bar.close && bar.open) {
      const upperShadow = bar.high - Math.max(bar.close, bar.open)
      const body = Math.abs(bar.close - bar.open)
      if (upperShadow > body * 2 && bar.close < bar.open) {
        sellScore += 1
        sellReasons.push('长上影线')
      }
    }
    
    // 生成信号（需要多个条件同时满足）
    if (buyScore >= 3) {
      buySignals.push({
        coord: [bar.date, bar.low * 0.995],
        value: bar.low,
        score: buyScore,
        reasons: buyReasons,
        price: bar.close
      })
    }
    
    if (sellScore >= 3) {
      sellSignals.push({
        coord: [bar.date, bar.high * 1.005],
        value: bar.high,
        score: sellScore,
        reasons: sellReasons,
        price: bar.close
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
  if (!chart || !props.bars?.length || !props.indicators) return
  
  const dates = props.bars.map(b => b.date)
  const ohlc = props.bars.map(b => [b.open, b.close, b.low, b.high])
  const vol = props.bars.map(b => ({
    value: b.volume,
    itemStyle: { color: b.close >= b.open ? UP : DOWN }
  }))
  const ma = a => a.map(v => v == null ? null : v)
  const macdBar = props.indicators.macd.hist.map(v => ({
    value: v,
    itemStyle: { color: v >= 0 ? UP : DOWN }
  }))
  
  // 计算买卖信号
  const { buySignals, sellSignals } = calculateSignals(props.bars, props.indicators)
  
  const option = {
    animation: false,
    backgroundColor: 'transparent',
    axisPointer: { link: [{ xAxisIndex: 'all' }], label: { backgroundColor: '#333' } },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' },
      backgroundColor: '#1c2230',
      borderColor: '#283040',
      textStyle: { color: '#c9d1d9', fontSize: 12 },
      formatter: function(params) {
        let result = ''
        let signalInfo = ''
        
        params.forEach(p => {
          if (p.seriesType === 'candlestick') {
            result += `<div style="font-weight:bold;margin-bottom:5px">${p.axisValue}</div>`
            result += `<div>开: ${p.data[1]} 收: ${p.data[2]}</div>`
            result += `<div>低: ${p.data[3]} 高: ${p.data[4]}</div>`
          } else if (p.seriesName === '成交量') {
            result += `<div>成交量: ${formatVolume(p.value)}</div>`
          } else if (p.seriesName === '入' && p.data && p.data.reasons) {
            signalInfo += `<div style="color:#14b143;font-weight:bold;margin-top:8px">▲ 入场信号</div>`
            signalInfo += `<div style="color:#14b143">价格: ${p.data.price}</div>`
            signalInfo += `<div style="color:#14b143">原因: ${p.data.reasons.join(', ')}</div>`
          } else if (p.seriesName === '出' && p.data && p.data.reasons) {
            signalInfo += `<div style="color:#ef232a;font-weight:bold;margin-top:8px">▼ 出场信号</div>`
            signalInfo += `<div style="color:#ef232a">价格: ${p.data.price}</div>`
            signalInfo += `<div style="color:#ef232a">原因: ${p.data.reasons.join(', ')}</div>`
          }
        })
        
        return result + signalInfo
      }
    },
    legend: {
      data: ['MA5', 'MA10', 'MA20', 'MA60', 'MACD', 'DIF', 'DEA', 'K', 'D', 'J', '入', '出'],
      textStyle: { color: '#8b949e', fontSize: 11 },
      top: 0,
      itemWidth: 12,
      itemHeight: 12
    },
    // 数据缩放配置
    dataZoom: [
      {
        type: 'inside',
        xAxisIndex: [0, 1, 2, 3],
        start: 60,
        end: 100,
        zoomOnMouseWheel: true,
        moveOnMouseMove: true,
        moveOnMouseWheel: false
      },
      {
        type: 'slider',
        xAxisIndex: [0, 1, 2, 3],
        start: 60,
        end: 100,
        height: 20,
        bottom: 5,
        borderColor: '#283040',
        backgroundColor: '#161b22',
        dataBackground: {
          lineStyle: { color: '#283040' },
          areaStyle: { color: '#1c2230' }
        },
        selectedDataBackground: {
          lineStyle: { color: '#58a6ff' },
          areaStyle: { color: 'rgba(88, 166, 255, 0.1)' }
        },
        handleStyle: { color: '#58a6ff', borderColor: '#58a6ff' },
        textStyle: { color: '#8b949e' },
        fillerColor: 'rgba(88, 166, 255, 0.15)'
      }
    ],
    grid: [
      { left: 56, right: 18, top: 30, height: '40%' },
      { left: 56, right: 18, top: '48%', height: '8%' },
      { left: 56, right: 18, top: '58%', height: '12%' },
      { left: 56, right: 18, top: '72%', height: '12%' },
      { left: 56, right: 18, bottom: 35, height: 0 }
    ],
    xAxis: [
      { type: 'category', data: dates, gridIndex: 0, axisLabel: { show: false }, axisLine: { lineStyle: { color: '#283040' } } },
      { type: 'category', data: dates, gridIndex: 1, axisLabel: { show: false }, axisLine: { lineStyle: { color: '#283040' } } },
      { type: 'category', data: dates, gridIndex: 2, axisLabel: { show: false }, axisLine: { lineStyle: { color: '#283040' } } },
      { type: 'category', data: dates, gridIndex: 3, axisLabel: { show: false }, axisLine: { lineStyle: { color: '#283040' } } },
    ],
    yAxis: [
      { scale: true, gridIndex: 0, splitLine: { lineStyle: { color: '#1c2230' } }, axisLabel: { color: '#8b949e', fontSize: 10 } },
      { scale: true, gridIndex: 1, splitNumber: 2, axisLabel: { color: '#8b949e', fontSize: 10 } },
      { scale: true, gridIndex: 2, splitNumber: 2, axisLabel: { color: '#8b949e', fontSize: 10 } },
      { scale: true, gridIndex: 3, splitNumber: 2, axisLabel: { color: '#8b949e', fontSize: 10 } },
    ],
    series: [
      // K线
      { name: 'K线', type: 'candlestick', data: ohlc, xAxisIndex: 0, yAxisIndex: 0, itemStyle: { color: UP, color0: DOWN, borderColor: UP, borderColor0: DOWN } },
      // 均线
      { name: 'MA5', type: 'line', data: ma(props.indicators.ma5), xAxisIndex: 0, yAxisIndex: 0, smooth: true, symbol: 'none', lineStyle: { width: 1, color: '#58a6ff' } },
      { name: 'MA10', type: 'line', data: ma(props.indicators.ma10), xAxisIndex: 0, yAxisIndex: 0, smooth: true, symbol: 'none', lineStyle: { width: 1, color: '#d29922' } },
      { name: 'MA20', type: 'line', data: ma(props.indicators.ma20), xAxisIndex: 0, yAxisIndex: 0, smooth: true, symbol: 'none', lineStyle: { width: 1, color: '#8b949e' } },
      { name: 'MA60', type: 'line', data: ma(props.indicators.ma60), xAxisIndex: 0, yAxisIndex: 0, smooth: true, symbol: 'none', lineStyle: { width: 1, color: '#f0f0f0' } },
      // 成交量
      { name: '成交量', type: 'bar', data: vol, xAxisIndex: 1, yAxisIndex: 1 },
      // MACD
      { name: 'MACD', type: 'bar', data: macdBar, xAxisIndex: 2, yAxisIndex: 2 },
      { name: 'DIF', type: 'line', data: props.indicators.macd.dif, xAxisIndex: 2, yAxisIndex: 2, symbol: 'none', lineStyle: { width: 1, color: '#58a6ff' } },
      { name: 'DEA', type: 'line', data: props.indicators.macd.dea, xAxisIndex: 2, yAxisIndex: 2, symbol: 'none', lineStyle: { width: 1, color: '#d29922' } },
      // KDJ
      { name: 'K', type: 'line', data: props.indicators.kdj.k, xAxisIndex: 3, yAxisIndex: 3, symbol: 'none', lineStyle: { width: 1, color: '#58a6ff' } },
      { name: 'D', type: 'line', data: props.indicators.kdj.d, xAxisIndex: 3, yAxisIndex: 3, symbol: 'none', lineStyle: { width: 1, color: '#14b143' } },
      { name: 'J', type: 'line', data: props.indicators.kdj.j, xAxisIndex: 3, yAxisIndex: 3, symbol: 'none', lineStyle: { width: 1, color: '#ef232a' } },
      // 买入信号（入）
      {
        name: '入',
        type: 'scatter',
        data: buySignals.map(s => ({
          value: [s.coord[0], s.coord[1]],
          price: s.price,
          reasons: s.reasons,
          score: s.score
        })),
        xAxisIndex: 0,
        yAxisIndex: 0,
        symbol: 'triangle',
        symbolSize: 14,
        itemStyle: { 
          color: '#14b143',
          borderColor: '#fff',
          borderWidth: 1
        },
        label: {
          show: true,
          position: 'bottom',
          formatter: '入',
          color: '#14b143',
          fontSize: 10,
          fontWeight: 'bold'
        },
        emphasis: {
          itemStyle: { 
            color: '#14b143',
            borderColor: '#fff',
            borderWidth: 2,
            shadowBlur: 10,
            shadowColor: 'rgba(20, 177, 67, 0.5)'
          }
        }
      },
      // 卖出信号（出）
      {
        name: '出',
        type: 'scatter',
        data: sellSignals.map(s => ({
          value: [s.coord[0], s.coord[1]],
          price: s.price,
          reasons: s.reasons,
          score: s.score
        })),
        xAxisIndex: 0,
        yAxisIndex: 0,
        symbol: 'pin',
        symbolSize: 14,
        itemStyle: { 
          color: '#ef232a',
          borderColor: '#fff',
          borderWidth: 1
        },
        label: {
          show: true,
          position: 'top',
          formatter: '出',
          color: '#ef232a',
          fontSize: 10,
          fontWeight: 'bold'
        },
        emphasis: {
          itemStyle: { 
            color: '#ef232a',
            borderColor: '#fff',
            borderWidth: 2,
            shadowBlur: 10,
            shadowColor: 'rgba(239, 35, 42, 0.5)'
          }
        }
      }
    ]
  }
  
  chart.setOption(option, true)
}

function formatVolume(vol) {
  if (vol >= 100000000) return (vol / 100000000).toFixed(2) + '亿'
  if (vol >= 10000) return (vol / 10000).toFixed(2) + '万'
  return vol.toString()
}

watch(() => [props.bars, props.indicators], () => {
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
.chart-container {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
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
