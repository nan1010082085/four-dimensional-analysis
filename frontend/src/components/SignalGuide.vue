<template>
  <div class="signal-guide">
    <div class="guide-header" @click="expanded = !expanded">
      <span>信号说明</span>
      <span class="toggle">{{ expanded ? '▼' : '▶' }}</span>
    </div>
    
    <div v-if="expanded" class="guide-content">
      <div class="signal-section">
        <h4 class="buy-title">▲ 入场信号（绿色）</h4>
        <p class="threshold">触发条件：满足3个以上</p>
        <ul>
          <li><span class="weight">+2</span> MA5上穿MA10（均线金叉）</li>
          <li><span class="weight">+2</span> MACD金叉（柱状线转正）</li>
          <li><span class="weight">+1</span> KDJ超卖回升（K<20后上穿）</li>
          <li><span class="weight">+1</span> RSI超卖回升（RSI<30后上穿）</li>
          <li><span class="weight">+1</span> 突破MA20（趋势确认）</li>
          <li><span class="weight">+1</span> 放量上涨（量比>1.3）</li>
          <li><span class="weight">+1</span> 阳包阴（反转形态）</li>
        </ul>
      </div>
      
      <div class="signal-section">
        <h4 class="sell-title">▼ 出场信号（红色）</h4>
        <p class="threshold">触发条件：满足3个以上</p>
        <ul>
          <li><span class="weight">+2</span> MA5下穿MA10（均线死叉）</li>
          <li><span class="weight">+2</span> MACD死叉（柱状线转负）</li>
          <li><span class="weight">+1</span> KDJ超买回落（K>80后下穿）</li>
          <li><span class="weight">+1</span> RSI超买回落（RSI>70后下穿）</li>
          <li><span class="weight">+1</span> 跌破MA20（趋势反转）</li>
          <li><span class="weight">+1</span> 放量下跌（恐慌抛售）</li>
          <li><span class="weight">+1</span> 阴包阳（反转形态）</li>
          <li><span class="weight">+1</span> 长上影线（见顶信号）</li>
        </ul>
      </div>
      
      <div class="signal-section">
        <h4>查看信号原因</h4>
        <ul>
          <li>鼠标悬停在信号标记上</li>
          <li>查看右侧AI分析面板</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const expanded = ref(false)
</script>

<style scoped>
.signal-guide {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 10px;
  overflow: hidden;
}

.guide-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  cursor: pointer;
  font-size: 12px;
  color: var(--accent);
  font-weight: bold;
}

.guide-header:hover {
  background: var(--card2);
}

.toggle {
  font-size: 10px;
  color: var(--muted);
}

.guide-content {
  padding: 0 14px 14px;
  font-size: 11px;
}

.signal-section {
  margin-bottom: 12px;
}

.signal-section h4 {
  margin: 0 0 6px;
  font-size: 12px;
}

.buy-title {
  color: #14b143;
}

.sell-title {
  color: #ef232a;
}

.threshold {
  color: var(--muted);
  font-size: 10px;
  margin-bottom: 6px;
}

.signal-section ul {
  margin: 0;
  padding-left: 16px;
}

.signal-section li {
  margin-bottom: 3px;
  color: var(--text);
}

.weight {
  display: inline-block;
  width: 24px;
  color: var(--accent);
  font-weight: bold;
}
</style>
