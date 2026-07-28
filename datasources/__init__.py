# -*- coding: utf-8 -*-
"""
数据源抽象层 - 统一接口定义
"""
import os
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple


class DataSource(ABC):
    """数据源基类 - 定义统一接口"""

    @abstractmethod
    def get_stock_realtime(self, code: str) -> Tuple[Optional[Dict], Optional[str]]:
        """获取股票实时行情
        
        Args:
            code: 股票代码，如 '600519', 'sh600519', '000001'
            
        Returns:
            (data, error) - data 为行情字典，error 为错误信息
        """
        pass

    @abstractmethod
    def get_future_realtime(self, code: str) -> Tuple[Optional[Dict], Optional[str]]:
        """获取期货实时行情
        
        Args:
            code: 期货代码，如 'IF0', 'rb0', 'IF2508'
            
        Returns:
            (data, error) - data 为行情字典，error 为错误信息
        """
        pass

    @abstractmethod
    def get_stock_kline(self, code: str, period: str = 'day', limit: int = 120) -> Tuple[Optional[List[Dict]], Optional[str]]:
        """获取股票K线数据
        
        Args:
            code: 股票代码
            period: 周期 ('day', 'week', 'month', '5', '15', '30', '60')
            limit: 数据条数
            
        Returns:
            (bars, error) - bars 为K线列表，error 为错误信息
        """
        pass

    @abstractmethod
    def get_future_kline(self, code: str, period: str = 'day', limit: int = 120) -> Tuple[Optional[List[Dict]], Optional[str]]:
        """获取期货K线数据
        
        Args:
            code: 期货代码
            period: 周期 ('day', 'week', 'month', '5', '15', '30', '60')
            limit: 数据条数
            
        Returns:
            (bars, error) - bars 为K线列表，error 为错误信息
        """
        pass

    @abstractmethod
    def get_stock_minute(self, code: str) -> Tuple[Optional[List[Dict]], Optional[str]]:
        """获取股票分时数据
        
        Args:
            code: 股票代码
            
        Returns:
            (data, error) - data 为分时数据列表，error 为错误信息
        """
        pass

    @abstractmethod
    def get_future_minute(self, code: str) -> Tuple[Optional[List[Dict]], Optional[str]]:
        """获取期货分时数据
        
        Args:
            code: 期货代码
            
        Returns:
            (data, error) - data 为分时数据列表，error 为错误信息
        """
        pass

    @abstractmethod
    def get_stock_fund_flow(self, code: str) -> Tuple[Optional[Dict], Optional[str]]:
        """获取股票资金流向
        
        Args:
            code: 股票代码
            
        Returns:
            (data, error) - data 为资金流向数据，error 为错误信息
        """
        pass

    @abstractmethod
    def get_stock_fundamentals(self, code: str) -> Tuple[Optional[Dict], Optional[str]]:
        """获取股票基本面数据（财务指标等）
        
        Args:
            code: 股票代码
            
        Returns:
            (data, error) - data 为基本面数据，error 为错误信息
        """
        pass


class DataSourceFactory:
    """数据源工厂 - 管理和创建数据源实例"""
    
    _instances = {}
    
    @classmethod
    def get_source(cls, source_type: str = None, **kwargs) -> DataSource:
        """获取数据源实例
        
        Args:
            source_type: 数据源类型 ('tushare', 'legacy')
            **kwargs: 数据源参数（如 token）
            
        Returns:
            DataSource 实例，legacy 模式返回 None
        """
        if source_type is None:
            source_type = os.environ.get('DATA_SOURCE', 'legacy')
        
        # legacy 模式使用原有免费数据源，返回 None
        if source_type == 'legacy':
            return None
        
        cache_key = source_type
        
        if cache_key not in cls._instances:
            if source_type == 'tushare':
                from .tushare_source import TushareSource
                token = kwargs.get('token') or os.environ.get('TUSHARE_TOKEN', '')
                cls._instances[cache_key] = TushareSource(token=token)
            else:
                raise ValueError(f"不支持的数据源类型: {source_type}")
        
        return cls._instances[cache_key]


def get_data_source(source_type: str = None, **kwargs) -> DataSource:
    """获取数据源实例的便捷函数"""
    return DataSourceFactory.get_source(source_type, **kwargs)
