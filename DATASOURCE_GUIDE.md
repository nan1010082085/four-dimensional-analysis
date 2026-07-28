# 数据源配置指南

## 快速配置

### 1. 使用 Tushare（推荐）

Tushare 提供专业级金融数据，数据质量高。

```bash
# 1. 注册账号
# 访问 https://tushare.pro/register 注册

# 2. 获取 Token
# 登录后在 https://tushare.pro/user/token 获取

# 3. 配置环境变量
export TUSHARE_TOKEN=your_token_here
export DATA_SOURCE=tushare

# 或者创建 .env 文件
cp .env.example .env
# 编辑 .env 文件填入 token
```

### 2. 使用 AkShare

AkShare 是免费开源的金融数据库，无需注册。

```bash
export DATA_SOURCE=akshare
```

### 3. 使用 Legacy 数据源

使用原有的免费数据源（腾讯/新浪），无需配置。

```bash
export DATA_SOURCE=legacy
```

## 数据源功能对比

| 功能 | Tushare | AkShare | Legacy |
|---|---|---|---|
| 股票实时行情 | ✓ | ✓ | ✓ |
| 期货实时行情 | ✓ | ✓ | 部分 |
| 日/周/月 K线 | ✓ | ✓ | ✓ |
| 分钟 K线 | ✓ | ✓ | ✓ |
| 分时数据 | ✓ | ✓ | ✓ |
| 资金流向 | ✓ | ✓ | ✗ |
| 基本面数据 | ✓ | ✓ | ✗ |
| 财务指标 | ✓ | ✓ | ✗ |

## API 接口

所有数据源都实现了统一的接口：

```python
from datasources import get_data_source

# 获取数据源
ds = get_data_source('tushare')  # 或 'akshare'

# 股票实时行情
data, error = ds.get_stock_realtime('600519')

# 期货实时行情
data, error = ds.get_future_realtime('IF0')

# 股票K线
bars, error = ds.get_stock_kline('600519', period='day', limit=120)

# 期货K线
bars, error = ds.get_future_kline('IF0', period='day', limit=120)

# 股票分时
data, error = ds.get_stock_minute('600519')

# 期货分时
data, error = ds.get_future_minute('IF0')

# 资金流向
data, error = ds.get_stock_fund_flow('600519')

# 基本面数据
data, error = ds.get_stock_fundamentals('600519')
```

## 返回数据格式

所有接口都返回 `(data, error)` 元组：

- `data`: 字典或列表，包含请求的数据
- `error`: 字符串，错误信息（成功时为 None）

### 行情数据示例

```python
{
    'name': '贵州茅台',
    'code': '600519',
    'price': 1297.37,
    'preclose': 1289.5,
    'open': 1299.0,
    'high': 1302.0,
    'low': 1289.52,
    'volume': 16027.0,
    'amount': 2078759114.0,
    'change': 7.87,
    'changepct': 0.61,
    'pe': 19.61,
    'currency': 'CNY',
    'time': '2026-07-28 10:54:32',
    'source': 'tushare'
}
```

### K线数据示例

```python
[
    {
        'date': '2026-07-28',
        'open': 1299.0,
        'high': 1302.0,
        'low': 1289.52,
        'close': 1297.37,
        'volume': 16027.0
    },
    # ...
]
```

## 扩展数据源

如需添加新的数据源，只需：

1. 在 `datasources/` 目录创建新文件
2. 继承 `DataSource` 基类
3. 实现所有抽象方法
4. 在 `DataSourceFactory` 中注册

```python
from datasources import DataSource

class MyDataSource(DataSource):
    def get_stock_realtime(self, code):
        # 实现你的逻辑
        pass
    
    # ... 实现其他方法
```
