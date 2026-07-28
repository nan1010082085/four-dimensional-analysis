# -*- coding: utf-8 -*-
"""
AkShare 数据源实现
免费开源，数据全面，适合个人项目
"""
import re
from typing import Dict, List, Optional, Tuple
from . import DataSource

try:
    import akshare as ak
    import pandas as pd
    HAS_AKSHARE = True
except ImportError:
    HAS_AKSHARE = False


class AkShareSource(DataSource):
    """AkShare 数据源"""

    def __init__(self):
        if not HAS_AKSHARE:
            raise ImportError("请安装 akshare: pip install akshare")

    def _normalize_stock_code(self, code: str) -> str:
        """标准化股票代码为纯数字"""
        code = code.strip().lower()
        # 移除市场前缀
        code = re.sub(r'^(sh|sz|bj|hk)', '', code)
        return code

    def _normalize_future_code(self, code: str) -> str:
        """标准化期货代码"""
        code = code.strip().upper()
        # 移除 nf_/hf_ 等前缀
        code = re.sub(r'^(NF|HF|SF|VF|UF|AF)_', '', code)
        return code

    def get_stock_realtime(self, code: str) -> Tuple[Optional[Dict], Optional[str]]:
        try:
            symbol = self._normalize_stock_code(code)
            # 获取单只股票实时行情
            df = ak.stock_zh_a_spot_em()
            row = df[df['代码'] == symbol]
            if row.empty:
                return None, f"未找到股票 {symbol}"
            row = row.iloc[0]
            return {
                'name': row['名称'],
                'code': symbol,
                'price': float(row['最新价']) if pd.notna(row['最新价']) else None,
                'preclose': float(row['昨收']) if pd.notna(row['昨收']) else None,
                'open': float(row['今开']) if pd.notna(row['今开']) else None,
                'high': float(row['最高']) if pd.notna(row['最高']) else None,
                'low': float(row['最低']) if pd.notna(row['最低']) else None,
                'volume': float(row['成交量']) if pd.notna(row['成交量']) else None,
                'amount': float(row['成交额']) if pd.notna(row['成交额']) else None,
                'turnover': float(row['换手率']) if pd.notna(row['换手率']) else None,
                'change': float(row['涨跌额']) if pd.notna(row['涨跌额']) else None,
                'changepct': float(row['涨跌幅']) if pd.notna(row['涨跌幅']) else None,
                'pe': float(row['市盈率-动态']) if pd.notna(row.get('市盈率-动态')) else None,
                'currency': 'CNY',
                'time': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
                'source': 'akshare',
            }, None
        except Exception as e:
            return None, f"AkShare 获取股票行情失败: {str(e)}"

    def get_future_realtime(self, code: str) -> Tuple[Optional[Dict], Optional[str]]:
        try:
            symbol = self._normalize_future_code(code)
            # 获取期货实时行情
            df = ak.futures_zh_spot()
            row = df[df['symbol'] == symbol]
            if row.empty:
                # 尝试用名称匹配
                row = df[df['name'].str.contains(symbol, na=False)]
            if row.empty:
                return None, f"未找到期货 {symbol}"
            row = row.iloc[0]
            return {
                'name': row.get('name', symbol),
                'code': symbol,
                'price': float(row['current_price']) if pd.notna(row.get('current_price')) else None,
                'preclose': float(row['pre_close']) if pd.notna(row.get('pre_close')) else None,
                'open': float(row['open']) if pd.notna(row.get('open')) else None,
                'high': float(row['high']) if pd.notna(row.get('high')) else None,
                'low': float(row['low']) if pd.notna(row.get('low')) else None,
                'volume': float(row['volume']) if pd.notna(row.get('volume')) else None,
                'openinterest': float(row['hold']) if pd.notna(row.get('hold')) else None,
                'change': float(row['change']) if pd.notna(row.get('change')) else None,
                'changepct': float(row['change_percent']) if pd.notna(row.get('change_percent')) else None,
                'currency': 'CNY',
                'time': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
                'realtime': True,
                'source': 'akshare',
            }, None
        except Exception as e:
            return None, f"AkShare 获取期货行情失败: {str(e)}"

    def get_stock_kline(self, code: str, period: str = 'day', limit: int = 120) -> Tuple[Optional[List[Dict]], Optional[str]]:
        try:
            symbol = self._normalize_stock_code(code)
            # 周期映射
            period_map = {
                'day': 'daily', 'week': 'weekly', 'month': 'monthly',
                '5': '5', '15': '15', '30': '30', '60': '60'
            }
            ak_period = period_map.get(period, 'daily')
            
            if ak_period in ['5', '15', '30', '60']:
                # 分钟级K线
                df = ak.stock_zh_a_hist_min_em(symbol=symbol, period=ak_period, adjust='qfq')
            else:
                # 日/周/月K线
                df = ak.stock_zh_a_hist(symbol=symbol, period=ak_period, adjust='qfq')
            
            if df.empty:
                return None, f"未找到 {symbol} 的K线数据"
            
            # 取最后 limit 条
            df = df.tail(limit)
            
            bars = []
            for _, row in df.iterrows():
                bars.append({
                    'date': str(row['时间']) if '时间' in df.columns else str(row['日期']),
                    'open': float(row['开盘']),
                    'high': float(row['最高']),
                    'low': float(row['最低']),
                    'close': float(row['收盘']),
                    'volume': float(row['成交量']),
                })
            return bars, None
        except Exception as e:
            return None, f"AkShare 获取股票K线失败: {str(e)}"

    def get_future_kline(self, code: str, period: str = 'day', limit: int = 120) -> Tuple[Optional[List[Dict]], Optional[str]]:
        try:
            symbol = self._normalize_future_code(code)
            
            if period in ['5', '15', '30', '60']:
                # 分钟级K线
                df = ak.futures_zh_minute_sina(symbol=symbol, period=period)
            else:
                # 日K线
                df = ak.futures_zh_daily_sina(symbol=symbol)
            
            if df.empty:
                return None, f"未找到期货 {symbol} 的K线数据"
            
            # 取最后 limit 条
            df = df.tail(limit)
            
            bars = []
            for _, row in df.iterrows():
                bars.append({
                    'date': str(row['date'] if 'date' in df.columns else row['datetime']),
                    'open': float(row['open']),
                    'high': float(row['high']),
                    'low': float(row['low']),
                    'close': float(row['close']),
                    'volume': float(row['volume']),
                })
            return bars, None
        except Exception as e:
            return None, f"AkShare 获取期货K线失败: {str(e)}"

    def get_stock_minute(self, code: str) -> Tuple[Optional[List[Dict]], Optional[str]]:
        try:
            symbol = self._normalize_stock_code(code)
            df = ak.stock_zh_a_hist_min_em(symbol=symbol, period='1', adjust='qfq')
            if df.empty:
                return None, f"未找到 {symbol} 的分时数据"
            
            data = []
            for _, row in df.iterrows():
                data.append({
                    'time': str(row['时间']),
                    'price': float(row['收盘']),
                    'avg': None,
                })
            return data, None
        except Exception as e:
            return None, f"AkShare 获取股票分时失败: {str(e)}"

    def get_future_minute(self, code: str) -> Tuple[Optional[List[Dict]], Optional[str]]:
        try:
            symbol = self._normalize_future_code(code)
            df = ak.futures_zh_minute_sina(symbol=symbol, period='1')
            if df.empty:
                return None, f"未找到期货 {symbol} 的分时数据"
            
            data = []
            for _, row in df.iterrows():
                data.append({
                    'time': str(row['datetime']),
                    'price': float(row['close']),
                    'avg': None,
                })
            return data, None
        except Exception as e:
            return None, f"AkShare 获取期货分时失败: {str(e)}"

    def get_stock_fund_flow(self, code: str) -> Tuple[Optional[Dict], Optional[str]]:
        try:
            symbol = self._normalize_stock_code(code)
            # 获取个股资金流向
            df = ak.stock_individual_fund_flow(stock=symbol, market='sh' if symbol.startswith('6') else 'sz')
            if df.empty:
                return None, f"未找到 {symbol} 的资金流向数据"
            
            latest = df.iloc[-1]
            return {
                'main_net': float(latest['主力净流入-净额']) if pd.notna(latest.get('主力净流入-净额')) else None,
                'main_pct': float(latest['主力净流入-净占比']) if pd.notna(latest.get('主力净流入-净占比')) else None,
                'super_net': float(latest['超大单净流入-净额']) if pd.notna(latest.get('超大单净流入-净额')) else None,
                'big_net': float(latest['大单净流入-净额']) if pd.notna(latest.get('大单净流入-净额')) else None,
                'mid_net': float(latest['中单净流入-净额']) if pd.notna(latest.get('中单净流入-净额')) else None,
                'small_net': float(latest['小单净流入-净额']) if pd.notna(latest.get('小单净流入-净额')) else None,
                'date': str(latest['日期']) if '日期' in df.columns else None,
                'source': 'akshare',
            }, None
        except Exception as e:
            return None, f"AkShare 获取资金流向失败: {str(e)}"

    def get_stock_fundamentals(self, code: str) -> Tuple[Optional[Dict], Optional[str]]:
        try:
            symbol = self._normalize_stock_code(code)
            # 获取财务指标
            df = ak.stock_financial_abstract_ths(symbol=symbol)
            if df.empty:
                return None, f"未找到 {symbol} 的财务数据"
            
            latest = df.iloc[0]
            return {
                'pe': float(latest.get('市盈率', None)) if pd.notna(latest.get('市盈率')) else None,
                'pb': float(latest.get('市净率', None)) if pd.notna(latest.get('市净率')) else None,
                'roe': float(latest.get('净资产收益率', None)) if pd.notna(latest.get('净资产收益率')) else None,
                'revenue': float(latest.get('营业总收入', None)) if pd.notna(latest.get('营业总收入')) else None,
                'profit': float(latest.get('净利润', None)) if pd.notna(latest.get('净利润')) else None,
                'source': 'akshare',
            }, None
        except Exception as e:
            return None, f"AkShare 获取基本面数据失败: {str(e)}"
