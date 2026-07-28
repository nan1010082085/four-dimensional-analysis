<template>
  <div class="help-overlay" v-if="show" @click.self="$emit('close')">
    <div class="help-panel">
      <div class="help-header">
        <h2>名词解释 & 交易规则</h2>
        <button class="close-btn" @click="$emit('close')">×</button>
      </div>
      
      <div class="help-tabs">
        <button 
          v-for="tab in tabs" 
          :key="tab.key"
          :class="{ active: activeTab === tab.key }"
          @click="activeTab = tab.key"
        >
          {{ tab.label }}
        </button>
      </div>
      
      <div class="help-content">
        <!-- 基本面指标 -->
        <div v-if="activeTab === 'fundamental'" class="section">
          <h3>基本面指标</h3>
          
          <div class="term">
            <div class="term-name">市盈率 (PE)</div>
            <div class="term-formula">股价 ÷ 每股收益</div>
            <div class="term-desc">衡量股票估值的核心指标。PE越低，估值越便宜。</div>
            <div class="term-range">
              <span class="low">低估 &lt;15</span>
              <span class="normal">合理 15-25</span>
              <span class="high">偏高 25-40</span>
              <span class="danger">高估 &gt;40</span>
            </div>
          </div>
          
          <div class="term">
            <div class="term-name">市净率 (PB)</div>
            <div class="term-formula">股价 ÷ 每股净资产</div>
            <div class="term-desc">衡量股价相对于净资产的溢价。PB&lt;1表示股价低于净资产。</div>
            <div class="term-range">
              <span class="low">低估 &lt;1</span>
              <span class="normal">合理 1-3</span>
              <span class="high">偏高 &gt;3</span>
            </div>
          </div>
          
          <div class="term">
            <div class="term-name">换手率</div>
            <div class="term-formula">成交量 ÷ 流通股本 × 100%</div>
            <div class="term-desc">反映股票交易活跃程度。换手率越高，交易越活跃。</div>
            <div class="term-range">
              <span class="low">低迷 &lt;1%</span>
              <span class="normal">正常 1-3%</span>
              <span class="warn">活跃 3-5%</span>
              <span class="danger">异常 &gt;5%</span>
            </div>
          </div>
          
          <div class="term">
            <div class="term-name">量比</div>
            <div class="term-formula">当前成交量 ÷ 近5日平均成交量</div>
            <div class="term-desc">衡量当日成交量相对于近期的变化。量比&gt;1表示放量。</div>
            <div class="term-range">
              <span class="low">缩量 &lt;0.5</span>
              <span class="normal">正常 0.5-1.5</span>
              <span class="warn">放量 1.5-3</span>
              <span class="danger">巨量 &gt;3</span>
            </div>
          </div>
          
          <div class="term">
            <div class="term-name">总市值 / 流通市值</div>
            <div class="term-desc">公司总价值 / 可交易股票价值。市值越大，股票越稳定。</div>
          </div>
        </div>
        
        <!-- 资金面指标 -->
        <div v-if="activeTab === 'fund'" class="section">
          <h3>资金面指标</h3>
          
          <div class="term">
            <div class="term-name">外盘 / 内盘</div>
            <div class="term-desc">
              <strong>外盘</strong>：以卖方价格成交的成交量（主动买入）<br>
              <strong>内盘</strong>：以买方价格成交的成交量（主动卖出）
            </div>
          </div>
          
          <div class="term">
            <div class="term-name">外内盘比</div>
            <div class="term-formula">外盘 ÷ 内盘</div>
            <div class="term-desc">衡量多空力量对比。比值越大，多方越强势。</div>
            <div class="term-range">
              <span class="danger">强烈看空 &lt;0.5</span>
              <span class="low">偏空 0.5-0.8</span>
              <span class="normal">均衡 0.8-1.2</span>
              <span class="high">偏多 1.2-1.5</span>
              <span class="good">强烈看多 &gt;1.5</span>
            </div>
          </div>
          
          <div class="term">
            <div class="term-name">主力净流入</div>
            <div class="term-desc">大单（通常指50万以上）买入金额 - 卖出金额。正值表示主力资金流入。</div>
            <div class="term-range">
              <span class="low">净流出（看空）</span>
              <span class="good">净流入（看多）</span>
            </div>
          </div>
          
          <div class="term">
            <div class="term-name">超大单 / 大单</div>
            <div class="term-desc">
              <strong>超大单</strong>：单笔成交金额 &gt; 100万元<br>
              <strong>大单</strong>：单笔成交金额 50-100万元<br>
              通常代表机构或大户资金动向。
            </div>
          </div>
        </div>
        
        <!-- 技术指标 -->
        <div v-if="activeTab === 'technical'" class="section">
          <h3>技术指标</h3>
          
          <div class="term">
            <div class="term-name">MA（移动平均线）</div>
            <div class="term-desc">
              <strong>MA5</strong>：5日均线，短线趋势<br>
              <strong>MA10</strong>：10日均线，短期趋势<br>
              <strong>MA20</strong>：20日均线，中期趋势<br>
              <strong>MA60</strong>：60日均线，长期趋势
            </div>
            <div class="term-rule">
              <strong>多头排列</strong>：MA5 > MA10 > MA20 > MA60，趋势向上<br>
              <strong>空头排列</strong>：MA5 < MA10 < MA20 < MA60，趋势向下
            </div>
          </div>
          
          <div class="term">
            <div class="term-name">MACD</div>
            <div class="term-desc">
              <strong>DIF</strong>：快线（12日EMA - 26日EMA）<br>
              <strong>DEA</strong>：慢线（DIF的9日EMA）<br>
              <strong>柱状</strong>：(DIF - DEA) × 2
            </div>
            <div class="term-rule">
              <strong>金叉</strong>：DIF上穿DEA，柱状由负转正，买入信号<br>
              <strong>死叉</strong>：DIF下穿DEA，柱状由正转负，卖出信号
            </div>
          </div>
          
          <div class="term">
            <div class="term-name">KDJ</div>
            <div class="term-desc">
              <strong>K</strong>：快速随机指标<br>
              <strong>D</strong>：慢速随机指标<br>
              <strong>J</strong>：3K - 2D，最敏感
            </div>
            <div class="term-range">
              <span class="danger">超买 &gt;80</span>
              <span class="normal">中性 20-80</span>
              <span class="low">超卖 &lt;20</span>
            </div>
          </div>
          
          <div class="term">
            <div class="term-name">RSI</div>
            <div class="term-desc">相对强弱指标，衡量价格变动的速度和幅度。</div>
            <div class="term-range">
              <span class="danger">超买 &gt;70</span>
              <span class="normal">中性 30-70</span>
              <span class="low">超卖 &lt;30</span>
            </div>
          </div>
          
          <div class="term">
            <div class="term-name">BOLL（布林带）</div>
            <div class="term-desc">
              <strong>上轨</strong>：中轨 + 2倍标准差，压力位<br>
              <strong>中轨</strong>：20日均线<br>
              <strong>下轨</strong>：中轨 - 2倍标准差，支撑位
            </div>
          </div>
          
          <div class="term">
            <div class="term-name">ATR</div>
            <div class="term-desc">平均真实波幅，衡量价格波动程度。用于设置止损距离。</div>
          </div>
        </div>
        
        <!-- 信号规则 -->
        <div v-if="activeTab === 'signal'" class="section">
          <h3>买卖信号规则</h3>
          
          <div class="signal-rule buy">
            <div class="signal-title">▲ 入场信号（绿色）</div>
            <div class="signal-threshold">触发条件：满足 <strong>3个以上</strong> 条件</div>
            <table>
              <tr><td>+2</td><td>MA5上穿MA10（均线金叉）</td></tr>
              <tr><td>+2</td><td>MACD金叉（柱状线转正）</td></tr>
              <tr><td>+1</td><td>KDJ超卖回升（K<20后上穿）</td></tr>
              <tr><td>+1</td><td>RSI超卖回升（RSI<30后上穿）</td></tr>
              <tr><td>+1</td><td>突破MA20（趋势确认）</td></tr>
              <tr><td>+1</td><td>放量上涨（量比>1.3）</td></tr>
              <tr><td>+1</td><td>阳包阴（反转形态）</td></tr>
            </table>
          </div>
          
          <div class="signal-rule sell">
            <div class="signal-title">▼ 出场信号（红色）</div>
            <div class="signal-threshold">触发条件：满足 <strong>3个以上</strong> 条件</div>
            <table>
              <tr><td>+2</td><td>MA5下穿MA10（均线死叉）</td></tr>
              <tr><td>+2</td><td>MACD死叉（柱状线转负）</td></tr>
              <tr><td>+1</td><td>KDJ超买回落（K>80后下穿）</td></tr>
              <tr><td>+1</td><td>RSI超买回落（RSI>70后下穿）</td></tr>
              <tr><td>+1</td><td>跌破MA20（趋势反转）</td></tr>
              <tr><td>+1</td><td>放量下跌（恐慌抛售）</td></tr>
              <tr><td>+1</td><td>阴包阳（反转形态）</td></tr>
              <tr><td>+1</td><td>长上影线（见顶信号）</td></tr>
            </table>
          </div>
          
          <div class="signal-note">
            <strong>查看信号原因：</strong>鼠标悬停在K线图的信号标记上，会显示具体触发的原因。
          </div>
        </div>
        
        <!-- 期货知识 -->
        <div v-if="activeTab === 'future'" class="section">
          <h3>期货基础知识</h3>
          
          <div class="term">
            <div class="term-name">持仓量</div>
            <div class="term-desc">未平仓合约数量。持仓量增加表示资金流入，减少表示资金流出。</div>
          </div>
          
          <div class="term">
            <div class="term-name">保证金</div>
            <div class="term-desc">期货交易采用保证金制度，通常只需支付合约价值的5%-15%。杠杆放大收益和风险。</div>
          </div>
          
          <div class="term">
            <div class="term-name">主力合约</div>
            <div class="term-desc">成交量最大的合约。代码中"0"结尾表示主力连续合约（如IF0）。</div>
          </div>
          
          <div class="term">
            <div class="term-name">交割</div>
            <div class="term-desc">合约到期时，买卖双方履行合约义务。个人投资者需在交割月前平仓。</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  show: Boolean
})

defineEmits(['close'])

const activeTab = ref('fundamental')

const tabs = [
  { key: 'fundamental', label: '基本面' },
  { key: 'fund', label: '资金面' },
  { key: 'technical', label: '技术指标' },
  { key: 'signal', label: '信号规则' },
  { key: 'future', label: '期货知识' },
]
</script>

<style scoped>
.help-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  z-index: 9999;
  display: flex;
  justify-content: center;
  align-items: center;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.help-panel {
  width: 700px;
  max-height: 80vh;
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.help-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--line);
}

.help-header h2 {
  margin: 0;
  font-size: 16px;
  color: var(--accent);
}

.close-btn {
  width: 32px;
  height: 32px;
  background: transparent;
  border: 1px solid var(--line);
  color: var(--muted);
  border-radius: 6px;
  cursor: pointer;
  font-size: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  border-color: var(--accent);
  color: var(--accent);
}

.help-tabs {
  display: flex;
  gap: 4px;
  padding: 12px 20px;
  border-bottom: 1px solid var(--line);
  background: var(--card2);
}

.help-tabs button {
  padding: 6px 14px;
  background: transparent;
  border: 1px solid transparent;
  color: var(--muted);
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s;
}

.help-tabs button:hover {
  color: var(--text);
}

.help-tabs button.active {
  background: var(--accent);
  color: #fff;
  border-color: var(--accent);
}

.help-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.section h3 {
  margin: 0 0 16px;
  font-size: 14px;
  color: var(--accent);
  border-bottom: 1px solid var(--line);
  padding-bottom: 8px;
}

.term {
  margin-bottom: 16px;
  padding: 12px;
  background: var(--card2);
  border-radius: 8px;
}

.term-name {
  font-size: 13px;
  font-weight: bold;
  color: var(--text);
  margin-bottom: 4px;
}

.term-formula {
  font-size: 11px;
  color: var(--accent);
  margin-bottom: 6px;
  font-family: monospace;
}

.term-desc {
  font-size: 12px;
  color: var(--muted);
  line-height: 1.6;
  margin-bottom: 8px;
}

.term-rule {
  font-size: 11px;
  color: var(--text);
  background: var(--bg);
  padding: 8px 10px;
  border-radius: 6px;
  line-height: 1.6;
}

.term-range {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  font-size: 11px;
}

.term-range span {
  padding: 3px 8px;
  border-radius: 4px;
  background: var(--bg);
}

.term-range .low { color: #14b143; }
.term-range .normal { color: #58a6ff; }
.term-range .warn { color: #d29922; }
.term-range .high { color: #d29922; }
.term-range .danger { color: #ef232a; }
.term-range .good { color: #14b143; }

.signal-rule {
  margin-bottom: 16px;
  padding: 12px;
  border-radius: 8px;
}

.signal-rule.buy {
  background: rgba(20, 177, 67, 0.1);
  border: 1px solid rgba(20, 177, 67, 0.3);
}

.signal-rule.sell {
  background: rgba(239, 35, 42, 0.1);
  border: 1px solid rgba(239, 35, 42, 0.3);
}

.signal-title {
  font-size: 13px;
  font-weight: bold;
  margin-bottom: 8px;
}

.signal-rule.buy .signal-title { color: #14b143; }
.signal-rule.sell .signal-title { color: #ef232a; }

.signal-threshold {
  font-size: 11px;
  color: var(--muted);
  margin-bottom: 10px;
}

.signal-rule table {
  width: 100%;
  font-size: 12px;
}

.signal-rule td {
  padding: 4px 0;
}

.signal-rule td:first-child {
  width: 40px;
  color: var(--accent);
  font-weight: bold;
}

.signal-note {
  padding: 10px;
  background: var(--card2);
  border-radius: 6px;
  font-size: 12px;
  color: var(--muted);
}
</style>
