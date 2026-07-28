<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  quote: any
  kind: string
}>()

function fmtNum(v: any, d = 2) {
  return v == null ? '--' : (+v).toFixed(d)
}

function fmtVol(v: any) {
  if (v == null) return '--'
  v = +v
  if (Math.abs(v) >= 1e8) return (v / 1e8).toFixed(2) + '亿'
  if (Math.abs(v) >= 1e4) return (v / 1e4).toFixed(2) + '万'
  return v.toFixed(0)
}

const changeColor = computed(() => {
  if (!props.quote) return 'var(--text)'
  const chg = props.quote.change || 0
  return chg > 0 ? 'var(--up)' : chg < 0 ? 'var(--down)' : 'var(--text)'
})

const chgText = computed(() => {
  if (!props.quote) return '--'
  const chg = props.quote.change || 0
  const pct = props.quote.changepct || 0
  return `${chg > 0 ? '+' : ''}${fmtNum(chg)}  (${pct > 0 ? '+' : ''}${fmtNum(pct)}%)`
})

const kvRows = computed(() => {
  if (!props.quote) return []
  const q = props.quote
  const rows: [string, any][] = [
    ['今开', q.open],
    ['昨收/结', q.preclose],
    ['最高', q.high],
    ['最低', q.low],
    ['成交量', fmtVol(q.volume)],
    ['成交额', fmtVol(q.amount)],
  ]
  if (props.kind === 'stock') {
    rows.push(['换手率', q.turnover == null ? '--' : fmtNum(q.turnover) + '%'])
    rows.push(['市盈率', q.pe])
  } else {
    rows.push(['持仓量', fmtVol(q.openinterest)])
  }
  return rows
})

const depthBids = computed(() => props.quote?.bids || [])
const depthAsks = computed(() => props.quote?.asks || [])
</script>

<template>
  <div class="card">
    <h2>行情数据 <small>{{ quote?.time || '' }}</small><span class="pill" :class="kind">{{ kind === 'future' ? '期货' : '股票' }}</span></h2>
    <div class="name">{{ quote ? `${quote.name} (${quote.code}) · ${quote.currency}${quote.realtime === false ? ' · 收盘参考(非实时)' : ''}` : '--' }}</div>
    <div class="price-row">
      <div class="price" :style="{ color: changeColor }">{{ quote?.price != null ? fmtNum(quote.price) : '--' }}</div>
      <div class="chg" :style="{ color: changeColor }">{{ chgText }}</div>
    </div>
    <div class="kv">
      <div v-for="[k, v] in kvRows" :key="k">
        <span>{{ k }}</span>
        <span>{{ v == null ? '--' : (typeof v === 'number' ? fmtNum(v) : v) }}</span>
      </div>
    </div>
    <div class="depth" v-if="kind === 'stock' && depthBids.length">
      <div class="hdr">卖盘</div>
      <div v-for="(a, i) in [...depthAsks].reverse()" :key="'a' + i" class="row ask">
        <span>卖{{ depthAsks.length - i }} {{ fmtNum(a.price) }}</span>
        <span>{{ fmtVol(a.vol) }}</span>
      </div>
      <div class="hdr">买盘</div>
      <div v-for="(b, i) in depthBids" :key="'b' + i" class="row bid">
        <span>买{{ i + 1 }} {{ fmtNum(b.price) }}</span>
        <span>{{ fmtVol(b.vol) }}</span>
      </div>
    </div>
    <div class="depth" v-else>
      <div class="hdr">提示</div>
      <div class="row"><span>期货实时盘口以持仓/成交量为核心</span></div>
    </div>
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

.name {
  font-size: 13px;
  color: var(--text);
  margin-bottom: 6px;
}

.price-row {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.price {
  font-size: 34px;
  font-weight: 700;
  line-height: 1;
}

.chg {
  font-size: 15px;
  font-weight: 600;
}

.kv {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 6px 14px;
  margin-top: 10px;
}

.kv div {
  display: flex;
  justify-content: space-between;
  border-bottom: 1px dashed var(--line);
  padding-bottom: 3px;
}

.kv span:first-child {
  color: var(--muted);
}

.depth {
  margin-top: 12px;
  font-size: 12px;
}

.depth .row {
  display: flex;
  justify-content: space-between;
  padding: 2px 6px;
  border-radius: 4px;
}

.depth .ask {
  color: var(--down);
}

.depth .bid {
  color: var(--up);
}

.depth .hdr {
  color: var(--muted);
  font-size: 11px;
  border-bottom: 1px solid var(--line);
  padding-bottom: 4px;
  margin-bottom: 4px;
}

.pill {
  display: inline-block;
  padding: 1px 7px;
  border-radius: 10px;
  font-size: 11px;
  margin-left: 6px;
}

.pill.stock {
  background: rgba(88, 166, 255, 0.15);
  color: var(--accent);
}

.pill.future {
  background: rgba(210, 153, 34, 0.15);
  color: var(--warn);
}
</style>
