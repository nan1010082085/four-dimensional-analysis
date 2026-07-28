<script setup lang="ts">
const props = defineProps<{
  code: string
  period: string
  autoRefresh: boolean
  status: string
  isLive: boolean
}>()

const emit = defineEmits<{
  'update:code': [code: string]
  'update:period': [period: string]
  'update:auto-refresh': [val: boolean]
}>()

const quickCodes = [
  { code: 'sh600519', label: '茅台' },
  { code: 'sz000001', label: '平安银行' },
  { code: 'sh510300', label: '沪深300ETF' },
  { code: 'IF0', label: 'IF主连' },
  { code: 'rb0', label: '螺纹主连' },
  { code: 'au0', label: '黄金主连' },
  { code: 'hk00700', label: '腾讯' },
]

const periods = [
  { value: 'minute', label: '分时' },
  { value: 'day', label: '日K' },
  { value: 'week', label: '周K' },
  { value: 'month', label: '月K' },
  { value: '60', label: '60分' },
  { value: '15', label: '15分' },
]

let inputCode = props.code

function onKeyDown(e: KeyboardEvent) {
  if (e.key === 'Enter') {
    emit('update:code', inputCode)
  }
}

function selectQuick(code: string) {
  inputCode = code
  emit('update:code', code)
}

function selectPeriod(p: string) {
  emit('update:period', p)
}

function onAutoChange(e: Event) {
  emit('update:auto-refresh', (e.target as HTMLInputElement).checked)
}
</script>

<template>
  <header>
    <div>
      <h1>四维分析盯盘台</h1>
      <div class="sub">行情 · 技术 · 基本面 · 资金 &nbsp;|&nbsp; 实时免费数据源</div>
    </div>
    <input
      :value="code"
      @input="inputCode = ($event.target as HTMLInputElement).value"
      @keydown="onKeyDown"
      placeholder="股票/期货代码"
      title="股票如 sh600519/600519/hk00700/usAAPL，期货如 IF0/rb0/IF2508"
    />
    <div class="chips">
      <span
        v-for="item in quickCodes"
        :key="item.code"
        class="chip"
        :class="{ active: code === item.code }"
        @click="selectQuick(item.code)"
      >{{ item.label }}</span>
    </div>
    <div class="seg">
      <button
        v-for="p in periods"
        :key="p.value"
        :class="{ active: period === p.value }"
        @click="selectPeriod(p.value)"
      >{{ p.label }}</button>
    </div>
    <label class="auto">
      <input type="checkbox" :checked="autoRefresh" @change="onAutoChange" />
      自动刷新(3s)
    </label>
    <div class="status">
      <span class="dot" :class="{ live: isLive }"></span>
      <span>{{ status }}</span>
    </div>
  </header>
</template>

<style scoped>
header {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  padding: 12px 16px;
  background: var(--card);
  border-bottom: 1px solid var(--line);
}

h1 {
  font-size: 15px;
  margin: 0;
  color: var(--accent);
  white-space: nowrap;
}

.sub {
  color: var(--muted);
  font-size: 11px;
}

input {
  padding: 6px 10px;
  background: var(--card2);
  border: 1px solid var(--line);
  color: var(--text);
  border-radius: 6px;
  width: 120px;
  font-size: 13px;
}

.chips {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.chip {
  padding: 5px 10px;
  background: var(--card2);
  border: 1px solid var(--line);
  border-radius: 14px;
  cursor: pointer;
  color: var(--muted);
  font-size: 12px;
}

.chip:hover {
  color: var(--text);
  border-color: var(--accent);
}

.chip.active {
  background: var(--accent);
  color: #04101f;
  border-color: var(--accent);
}

.seg {
  display: flex;
  gap: 4px;
}

.seg button {
  padding: 5px 9px;
  background: var(--card2);
  border: 1px solid var(--line);
  color: var(--muted);
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
}

.seg button.active {
  color: var(--text);
  border-color: var(--accent);
}

.auto {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--muted);
  font-size: 12px;
}

.status {
  margin-left: auto;
  color: var(--muted);
  font-size: 12px;
}

.dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--muted);
  margin-right: 5px;
}

.dot.live {
  background: var(--down);
  box-shadow: 0 0 6px var(--down);
}
</style>
