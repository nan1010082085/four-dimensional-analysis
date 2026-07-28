<template>
  <div class="risk-panel">
    <h3>风险控制</h3>
    
    <div class="risk-section">
      <div class="section-title">止损止盈计算器</div>
      <div class="input-row">
        <label>入场价</label>
        <input v-model.number="entryPrice" type="number" placeholder="输入价格" />
      </div>
      <div class="input-row">
        <label>止损比例</label>
        <select v-model.number="stopLossPct">
          <option :value="1">1%</option>
          <option :value="2">2%</option>
          <option :value="3">3%</option>
          <option :value="5">5%</option>
          <option :value="8">8%</option>
          <option :value="10">10%</option>
        </select>
      </div>
      <div class="input-row">
        <label>止盈比例</label>
        <select v-model.number="takeProfitPct">
          <option :value="3">3%</option>
          <option :value="5">5%</option>
          <option :value="8">8%</option>
          <option :value="10">10%</option>
          <option :value="15">15%</option>
          <option :value="20">20%</option>
        </select>
      </div>
      
      <div class="result-box" v-if="entryPrice">
        <div class="result-item">
          <span class="label">止损价</span>
          <span class="value down">{{ stopLossPrice }}</span>
        </div>
        <div class="result-item">
          <span class="label">止盈价</span>
          <span class="value up">{{ takeProfitPrice }}</span>
        </div>
        <div class="result-item">
          <span class="label">盈亏比</span>
          <span class="value" :class="profitLossRatio >= 2 ? 'up' : 'warn'">{{ profitLossRatio }}</span>
        </div>
      </div>
    </div>
    
    <div class="risk-section">
      <div class="section-title">仓位计算器</div>
      <div class="input-row">
        <label>总资金</label>
        <input v-model.number="totalCapital" type="number" placeholder="输入总资金" />
      </div>
      <div class="input-row">
        <label>单笔风险</label>
        <select v-model.number="riskPerTrade">
          <option :value="0.5">0.5%</option>
          <option :value="1">1%</option>
          <option :value="2">2%</option>
          <option :value="3">3%</option>
          <option :value="5">5%</option>
        </select>
      </div>
      
      <div class="result-box" v-if="totalCapital && entryPrice">
        <div class="result-item">
          <span class="label">最大亏损</span>
          <span class="value down">{{ maxLoss }} 元</span>
        </div>
        <div class="result-item">
          <span class="label">建议仓位</span>
          <span class="value accent">{{ positionSize }} 股</span>
        </div>
        <div class="result-item">
          <span class="label">仓位金额</span>
          <span class="value">{{ positionValue }} 元</span>
        </div>
        <div class="result-item">
          <span class="label">仓位占比</span>
          <span class="value">{{ positionPct }}%</span>
        </div>
      </div>
    </div>
    
    <div class="risk-section">
      <div class="section-title">ATR止损参考</div>
      <div class="atr-info" v-if="atr">
        <div class="result-item">
          <span class="label">ATR(14)</span>
          <span class="value">{{ atr }}</span>
        </div>
        <div class="result-item">
          <span class="label">1倍ATR止损</span>
          <span class="value down">{{ atrStop1 }}</span>
        </div>
        <div class="result-item">
          <span class="label">2倍ATR止损</span>
          <span class="value down">{{ atrStop2 }}</span>
        </div>
      </div>
      <div v-else class="atr-empty">加载行情后显示ATR</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  quote: Object,
  kline: Object
})

const entryPrice = ref(null)
const stopLossPct = ref(2)
const takeProfitPct = ref(5)
const totalCapital = ref(100000)
const riskPerTrade = ref(2)

// 止损价
const stopLossPrice = computed(() => {
  if (!entryPrice.value) return '--'
  return (entryPrice.value * (1 - stopLossPct.value / 100)).toFixed(2)
})

// 止盈价
const takeProfitPrice = computed(() => {
  if (!entryPrice.value) return '--'
  return (entryPrice.value * (1 + takeProfitPct.value / 100)).toFixed(2)
})

// 盈亏比
const profitLossRatio = computed(() => {
  if (!entryPrice.value) return 0
  return (takeProfitPct.value / stopLossPct.value).toFixed(1)
})

// 最大亏损
const maxLoss = computed(() => {
  if (!totalCapital.value) return 0
  return (totalCapital.value * riskPerTrade.value / 100).toFixed(0)
})

// 仓位大小（股数）
const positionSize = computed(() => {
  if (!entryPrice.value || !maxLoss.value) return 0
  const lossPerShare = entryPrice.value * stopLossPct.value / 100
  return Math.floor(maxLoss.value / lossPerShare)
})

// 仓位金额
const positionValue = computed(() => {
  if (!entryPrice.value || !positionSize.value) return 0
  return (entryPrice.value * positionSize.value).toFixed(0)
})

// 仓位占比
const positionPct = computed(() => {
  if (!totalCapital.value || !positionValue.value) return 0
  return ((positionValue.value / totalCapital.value) * 100).toFixed(1)
})

// ATR计算
const atr = computed(() => {
  if (!props.kline?.bars || props.kline.bars.length < 15) return null
  
  const bars = props.kline.bars.slice(-14)
  let sum = 0
  
  for (let i = 1; i < bars.length; i++) {
    const high = bars[i].high
    const low = bars[i].low
    const prevClose = bars[i-1].close
    
    const tr = Math.max(
      high - low,
      Math.abs(high - prevClose),
      Math.abs(low - prevClose)
    )
    sum += tr
  }
  
  return (sum / 14).toFixed(2)
})

// ATR止损价
const atrStop1 = computed(() => {
  if (!props.quote?.price || !atr.value) return '--'
  return (props.quote.price - parseFloat(atr.value)).toFixed(2)
})

const atrStop2 = computed(() => {
  if (!props.quote?.price || !atr.value) return '--'
  return (props.quote.price - parseFloat(atr.value) * 2).toFixed(2)
})

// 自动填入当前价格
watch(() => props.quote, (newQuote) => {
  if (newQuote?.price && !entryPrice.value) {
    entryPrice.value = newQuote.price
  }
}, { immediate: true })
</script>

<style scoped>
.risk-panel {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 10px;
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.risk-panel h3 {
  margin: 0;
  font-size: 13px;
  color: var(--accent);
  border-left: 3px solid var(--accent);
  padding-left: 8px;
}

.risk-section {
  background: var(--card2);
  border-radius: 8px;
  padding: 12px;
}

.section-title {
  font-size: 12px;
  color: var(--muted);
  margin-bottom: 10px;
  font-weight: bold;
}

.input-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.input-row label {
  font-size: 12px;
  color: var(--muted);
  min-width: 60px;
}

.input-row input,
.input-row select {
  flex: 1;
  padding: 6px 10px;
  background: var(--bg);
  border: 1px solid var(--line);
  color: var(--text);
  border-radius: 4px;
  font-size: 12px;
}

.input-row input:focus,
.input-row select:focus {
  outline: none;
  border-color: var(--accent);
}

.result-box {
  margin-top: 10px;
  padding: 10px;
  background: var(--bg);
  border-radius: 6px;
}

.result-item {
  display: flex;
  justify-content: space-between;
  padding: 4px 0;
  font-size: 12px;
}

.result-item .label {
  color: var(--muted);
}

.result-item .value {
  color: var(--text);
  font-weight: bold;
}

.result-item .value.up {
  color: #14b143;
}

.result-item .value.down {
  color: #ef232a;
}

.result-item .value.accent {
  color: var(--accent);
}

.result-item .value.warn {
  color: var(--warn);
}

.atr-info {
  padding: 10px;
  background: var(--bg);
  border-radius: 6px;
}

.atr-empty {
  font-size: 11px;
  color: var(--muted);
  text-align: center;
  padding: 10px;
}
</style>
