<template>
  <div v-if="show" class="signal-alert" :class="type" @click="close">
    <div class="alert-icon">{{ type === 'buy' ? '▲' : '▼' }}</div>
    <div class="alert-content">
      <div class="alert-title">{{ type === 'buy' ? '买入信号' : '卖出信号' }}</div>
      <div class="alert-code">{{ code }} {{ name }}</div>
      <div class="alert-price">价格: {{ price }}</div>
      <div class="alert-reasons">{{ reasons.join(', ') }}</div>
    </div>
    <div class="alert-close" @click.stop="close">×</div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'

const props = defineProps({
  signal: Object,
  code: String,
  name: String
})

const emit = defineEmits(['close'])

const show = ref(false)
const type = ref('')
const price = ref('')
const reasons = ref([])

// 音频上下文
let audioCtx = null

function playSound(isBuy) {
  try {
    if (!audioCtx) {
      audioCtx = new (window.AudioContext || window.webkitAudioContext)()
    }
    
    const oscillator = audioCtx.createOscillator()
    const gainNode = audioCtx.createGain()
    
    oscillator.connect(gainNode)
    gainNode.connect(audioCtx.destination)
    
    // 买入用升调，卖出用降调
    oscillator.frequency.setValueAtTime(isBuy ? 600 : 400, audioCtx.currentTime)
    oscillator.frequency.linearRampToValueAtTime(isBuy ? 800 : 300, audioCtx.currentTime + 0.2)
    
    gainNode.gain.setValueAtTime(0.3, audioCtx.currentTime)
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.5)
    
    oscillator.start(audioCtx.currentTime)
    oscillator.stop(audioCtx.currentTime + 0.5)
  } catch (e) {
    console.log('音频播放失败:', e)
  }
}

function sendNotification(isBuy, code, name, price, reasons) {
  if ('Notification' in window && Notification.permission === 'granted') {
    const title = isBuy ? '▲ 买入信号' : '▼ 卖出信号'
    const body = `${code} ${name}\n价格: ${price}\n原因: ${reasons.join(', ')}`
    
    new Notification(title, {
      body: body,
      icon: '/favicon.ico',
      tag: `signal-${code}-${Date.now()}`
    })
  }
}

function requestNotificationPermission() {
  if ('Notification' in window && Notification.permission === 'default') {
    Notification.requestPermission()
  }
}

function close() {
  show.value = false
  emit('close')
}

watch(() => props.signal, (newSignal) => {
  if (newSignal && newSignal.type) {
    type.value = newSignal.type
    price.value = newSignal.price
    reasons.value = newSignal.reasons || []
    show.value = true
    
    // 播放声音
    playSound(newSignal.type === 'buy')
    
    // 发送桌面通知
    sendNotification(
      newSignal.type === 'buy',
      props.code,
      props.name,
      newSignal.price,
      newSignal.reasons || []
    )
    
    // 5秒后自动关闭
    setTimeout(() => {
      show.value = false
    }, 5000)
  }
}, { deep: true })

onMounted(() => {
  requestNotificationPermission()
})
</script>

<style scoped>
.signal-alert {
  position: fixed;
  top: 80px;
  right: 20px;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  border-radius: 10px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
  z-index: 10000;
  cursor: pointer;
  animation: slideIn 0.3s ease-out;
  min-width: 280px;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.signal-alert.buy {
  background: linear-gradient(135deg, #1a3a2a 0%, #0d2818 100%);
  border: 2px solid #14b143;
}

.signal-alert.sell {
  background: linear-gradient(135deg, #3a1a1a 0%, #280d0d 100%);
  border: 2px solid #ef232a;
}

.alert-icon {
  font-size: 24px;
  font-weight: bold;
}

.signal-alert.buy .alert-icon {
  color: #14b143;
}

.signal-alert.sell .alert-icon {
  color: #ef232a;
}

.alert-content {
  flex: 1;
}

.alert-title {
  font-size: 14px;
  font-weight: bold;
  margin-bottom: 4px;
}

.signal-alert.buy .alert-title {
  color: #14b143;
}

.signal-alert.sell .alert-title {
  color: #ef232a;
}

.alert-code {
  font-size: 13px;
  color: #c9d1d9;
  margin-bottom: 2px;
}

.alert-price {
  font-size: 13px;
  color: #58a6ff;
  margin-bottom: 4px;
}

.alert-reasons {
  font-size: 11px;
  color: #8b949e;
}

.alert-close {
  font-size: 20px;
  color: #8b949e;
  cursor: pointer;
  padding: 0 4px;
}

.alert-close:hover {
  color: #c9d1d9;
}
</style>
