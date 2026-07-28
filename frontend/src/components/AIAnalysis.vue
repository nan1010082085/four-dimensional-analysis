<template>
  <div class="card ai-card">
    <h2>
      <span class="ai-icon">🤖</span>
      AI 量化分析 
      <small>DeepSeek 智能策略</small>
      <button 
        class="ai-btn" 
        :class="{ loading: loading }"
        :disabled="loading"
        @click="requestAnalysis"
      >
        {{ loading ? '分析中...' : '重新分析' }}
      </button>
    </h2>
    
    <div v-if="error" class="error">{{ error }}</div>
    
    <div v-if="analysis" class="analysis-content">
      <div class="analysis-text" v-html="formatAnalysis(analysis)"></div>
    </div>
    
    <div v-else-if="!loading" class="placeholder">
      正在加载 AI 分析...
    </div>
    
    <div v-if="loading" class="loading-indicator">
      <div class="loading-spinner"></div>
      <span>AI 正在分析 {{ code }}...</span>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { fetchApi } from '../api.js'

const props = defineProps({
  code: String,
  period: String,
  kind: String
})

const emit = defineEmits(['signal'])

const loading = ref(false)
const analysis = ref('')
const error = ref('')

async function requestAnalysis() {
  loading.value = true
  error.value = ''
  
  try {
    const url = `/api/ai-analysis?code=${encodeURIComponent(props.code)}&period=${props.period}&type=comprehensive`
    const data = await fetchApi(url)
    
    if (data.ok) {
      analysis.value = data.analysis
      // 提取信号方向
      extractSignalDirection(data.analysis)
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
  return text
    .replace(/\n/g, '<br>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/^#{1,3}\s+(.*?)$/gm, '<h4>$1</h4>')
    .replace(/^[-*]\s+(.*?)$/gm, '<li>$1</li>')
}

// 提取信号方向
function extractSignalDirection(text) {
  if (!text) return
  
  const buyKeywords = ['买入', '做多', '看多', '买入信号', '建议买入', '可以买入']
  const sellKeywords = ['卖出', '做空', '看空', '卖出信号', '建议卖出', '可以卖出']
  const holdKeywords = ['观望', '持有', '等待', '观望为主', '暂时观望']
  
  let direction = null
  
  for (const keyword of buyKeywords) {
    if (text.includes(keyword)) {
      direction = 'buy'
      break
    }
  }
  
  if (!direction) {
    for (const keyword of sellKeywords) {
      if (text.includes(keyword)) {
        direction = 'sell'
        break
      }
    }
  }
  
  if (!direction) {
    for (const keyword of holdKeywords) {
      if (text.includes(keyword)) {
        direction = 'hold'
        break
      }
    }
  }
  
  // 发送信号给父组件
  if (direction) {
    emit('signal', {
      type: direction,
      reason: `AI分析: ${direction === 'buy' ? '看多' : direction === 'sell' ? '看空' : '观望'}`,
      price: null,
      stop_loss: null,
      take_profit: null
    })
  }
}

// 监听代码变化，自动分析
watch(() => [props.code, props.period], () => {
  if (props.code) {
    requestAnalysis()
  }
}, { immediate: true })
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

.ai-icon {
  font-size: 16px;
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

.analysis-text :deep(h4) {
  color: var(--accent);
  margin: 12px 0 6px;
  font-size: 14px;
}

.analysis-text :deep(li) {
  margin-left: 16px;
  margin-bottom: 4px;
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

.loading-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 20px;
  color: var(--accent);
  font-size: 13px;
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid var(--line);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
