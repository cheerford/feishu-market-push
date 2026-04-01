#!/usr/bin/env python3
"""云端版市场推送脚本 - 支持 GitHub Actions"""
import os
import sys
import requests
from datetime import datetime

FEISHU_WEBHOOK = os.getenv("FEISHU_WEBHOOK")
ALPHA_KEY = os.getenv("ALPHA_VANTAGE_KEY", "demo")

def get_us_data():
    indices = {"SPY": "标普500", "QQQ": "纳斯达克", "DIA": "道琼斯"}
    results = []
    for symbol, name in indices.items():
        try:
            url = "https://www.alphavantage.co/query"
            params = {"function": "GLOBAL_QUOTE", "symbol": symbol, "apikey": ALPHA_KEY}
            resp = requests.get(url, params=params, timeout=15)
            data = resp.json()
            if "Global Quote" in data:
                q = data["Global Quote"]
                price = float(q.get("05. price", 0))
                change = float(q.get("10. change percent", "0%").replace("%", ""))
                emoji = "📈" if change >= 0 else "📉"
                results.append(f"{emoji} {name}: ${price:.2f} ({change:+.2f}%)")
        except Exception as e:
            print(f"Error: {e}")
    return "\n".join(results) if results else "📊 数据获取中..."

def get_cn_data():
    headers = {"User-Agent": "Mozilla/5.0"}
    indices = {"000001.SS": "上证指数", "399001.SZ": "深证成指", "000300.SS": "沪深300"}
    results = []
    for symbol, name in indices.items():
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
            resp = requests.get(url, params={"interval": "1d", "range": "2d"}, headers=headers, timeout=10)
            data = resp.json()
            if "chart" in data and data["chart"]["result"]:
                quote = data["chart"]["result"][0].get("indicators", {}).get("quote", [{}])[0]
                closes = [c for c in quote.get("close", []) if c is not None]
                if len(closes) >= 2:
                    change = ((closes[-1] - closes[-2]) / closes[-2]) * 100
                    emoji = "📈" if change >= 0 else "📉"
                    results.append(f"{emoji} {name}: {closes[-1]:,.2f} ({change:+.2f}%)")
        except Exception as e:
            print(f"Error: {e}")
    return "\n".join(results) if results else "📊 数据获取中..."

def get_hk_data():
    headers = {"User-Agent": "Mozilla/5.0"}
    indices = {"^HSI": "恒生指数", "0700.HK": "腾讯控股", "3690.HK": "美团"}
    results = []
    for symbol, name in indices.items():
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
            resp = requests.get(url, params={"interval": "1d", "range": "2d"}, headers=headers, timeout=10)
            data = resp.json()
            if "chart" in data and data["chart"]["result"]:
                quote = data["chart"]["result"][0].get("indicators", {}).get("quote", [{}])[0]
                closes = [c for c in quote.get("close", []) if c is not None]
                if len(closes) >= 2:
                    change = ((closes[-1] - closes[-2]) / closes[-2]) * 100
                    emoji = "📈" if change >= 0 else "📉"
                    currency = "HK$" if ".HK" in symbol else ""
                    results.append(f"{emoji} {name}: {currency}{closes[-1]:,.2f} ({change:+.2f}%)")
        except Exception as e:
            print(f"Error: {e}")
    return "\n".join(results) if results else "📊 数据获取中..."

def send_to_feishu(message):
    if not FEISHU_WEBHOOK:
        print("❌ 错误: 未设置 FEISHU_WEBHOOK")
        print(message)
        return False
    payload = {"msg_type": "text", "content": {"text": message}}
    try:
        resp = requests.post(FEISHU_WEBHOOK, json=payload, timeout=10)
        result = resp.json()
        if result.get("code") == 0:
            print("✅ 发送成功")
            return True
        else:
            print(f"❌ 失败: {result}")
            return False
    except Exception as e:
        print(f"❌ 异常: {e}")
        return False

def main():
    report_type = sys.argv[1] if len(sys.argv) > 1 else "morning"
    date_str = datetime.now().strftime("%Y年%m月%d日")
    if report_type == "morning":
        message = f"""📊 资本市场早报 | {date_str}
【🇺🇸 美股指数】
{get_us_data()}
【🇨🇳 A股市场】
{get_cn_data()}
【🇭🇰 港股市场】
{get_hk_data()}
—— 由 Claude Code 自动推送"""
    else:
        message = f"""🌙 市场复盘 | {date_str}
【🇺🇸 美股表现】
{get_us_data()}
【🇨🇳 A股表现】
{get_cn_data()}
【🇭🇰 港股表现】
{get_hk_data()}
—— 由 Claude Code 自动推送"""
    success = send_to_feishu(message)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
