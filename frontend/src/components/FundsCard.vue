<script setup>
import { computed } from 'vue'

const props = defineProps({
  funds: Object,
  kind: String,
  quote: Object
})

function fmtNum(v, d = 2) {
  if (v == null || v === '--') return '--'
  return (+v).toFixed(d)
}

function fmtVol(v) {
  if (v == null) return '--'
  v = +v
  if (Math.abs(v) >= 1e8) return (v / 1e8).toFixed(2) + '亿'
  if (Math.abs(v) >= 1e4) return (v / 1e4).toFixed(2) + '万'
  return v.toFixed(0)
}

function fmtMoney(v) {
  if (v == null) return '--'
  v = +v
  if (Math.abs(v) >= 1e12) return (v / 1e12).toFixed(2) + '万亿'
  if (Math.abs(v) >= 1e8) return (v / 1e8).toFixed(2) + '亿'
  if (Math.abs(v) >= 1e4) return (v / 1e4).toFixed(2) + '万'
  return v.toFixed(0)
}

// 外内盘比分析
const oiRatio = computed(() => {
  const outer = props.funds?.outer || props.quote?.outer
  const inner = props.funds?.inner || props.quote?.inner
  if (!outer || !inner || inner === 0) return null
  return (outer / inner).toFixed(2)
})

const oiAnalysis = computed(() => {
  if (!oiRatio.value) return null
  const ratio = parseFloat(oiRatio.value)
  if (ratio > 1.5) return { text: '强烈看多', color: '#ef232a', desc: '主动买盘远超卖盘' }
  if (ratio > 1.2) return { text: '偏多', color: '#ef232a', desc: '买盘力量较强' }
  if (ratio > 0.8) return { text: '均衡', color: '#58a6ff', desc: '多空力量平衡' }
  if (ratio > 0.5) return { text: '偏空', color: '#14b143', desc: '卖盘力量较强' }
  return { text: '强烈看空', color: '#14b143', desc: '主动卖盘远超买盘' }
})

// 主力资金分析
const mainFundAnalysis = computed(() => {
  const mainNet = props.funds?.main_net
  if (mainNet == null) return null
  if (mainNet > 0) return { text: '净流入', color: '#ef232a' }
  if (mainNet < 0) return { text: '净流出', color: '#14b143' }
  return { text: '平衡', color: '#58a6ff' }
})

const kvRows = computed(() => {
  const f = props.funds || {}
  const q = props.quote || {}
  const rows = []
  
  if (props.kind === 'stock') {
    // 成交额
    if (f.amount || q.amount) {
      rows.push({ label: '成交额', value: fmtMoney(f.amount || q.amount), icon: '💰' })
    }
    
    // 成交量
    if (f.volume || q.volume) {
      rows.push({ label: '成交量', value: fmtVol(f.volume || q.volume), icon: '📊' })
    }
    
    // 换手率
    if (f.turnover || q.turnover) {
      rows.push({ label: '换手率', value: fmtNum(f.turnover || q.turnover) + '%', icon: '🔄' })
    }
    
    // 外盘
    if (f.outer || q.outer) {
      rows.push({ 
        label: '外盘(主动买)', 
        value: fmtVol(f.outer || q.outer), 
        icon: '🔴',
        highlight: true
      })
    }
    
    // 内盘
    if (f.inner || q.inner) {
      rows.push({ 
        label: '内盘(主动卖)', 
        value: fmtVol(f.inner || q.inner), 
        icon: '🟢',
        highlight: true
      })
    }
    
    // 外内盘比
    if (oiRatio.value) {
      rows.push({ 
        label: '外内盘比', 
        value: oiRatio.value, 
        icon: '⚖️',
        rating: oiAnalysis.value
      })
    }
    
    // 主力净流入
    if (f.main_net != null) {
      rows.push({ 
        label: '主力净流入', 
        value: fmtMoney(f.main_net), 
        icon: '🏦',
        rating: mainFundAnalysis.value,
        color: f.main_net >= 0 ? '#ef232a' : '#14b143'
      })
    }
    
    // 超大单净流入
    if (f.super_net != null) {
      rows.push({ label: '超大单净流入', value: fmtMoney(f.super_net), icon: '🐋', color: f.super_net >= 0 ? '#ef232a' : '#14b143' })
    }
    
    // 大单净流入
    if (f.big_net != null) {
      rows.push({ label: '大单净流入', value: fmtMoney(f.big_net), icon: '🦈', color: f.big_net >= 0 ? '#ef232a' : '#14b143' })
    }
  } else {
    // 期货
    if (f.openinterest || q.openinterest) {
      rows.push({ label: '持仓量', value: fmtVol(f.openinterest || q.openinterest), icon: '📊' })
    }
    if (f.volume || q.volume) {
      rows.push({ label: '成交量', value: fmtVol(f.volume || q.volume), icon: '📈' })
    }
  }
  
  return rows.filter(r => r.value != null && r.value !== '--')
})
</script>

<template>
  <div class="card">
    <h2>
      <span class="title-icon">💰</span>
      资金面
      <small>{{ kind === 'future' ? '持仓分析' : '资金博弈' }}</small>
    </h2>
    
    <div class="kv-grid">
      <div v-for="row in kvRows" :key="row.label" class="kv-item" :class="{ highlight: row.highlight }">
        <div class="kv-label">
          <span class="kv-icon">{{ row.icon }}</span>
          {{ row.label }}
        </div>
        <div class="kv-value" :style="{ color: row.color || 'var(--text)' }">
          {{ row.value }}
          <span v-if="row.rating" class="rating" :style="{ color: row.rating.color }">
            {{ row.rating.text }}
          </span>
        </div>
      </div>
    </div>
    
    <div class="insight" v-if="oiAnalysis">
      <span class="insight-icon">💡</span>
      <span>
        多空力量<strong :style="{ color: oiAnalysis.color }">{{ oiAnalysis.text }}</strong>
        ，{{ oiAnalysis.desc }}
      </span>
    </div>
  </div>
</template>

<style scoped>
.card {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 10px;
  padding: 12px;
}

h2 {
  margin: 0 0 12px;
  font-size: 13px;
  color: var(--accent);
  display: flex;
  align-items: center;
  gap: 6px;
}

.title-icon {
  font-size: 14px;
}

h2 small {
  color: var(--muted);
  font-weight: normal;
  font-size: 11px;
  margin-left: auto;
}

.kv-grid {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.kv-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 8px;
  background: var(--card2);
  border-radius: 6px;
}

.kv-item.highlight {
  border-left: 2px solid var(--accent);
}

.kv-label {
  font-size: 11px;
  color: var(--muted);
  display: flex;
  align-items: center;
  gap: 6px;
}

.kv-icon {
  font-size: 12px;
}

.kv-value {
  font-size: 12px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 6px;
}

.rating {
  font-size: 10px;
  padding: 1px 6px;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.05);
}

.insight {
  margin-top: 10px;
  padding: 8px 10px;
  background: rgba(88, 166, 255, 0.08);
  border: 1px solid rgba(88, 166, 255, 0.2);
  border-radius: 6px;
  font-size: 11px;
  color: var(--text);
  display: flex;
  align-items: center;
  gap: 6px;
}

.insight-icon {
  font-size: 12px;
}

strong {
  font-weight: 600;
}
</style>
