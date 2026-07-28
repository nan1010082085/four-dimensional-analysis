# -*- coding: utf-8 -*-
"""
AI 分析模块 - 短线精准信号分析
"""
import os
import json
from typing import Dict, Optional, Tuple, List

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False


class AIAnalyzer:
    """AI 短线分析器"""
    
    def __init__(self):
        if not HAS_OPENAI:
            raise ImportError("请安装 openai: pip install openai")
        
        self.api_key = os.environ.get('DEEPSEEK_API_KEY', '')
        self.base_url = os.environ.get('DEEPSEEK_BASE_URL', 'https://api.deepseek.com')
        self.model = os.environ.get('DEEPSEEK_MODEL', 'deepseek-chat')
        
        if not self.api_key:
            raise ValueError("请设置 DEEPSEEK_API_KEY 环境变量")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    def analyze(self, data: Dict, analysis_type: str = 'comprehensive') -> Tuple[Optional[str], Optional[str]]:
        """进行AI分析"""
        try:
            prompt = self._build_prompt(data, analysis_type)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # 降低温度，提高确定性
                max_tokens=2500
            )
            
            return response.choices[0].message.content, None
        except Exception as e:
            return None, f"AI 分析失败: {str(e)}"
    
    def get_signal(self, data: Dict) -> Tuple[Optional[Dict], Optional[str]]:
        """获取精准买卖信号"""
        try:
            prompt = self._build_signal_prompt(data)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_signal_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # 极低温度，确保信号一致性
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result, None
        except Exception as e:
            return None, f"信号获取失败: {str(e)}"
    
    def _get_system_prompt(self) -> str:
        """短线分析系统提示词"""
        return """你是一位专注A股/期货的短线交易分析师，擅长日内和波段交易。

## 分析原则

1. **明确观点**：直接给出买入/卖出/观望建议，不含糊
2. **精准点位**：给出具体的入场价、止损价、止盈价
3. **时效性**：短线信号有效期1-3天
4. **概率思维**：说明信号成功概率和风险收益比

## 短线信号判断标准

### 买入信号（满足2个以上）
- MACD金叉或即将金叉
- KDJ超卖区回升（K<20后上穿）
- RSI超卖回升（RSI<30后上穿）
- 股价站上5日均线
- 放量突破关键压力位
- 阳包阴反转形态

### 卖出信号（满足2个以上）
- MACD死叉或即将死叉
- KDJ超买区回落（K>80后下穿）
- RSI超买回落（RSI>70后下穿）
- 股价跌破5日均线
- 放量滞涨或缩量上涨
- 阴包阳反转形态
- 高位长上影线

## 输出要求

1. 当前状态（1句话）
2. 操作建议（买入/卖出/观望）
3. 入场价格区间
4. 止损位（必须设置）
5. 止盈目标（至少1个）
6. 信号强度（强/中/弱）
7. 风险提示

用中文回答，简洁明了。"""
    
    def _get_signal_system_prompt(self) -> str:
        """信号提取系统提示词"""
        return """你是一个交易信号提取器。根据分析数据，输出JSON格式的交易信号。

输出格式：
{
  "action": "buy" | "sell" | "hold",
  "confidence": 0.0-1.0,
  "entry_price": 价格,
  "stop_loss": 止损价,
  "take_profit_1": 止盈价1,
  "take_profit_2": 止盈价2,
  "reason": "信号原因",
  "valid_until": "有效期（如：1-3天）"
}

只输出JSON，不要其他内容。"""
    
    def _build_signal_prompt(self, data: Dict) -> str:
        """构建信号提取提示词"""
        quote = data.get('quote', {})
        kline = data.get('kline', {})
        indicators = kline.get('indicators', {}) if kline else {}
        
        prompt = "根据以下数据，提取交易信号：\n\n"
        
        if quote:
            prompt += f"当前价格: {quote.get('price')}\n"
            prompt += f"涨跌幅: {quote.get('changepct')}%\n"
            prompt += f"最高: {quote.get('high')}\n"
            prompt += f"最低: {quote.get('low')}\n"
            prompt += f"昨收: {quote.get('preclose')}\n\n"
        
        if indicators:
            # MA状态
            ma5 = indicators.get('ma5', [])
            ma10 = indicators.get('ma10', [])
            ma20 = indicators.get('ma20', [])
            
            if ma5 and ma10 and ma20:
                last_ma5 = ma5[-1] if ma5[-1] else 0
                last_ma10 = ma10[-1] if ma10[-1] else 0
                last_ma20 = ma20[-1] if ma20[-1] else 0
                
                if last_ma5 > last_ma10 > last_ma20:
                    prompt += "均线状态: 多头排列\n"
                elif last_ma5 < last_ma10 < last_ma20:
                    prompt += "均线状态: 空头排列\n"
                else:
                    prompt += "均线状态: 纠缠\n"
            
            # MACD状态
            macd = indicators.get('macd', {})
            if macd.get('hist'):
                hist = macd['hist']
                if hist[-1] > 0 and hist[-2] <= 0:
                    prompt += "MACD: 刚刚金叉\n"
                elif hist[-1] < 0 and hist[-2] >= 0:
                    prompt += "MACD: 刚刚死叉\n"
                elif hist[-1] > 0:
                    prompt += "MACD: 多头\n"
                else:
                    prompt += "MACD: 空头\n"
            
            # KDJ状态
            kdj = indicators.get('kdj', {})
            if kdj.get('k'):
                k = kdj['k'][-1]
                if k and k < 20:
                    prompt += "KDJ: 超卖区\n"
                elif k and k > 80:
                    prompt += "KDJ: 超买区\n"
            
            # RSI状态
            rsi = indicators.get('rsi', [])
            if rsi and rsi[-1]:
                if rsi[-1] < 30:
                    prompt += "RSI: 超卖\n"
                elif rsi[-1] > 70:
                    prompt += "RSI: 超买\n"
        
        prompt += "\n请输出交易信号JSON。"
        
        return prompt
    
    def _build_prompt(self, data: Dict, analysis_type: str) -> str:
        """构建分析提示词"""
        kind = data.get('kind', 'stock')
        code = data.get('code', '')
        quote = data.get('quote', {})
        kline = data.get('kline', {})
        
        prompt = f"【短线交易分析】{'股票' if kind == 'stock' else '期货'}: {code}\n\n"
        
        # 行情数据
        if quote:
            prompt += "【实时行情】\n"
            prompt += f"最新价: {quote.get('price')}\n"
            prompt += f"涨跌: {quote.get('change')} ({quote.get('changepct')}%)\n"
            prompt += f"今开: {quote.get('open')} | 最高: {quote.get('high')} | 最低: {quote.get('low')}\n"
            prompt += f"昨收: {quote.get('preclose')}\n"
            
            if kind == 'stock':
                prompt += f"成交量: {quote.get('volume')} | 换手率: {quote.get('turnover')}%\n"
                if quote.get('outer') and quote.get('inner'):
                    ratio = quote['outer'] / quote['inner'] if quote['inner'] > 0 else 0
                    prompt += f"外内盘比: {ratio:.2f} {'(多方主导)' if ratio > 1 else '(空方主导)'}\n"
            else:
                prompt += f"持仓量: {quote.get('openinterest')}\n"
            
            prompt += "\n"
        
        # 技术指标
        if kline and kline.get('indicators'):
            ind = kline['indicators']
            
            prompt += "【技术指标】\n"
            
            # 均线
            ma5 = ind.get('ma5', [])
            ma10 = ind.get('ma10', [])
            ma20 = ind.get('ma20', [])
            if ma5 and ma10 and ma20:
                prompt += f"MA5: {ma5[-1]} | MA10: {ma10[-1]} | MA20: {ma20[-1]}\n"
            
            # MACD
            macd = ind.get('macd', {})
            if macd.get('dif') and macd.get('dea') and macd.get('hist'):
                prompt += f"MACD: DIF={macd['dif'][-1]}, DEA={macd['dea'][-1]}, 柱={macd['hist'][-1]}\n"
            
            # KDJ
            kdj = ind.get('kdj', {})
            if kdj.get('k') and kdj.get('d') and kdj.get('j'):
                prompt += f"KDJ: K={kdj['k'][-1]}, D={kdj['d'][-1]}, J={kdj['j'][-1]}\n"
            
            # RSI
            rsi = ind.get('rsi', [])
            if rsi and rsi[-1]:
                prompt += f"RSI: {rsi[-1]}\n"
            
            # 布林带
            boll = ind.get('boll', {})
            if boll.get('upper') and boll.get('middle') and boll.get('lower'):
                prompt += f"BOLL: 上={boll['upper'][-1]}, 中={boll['middle'][-1]}, 下={boll['lower'][-1]}\n"
            
            # ATR
            atr = ind.get('atr', [])
            if atr and atr[-1]:
                prompt += f"ATR(14): {atr[-1]}\n"
            
            prompt += "\n"
        
        # 分析要求
        prompt += """【请按以下格式输出分析】

1. **当前状态**（1句话概括）
2. **操作建议**：买入 / 卖出 / 观望
3. **入场价格**：具体价格区间
4. **止损位**：必须设置，基于ATR或关键支撑
5. **止盈目标**：至少2个目标位
6. **信号强度**：强 / 中 / 弱
7. **风险收益比**：预期盈亏比
8. **风险提示**：需要注意的风险点

要求：
- 直接给出结论，不要过多分析过程
- 止损止盈必须给出具体价格
- 说明信号有效期（1-3天）
- 如果是观望，说明等待什么条件触发"""
        
        return prompt


# 全局实例
_analyzer = None

def get_analyzer() -> Optional[AIAnalyzer]:
    """获取AI分析器实例"""
    global _analyzer
    if _analyzer is None:
        try:
            _analyzer = AIAnalyzer()
        except Exception as e:
            print(f"警告: 无法初始化 AI 分析器: {e}")
    return _analyzer
