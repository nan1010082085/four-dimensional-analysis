<template>
  <div class="card ai-card">
    <h2>
      AI 量化分析 
      <small>DeepSeek 量化策略</small>
      <button 
        class="ai-btn" 
        :class="{ loading: loading }"
        :disabled="loading"
        @click="requestAnalysis"
      >
        {{ loading ? '分析中...' : '开始分析' }}
      </button>
    </h2>
    
    <div class="analysis-types">
      <div class="type-group">
        <span class="group-label">基础分析</span>
        <button 
          v-for="t in basicTypes" 
          :key="t.value"
          :class="{ active: analysisType === t.value }"
          @click="analysisType = t.value"
        >
          {{ t.label }}
        </button>
      </div>
      <div class="type-group">
        <span class="group-label">量化策略</span>
        <button 
          v-for="t in quantTypes" 
          :key="t.value"
          :class="{ active: analysisType === t.value }"
          @click="analysisType = t.value"
        >
          {{ t.label }}
        </button>
      </div>
    </div>
    
    <div v-if="error" class="error">{{ error }}</div>
    
    <div v-if="analysis" class="analysis-content">
      <div class="analysis-text" v-html="formatAnalysis(analysis)"></div>
    </div>
    
    <div v-else-if="!loading" class="placeholder">
      点击「开始分析」获取 AI 量化分析报告
    </div>
  </div>
</template>

<script setup>
import { ref, defineProps } from 'vue'
import { fetchApi } from '../api.js'

const props = defineProps({
  code: String,
  period: String,
  kind: String
})

const loading = ref(false)
const analysis = ref('')
const error = ref('')
const analysisType = ref('comprehensive')

const basicTypes = [
  { label: '综合分析', value: 'comprehensive' },
  { label: '技术分析', value: 'technical' },
  { label: '基本面分析', value: 'fundamental' },
  { label: '资金分析', value: 'funds' },
]

const quantTypes = [
  { label: '趋势跟踪', value: 'trend' },
  { label: '均值回归', value: 'mean_reversion' },
  { label: '统计套利', value: 'statistical_arbitrage' },
  { label: '风险控制', value: 'risk_control' },
]

async function requestAnalysis() {
  loading.value = true
  error.value = ''
  analysis.value = ''
  
  try {
    const url = `/api/ai-analysis?code=${encodeURIComponent(props.code)}&period=${props.period}&type=${analysisType.value}`
    const data = await fetchApi(url)
    
    if (data.ok) {
      analysis.value = data.analysis
    } else {
      error.value = data.error || '分析失败'
    }
  } catch (e) {
    error.value = '请求失败: ' + e.message
  } finally {
    loading.value = false
  }
}

function formatAnalysis(text) {
  if (!text) return ''
  // 简单的 Markdown 转 HTML
  return text
    .replace(/\n/g, '<br>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
}
</script>

<style scoped>
.ai-card {
  margin-top: 12px;
}

.ai-card h2 {
  display: flex;
  align-items: center;
  gap: 8px;
}

.ai-btn {
  margin-left: auto;
  padding: 6px 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  transition: all 0.3s;
}

.ai-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.ai-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.ai-btn.loading {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  background-size: 200% 200%;
  animation: gradient 1.5s ease infinite;
}

@keyframes gradient {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.analysis-types {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 12px;
}

.type-group {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.group-label {
  font-size: 11px;
  color: var(--muted);
  min-width: 60px;
}

.analysis-types button {
  padding: 5px 12px;
  background: var(--card2);
  border: 1px solid var(--line);
  color: var(--muted);
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s;
}

.analysis-types button:hover {
  color: var(--text);
  border-color: var(--accent);
}

.analysis-types button.active {
  background: var(--accent);
  color: #04101f;
  border-color: var(--accent);
}

.error {
  color: var(--up);
  padding: 12px;
  background: rgba(239, 35, 42, 0.1);
  border: 1px solid rgba(239, 35, 42, 0.3);
  border-radius: 6px;
  font-size: 13px;
}

.analysis-content {
  padding: 16px;
  background: var(--card2);
  border-radius: 8px;
  border: 1px solid var(--line);
}

.analysis-text {
  font-size: 13px;
  line-height: 1.8;
  color: var(--text);
}

.analysis-text :deep(strong) {
  color: var(--accent);
}

.analysis-text :deep(em) {
  color: var(--warn);
  font-style: normal;
}

.placeholder {
  padding: 24px;
  text-align: center;
  color: var(--muted);
  font-size: 13px;
  background: var(--card2);
  border-radius: 8px;
  border: 1px dashed var(--line);
}
</style>
