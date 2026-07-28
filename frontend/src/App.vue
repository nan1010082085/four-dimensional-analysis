<template>
  <div class="app">
    <header>
      <div>
        <h1>四维分析盯盘台</h1>
        <div class="sub">行情 · 技术 · 基本面 · 资金 · AI &nbsp;|&nbsp; 实时数据源</div>
      </div>
      
      <!-- 股票/期货选择下拉面板 -->
      <div class="selector-wrapper">
        <div class="selector" @click="showPanel = !showPanel">
          <span class="selector-value">{{ currentName || '选择标的' }}</span>
          <span class="selector-arrow">▼</span>
        </div>
        
        <div v-if="showPanel" class="panel" @click.stop>
          <div class="panel-header">
            <input 
              v-model="searchText" 
              placeholder="搜索股票/期货..."
              class="search-input"
              @keydown.enter="selectCustom"
            />
            <button class="search-btn" @click="selectCustom">确定</button>
          </div>
          
          <div class="panel-tabs">
            <button 
              v-for="tab in tabs" 
              :key="tab.key"
              :class="{ active: activeTab === tab.key }"
              @click="activeTab = tab.key"
            >
              {{ tab.name }}
            </button>
          </div>
          
          <div class="panel-content">
            <div 
              v-for="item in currentList" 
              :key="item.code"
              class="panel-item"
              :class="{ active: code === item.code }"
              @click="selectItem(item)"
            >
              <span class="item-name">{{ item.name }}</span>
              <span class="item-code">{{ item.code }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 周期选择面板 -->
      <div class="period-wrapper">
        <div class="period-btn" @click="showPeriodPanel = !showPeriodPanel">
          <span>{{ currentPeriodLabel }}</span>
          <span class="arrow">▼</span>
        </div>
        <div v-if="showPeriodPanel" class="period-panel" @click.stop>
          <div class="period-group">
            <div class="group-title">分时</div>
            <div class="group-items">
              <button :class="{ active: period === 'minute' }" @click="selectPeriod('minute')">分时</button>
            </div>
          </div>
          <div class="period-group">
            <div class="group-title">分钟K线</div>
            <div class="group-items">
              <button :class="{ active: period === '1' }" @click="selectPeriod('1')">1分</button>
              <button :class="{ active: period === '2' }" @click="selectPeriod('2')">2分</button>
              <button :class="{ active: period === '3' }" @click="selectPeriod('3')">3分</button>
              <button :class="{ active: period === '5' }" @click="selectPeriod('5')">5分</button>
              <button :class="{ active: period === '10' }" @click="selectPeriod('10')">10分</button>
              <button :class="{ active: period === '15' }" @click="selectPeriod('15')">15分</button>
              <button :class="{ active: period === '30' }" @click="selectPeriod('30')">30分</button>
              <button :class="{ active: period === '60' }" @click="selectPeriod('60')">60分</button>
            </div>
          </div>
          <div class="period-group">
            <div class="group-title">日K线</div>
            <div class="group-items">
              <button :class="{ active: period === 'day' }" @click="selectPeriod('day')">日K</button>
              <button :class="{ active: period === 'week' }" @click="selectPeriod('week')">周K</button>
              <button :class="{ active: period === 'month' }" @click="selectPeriod('month')">月K</button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 刷新时间设置 -->
      <div class="refresh-settings">
        <label class="auto">
          <input type="checkbox" v-model="autoRefresh" @change="toggleAutoRefresh" />
          自动刷新
        </label>
        <div v-if="autoRefresh" class="interval-selector">
          <select v-model="refreshInterval" @change="updateRefreshInterval">
            <option :value="1000">1秒</option>
            <option :value="2000">2秒</option>
            <option :value="3000">3秒</option>
            <option :value="5000">5秒</option>
            <option :value="10000">10秒</option>
            <option :value="30000">30秒</option>
            <option :value="60000">60秒</option>
          </select>
        </div>
      </div>
      
      <!-- AI信号方向 -->
      <div v-if="aiSignalDirection" class="signal-direction" :class="aiSignalDirection">
        {{ aiSignalDirection === 'buy' ? '▲ 看多' : aiSignalDirection === 'sell' ? '▼ 看空' : '◆ 观望' }}
      </div>
      
      <!-- 数据源切换 -->
      <div class="datasource-wrapper">
        <div class="datasource-btn" @click="showDatasourcePanel = !showDatasourcePanel">
          <span class="ds-icon">📡</span>
          <span class="ds-label">{{ currentDatasourceLabel }}</span>
        </div>
        <div v-if="showDatasourcePanel" class="datasource-panel" @click.stop>
          <div class="ds-title">数据源选择</div>
          <div 
            v-for="ds in availableDatasources" 
            :key="ds.value"
            class="ds-item"
            :class="{ active: dataSource === ds.value }"
            @click="switchDatasource(ds.value)"
          >
            <span class="ds-name">{{ ds.name }}</span>
            <span class="ds-desc">{{ ds.desc }}</span>
            <span v-if="dataSource === ds.value" class="ds-check">✓</span>
          </div>
        </div>
      </div>
      
      <div id="status">
        <span class="dot" :class="{ live: isLive }"></span>
        <span>{{ statusText }}</span>
      </div>
      
      <!-- 风险控制按钮 -->
      <button class="toolbar-btn risk-btn" @click="showRiskPanel = !showRiskPanel" title="风险控制">
        🛡️ 风控
      </button>
      
      <!-- 模拟盘按钮 -->
      <button class="toolbar-btn" @click="showPaperTrading = !showPaperTrading" title="模拟盘">
        💰 模拟盘
      </button>
      
      <!-- 帮助按钮 -->
      <button class="help-btn" @click="showHelp = true" title="名词解释 & 交易规则">
        ?
      </button>
    </header>

    <!-- 风险控制面板 -->
    <div v-if="showRiskPanel" class="risk-overlay" @click.self="showRiskPanel = false">
      <div class="risk-panel-wrapper">
        <RiskPanel :quote="quote" :kline="kline" :signal="currentSignal" @close="showRiskPanel = false" />
      </div>
    </div>

    <!-- 模拟盘面板 -->
    <div v-if="showPaperTrading" class="paper-overlay" @click.self="showPaperTrading = false">
      <div class="paper-panel">
        <PaperTrading :code="code" :quote="quote" :signal="currentSignal" @close="showPaperTrading = false" />
      </div>
    </div>

    <!-- 帮助面板 -->
    <HelpPanel :show="showHelp" @close="showHelp = false" />
    
    <!-- 信号提醒弹窗 -->
    <SignalAlert 
      :signal="currentSignal" 
      :code="signalStockCode"
      :name="signalStockName"
      @close="currentSignal = null"
    />
    
    <main>
      <!-- 左栏：行情数据 + 监控 -->
      <div class="col-left">
        <WatchlistPanel 
          @select="selectFromWatchlist" 
          @signal="handleSignal"
        />
        <SignalGuide />
        <QuoteCard :quote="quote" :kind="kind" />
        <FundamentalsCard :fundamentals="fundamentals" :kind="kind" />
        <FundsCard :funds="funds" :kind="kind" />
      </div>
      
      <!-- 中栏：K线图表 -->
      <div class="col-center">
        <div class="card chart-card">
          <h2>
            <span class="chart-icon">📊</span>
            {{ quote?.name || code }} 
            <small>{{ currentPeriodLabel }} · 技术分析</small>
          </h2>
          <KlineChart 
            v-if="!isMinutePeriod" 
            :bars="kline.bars" 
            :indicators="kline.indicators" 
            :period="period"
          />
          <MinuteChart 
            v-else 
            :data="minuteData" 
            :quote="quote" 
          />
        </div>
      </div>
      
      <!-- 右栏：AI分析 -->
      <div class="col-right">
        <AIAnalysis :code="code" :period="period" :kind="kind" @signal="handleAISignal" />
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { getApiUrl, fetchApi } from './api.js'
import QuoteCard from './components/QuoteCard.vue'
import FundamentalsCard from './components/FundamentalsCard.vue'
import FundsCard from './components/FundsCard.vue'
import KlineChart from './components/KlineChart.vue'
import MinuteChart from './components/MinuteChart.vue'
import AIAnalysis from './components/AIAnalysis.vue'
import SignalAlert from './components/SignalAlert.vue'
import WatchlistPanel from './components/WatchlistPanel.vue'
import RiskPanel from './components/RiskPanel.vue'
import PaperTrading from './components/PaperTrading.vue'
import SignalGuide from './components/SignalGuide.vue'
import HelpPanel from './components/HelpPanel.vue'

const code = ref('sh600519')
const period = ref('day')
const kind = ref('stock')
const quote = ref(null)
const fundamentals = ref(null)
const funds = ref(null)
const kline = ref({ bars: [], indicators: null })
const minuteData = ref([])
const autoRefresh = ref(true)
const refreshInterval = ref(3000)
const isLive = ref(false)
const statusText = ref('就绪')
const showHelp = ref(false)
const showPanel = ref(false)
const showPeriodPanel = ref(false)
const showPaperTrading = ref(false)
const showRiskPanel = ref(false)
const showDatasourcePanel = ref(false)
const activeTab = ref('hot')
const searchText = ref('sh600519')

// 数据源相关
const dataSource = ref('legacy')
const availableDatasources = ref([])

const currentDatasourceLabel = computed(() => {
  const ds = availableDatasources.value.find(d => d.value === dataSource.value)
  return ds ? ds.name : '数据源'
})
const currentSignal = ref(null)
const signalStockCode = ref('')
const signalStockName = ref('')
let timer = null

// 周期标签映射
const periodLabels = {
  'minute': '分时',
  '1': '1分钟',
  '2': '2分钟',
  '3': '3分钟',
  '5': '5分钟',
  '10': '10分钟',
  '15': '15分钟',
  '30': '30分钟',
  '60': '60分钟',
  'day': '日K',
  'week': '周K',
  'month': '月K'
}

// 当前周期标签
const currentPeriodLabel = computed(() => periodLabels[period.value] || '日K')

// 是否为分钟周期
const isMinutePeriod = computed(() => {
  return ['minute', '1', '2', '3', '5', '10', '15', '30', '60'].includes(period.value)
})

// 选择周期
function selectPeriod(p) {
  period.value = p
  showPeriodPanel.value = false
  loadAll()
}

// 股票/期货分类数据
const tabs = [
  { key: 'hot', name: '热门' },
  { key: 'stock_sh', name: '上证' },
  { key: 'stock_sz', name: '深证' },
  { key: 'stock_cyb', name: '创业板' },
  { key: 'stock_kcb', name: '科创板' },
  { key: 'stock_bj', name: '北证' },
  { key: 'stock_hk', name: '港股' },
  { key: 'stock_us', name: '美股' },
  { key: 'etf', name: 'ETF' },
  { key: 'future_cffex', name: '中金所' },
  { key: 'future_shfe', name: '上期所' },
  { key: 'future_dce', name: '大商所' },
  { key: 'future_czce', name: '郑商所' },
]

const stockLists = {
  hot: [
    { name: '贵州茅台', code: 'sh600519' },
    { name: '平安银行', code: 'sz000001' },
    { name: '宁德时代', code: 'sz300750' },
    { name: '比亚迪', code: 'sz002594' },
    { name: '中国平安', code: 'sh601318' },
    { name: '招商银行', code: 'sh600036' },
    { name: '腾讯控股', code: 'hk00700' },
    { name: '阿里巴巴', code: 'hk09988' },
    { name: 'IF主连', code: 'IF0' },
    { name: '螺纹主连', code: 'rb0' },
    { name: '黄金主连', code: 'au0' },
  ],
  stock_sh: [
    { name: '贵州茅台', code: 'sh600519' },
    { name: '中国平安', code: 'sh601318' },
    { name: '招商银行', code: 'sh600036' },
    { name: '工商银行', code: 'sh601398' },
    { name: '农业银行', code: 'sh601288' },
    { name: '中国银行', code: 'sh601988' },
    { name: '建设银行', code: 'sh601939' },
    { name: '中信证券', code: 'sh600030' },
    { name: '海天味业', code: 'sh603288' },
    { name: '恒瑞医药', code: 'sh600276' },
  ],
  stock_sz: [
    { name: '平安银行', code: 'sz000001' },
    { name: '万科A', code: 'sz000002' },
    { name: '格力电器', code: 'sz000651' },
    { name: '美的集团', code: 'sz000333' },
    { name: '五粮液', code: 'sz000858' },
    { name: '泸州老窖', code: 'sz000568' },
    { name: '洋河股份', code: 'sz002304' },
    { name: '海康威视', code: 'sz002415' },
    { name: '立讯精密', code: 'sz002475' },
    { name: '牧原股份', code: 'sz002714' },
  ],
  stock_cyb: [
    { name: '宁德时代', code: 'sz300750' },
    { name: '迈瑞医疗', code: 'sz300760' },
    { name: '东方财富', code: 'sz300059' },
    { name: '汇川技术', code: 'sz300124' },
    { name: '阳光电源', code: 'sz300274' },
    { name: '温氏股份', code: 'sz300498' },
    { name: '亿纬锂能', code: 'sz300014' },
    { name: '爱尔眼科', code: 'sz300015' },
    { name: '智飞生物', code: 'sz300122' },
    { name: '泰格医药', code: 'sz300347' },
  ],
  stock_kcb: [
    { name: '中芯国际', code: 'sh688981' },
    { name: '金山办公', code: 'sh688111' },
    { name: '传音控股', code: 'sh688036' },
    { name: '澜起科技', code: 'sh688008' },
    { name: '中微公司', code: 'sh688012' },
    { name: '沪硅产业', code: 'sh688126' },
    { name: '华润微', code: 'sh688396' },
    { name: '奇安信', code: 'sh688561' },
    { name: '君实生物', code: 'sh688180' },
    { name: '康希诺', code: 'sh688185' },
  ],
  stock_bj: [
    { name: '贝特瑞', code: 'bj835185' },
    { name: '连城数控', code: 'bj835368' },
    { name: '吉林碳谷', code: 'bj836077' },
    { name: '长虹能源', code: 'bj836239' },
    { name: '森萱医药', code: 'bj830946' },
  ],
  stock_hk: [
    { name: '腾讯控股', code: 'hk00700' },
    { name: '阿里巴巴', code: 'hk09988' },
    { name: '美团', code: 'hk03690' },
    { name: '小米集团', code: 'hk01810' },
    { name: '京东集团', code: 'hk09618' },
    { name: '网易', code: 'hk09999' },
    { name: '百度集团', code: 'hk09888' },
    { name: '比亚迪', code: 'hk01211' },
    { name: '中国海洋石油', code: 'hk00883' },
    { name: '建设银行', code: 'hk00939' },
  ],
  stock_us: [
    { name: '苹果', code: 'usAAPL' },
    { name: '微软', code: 'usMSFT' },
    { name: '谷歌', code: 'usGOOGL' },
    { name: '亚马逊', code: 'usAMZN' },
    { name: '英伟达', code: 'usNVDA' },
    { name: '特斯拉', code: 'usTSLA' },
    { name: 'Meta', code: 'usMETA' },
    { name: '台积电', code: 'usTSM' },
    { name: '阿里巴巴', code: 'usBABA' },
    { name: '拼多多', code: 'usPDD' },
  ],
  etf: [
    { name: '沪深300ETF', code: 'sh510300' },
    { name: '上证50ETF', code: 'sh510050' },
    { name: '中证500ETF', code: 'sh510500' },
    { name: '创业板ETF', code: 'sz159915' },
    { name: '科创50ETF', code: 'sh588000' },
    { name: '恒生ETF', code: 'sz159920' },
    { name: '纳斯达克ETF', code: 'sh513100' },
    { name: '标普500ETF', code: 'sh513500' },
    { name: '黄金ETF', code: 'sh518880' },
    { name: '国债ETF', code: 'sh511010' },
  ],
  future_cffex: [
    { name: '沪深300主连', code: 'IF0' },
    { name: '上证50主连', code: 'IH0' },
    { name: '中证500主连', code: 'IC0' },
    { name: '中证1000主连', code: 'IM0' },
    { name: '2年国债主连', code: 'TS0' },
    { name: '5年国债主连', code: 'TF0' },
    { name: '10年国债主连', code: 'T0' },
    { name: '30年国债主连', code: 'TL0' },
  ],
  future_shfe: [
    { name: '螺纹钢主连', code: 'rb0' },
    { name: '热卷主连', code: 'hc0' },
    { name: '线材主连', code: 'wr0' },
    { name: '铜主连', code: 'cu0' },
    { name: '铝主连', code: 'al0' },
    { name: '锌主连', code: 'zn0' },
    { name: '铅主连', code: 'pb0' },
    { name: '镍主连', code: 'ni0' },
    { name: '锡主连', code: 'sn0' },
    { name: '黄金主连', code: 'au0' },
    { name: '白银主连', code: 'ag0' },
    { name: '原油主连', code: 'sc0' },
  ],
  future_dce: [
    { name: '豆一主连', code: 'a0' },
    { name: '豆二主连', code: 'b0' },
    { name: '豆粕主连', code: 'm0' },
    { name: '豆油主连', code: 'y0' },
    { name: '玉米主连', code: 'c0' },
    { name: '玉米淀粉主连', code: 'cs0' },
    { name: '棕榈油主连', code: 'p0' },
    { name: '鸡蛋主连', code: 'jd0' },
    { name: '生猪主连', code: 'lh0' },
    { name: '聚乙烯主连', code: 'l0' },
    { name: '聚丙烯主连', code: 'pp0' },
    { name: '焦炭主连', code: 'j0' },
    { name: '焦煤主连', code: 'jm0' },
    { name: '铁矿石主连', code: 'i0' },
  ],
  future_czce: [
    { name: '白糖主连', code: 'SR0' },
    { name: '棉花主连', code: 'CF0' },
    { name: 'PTA主连', code: 'TA0' },
    { name: '甲醇主连', code: 'MA0' },
    { name: '菜油主连', code: 'OI0' },
    { name: '菜粕主连', code: 'RM0' },
    { name: '动力煤主连', code: 'ZC0' },
    { name: '玻璃主连', code: 'FG0' },
    { name: '纯碱主连', code: 'SA0' },
    { name: '尿素主连', code: 'UR0' },
    { name: '苹果主连', code: 'AP0' },
    { name: '红枣主连', code: 'CJ0' },
  ],
}

const currentList = computed(() => {
  return stockLists[activeTab.value] || []
})

const currentName = computed(() => {
  for (const tab of Object.values(stockLists)) {
    const found = tab.find(item => item.code === code.value)
    if (found) return found.name
  }
  return code.value
})

const periods = [
  { label: '分时', value: 'minute' },
  { label: '日K', value: 'day' },
  { label: '周K', value: 'week' },
  { label: '月K', value: 'month' },
  { label: '60分', value: '60' },
  { label: '15分', value: '15' },
]

function selectItem(item) {
  code.value = item.code
  searchText.value = item.code
  showPanel.value = false
  loadAll()
}

function selectCustom() {
  if (searchText.value) {
    code.value = searchText.value.trim()
    showPanel.value = false
    loadAll()
  }
}

function setStatus(txt, live) {
  statusText.value = txt
  isLive.value = live
}

// 从自选股列表选择
function selectFromWatchlist(stockCode) {
  code.value = stockCode
  searchText.value = stockCode
  loadAll()
}

// 处理信号提醒
function handleSignal(signal) {
  currentSignal.value = signal
  signalStockCode.value = signal.code
  signalStockName.value = signal.name
}

// 处理AI分析信号
function handleAISignal(signal) {
  if (signal) {
    currentSignal.value = signal
    signalStockCode.value = code.value
    signalStockName.value = quote.value?.name || code.value
  }
}

// AI信号方向
const aiSignalDirection = ref(null) // 'buy' / 'sell' / 'hold'

async function loadAll() {
  setStatus('加载中…', false)
  try {
    const url = `/api/analysis?code=${encodeURIComponent(code.value)}&period=${period.value}&limit=160`
    const data = await fetchApi(url)
    
    if (!data.ok) {
      setStatus('失败: ' + data.error, false)
      return
    }
    
    kind.value = data.kind
    quote.value = data.quote
    fundamentals.value = data.fundamentals
    funds.value = data.funds
    
    if (period.value === 'minute') {
      const minuteData2 = await fetchApi(`/api/minute?code=${encodeURIComponent(code.value)}`)
      minuteData.value = minuteData2.ok ? minuteData2.data : []
    } else {
      kline.value = {
        bars: data.kline?.bars || [],
        indicators: data.kline?.indicators || null
      }
    }
    
    setStatus('更新 ' + new Date().toLocaleTimeString('zh-CN'), true)
  } catch (e) {
    setStatus('错误: ' + e.message, false)
  }
}

async function refreshQuote() {
  if (document.hidden) return
  try {
    const data = await fetchApi(`/api/quote?code=${encodeURIComponent(code.value)}`)
    if (data.ok) {
      quote.value = data.data
    }
  } catch (e) {
    // ignore
  }
}

function toggleAutoRefresh() {
  if (timer) {
    clearInterval(timer)
    timer = null
  }
  if (autoRefresh.value) {
    timer = setInterval(refreshQuote, refreshInterval.value)
  }
}

function updateRefreshInterval() {
  if (timer) {
    clearInterval(timer)
    timer = null
  }
  if (autoRefresh.value) {
    timer = setInterval(refreshQuote, refreshInterval.value)
  }
}

// 点击外部关闭面板
function closePanel(e) {
  if (!e.target.closest('.selector-wrapper')) {
    showPanel.value = false
  }
  if (!e.target.closest('.period-wrapper')) {
    showPeriodPanel.value = false
  }
  if (!e.target.closest('.datasource-wrapper')) {
    showDatasourcePanel.value = false
  }
}

// 加载数据源配置
async function loadDatasourceConfig() {
  try {
    const data = await fetchApi('/api/datasource')
    if (data.ok) {
      dataSource.value = data.current
      availableDatasources.value = data.available.map(ds => {
        const labels = {
          'legacy': { name: 'Legacy', desc: '腾讯/新浪免费源' },
          'akshare': { name: 'AkShare', desc: '开源金融数据库' },
          'tushare': { name: 'Tushare', desc: '专业金融数据' }
        }
        return { value: ds, ...labels[ds] }
      })
    }
  } catch (e) {
    console.error('加载数据源配置失败:', e)
  }
}

// 切换数据源
async function switchDatasource(source) {
  try {
    const data = await fetchApi('/api/datasource', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ source })
    })
    
    if (data.ok) {
      dataSource.value = data.data_source
      showDatasourcePanel.value = false
      // 重新加载数据
      loadAll()
    } else {
      alert('切换失败: ' + data.error)
    }
  } catch (e) {
    alert('切换失败: ' + e.message)
  }
}

onMounted(() => {
  loadDatasourceConfig()
  loadAll()
  if (autoRefresh.value) {
    timer = setInterval(refreshQuote, refreshInterval.value)
  }
  document.addEventListener('click', closePanel)
})

onUnmounted(() => {
  if (timer) {
    clearInterval(timer)
  }
  document.removeEventListener('click', closePanel)
})
</script>

<style>
:root {
  --bg: #0e1117;
  --card: #161b22;
  --card2: #1c2230;
  --line: #283040;
  --text: #c9d1d9;
  --muted: #8b949e;
  --accent: #58a6ff;
  --up: #ef232a;
  --down: #14b143;
  --warn: #d29922;
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html, body {
  height: 100%;
  overflow: hidden;
}

body {
  background: var(--bg);
  color: var(--text);
  font-family: -apple-system, "PingFang SC", "Microsoft YaHei", Helvetica, Arial, sans-serif;
  font-size: 13px;
}

/* 全局滚动条样式 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: rgba(139, 148, 158, 0.3);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(139, 148, 158, 0.5);
}

/* Firefox滚动条 */
* {
  scrollbar-width: thin;
  scrollbar-color: rgba(139, 148, 158, 0.3) transparent;
}

.app {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}

header {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  padding: 12px 16px;
  background: var(--card);
  border-bottom: 1px solid var(--line);
}

header h1 {
  font-size: 15px;
  margin: 0;
  color: var(--accent);
  white-space: nowrap;
}

header .sub {
  color: var(--muted);
  font-size: 11px;
}

/* 选择器样式 */
.selector-wrapper {
  position: relative;
}

.selector {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  background: var(--card2);
  border: 1px solid var(--line);
  border-radius: 6px;
  cursor: pointer;
  min-width: 150px;
}

.selector:hover {
  border-color: var(--accent);
}

.selector-value {
  flex: 1;
  font-size: 13px;
}

.selector-arrow {
  font-size: 10px;
  color: var(--muted);
}

.panel {
  position: absolute;
  top: 100%;
  left: 0;
  margin-top: 4px;
  width: 320px;
  max-height: 400px;
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 8px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
  z-index: 1000;
  overflow: hidden;
}

.panel-header {
  display: flex;
  gap: 8px;
  padding: 12px;
  border-bottom: 1px solid var(--line);
}

.search-input {
  flex: 1;
  padding: 6px 10px;
  background: var(--card2);
  border: 1px solid var(--line);
  color: var(--text);
  border-radius: 4px;
  font-size: 12px;
}

.search-input:focus {
  outline: none;
  border-color: var(--accent);
}

.search-btn {
  padding: 6px 12px;
  background: var(--accent);
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.search-btn:hover {
  opacity: 0.9;
}

.panel-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  padding: 8px 12px;
  border-bottom: 1px solid var(--line);
}

.panel-tabs button {
  padding: 4px 8px;
  background: transparent;
  border: 1px solid transparent;
  color: var(--muted);
  cursor: pointer;
  font-size: 11px;
  border-radius: 4px;
}

.panel-tabs button:hover {
  color: var(--text);
}

.panel-tabs button.active {
  background: var(--accent);
  color: #fff;
  border-color: var(--accent);
}

.panel-content {
  max-height: 280px;
  overflow-y: auto;
}

.panel-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  cursor: pointer;
  transition: background 0.2s;
}

.panel-item:hover {
  background: var(--card2);
}

.panel-item.active {
  background: rgba(88, 166, 255, 0.1);
}

.item-name {
  font-size: 13px;
}

.item-code {
  font-size: 11px;
  color: var(--muted);
}

/* 周期选择面板 */
.period-wrapper {
  position: relative;
}

.period-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: var(--card2);
  border: 1px solid var(--line);
  border-radius: 6px;
  cursor: pointer;
  min-width: 80px;
}

.period-btn:hover {
  border-color: var(--accent);
}

.period-btn .arrow {
  font-size: 10px;
  color: var(--muted);
}

.period-panel {
  position: absolute;
  top: 100%;
  left: 0;
  margin-top: 4px;
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 8px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
  z-index: 1000;
  padding: 12px;
  min-width: 200px;
}

.period-group {
  margin-bottom: 10px;
}

.period-group:last-child {
  margin-bottom: 0;
}

.group-title {
  font-size: 10px;
  color: var(--muted);
  margin-bottom: 6px;
  text-transform: uppercase;
}

.group-items {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.group-items button {
  padding: 4px 10px;
  background: var(--card2);
  border: 1px solid var(--line);
  color: var(--muted);
  border-radius: 4px;
  cursor: pointer;
  font-size: 11px;
}

.group-items button:hover {
  color: var(--text);
  border-color: var(--accent);
}

.group-items button.active {
  background: var(--accent);
  color: #fff;
  border-color: var(--accent);
}

/* 数据源切换 */
.datasource-wrapper {
  position: relative;
}

.datasource-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 5px 12px;
  background: var(--card2);
  border: 1px solid var(--line);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.datasource-btn:hover {
  border-color: var(--accent);
}

.ds-icon {
  font-size: 14px;
}

.ds-label {
  font-size: 12px;
  color: var(--text);
}

.datasource-panel {
  position: absolute;
  top: 100%;
  left: 0;
  margin-top: 4px;
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 8px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
  z-index: 1000;
  min-width: 200px;
  overflow: hidden;
}

.ds-title {
  padding: 10px 12px;
  font-size: 11px;
  color: var(--muted);
  border-bottom: 1px solid var(--line);
  font-weight: bold;
}

.ds-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  cursor: pointer;
  transition: background 0.2s;
}

.ds-item:hover {
  background: var(--card2);
}

.ds-item.active {
  background: rgba(88, 166, 255, 0.1);
}

.ds-name {
  font-size: 13px;
  color: var(--text);
  font-weight: 500;
}

.ds-desc {
  font-size: 11px;
  color: var(--muted);
  margin-left: auto;
}

.ds-check {
  color: var(--accent);
  font-weight: bold;
}

/* 刷新设置 */
.refresh-settings {
  display: flex;
  align-items: center;
  gap: 8px;
}

.auto {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--muted);
  font-size: 12px;
  cursor: pointer;
}

.interval-selector select {
  padding: 4px 8px;
  background: var(--card2);
  border: 1px solid var(--line);
  color: var(--text);
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
}

.interval-selector select:focus {
  outline: none;
  border-color: var(--accent);
}

.help-btn {
  width: 28px;
  height: 28px;
  background: transparent;
  border: 1px solid var(--line);
  color: var(--accent);
  border-radius: 50%;
  cursor: pointer;
  font-size: 14px;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.help-btn:hover {
  background: var(--accent);
  color: #fff;
  border-color: var(--accent);
}

.toolbar-btn {
  padding: 5px 12px;
  background: var(--card2);
  border: 1px solid var(--line);
  color: var(--text);
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s;
}

.toolbar-btn:hover {
  border-color: var(--accent);
  background: rgba(88, 166, 255, 0.1);
}

/* AI信号方向 */
.signal-direction {
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
}

.signal-direction.buy {
  background: rgba(20, 177, 67, 0.2);
  color: #14b143;
  border: 1px solid rgba(20, 177, 67, 0.4);
}

.signal-direction.sell {
  background: rgba(239, 35, 42, 0.2);
  color: #ef232a;
  border: 1px solid rgba(239, 35, 42, 0.4);
}

.signal-direction.hold {
  background: rgba(88, 166, 255, 0.2);
  color: #58a6ff;
  border: 1px solid rgba(88, 166, 255, 0.4);
}

.risk-btn {
  position: relative;
}

/* 风险控制面板 */
.risk-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 9998;
  display: flex;
  justify-content: center;
  align-items: center;
}

.risk-panel-wrapper {
  width: 500px;
  max-height: 80vh;
  background: var(--bg);
  border: 1px solid var(--line);
  border-radius: 12px;
  overflow-y: auto;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}

/* 模拟盘面板 */
.paper-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 9998;
  display: flex;
  justify-content: flex-end;
}

.paper-panel {
  width: 400px;
  height: 100vh;
  background: var(--bg);
  border-left: 1px solid var(--line);
  overflow-y: auto;
  animation: slideInRight 0.3s ease;
}

@keyframes slideInRight {
  from { transform: translateX(100%); }
  to { transform: translateX(0); }
}

#status {
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

main {
  display: grid;
  grid-template-columns: 280px 1fr 320px;
  gap: 10px;
  padding: 10px;
  flex: 1;
  overflow: hidden;
  min-height: 0;
}

.col-left {
  display: flex;
  flex-direction: column;
  gap: 10px;
  overflow-y: auto;
  height: 100%;
  min-height: 0;
}

/* 左栏卡片保持自然高度，内容超出时由 col-left 整体滚动，避免被压缩截断 */
.col-left > * {
  flex-shrink: 0;
}

.col-center {
  display: flex;
  flex-direction: column;
  min-width: 0;
  height: 100%;
  overflow: hidden;
}

.col-center .chart-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
}

.col-center .chart-container {
  flex: 1;
  min-height: 0;
}

.col-center .chart {
  height: 100% !important;
}

.col-right {
  display: flex;
  flex-direction: column;
  gap: 10px;
  overflow-y: auto;
  height: 100%;
  min-height: 0;
}

.card {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 10px;
  padding: 14px;
}

.card h2 {
  margin: 0 0 10px;
  font-size: 13px;
  color: var(--accent);
  display: flex;
  align-items: center;
  gap: 6px;
  border-left: 3px solid var(--accent);
  padding-left: 8px;
}

.card h2 small {
  color: var(--muted);
  font-weight: normal;
  font-size: 11px;
}

.chart-icon {
  font-size: 16px;
}
</style>
