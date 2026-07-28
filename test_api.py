#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
四维分析盯盘台 - API 测试脚本
"""
import requests
import json

BASE_URL = "http://localhost:5080"

def test_api(endpoint, params=None):
    """测试 API 接口"""
    url = f"{BASE_URL}{endpoint}"
    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        if data.get('ok'):
            print(f"✓ {endpoint} - 成功")
            return data
        else:
            print(f"✗ {endpoint} - 失败: {data.get('error')}")
            return None
    except Exception as e:
        print(f"✗ {endpoint} - 错误: {e}")
        return None

def main():
    print("=" * 50)
    print("四维分析盯盘台 - API 测试")
    print("=" * 50)
    print()
    
    # 测试股票行情
    print("【股票测试】")
    data = test_api("/api/quote", {"code": "sh600519"})
    if data:
        q = data['data']
        print(f"  {q['name']} ({q['code']}): {q['price']}")
    print()
    
    # 测试股票K线
    data = test_api("/api/kline", {"code": "sh600519", "period": "day", "limit": "5"})
    if data:
        print(f"  K线数据: {len(data['bars'])} 条")
    print()
    
    # 测试股票分析
    data = test_api("/api/analysis", {"code": "sh600519", "period": "day", "limit": "5"})
    if data:
        print(f"  基本面: PE={data['fundamentals'].get('pe')}")
        print(f"  资金面: 成交额={data['funds'].get('amount')}")
    print()
    
    # 测试期货行情
    print("【期货测试】")
    data = test_api("/api/quote", {"code": "IF0"})
    if data:
        q = data['data']
        print(f"  {q['name']} ({q['code']}): {q['price']}")
    print()
    
    # 测试期货K线
    data = test_api("/api/kline", {"code": "IF0", "period": "day", "limit": "5"})
    if data:
        print(f"  K线数据: {len(data['bars'])} 条")
    print()
    
    # 测试其他股票
    print("【其他股票测试】")
    for code in ["sz000001", "sh510300", "hk00700"]:
        data = test_api("/api/quote", {"code": code})
        if data:
            q = data['data']
            print(f"  {q['name']} ({q['code']}): {q['price']}")
    print()
    
    # 测试其他期货
    print("【其他期货测试】")
    for code in ["rb0", "au0", "cu0"]:
        data = test_api("/api/quote", {"code": code})
        if data:
            q = data['data']
            print(f"  {q['name']} ({q['code']}): {q['price']}")
    print()
    
    print("=" * 50)
    print("测试完成！")
    print("=" * 50)

if __name__ == "__main__":
    main()
