<script setup>
import { computed } from 'vue'

const props = defineProps({
  fundamentals: Object,
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

// 估值评级
const peRating = computed(() => {
  const pe = props.fundamentals?.pe || props.quote?.pe
  if (!pe) return null
  if (pe < 0) return { text: '亏损', color: '#ef232a' }
  if (pe < 15) return { text: '低估', color: '#14b143' }
  if (pe < 25) return { text: '合理', color: '#58a6ff' }
  if (pe < 40) return { text: '偏高', color: '#d29922' }
  return { text: '高估', color: '#ef232a' }
})

// 换手率评级
const turnoverRating = computed(() => {
  const t = props.fundamentals?.turnover || props.quote?.turnover
  if (!t) return null
  if (t < 1) return { text: '低迷', color: '#8b949e' }
  if (t < 3) return { text: '正常', color: '#58a6ff' }
  if (t < 5) return { text: '活跃', color: '#d29922' }
  return { text: '异常', color: '#ef232a' }
})

// 量比
const volumeRatio = computed(() => {
  if (!props.quote?.volume || !props.fundamentals?.avg_volume) return null
  return (props.quote.volume / props.fundamentals.avg_volume).toFixed(2)
})

const kvRows = computed(() => {
  const f = props.fundamentals || {}
  const q = props.quote || {}
  const rows = []
  
  if (props.kind === 'future') {
    // 期货特有
    if (f.openinterest != null || q.openinterest != null) {
      rows.push({ label: '持仓量', value: fmtVol(f.openinterest || q.openinterest), icon: '📊' })
    }
    rows.push(
      { label: '成交量', value: fmtVol(f.volume || q.volume), icon: '📈' },
    )
  } else {
    // 股票特有
    const pe = f.pe || q.pe
    if (pe != null) {
      rows.push({ 
        label: '市盈率(PE)', 
        value: fmtNum(pe), 
        icon: '💰',
        rating: peRating.value
      })
    }
    
    if (f.pb != null) {
      rows.push({ label: '市净率(PB)', value: fmtNum(f.pb), icon: '📗' })
    }
    
    if (f.total_mv != null) {
      rows.push({ label: '总市值', value: fmtMoney(f.total_mv), icon: '🏦' })
    }
    
    if (f.circ_mv != null) {
      rows.push({ label: '流通市值', value: fmtMoney(f.circ_mv), icon: '💎' })
    }
    
    const turnover = f.turnover || q.turnover
    if (turnover != null) {
      rows.push({ 
        label: '换手率', 
        value: fmtNum(turnover) + '%', 
        icon: '🔄',
        rating: turnoverRating.value
      })
    }
    
    rows.push(
      { label: '成交量', value: fmtVol(f.volume || q.volume), icon: '📊' },
      { label: '成交额', value: fmtMoney(f.amount || q.amount), icon: '💵' },
    )
    
    if (volumeRatio.value) {
      rows.push({ label: '量比', value: volumeRatio.value, icon: '⚖️' })
    }
  }
  
  return rows.filter(r => r.value != null && r.value !== '--')
})
</script>

<template>
  <div class="card">
    <h2>
      <span class="title-icon">📊</span>
      基本面
      <small>{{ kind === 'future' ? '期货数据' : '估值分析' }}</small>
    </h2>
    
    <div class="kv-grid">
      <div v-for="row in kvRows" :key="row.label" class="kv-item">
        <div class="kv-label">
          <span class="kv-icon">{{ row.icon }}</span>
          {{ row.label }}
        </div>
        <div class="kv-value">
          {{ row.value }}
          <span v-if="row.rating" class="rating" :style="{ color: row.rating.color }">
            {{ row.rating.text }}
          </span>
        </div>
      </div>
    </div>
    
    <div class="insight" v-if="peRating">
      <span class="insight-icon">💡</span>
      <span v-if="kind === 'stock'">
        当前估值<strong :style="{ color: peRating.color }">{{ peRating.text }}</strong>
        <template v-if="peRating.text === '低估'">，具备安全边际</template>
        <template v-else-if="peRating.text === '高估'">，注意风险</template>
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
  color: var(--text);
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
