# -*- coding: utf-8 -*-
"""
Tushare 数据源实现
专业级数据，交易所官方合作接口，数据质量高
"""
import re
import os
from typing import Dict, List, Optional, Tuple
from . import DataSource

try:
    import tushare as ts
    import pandas as pd
    HAS_TUSHARE = True
except ImportError:
    HAS_TUSHARE = False


class TushareSource(DataSource):
    """Tushare 数据源"""

    def __init__(self, token: str = None):
        if not HAS_TUSHARE:
            raise ImportError("请安装 tushare: pip install tushare")
        
        # 优先使用传入的 token，其次使用环境变量
        self.token = token or os.environ.get('TUSHARE_TOKEN', '')
        if not self.token:
            raise ValueError("请设置 TUSHARE_TOKEN 环境变量或传入 token")
        
        ts.set_token(self.token)
        self.pro = ts.pro_api()

    def _normalize_stock_code(self, code: str) -> Tuple[str, str]:
        """标准化股票代码，返回 (symbol, market)"""
        code = code.strip().lower()
        market = 'sh'
        
        if code.startswith('sh'):
            market = 'sh'
            code = code[2:]
        elif code.startswith('sz'):
            market = 'sz'
            code = code[2:]
        elif code.startswith('bj'):
            market = 'bj'
            code = code[2:]
        elif code.startswith('hk'):
            market = 'hk'
            code = code[2:]
        else:
            # 根据代码判断市场
            if code.startswith('6') or code.startswith('9'):
                market = 'sh'
            elif code.startswith('0') or code.startswith('3') or code.startswith('2'):
                market = 'sz'
            elif code.startswith('4') or code.startswith('8'):
                market = 'bj'
        
        return code, market

    def _to_ts_code(self, code: str, market: str = None) -> str:
        """转换为 Tushare 格式的代码 (XXXXXX.SH/SZ)"""
        if market:
            return f"{code}.{market.upper()}"
        code, market = self._normalize_stock_code(code)
        return f"{code}.{market.upper()}"

    def _normalize_future_code(self, code: str) -> str:
        """标准化期货代码"""
        code = code.strip().upper()
        # 移除 nf_/hf_ 等前缀
        code = re.sub(r'^(NF|HF|SF|VF|UF|AF)_', '', code)
        return code

    def get_stock_realtime(self, code: str) -> Tuple[Optional[Dict], Optional[str]]:
        try:
            ts_code = self._to_ts_code(code)
            
            # 获取日线数据（包含最新行情）
            df = self.pro.daily(ts_code=ts_code)
            if df.empty:
                return None, f"未找到股票 {ts_code}"
            
            latest = df.iloc[0]
            
            # 获取股票基本信息
            stock_info = self.pro.stock_basic(ts_code=ts_code, fields='ts_code,name,industry,market')
            name = stock_info.iloc[0]['name'] if not stock_info.empty else ts_code
            
            return {
                'name': name,
                'code': ts_code.split('.')[0],
                'price': float(latest['close']) if pd.notna(latest['close']) else None,
                'preclose': float(latest['pre_close']) if pd.notna(latest['pre_close']) else None,
                'open': float(latest['open']) if pd.notna(latest['open']) else None,
                'high': float(latest['high']) if pd.notna(latest['high']) else None,
                'low': float(latest['low']) if pd.notna(latest['low']) else None,
                'volume': float(latest['vol']) if pd.notna(latest['vol']) else None,
                'amount': float(latest['amount']) if pd.notna(latest['amount']) else None,
                'change': float(latest['change']) if pd.notna(latest['change']) else None,
                'changepct': float(latest['pct_chg']) if pd.notna(latest['pct_chg']) else None,
                'currency': 'CNY',
                'time': str(latest['trade_date']),
                'source': 'tushare',
            }, None
        except Exception as e:
            return None, f"Tushare 获取股票行情失败: {str(e)}"

    def get_future_realtime(self, code: str) -> Tuple[Optional[Dict], Optional[str]]:
        try:
            symbol = self._normalize_future_code(code)
            
            # 获取期货日线数据
            df = self.pro.fut_daily(ts_code=f"{symbol}.CFX")
            if df.empty:
                # 尝试其他交易所
                for exchange in ['CFFEX', 'SHFE', 'DCE', 'CZCE', 'INE']:
                    df = self.pro.fut_daily(ts_code=f"{symbol}.{exchange}")
                    if not df.empty:
                        break
            
            if df.empty:
                return None, f"未找到期货 {symbol}"
            
            latest = df.iloc[0]
            
            return {
                'name': symbol,
                'code': symbol,
                'price': float(latest['close']) if pd.notna(latest['close']) else None,
                'preclose': float(latest['pre_close']) if pd.notna(latest['pre_close']) else None,
                'open': float(latest['open']) if pd.notna(latest['open']) else None,
                'high': float(latest['high']) if pd.notna(latest['high']) else None,
                'low': float(latest['low']) if pd.notna(latest['low']) else None,
                'volume': float(latest['vol']) if pd.notna(latest['vol']) else None,
                'openinterest': float(latest['oi']) if pd.notna(latest['oi']) else None,
                'change': float(latest['change']) if pd.notna(latest['change']) else None,
                'changepct': float(latest['pct_chg']) if pd.notna(latest['pct_chg']) else None,
                'currency': 'CNY',
                'time': str(latest['trade_date']),
                'realtime': True,
                'source': 'tushare',
            }, None
        except Exception as e:
            return None, f"Tushare 获取期货行情失败: {str(e)}"

    def get_stock_kline(self, code: str, period: str = 'day', limit: int = 120) -> Tuple[Optional[List[Dict]], Optional[str]]:
        try:
            ts_code = self._to_ts_code(code)
            
            # 周期映射
            period_map = {
                'day': 'D', 'week': 'W', 'month': 'M',
                '5': '5min', '15': '15min', '30': '30min', '60': '60min'
            }
            freq = period_map.get(period, 'D')
            
            if freq in ['5min', '15min', '30min', '60min']:
                # 分钟级K线
                df = self.pro.stk_mins(ts_code=ts_code, freq=freq)
            else:
                # 日/周/月K线
                df = self.pro.daily(ts_code=ts_code, freq=freq)
            
            if df.empty:
                return None, f"未找到 {ts_code} 的K线数据"
            
            # 按日期排序并取最后 limit 条
            df = df.sort_values('trade_date').tail(limit)
            
            bars = []
            for _, row in df.iterrows():
                bars.append({
                    'date': str(row['trade_date']),
                    'open': float(row['open']),
                    'high': float(row['high']),
                    'low': float(row['low']),
                    'close': float(row['close']),
                    'volume': float(row['vol']),
                })
            return bars, None
        except Exception as e:
            return None, f"Tushare 获取股票K线失败: {str(e)}"

    def get_future_kline(self, code: str, period: str = 'day', limit: int = 120) -> Tuple[Optional[List[Dict]], Optional[str]]:
        try:
            symbol = self._normalize_future_code(code)
            
            # 尝试不同的交易所后缀
            ts_code = None
            for exchange in ['CFX', 'CFFEX', 'SHFE', 'DCE', 'CZCE', 'INE']:
                test_code = f"{symbol}.{exchange}"
                df_test = self.pro.fut_daily(ts_code=test_code)
                if not df_test.empty:
                    ts_code = test_code
                    break
            
            if not ts_code:
                return None, f"未找到期货 {symbol} 的K线数据"
            
            # 获取日线数据
            df = self.pro.fut_daily(ts_code=ts_code)
            
            if df.empty:
                return None, f"未找到期货 {ts_code} 的K线数据"
            
            # 按日期排序并取最后 limit 条
            df = df.sort_values('trade_date').tail(limit)
            
            bars = []
            for _, row in df.iterrows():
                bars.append({
                    'date': str(row['trade_date']),
                    'open': float(row['open']),
                    'high': float(row['high']),
                    'low': float(row['low']),
                    'close': float(row['close']),
                    'volume': float(row['vol']),
                })
            return bars, None
        except Exception as e:
            return None, f"Tushare 获取期货K线失败: {str(e)}"

    def get_stock_minute(self, code: str) -> Tuple[Optional[List[Dict]], Optional[str]]:
        try:
            ts_code = self._to_ts_code(code)
            
            # 获取1分钟线
            df = self.pro.stk_mins(ts_code=ts_code, freq='1min')
            
            if df.empty:
                return None, f"未找到 {ts_code} 的分时数据"
            
            # 取当天的数据
            df = df.sort_values('trade_time')
            
            data = []
            for _, row in df.iterrows():
                data.append({
                    'time': str(row['trade_time']),
                    'price': float(row['close']),
                    'avg': None,
                })
            return data, None
        except Exception as e:
            return None, f"Tushare 获取股票分时失败: {str(e)}"

    def get_future_minute(self, code: str) -> Tuple[Optional[List[Dict]], Optional[str]]:
        try:
            symbol = self._normalize_future_code(code)
            
            # Tushare 期货分钟数据接口
            # 尝试不同的交易所
            for exchange in ['CFX', 'CFFEX', 'SHFE', 'DCE', 'CZCE', 'INE']:
                try:
                    df = self.pro.fut_min(ts_code=f"{symbol}.{exchange}", freq='1min')
                    if not df.empty:
                        df = df.sort_values('trade_time')
                        data = []
                        for _, row in df.iterrows():
                            data.append({
                                'time': str(row['trade_time']),
                                'price': float(row['close']),
                                'avg': None,
                            })
                        return data, None
                except:
                    continue
            
            return None, f"未找到期货 {symbol} 的分时数据"
        except Exception as e:
            return None, f"Tushare 获取期货分时失败: {str(e)}"

    def get_stock_fund_flow(self, code: str) -> Tuple[Optional[Dict], Optional[str]]:
        try:
            ts_code = self._to_ts_code(code)
            
            # 获取资金流向数据
            df = self.pro.moneyflow(ts_code=ts_code)
            
            if df.empty:
                return None, f"未找到 {ts_code} 的资金流向数据"
            
            latest = df.iloc[0]
            
            return {
                'main_net': float(latest['buy_sm_amount'] - latest['sell_sm_amount']) if pd.notna(latest.get('buy_sm_amount')) else None,
                'super_net': float(latest['buy_lg_amount'] - latest['sell_lg_amount']) if pd.notna(latest.get('buy_lg_amount')) else None,
                'big_net': float(latest['buy_md_amount'] - latest['sell_md_amount']) if pd.notna(latest.get('buy_md_amount')) else None,
                'small_net': float(latest['buy_elg_amount'] - latest['sell_elg_amount']) if pd.notna(latest.get('buy_elg_amount')) else None,
                'date': str(latest['trade_date']),
                'source': 'tushare',
            }, None
        except Exception as e:
            return None, f"Tushare 获取资金流向失败: {str(e)}"

    def get_stock_fundamentals(self, code: str) -> Tuple[Optional[Dict], Optional[str]]:
        try:
            ts_code = self._to_ts_code(code)
            
            # 获取每日指标
            df = self.pro.daily_basic(ts_code=ts_code)
            
            if df.empty:
                return None, f"未找到 {ts_code} 的基本面数据"
            
            latest = df.iloc[0]
            
            return {
                'pe': float(latest['pe_ttm']) if pd.notna(latest.get('pe_ttm')) else None,
                'pb': float(latest['pb']) if pd.notna(latest.get('pb')) else None,
                'ps': float(latest['ps_ttm']) if pd.notna(latest.get('ps_ttm')) else None,
                'dv_ratio': float(latest['dv_ratio']) if pd.notna(latest.get('dv_ratio')) else None,
                'total_mv': float(latest['total_mv']) if pd.notna(latest.get('total_mv')) else None,
                'circ_mv': float(latest['circ_mv']) if pd.notna(latest.get('circ_mv')) else None,
                'turnover_rate': float(latest['turnover_rate']) if pd.notna(latest.get('turnover_rate')) else None,
                'volume_ratio': float(latest['volume_ratio']) if pd.notna(latest.get('volume_ratio')) else None,
                'date': str(latest['trade_date']),
                'source': 'tushare',
            }, None
        except Exception as e:
            return None, f"Tushare 获取基本面数据失败: {str(e)}"
