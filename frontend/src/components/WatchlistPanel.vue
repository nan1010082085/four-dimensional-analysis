<template>
  <div class="watchlist-panel">
    <div class="panel-header">
      <h3>自选监控</h3>
      <button class="add-btn" @click="showAdd = !showAdd">+</button>
    </div>
    
    <div v-if="showAdd" class="add-form">
      <input 
        v-model="newCode" 
        placeholder="输入代码"
        @keydown.enter="addStock"
      />
      <button @click="addStock">添加</button>
    </div>
    
    <div class="stock-list">
      <div 
        v-for="stock in watchlist" 
        :key="stock.code"
        class="stock-item"
        :class="{ active: selectedCode === stock.code }"
        @click="selectStock(stock)"
      >
        <div class="stock-info">
          <span class="stock-name">{{ stock.name }}</span>
          <span class="stock-code">{{ stock.code }}</span>
        </div>
        <div class="stock-price" :class="stock.change >= 0 ? 'up' : 'down'">
          {{ stock.price || '--' }}
        </div>
        <div class="stock-change" :class="stock.change >= 0 ? 'up' : 'down'">
          {{ stock.change >= 0 ? '+' : '' }}{{ stock.changepct || '0' }}%
        </div>
        <div class="stock-signal">
          <span v-if="stock.signal === 'buy'" class="signal-buy">▲入</span>
          <span v-else-if="stock.signal === 'sell'" class="signal-sell">▼出</span>
          <span v-else class="signal-none">--</span>
        </div>
        <button class="remove-btn" @click.stop="removeStock(stock.code)">×</button>
      </div>
    </div>
    
    <div class="scan-section">
      <button class="scan-btn" @click="scanSignals" :disabled="scanning">
        {{ scanning ? '扫描中...' : '一键扫描信号' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const emit = defineEmits(['select', 'signal'])

const watchlist = ref([])
const selectedCode = ref('')
const showAdd = ref(false)
const newCode = ref('')
const scanning = ref(false)
let refreshTimer = null

// 预设的热门股票
const defaultStocks = [
  { name: '贵州茅台', code: 'sh600519' },
  { name: '平安银行', code: 'sz000001' },
  { name: '宁德时代', code: 'sz300750' },
  { name: '比亚迪', code: 'sz002594' },
  { name: 'IF主连', code: 'IF0' },
]

onMounted(() => {
  // 从本地存储加载自选股
  const saved = localStorage.getItem('watchlist')
  if (saved) {
    try {
      watchlist.value = JSON.parse(saved)
    } catch (e) {
      watchlist.value = [...defaultStocks]
    }
  } else {
    watchlist.value = [...defaultStocks]
  }
  
  // 初始加载行情
  refreshAll()
  
  // 定时刷新
  refreshTimer = setInterval(refreshAll, 5000)
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
})

function saveWatchlist() {
  localStorage.setItem('watchlist', JSON.stringify(watchlist.value))
}

function addStock() {
  const code = newCode.value.trim()
  if (!code) return
  
  // 检查是否已存在
  if (watchlist.value.find(s => s.code === code)) {
    newCode.value = ''
    showAdd.value = false
    return
  }
  
  watchlist.value.push({
    name: code,
    code: code,
    price: null,
    change: null,
    changepct: null,
    signal: null
  })
  
  newCode.value = ''
  showAdd.value = false
  saveWatchlist()
  refreshStock(code)
}

function removeStock(code) {
  watchlist.value = watchlist.value.filter(s => s.code !== code)
  saveWatchlist()
}

function selectStock(stock) {
  selectedCode.value = stock.code
  emit('select', stock.code)
}

async function refreshStock(code) {
  try {
    const res = await fetch(`/api/quote?code=${encodeURIComponent(code)}`)
    const data = await res.json()
    if (data.ok) {
      const stock = watchlist.value.find(s => s.code === code)
      if (stock) {
        stock.name = data.data.name
        stock.price = data.data.price
        stock.change = data.data.change
        stock.changepct = data.data.changepct
      }
    }
  } catch (e) {
    // ignore
  }
}

async function refreshAll() {
  for (const stock of watchlist.value) {
    await refreshStock(stock.code)
  }
}

async function scanSignals() {
  scanning.value = true
  
  for (const stock of watchlist.value) {
    try {
      const res = await fetch(`/api/analysis?code=${encodeURIComponent(stock.code)}&period=day&limit=20`)
      const data = await res.json()
      if (data.ok && data.kline) {
        // 简单的信号判断
        const bars = data.kline.bars
        const indicators = data.kline.indicators
        if (bars && indicators) {
          const lastBar = bars[bars.length - 1]
          const ma5 = indicators.ma5
          const ma10 = indicators.ma10
          
          if (ma5 && ma10 && ma5.length > 1 && ma10.length > 1) {
            const lastMa5 = ma5[ma5.length - 1]
            const lastMa10 = ma10[ma10.length - 1]
            const prevMa5 = ma5[ma5.length - 2]
            const prevMa10 = ma10[ma10.length - 2]
            
            if (lastMa5 && lastMa10 && prevMa5 && prevMa10) {
              // MA金叉
              if (lastMa5 > lastMa10 && prevMa5 <= prevMa10) {
                stock.signal = 'buy'
                emit('signal', {
                  type: 'buy',
                  code: stock.code,
                  name: stock.name,
                  price: lastBar.close,
                  reasons: ['MA5上穿MA10']
                })
              }
              // MA死叉
              else if (lastMa5 < lastMa10 && prevMa5 >= prevMa10) {
                stock.signal = 'sell'
                emit('signal', {
                  type: 'sell',
                  code: stock.code,
                  name: stock.name,
                  price: lastBar.close,
                  reasons: ['MA5下穿MA10']
                })
              } else {
                stock.signal = null
              }
            }
          }
        }
      }
    } catch (e) {
      // ignore
    }
  }
  
  scanning.value = false
}
</script>

<style scoped>
.watchlist-panel {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 10px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.panel-header h3 {
  margin: 0;
  font-size: 13px;
  color: var(--accent);
}

.add-btn {
  width: 24px;
  height: 24px;
  background: var(--accent);
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.add-form {
  display: flex;
  gap: 8px;
}

.add-form input {
  flex: 1;
  padding: 6px 10px;
  background: var(--card2);
  border: 1px solid var(--line);
  color: var(--text);
  border-radius: 4px;
  font-size: 12px;
}

.add-form button {
  padding: 6px 12px;
  background: var(--accent);
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.stock-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
  max-height: 300px;
  overflow-y: auto;
}

.stock-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  background: var(--card2);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.stock-item:hover {
  border-color: var(--accent);
}

.stock-item.active {
  border: 1px solid var(--accent);
  background: rgba(88, 166, 255, 0.1);
}

.stock-info {
  flex: 1;
  min-width: 0;
}

.stock-name {
  display: block;
  font-size: 12px;
  color: var(--text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.stock-code {
  display: block;
  font-size: 10px;
  color: var(--muted);
}

.stock-price {
  font-size: 13px;
  font-weight: bold;
  min-width: 60px;
  text-align: right;
}

.stock-change {
  font-size: 11px;
  min-width: 50px;
  text-align: right;
}

.stock-signal {
  min-width: 30px;
  text-align: center;
}

.signal-buy {
  color: #14b143;
  font-weight: bold;
  font-size: 11px;
}

.signal-sell {
  color: #ef232a;
  font-weight: bold;
  font-size: 11px;
}

.signal-none {
  color: var(--muted);
  font-size: 11px;
}

.up {
  color: #ef232a;
}

.down {
  color: #14b143;
}

.remove-btn {
  width: 20px;
  height: 20px;
  background: transparent;
  border: none;
  color: var(--muted);
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s;
}

.stock-item:hover .remove-btn {
  opacity: 1;
}

.remove-btn:hover {
  color: #ef232a;
}

.scan-section {
  margin-top: 8px;
}

.scan-btn {
  width: 100%;
  padding: 8px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  font-weight: bold;
}

.scan-btn:hover:not(:disabled) {
  opacity: 0.9;
}

.scan-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
