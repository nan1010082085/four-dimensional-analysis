# -*- coding: utf-8 -*-
"""
Tushare 数据接口分类调用
按照数据类型分类管理，提供更丰富的数据支持
"""
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

try:
    import tushare as ts
    HAS_TUSHARE = True
except ImportError:
    HAS_TUSHARE = False


class TushareDataCenter:
    """Tushare 数据中心 - 按分类管理接口"""
    
    def __init__(self):
        if not HAS_TUSHARE:
            raise ImportError("请安装 tushare: pip install tushare")
        
        self.token = os.environ.get('TUSHARE_TOKEN', '')
        if not self.token:
            raise ValueError("请设置 TUSHARE_TOKEN 环境变量")
        
        ts.set_token(self.token)
        self.pro = ts.pro_api()
    
    # =========================================================================
    # 1. 行情数据类
    # =========================================================================
    
    def get_daily_quote(self, ts_code: str, start_date: str = None, end_date: str = None) -> Tuple[Optional[List], Optional[str]]:
        """日线行情
        
        Args:
            ts_code: 股票代码 (如 600519.SH)
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
        """
        try:
            if not start_date:
                start_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
            if not end_date:
                end_date = datetime.now().strftime('%Y%m%d')
            
            df = self.pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
            if df.empty:
                return None, "无数据"
            
            return df.to_dict('records'), None
        except Exception as e:
            return None, f"获取日线失败: {e}"
    
    def get_minute_quote(self, ts_code: str, freq: str = '5min') -> Tuple[Optional[List], Optional[str]]:
        """分钟线行情
        
        Args:
            ts_code: 股票代码
            freq: 频率 (1min/5min/15min/30min/60min)
        """
        try:
            df = self.pro.stk_mins(ts_code=ts_code, freq=freq)
            if df.empty:
                return None, "无数据"
            
            return df.to_dict('records'), None
        except Exception as e:
            return None, f"获取分钟线失败: {e}"
    
    def get_realtime_quote(self, ts_code: str) -> Tuple[Optional[Dict], Optional[str]]:
        """实时行情（通过日线最新数据推算）"""
        try:
            df = self.pro.daily(ts_code=ts_code)
            if df.empty:
                return None, "无数据"
            
            latest = df.iloc[0]
            return {
                'ts_code': ts_code,
                'trade_date': str(latest['trade_date']),
                'open': float(latest['open']),
                'high': float(latest['high']),
                'low': float(latest['low']),
                'close': float(latest['close']),
                'pre_close': float(latest['pre_close']),
                'change': float(latest['change']),
                'pct_chg': float(latest['pct_chg']),
                'vol': float(latest['vol']),
                'amount': float(latest['amount']),
            }, None
        except Exception as e:
            return None, f"获取实时行情失败: {e}"
    
    # =========================================================================
    # 2. 基本面数据类
    # =========================================================================
    
    def get_daily_basic(self, ts_code: str) -> Tuple[Optional[Dict], Optional[str]]:
        """每日指标（PE/PB/换手率等）"""
        try:
            df = self.pro.daily_basic(ts_code=ts_code)
            if df.empty:
                return None, "无数据"
            
            latest = df.iloc[0]
            return {
                'ts_code': ts_code,
                'trade_date': str(latest['trade_date']),
                'close': float(latest['close']),
                'turnover_rate': float(latest['turnover_rate']) if latest.get('turnover_rate') else None,
                'turnover_rate_f': float(latest['turnover_rate_f']) if latest.get('turnover_rate_f') else None,
                'volume_ratio': float(latest['volume_ratio']) if latest.get('volume_ratio') else None,
                'pe': float(latest['pe']) if latest.get('pe') else None,
                'pe_ttm': float(latest['pe_ttm']) if latest.get('pe_ttm') else None,
                'pb': float(latest['pb']) if latest.get('pb') else None,
                'ps': float(latest['ps']) if latest.get('ps') else None,
                'ps_ttm': float(latest['ps_ttm']) if latest.get('ps_ttm') else None,
                'dv_ratio': float(latest['dv_ratio']) if latest.get('dv_ratio') else None,
                'dv_ttm': float(latest['dv_ttm']) if latest.get('dv_ttm') else None,
                'total_share': float(latest['total_share']) if latest.get('total_share') else None,
                'float_share': float(latest['float_share']) if latest.get('float_share') else None,
                'free_share': float(latest['free_share']) if latest.get('free_share') else None,
                'total_mv': float(latest['total_mv']) if latest.get('total_mv') else None,
                'circ_mv': float(latest['circ_mv']) if latest.get('circ_mv') else None,
            }, None
        except Exception as e:
            return None, f"获取每日指标失败: {e}"
    
    def get_financial_indicator(self, ts_code: str) -> Tuple[Optional[Dict], Optional[str]]:
        """财务指标（ROE/毛利率等）"""
        try:
            df = self.pro.fina_indicator(ts_code=ts_code)
            if df.empty:
                return None, "无数据"
            
            latest = df.iloc[0]
            return {
                'ts_code': ts_code,
                'ann_date': str(latest['ann_date']),
                'end_date': str(latest['end_date']),
                'eps': float(latest['eps']) if latest.get('eps') else None,
                'dt_eps': float(latest['dt_eps']) if latest.get('dt_eps') else None,
                'total_revenue_ps': float(latest['total_revenue_ps']) if latest.get('total_revenue_ps') else None,
                'revenue_ps': float(latest['revenue_ps']) if latest.get('revenue_ps') else None,
                'capital_rese_ps': float(latest['capital_rese_ps']) if latest.get('capital_rese_ps') else None,
                'surplus_rese_ps': float(latest['surplus_rese_ps']) if latest.get('surplus_rese_ps') else None,
                'undist_profit_ps': float(latest['undist_profit_ps']) if latest.get('undist_profit_ps') else None,
                'extra_item': float(latest['extra_item']) if latest.get('extra_item') else None,
                'profit_dedt': float(latest['profit_dedt']) if latest.get('profit_dedt') else None,
                'gross_margin': float(latest['gross_margin']) if latest.get('gross_margin') else None,
                'current_ratio': float(latest['current_ratio']) if latest.get('current_ratio') else None,
                'quick_ratio': float(latest['quick_ratio']) if latest.get('quick_ratio') else None,
                'cash_ratio': float(latest['cash_ratio']) if latest.get('cash_ratio') else None,
                'arturn_days': float(latest['arturn_days']) if latest.get('arturn_days') else None,
                'invturn_days': float(latest['invturn_days']) if latest.get('invturn_days') else None,
                'assurturn_days': float(latest['assurturn_days']) if latest.get('assurturn_days') else None,
                'roe': float(latest['roe']) if latest.get('roe') else None,
                'roe_waa': float(latest['roe_waa']) if latest.get('roe_waa') else None,
                'roe_dt': float(latest['roe_dt']) if latest.get('roe_dt') else None,
                'roa': float(latest['roa']) if latest.get('roa') else None,
                'npta': float(latest['npta']) if latest.get('npta') else None,
                'roic': float(latest['roic']) if latest.get('roic') else None,
                'roe_yearly': float(latest['roe_yearly']) if latest.get('roe_yearly') else None,
                'roa2_yearly': float(latest['roa2_yearly']) if latest.get('roa2_yearly') else None,
                'debt_to_assets': float(latest['debt_to_assets']) if latest.get('debt_to_assets') else None,
                'op_yoy': float(latest['op_yoy']) if latest.get('op_yoy') else None,
                'ebt_yoy': float(latest['ebt_yoy']) if latest.get('ebt_yoy') else None,
                'tr_yoy': float(latest['tr_yoy']) if latest.get('tr_yoy') else None,
                'or_yoy': float(latest['or_yoy']) if latest.get('or_yoy') else None,
                'equity_yoy': float(latest['equity_yoy']) if latest.get('equity_yoy') else None,
            }, None
        except Exception as e:
            return None, f"获取财务指标失败: {e}"
    
    # =========================================================================
    # 3. 资金流向类
    # =========================================================================
    
    def get_money_flow(self, ts_code: str) -> Tuple[Optional[Dict], Optional[str]]:
        """个股资金流向"""
        try:
            df = self.pro.moneyflow(ts_code=ts_code)
            if df.empty:
                return None, "无数据"
            
            latest = df.iloc[0]
            return {
                'ts_code': ts_code,
                'trade_date': str(latest['trade_date']),
                'buy_sm_vol': float(latest['buy_sm_vol']) if latest.get('buy_sm_vol') else None,
                'buy_sm_amount': float(latest['buy_sm_amount']) if latest.get('buy_sm_amount') else None,
                'sell_sm_vol': float(latest['sell_sm_vol']) if latest.get('sell_sm_vol') else None,
                'sell_sm_amount': float(latest['sell_sm_amount']) if latest.get('sell_sm_amount') else None,
                'buy_md_vol': float(latest['buy_md_vol']) if latest.get('buy_md_vol') else None,
                'buy_md_amount': float(latest['buy_md_amount']) if latest.get('buy_md_amount') else None,
                'sell_md_vol': float(latest['sell_md_vol']) if latest.get('sell_md_vol') else None,
                'sell_md_amount': float(latest['sell_md_amount']) if latest.get('sell_md_amount') else None,
                'buy_lg_vol': float(latest['buy_lg_vol']) if latest.get('buy_lg_vol') else None,
                'buy_lg_amount': float(latest['buy_lg_amount']) if latest.get('buy_lg_amount') else None,
                'sell_lg_vol': float(latest['sell_lg_vol']) if latest.get('sell_lg_vol') else None,
                'sell_lg_amount': float(latest['sell_lg_amount']) if latest.get('sell_lg_amount') else None,
                'buy_elg_vol': float(latest['buy_elg_vol']) if latest.get('buy_elg_vol') else None,
                'buy_elg_amount': float(latest['buy_elg_amount']) if latest.get('buy_elg_amount') else None,
                'sell_elg_vol': float(latest['sell_elg_vol']) if latest.get('sell_elg_vol') else None,
                'sell_elg_amount': float(latest['sell_elg_amount']) if latest.get('sell_elg_amount') else None,
                'net_mf_vol': float(latest['net_mf_vol']) if latest.get('net_mf_vol') else None,
                'net_mf_amount': float(latest['net_mf_amount']) if latest.get('net_mf_amount') else None,
            }, None
        except Exception as e:
            return None, f"获取资金流向失败: {e}"
    
    def get_hsgt_top10(self, trade_date: str = None, market_type: str = '1') -> Tuple[Optional[List], Optional[str]]:
        """沪深股通十大成交股
        
        Args:
            trade_date: 交易日期
            market_type: 市场类型 (1:沪股通 3:深股通)
        """
        try:
            if not trade_date:
                trade_date = datetime.now().strftime('%Y%m%d')
            
            df = self.pro.hsgt_top10(trade_date=trade_date, market_type=market_type)
            if df.empty:
                return None, "无数据"
            
            return df.to_dict('records'), None
        except Exception as e:
            return None, f"获取沪深股通数据失败: {e}"
    
    # =========================================================================
    # 4. 期货数据类
    # =========================================================================
    
    def get_future_daily(self, ts_code: str, start_date: str = None, end_date: str = None) -> Tuple[Optional[List], Optional[str]]:
        """期货日线行情"""
        try:
            if not start_date:
                start_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
            if not end_date:
                end_date = datetime.now().strftime('%Y%m%d')
            
            df = self.pro.fut_daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
            if df.empty:
                return None, "无数据"
            
            return df.to_dict('records'), None
        except Exception as e:
            return None, f"获取期货日线失败: {e}"
    
    def get_future_mapping(self, ts_code: str) -> Tuple[Optional[List], Optional[str]]:
        """期货合约映射"""
        try:
            df = self.pro.fut_mapping(ts_code=ts_code)
            if df.empty:
                return None, "无数据"
            
            return df.to_dict('records'), None
        except Exception as e:
            return None, f"获取期货映射失败: {e}"
    
    # =========================================================================
    # 5. 指数数据类
    # =========================================================================
    
    def get_index_daily(self, ts_code: str, start_date: str = None, end_date: str = None) -> Tuple[Optional[List], Optional[str]]:
        """指数日线行情"""
        try:
            if not start_date:
                start_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
            if not end_date:
                end_date = datetime.now().strftime('%Y%m%d')
            
            df = self.pro.index_daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
            if df.empty:
                return None, "无数据"
            
            return df.to_dict('records'), None
        except Exception as e:
            return None, f"获取指数日线失败: {e}"
    
    def get_index_weight(self, index_code: str, start_date: str = None, end_date: str = None) -> Tuple[Optional[List], Optional[str]]:
        """指数成分和权重"""
        try:
            if not start_date:
                start_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
            if not end_date:
                end_date = datetime.now().strftime('%Y%m%d')
            
            df = self.pro.index_weight(index_code=index_code, start_date=start_date, end_date=end_date)
            if df.empty:
                return None, "无数据"
            
            return df.to_dict('records'), None
        except Exception as e:
            return None, f"获取指数权重失败: {e}"
    
    # =========================================================================
    # 6. 板块数据类
    # =========================================================================
    
    def get_concept_list(self, src: str = 'ts') -> Tuple[Optional[List], Optional[str]]:
        """概念板块列表"""
        try:
            df = self.pro.concept(src=src)
            if df.empty:
                return None, "无数据"
            
            return df.to_dict('records'), None
        except Exception as e:
            return None, f"获取概念板块失败: {e}"
    
    def get_concept_detail(self, id: str) -> Tuple[Optional[List], Optional[str]]:
        """概念板块成分"""
        try:
            df = self.pro.concept_detail(id=id)
            if df.empty:
                return None, "无数据"
            
            return df.to_dict('records'), None
        except Exception as e:
            return None, f"获取概念成分失败: {e}"
    
    def get_industry_list(self) -> Tuple[Optional[List], Optional[str]]:
        """行业板块列表"""
        try:
            df = self.pro.index_classify(level='L2', src='SW2021')
            if df.empty:
                return None, "无数据"
            
            return df.to_dict('records'), None
        except Exception as e:
            return None, f"获取行业板块失败: {e}"
    
    # =========================================================================
    # 7. 参考数据类
    # =========================================================================
    
    def get_trade_cal(self, start_date: str = None, end_date: str = None) -> Tuple[Optional[List], Optional[str]]:
        """交易日历"""
        try:
            if not start_date:
                start_date = datetime.now().strftime('%Y%m%d')
            if not end_date:
                end_date = (datetime.now() + timedelta(days=30)).strftime('%Y%m%d')
            
            df = self.pro.trade_cal(exchange='SSE', start_date=start_date, end_date=end_date)
            if df.empty:
                return None, "无数据"
            
            return df.to_dict('records'), None
        except Exception as e:
            return None, f"获取交易日历失败: {e}"
    
    def get_stock_basic(self, exchange: str = '', list_status: str = 'L') -> Tuple[Optional[List], Optional[str]]:
        """股票列表"""
        try:
            df = self.pro.stock_basic(exchange=exchange, list_status=list_status)
            if df.empty:
                return None, "无数据"
            
            return df.to_dict('records'), None
        except Exception as e:
            return None, f"获取股票列表失败: {e}"
    
    def get_stock_company(self, ts_code: str) -> Tuple[Optional[Dict], Optional[str]]:
        """上市公司基本信息"""
        try:
            df = self.pro.stock_company(ts_code=ts_code)
            if df.empty:
                return None, "无数据"
            
            latest = df.iloc[0]
            return {
                'ts_code': ts_code,
                'chairman': latest.get('chairman'),
                'manager': latest.get('manager'),
                'secretary': latest.get('secretary'),
                'reg_capital': float(latest['reg_capital']) if latest.get('reg_capital') else None,
                'setup_date': str(latest['setup_date']) if latest.get('setup_date') else None,
                'province': latest.get('province'),
                'city': latest.get('city'),
                'introduction': latest.get('introduction'),
                'website': latest.get('website'),
                'email': latest.get('email'),
                'office': latest.get('office'),
                'employees': int(latest['employees']) if latest.get('employees') else None,
                'main_business': latest.get('main_business'),
                'business_scope': latest.get('business_scope'),
            }, None
        except Exception as e:
            return None, f"获取公司信息失败: {e}"


# 全局实例
_data_center = None

def get_data_center() -> Optional[TushareDataCenter]:
    """获取数据中心实例"""
    global _data_center
    if _data_center is None:
        try:
            _data_center = TushareDataCenter()
        except Exception as e:
            print(f"警告: 无法初始化 TushareDataCenter: {e}")
    return _data_center
