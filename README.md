# 四维分析盯盘台

股票 / 期货 **行情 · 技术 · 基本面 · 资金** 一体化本地盯盘工具，基于「四维分析法」框架。

## 技术栈

- **前端**: Vue 3 + Vite + ECharts
- **后端**: Python Flask + flask-cors
- **数据源**: Tushare（推荐）/ AkShare / 免费公开源
- **AI 分析**: DeepSeek

## 快速启动

```bash
# 方式一：一键启动（推荐）
./start.sh

# 方式二：开发模式（前端热更新）
./start.sh --dev

# 方式三：分别启动
# 终端1 - 后端
source venv/bin/activate
python app.py

# 终端2 - 前端
cd frontend
npm install
npm run dev
```

- 生产模式: http://localhost:5080
- 开发模式: http://localhost:5173（前端） + http://localhost:5080（后端）

## 用法

- **输入标的**（代码框回车，或点快捷标签）：
  - 股票：`sh600519` / `600519` / `sz000001` / `hk00700` / `usAAPL`
  - 期货：`IF0`(沪深300主连) / `rb0`(螺纹主连) / `au0`(黄金主连) / `cu0` 等；也支持具体合约 `IF2508`
- **周期**：分时 / 日K / 周K / 月K / 15分 / 60分
- **自动刷新**：默认每 3 秒拉一次实时行情（盘中盯盘）

## 四维框架

1. **行情数据（实时）**：最新价、涨跌、开高低、量额、盘口五档（股票）、持仓量（期货）
2. **技术面（趋势）**：K线 + MA(5/10/20/60) + 成交量 + MACD + KDJ（指标纯 Python 计算）
3. **基本面（逻辑）**：PE、换手、量额等估值/交易字段（股票）；期货为价格驱动，标注不适用
4. **资金面（博弈）**：成交额、换手、内外盘（股票）；持仓/成交（期货）；预留主力净流入扩展
5. **AI 分析（智能）**：基于 DeepSeek 大模型，提供技术分析、基本面分析、资金分析、综合分析

## AI 分析功能

项目集成了 DeepSeek AI 大模型，可以对股票/期货进行智能分析：

- **综合分析**：技术面 + 基本面 + 资金面全方位分析
- **技术分析**：趋势、支撑位、压力位、技术指标信号
- **基本面分析**：估值水平、盈利能力、成长性
- **资金分析**：资金流向、主力动向、市场情绪

### 配置 AI 分析

1. 访问 [DeepSeek 平台](https://platform.deepseek.com) 注册账号
2. 获取 API Key
3. 编辑 `.env` 文件：

```bash
DEEPSEEK_API_KEY=your_api_key_here
DEEPSEEK_MODEL=deepseek-chat
```

## 数据源配置

支持三种数据源，可通过环境变量 `DATA_SOURCE` 切换：

| 数据源 | 说明 | 配置 |
|---|---|---|
| `tushare`（推荐） | 专业级数据，交易所官方合作 | 需要设置 `TUSHARE_TOKEN` |
| `akshare` | 免费开源，数据全面 | 无需配置 |
| `legacy` | 原有免费数据源（腾讯/新浪） | 无需配置 |

### Tushare 配置（推荐）

1. 注册 [Tushare Pro](https://tushare.pro/register) 账号
2. 获取 API Token
3. 设置环境变量：

```bash
# 方式一：创建 .env 文件
cp .env.example .env
# 编辑 .env 文件，填入你的 token

# 方式二：直接设置环境变量
export TUSHARE_TOKEN=your_token_here
export DATA_SOURCE=tushare
```

### 数据源对比

| 功能 | Tushare | AkShare | Legacy |
|---|---|---|---|
| 股票实时行情 | ✓ | ✓ | ✓ |
| 期货实时行情 | ✓ | ✓ | 部分 |
| K线数据 | ✓ | ✓ | ✓ |
| 资金流向 | ✓ | ✓ | ✗ |
| 基本面数据 | ✓ | ✓ | ✗ |
| 数据准确性 | 高 | 中 | 中 |
| 稳定性 | 高 | 中 | 低 |

## 项目结构

```
four-dimensional-analysis/
├── app.py              # Flask 后端（API 路由）
├── ai/                 # AI 分析模块
│   └── __init__.py     # DeepSeek 分析器
├── datasources/        # 数据源抽象层
│   ├── __init__.py     # DataSource 基类 + 工厂
│   ├── tushare_source.py  # Tushare 数据源
│   └── akshare_source.py  # AkShare 数据源
├── frontend/           # Vue3 前端
│   ├── src/
│   │   ├── App.vue     # 主应用组件
│   │   └── components/ # 子组件
│   │       ├── QuoteCard.vue
│   │       ├── FundamentalsCard.vue
│   │       ├── FundsCard.vue
│   │       ├── KlineChart.vue
│   │       ├── MinuteChart.vue
│   │       └── AIAnalysis.vue  # AI 分析组件
│   ├── index.html
│   └── vite.config.js
├── .env.example        # 环境变量示例
├── requirements.txt
├── start.sh            # 一键启动脚本
└── venv/               # Python 虚拟环境
```

## 已知限制 / 扩展点

- **商品期货实时**：公开实时源已失效且会返回错乱伪数据，已自动退化为「日K 最新收盘参考」并在 UI 标注「非实时」。如需商品期货实时，可在 `app.py` 的 `future_realtime` 接入 Tushare / 交易所行情 API / 期货公司 API。
- **深度数据**：主力净流入、北向资金、期货持仓排名等已预留接口（见 `funds`/`fundamentals` 的 `note`），可经 AkShare / Tushare 填充。
