# -*- coding: utf-8 -*-
"""
模拟盘模块 - 用于验证交易策略
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Optional


class PaperTrading:
    """模拟盘交易系统"""
    
    def __init__(self, initial_capital: float = 100000):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.positions = {}  # 持仓 {code: {qty, avg_price, ...}}
        self.trades = []  # 交易记录
        self.balance_history = []  # 资金曲线
        self.data_file = "paper_trading.json"
        self._load()
    
    def _load(self):
        """从文件加载数据"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.capital = data.get('capital', self.initial_capital)
                    self.positions = data.get('positions', {})
                    self.trades = data.get('trades', [])
                    self.balance_history = data.get('balance_history', [])
            except Exception as e:
                print(f"加载模拟盘数据失败: {e}")
    
    def _save(self):
        """保存数据到文件"""
        data = {
            'capital': self.capital,
            'positions': self.positions,
            'trades': self.trades,
            'balance_history': self.balance_history
        }
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def buy(self, code: str, name: str, price: float, qty: int, 
            stop_loss: float = None, take_profit: float = None, reason: str = "") -> Dict:
        """买入"""
        total_cost = price * qty
        
        if total_cost > self.capital:
            return {"success": False, "error": "资金不足"}
        
        # 扣除资金
        self.capital -= total_cost
        
        # 更新持仓
        if code in self.positions:
            pos = self.positions[code]
            total_qty = pos['qty'] + qty
            avg_price = (pos['avg_price'] * pos['qty'] + price * qty) / total_qty
            pos['qty'] = total_qty
            pos['avg_price'] = avg_price
        else:
            self.positions[code] = {
                'name': name,
                'qty': qty,
                'avg_price': price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'entry_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        
        # 记录交易
        trade = {
            'type': 'buy',
            'code': code,
            'name': name,
            'price': price,
            'qty': qty,
            'amount': total_cost,
            'reason': reason,
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        self.trades.append(trade)
        
        # 记录资金曲线
        self._record_balance()
        
        self._save()
        
        return {
            "success": True,
            "trade": trade,
            "position": self.positions[code],
            "capital": self.capital
        }
    
    def sell(self, code: str, price: float, qty: int = None, reason: str = "") -> Dict:
        """卖出"""
        if code not in self.positions:
            return {"success": False, "error": "无持仓"}
        
        pos = self.positions[code]
        
        if qty is None:
            qty = pos['qty']
        
        if qty > pos['qty']:
            return {"success": False, "error": "卖出数量超过持仓"}
        
        # 计算盈亏
        pnl = (price - pos['avg_price']) * qty
        pnl_pct = (price / pos['avg_price'] - 1) * 100
        
        # 增加资金
        self.capital += price * qty
        
        # 更新持仓
        pos['qty'] -= qty
        if pos['qty'] == 0:
            del self.positions[code]
        
        # 记录交易
        trade = {
            'type': 'sell',
            'code': code,
            'name': pos['name'],
            'price': price,
            'qty': qty,
            'amount': price * qty,
            'pnl': round(pnl, 2),
            'pnl_pct': round(pnl_pct, 2),
            'reason': reason,
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        self.trades.append(trade)
        
        # 记录资金曲线
        self._record_balance()
        
        self._save()
        
        return {
            "success": True,
            "trade": trade,
            "capital": self.capital
        }
    
    def _record_balance(self):
        """记录资金曲线"""
        # 计算总资产
        total_assets = self.capital
        for code, pos in self.positions.items():
            total_assets += pos['avg_price'] * pos['qty']  # 简化，用成本价
        
        self.balance_history.append({
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'capital': round(self.capital, 2),
            'assets': round(total_assets, 2),
            'positions': len(self.positions)
        })
        
        # 只保留最近1000条记录
        if len(self.balance_history) > 1000:
            self.balance_history = self.balance_history[-1000:]
    
    def get_status(self) -> Dict:
        """获取当前状态"""
        # 计算总资产
        total_assets = self.capital
        position_details = []
        
        for code, pos in self.positions.items():
            pos_value = pos['avg_price'] * pos['qty']
            total_assets += pos_value
            position_details.append({
                'code': code,
                'name': pos['name'],
                'qty': pos['qty'],
                'avg_price': pos['avg_price'],
                'stop_loss': pos.get('stop_loss'),
                'take_profit': pos.get('take_profit'),
                'entry_time': pos['entry_time'],
                'cost': round(pos_value, 2)
            })
        
        # 计算总盈亏
        total_pnl = total_assets - self.initial_capital
        total_pnl_pct = (total_assets / self.initial_capital - 1) * 100
        
        # 计算胜率
        win_trades = len([t for t in self.trades if t.get('pnl', 0) > 0])
        sell_trades = len([t for t in self.trades if t['type'] == 'sell'])
        win_rate = (win_trades / sell_trades * 100) if sell_trades > 0 else 0
        
        return {
            'capital': round(self.capital, 2),
            'total_assets': round(total_assets, 2),
            'total_pnl': round(total_pnl, 2),
            'total_pnl_pct': round(total_pnl_pct, 2),
            'positions': position_details,
            'trades_count': len(self.trades),
            'win_rate': round(win_rate, 1),
            'balance_history': self.balance_history[-50:]  # 返回最近50条
        }
    
    def get_trades(self, limit: int = 50) -> List:
        """获取交易记录"""
        return self.trades[-limit:]
    
    def reset(self):
        """重置模拟盘"""
        self.capital = self.initial_capital
        self.positions = {}
        self.trades = []
        self.balance_history = []
        self._save()


# 全局实例
_paper_trading = None

def get_paper_trading() -> PaperTrading:
    """获取模拟盘实例"""
    global _paper_trading
    if _paper_trading is None:
        _paper_trading = PaperTrading()
    return _paper_trading
