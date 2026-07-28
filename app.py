# -*- coding: utf-8 -*-
"""
股票 / 期货 四维分析盯盘工具 —— 后端服务
四维：行情数据(实时) / 技术面(趋势) / 基本面(逻辑) / 资金面(博弈)

支持数据源：
  - tushare: 专业级数据，需要 token（推荐）
  - akshare: 免费开源，数据全面
  - legacy: 原有免费数据源（腾讯/新浪）
"""
import os
import re
import json
import urllib.request
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 导入 AI 分析模块
from ai import get_analyzer

APP_DIR = "/Users/yangdongnan/work/four-dimensional-analysis"
app = Flask(__name__, static_folder="frontend/dist", static_url_path="")
CORS(app)

# 数据源配置
DATA_SOURCE = os.environ.get('DATA_SOURCE', 'legacy')  # tushare / akshare / legacy
data_source = None

def get_data_source():
    """获取数据源实例（懒加载）"""
    global data_source
    if data_source is None:
        try:
            from datasources import get_data_source as _get_source
            data_source = _get_source(DATA_SOURCE)
        except Exception as e:
            print(f"警告: 无法初始化 {DATA_SOURCE} 数据源: {e}")
            print("将使用 legacy 数据源（腾讯/新浪）")
    return data_source


# ----------------------------------------------------------------------------
# 网络
# ----------------------------------------------------------------------------
def http_get(url, referer=None, timeout=15, decode="utf-8"):
    headers = {"User-Agent": "Mozilla/5.0"}
    if referer:
        headers["Referer"] = referer
    req = urllib.request.Request(url, headers=headers)
    try:
        raw = urllib.request.urlopen(req, timeout=timeout).read()
    except Exception as e:  # noqa
        return None, str(e)
    return raw.decode(decode, "ignore"), None


# ----------------------------------------------------------------------------
# 工具
# ----------------------------------------------------------------------------
def _f(x):
    try:
        if x is None or x == "":
            return None
        return float(x)
    except Exception:  # noqa
        return None


def _fmt_time(s):
    s = str(s)
    if re.match(r"\d{14}", s):
        return f"{s[0:4]}-{s[4:6]}-{s[6:8]} {s[8:10]}:{s[10:12]}:{s[12:14]}"
    return s


def classify(code):
    """股票 / 期货识别"""
    c = code.strip().lower()
    if re.match(r"^(nf|hf|sf|vf|uf|af)_", c):
        return "future"
    if c.startswith("sh") or c.startswith("sz") or c.startswith("bj"):
        return "stock"
    if c.startswith("hk"):
        return "stock"
    if c.startswith("us"):
        return "stock"
    if re.fullmatch(r"\d{6}", c):
        return "stock"
    if re.fullmatch(r"[a-z]{1,2}0", c):          # IF0 / rb0 主力连续
        return "future"
    if re.fullmatch(r"[a-z]{1,2}\d{3,4}", c):     # IF2508 / rb2410 具体合约
        return "future"
    return "stock"


def normalize(code):
    """返回 (kind, tencent_code, sina_symbol)"""
    c = code.strip().lower()
    kind = classify(c)
    if kind == "future":
        sina = re.sub(r"^(nf|hf|sf|vf|uf|af)_", "", c).upper()
        return "future", None, sina
    # 股票
    if re.fullmatch(r"\d{6}", c):
        tc = ("sh" if c.startswith("6") else "sz") + c
    else:
        tc = c
    return "stock", tc, None


# ----------------------------------------------------------------------------
# 实时行情
# ----------------------------------------------------------------------------
def stock_realtime(tencent_code):
    url = "https://qt.gtimg.cn/q=" + tencent_code
    txt, err = http_get(url, referer="https://finance.qq.com", decode="gbk")
    if err:
        return None, err
    m = re.search(r'v_' + re.escape(tencent_code) + r'="([^"]*)"', txt)
    if not m:
        return None, "no data"
    p = m.group(1).split("~")
    g = lambda i: p[i] if 0 <= i < len(p) else ""

    def depth(base):
        out = []
        try:
            for i in range(5):
                out.append({"price": _f(g(base + 2 * i)), "vol": _f(g(base + 1 + 2 * i))})
        except Exception:  # noqa
            pass
        return out

    amount = g(35)
    amount_val = amount.split("/")[-1] if "/" in amount else g(37)
    return {
        "name": g(1), "code": g(2), "price": _f(g(3)), "preclose": _f(g(4)),
        "open": _f(g(5)), "high": _f(g(33)), "low": _f(g(34)),
        "volume": _f(g(6)), "amount": _f(amount_val), "turnover": _f(g(38)),
        "change": _f(g(31)), "changepct": _f(g(32)),
        "time": _fmt_time(g(30)), "pe": _f(g(39)),
        "outer": _f(g(7)), "inner": _f(g(8)),
        "bids": depth(9), "asks": depth(19),
        "currency": "CNY",
    }, None


def future_realtime(sina_symbol):
    """期货实时行情。
    中金所股指期货(IF/IC/IH等)新浪实时可用；商品期货公开实时源已失效且会返回
    错乱伪数据，因此商品期货直接退化为日K最新收盘推导，标注 realtime=False。
    """
    sym = sina_symbol  # 新浪变量名大小写敏感（如 IF0）
    is_cffex = re.match(r"^(IF|IC|IH|IM|T|TS|TF|TL)\d*", sym, re.I) is not None
    if is_cffex:
        url = "https://hq.sinajs.cn/list=nf_" + sym
        txt, err = http_get(url, referer="https://finance.sina.com.cn", decode="gbk")
        if not err:
            m = re.search(r'hq_str_nf_' + re.escape(sym) + r'="([^"]*)"', txt)
            if m and m.group(1).strip():
                p = m.group(1).split(",")
                open_ = _f(p[0]); pre_settle = _f(p[1]); last = _f(p[3])
                high = _f(p[9]); low = _f(p[10]); volume = _f(p[4]); oi = _f(p[6])
                change = round(last - pre_settle, 3) if (last is not None and pre_settle) else None
                changepct = round(change / pre_settle * 100, 2) if (change is not None and pre_settle) else None
                date = next((x for x in p if re.match(r"\d{4}-\d{2}-\d{2}", x)), "")
                t = next((x for x in p if re.match(r"\d{2}:\d{2}:\d{2}", x)), "")
                name = p[-1] if p else sym
                return {
                    "name": name, "code": sym, "price": last, "preclose": pre_settle,
                    "open": open_, "high": high, "low": low, "volume": volume,
                    "openinterest": oi, "change": change, "changepct": changepct,
                    "time": (date + " " + t).strip(), "currency": "CNY", "realtime": True,
                }, None
    # 兜底：从日K最新收盘推导（商品期货实时源不可用）
    bars, _ = future_kline(sym, "day", 2)
    if bars and len(bars) >= 2:
        last = bars[-1]; prev = bars[-2]
        price = last["close"]; pre = prev["close"]
        chg = round(price - pre, 3)
        pct = round(chg / pre * 100, 2) if pre else None
        return {
            "name": sym + "（收盘参考）", "code": sym, "price": price, "preclose": pre,
            "open": last["open"], "high": last["high"], "low": last["low"], "volume": last["volume"],
            "openinterest": None, "change": chg, "changepct": pct,
            "time": last["date"] + " 收盘参考", "currency": "CNY", "realtime": False,
        }, None
    return None, "no data"


# ----------------------------------------------------------------------------
# K 线 / 分时
# ----------------------------------------------------------------------------
STOCK_SCALE = {"day": 240, "week": 1200, "month": 6000, "5": 5, "15": 15, "30": 30, "60": 60}


def stock_kline(tencent_code, period, limit):
    sc = STOCK_SCALE.get(period, 240)
    url = (f"https://money.finance.sina.com.cn/quotes_service/api/json_v2.php/"
           f"CN_MarketData.getKLineData?symbol={tencent_code}&scale={sc}&ma=5&datalen={limit}")
    txt, err = http_get(url, referer="https://finance.sina.com.cn")
    if err:
        return None, err
    try:
        data = json.loads(txt)
    except Exception as e:  # noqa
        return None, "parse error: " + str(e)
    bars = [{"date": b["day"], "open": _f(b["open"]), "high": _f(b["high"]),
             "low": _f(b["low"]), "close": _f(b["close"]), "volume": _f(b["volume"])}
            for b in data]
    return bars, None


def future_kline(sina_symbol, period, limit):
    if period in ("5", "15", "30", "60"):
        url = (f"https://stock2.finance.sina.com.cn/futures/api/json.php/"
               f"InnerFuturesNewService.getFewMinLine?symbol={sina_symbol}&type={period}")
    else:
        url = (f"https://stock2.finance.sina.com.cn/futures/api/json.php/"
               f"InnerFuturesNewService.getDailyKLine?symbol={sina_symbol}")
    txt, err = http_get(url, referer="https://finance.sina.com.cn")
    if err:
        return None, err
    try:
        data = json.loads(txt)
    except Exception as e:  # noqa
        return None, "parse error: " + str(e)
    if period in ("5", "15", "30", "60"):
        bars = [{"date": b["d"], "open": _f(b["o"]), "high": _f(b["h"]),
                 "low": _f(b["l"]), "close": _f(b["c"]), "volume": _f(b["v"])} for b in data]
    else:
        bars = [{"date": b["d"], "open": _f(b["o"]), "high": _f(b["h"]),
                 "low": _f(b["l"]), "close": _f(b["c"]), "volume": _f(b["v"])} for b in data]
    return bars[-int(limit):], None


def stock_minute(tencent_code):
    url = f"https://web.ifzq.gtimg.cn/appstock/app/minute/query?code={tencent_code}"
    txt, err = http_get(url, referer="https://finance.qq.com")
    if err:
        return None, err
    try:
        data = json.loads(txt)
        node = data["data"][tencent_code]["data"]["data"]
    except Exception as e:  # noqa
        return None, "parse error: " + str(e)
    out = []
    for row in node:
        parts = row.split()
        if len(parts) >= 2:
            out.append({"time": parts[0], "price": _f(parts[1]), "avg": None})
    return out, None


def future_minute(sina_symbol):
    url = (f"https://stock2.finance.sina.com.cn/futures/api/json.php/"
           f"InnerFuturesNewService.getFewMinLine?symbol={sina_symbol}&type=1")
    txt, err = http_get(url, referer="https://finance.sina.com.cn")
    if err:
        return None, err
    try:
        data = json.loads(txt)
    except Exception as e:  # noqa
        return None, "parse error: " + str(e)
    out = [{"time": b["d"], "price": _f(b["c"]), "avg": None} for b in data]
    return out, None


# ----------------------------------------------------------------------------
# 技术指标
# ----------------------------------------------------------------------------
def calc_ma(closes, n):
    out = [None] * len(closes)
    for i in range(len(closes)):
        if i + 1 >= n and closes[i] is not None:
            win = closes[i + 1 - n:i + 1]
            if all(x is not None for x in win):
                out[i] = round(sum(win) / n, 3)
    return out


def calc_ema(vals, n):
    out = [None] * len(vals)
    k = 2 / (n + 1)
    prev = None
    for i, v in enumerate(vals):
        if v is None:
            continue
        prev = v if prev is None else v * k + prev * (1 - k)
        out[i] = round(prev, 4)
    return out


def calc_macd(closes, fast=12, slow=26, sig=9):
    ef = calc_ema(closes, fast)
    es = calc_ema(closes, slow)
    dif = [(round(ef[i] - es[i], 4) if ef[i] is not None and es[i] is not None else None)
           for i in range(len(closes))]
    valid = [d for d in dif if d is not None]
    dea_valid = calc_ema(valid, sig)
    dea = [None] * (len(closes) - len(valid)) + dea_valid
    hist = [(round((dif[i] - dea[i]) * 2, 4) if dif[i] is not None and dea[i] is not None else None)
            for i in range(len(closes))]
    return dif, dea, hist


def calc_rsi(closes, n=14):
    out = [None] * len(closes)
    for i in range(1, len(closes)):
        if i + 1 < n or closes[i] is None or closes[i - 1] is None:
            continue
        gains = losses = 0.0
        for j in range(i + 1 - n, i + 1):
            ch = closes[j] - closes[j - 1]
            if ch > 0:
                gains += ch
            else:
                losses -= ch
        out[i] = 100.0 if losses == 0 else round(100 - 100 / (1 + gains / losses), 2)
    return out


def calc_kdj(highs, lows, closes, n=9):
    K = [None] * len(closes)
    D = [None] * len(closes)
    J = [None] * len(closes)
    prev_k = prev_d = None
    for i in range(len(closes)):
        if i + 1 < n:
            continue
        win_h = highs[i + 1 - n:i + 1]
        win_l = lows[i + 1 - n:i + 1]
        if any(x is None for x in win_h) or any(x is None for x in win_l):
            continue
        hh, ll = max(win_h), min(win_l)
        rsv = 50 if hh == ll else (closes[i] - ll) / (hh - ll) * 100
        k = rsv if prev_k is None else prev_k * (1 - 1 / 3) + rsv * (1 / 3)
        d = k if prev_d is None else prev_d * (1 - 1 / 3) + k * (1 / 3)
        k, d = round(k, 2), round(d, 2)
        K[i], D[i], J[i] = k, d, round(3 * k - 2 * d, 2)
        prev_k, prev_d = k, d
    return K, D, J


def calc_boll(closes, n=20, k=2):
    """计算布林带"""
    upper = [None] * len(closes)
    middle = [None] * len(closes)
    lower = [None] * len(closes)
    
    for i in range(n - 1, len(closes)):
        window = closes[i + 1 - n:i + 1]
        if any(x is None for x in window):
            continue
        avg = sum(window) / n
        std = (sum((x - avg) ** 2 for x in window) / n) ** 0.5
        middle[i] = round(avg, 2)
        upper[i] = round(avg + k * std, 2)
        lower[i] = round(avg - k * std, 2)
    
    return upper, middle, lower


def calc_atr(highs, lows, closes, n=14):
    """计算ATR（平均真实波幅）"""
    atr = [None] * len(closes)
    
    for i in range(1, len(closes)):
        if i < n:
            continue
        
        tr_list = []
        for j in range(i + 1 - n, i + 1):
            if j < 1:
                continue
            high = highs[j]
            low = lows[j]
            prev_close = closes[j - 1]
            if any(x is None for x in [high, low, prev_close]):
                continue
            tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
            tr_list.append(tr)
        
        if len(tr_list) >= n:
            atr[i] = round(sum(tr_list) / n, 2)
    
    return atr


def calc_obv(closes, volumes):
    """计算OBV（能量潮）"""
    obv = [0] * len(closes)
    
    for i in range(1, len(closes)):
        if closes[i] is None or closes[i - 1] is None:
            obv[i] = obv[i - 1]
            continue
        
        if closes[i] > closes[i - 1]:
            obv[i] = obv[i - 1] + (volumes[i] or 0)
        elif closes[i] < closes[i - 1]:
            obv[i] = obv[i - 1] - (volumes[i] or 0)
        else:
            obv[i] = obv[i - 1]
    
    return obv


def calc_wr(highs, lows, closes, n=14):
    """计算威廉指标（WR）"""
    wr = [None] * len(closes)
    
    for i in range(n - 1, len(closes)):
        window_h = highs[i + 1 - n:i + 1]
        window_l = lows[i + 1 - n:i + 1]
        
        if any(x is None for x in window_h) or any(x is None for x in window_l):
            continue
        
        hh = max(window_h)
        ll = min(window_l)
        
        if hh == ll:
            wr[i] = 50
        else:
            wr[i] = round((hh - closes[i]) / (hh - ll) * -100, 2)
    
    return wr


def calc_cci(highs, lows, closes, n=14):
    """计算CCI（顺势指标）"""
    cci = [None] * len(closes)
    
    for i in range(n - 1, len(closes)):
        tp_list = []
        for j in range(i + 1 - n, i + 1):
            if any(x is None for x in [highs[j], lows[j], closes[j]]):
                continue
            tp = (highs[j] + lows[j] + closes[j]) / 3
            tp_list.append(tp)
        
        if len(tp_list) < n:
            continue
        
        tp_avg = sum(tp_list) / n
        tp_std = (sum((x - tp_avg) ** 2 for x in tp_list) / n) ** 0.5
        
        if tp_std == 0:
            cci[i] = 0
        else:
            cci[i] = round((tp_list[-1] - tp_avg) / (0.015 * tp_std), 2)
    
    return cci


def attach_indicators(bars):
    closes = [b["close"] for b in bars]
    highs = [b["high"] for b in bars]
    lows = [b["low"] for b in bars]
    volumes = [b["volume"] for b in bars]
    
    ma5, ma10, ma20, ma60 = (calc_ma(closes, n) for n in (5, 10, 20, 60))
    dif, dea, hist = calc_macd(closes)
    rsi = calc_rsi(closes)
    k, d, j = calc_kdj(highs, lows, closes)
    boll_upper, boll_middle, boll_lower = calc_boll(closes)
    atr = calc_atr(highs, lows, closes)
    obv = calc_obv(closes, volumes)
    wr = calc_wr(highs, lows, closes)
    cci = calc_cci(highs, lows, closes)
    
    return {
        "ma5": ma5, "ma10": ma10, "ma20": ma20, "ma60": ma60,
        "macd": {"dif": dif, "dea": dea, "hist": hist},
        "rsi": rsi, "kdj": {"k": k, "d": d, "j": j},
        "boll": {"upper": boll_upper, "middle": boll_middle, "lower": boll_lower},
        "atr": atr, "obv": obv, "wr": wr, "cci": cci,
    }


# ----------------------------------------------------------------------------
# API
# ----------------------------------------------------------------------------
@app.route("/")
def index():
    return send_file(f"{APP_DIR}/frontend/dist/index.html")


@app.route("/api/quote")
def api_quote():
    code = request.args.get("code", "sh600519").strip()
    kind, tc, sina = normalize(code)
    
    # 尝试使用新数据源
    ds = get_data_source()
    if ds:
        if kind == "stock":
            data, err = ds.get_stock_realtime(code)
        else:
            data, err = ds.get_future_realtime(code)
    else:
        # 使用 legacy 数据源
        if kind == "stock":
            data, err = stock_realtime(tc)
        else:
            data, err = future_realtime(sina)
    
    if err:
        return jsonify({"ok": False, "error": err, "kind": kind})
    return jsonify({"ok": True, "kind": kind, "data": data})


@app.route("/api/kline")
def api_kline():
    code = request.args.get("code", "sh600519").strip()
    period = request.args.get("period", "day")
    limit = request.args.get("limit", "120")
    kind, tc, sina = normalize(code)
    
    # 尝试使用新数据源
    ds = get_data_source()
    if ds:
        if kind == "stock":
            bars, err = ds.get_stock_kline(code, period, limit)
        else:
            bars, err = ds.get_future_kline(code, period, limit)
    else:
        if kind == "stock":
            bars, err = stock_kline(tc, period, limit)
        else:
            bars, err = future_kline(sina, period, limit)
    
    if err:
        return jsonify({"ok": False, "error": err})
    ind = attach_indicators(bars)
    return jsonify({"ok": True, "kind": kind, "period": period, "bars": bars, "indicators": ind})


@app.route("/api/minute")
def api_minute():
    code = request.args.get("code", "sh600519").strip()
    kind, tc, sina = normalize(code)
    
    # 尝试使用新数据源
    ds = get_data_source()
    if ds:
        if kind == "stock":
            data, err = ds.get_stock_minute(code)
        else:
            data, err = ds.get_future_minute(code)
    else:
        if kind == "stock":
            data, err = stock_minute(tc)
        else:
            data, err = future_minute(sina)
    
    if err:
        return jsonify({"ok": False, "error": err})
    return jsonify({"ok": True, "kind": kind, "data": data})


@app.route("/api/analysis")
def api_analysis():
    code = request.args.get("code", "sh600519").strip()
    period = request.args.get("period", "day")
    limit = request.args.get("limit", "120")
    kind, tc, sina = normalize(code)
    
    # 尝试使用新数据源
    ds = get_data_source()
    if ds:
        if kind == "stock":
            quote, qerr = ds.get_stock_realtime(code)
            bars, kerr = ds.get_stock_kline(code, period, limit)
        else:
            quote, qerr = ds.get_future_realtime(code)
            bars, kerr = ds.get_future_kline(code, period, limit)
    else:
        if kind == "stock":
            quote, qerr = stock_realtime(tc)
            bars, kerr = stock_kline(tc, period, limit)
        else:
            quote, qerr = future_realtime(sina)
            bars, kerr = future_kline(sina, period, limit)

    if qerr and kerr:
        return jsonify({"ok": False, "error": qerr or kerr, "kind": kind})

    indicators = attach_indicators(bars) if bars else None

    # 基本面（逻辑）
    if kind == "stock" and quote:
        # 尝试获取更详细的基本面数据
        fund_data = None
        if ds:
            fund_data, _ = ds.get_stock_fundamentals(code)
        
        if fund_data:
            fundamentals = {
                "pe": fund_data.get("pe"), "pb": fund_data.get("pb"),
                "turnover": fund_data.get("turnover_rate") or quote.get("turnover"),
                "volume": quote.get("volume"), "amount": quote.get("amount"),
                "open": quote.get("open"), "preclose": quote.get("preclose"),
                "high": quote.get("high"), "low": quote.get("low"),
                "total_mv": fund_data.get("total_mv"),
                "circ_mv": fund_data.get("circ_mv"),
                "source": fund_data.get("source", "legacy"),
            }
        else:
            fundamentals = {
                "pe": quote.get("pe"), "turnover": quote.get("turnover"),
                "volume": quote.get("volume"), "amount": quote.get("amount"),
                "open": quote.get("open"), "preclose": quote.get("preclose"),
                "high": quote.get("high"), "low": quote.get("low"),
                "note": "估值/财报深度数据可接入 AkShare / Tushare 扩展",
            }
    else:
        fundamentals = {"note": "期货为价格驱动品种，无传统基本面（PE/ROE 不适用）",
                        "openinterest": quote.get("openinterest") if quote else None}

    # 资金面（博弈）
    if kind == "stock" and quote:
        # 尝试获取资金流向数据
        fund_flow = None
        if ds:
            fund_flow, _ = ds.get_stock_fund_flow(code)
        
        if fund_flow:
            funds = {
                "amount": quote.get("amount"), "volume": quote.get("volume"),
                "turnover": quote.get("turnover"),
                "outer": quote.get("outer"), "inner": quote.get("inner"),
                "main_net": fund_flow.get("main_net"),
                "super_net": fund_flow.get("super_net"),
                "big_net": fund_flow.get("big_net"),
                "source": fund_flow.get("source", "legacy"),
            }
        else:
            funds = {
                "amount": quote.get("amount"), "volume": quote.get("volume"),
                "turnover": quote.get("turnover"),
                "outer": quote.get("outer"), "inner": quote.get("inner"),
                "main_net": None, "note": "主力净流入需接入 AkShare 沪深股通/主力资金扩展",
            }
    else:
        funds = {
            "openinterest": quote.get("openinterest") if quote else None,
            "volume": quote.get("volume") if quote else None,
            "note": "持仓量变化/多空持仓可接入交易所持仓排名扩展",
        }

    return jsonify({
        "ok": True, "kind": kind, "code": code, "period": period,
        "quote": quote, "kline": {"bars": bars, "indicators": indicators} if bars else None,
        "fundamentals": fundamentals, "funds": funds,
    })


@app.route("/api/ai-analysis")
def api_ai_analysis():
    """AI 分析接口"""
    code = request.args.get("code", "sh600519").strip()
    period = request.args.get("period", "day")
    limit = request.args.get("limit", "120")
    analysis_type = request.args.get("type", "comprehensive")  # technical/fundamental/funds/comprehensive
    
    # 先获取分析数据
    kind, tc, sina = normalize(code)
    
    # 尝试使用新数据源
    ds = get_data_source()
    if ds:
        if kind == "stock":
            quote, qerr = ds.get_stock_realtime(code)
            bars, kerr = ds.get_stock_kline(code, period, limit)
        else:
            quote, qerr = ds.get_future_realtime(code)
            bars, kerr = ds.get_future_kline(code, period, limit)
    else:
        if kind == "stock":
            quote, qerr = stock_realtime(tc)
            bars, kerr = stock_kline(tc, period, limit)
        else:
            quote, qerr = future_realtime(sina)
            bars, kerr = future_kline(sina, period, limit)

    if qerr and kerr:
        return jsonify({"ok": False, "error": qerr or kerr, "kind": kind})

    indicators = attach_indicators(bars) if bars else None

    # 构建分析数据
    analysis_data = {
        "kind": kind,
        "code": code,
        "period": period,
        "quote": quote,
        "kline": {"bars": bars, "indicators": indicators} if bars else None,
    }
    
    # 添加基本面和资金面数据
    if kind == "stock" and quote:
        analysis_data["fundamentals"] = {
            "pe": quote.get("pe"),
            "turnover": quote.get("turnover"),
            "volume": quote.get("volume"),
            "amount": quote.get("amount"),
        }
        analysis_data["funds"] = {
            "amount": quote.get("amount"),
            "outer": quote.get("outer"),
            "inner": quote.get("inner"),
        }
    
    # 调用 AI 分析
    analyzer = get_analyzer()
    if not analyzer:
        return jsonify({"ok": False, "error": "AI 分析服务未配置，请设置 DEEPSEEK_API_KEY 环境变量"})
    
    result, err = analyzer.analyze(analysis_data, analysis_type)
    if err:
        return jsonify({"ok": False, "error": err})
    
    return jsonify({
        "ok": True,
        "kind": kind,
        "code": code,
        "analysis_type": analysis_type,
        "analysis": result,
    })


@app.route("/api/config")
def api_config():
    """获取配置信息"""
    return jsonify({
        "ok": True,
        "data_source": DATA_SOURCE,
        "ai_enabled": os.environ.get('DEEPSEEK_API_KEY') != '',
        "model": os.environ.get('DEEPSEEK_MODEL', 'deepseek-chat'),
    })


# ----------------------------------------------------------------------------
# 模拟盘API
# ----------------------------------------------------------------------------
from paper_trading import get_paper_trading


@app.route("/api/paper/status")
def api_paper_status():
    """获取模拟盘状态"""
    pt = get_paper_trading()
    return jsonify({"ok": True, "data": pt.get_status()})


@app.route("/api/paper/buy", methods=["POST"])
def api_paper_buy():
    """模拟买入"""
    data = request.json
    pt = get_paper_trading()
    
    result = pt.buy(
        code=data.get('code'),
        name=data.get('name', data.get('code')),
        price=float(data.get('price', 0)),
        qty=int(data.get('qty', 100)),
        stop_loss=float(data.get('stop_loss')) if data.get('stop_loss') else None,
        take_profit=float(data.get('take_profit')) if data.get('take_profit') else None,
        reason=data.get('reason', '')
    )
    
    return jsonify({"ok": result['success'], "data": result})


@app.route("/api/paper/sell", methods=["POST"])
def api_paper_sell():
    """模拟卖出"""
    data = request.json
    pt = get_paper_trading()
    
    result = pt.sell(
        code=data.get('code'),
        price=float(data.get('price', 0)),
        qty=int(data.get('qty')) if data.get('qty') else None,
        reason=data.get('reason', '')
    )
    
    return jsonify({"ok": result['success'], "data": result})


@app.route("/api/paper/trades")
def api_paper_trades():
    """获取交易记录"""
    pt = get_paper_trading()
    limit = request.args.get('limit', 50, type=int)
    return jsonify({"ok": True, "data": pt.get_trades(limit)})


@app.route("/api/paper/reset", methods=["POST"])
def api_paper_reset():
    """重置模拟盘"""
    pt = get_paper_trading()
    pt.reset()
    return jsonify({"ok": True, "message": "模拟盘已重置"})


@app.route("/api/signal")
def api_signal():
    """获取AI交易信号"""
    code = request.args.get("code", "sh600519").strip()
    kind, tc, sina = normalize(code)
    
    # 获取行情数据
    ds = get_data_source()
    if ds:
        if kind == "stock":
            quote, qerr = ds.get_stock_realtime(code)
            bars, kerr = ds.get_stock_kline(code, "day", 60)
        else:
            quote, qerr = ds.get_future_realtime(code)
            bars, kerr = ds.get_future_kline(code, "day", 60)
    else:
        if kind == "stock":
            quote, qerr = stock_realtime(tc)
            bars, kerr = stock_kline(tc, "day", 60)
        else:
            quote, qerr = future_realtime(sina)
            bars, kerr = future_kline(sina, "day", 60)
    
    if qerr and kerr:
        return jsonify({"ok": False, "error": qerr or kerr})
    
    indicators = attach_indicators(bars) if bars else None
    
    signal_data = {
        "kind": kind,
        "code": code,
        "quote": quote,
        "kline": {"bars": bars, "indicators": indicators} if bars else None,
    }
    
    analyzer = get_analyzer()
    if not analyzer:
        return jsonify({"ok": False, "error": "AI 服务未配置"})
    
    result, err = analyzer.get_signal(signal_data)
    if err:
        return jsonify({"ok": False, "error": err})
    
    return jsonify({"ok": True, "signal": result})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5080, debug=False)
