<template>
  <div class="paper-trading">
    <div class="panel-header">
      <h3>💰 模拟盘交易</h3>
      <div class="header-actions">
        <button class="reset-btn" @click="resetPaper" title="重置">↻</button>
        <button class="close-btn" @click="$emit('close')" title="关闭">×</button>
      </div>
    </div>
    
    <!-- 资金概览 -->
    <div class="stats-grid">
      <div class="stat-item">
        <span class="stat-label">总资产</span>
        <span class="stat-value">{{ formatMoney(status.total_assets) }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">可用资金</span>
        <span class="stat-value">{{ formatMoney(status.capital) }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">总盈亏</span>
        <span class="stat-value" :class="status.total_pnl >= 0 ? 'up' : 'down'">
          {{ status.total_pnl >= 0 ? '+' : '' }}{{ formatMoney(status.total_pnl) }}
        </span>
      </div>
      <div class="stat-item">
        <span class="stat-label">收益率</span>
        <span class="stat-value" :class="status.total_pnl_pct >= 0 ? 'up' : 'down'">
          {{ status.total_pnl_pct >= 0 ? '+' : '' }}{{ status.total_pnl_pct }}%
        </span>
      </div>
      <div class="stat-item">
        <span class="stat-label">胜率</span>
        <span class="stat-value">{{ status.win_rate }}%</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">交易次数</span>
        <span class="stat-value">{{ status.trades_count }}</span>
      </div>
    </div>
    
    <!-- 交易设置 -->
    <div class="settings-section">
      <div class="section-header" @click="showSettings = !showSettings">
        <span>⚙️ 交易设置</span>
        <span class="toggle">{{ showSettings ? '▼' : '▶' }}</span>
      </div>
      <div v-if="showSettings" class="settings-content">
        <div class="setting-row">
          <label>初始资金</label>
          <input v-model.number="initialCapital" type="number" placeholder="100000" />
        </div>
        <div class="setting-row">
          <label>默认止损</label>
          <select v-model.number="defaultStopLoss">
            <option :value="1">1%</option>
            <option :value="2">2%</option>
            <option :value="3">3%</option>
            <option :value="5">5%</option>
            <option :value="8">8%</option>
            <option :value="10">10%</option>
          </select>
        </div>
        <div class="setting-row">
          <label>默认止盈</label>
          <select v-model.number="defaultTakeProfit">
            <option :value="3">3%</option>
            <option :value="5">5%</option>
            <option :value="8">8%</option>
            <option :value="10">10%</option>
            <option :value="15">15%</option>
            <option :value="20">20%</option>
          </select>
        </div>
        <div class="setting-row">
          <label>单笔风险</label>
          <select v-model.number="riskPerTrade">
            <option :value="1">1%</option>
            <option :value="2">2%</option>
            <option :value="3">3%</option>
            <option :value="5">5%</option>
          </select>
        </div>
        <div class="setting-row">
          <label>默认数量</label>
          <input v-model.number="defaultQty" type="number" step="100" placeholder="100" />
        </div>
        <div class="setting-row">
          <label>自动交易</label>
          <select v-model="autoTradeMode">
            <option value="manual">手动确认</option>
            <option value="auto_buy">自动买入</option>
            <option value="auto_sell">自动卖出</option>
            <option value="auto_all">全自动</option>
          </select>
        </div>
      </div>
    </div>
    
    <!-- 快捷交易 -->
    <div class="trade-section">
      <div class="trade-header">
        <span>快捷交易</span>
        <span class="current-price" v-if="quote">
          {{ quote.name }} {{ quote.price }}
        </span>
      </div>
      <div class="trade-form">
        <div class="form-row">
          <label>数量</label>
          <input v-model.number="tradeQty" type="number" :step="100" :placeholder="defaultQty" />
        </div>
        <div class="form-row">
          <label>止损价</label>
          <input v-model.number="stopLoss" type="number" :placeholder="stopLossPlaceholder" />
        </div>
        <div class="form-row">
          <label>止盈价</label>
          <input v-model.number="takeProfit" type="number" :placeholder="takeProfitPlaceholder" />
        </div>
        <div class="trade-buttons">
          <button class="buy-btn" @click="executeBuy" :disabled="!quote">
            买入 {{ quote?.name || '' }}
          </button>
          <button class="sell-btn" @click="executeSell" :disabled="!hasPosition">
            卖出 {{ quote?.name || '' }}
          </button>
        </div>
      </div>
    </div>
    
    <!-- 持仓列表 -->
    <div class="positions-section" v-if="status.positions.length > 0">
      <div class="section-title">当前持仓</div>
      <div class="position-list">
        <div v-for="pos in status.positions" :key="pos.code" class="position-item">
          <div class="pos-header">
            <span class="pos-name">{{ pos.name }}</span>
            <span class="pos-code">{{ pos.code }}</span>
          </div>
          <div class="pos-details">
            <div class="pos-row">
              <span>数量: {{ pos.qty }}</span>
              <span>成本: {{ pos.avg_price }}</span>
            </div>
            <div class="pos-row">
              <span v-if="pos.stop_loss" class="stop-loss">止损: {{ pos.stop_loss }}</span>
              <span v-if="pos.take_profit" class="take-profit">止盈: {{ pos.take_profit }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 最近交易 -->
    <div class="trades-section">
      <div class="section-title">最近交易</div>
      <div class="trade-list">
        <div v-for="trade in recentTrades" :key="trade.time" class="trade-item" :class="trade.type">
          <div class="trade-header">
            <span class="trade-type">{{ trade.type === 'buy' ? '买入' : '卖出' }}</span>
            <span class="trade-time">{{ formatTime(trade.time) }}</span>
          </div>
          <div class="trade-details">
            <span>{{ trade.name }}</span>
            <span>{{ trade.price }} × {{ trade.qty }}</span>
            <span v-if="trade.pnl !== undefined" :class="trade.pnl >= 0 ? 'up' : 'down'">
              {{ trade.pnl >= 0 ? '+' : '' }}{{ trade.pnl }}
            </span>
          </div>
          <div v-if="trade.reason" class="trade-reason">{{ trade.reason }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { fetchApi } from '../api.js'

const props = defineProps({
  code: String,
  quote: Object,
  signal: Object
})

defineEmits(['close'])

const status = ref({
  capital: 100000,
  total_assets: 100000,
  total_pnl: 0,
  total_pnl_pct: 0,
  positions: [],
  trades_count: 0,
  win_rate: 0,
  balance_history: []
})

const recentTrades = ref([])
const tradeQty = ref(100)
const stopLoss = ref(null)
const takeProfit = ref(null)
const showSettings = ref(false)

// 交易设置
const initialCapital = ref(100000)
const defaultStopLoss = ref(2)
const defaultTakeProfit = ref(5)
const riskPerTrade = ref(2)
const defaultQty = ref(100)
const autoTradeMode = ref('manual') // manual / auto_buy / auto_sell / auto_all

const hasPosition = computed(() => {
  return status.value.positions.some(p => p.code === props.code)
})

const stopLossPlaceholder = computed(() => {
  if (!props.quote?.price) return '止损价'
  return (props.quote.price * (1 - defaultStopLoss.value / 100)).toFixed(2)
})

const takeProfitPlaceholder = computed(() => {
  if (!props.quote?.price) return '止盈价'
  return (props.quote.price * (1 + defaultTakeProfit.value / 100)).toFixed(2)
})

// 监听信号变化，自动填入止损止盈
watch(() => props.signal, (newSignal) => {
  if (newSignal) {
    // 自动填入止损止盈
    if (newSignal.stop_loss) {
      stopLoss.value = newSignal.stop_loss
    } else if (props.quote?.price) {
      stopLoss.value = parseFloat((props.quote.price * (1 - defaultStopLoss.value / 100)).toFixed(2))
    }
    
    if (newSignal.take_profit_1) {
      takeProfit.value = newSignal.take_profit_1
    } else if (props.quote?.price) {
      takeProfit.value = parseFloat((props.quote.price * (1 + defaultTakeProfit.value / 100)).toFixed(2))
    }
    
    // 自动交易
    if (autoTradeMode.value === 'auto_all' || 
        (autoTradeMode.value === 'auto_buy' && newSignal.type === 'buy') ||
        (autoTradeMode.value === 'auto_sell' && newSignal.type === 'sell')) {
      if (newSignal.type === 'buy' && !hasPosition.value) {
        executeBuy()
      } else if (newSignal.type === 'sell' && hasPosition.value) {
        executeSell()
      }
    }
  }
}, { deep: true })

// 记录已自动填入止损止盈的股票，切换股票后允许重新填入
let lastFillCode = ''

// 切换股票代码时，重置止损止盈（让价格watch按新价格重新计算）
watch(() => props.code, () => {
  lastFillCode = ''
  stopLoss.value = null
  takeProfit.value = null
  tradeQty.value = defaultQty.value
})

// 监听价格变化，自动填入止损止盈（每个股票首次到达价格时填入，之后尊重手动修改）
watch(() => props.quote?.price, (newPrice) => {
  if (!newPrice) return
  if (lastFillCode !== props.code || !stopLoss.value) {
    stopLoss.value = parseFloat((newPrice * (1 - defaultStopLoss.value / 100)).toFixed(2))
    takeProfit.value = parseFloat((newPrice * (1 + defaultTakeProfit.value / 100)).toFixed(2))
    tradeQty.value = defaultQty.value
    lastFillCode = props.code
  }
}, { immediate: true })

// 加载状态
async function loadStatus() {
  try {
    const data = await fetchApi('/api/paper/status')
    if (data.ok) {
      status.value = data.data
    }
  } catch (e) {
    console.error('加载模拟盘状态失败:', e)
  }
}

// 加载交易记录
async function loadTrades() {
  try {
    const data = await fetchApi('/api/paper/trades?limit=10')
    if (data.ok) {
      recentTrades.value = data.data.reverse()
    }
  } catch (e) {
    console.error('加载交易记录失败:', e)
  }
}

// 买入
async function executeBuy() {
  if (!props.quote) return
  
  const sl = stopLoss.value || parseFloat(stopLossPlaceholder.value)
  const tp = takeProfit.value || parseFloat(takeProfitPlaceholder.value)
  
  try {
    const data = await fetchApi('/api/paper/buy', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        code: props.code,
        name: props.quote.name,
        price: props.quote.price,
        qty: tradeQty.value || defaultQty.value,
        stop_loss: sl,
        take_profit: tp,
        reason: props.signal ? `AI信号: ${props.signal.reason}` : '手动买入'
      })
    })
    
    if (data.ok) {
      alert('买入成功！')
      loadStatus()
      loadTrades()
    } else {
      alert('买入失败: ' + data.data.error)
    }
  } catch (e) {
    alert('买入失败: ' + e.message)
  }
}

// 卖出
async function executeSell() {
  if (!props.quote) return
  
  const pos = status.value.positions.find(p => p.code === props.code)
  if (!pos) return
  
  try {
    const data = await fetchApi('/api/paper/sell', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        code: props.code,
        price: props.quote.price,
        qty: pos.qty,
        reason: props.signal ? `AI信号: ${props.signal.reason}` : '手动卖出'
      })
    })
    
    if (data.ok) {
      const trade = data.data.trade
      alert(`卖出成功！盈亏: ${trade.pnl >= 0 ? '+' : ''}${trade.pnl}`)
      loadStatus()
      loadTrades()
    } else {
      alert('卖出失败: ' + data.data.error)
    }
  } catch (e) {
    alert('卖出失败: ' + e.message)
  }
}

// 重置
async function resetPaper() {
  if (!confirm('确定要重置模拟盘吗？所有数据将清空。')) return
  
  try {
    await fetchApi('/api/paper/reset', { method: 'POST' })
    loadStatus()
    loadTrades()
    alert('模拟盘已重置')
  } catch (e) {
    alert('重置失败: ' + e.message)
  }
}

function formatMoney(val) {
  if (val === undefined || val === null) return '--'
  return Number(val).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function formatTime(time) {
  if (!time) return ''
  return time.substring(5, 16)
}

onMounted(() => {
  loadStatus()
  loadTrades()
})
</script>

<style scoped>
.paper-trading {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--line);
}

.panel-header h3 {
  margin: 0;
  font-size: 15px;
  color: var(--accent);
}

.header-actions {
  display: flex;
  gap: 8px;
}

.reset-btn,
.close-btn {
  width: 28px;
  height: 28px;
  background: transparent;
  border: 1px solid var(--line);
  color: var(--muted);
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.reset-btn:hover,
.close-btn:hover {
  border-color: var(--accent);
  color: var(--accent);
}

.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 8px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  padding: 10px;
  background: var(--card);
  border-radius: 8px;
}

.stat-label {
  font-size: 10px;
  color: var(--muted);
  margin-bottom: 4px;
}

.stat-value {
  font-size: 14px;
  font-weight: bold;
  color: var(--text);
}

.stat-value.up { color: #ef232a; }
.stat-value.down { color: #14b143; }

.settings-section {
  background: var(--card);
  border-radius: 8px;
  overflow: hidden;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  cursor: pointer;
  font-size: 12px;
  color: var(--muted);
}

.section-header:hover {
  background: var(--card2);
}

.toggle {
  font-size: 10px;
}

.settings-content {
  padding: 0 12px 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.setting-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.setting-row label {
  font-size: 11px;
  color: var(--muted);
}

.setting-row input,
.setting-row select {
  width: 120px;
  padding: 4px 8px;
  background: var(--bg);
  border: 1px solid var(--line);
  color: var(--text);
  border-radius: 4px;
  font-size: 11px;
}

.trade-section {
  background: var(--card);
  border-radius: 8px;
  padding: 12px;
}

.trade-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  font-size: 12px;
}

.current-price {
  color: var(--accent);
  font-weight: bold;
}

.trade-form {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.form-row label {
  font-size: 11px;
  color: var(--muted);
  min-width: 40px;
}

.form-row input {
  flex: 1;
  padding: 6px 8px;
  background: var(--bg);
  border: 1px solid var(--line);
  color: var(--text);
  border-radius: 4px;
  font-size: 12px;
}

.form-row input:focus {
  outline: none;
  border-color: var(--accent);
}

.trade-buttons {
  display: flex;
  gap: 8px;
  margin-top: 4px;
}

.buy-btn,
.sell-btn {
  flex: 1;
  padding: 10px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  font-weight: bold;
}

.buy-btn {
  background: linear-gradient(135deg, #ef232a 0%, #c41e24 100%);
  color: #fff;
}

.buy-btn:hover:not(:disabled) { opacity: 0.9; }

.sell-btn {
  background: linear-gradient(135deg, #14b143 0%, #0e8a35 100%);
  color: #fff;
}

.sell-btn:hover:not(:disabled) { opacity: 0.9; }

.buy-btn:disabled,
.sell-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.section-title {
  font-size: 12px;
  color: var(--muted);
  margin-bottom: 8px;
  font-weight: bold;
}

.positions-section,
.trades-section {
  background: var(--card);
  border-radius: 8px;
  padding: 12px;
  max-height: 200px;
  overflow-y: auto;
}

.position-list,
.trade-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.position-item,
.trade-item {
  padding: 8px;
  background: var(--card2);
  border-radius: 6px;
  font-size: 11px;
}

.pos-header,
.trade-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
}

.pos-name,
.trade-type {
  font-weight: bold;
  color: var(--text);
}

.pos-code,
.trade-time {
  color: var(--muted);
  font-size: 10px;
}

.pos-details,
.trade-details {
  display: flex;
  justify-content: space-between;
  color: var(--muted);
}

.stop-loss { color: #14b143; }
.take-profit { color: #ef232a; }

.trade-item.buy .trade-type { color: #ef232a; }
.trade-item.sell .trade-type { color: #14b143; }

.trade-reason {
  margin-top: 4px;
  font-size: 10px;
  color: var(--muted);
  font-style: italic;
}

.up { color: #ef232a; }
.down { color: #14b143; }
</style>
